"""The 40 pre-registered theories (PREREGISTRATION.md). Each function returns (candles, Book) or None if not applicable."""
import numpy as np
import pandas as pd
import datetime as _dt
from engine import (EXNESS, CRYPTO, INDICES, NY, BER, Book, adx, atr, candles, ema, from_positions, local_minute, manage, psar, rsi, sma, supertrend)

ALL = EXNESS + CRYPTO
EPOCH_ORD = _dt.date(1970, 1, 1).toordinal()


def C(mkt, tf):
    return candles(mkt, tf)


# ---------------------------------------------------------------- A. trend
def a1(m, tf):
    c = C(m, tf); e9, e21 = ema(c.c, 9), ema(c.c, 21); return c, from_positions(c, np.where(e9 > e21, 1, -1))


def a2(m, tf):
    c = C(m, tf); s50, s200 = sma(c.c, 50), sma(c.c, 200); return c, from_positions(c, np.where(s200.isna(), 0, np.where(s50 > s200, 1, -1)))


def a3(m, tf):
    c = C(m, tf); mac = ema(c.c, 12) - ema(c.c, 26); return c, from_positions(c, np.where(mac > ema(mac, 9), 1, -1))


def a4(m, tf):
    c = C(m, tf); return c, from_positions(c, supertrend(c))


def a5(m, tf):
    c = C(m, tf); return c, from_positions(c, psar(c.h.values, c.l.values))


def a6(m, tf):
    c = C(m, tf); a, p, q = adx(c); pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        if a.iloc[i] > 25: cur = 1 if p.iloc[i] > q.iloc[i] else -1
        elif a.iloc[i] < 20: cur = 0
        pos[i] = cur
    return c, from_positions(c, pos)


def donchian(c, n_in, n_out):
    hi_in, lo_in = c.h.rolling(n_in).max().shift(), c.l.rolling(n_in).min().shift()
    hi_out, lo_out = c.h.rolling(n_out).max().shift(), c.l.rolling(n_out).min().shift(); pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        cl = c.c.iloc[i]
        if cur > 0 and cl < lo_out.iloc[i]: cur = 0
        elif cur < 0 and cl > hi_out.iloc[i]: cur = 0
        if cur == 0:
            if cl > hi_in.iloc[i]: cur = 1
            elif cl < lo_in.iloc[i]: cur = -1
        pos[i] = cur
    return pos


def a7(m, tf):
    c = C(m, tf); return c, from_positions(c, donchian(c, 20, 10))


def a8(m, tf):
    c = C(m, tf); return c, from_positions(c, donchian(c, 55, 20))


