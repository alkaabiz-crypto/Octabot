"""STR-043 (PREREG.md): value-area scenarios from the soualium reel. S1 = VAL/VAH wick rejection -> opposite edge;
S2 = strong value-area break + FVG retest rejection -> 2R. 1h signals, 15m execution (STR-041 loaders/manage/bench).
usage: BTC_DATA=<dir> DISCOVERY_DATA=<scratch> python3 -I run_str043.py"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "str_041"))
import run_str041 as S41  # noqa: E402  load(), atr(), manage(), bench(), PER
PER = S41.PER; PIV = 10; LIFE = 120; BINS = 50; HOLD = 72 * 4; MIN_RISK = 0.0015


def value_area(h, l, v, a, b):
    lo, hi = l[a:b + 1].min(), h[a:b + 1].max()
    if hi <= lo: return None
    edges = np.linspace(lo, hi, BINS + 1); vol = np.zeros(BINS)
    for i in range(a, b + 1):
        i0 = max(0, min(BINS - 1, int((l[i] - lo) / (hi - lo) * BINS))); i1 = max(0, min(BINS - 1, int((h[i] - lo) / (hi - lo) * BINS)))
        vol[i0:i1 + 1] += v[i] / (i1 - i0 + 1)
    tot = vol.sum()
    if tot <= 0: return None
    p = int(np.argmax(vol)); lo_i = hi_i = p; acc = vol[p]
    while acc < 0.7 * tot:
        dn = vol[lo_i - 1] if lo_i > 0 else -1; up = vol[hi_i + 1] if hi_i < BINS - 1 else -1
        if up >= dn: hi_i += 1; acc += vol[hi_i]
        else: lo_i -= 1; acc += vol[lo_i]
    return edges[lo_i], edges[hi_i + 1]


def signals(H, scen):
    o, h, l, c, v, t = H["o"], H["h"], H["l"], H["c"], H["v"], H["t"]; n = len(c); A = S41.atr(H); out = []
    last_hi = last_lo = None; prof = None; brk = []
    for i in range(2 * PIV + 2, n):
        j = i - PIV; new = None
        if h[j] == h[j - PIV:j + PIV + 1].max():
            if last_lo is not None and last_lo < j: new = (last_lo, j)
            last_hi = j
        if l[j] == l[j - PIV:j + PIV + 1].min():
            if last_hi is not None and last_hi < j: new = (last_hi, j)
            last_lo = j
        if new is not None:
            va = value_area(h, l, v, *new)
            if va: prof = (va[0], va[1], i); brk = []
        if prof is None or i - prof[2] > LIFE: continue
        VAL, VAH, _ = prof; rng = h[i] - l[i]
        if rng <= 0: continue
        if scen == "S1":
            lw = min(o[i], c[i]) - l[i]; uw = h[i] - max(o[i], c[i])
            if l[i] < VAL < c[i] and lw >= 0.5 * rng: out.append((int(t[i] + 3600), 1, float(l[i] - 0.1 * A[i]), float(VAH), i))
            elif h[i] > VAH > c[i] and uw >= 0.5 * rng: out.append((int(t[i] + 3600), -1, float(h[i] + 0.1 * A[i]), float(VAL), i))
        else:
            if c[i] < VAL - 0.5 * A[i]: brk.append([-1, i, None])
            if c[i] > VAH + 0.5 * A[i]: brk.append([1, i, None])
            keep = []
            for b in brk:
                side, bi, gap = b
                if gap is None and i <= bi + 2:                                   # FVG formed at bars bi..bi+2 (k = i)
                    if side < 0 and h[i] < l[i - 2]: b[2] = gap = (h[i], l[i - 2], i)
                    if side > 0 and l[i] > h[i - 2]: b[2] = gap = (h[i - 2], l[i], i)
                if gap is None:
                    if i < bi + 2: keep.append(b)
                    continue
                if i - gap[2] > 24: continue
                if i > gap[2]:
                    if side < 0 and h[i] >= gap[0] and c[i] < gap[0]:
                        out.append((int(t[i] + 3600), -1, float(max(h[i], gap[1]) + 0.1 * A[i]), None, i)); continue
                    if side > 0 and l[i] <= gap[1] and c[i] > gap[1]:
                        out.append((int(t[i] + 3600), 1, float(min(l[i], gap[0]) - 0.1 * A[i]), None, i)); continue
                keep.append(b)
            brk = keep
    return out


def run(Q, sig, cp, cs):
    t, o, h, l, c = Q["t"], Q["o"], Q["h"], Q["l"], Q["c"]; trades = []; free = 0
    for ta, side, stp, tgt, _ in sig:
        if ta < free: continue
        i = int(np.searchsorted(t, ta))
        if i >= len(t) or t[i] - ta > 3600: continue
        e = o[i]; risk = (e - stp) * side
        if risk <= 0 or risk / e < MIN_RISK: continue
        tg = tgt if tgt is not None else e + side * 2 * risk
        if (tg - e) * side <= 0: continue
        rg, x = S41.manage(o, h, l, c, i, side, e, stp, tg, HOLD)
        trades.append(dict(t=int(t[i]), side=side, risk_pct=risk / e, tr=abs(tg - e) / risk, r=rg - cp * e / risk, rs=rg - cs * e / risk)); free = int(t[x]) + 900
    return trades


def main():
    R = {}; rng = np.random.default_rng(3043)
    for m in ("BTCUSDT", "ETHUSDT", "XAUUSDm", "USOILm", "US500m"):
        Q, H, sp = S41.load(m); cp, cs = (0.0005, 0.0020) if sp is None else (1.5 * sp, 3 * sp)
        for scen in ("S1", "S2"):
            tr = run(Q, signals(H, scen), cp, cs); res = {}
            for p, lo, hi in PER:
                s = [x for x in tr if lo <= x["t"] < hi]
                if len(s) < 3: res[p] = dict(trades=len(s)); continue
                r = np.array([x["r"] for x in s]); rs = np.array([x["rs"] for x in s])
                q = dict(trades=len(s), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1), avg_target_R=round(float(np.mean([x["tr"] for x in s])), 2))
                if p == "TEST" and len(s) >= 10: q["p_random"], q["random_mean_R"] = S41.bench(Q, s, cp, lo, hi, rng); q["random_mean_R"] = round(q["random_mean_R"], 4)
                res[p] = q
            R[f"STR-043{scen}|{m}"] = dict(results=res)
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
