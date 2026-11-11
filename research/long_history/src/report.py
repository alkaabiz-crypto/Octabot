"""Apply the pre-registered pass rule to reports/raw_*.json; write reports/results.json and reports/RESULTS.md."""
import glob
import json
import os
import statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MKTS = ("USOILm", "XAUUSDm", "BTCUSDm")


def benjamini_hochberg(pvals, q=0.05):
    """Indices of the hypotheses rejected at false-discovery rate q."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m, k_max = len(pvals), 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            k_max = rank
    return set(order[:k_max])


def consistent(r):
    yrs = [v for v in r.get("years", {}).values() if v[0] >= 10]
    h = r.get("halves", [None, None])
    return (None not in h and h[0] > 0 and h[1] > 0 and yrs and sum(v[1] > 0 for v in yrs) >= 2 * len(yrs) / 3)


def main():
    res = {m: {} for m in MKTS}
    for path in glob.glob(os.path.join(ROOT, "reports", "raw_*.json")):
        d = json.load(open(path))
        res[d["meta"]["market"]].update(d["results"])
    keys = [(m, k) for m in MKTS for k in res[m]]
    pvals = [res[m][k].get("p_z", 1.0) for m, k in keys]
    rejected = benjamini_hochberg(pvals)
    for idx, (m, k) in enumerate(keys):
        r = res[m][k]
        r["fdr_significant"] = idx in rejected
        r["consistent"] = bool(consistent(r))
        r["passes"] = (r["trades"] >= 200 and r.get("expectancy_r", -1) > 0 and r.get("expectancy_stress_r", -1) > 0
                       and r["fdr_significant"] and r["consistent"])
        r["worthy_70"] = r["passes"] and r.get("win_rate_pct", 0) >= 70
    json.dump(res, open(os.path.join(ROOT, "reports", "results.json"), "w"))
    tested = [(m, k) for m, k in keys if res[m][k]["trades"] >= 30]
    L = ["# Results: every indicator on the full available history", "",
         f"{len(keys)} variants; {len(tested)} had at least 30 trades. Primary cost. z and p are against matched random entry.", "",
         "## Summary", "", "| Market | Variants | ≥ 200 trades | Raw p ≤ 0.05 | Significant after FDR | Passes all rules | 70%+ and passes |",
         "|---|---|---|---|---|---|---|"]
    for m in MKTS:
        rs = list(res[m].values())
        L.append(f"| {m} | {len(rs)} | {sum(r['trades'] >= 200 for r in rs)} | {sum(r.get('p_z', 1) <= 0.05 for r in rs)} | "
                 f"{sum(r['fdr_significant'] for r in rs)} | {sum(r['passes'] for r in rs)} | {sum(r['worthy_70'] for r in rs)} |")
    n_ok = sum(1 for m, k in keys if res[m][k].get("p_z") is not None)
    L += ["", f"With {n_ok} variants and no real edge anywhere, about {0.05 * n_ok:.0f} would show raw p ≤ 0.05 by luck.", ""]

    def row(m, k, r):
        yrs = " ".join(f"{y[2:]}:{v[1]:+.2f}" for y, v in r.get("years", {}).items() if v[0] >= 10)
        return (f"| {m} | {k} | {r['trades']} | {r.get('win_rate_pct', 0):.1f}% | {r.get('random_win_rate_pct', float('nan')):.1f}% | "
                f"{r.get('expectancy_r', 0):+.3f}R | {r.get('expectancy_stress_r', 0):+.3f}R | {r.get('random_mean_r', 0):+.3f}R | "
                f"{r.get('z', 0):+.2f} | {r.get('p_z', 1):.2g} | {'yes' if r['fdr_significant'] else 'no'} | {'yes' if r['consistent'] else 'no'} | {yrs} |")
    head = ["| Market | Variant | Trades | Win | Random win | E | E stress | Random E | z | p | FDR | Consistent | By year |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    L += ["## Passing variants", ""] + head + [row(m, k, res[m][k]) for m, k in keys if res[m][k]["passes"]]
    top = sorted((x for x in keys if res[x[0]][x[1]]["trades"] >= 200), key=lambda x: -res[x[0]][x[1]].get("z", -99))[:40]
    L += ["", "## Top 40 by z-score (at least 200 trades), passing or not", ""] + head + [row(m, k, res[m][k]) for m, k in top]
    hi = [(m, k) for m, k in keys if res[m][k]["trades"] >= 200 and res[m][k].get("win_rate_pct", 0) >= 70]
    L += ["", f"## Variants winning 70%+ of at least 200 trades ({len(hi)})", ""] + head + [row(m, k, res[m][k]) for m, k in hi]
    for m in MKTS:
        hw = [r for k, r in res[m].items() if k.endswith("|HW") and r["trades"] >= 200]
        if hw:
            L.append(f"\n{m}, target half the stop: median win rate {statistics.median(r['win_rate_pct'] for r in hw):.1f}%, "
                     f"random entries {statistics.median(r['random_win_rate_pct'] for r in hw):.1f}%.")
    open(os.path.join(ROOT, "reports", "RESULTS.md"), "w").write("\n".join(L) + "\n")
    print(open(os.path.join(ROOT, "reports", "RESULTS.md")).read()[:6000])


if __name__ == "__main__":
    main()
