"""STR-044 (PREREG.md): liquidity-sweep entry. usage: BTC_DATA=<dir> DISCOVERY_DATA=<scratch> python3 -I run_str044.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("str_041", "str_043"): sys.path.insert(0, os.path.join(ND, p))
import run_str041 as S41, run_str043 as S43  # noqa: E401,E402
PER = S41.PER; PIV = 5; LOOK = 100


def signals(H, equal=True):
    o, h, l, c, t = H["o"], H["h"], H["l"], H["c"], H["t"]; n = len(c); A = S41.atr(H); lows, highs, out = [], [], []; used_lo, used_hi = set(), set()
    for i in range(2 * PIV + 2, n):
        j = i - PIV
        if l[j] == l[j - PIV:j + PIV + 1].min(): lows.append(j)
        if h[j] == h[j - PIV:j + PIV + 1].max(): highs.append(j)
        lows = [x for x in lows if i - x <= LOOK]; highs = [x for x in highs if i - x <= LOOK]
        for side, pts, arr, used in ((1, lows, l, used_lo), (-1, highs, h, used_hi)):
            pools = []
            if equal:
                for a in range(len(pts)):
                    for b in range(a + 1, len(pts)):
                        if abs(arr[pts[a]] - arr[pts[b]]) <= 0.1 * A[i]: pools.append((min(arr[pts[a]], arr[pts[b]]) if side > 0 else max(arr[pts[a]], arr[pts[b]]), (pts[a], pts[b])))
            else:
                pools = [(arr[p], (p,)) for p in pts]
            for lvl, key in pools:
                if key in used: continue
                if side > 0 and l[i] < lvl < c[i]:
                    used.add(key); out.append((int(t[i] + 3600), 1, float(l[i] - 0.1 * A[i]), None, i)); break
                if side < 0 and h[i] > lvl > c[i]:
                    used.add(key); out.append((int(t[i] + 3600), -1, float(h[i] + 0.1 * A[i]), None, i)); break
            # pools whose level is cleanly broken by a close are spent
            for lvl, key in pools:
                if (side > 0 and c[i] < lvl) or (side < 0 and c[i] > lvl): used.add(key)
    return sorted(out)


def main():
    R = {}; rng = np.random.default_rng(3044)
    for m in ("BTCUSDT", "ETHUSDT", "XAUUSDm", "USOILm", "US500m"):
        Q, H, sp = S41.load(m); cp, cs = (0.0005, 0.0020) if sp is None else (1.5 * sp, 3 * sp)
        for var, eq in (("A", True), ("B", False)):
            tr = S43.run(Q, signals(H, eq), cp, cs); res = {}
            for p, lo, hi in PER:
                s = [x for x in tr if lo <= x["t"] < hi]
                if len(s) < 3: res[p] = dict(trades=len(s)); continue
                r = np.array([x["r"] for x in s]); rs = np.array([x["rs"] for x in s])
                q = dict(trades=len(s), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1))
                if p == "TEST" and len(s) >= 10: q["p_random"], q["random_mean_R"] = S41.bench(Q, s, cp, lo, hi, rng); q["random_mean_R"] = round(q["random_mean_R"], 4)
                res[p] = q
            R[f"STR-044{var}|{m}"] = dict(results=res)
        print(m, "done", flush=True)
    keys = list(R); ps = [R[k]["results"]["TEST"].get("p_random", 1.0) for k in keys]; o = np.argsort(ps); sig = set()
    for rank, i in enumerate(o):
        if ps[i] <= 0.05 * (rank + 1) / len(ps): sig = set(o[:rank + 1])
    for i, k in enumerate(keys):
        f = R[k]["results"]; av = [p for p, *_ in PER if f[p].get("mean_R") is not None]; pos = bool(av) and all(f[p]["mean_R"] > 0 for p in av); te = f["TEST"]
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(k, R[k]["decision"], {p: (v.get("trades"), v.get("mean_R"), v.get("win_pct")) for p, v in f.items()}, te.get("p_random"), te.get("random_mean_R"))
    json.dump(dict(n_tests=len(keys), results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
