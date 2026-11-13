"""Batch 3 engine: bars, indicators, causal trade outcomes. Implements PREREGISTRATION.md.
Every signal is decided on a CLOSED bar and entered at the NEXT bar's open (market order); stop is checked before target;
a target needs price one spread beyond it. Outcomes are precomputed per bar, side and exit rule, so any combination's trades
are just a mask over the same outcome arrays (identical execution for every idea).
"""
import os, time
import numpy as np
import pandas as pd

H2026 = 1767225600000 // 60000            # 2026-01-01 in epoch minutes (confirmation period start)
EXITS = {"X1": (1.5, 3.0, 24), "X2": (1.0, 1.5, 12), "X3": (None, None, 12)}
CRYPTO_SPREAD_BP = {"BTCUSDT": 0.79, "ETHUSDT": 4.13}     # Exness BTCUSDm / ETHUSDm medians (../batch2_review/REVIEW.md)


def load_1m(path, market):
    z = np.load(path); d = dict(m=z["m"].astype(np.int64), o=z["o"], h=z["h"], l=z["l"], c=z["c"])
    assert d["m"][0] * 60000 >= 1735689600000, "data before 2025-01-01"
    cost_bp = float(np.median(z["sp"] / z["c"]) * 1e4) if "sp" in z else CRYPTO_SPREAD_BP[market]
    return d, cost_bp


def bars(d, tf):
    b = d["m"] // tf; st = np.flatnonzero(np.r_[True, b[1:] != b[:-1]]); en = np.r_[st[1:], len(b)]
    return pd.DataFrame(dict(t=b[st] * tf, o=d["o"][st], h=np.maximum.reduceat(d["h"], st), l=np.minimum.reduceat(d["l"], st), c=d["c"][en - 1]))


# ------------------------------------------------------------------ indicators (all causal: value at bar i uses bars <= i)
def ema(x, n): return x.ewm(span=n, adjust=False).mean()
def sma(x, n): return x.rolling(n).mean()
def rma(x, n): return x.ewm(alpha=1 / n, adjust=False).mean()


def atr(df, n=14):
    pc = df.c.shift(); tr = pd.concat([df.h - df.l, (df.h - pc).abs(), (df.l - pc).abs()], axis=1).max(axis=1); return rma(tr, n)


def rsi(c, n):
    d = c.diff(); up = rma(d.clip(lower=0), n); dn = rma(-d.clip(upper=0), n); return 100 - 100 / (1 + up / dn)


def supertrend(df, n=10, k=3.0):
    a = atr(df, n).values; hl2 = ((df.h + df.l) / 2).values; c = df.c.values; N = len(c)
    ub, lb = hl2 + k * a, hl2 - k * a; fu, fl = ub.copy(), lb.copy(); dr = np.ones(N, dtype=int)
    for i in range(1, N):
        fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        dr[i] = 1 if c[i] > fu[i - 1] else (-1 if c[i] < fl[i - 1] else dr[i - 1])
    return dr


def psar(df, step=0.02, mx=0.2):
    h, l = df.h.values, df.l.values; N = len(h); up = True; ep = h[0]; s = l[0]; af = step; dr = np.ones(N, dtype=int)
    for i in range(1, N):
        s = s + af * (ep - s)
        if up:
            s = min(s, l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < s: up, s, ep, af = False, ep, l[i], step
            elif h[i] > ep: ep, af = h[i], min(af + step, mx)
        else:
            s = max(s, h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > s: up, s, ep, af = True, ep, h[i], step
            elif l[i] < ep: ep, af = l[i], min(af + step, mx)
        dr[i] = 1 if up else -1
    return dr


def adx(df, n=14):
    up = df.h.diff(); dn = -df.l.diff(); pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(df, n); pdi = 100 * rma(pd.Series(pdm, index=df.index), n) / a; ndi = 100 * rma(pd.Series(ndm, index=df.index), n) / a
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi); return rma(dx, n), pdi, ndi


def x_up(a, b): a, b = np.asarray(a, float), np.asarray(b, float); return np.r_[False, (a[1:] > b[1:]) & (a[:-1] <= b[:-1])]
def x_dn(a, b): a, b = np.asarray(a, float), np.asarray(b, float); return np.r_[False, (a[1:] < b[1:]) & (a[:-1] >= b[:-1])]


def roll_prev_max(x, n): return pd.Series(x).shift(1).rolling(n).max().values
def roll_prev_min(x, n): return pd.Series(x).shift(1).rolling(n).min().values


# ------------------------------------------------------------------ outcomes
def outcomes(df, cost_bp):
    """For every bar i (signal at its close) and side, the net return of a trade entered at o[i+1] under each exit rule.
    Returns {exit: {side: (net_1x, exit_index)}} with NaN where data runs out."""
    o, h, l, c = df.o.values, df.h.values, df.l.values, df.c.values; A = atr(df).values; N = len(o); cost = cost_bp / 1e4
    out = {}
    for ex, (ks, kt, hold) in EXITS.items():
        out[ex] = {}
        for side in (1, -1):
            net = np.full(N, np.nan); xi = np.full(N, -1, dtype=np.int64)
            e = np.arange(N) + 1; ok = (e + hold - 1 < N) & ~np.isnan(A)
            ent = np.where(e < N, o[np.minimum(e, N - 1)], np.nan); done = ~ok; px = np.full(N, np.nan)
            if ks is not None:
                stop = ent - side * ks * A; tp = ent + side * kt * A; pen = ent * cost
                for k in range(hold):
                    j = np.minimum(e + k, N - 1); live = ~done
                    gap = live & (k > 0) & ((o[j] - stop) * side <= 0)
                    hit_s = live & ~gap & (((l[j] if side > 0 else h[j]) - stop) * side <= 0)
                    hit_t = live & ~gap & ~hit_s & (((h[j] if side > 0 else l[j]) - (tp + side * pen)) * side >= 0)
                    px[gap] = o[j][gap]; px[hit_s] = stop[hit_s]; px[hit_t] = tp[hit_t]
                    fin = gap | hit_s | hit_t; xi[fin] = j[fin]; done |= fin
            last = np.minimum(e + hold - 1, N - 1); rest = ~done
            px[rest] = c[last][rest]; xi[rest] = last[rest]
            r = side * (px / ent - 1) - cost; r[~ok] = np.nan; xi[~ok] = -1
            out[ex][side] = (r, xi)
    return out