def a9(m, tf):
    c = C(m, tf); h, l = c.h, c.l
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2; kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((ten + kij) / 2).shift(26); sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    top, bot = np.maximum(sa, sb), np.minimum(sa, sb); pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        cl = c.c.iloc[i]
        if np.isnan(top.iloc[i]): continue
        if cur > 0 and cl < top.iloc[i]: cur = 0
        elif cur < 0 and cl > bot.iloc[i]: cur = 0
        if cur == 0:
            if cl > top.iloc[i] and ten.iloc[i] > kij.iloc[i]: cur = 1
            elif cl < bot.iloc[i] and ten.iloc[i] < kij.iloc[i]: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def a10(m, tf):
    c = C(m, tf); hc = ((c.o + c.h + c.l + c.c) / 4).values; ho = np.zeros(len(c)); ho[0] = (c.o.iloc[0] + c.c.iloc[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    return c, from_positions(c, np.where(hc > ho, 1, -1))


def a11(m, tf):
    c = C(m, tf); r = c.c / c.c.shift(20) - 1; return c, from_positions(c, np.sign(r.fillna(0)))


def a12(m, tf):
    c = C(m, tf); mid = sma(c.c, 20); sd = c.c.rolling(20).std(); a = atr(c, 20); em = ema(c.c, 20)
    sq = ((mid + 2 * sd) < (em + 1.5 * a)) & ((mid - 2 * sd) > (em - 1.5 * a)); pos = np.zeros(len(c)); cur = 0; armed = False
    for i in range(1, len(c)):
        cl = c.c.iloc[i]
        if cur > 0 and cl < mid.iloc[i]: cur = 0
        elif cur < 0 and cl > mid.iloc[i]: cur = 0
        if sq.iloc[i - 1]: armed = True
        if cur == 0 and armed:
            if cl > mid.iloc[i] + 2 * sd.iloc[i]: cur, armed = 1, False
            elif cl < mid.iloc[i] - 2 * sd.iloc[i]: cur, armed = -1, False
        pos[i] = cur
    return c, from_positions(c, pos)


def a13(m, tf):
    c = C(m, tf); d1 = C(m, "1d").set_index("day"); bk = Book(c); o, h, l, cl, day = c.o.values, c.h.values, c.l.values, c.c.values, c.day.values
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); ends = np.r_[starts[1:], len(c)]
    for s, e in zip(starts, ends):
        if day[s] - 1 not in d1.index or e - s < 3: continue
        pr = d1.loc[day[s] - 1]; rg = pr.h - pr.l; bu, bd = o[s] + 0.6 * rg, o[s] - 0.6 * rg
        for k in range(s, e):
            up, dn = h[k] >= bu, l[k] <= bd
            if up and dn: break
            if up or dn:
                side = 1 if up else -1; lvl = bu if up else bd; fill = o[k] if (side > 0 and o[k] > lvl) or (side < 0 and o[k] < lvl) else lvl
                bk.add(k, e - 1, side, fill, cl[e - 1]); break
    return c, bk


# ---------------------------------------------------------------- B. mean reversion (state machines)
def osc_machine(c, x, lo_cross, hi_cross, lo_exit, hi_exit):
    pos = np.zeros(len(c)); cur = 0; xv = x.values
    for i in range(1, len(c)):
        if np.isnan(xv[i]) or np.isnan(xv[i - 1]): continue
        if cur > 0 and xv[i] > lo_exit: cur = 0
        elif cur < 0 and xv[i] < hi_exit: cur = 0
        if cur == 0:
            if xv[i - 1] < lo_cross <= xv[i]: cur = 1
            elif xv[i - 1] > hi_cross >= xv[i]: cur = -1
        pos[i] = cur
    return pos


def b1(m, tf):
    c = C(m, tf); return c, from_positions(c, osc_machine(c, rsi(c.c, 14), 30, 70, 50, 50))


def b2(m, tf):
    c = C(m, tf); r2, s200, s5 = rsi(c.c, 2), sma(c.c, 200), sma(c.c, 5); pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        if np.isnan(s200.iloc[i]): continue
        cl = c.c.iloc[i]
        if cur > 0 and cl > s5.iloc[i]: cur = 0
        elif cur < 0 and cl < s5.iloc[i]: cur = 0
        if cur == 0:
            if cl > s200.iloc[i] and r2.iloc[i] < 10: cur = 1
            elif cl < s200.iloc[i] and r2.iloc[i] > 90: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def b3(m, tf):
    c = C(m, tf); mid = sma(c.c, 20); sd = c.c.rolling(20).std(); pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        if np.isnan(sd.iloc[i]): continue
        cl = c.c.iloc[i]
        if cur > 0 and cl >= mid.iloc[i]: cur = 0
        elif cur < 0 and cl <= mid.iloc[i]: cur = 0
        if cur == 0:
            if cl < mid.iloc[i] - 2 * sd.iloc[i]: cur = 1
            elif cl > mid.iloc[i] + 2 * sd.iloc[i]: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def b4(m, tf):
    c = C(m, tf); k = (100 * (c.c - c.l.rolling(14).min()) / (c.h.rolling(14).max() - c.l.rolling(14).min())).rolling(3).mean(); d = k.rolling(3).mean()
    pos = np.zeros(len(c)); cur = 0
    for i in range(1, len(c)):
        if np.isnan(d.iloc[i]) or np.isnan(d.iloc[i - 1]): continue
        if cur > 0 and k.iloc[i] > 50: cur = 0
        elif cur < 0 and k.iloc[i] < 50: cur = 0
        if cur == 0:
            if k.iloc[i - 1] <= d.iloc[i - 1] and k.iloc[i] > d.iloc[i] and k.iloc[i] < 20: cur = 1
            elif k.iloc[i - 1] >= d.iloc[i - 1] and k.iloc[i] < d.iloc[i] and k.iloc[i] > 80: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def b5(m, tf):
    c = C(m, tf); tp = (c.h + c.l + c.c) / 3; cci = (tp - sma(tp, 20)) / (0.015 * tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True))
    return c, from_positions(c, osc_machine(c, cci, -100, 100, 0, 0))


