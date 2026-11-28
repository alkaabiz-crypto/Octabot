"""SIG-005 post-hoc sensitivity (user question 2026-11-20: "maybe the target is too much"): every combination of
target {2,3,5,7,10,15,20}% x stop {3,5,10,none}%, max 7 days, on the unique calls (1h Binance, 0.10%/side),
each against random entries (same coin, 30-60 days away) with the same rule. BH over the 28 cells.
Labelled post-hoc; it cannot upgrade the pre-registered verdict, only show whether the exit choice changes the picture.
usage: python3 -I grid.py <all_calls.json> <px1h_dir>"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import score as S  # noqa: E402
TG = [0.02, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20]; ST = [0.03, 0.05, 0.10, None]; HOLD = 168; COST = 0.002


def ex(a, i, side, stop_pct, tgt_pct):
    o, h, l, c = a[:, 1], a[:, 2], a[:, 3], a[:, 4]; e = o[i]; tgt = e * (1 + side * tgt_pct); stop = e * (1 - side * stop_pct) if stop_pct else None
    for k in range(i, i + HOLD):
        if stop is not None:
            if k > i and (o[k] - stop) * side <= 0: return side * (o[k] / e - 1)
            if ((l[k] if side > 0 else h[k]) - stop) * side <= 0: return -stop_pct
        if ((h[k] if side > 0 else l[k]) - tgt) * side >= 0: return tgt_pct
    return side * (c[i + HOLD - 1] / e - 1)


def main():
    calls = json.load(open(sys.argv[1])); px = sys.argv[2]; rng = np.random.default_rng(3006); seen = set(); setups = []
    for c in calls:
        b = c["pair"].split("-")[0].upper(); ts = c["timestamp"]; k = (b, ts)
        if k in seen: continue
        seen.add(k); a = S.load(px, b)
        if len(a) == 0: continue
        i = int(np.searchsorted(a[:, 0], ts))
        if i >= len(a) or a[i, 0] - ts > 2 * S.H or i + HOLD >= len(a): continue
        cand = np.r_[np.arange(i - 60 * 24, i - 30 * 24), np.arange(i + 30 * 24, i + 60 * 24)]; cand = cand[(cand >= 0) & (cand + HOLD < len(a))]
        if len(cand) < 20: continue
        setups.append((a, i, 1 if c["side"] == "BUY" else -1, rng.choice(cand, 20, replace=False)))
    cells = []
    for st in ST:
        for tg in TG:
            act = np.array([ex(a, i, s, st, tg) - COST for a, i, s, _ in setups]); rnd = np.array([[ex(a, int(j), s, st, tg) - COST for j in js] for a, i, s, js in setups])
            pick = rng.integers(0, 20, size=(1000, len(setups))); means = rnd[np.arange(len(setups))[None, :], pick].mean(axis=1)
            cells.append(dict(stop=st, target=tg, n=len(act), calls_mean_pct=round(float(act.mean() * 100), 3), calls_win_pct=round(float((act > 0).mean() * 100), 1),
                              random_mean_pct=round(float(means.mean() * 100), 3), edge_vs_random_pct=round(float((act.mean() - means.mean()) * 100), 3), p=float((means >= act.mean()).mean())))
            print(cells[-1], flush=True)
    ps = [x["p"] for x in cells]; o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / len(ps): sig = set(o[:r + 1])
    for i, x in enumerate(cells): x["bh_significant"] = i in sig
    json.dump(dict(label="post-hoc sensitivity", cells=cells), open(os.path.join(HERE, "grid.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
