"""Batch G theories (PREREGISTRATION.md, addendum 2). Same conventions as theories.py."""
import numpy as np
import pandas as pd
from engine import (EXNESS, CRYPTO, INDICES, NY, BER, Book, atr, ema, from_positions, local_minute, manage, sma)
from theories import ALL, C, EPOCH_ORD, day_slices
from theories_f import fractals

SESS = {"US500m": (NY, (16, 0), (10, 0), (15, 30), (16, 0)), "USTECm": (NY, (16, 0), (10, 0), (15, 30), (16, 0)),
        "DE30m": (BER, (17, 30), (9, 30), (17, 0), (17, 30)), "XAUUSDm": (NY, (13, 30), (8, 50), (13, 0), (13, 30)),
        "USOILm": (NY, (14, 30), (9, 30), (14, 0), (14, 30))}


def last_before(mm, t, tol=10):
    i = int(np.searchsorted(mm, t, side="right")) - 1
    return i if i >= 0 and t - mm[i] <= tol else None


def g1(m, tf):
    if m not in SESS: return None
    c = C(m, tf); bk = Book(c); mm, o, cl = c.m.values, c.o.values, c.c.values; tz, pc, fh, ls, le = SESS[m]
    days = sorted({EPOCH_ORD + int(x) for x in np.unique(c.day.values)}); prev = None
    for d in days:
        if pd.Timestamp.fromordinal(d).weekday() >= 5: continue
        i_close = last_before(mm, local_minute(d, tz, *le)); i_first = last_before(mm, local_minute(d, tz, *fh))
        ls_t = local_minute(d, tz, *ls); i_ls = int(np.searchsorted(mm, ls_t))
        if prev is not None and i_first is not None and i_close is not None and i_ls < len(c) and mm[i_ls] - ls_t <= 5 and i_ls < i_close:
            r = cl[i_first] / cl[prev] - 1
            if r != 0: bk.add(i_ls, i_close, int(np.sign(r)), o[i_ls], cl[i_close])
        prev = last_before(mm, local_minute(d, tz, *pc))
    return c, bk


def g2(m, tf):
    c = C(m, tf); d1 = C(m, "1d").set_index("day"); bk = Book(c); o, h, l, cl, day = c.o.values, c.h.values, c.l.values, c.c.values, c.day.values
    days = d1.index.values
    for s, e in day_slices(c):
        k = np.searchsorted(days, day[s])
        if k < 4 or e - s < 3: continue
        p = d1.loc[days[k - 4:k]]; R = max(p.h.max() - p.c.min(), p.c.max() - p.l.min()); up, dn = o[s] + 0.5 * R, o[s] - 0.5 * R
        pos, pe, pi = 0, None, None
        for q in range(s, e):
            hu, hd = h[q] >= up, l[q] <= dn
            if hu and hd: break                                      # ambiguous candle: stop trading this day
            if hu and pos <= 0:
                f = max(o[q], up)
                if pos < 0: bk.add(pi, q, -1, pe, f)
                pos, pe, pi = 1, f, q
            elif hd and pos >= 0:
                f = min(o[q], dn)
                if pos > 0: bk.add(pi, q, 1, pe, f)
                pos, pe, pi = -1, f, q
        if pos != 0: bk.add(pi, e - 1, pos, pe, cl[e - 1])
    return c, bk


def smma(x, n):
    return x.ewm(alpha=1 / n, adjust=False).mean()


def g3(m, tf):
    c = C(m, tf); med = (c.h + c.l) / 2; jaw, teeth, lips = smma(med, 13).shift(8).values, smma(med, 8).shift(5).values, smma(med, 5).shift(3).values
    h, l, x = c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); pos = np.zeros(len(c)); cur = 0; uf = df = None
    for i in range(4, len(c)):
        if sh[i - 2]: uf = h[i - 2]
        if sl[i - 2]: df = l[i - 2]
        if np.isnan(jaw[i]): continue
        if cur > 0 and x[i] < teeth[i]: cur = 0
        elif cur < 0 and x[i] > teeth[i]: cur = 0
        if cur == 0:
            if lips[i] > teeth[i] > jaw[i] and uf is not None and uf > teeth[i] and x[i] > uf: cur = 1
            elif lips[i] < teeth[i] < jaw[i] and df is not None and df < teeth[i] and x[i] < df: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def g4(m, tf):
    c = C(m, tf); up = c.h.rolling(26).apply(lambda v: 100 * np.argmax(v) / 25, raw=True); dn = c.l.rolling(26).apply(lambda v: 100 * np.argmin(v) / 25, raw=True)
    return c, from_positions(c, np.where(up.isna(), 0, np.where(up > dn, 1, -1)))