def b6(m, tf):
    c = C(m, tf); wr = -100 * (c.h.rolling(14).max() - c.c) / (c.h.rolling(14).max() - c.l.rolling(14).min())
    return c, from_positions(c, osc_machine(c, wr, -80, -20, -50, -50))


def b7(m, tf):
    if m in CRYPTO: return None
    c = C(m, tf); bk = Book(c); cl, day = c.c.values, c.day.values
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); ends = np.r_[starts[1:], len(c)]
    for s, e in zip(starts, ends):
        k = s + 8
        while k < e - 2:
            seg = cl[s:k + 1]; tw, sd = seg.mean(), seg.std()
            if sd > 0 and abs(cl[k] - tw) > 2 * sd:
                side = -1 if cl[k] > tw else 1; i0 = k + 1
                x, px = manage(c, i0, side, tw - side * 3 * sd, tw, last=e - 1); bk.add(i0, x, side, c.o.values[i0], px); k = x + 1
            else: k += 1
    return c, bk


def b8(m, tf):
    if m in CRYPTO: return None
    c = C(m, tf); d1 = C(m, "1d").set_index("day"); bk = Book(c); o, h, l, day = c.o.values, c.h.values, c.l.values, c.day.values
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); ends = np.r_[starts[1:], len(c)]
    for s, e in zip(starts, ends):
        if day[s] - 1 not in d1.index: continue
        pr = d1.loc[day[s] - 1]; P = (pr.h + pr.l + pr.c) / 3; r1, s1 = 2 * P - pr.l, 2 * P - pr.h; r2, s2 = P + (pr.h - pr.l), P - (pr.h - pr.l)
        for k in range(s, e - 1):
            if h[k] >= r1 and o[k] < r1: x, px = manage(c, k + 1, -1, r2, P, last=e - 1); bk.add(k, x, -1, r1, px); break
            if l[k] <= s1 and o[k] > s1: x, px = manage(c, k + 1, 1, s2, P, last=e - 1); bk.add(k, x, 1, s1, px); break
    return c, bk


def b9(m, tf):
    c = C(m, tf); s50 = sma(c.c, 50); bk = Book(c); o, h, l, cl = c.o.values, c.h.values, c.l.values, c.c.values; i = 50
    while i < len(c) - 2:
        hh, ll = h[i - 19:i + 1], l[i - 19:i + 1]; ih, il = int(np.argmax(hh)), int(np.argmin(ll)); H, L = hh[ih], ll[il]
        side = 1 if (cl[i] > s50.iloc[i] and ih > il) else (-1 if (cl[i] < s50.iloc[i] and il > ih) else 0)
        if side == 0 or H <= L: i += 1; continue
        lim = H - 0.618 * (H - L) if side > 0 else L + 0.618 * (H - L); stop, tp = (L, H) if side > 0 else (H, L); filled = None
        for k in range(i + 1, min(i + 11, len(c))):
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim): filled = k; break
        if filled is None: i += 1; continue
        pe = min(o[filled], lim) if side > 0 else max(o[filled], lim)
        x, px = manage(c, filled, side, stop, tp, tmax=20); bk.add(filled, x, side, pe, px); i = x + 1
    return c, bk


def px_trade(c, bk, i, side, stop, tmax=20):
    """Standard pattern exit: enter next open, stop given, 2R target."""
    if i + 1 >= len(c): return i
    pe = c.o.values[i + 1]; R = side * (pe - stop)
    if R <= 0: return i
    x, px = manage(c, i + 1, side, stop, pe + side * 2 * R, tmax=tmax); bk.add(i + 1, x, side, pe, px); return x


