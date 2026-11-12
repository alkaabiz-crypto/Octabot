"""Batch F theories (PREREGISTRATION.md, addendum 1). Same conventions as theories.py."""
import numpy as np
import pandas as pd
from engine import Book, atr, ema, from_positions, manage, sma, rsi
from theories import ALL, C, px_trade


def fractals(h, l):
    """Swing high/low flags at candle i (5-candle window), usable only from candle i+2."""
    n = len(h); sh = np.zeros(n, bool); sl = np.zeros(n, bool)
    for i in range(2, n - 2):
        sh[i] = h[i] == h[i - 2:i + 3].max(); sl[i] = l[i] == l[i - 2:i + 3].min()
    return sh, sl


def linreg_last(x, n):
    """Value of the least-squares line at the last point of each rolling window (TradingView linreg(x, n, 0))."""
    idx = np.arange(n); xm = idx.mean(); den = ((idx - xm) ** 2).sum()
    def f(w):
        b = ((idx - xm) * (w - w.mean())).sum() / den; return w.mean() + b * (n - 1 - xm)
    return x.rolling(n).apply(f, raw=True)


def f1(m, tf):
    c = C(m, tf); mid = sma(c.c, 20); sd = c.c.rolling(20).std(); a = atr(c, 20); em = ema(c.c, 20)
    sq = ((mid + 2 * sd) < (em + 1.5 * a)) & ((mid - 2 * sd) > (em - 1.5 * a))
    val = linreg_last(c.c - ((c.h.rolling(20).max() + c.l.rolling(20).min()) / 2 + mid) / 2, 20).values
    pos = np.zeros(len(c)); cur = 0; sqv = sq.values
    for i in range(1, len(c)):
        if np.isnan(val[i]): continue
        if cur != 0 and np.sign(val[i]) != cur: cur = 0
        if cur == 0 and sqv[i - 1] and not sqv[i]: cur = int(np.sign(val[i]))
        pos[i] = cur
    return c, from_positions(c, pos)


def f2(m, tf):
    c = C(m, tf); a = atr(c, 10).values; x = c.c.values; n = len(x); stop = np.zeros(n); side = np.zeros(n)
    for i in range(1, n):
        loss = 1.0 * a[i]; ps = stop[i - 1]
        if x[i] > ps and x[i - 1] > ps: stop[i] = max(ps, x[i] - loss)
        elif x[i] < ps and x[i - 1] < ps: stop[i] = min(ps, x[i] + loss)
        else: stop[i] = x[i] - loss if x[i] > ps else x[i] + loss
        side[i] = 1 if x[i] > stop[i] else -1
    side[:11] = 0; return c, from_positions(c, side)


def f3(m, tf):
    c = C(m, tf); a = atr(c, 22); ls = (c.h.rolling(22).max() - 3 * a).values; ss = (c.l.rolling(22).min() + 3 * a).values; x = c.c.values
    pos = np.zeros(len(c)); cur = 0
    for i in range(1, len(c)):
        if np.isnan(ls[i - 1]): continue
        if x[i] > ss[i - 1]: cur = 1
        elif x[i] < ls[i - 1]: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def f4(m, tf):
    c = C(m, tf); sh, sl = sma(c.h, 10).values, sma(c.l, 10).values; x = c.c.values; pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        if np.isnan(sh[i]): continue
        if x[i] > sh[i]: cur = 1
        elif x[i] < sl[i]: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def wma(x, n):
    w = np.arange(1, n + 1); return x.rolling(n).apply(lambda v: (v * w).sum() / w.sum(), raw=True)


def f5(m, tf):
    c = C(m, tf); h = wma(2 * wma(c.c, 27) - wma(c.c, 55), int(np.sqrt(55))); d = h.diff()
    return c, from_positions(c, np.where(d.isna(), 0, np.sign(d)))


