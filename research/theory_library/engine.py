"""Shared data, indicators and trade simulation for the theory library (PREREGISTRATION.md)."""
import datetime as dt, os
from functools import lru_cache
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BARS = os.environ.get("BARS_DIR", "")
EXNESS = ("XAUUSDm", "USOILm", "DE30m", "US500m", "USTECm"); CRYPTO = ("BTCUSDT", "ETHUSDT"); INDICES = ("DE30m", "US500m", "USTECm")
CRYPTO_FEE = 0.0005; HOLDOUT_MS = 1767225600000  # 2026-01-01 UTC
TF_MIN = {"1m": 1, "5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
NY, BER = ZoneInfo("America/New_York"), ZoneInfo("Europe/Berlin")


# ---------------------------------------------------------------- data
@lru_cache(maxsize=None)
def base(mkt):
    if mkt in EXNESS:
        z = np.load(os.path.join(BARS, f"{mkt}_1m.npz"))
        return pd.DataFrame(dict(m=z["m"], o=z["o"], h=z["h"], l=z["l"], c=z["c"], hs=z["sp"] / 2))
    d = pd.read_csv(os.path.join(ROOT, "daily_signal_dca", "from_2025", "data", f"{mkt}_1h_from2025.csv.gz"))
    assert d.t.min() >= 1735689600000
    return pd.DataFrame(dict(m=d.t // 60000, o=d.o, h=d.h, l=d.l, c=d.c, hs=d.o * CRYPTO_FEE))


@lru_cache(maxsize=None)
def candles(mkt, tf):
    b = base(mkt); n = TF_MIN[tf]
    if mkt in CRYPTO and n < 60: return None
    if tf == "1d": key = (b.m + 120) // 1440 if mkt in EXNESS else b.m // 1440
    elif mkt in CRYPTO and n == 60: key = b.m // 60
    else: key = b.m // n
    g = b.groupby(key.values, sort=True)
    c = pd.DataFrame(dict(o=g.o.first(), h=g.h.max(), l=g.l.min(), c=g.c.last(), hs=g.hs.first(), m=g.m.first(), nb=g.m.size()))
    if tf == "1d" and mkt in EXNESS: c = c[c.nb >= 100]
    c = c.reset_index(drop=True)
    c["day"] = ((c.m + 120) // 1440) if mkt in EXNESS else (c.m // 1440)
    c["ms"] = c.m * 60000
    return c


@lru_cache(maxsize=None)
def local_minute(day_ordinal, tz, hh, mm):
    d = dt.date.fromordinal(day_ordinal)
    return int(dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz).timestamp() // 60)


# ---------------------------------------------------------------- indicators
ema = lambda x, n: x.ewm(span=n, adjust=False).mean()
sma = lambda x, n: x.rolling(n).mean()


def rsi(c, n):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def atr(df, n):
    tr = pd.concat([df.h - df.l, (df.h - df.c.shift()).abs(), (df.l - df.c.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df, n=14):
    up, dn = df.h.diff(), -df.l.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index); mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    a = atr(df, n); pdi = 100 * pdm.ewm(alpha=1 / n, adjust=False).mean() / a; mdi = 100 * mdm.ewm(alpha=1 / n, adjust=False).mean() / a
    return (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / n, adjust=False).mean(), pdi, mdi


def supertrend(df, n=10, k=3.0):
    a = atr(df, n).values; hl2 = ((df.h + df.l) / 2).values; c = df.c.values; N = len(c)
    ub, lb = hl2 + k * a, hl2 - k * a; fu, fl = ub.copy(), lb.copy(); d = np.ones(N)
    for i in range(1, N):
        fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]
        fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        d[i] = 1 if c[i] > fu[i - 1] else (-1 if c[i] < fl[i - 1] else d[i - 1])
    d[:n] = 0; return d


def psar(h, l, step=0.02, mx=0.2):
    n = len(h); s = np.zeros(n); up = True; af = step; ep = h[0]; s[0] = l[0]; side = np.ones(n)
    for i in range(1, n):
        s[i] = s[i - 1] + af * (ep - s[i - 1])
        if up:
            s[i] = min(s[i], l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < s[i]: up, s[i], ep, af = False, ep, l[i], step
            elif h[i] > ep: ep, af = h[i], min(af + step, mx)
        else:
            s[i] = max(s[i], h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > s[i]: up, s[i], ep, af = True, ep, h[i], step
            elif l[i] < ep: ep, af = l[i], min(af + step, mx)
        side[i] = 1 if up else -1
    return side


# ---------------------------------------------------------------- trades
class Book:
    """Collects trades as (entry_idx, exit_idx, side, entry_px, exit_px) on one candle frame."""
    def __init__(self, c): self.c = c; self.rows = []
    def add(self, i, j, side, pe, px): self.rows.append((int(i), int(j), int(side), float(pe), float(px)))


def from_positions(c, pos, flat_at_day_end=False):
    """pos[i] decided at close of candle i, held from open i+1. Each run of a constant non-zero side is one trade (open to open)."""
    pos = np.nan_to_num(np.asarray(pos, dtype=float)); bk = Book(c); o = c.o.values; n = len(o)
    if flat_at_day_end:
        last = np.r_[c.day.values[1:] != c.day.values[:-1], True]; pos = np.where(last, 0, pos)
    held = np.r_[0, pos[:-1]]
    i = 1
    while i < n:
        if held[i] != 0:
            j = i
            while j + 1 < n and held[j + 1] == held[i]: j += 1
            if j + 1 < n: bk.add(i, j + 1, held[i], o[i], o[j + 1])
            i = j + 1
        else: i += 1
    return bk


def manage(c, i0, side, stop, tp, tmax=None, last=None):
    """From candle i0 (already filled at its open or intrabar), stop first, then target; returns (exit_idx, exit_px)."""
    o, h, l, cl = c.o.values, c.h.values, c.l.values, c.c.values
    end = len(o) - 1 if last is None else min(last, len(o) - 1)
    if tmax is not None: end = min(end, i0 + tmax)
    for k in range(i0, end + 1):
        if k > i0 and ((side > 0 and o[k] <= stop) or (side < 0 and o[k] >= stop)): return k, o[k]
        if (side > 0 and l[k] <= stop) or (side < 0 and h[k] >= stop): return k, stop
        if tp is not None and ((side > 0 and h[k] >= tp) or (side < 0 and l[k] <= tp)):
            return k, (o[k] if (k > i0 and ((side > 0 and o[k] >= tp) or (side < 0 and o[k] <= tp))) else tp)
    return end, cl[end]


def evaluate(c, bk, mult):
    """Net returns per trade at cost multiple `mult`, split by entry period."""
    if not bk.rows: return {"dev": np.array([]), "holdout": np.array([])}, np.zeros((0, 3), dtype=int)
    r = np.array(bk.rows); i, j, side, pe, px = r[:, 0].astype(int), r[:, 1].astype(int), r[:, 2], r[:, 3], r[:, 4]
    hs = c.hs.values; ms = c.ms.values
    net = side * (px - pe) / pe - mult * (hs[i] + hs[np.minimum(j, len(hs) - 1)]) / pe
    hold = ms[i] >= HOLDOUT_MS
    return {"dev": net[~hold], "holdout": net[hold]}, np.c_[i, np.maximum(j - i, 1), side.astype(int)]


def random_control(c, meta, mult, draws, rng):
    o = c.o.values; hs = c.hs.values; ms = c.ms.values; n = len(o); split = int(np.searchsorted(ms, HOLDOUT_MS)); out = {}
    for p, (lo, hi) in (("dev", (0, split)), ("holdout", (split, n))):
        sel = meta[(meta[:, 0] >= lo) & (meta[:, 0] < hi)]
        if len(sel) == 0: out[p] = None; continue
        dur, side = sel[:, 1], sel[:, 2]
        span = np.maximum(hi - lo - dur - 1, 1)
        s = lo + (rng.random((draws, len(sel))) * span).astype(int); e = np.minimum(s + dur, n - 1)
        ret = side * (o[e] - o[s]) / o[s] - mult * (hs[s] + hs[e]) / o[s]
        out[p] = np.percentile(ret.mean(axis=1), [50, 95])
    return out
