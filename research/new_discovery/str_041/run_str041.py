"""STR-041 (PREREG.md): liquidity sweep -> CHoCH -> buyer/seller dominance -> OTE limit at 70.5%, stop beyond the sweep, 2R / leg-high target.
usage: BTC_DATA=<dir> DISCOVERY_DATA=<scratch with long/ and multi/bars/> python3 -I run_str041.py"""
import json, math, os, sys
import numpy as np, pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "str_027"))
import run_str027 as S27  # noqa: E402  load(), PER, summarize-style periods
PER = S27.PER; HOLD = 72 * 4; VALID_H = 24; MIN_RISK = 0.0015; OTE = 0.705


def load(m):
    if m != "US500m": return S27.load(m)
    d = pd.read_csv(os.path.join(os.environ["DISCOVERY_DATA"], "multi", "bars", "US500m_15m.csv.gz"))
    o, h, l, c = (d.bo + d.ao) / 2, (d.bh + d.ah) / 2, (d.bl + d.al) / 2, (d.bc + d.ac) / 2; sp = float(((d.ao - d.bo) / o).median())
    q = dict(t=d.t.values.astype(np.int64), o=o.values, h=h.values, l=l.values, c=c.values)
    g = pd.DataFrame(dict(o=o, h=h, l=l, c=c, v=d.ticks, k=d.t // 3600 * 3600)).groupby("k")
    return q, dict(t=np.array(g.o.first().index, np.int64), o=g.o.first().values, h=g.h.max().values, l=g.l.min().values, c=g.c.last().values, v=g.v.sum().values.astype(float)), sp


def atr(H, n=14):
    h, l, c = H["h"], H["l"], H["c"]; pc = np.r_[c[0], c[:-1]]; tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
    return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().values


def setups(H, use_dom=True, target_leg=False):
    o, h, l, c, v, t = H["o"], H["h"], H["l"], H["c"], H["v"], H["t"]; n = len(c); A = atr(H); out = []
    shi = slo = None; pend = []                                              # pend: [side, sweep_i, extreme, swing_level_for_choch]
    for i in range(12, n):
        j = i - 5
        if h[j] == h[j - 5:j + 6].max(): shi = j
        if l[j] == l[j - 5:j + 6].min(): slo = j
        if slo is not None and l[i] < l[slo] and c[i] > l[slo] and shi is not None: pend.append([1, i, l[i], h[shi]])
        if shi is not None and h[i] > h[shi] and c[i] < h[shi] and slo is not None: pend.append([-1, i, h[i], l[slo]])
        keep = []
        for p in pend:
            side, si, ext, lvl = p
            if i - si > 24: continue
            if side > 0: ext = min(ext, l[i]); p[2] = ext
            else: ext = max(ext, h[i]); p[2] = ext
            if i > si and (c[i] - lvl) * side > 0:                            # CHoCH close beyond the opposite swing
                seg = slice(si, i + 1); up = (c[seg] - o[seg]) * side > 0; tot = v[seg].sum(); dom = v[seg][up].sum() / tot if tot > 0 else 0
                if (not use_dom) or dom >= 0.55:
                    far = ext; peak = h[si:i + 1].max() if side > 0 else l[si:i + 1].min()
                    entry = peak - side * OTE * abs(peak - far); stop = far - side * 0.1 * A[i]; tgt = peak if target_leg else None
                    out.append((int(t[i] + 3600), int(t[i] + 3600 + VALID_H * 3600), side, float(entry), float(stop), tgt, i))
                continue
            keep.append(p)
        pend = keep
    return out


@njit(cache=True)
def manage(o, h, l, c, i0, side, entry, stop, tgt, hold):
    end = min(i0 + hold, len(o) - 1); risk = (entry - stop) * side
    for i in range(i0, end + 1):
        if ((l[i] if side > 0 else h[i]) - stop) * side <= 0:
            px = stop
            if i > i0 and (o[i] - stop) * side < 0: px = o[i]
            return (px - entry) * side / risk, i
        if i > i0 and ((h[i] if side > 0 else l[i]) - tgt) * side >= 0: return (tgt - entry) * side / risk, i
    return (c[end] - entry) * side / risk, end


def run(Q, orders, cp, cs):
    t, o, h, l, c = Q["t"], Q["o"], Q["h"], Q["l"], Q["c"]; trades = []; pend = None; oi = 0; i = 0; n = len(t); free = 0
    while i < n:
        while oi < len(orders) and orders[oi][0] <= t[i]:
            if orders[oi][0] >= free: pend = orders[oi]
            oi += 1
        if pend is not None:
            ta, te, side, ent, stp, tg, _ = pend
            if t[i] >= te: pend = None
            elif (l[i] <= ent if side > 0 else h[i] >= ent):
                e = min(o[i], ent) if side > 0 else max(o[i], ent); risk = (e - stp) * side
                if risk > 0 and risk / e >= MIN_RISK:
                    tgt = tg if tg is not None and (tg - e) * side > 0 else e + side * 2 * risk
                    rg, x = manage(o, h, l, c, i, side, e, stp, tgt, HOLD)
                    trades.append(dict(t=int(t[i]), side=side, risk_pct=risk / e, tr=abs(tgt - e) / risk, r=rg - cp * e / risk, rs=rg - cs * e / risk))
                    free = int(t[x]) + 900; pend = None; i = x + 1; continue
                pend = None
        i += 1
    return trades


def bench(Q, sel, cp, lo, hi, rng, sets=1000, per=40):
    t, o, h, l, c = Q["t"], Q["o"], Q["h"], Q["l"], Q["c"]; pool = np.flatnonzero((t >= lo) & (t < hi - HOLD * 900)); sims = np.empty((len(sel), per))
    for a, x in enumerate(sel):
        for b in range(per):
            i = int(pool[rng.integers(len(pool))]); e = o[i]; risk = x["risk_pct"] * e; stp = e - x["side"] * risk
            rg, _ = manage(o, h, l, c, i, x["side"], e, stp, e + x["side"] * x["tr"] * risk, HOLD); sims[a, b] = rg - cp * e / risk
    pick = rng.integers(per, size=(sets, len(sel))); m = sims[np.arange(len(sel)), pick].mean(axis=1); act = np.mean([x["r"] for x in sel])
    return float((m >= act).mean()), float(m.mean())


def main():
    R = {}; rng = np.random.default_rng(3041)
    for m in ("BTCUSDT", "ETHUSDT", "XAUUSDm", "USOILm", "US500m"):
        Q, H, sp = load(m); cp, cs = (0.0005, 0.0020) if sp is None else (1.5 * sp, 3 * sp)
        for var, ud, tl in (("A", True, False), ("B", False, False), ("C", True, True)):
            tr = run(Q, setups(H, ud, tl), cp, cs); res = {}
            for p, lo, hi in PER:
                s = [x for x in tr if lo <= x["t"] < hi]
                if len(s) < 3: res[p] = dict(trades=len(s)); continue
                r = np.array([x["r"] for x in s]); rs = np.array([x["rs"] for x in s])
                q = dict(trades=len(s), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1))
                if p == "TEST" and len(s) >= 10: q["p_random"], q["random_mean_R"] = bench(Q, s, cp, lo, hi, rng); q["random_mean_R"] = round(q["random_mean_R"], 4)
                res[p] = q
            R[f"STR-041{var}|{m}"] = dict(results=res)
        print(m, {k.split("|")[0]: {p: (v.get("trades"), v.get("mean_R")) for p, v in R[k]["results"].items()} for k in R if k.endswith(m)}, flush=True)
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