def g5(m, tf):
    c = C(m, tf); tr = pd.concat([c.h - c.l, (c.h - c.c.shift()).abs(), (c.l - c.c.shift()).abs()], axis=1).max(axis=1)
    vp, vm = (c.h - c.l.shift()).abs().rolling(14).sum() / tr.rolling(14).sum(), (c.l - c.h.shift()).abs().rolling(14).sum() / tr.rolling(14).sum()
    return c, from_positions(c, np.where(vp.isna(), 0, np.where(vp > vm, 1, -1)))


def g6(m, tf):
    c = C(m, tf); t3 = ema(ema(ema(c.c, 15), 15), 15); trix = 100 * t3.pct_change(); sig = ema(trix, 9)
    return c, from_positions(c, np.where(trix.isna() | (np.arange(len(c)) < 60), 0, np.where(trix > sig, 1, -1)))


def g7(m, tf):
    c = C(m, tf); roc = lambda n: 100 * (c.c / c.c.shift(n) - 1)
    kst = sma(roc(10), 10) + 2 * sma(roc(15), 10) + 3 * sma(roc(20), 10) + 4 * sma(roc(30), 15); sig = sma(kst, 9)
    return c, from_positions(c, np.where(sig.isna(), 0, np.where(kst > sig, 1, -1)))


def g8(m, tf):
    c = C(m, tf); x = c.c.values; n = len(x); k = np.full(n, np.nan); fast, slow = 2 / 3, 2 / 31
    for i in range(10, n):
        ch = abs(x[i] - x[i - 10]); vol = np.abs(np.diff(x[i - 10:i + 1])).sum(); er = ch / vol if vol > 0 else 0
        scv = (er * (fast - slow) + slow) ** 2; k[i] = x[i] if np.isnan(k[i - 1]) else k[i - 1] + scv * (x[i] - k[i - 1])
    d = np.r_[0, np.diff(k)]; return c, from_positions(c, np.where(np.isnan(d), 0, np.sign(d)))


def g9(m, tf):
    c = C(m, tf); mid = ema(c.c, 20).values; a = atr(c, 20).values; x = c.c.values; pos = np.zeros(len(c)); cur = 0
    for i in range(20, len(c)):
        if cur > 0 and x[i] < mid[i]: cur = 0
        elif cur < 0 and x[i] > mid[i]: cur = 0
        if cur == 0:
            if x[i] > mid[i] + 2 * a[i]: cur = 1
            elif x[i] < mid[i] - 2 * a[i]: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos)


def g10(m, tf):
    c = C(m, tf); z = ((c.c - sma(c.c, 20)) / c.c.rolling(20).std()).values; pos = np.zeros(len(c)); cur = 0
    for i in range(len(c)):
        if np.isnan(z[i]): continue
        if cur > 0 and z[i] > 0: cur = 0
        elif cur < 0 and z[i] < 0: cur = 0
        if cur == 0:
            if z[i] < -2: cur = 1
            elif z[i] > 2: cur = -1
        pos[i] = cur
    return c, from_positions(c, pos, flat_at_day_end=True)


def g13(m, tf):
    if m not in CRYPTO: return None
    c = C(m, tf); bk = Book(c); mm, o = c.m.values, c.o.values; hr = (mm % 1440) // 60
    for i in np.flatnonzero(hr == 21):
        if i + 2 < len(c) and mm[i + 2] - mm[i] == 120: bk.add(i, i + 2, 1, o[i], o[i + 2])
    return c, bk


def g14(m, tf):
    if m not in CRYPTO: return None
    c = C(m, tf); bk = Book(c); mm, o = c.m.values, c.o.values; wd = pd.to_datetime(mm * 60, unit="s").weekday.values; hr = (mm % 1440) // 60
    for i in np.flatnonzero((wd == 0) & (hr == 0)):
        if i + 24 < len(c) and mm[i + 24] - mm[i] == 1440: bk.add(i, i + 24, 1, o[i], o[i + 24])
    return c, bk


REGISTRY_G = [
    ("G1", "session", ["1m"], list(SESS), g1), ("G2", "session", ["1h"], ALL, g2), ("G3", "trend", ["1h", "4h"], ALL, g3), ("G4", "trend", ["1h", "4h"], ALL, g4),
    ("G5", "trend", ["1h", "4h"], ALL, g5), ("G6", "trend", ["1h", "4h"], ALL, g6), ("G7", "trend", ["4h", "1d"], ALL, g7), ("G8", "trend", ["1h", "4h"], ALL, g8),
    ("G9", "trend", ["1h", "4h"], ALL, g9), ("G10", "meanrev", ["15m"], EXNESS, g10), ("G13", "calendar", ["1h"], CRYPTO, g13), ("G14", "calendar", ["1h"], CRYPTO, g14),
]
