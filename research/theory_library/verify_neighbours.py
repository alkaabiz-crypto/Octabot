"""V2 of VERIFY_PREREG.md: neighbouring parameters for the screen passes, using the screen engine.
The functions below are the screen's b9 / d4_fvg / b7 with their constants turned into arguments (defaults = screen).

Usage: BARS_DIR=<orb 1m bars> python3 -I verify_neighbours.py
"""
import itertools, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E  # noqa: E402
from engine import Book, manage, sma  # noqa: E402
from theories import C  # noqa: E402


def b9(m, tf, fib=0.618, look=20):
    c = C(m, tf); s50 = sma(c.c, 50); bk = Book(c); o, h, l, cl = c.o.values, c.h.values, c.l.values, c.c.values; i = 50
    while i < len(c) - 2:
        hh, ll = h[i - look + 1:i + 1], l[i - look + 1:i + 1]; ih, il = int(np.argmax(hh)), int(np.argmin(ll)); H, L = hh[ih], ll[il]
        side = 1 if (cl[i] > s50.iloc[i] and ih > il) else (-1 if (cl[i] < s50.iloc[i] and il > ih) else 0)
        if side == 0 or H <= L: i += 1; continue
        lim = H - fib * (H - L) if side > 0 else L + fib * (H - L); stop, tp = (L, H) if side > 0 else (H, L); filled = None
        for k in range(i + 1, min(i + 11, len(c))):
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim): filled = k; break
        if filled is None: i += 1; continue
        pe = min(o[filled], lim) if side > 0 else max(o[filled], lim)
        x, px = manage(c, filled, side, stop, tp, tmax=20, intrabar=True); bk.add(filled, x, side, pe, px); i = x + 1
    return c, bk


def d4(m, tf, valid=10, rr=2.0):
    c = C(m, tf); bk = Book(c); o, h, l = c.o.values, c.h.values, c.l.values; i = 2
    while i < len(c) - 1:
        side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
        if not side: i += 1; continue
        lim = h[i - 2] if side > 0 else l[i - 2]; stop = l[i - 2] if side > 0 else h[i - 2]; R = side * (lim - stop); done = False
        if R <= 0: i += 1; continue
        for k in range(i + 1, min(i + 1 + valid, len(c))):
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim):
                pe = min(o[k], lim) if side > 0 else max(o[k], lim); x, px = manage(c, k, side, stop, lim + side * rr * R, tmax=20, intrabar=True)
                bk.add(k, x, side, pe, px); i = x + 1; done = True; break
        if not done: i += 1
    return c, bk


def b7(m, tf, band=2.0, minc=8):
    c = C(m, tf); bk = Book(c); cl, day = c.c.values, c.day.values
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); ends = np.r_[starts[1:], len(c)]
    for s, e in zip(starts, ends):
        k = s + minc
        while k < e - 2:
            seg = cl[s:k + 1]; tw, sd = seg.mean(), seg.std()
            if sd > 0 and abs(cl[k] - tw) > band * sd:
                side = -1 if cl[k] > tw else 1; i0 = k + 1
                x, px = manage(c, i0, side, tw - side * (band + 1) * sd, tw, last=e - 1); bk.add(i0, x, side, c.o.values[i0], px); k = x + 1
            else: k += 1
    return c, bk


GRID = {"B9": (b9, [dict(fib=f, look=lk) for f, lk in itertools.product((0.5, 0.618, 0.786), (15, 20, 25))]),
        "D4": (d4, [dict(valid=v, rr=r) for v, r in itertools.product((5, 10, 15), (1.5, 2.0, 2.5))]),
        "B7": (b7, [dict(band=b, minc=n) for b, n in itertools.product((1.5, 2.0, 2.5), (6, 8, 10))])}
CANDIDATES = [("B9", "USOILm", "1h"), ("B9", "ETHUSDT", "1h"), ("B9", "BTCUSDT", "1h"), ("D4", "XAUUSDm", "1h"), ("B7", "XAUUSDm", "15m"), ("B7", "USTECm", "15m")]


def main():
    out = {}
    for tid, mkt, tf in CANDIDATES:
        fn, grid = GRID[tid]; rows = []
        for p in grid:
            c, bk = fn(mkt, tf, **p); r, _ = E.evaluate(c, bk, 2)
            rows.append(dict(params=p, dev_bp=round(float(r["dev"].mean() * 1e4), 2), hold_bp=round(float(r["holdout"].mean() * 1e4), 2),
                             dev_n=int(len(r["dev"])), hold_n=int(len(r["holdout"]))))
        pos = sum(x["hold_bp"] > 0 for x in rows)
        out[f"{tid}|{mkt}|{tf}"] = dict(grid=rows, holdout_positive=f"{pos}/9", V2="PASS" if pos >= 7 else "FAIL")
        print(tid, mkt, tf, out[f"{tid}|{mkt}|{tf}"]["holdout_positive"], out[f"{tid}|{mkt}|{tf}"]["V2"], [(tuple(x["params"].values()), x["dev_bp"], x["hold_bp"]) for x in rows], flush=True)
    json.dump(out, open(os.path.join(HERE, "results", "verify_neighbours.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