def b10(m, tf):
    c = C(m, tf); bk = Book(c); h, l, cl = c.h.values, c.l.values, c.c.values; i = 21
    while i < len(c) - 1:
        pl = l[i - 20:i]; ph = h[i - 20:i]; il, ih = int(np.argmin(pl)), int(np.argmax(ph))
        if l[i] < pl[il] and il <= 15 and cl[i] > pl[il]: i = px_trade(c, bk, i, 1, l[i]) + 1; continue
        if h[i] > ph[ih] and ih <= 15 and cl[i] < ph[ih]: i = px_trade(c, bk, i, -1, h[i]) + 1; continue
        i += 1
    return c, bk


# ---------------------------------------------------------------- C. patterns
def pattern(m, tf, test):
    c = C(m, tf); bk = Book(c); o, h, l, cl = c.o.values, c.h.values, c.l.values, c.c.values; i = 3
    while i < len(c) - 1:
        r = test(o, h, l, cl, i)
        if r: i = px_trade(c, bk, i, r[0], r[1]) + 1
        else: i += 1
    return c, bk


def c1(m, tf):
    def t(o, h, l, c, i):
        if c[i - 1] < o[i - 1] and c[i] > o[i] and c[i] >= o[i - 1] and o[i] <= c[i - 1]: return (1, min(l[i], l[i - 1]))
        if c[i - 1] > o[i - 1] and c[i] < o[i] and c[i] <= o[i - 1] and o[i] >= c[i - 1]: return (-1, max(h[i], h[i - 1]))
    return pattern(m, tf, t)


def c2(m, tf):
    def t(o, h, l, c, i):
        rg = h[i] - l[i]; b = abs(c[i] - o[i])
        if rg <= 0: return None
        if (min(o[i], c[i]) - l[i]) >= 2 * b and min(o[i], c[i]) >= l[i] + 2 / 3 * rg: return (1, l[i])
        if (h[i] - max(o[i], c[i])) >= 2 * b and max(o[i], c[i]) <= l[i] + 1 / 3 * rg: return (-1, h[i])
    return pattern(m, tf, t)


def stop_break(m, tf, setup, valid):
    """Stop orders at a setup candle's high/low (C3 inside bar, C4 NR7); first break fills; stop at the other side, 2R, 20 candles."""
    c = C(m, tf); bk = Book(c); o, h, l = c.o.values, c.h.values, c.l.values; i = 8
    while i < len(c) - 1:
        lv = setup(h, l, i)
        if not lv: i += 1; continue
        hi, lo = lv; R = hi - lo; done = False
        for k in range(i + 1, min(i + 1 + valid, len(c))):
            up, dn = h[k] >= hi, l[k] <= lo
            if up and dn: break                                      # ambiguous candle: skip this setup
            if up or dn:
                side = 1 if up else -1; lvl = hi if up else lo; pe = max(o[k], lvl) if up else min(o[k], lvl); stop = lo if up else hi
                x, px = manage(c, k, side, stop, pe + side * 2 * R, tmax=20); bk.add(k, x, side, pe, px); i = x + 1; done = True; break
        if not done: i += 1
    return c, bk


def c3(m, tf):
    return stop_break(m, tf, lambda h, l, i: (h[i - 1], l[i - 1]) if (h[i] < h[i - 1] and l[i] > l[i - 1]) else None, 5)


def c4(m, tf):
    return stop_break(m, tf, lambda h, l, i: (h[i], l[i]) if (h[i] - l[i]) <= (h[i - 6:i + 1] - l[i - 6:i + 1]).min() else None, 3)


def c5(m, tf):
    def t(o, h, l, c, i):
        b0, b1, b2 = abs(c[i - 2] - o[i - 2]), abs(c[i - 1] - o[i - 1]), abs(c[i] - o[i])
        if c[i - 2] < o[i - 2] and b1 < 0.5 * b0 and c[i] > o[i] and c[i] > (o[i - 2] + c[i - 2]) / 2: return (1, min(l[i - 2:i + 1]))
        if c[i - 2] > o[i - 2] and b1 < 0.5 * b0 and c[i] < o[i] and c[i] < (o[i - 2] + c[i - 2]) / 2: return (-1, max(h[i - 2:i + 1]))
    return pattern(m, tf, t)


