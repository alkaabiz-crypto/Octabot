"""Apply PROTOCOL.md section 10 to results/batch_001.json; write RESULTS.md and append to ../REGISTRY.csv."""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import common as C  # noqa: E402

INFO = {
    "D001": ("Statistical-arbitrage pairs (spread z-score reversion)", "1h", "Gatev, Goetzmann & Rouwenhorst (2006); Büyükşahin et al. (2013)",
             "z of ln(A)-ln(B) over 480 h; |z|>=2 enter against the spread, exit z=0, |z|>=4 or 120 h", "z 480 h, entry 2, stop 4, max 120 h"),
    "D002": ("Cross-market relative strength (risk-adjusted 60-day momentum)", "weekly", "Asness, Moskowitz & Pedersen (2013)",
             "each Monday long top-3 / short bottom-3 of 11 markets by 60-day return/vol, inverse-vol weights", "lookback 60 d, top/bottom 3"),
    "D003": ("Regime-adaptive trend / mean reversion (efficiency ratio)", "4h", "Kaufman (2013); Daniel & Moskowitz (2016)",
             "ER20>=0.35 follow 20-bar direction; ER20<=0.15 fade |z20|>=1.5; else flat; hold 1 bar, runs merged", "ER 0.35/0.15, z 1.5, 20 bars"),
    "D004": ("Walk-forward logistic direction model (8 price features)", "1h", "Gu, Kelly & Xiu (2020); Krauss, Do & Huck (2017)",
             "monthly expanding refit; long p>=0.55, short p<=0.45, hold 4 h, no overlap", "L2 lambda 1, thresholds 0.55/0.45, horizon 4 h"),
}
COSTS = "Exness bid/ask + 0.5x median spread slippage (stress 1.5x + 0.02%/day)"


def units(exp):
    if exp == "D001":
        return [(k, v["results"]) for k, v in DATA["D001"].items()]
    if exp == "D002":
        return [("portfolio", DATA["D002"]["portfolio"]["results"])]
    if exp == "D003":
        return [(k, v["adaptive"]) for k, v in DATA["D003"].items()]
    return [(k, {p: v[p] for p in v if p in list(C.PERIODS) + ["SINCE_2025"]}) for k, v in DATA["D004"].items()]