def f6(m, tf):
    c = C(m, tf); e200 = ema(c.c, 200).values; mac = ema(c.c, 12) - ema(c.c, 26); sig = ema(mac, 9); mv, sv = mac.values, sig.values
    bk = Book(c); x, h, l, o = c.c.values, c.h.values, c.l.values, c.o.values; i = 200
    while i < len(c) - 1:
        up = mv[i - 1] <= sv[i - 1] and mv[i] > sv[i] and mv[i] < 0 and x[i] > e200[i]
        dn = mv[i - 1] >= sv[i - 1] and mv[i] < sv[i] and mv[i] > 0 and x[i] < e200[i]
        if up or dn:
            side = 1 if up else -1; stop = l[i - 9:i + 1].min() if up else h[i - 9:i + 1].max(); pe = o[i + 1]; R = side * (pe - stop)
            if R > 0:
                k, px = manage(c, i + 1, side, stop, pe + side * 1.5 * R, tmax=50); bk.add(i + 1, k, side, pe, px); i = k + 1; continue
        i += 1
    return c, bk


def f7(m, tf):
    c = C(m, tf); r = rsi(c.c, 14).values; h, l = c.h.values, c.l.values; sh, sl = fractals(h, l); bk = Book(c); last_l = last_h = None; i = 4; nxt = 0
    while i < len(c) - 1:
        j = i - 2
        if sl[j]:
            if last_l is not None and j - last_l <= 30 and l[j] < l[last_l] and r[j] > r[last_l] and r[j] < 40 and i >= nxt: nxt = px_trade(c, bk, i, 1, l[j]) + 1
            last_l = j
        if sh[j]:
            if last_h is not None and j - last_h <= 30 and h[j] > h[last_h] and r[j] < r[last_h] and r[j] > 60 and i >= nxt: nxt = px_trade(c, bk, i, -1, h[j]) + 1
            last_h = j
        i += 1
    return c, bk


def f8(m, tf):
    c = C(m, tf); e20, e50, e200 = ema(c.c, 20).values, ema(c.c, 50).values, ema(c.c, 200).values; bk = Book(c); h, l, x = c.h.values, c.l.values, c.c.values; i = 200
    while i < len(c) - 1:
        if e50[i] > e200[i] and l[i] <= e20[i] < x[i]: i = px_trade(c, bk, i, 1, l[i]) + 1; continue
        if e50[i] < e200[i] and h[i] >= e20[i] > x[i]: i = px_trade(c, bk, i, -1, h[i]) + 1; continue
        i += 1
    return c, bk


def f9(m, tf):
    c = C(m, tf); o, h, l, x = c.o.values, c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); bk = Book(c); lh = ll = None; i = 4
    while i < len(c) - 1:
        if sh[i - 2]: lh = i - 2
        if sl[i - 2]: ll = i - 2
        trade = None
        if lh is not None and x[i] > h[lh] and x[i - 1] <= h[lh]:
            k = next((q for q in range(i - 1, max(lh, i - 20), -1) if x[q] < o[q]), None)
            if k is not None: trade = (1, h[k], l[k]); lh = None
        elif ll is not None and x[i] < l[ll] and x[i - 1] >= l[ll]:
            k = next((q for q in range(i - 1, max(ll, i - 20), -1) if x[q] > o[q]), None)
            if k is not None: trade = (-1, l[k], h[k]); ll = None
        if trade:
            side, lim, stop = trade; R = side * (lim - stop)
            if R > 0:
                for k2 in range(i + 1, min(i + 21, len(c))):
                    if (side > 0 and l[k2] <= lim) or (side < 0 and h[k2] >= lim):
                        pe = min(o[k2], lim) if side > 0 else max(o[k2], lim); e, px = manage(c, k2, side, stop, lim + side * 2 * R, tmax=20, intrabar=True)
                        bk.add(k2, e, side, pe, px); i = e; break
        i += 1
    return c, bk


