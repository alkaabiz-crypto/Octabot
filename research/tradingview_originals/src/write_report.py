"""Write reports/RESULTS.md from reports/results.json."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def row(k, r):
    s, c = r["selection 2025"], r["confirmation 2026"]
    f = lambda x: f"{x['trades']} | {x.get('win_rate_pct', 0):.1f}% | {x.get('expectancy_r', 0):+.3f}R | {x.get('random_mean_r', 0):+.3f}R | {x.get('p_random', 1):.3f}"  # noqa: E731
    flag = "**reliable**" if r["reliable"] else ("2025 only" if r["passes_selection"] else "")
    return f"| {k} | {f(s)} | {f(c)} | {flag} |"


def main():
    d = json.load(open(os.path.join(ROOT, "reports", "results.json")))
    lines = ["# Results: original TradingView scripts", "", f"Generated {d['meta']['generated_utc']} UTC from `results.json`. "
             "Primary cost. 'Random' is the matched random-entry (standard exits) or duration-matched (FLIP, NATIVE) benchmark mean.", ""]
    total = passed_sel = reliable = 0
    for mkt in ("USOILm", "XAUUSDm", "BTCUSDm"):
        res = d[mkt]
        total += len(res)
        passed_sel += sum(r["passes_selection"] for r in res.values())
        reliable += sum(r["reliable"] for r in res.values())
        lines += [f"## {mkt}", "", "| Variant | 2025 trades | win | E | random | p | 2026 trades | win | E | random | p | status |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        lines += [row(k, r) for k, r in res.items()]
        lines.append("")
    lines[3:3] = [f"**{total} variants. {passed_sel} passed 2025 (about {total * 0.05:.0f} expected by luck). {reliable} passed both years.**", ""]
    open(os.path.join(ROOT, "reports", "RESULTS.md"), "w").write("\n".join(lines) + "\n")
    print(total, passed_sel, reliable)
    for mkt in ("USOILm", "XAUUSDm", "BTCUSDm"):
        for k, r in d[mkt].items():
            if r["passes_selection"] or r["win_rate_70_both"]:
                print(mkt, row(k, r))


if __name__ == "__main__":
    main()
