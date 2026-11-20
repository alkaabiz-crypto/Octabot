"""THE-005 event study (PREREG.md). usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_the005.py"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ND, "batch_003")); sys.path.insert(0, os.path.join(ND, "src"))
import run_batch as RB, common as C  # noqa: E401,E402
GRID = RB.GRID; P = ["EARLY", "TRAIN", "VALIDATION", "TEST"]; LOOK, HOLD = 8, 16


def outcome(h, l, k, up_level, lo_level):
    """First of (high >= up_level) or (low <= lo_level) over candles k+1..k+HOLD: 'up', 'dn', 'both' (same candle) or None."""
    for q in range(k + 1, min(k + 1 + HOLD, len(h))):
        u, d = h[q] >= up_level, l[q] <= lo_level
        if u and d: return "both"
        if u: return "up"
        if d: return "dn"
    return None


def events(m, offset):
    d = RB.load(m); G = GRID[m]; D = 0.25 * G; h, l, c = d.mh.values, d.ml.values, d.mc.values; per = [RB.period(t) for t in d.index]
    lvl = lambda x, f: (f((x - offset) / G)) * G + offset                    # grid shifted by `offset`
    rev, cont = {p: [] for p in P}, {p: [] for p in P}
    for k in range(LOOK, len(c) - 1):
        p = per[k]
        if p is None: continue
        hi8, lo8 = h[k - LOOK:k].max(), l[k - LOOK:k].min()
        L = lvl(h[k], math.floor)                                            # touched from below
        if L > hi8 and L <= h[k]:
            o = outcome(h, l, k, L + D, L - D)
            if o in ("up", "dn"): rev[p].append(1 if o == "dn" else 0)
        L = lvl(l[k], math.ceil)                                             # touched from above
        if L < lo8 and L >= l[k]:
            o = outcome(h, l, k, L + D, L - D)
            if o in ("up", "dn"): rev[p].append(1 if o == "up" else 0)
        mx, mn = c[k - LOOK:k].max(), c[k - LOOK:k].min()
        Lu = lvl(c[k], math.floor)
        if Lu > mx:                                                          # crossed up, closed at/above
            o = outcome(h, l, k, Lu + D, Lu - D)
            if o in ("up", "dn"): cont[p].append(1 if o == "up" else 0)
        Ld = lvl(c[k], math.ceil)
        if Ld < mn:
            o = outcome(h, l, k, Ld + D, Ld - D)
            if o in ("up", "dn"): cont[p].append(1 if o == "dn" else 0)
    return rev, cont


def ztest(a, b):
    n1, n2 = len(a), len(b)
    if n1 < 30 or n2 < 30: return None
    p1, p2 = np.mean(a), np.mean(b); pp = (sum(a) + sum(b)) / (n1 + n2); se = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se if se > 0 else 0.0
    return dict(n_round=n1, n_null=n2, rate_round=round(float(p1), 4), rate_null=round(float(p2), 4), effect_pp=round(100 * float(p1 - p2), 2), p=float(0.5 * math.erfc(z / math.sqrt(2))))


def main():
    R = {}
    for m in GRID:
        rr, cr = events(m, 0.0); rn, cn = events(m, GRID[m] / 2)
        R[m] = {"reversal": {p: ztest(rr[p], rn[p]) for p in P}, "acceleration": {p: ztest(cr[p], cn[p]) for p in P}}
        print(m, {k: {p: (v["effect_pp"], round(v["p"], 4), v["n_round"]) for p, v in R[m][k].items() if v} for k in R[m]}, flush=True)
    verdict = {}
    for claim in ("reversal", "acceleration"):
        mk = list(GRID); ps = [R[m][claim]["TEST"]["p"] if R[m][claim]["TEST"] else 1.0 for m in mk]; sig = C.bh(ps)
        ok = [m for i, m in enumerate(mk) if i in sig and R[m][claim]["TEST"]["effect_pp"] > 0 and all(v["effect_pp"] > 0 for p, v in R[m][claim].items() if v and p != "TEST")]
        early = [m for m in mk if any(v and v["p"] <= 0.05 and v["effect_pp"] > 0 for p, v in R[m][claim].items() if p in ("EARLY", "TRAIN"))]
        verdict[claim] = dict(verdict="SUPPORTED" if len(ok) >= 4 else ("PARTLY SUPPORTED" if ok else ("DECAYED" if early else "NOT SUPPORTED")), markets=ok, early_significant=early)
    json.dump(dict(results=R, verdict=verdict), open(os.path.join(HERE, "results.json"), "w"), indent=1); print(json.dumps(verdict))


if __name__ == "__main__":
    main()
