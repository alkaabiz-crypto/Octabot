"""Same-candle ambiguity audit (CAUSAL_IMPACT_ASSESSMENT.md §3, open item). Frozen rules A13, C3/C4 (stop_break) and D1 skip a
setup when ONE candle trades through both entry levels. That decision uses the whole candle. Here, for every such skip, the
1-minute bars inside the candle decide which level traded first, and the trade the rule would then have taken is managed with
the frozen engine.manage (intrabar=True), exactly as the frozen code manages a normal entry. G2 (stop-and-reverse, 1h) is
counted only. Frozen functions are not modified; the same logic is re-traced here to find the skips.
usage: LIB_DIR=<theory_library> BARS_DIR=<exness 1m bars> python3 -I ambiguity_audit.py <out_json>
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.environ["LIB_DIR"]); import engine as E, theories as T  # noqa: E401,E402
from engine import manage  # noqa: E402
OUT = sys.argv[1]


def minute_first(mkt, c, k, hi, lo):
    """Which level traded first inside candle k (Exness 1m mid bars). 'up', 'dn' or 'same' (both in one minute)."""
    b = E.base(mkt); m0 = c.m.values[k]; m1 = c.m.values[k + 1] if k + 1 < len(c) else m0 + 10 ** 9
    s = b[(b.m >= m0) & (b.m < m1)]; up = np.flatnonzero(s.h.values >= hi); dn = np.flatnonzero(s.l.values <= lo)
    fu = up[0] if len(up) else 10 ** 9; fd = dn[0] if len(dn) else 10 ** 9
    return "same" if fu == fd else ("up" if fu < fd else "dn")


def net2(c, k, x, side, pe, px):
    hs = c.hs.values; return side * (px - pe) / pe - 2 * (hs[k] + hs[min(x, len(hs) - 1)]) / pe


def audit_stop_break(mkt, tf, setup, valid, label):
    c = T.C(mkt, tf); o, h, l = c.o.values, c.h.values, c.l.values; i = 8; skips = []; taken = 0
    while i < len(c) - 1:
        lv = setup(h, l, i)
        if not lv: i += 1; continue
        hi, lo = lv; R = hi - lo; done = False
        for k in range(i + 1, min(i + 1 + valid, len(c))):
            up, dn = h[k] >= hi, l[k] <= lo
            if up and dn:
                skips.append((k, hi, lo, R)); break
            if up or dn:
                side = 1 if up else -1; lvl = hi if up else lo; pe = max(o[k], lvl) if up else min(o[k], lvl); st = lo if up else hi
                x, px = manage(c, k, side, st, pe + side * 2 * R, tmax=20, intrabar=True); i = x + 1; done = True; taken += 1; break
        if not done: i += 1
    res = []
    for k, hi, lo, R in skips:
        w = minute_first(mkt, c, k, hi, lo) if mkt in E.EXNESS else "no-1m"
        if w in ("up", "dn"):
            side = 1 if w == "up" else -1; lvl = hi if side > 0 else lo; pe = max(o[k], lvl) if side > 0 else min(o[k], lvl); st = lo if side > 0 else hi
            x, px = manage(c, k, side, st, pe + side * 2 * R, tmax=20, intrabar=True); res.append(net2(c, k, x, side, pe, px))
    return dict(rule=label, market=mkt, tf=tf, trades_taken=taken, ambiguous_skips=len(skips), resolved_by_1m=len(res),
                skipped_mean_bp_2x=round(float(np.mean(res) * 1e4), 2) if res else None)


def audit_a13(mkt, tf="1h"):
    c = T.C(mkt, tf); d1 = T.C(mkt, "1d").set_index("day"); o, h, l, cl, day = c.o.values, c.h.values, c.l.values, c.c.values, c.day.values
    starts = np.flatnonzero(np.r_[True, day[1:] != day[:-1]]); ends = np.r_[starts[1:], len(c)]; skips = []; taken = 0
    for s, e in zip(starts, ends):
        if day[s] - 1 not in d1.index or e - s < 3: continue
        pr = d1.loc[day[s] - 1]; rg = pr.h - pr.l; bu, bd = o[s] + 0.6 * rg, o[s] - 0.6 * rg
        for k in range(s, e):
            up, dn = h[k] >= bu, l[k] <= bd
            if up and dn: skips.append((k, bu, bd, e)); break
            if up or dn: taken += 1; break
    res = []
    for k, bu, bd, e in skips:
        w = minute_first(mkt, c, k, bu, bd) if mkt in E.EXNESS else "no-1m"
        if w in ("up", "dn"):
            side = 1 if w == "up" else -1; lvl = bu if side > 0 else bd; pe = o[k] if (side > 0 and o[k] > lvl) or (side < 0 and o[k] < lvl) else lvl
            res.append(net2(c, k, e - 1, side, pe, cl[e - 1]))            # A13 holds to the day's last candle close
    return dict(rule="A13", market=mkt, tf=tf, trades_taken=taken, ambiguous_skips=len(skips), resolved_by_1m=len(res),
                skipped_mean_bp_2x=round(float(np.mean(res) * 1e4), 2) if res else None)


def count_g2(mkt, tf="1h"):
    c = T.C(mkt, tf); d1 = T.C(mkt, "1d").set_index("day"); o, h, l, day = c.o.values, c.h.values, c.l.values, c.day.values; days = d1.index.values; n = amb = 0
    for s, e in T.day_slices(c):
        k = np.searchsorted(days, day[s])
        if k < 4 or e - s < 3: continue
        p = d1.loc[days[k - 4:k]]; R = max(p.h.max() - p.c.min(), p.c.max() - p.l.min()); up, dn = o[s] + 0.5 * R, o[s] - 0.5 * R; n += 1
        if any(h[q] >= up and l[q] <= dn for q in range(s, e)): amb += 1
    return dict(rule="G2", market=mkt, tf=tf, days=n, days_with_an_ambiguous_candle=amb)


def main():
    out = []
    C3 = lambda h, l, i: (h[i - 1], l[i - 1]) if (h[i] < h[i - 1] and l[i] > l[i - 1]) else None
    C4 = lambda h, l, i: (h[i], l[i]) if (h[i] - l[i]) <= (h[i - 6:i + 1] - l[i - 6:i + 1]).min() else None
    for mkt in E.EXNESS + E.CRYPTO:
        for tf in ("1h", "1d"): out.append(audit_stop_break(mkt, tf, C3, 5, "C3"))
        out.append(audit_stop_break(mkt, "1d", C4, 3, "C4")); out.append(audit_a13(mkt)); out.append(count_g2(mkt))
        for r in out[-5:]: print(r, flush=True)
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