def f10(m, tf):
    c = C(m, tf); a = atr(c, 14).values; o, h, l, x = c.o.values, c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); bk = Book(c)
    lows, highs = [], []; pend = None; i = 4
    while i < len(c) - 1:
        j = i - 2
        if sl[j]:
            for p in lows[::-1]:
                if 5 <= j - p <= 40 and abs(l[j] - l[p]) <= 0.5 * a[j]: pend = (1, h[p:j + 1].max(), min(l[p], l[j])); break
            lows.append(j)
        if sh[j]:
            for p in highs[::-1]:
                if 5 <= j - p <= 40 and abs(h[j] - h[p]) <= 0.5 * a[j]: pend = (-1, l[p:j + 1].min(), max(h[p], h[j])); break
            highs.append(j)
        if pend:
            side, neck, ext = pend
            if (side > 0 and x[i] > neck) or (side < 0 and x[i] < neck):
                pe = o[i + 1]; stop = ext; tgt = neck + (neck - ext)
                if side * (pe - stop) > 0 and side * (tgt - pe) > 0:
                    k, px = manage(c, i + 1, side, stop, tgt, tmax=20); bk.add(i + 1, k, side, pe, px); i = k + 1; pend = None; continue
                pend = None
            elif (side > 0 and x[i] < ext) or (side < 0 and x[i] > ext): pend = None
        i += 1
    return c, bk


def f11(m, tf):
    c = C(m, tf); h, l, x = c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); bk = Book(c); seq = []; i = 4
    while i < len(c) - 1:
        j = i - 2
        if sl[j]: seq.append(("L", j))
        if sh[j]: seq.append(("H", j))
        seq = seq[-3:]; done = False
        if len(seq) == 3:
            (t1, p1), (t2, p2), (t3, p3) = seq
            if (t1, t2, t3) == ("L", "H", "L") and l[p3] > l[p1] and x[i] > h[p2]: i = px_trade(c, bk, i, 1, l[p3]) + 1; seq = []; done = True
            elif (t1, t2, t3) == ("H", "L", "H") and h[p3] < h[p1] and x[i] < l[p2]: i = px_trade(c, bk, i, -1, h[p3]) + 1; seq = []; done = True
        if not done: i += 1
    return c, bk


def f12(m, tf):
    c = C(m, tf); a = atr(c, 14).values; o, h, l, x = c.o.values, c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); bk = Book(c)
    hs, ls = [], []; pend = None; i = 4
    while i < len(c) - 1:
        j = i - 2
        if sh[j]:
            hs.append(j)
            if len(hs) >= 3:
                p1, p2, p3 = hs[-3:]
                if h[p2] - max(h[p1], h[p3]) >= 0.5 * a[j] and abs(h[p1] - h[p3]) <= a[j] and p3 - p1 <= 60: pend = (-1, l[p1:p3 + 1].min(), h[p3], h[p2])
        if sl[j]:
            ls.append(j)
            if len(ls) >= 3:
                p1, p2, p3 = ls[-3:]
                if min(l[p1], l[p3]) - l[p2] >= 0.5 * a[j] and abs(l[p1] - l[p3]) <= a[j] and p3 - p1 <= 60: pend = (1, h[p1:p3 + 1].max(), l[p3], l[p2])
        if pend:
            side, neck, shoulder, head = pend
            if (side < 0 and x[i] < neck) or (side > 0 and x[i] > neck):
                pe = o[i + 1]; tgt = neck - (head - neck) if side < 0 else neck + (neck - head)
                if side * (pe - shoulder) > 0 and side * (tgt - pe) > 0:
                    k, px = manage(c, i + 1, side, shoulder, tgt, tmax=40); bk.add(i + 1, k, side, pe, px); i = k + 1; pend = None; continue
                pend = None
            elif (side < 0 and x[i] > shoulder) or (side > 0 and x[i] < shoulder): pend = None
        i += 1
    return c, bk


REGISTRY_F = [
    ("F1", "retail", ["1h", "4h"], ALL, f1), ("F2", "retail", ["1h", "4h"], ALL, f2), ("F3", "retail", ["1h", "4h"], ALL, f3), ("F4", "retail", ["1h", "4h"], ALL, f4),
    ("F5", "retail", ["1h", "4h"], ALL, f5), ("F6", "retail", ["1h"], ALL, f6), ("F7", "retail", ["1h"], ALL, f7), ("F8", "retail", ["1h"], ALL, f8),
    ("F9", "smc_pattern", ["1h"], ALL, f9), ("F10", "smc_pattern", ["1h", "1d"], ALL, f10), ("F11", "smc_pattern", ["1h"], ALL, f11), ("F12", "smc_pattern", ["1h"], ALL, f12),
]
