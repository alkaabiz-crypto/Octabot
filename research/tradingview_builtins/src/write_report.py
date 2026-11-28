"""Write reports/RESULTS.md from reports/results_<market>.json and reports/untouched.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MKTS = ("USOILm", "XAUUSDm", "BTCUSDm")
PART = {"A": "Built-in strategies", "B": "Built-in indicators", "C": "ChartArt community strategies", "D": "Signal + entry filter"}


def cell(x):
    return f"{x['trades']} | {x.get('win_rate_pct', 0):.1f}% | {x.get('expectancy_r', 0):+.3f}R | {x.get('p_random', 1):.3f}"


def main():
    res = {m: json.load(open(os.path.join(ROOT, "reports", f"results_{m}.json")))["results"] for m in MKTS}
    unt_path = os.path.join(ROOT, "reports", "untouched.json")
    unt = json.load(open(unt_path)) if os.path.exists(unt_path) else {}
    L = ["# Results: every TradingView built-in, ChartArt's community strategies, and signal + filter combinations", "",
         "Primary cost (real Exness spread + 0.02% slippage). Columns per period: trades | win rate | expectancy | p vs random.",
         "", "## Summary", "", "| Market | Part | Variants | Passed 2025 | Passed both years | Expected to pass both by luck | 70%+ win both years |",
         "|---|---|---|---|---|---|---|"]
    for m in MKTS:
        for p in "ABCD":
            rs = [r for k, r in res[m].items() if k.startswith(p + "|")]
            if not rs:
                continue
            L.append(f"| {m} | {PART[p]} | {len(rs)} | {sum(r['passes_selection'] for r in rs)} | {sum(r['reliable'] for r in rs)} | "
                     f"{len(rs) * 0.05 * 0.05:.1f} | {sum(r['win_rate_70_both'] for r in rs)} |")
    L += ["", "## Passed both years, and the untouched-data check", "",
          "| Market | Variant | 2025 | 2026 | Untouched data | Validated |", "|---|---|---|---|---|---|"]
    for m in MKTS:
        for k, r in res[m].items():
            if r["reliable"]:
                u = unt.get(m, {}).get(k)
                L.append(f"| {m} | {k} | {cell(r['selection 2025'])} | {cell(r['confirmation 2026'])} | "
                         f"{cell(u) if u else 'not run'} | {'**yes**' if u and u['validated'] else 'no'} |")
    L += ["", "## 70%+ win rate in both years", "", "| Market | Variant | 2025 | 2026 | Random win rate 2025 / 2026 |", "|---|---|---|---|---|"]
    for m in MKTS:
        for k, r in res[m].items():
            if r["win_rate_70_both"] and r["selection 2025"]["trades"] >= 30:
                s, c = r["selection 2025"], r["confirmation 2026"]
                L.append(f"| {m} | {k} | {cell(s)} | {cell(c)} | {s.get('random_win_rate_pct', float('nan')):.1f}% / {c.get('random_win_rate_pct', float('nan')):.1f}% |")
    for m in MKTS:
        L += ["", f"## All variants: {m}", "", "| Variant | 2025 | | | | 2026 | | | | status |", "|---|---|---|---|---|---|---|---|---|---|"]
        for k, r in res[m].items():
            st = "**both years**" if r["reliable"] else ("2025 only" if r["passes_selection"] else "")
            L.append(f"| {k} | {cell(r['selection 2025'])} | {cell(r['confirmation 2026'])} | {st} |")
    open(os.path.join(ROOT, "reports", "RESULTS.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
