"""Missing-data sensitivity (FREEZE reconciliation item 3): every combination with and without the Exness archive-hole rule.

ORIGINAL  = trades spanning 2026-03-29 23:59 -> 2026-04-01 00:00 kept (as first run, before the data audit)
CORRECTED = those trades dropped (engine.DATA_HOLES_MIN), the published results
Metrics per period at 2x cost: trades, mean bp, sum %, compounded %, max drawdown of compounded equity, t-stat of the mean,
percentile against the 500-draw random control (same seeds as run.py), verdict and holdout rank.
Average R is not reported: most theories are position strategies without a defined stop, so R is undefined; bp of price is used.

Usage: BARS_DIR=<orb 1m bars> python3 -I sensitivity_hole.py
"""
import json, os, sys, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E  # noqa: E402
import theories as T, theories_f as TF, theories_g as TG  # noqa: E402

DRAWS, SEED = 500, 20261112


def rand_means(c, meta, rng):
    o, hs, ms = c.o.values, c.hs.values, c.ms.values; n = len(o); split = int(np.searchsorted(ms, E.HOLDOUT_MS)); out = {}
    for p, (lo, hi) in (("dev", (0, split)), ("holdout", (split, n))):
        sel = meta[(meta[:, 0] >= lo) & (meta[:, 0] < hi)]
        if not len(sel): out[p] = None; continue
        dur, side = sel[:, 1], sel[:, 2]; span = np.maximum(hi - lo - dur - 1, 1)
        s = lo + (rng.random((DRAWS, len(sel))) * span).astype(int); e = np.minimum(s + dur, n - 1)
        out[p] = (side * (o[e] - o[s]) / o[s] - 2 * (hs[s] + hs[e]) / o[s]).mean(axis=1)
    return out


def stats(r, rnd):
    if not len(r): return dict(trades=0)
    eq = np.cumprod(1 + r); dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    t = float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))) if len(r) > 1 and r.std() > 0 else None
    return dict(trades=int(len(r)), mean_bp=round(float(r.mean() * 1e4), 2), sum_pct=round(float(r.sum() * 100), 2), compounded_pct=round(float((eq[-1] - 1) * 100), 2),
                max_dd_pct=round(dd * 100, 2), t_stat=round(t, 2) if t is not None else None,
                random_pct=round(float((rnd < r.mean()).mean() * 100), 1) if rnd is not None else None, random_p95_bp=round(float(np.percentile(rnd, 95) * 1e4), 2) if rnd is not None else None)


def run(hole):
    E.HOLE_MARKETS = E.HOLE_MARKETS if hole else (); E.candles.cache_clear(); out = {}
    for reg in (T.REGISTRY, TF.REGISTRY_F, TG.REGISTRY_G):
        for tid, fam, tfs, mkts, fn in reg:
            for m in mkts:
                for tf in tfs:
                    if E.candles(m, tf) is None: continue
                    key = f"{tid}|{m}|{tf}"; res = fn(m, tf)
                    if res is None: continue
                    c, bk = res; r2, meta = E.evaluate(c, bk, 2); rnd = rand_means(c, meta, np.random.default_rng(SEED + zlib.crc32(key.encode()) % 100000)) if len(meta) else {"dev": None, "holdout": None}
                    d, h = stats(r2["dev"], rnd["dev"]), stats(r2["holdout"], rnd["holdout"])
                    ok = d.get("trades", 0) and h.get("trades", 0) >= 30 and d["mean_bp"] > 0 and h["mean_bp"] > 0 and d["random_p95_bp"] is not None and d["mean_bp"] > d["random_p95_bp"] and h["mean_bp"] > h["random_p95_bp"]
                    out[key] = dict(dev=d, holdout=h, verdict="PASS" if ok else "FAIL")
    keys = sorted(out, key=lambda k: -(out[k]["holdout"].get("mean_bp") if out[k]["holdout"].get("mean_bp") is not None else -1e9))
    for rank, k in enumerate(keys, 1): out[k]["holdout_rank"] = rank
    return out


def main():
    hole_markets = E.HOLE_MARKETS; orig = run(False); E.HOLE_MARKETS = hole_markets; corr = run(True)
    ch = []
    for k in corr:
        a, b = orig[k], corr[k]; da = a["dev"].get("trades", 0) + a["holdout"].get("trades", 0); db = b["dev"].get("trades", 0) + b["holdout"].get("trades", 0)
        if da != db:
            p = "holdout" if a["holdout"].get("trades", 0) != b["holdout"].get("trades", 0) else "dev"
            ch.append(dict(key=k, period=p, removed_trades=da - db, mean_bp=[a[p].get("mean_bp"), b[p].get("mean_bp")], sum_pct=[a[p].get("sum_pct"), b[p].get("sum_pct")],
                           max_dd_pct=[a[p].get("max_dd_pct"), b[p].get("max_dd_pct")], t_stat=[a[p].get("t_stat"), b[p].get("t_stat")],
                           random_pct=[a[p].get("random_pct"), b[p].get("random_pct")], holdout_rank=[a["holdout_rank"], b["holdout_rank"]], verdict=[a["verdict"], b["verdict"]]))
    summary = dict(combinations=len(corr), affected=len(ch), removed_trades=int(sum(x["removed_trades"] for x in ch)), verdict_changes=[x for x in ch if x["verdict"][0] != x["verdict"][1]],
                   pass_original=sorted(k for k, v in orig.items() if v["verdict"] == "PASS"), pass_corrected=sorted(k for k, v in corr.items() if v["verdict"] == "PASS"),
                   largest_mean_bp_changes=sorted(ch, key=lambda x: -abs((x["mean_bp"][0] or 0) - (x["mean_bp"][1] or 0)))[:10],
                   largest_rank_changes=sorted(ch, key=lambda x: -abs(x["holdout_rank"][0] - x["holdout_rank"][1]))[:10])
    json.dump(orig, open(os.path.join(HERE, "results", "sensitivity_original_no_hole_rule.json"), "w"), indent=1)
    json.dump(corr, open(os.path.join(HERE, "results", "sensitivity_corrected.json"), "w"), indent=1)
    json.dump(dict(summary=summary, affected=ch), open(os.path.join(HERE, "results", "sensitivity_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("largest_mean_bp_changes", "largest_rank_changes")}, indent=1))
    for x in summary["largest_mean_bp_changes"]: print("bp", x)
    for x in summary["largest_rank_changes"]: print("rank", x["key"], x["holdout_rank"], x["mean_bp"])


if __name__ == "__main__":
    main()