def c6(m, tf):
    def t(o, h, l, c, i):
        if all(c[k] > o[k] and c[k] > c[k - 1] for k in (i - 2, i - 1, i)): return (1, l[i - 2])
        if all(c[k] < o[k] and c[k] < c[k - 1] for k in (i - 2, i - 1, i)): return (-1, h[i - 2])
    return pattern(m, tf, t)


# ---------------------------------------------------------------- D. sessions / ICT
def day_slices(c):
    day = c.day.values; s = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); return list(zip(s, np.r_[s[1:], len(c)]))


def utc_min(c):
    return (c.m.values % 1440)


def d1_asian(m, tf):
    c = C(m, tf); bk = Book(c); o, h, l, cl = c.o.values, c.h.values, c.l.values, c.c.values; um = utc_min(c)
    for s, e in day_slices(c):
        a = [k for k in range(s, e) if um[k] < 7 * 60 and c.m.values[k] // 1440 == c.m.values[e - 1] // 1440]
        if len(a) < 3: continue
        hi, lo = h[a].max(), l[a].min(); R = hi - lo
        if R <= 0: continue
        win = [k for k in range(a[-1] + 1, e) if 7 * 60 <= um[k] < 12 * 60]; last = [k for k in range(a[-1] + 1, e) if um[k] < 16 * 60]
        if not win or not last: continue
        for k in win:
            up, dn = h[k] >= hi, l[k] <= lo
            if up and dn: break
            if up or dn:
                side = 1 if up else -1; pe = max(o[k], hi) if up else min(o[k], lo)
                x, px = manage(c, k, side, lo if up else hi, pe + side * R, last=last[-1]); bk.add(k, x, side, pe, px); break
    return c, bk


def d2_judas(m, tf):
    c = C(m, tf); bk = Book(c); h, l, cl, o = c.h.values, c.l.values, c.c.values, c.o.values; um = utc_min(c)
    for s, e in day_slices(c):
        a = [k for k in range(s, e) if um[k] < 7 * 60 and c.m.values[k] // 1440 == c.m.values[e - 1] // 1440]
        if len(a) < 3: continue
        hi, lo = h[a].max(), l[a].min(); win = [k for k in range(a[-1] + 1, e) if 7 * 60 <= um[k] < 10 * 60]; last = [k for k in range(a[-1] + 1, e) if um[k] < 16 * 60]
        if not win or not last: continue
        sh, sl = -np.inf, np.inf
        for k in win:
            sh, sl = max(sh, h[k]), min(sl, l[k])
            if k + 1 >= e: break
            if sh > hi and cl[k] < hi: x, px = manage(c, k + 1, -1, sh, lo, last=last[-1]); bk.add(k + 1, x, -1, o[k + 1], px); break
            if sl < lo and cl[k] > lo: x, px = manage(c, k + 1, 1, sl, hi, last=last[-1]); bk.add(k + 1, x, 1, o[k + 1], px); break
    return c, bk


def d3_silver(m, tf):
    if m in CRYPTO: return None
    c = C(m, tf); bk = Book(c); o, h, l, mm = c.o.values, c.h.values, c.l.values, c.m.values
    for s, e in day_slices(c):
        dord = EPOCH_ORD + int(c.day.values[s])
        t930, t10, t11, t12 = (local_minute(dord, NY, *x) for x in ((9, 30), (10, 0), (11, 0), (12, 0)))
        pre = [k for k in range(s, e) if t930 <= mm[k] < t10]; win = [k for k in range(s, e) if t10 <= mm[k] < t11]; last = [k for k in range(s, e) if mm[k] < t12]
        if len(pre) < 4 or len(win) < 4 or not last: continue
        ph, pl = h[pre].max(), l[pre].min(); swept_lo = swept_hi = False; trade = None
        for k in win:
            swept_lo |= l[k] < pl; swept_hi |= h[k] > ph
            if k - 2 < s: continue
            if swept_lo and l[k] > h[k - 2]: trade = (1, l[k], l[k - 2], k); break
            if swept_hi and h[k] < l[k - 2]: trade = (-1, h[k], h[k - 2], k); break
        if not trade: continue
        side, lim, stop, k0 = trade; R = side * (lim - stop)
        if R <= 0: continue
        for k in range(k0 + 1, min(len(c), (win[-1] + 1))):
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim):
                pe = min(o[k], lim) if side > 0 else max(o[k], lim); x, px = manage(c, k, side, stop, lim + side * 2 * R, last=last[-1]); bk.add(k, x, side, pe, px); break
    return c, bk


def d4_fvg(m, tf):
    c = C(m, tf); bk = Book(c); o, h, l = c.o.values, c.h.values, c.l.values; i = 2
    while i < len(c) - 1:
        side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
        if not side: i += 1; continue
        lim = h[i - 2] if side > 0 else l[i - 2]; stop = l[i - 2] if side > 0 else h[i - 2]; R = side * (lim - stop); done = False
        if R <= 0: i += 1; continue
        for k in range(i + 1, min(i + 11, len(c))):
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim):
                pe = min(o[k], lim) if side > 0 else max(o[k], lim); x, px = manage(c, k, side, stop, lim + side * 2 * R, tmax=20); bk.add(k, x, side, pe, px); i = x + 1; done = True; break
        if not done: i += 1
    return c, bk