def main():
    global DATA
    DATA = json.load(open(os.path.join(HERE, "results", "batch_001.json")))
    rows = []
    for exp in ("D001", "D002", "D003", "D004"):
        for mkt, r in units(exp):
            rows.append((exp, mkt, r))
    tp = [r["TEST"].get("p_vs_benchmark", 1.0) for _, _, r in rows]
    rej = C.bh(tp)
    out_rows, md = [], ["# Batch 001 results", "",
                        "Pre-registered in `PREREG.md`. Costs are at primary level unless noted. The p-value is one-sided, against each experiment's random benchmark.",
                        "", f"**26 TEST-period tests, Benjamini–Hochberg at 5%: {len(rej)} significant.**", "",
                        "| Exp | Market | TRAIN n, mean bp | VALID n, mean bp | TEST n, mean bp (stress) | TEST 95% CI | TEST PF | TEST max DD bp | TEST p | Since 2025 n, mean bp | Decision |",
                        "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (exp, mkt, r) in enumerate(rows):
        tr, va, te, s25 = r["TRAIN"], r["VALIDATION"], r["TEST"], r["SINCE_2025"]
        pos_all = all(x.get("mean_bp", -1) > 0 for x in (tr, va, te))
        n_min = 52 if exp == "D002" else 30
        cand = pos_all and te.get("mean_stress_bp", -1) > 0 and te.get("p_vs_benchmark", 1) <= 0.05 and i in rej and te.get("trades", 0) >= n_min
        dec = "CANDIDATE" if cand else ("WATCH" if pos_all else "REJECT")
        why = ("passed every pre-registered rule" if cand else
               "positive in all periods but not significant after correction" if pos_all else
               "not positive in every period" + ("" if te.get("mean_bp", -1) > 0 else "; TEST mean <= 0"))

        def f(x):
            return f"{x.get('trades', 0)}, {x.get('mean_bp', float('nan')):+.1f}" if "mean_bp" in x else f"{x.get('trades', 0)}, -"
        ci = te.get("ci95_bp", [float("nan")] * 2)
        md.append(f"| {exp} | {mkt} | {f(tr)} | {f(va)} | {f(te)} ({te.get('mean_stress_bp', float('nan')):+.1f}) | "
                  f"{ci[0]:+.1f} to {ci[1]:+.1f} | {te.get('profit_factor') or float('nan'):.2f} | {te.get('max_drawdown_bp', float('nan')):.0f} | "
                  f"{te.get('p_vs_benchmark', float('nan')):.3f} | {f(s25)} | **{dec}** |")
        name, tf, ref, rules, params = INFO[exp]
        out_rows.append({"experiment_id": f"{exp}-{mkt}", "batch": "001", "name": name, "market": mkt, "timeframe": tf,
                         "hypothesis_ref": "batch_001/PREREG.md", "source": ref, "rules": rules, "parameters": params,
                         "periods": "TRAIN 2023-01..2024-06 / VALID 2024-07..2025-06 / TEST 2025-07..latest", "variants_tested": 1,
                         "data": "Exness 15m bid/ask (ticks.ex2archive.com), not archived", "costs": COSTS,
                         "train_mean_bp": round(tr.get("mean_bp", float("nan")), 2), "valid_mean_bp": round(va.get("mean_bp", float("nan")), 2),
                         "test_mean_bp": round(te.get("mean_bp", float("nan")), 2), "test_stress_bp": round(te.get("mean_stress_bp", float("nan")), 2),
                         "test_trades": te.get("trades", 0), "test_p": round(te.get("p_vs_benchmark", float("nan")), 4),
                         "bh_significant": i in rej, "robustness": "not run (only for CANDIDATEs)", "decision": dec, "reason": why})
    if "D003" in DATA:
        md += ["", "### D003 components (information only, not decisions): TEST mean bp per trade", "", "| Market | trend-only | range-only |", "|---|---|---|"]
        for m, v in DATA["D003"].items():
            md.append(f"| {m} | {v['trend_only (info)']['TEST'].get('mean_bp', float('nan')):+.1f} ({v['trend_only (info)']['TEST'].get('trades', 0)}) | "
                      f"{v['range_only (info)']['TEST'].get('mean_bp', float('nan')):+.1f} ({v['range_only (info)']['TEST'].get('trades', 0)}) |")
    if "D001" in DATA:
        md += ["", "### D001 diagnostics", ""]
        for k, v in DATA["D001"].items():
            md.append(f"- {k}: {json.dumps(v['diagnostics'])}")
    if "D002" in DATA:
        p = DATA["D002"]["portfolio"]["results"]
        md += ["", "### D002 portfolio extras", "", "| Period | Sharpe (annual) | Equal-weight long, mean bp per week | Top-3 long only, mean bp per week |", "|---|---|---|---|"]
        for per, v in p.items():
            md.append(f"| {per} | {v.get('sharpe_annual') if v.get('sharpe_annual') is None else round(v['sharpe_annual'], 2)} | "
                      f"{v.get('benchmark_equal_weight_long_mean_bp', float('nan')):+.1f} | {v.get('benchmark_top3_long_mean_bp', float('nan')):+.1f} |")
    open(os.path.join(HERE, "RESULTS.md"), "w").write("\n".join(md) + "\n")
    reg = os.path.join(ROOT, "REGISTRY.csv")
    old = [r for r in csv.DictReader(open(reg))] if os.path.exists(reg) else []
    old = [r for r in old if r["batch"] != "001"]
    with open(reg, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(out_rows[0]))
        w.writeheader()
        w.writerows(old + out_rows)
    print("\n".join(md[:40]))


if __name__ == "__main__":
    main()
