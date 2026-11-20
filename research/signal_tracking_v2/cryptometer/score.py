"""SIG-005 scoring (PREREG.md + Amendment 1). usage: python3 -I score.py <all_calls.json> <px1h_dir>
Writes results.json (derived statistics only; no third-party raw rows)."""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); H = 3600 * 1000; D = 24 * H
COST, STRESS = 0.0010, 0.0025; STOP, TGT, HOLD = 0.05, 0.10, 168; SPLIT = 1751328000000  # 2025-07-01


def load(px, base, cache={}):
    if base not in cache:
        f = os.path.join(px, f"{base}.json"); a = np.array(json.load(open(f)), float) if os.path.exists(f) else np.empty((0, 5))
        cache[base] = a
    return cache[base]


def trade(a, i, side):
    """returns gross returns for E1, E2, E3 from entry at open of candle i, or None if not enough data."""
    if i + HOLD >= len(a): return None
    o, h, l, c = a[:, 1], a[:, 2], a[:, 3], a[:, 4]; e = o[i]; stop = e * (1 - side * STOP); tgt = e * (1 + side * TGT); e1 = None
    for k in range(i, i + HOLD):
        if k > i and (o[k] - stop) * side <= 0: e1 = side * (o[k] / e - 1); break
        if ((l[k] if side > 0 else h[k]) - stop) * side <= 0: e1 = -STOP; break
        if ((h[k] if side > 0 else l[k]) - tgt) * side >= 0: e1 = TGT; break
    if e1 is None: e1 = side * (c[i + HOLD - 1] / e - 1)
    return e1, side * (o[i + 24] / e - 1), side * (o[i + HOLD] / e - 1)


def stats(x):
    x = np.asarray(x); return dict(n=len(x), mean_pct=round(float(x.mean() * 100), 3), win_pct=round(float((x > 0).mean() * 100), 1),
                                   t=round(float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))), 2) if len(x) > 2 else None)


def main():
    calls = json.load(open(sys.argv[1])); px = sys.argv[2]; rng = np.random.default_rng(3005); rows = []; seen = set(); skipped = dict(no_price=0, no_room=0)
    for c in calls:
        b = c["pair"].split("-")[0].upper(); ts = c["timestamp"]; side = 1 if c["side"] == "BUY" else -1; a = load(px, b)
        if len(a) == 0: skipped["no_price"] += 1; continue
        i = int(np.searchsorted(a[:, 0], ts, side="left"))
        if i >= len(a) or a[i, 0] - ts > 2 * H: skipped["no_price"] += 1; continue
        r = trade(a, i, side)
        if r is None: skipped["no_room"] += 1; continue
        mfe = (a[i:i + 720, 2].max() / a[i, 1] - 1) if side > 0 else (1 - a[i:i + 720, 3].min() / a[i, 1])
        cand = np.r_[np.arange(i - 60 * 24, i - 30 * 24), np.arange(i + 30 * 24, i + 60 * 24)]; cand = cand[(cand >= 0) & (cand + HOLD < len(a))]
        rnd = [trade(a, int(j), side) for j in rng.choice(cand, size=min(30, len(cand)), replace=False)] if len(cand) else []
        key = (b, ts); dup = key in seen; seen.add(key)
        rows.append(dict(ts=ts, dup=dup, side=side, gross=r, mfe=mfe, site_pnl=c["pnl"], slip=a[i, 1] / c["entryPrice"] - 1 if c["entryPrice"] else None, rnd=rnd))
    out = dict(calls_total=len(calls), scored_rows=len(rows), skipped=skipped, results={})
    for label, use in (("unique_coin_time", lambda r: not r["dup"]), ("all_rows", lambda r: True)):
        res = {}
        for per, sel in (("VALIDATION_2024-12_to_2025-06", lambda r: r["ts"] < SPLIT), ("TEST_2025-07_to_2026-11", lambda r: r["ts"] >= SPLIT), ("ALL", lambda r: True)):
            s = [r for r in rows if use(r) and sel(r)]
            if len(s) < 5: continue
            q = dict(n=len(s), site_method_mfe_mean_pct=round(float(np.mean([r["mfe"] for r in s]) * 100), 2), site_method_win_pct=round(float(np.mean([r["mfe"] > 0.02 for r in s]) * 100), 1),
                     entry_gap_vs_site_median_pct=round(float(np.nanmedian([r["slip"] for r in s if r["slip"] is not None]) * 100), 2))
            for k, name in enumerate(("E1_stop5_target10_7d", "E2_hold24h", "E3_hold7d")):
                net = np.array([r["gross"][k] - 2 * COST for r in s]); st = np.array([r["gross"][k] - 2 * STRESS for r in s])
                sims = [r for r in s if len(r["rnd"]) >= 5]; m = np.array([[x[k] - 2 * COST for x in r["rnd"][:30]] + [np.nan] * (30 - len(r["rnd"][:30])) for r in sims])
                cnt = np.array([min(30, len(r["rnd"])) for r in sims]); pick = (rng.random((1000, len(sims))) * cnt).astype(int); vals = m[np.arange(len(sims))[None, :], pick]
                means = np.nanmean(vals, axis=1); act = float(np.mean([r["gross"][k] - 2 * COST for r in sims]))
                q[name] = dict(net=stats(net), stress_mean_pct=round(float(st.mean() * 100), 3), random_mean_pct=round(float(np.nanmean(means) * 100), 3), p_vs_random=float((means >= act).mean()))
            res[per] = q
        out["results"][label] = res
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__":
    main()