def cash_times(m, dord):
    if m == "DE30m": return local_minute(dord, BER, 9, 0), local_minute(dord, BER, 17, 30)
    return local_minute(dord, NY, 9, 30), local_minute(dord, NY, 16, 0)


def d5_gap(m, tf):
    if m not in INDICES: return None
    c = C(m, tf); bk = Book(c); mm, o, cl = c.m.values, c.o.values, c.c.values; prev_close = None
    for s, e in day_slices(c):
        dord = EPOCH_ORD + int(c.day.values[s]); op, clo = cash_times(m, dord)
        i0, i1 = int(np.searchsorted(mm, op)), int(np.searchsorted(mm, clo)) - 1
        if i0 >= len(c) or mm[i0] != op or i1 <= i0: prev_close = None; continue
        if prev_close is not None:
            g = o[i0] - prev_close
            if abs(g) > 4 * c.hs.values[i0]:
                side = -int(np.sign(g)); x, px = manage(c, i0, side, o[i0] - side * abs(g), prev_close, last=i1); bk.add(i0, x, side, o[i0], px)
        prev_close = cl[i1]
    return c, bk


def d6_pdh(m, tf):
    c = C(m, tf); d1 = C(m, "1d").set_index("day"); bk = Book(c); cl, day = c.c.values, c.day.values; i = 1
    while i < len(c) - 1:
        dd = day[i]
        if dd - 1 not in d1.index: i += 1; continue
        pr = d1.loc[dd - 1]; mid = (pr.h + pr.l) / 2; nxt = i
        if cl[i] > pr.h and cl[i - 1] <= pr.h and day[i - 1] == dd: nxt = px_trade(c, bk, i, 1, mid)
        elif cl[i] < pr.l and cl[i - 1] >= pr.l and day[i - 1] == dd: nxt = px_trade(c, bk, i, -1, mid)
        i = nxt + 1
    return c, bk


# ---------------------------------------------------------------- E. calendar
def e1_tuesday(m, tf):
    if m not in INDICES: return None
    c = C(m, tf); bk = Book(c); mm, o = c.m.values, c.o.values; closes = {}
    for s, e in day_slices(c):
        dord = EPOCH_ORD + int(c.day.values[s]); _, clo = cash_times(m, dord); i1 = int(np.searchsorted(mm, clo)) - 1   # last bar before the cash close
        if i1 >= 0 and clo - mm[i1] <= 5: closes[dord] = i1
    for d, i1 in closes.items():
        dd = _dt.date.fromordinal(d)
        if dd.weekday() != 0 or (d - 3) not in closes or (d + 1) not in closes: continue
        cl = c.c.values
        if cl[i1] < cl[closes[d - 3]]: bk.add(i1, closes[d + 1], 1, cl[i1], cl[closes[d + 1]])
    return c, bk


def e2_tom(m, tf):
    c = C(m, tf); bk = Book(c); mon = pd.to_datetime(c.day * 86400, unit="s").dt.month.values; o = c.o.values
    first = np.flatnonzero(np.r_[False, mon[1:] != mon[:-1]])
    for f in first:
        if f + 3 < len(c): bk.add(f, f + 3, 1, o[f], o[f + 3])
    return c, bk


def e3_overnight(m, tf):
    if m not in INDICES: return None
    c = C(m, tf); bk = Book(c); mm, o = c.m.values, c.o.values; days = sorted({EPOCH_ORD + int(x) for x in np.unique(c.day.values)})
    for d in days:
        _, clo = cash_times(m, d); op, _ = cash_times(m, d + (3 if pd.Timestamp.fromordinal(d).weekday() == 4 else 1))
        i, j = int(np.searchsorted(mm, clo)) - 1, int(np.searchsorted(mm, op))       # last bar before the close -> first bar of the open
        if i >= 0 and j < len(c) and clo - mm[i] <= 5 and abs(mm[j] - op) <= 5 and j > i: bk.add(i, j, 1, c.c.values[i], o[j])
    return c, bk


def e4_weekend(m, tf):
    if m not in CRYPTO: return None
    c = C(m, tf); bk = Book(c); mm, o = c.m.values, c.o.values; wd = pd.to_datetime(mm * 60, unit="s").weekday.values; hr = (mm % 1440) // 60
    for i in np.flatnonzero((wd == 4) & (hr == 0)):
        j = i + 72
        if j < len(c): bk.add(i, j, 1, o[i], o[j])
    return c, bk


REGISTRY = [
    ("A1", "trend", ["1h"], ALL, a1), ("A2", "trend", ["4h"], ALL, a2), ("A3", "trend", ["1h", "4h"], ALL, a3), ("A4", "trend", ["1h", "4h"], ALL, a4),
    ("A5", "trend", ["1h"], ALL, a5), ("A6", "trend", ["1h"], ALL, a6), ("A7", "trend", ["1d", "4h"], ALL, a7), ("A8", "trend", ["4h"], ALL, a8),
    ("A9", "trend", ["4h"], ALL, a9), ("A10", "trend", ["1h"], ALL, a10), ("A11", "trend", ["1d"], ALL, a11), ("A12", "trend", ["1h"], ALL, a12),
    ("A13", "trend", ["1h"], ALL, a13),
    ("B1", "meanrev", ["15m", "1h"], ALL, b1), ("B2", "meanrev", ["1d", "1h"], ALL, b2), ("B3", "meanrev", ["1h"], ALL, b3), ("B4", "meanrev", ["1h"], ALL, b4),
    ("B5", "meanrev", ["1h"], ALL, b5), ("B6", "meanrev", ["1h"], ALL, b6), ("B7", "meanrev", ["15m"], EXNESS, b7), ("B8", "meanrev", ["15m"], EXNESS, b8),
    ("B9", "meanrev", ["1h"], ALL, b9), ("B10", "meanrev", ["1d"], ALL, b10),
    ("C1", "pattern", ["1h"], ALL, c1), ("C2", "pattern", ["1h"], ALL, c2), ("C3", "pattern", ["1h", "1d"], ALL, c3), ("C4", "pattern", ["1d"], ALL, c4),
    ("C5", "pattern", ["1h"], ALL, c5), ("C6", "pattern", ["1h"], ALL, c6),
    ("D1", "session", ["1m"], EXNESS, d1_asian), ("D1", "session", ["1h"], CRYPTO, d1_asian), ("D2", "session", ["15m"], EXNESS, d2_judas),
    ("D2", "session", ["1h"], CRYPTO, d2_judas), ("D3", "session", ["5m"], EXNESS, d3_silver), ("D4", "session", ["1h"], ALL, d4_fvg),
    ("D5", "session", ["1m"], INDICES, d5_gap), ("D6", "session", ["1h"], ALL, d6_pdh),
    ("E1", "calendar", ["1m"], INDICES, e1_tuesday), ("E2", "calendar", ["1d"], ALL, e2_tom), ("E3", "calendar", ["1m"], INDICES, e3_overnight),
    ("E4", "calendar", ["1h"], CRYPTO, e4_weekend),
]
