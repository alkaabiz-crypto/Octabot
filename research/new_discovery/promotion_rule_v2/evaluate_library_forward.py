"""Read-only evaluator for the library paper tests (ETH_FIB, OIL_FIB, GOLD_FVG; ledgers written by the frozen
research/library_forward/forward.py on branch claude/download-skill-27d08k). Reports, per test, side by side:
  1. the FROZEN rule (FORWARD_RULES.md): at >= 100 closed trades, PASS if mean net_bp_2x > 0 and >= 2 bp;
  2. RULE V2 (PROMOTION_RULE_V2.md): looks at 100/300/600/1000, PASS if Newey-West t >= 2.87 and mean >= 2 bp, STOP if mean +
     1.645 se < 2 bp;
  3. a VENUE-COST view for gold and oil: net_bp_2x minus Hyperliquid base-tier fees (maker 1.5 bp entry; exit maker 1.5 bp at a
     target, taker 4.5 bp otherwise); see research/audits/library_candidates/HYPERLIQUID_COSTS.md. Funding is not included.
It changes nothing. usage: python3 -I evaluate_library_forward.py <dir containing ledger_<TEST>.csv files>
"""
import csv, math, os, sys

LOOKS = (100, 300, 600, 1000); Z = 2.87; MIN_BP = 2.0; MAKER, TAKER = 1.5, 4.5


def nw(x, L=5):
    n = len(x); m = sum(x) / n; d = [v - m for v in x]
    g = lambda j: sum(d[i] * d[i - j] for i in range(j, n)) / n
    v = g(0) + 2 * sum((1 - j / (L + 1)) * g(j) for j in range(1, min(L, n - 1) + 1))
    return m, math.sqrt(max(v, 1e-12) / n)


def v2(x):
    for n in LOOKS:
        if len(x) < n: return f"no look reached yet (next at {n} trades)"
        m, se = nw(x[:n])
        if m / se >= Z and m >= MIN_BP: return f"PASS at {n} trades (mean {m:+.2f} bp, NW t {m / se:.2f})"
        if m + 1.645 * se < MIN_BP: return f"STOP for futility at {n} trades (mean {m:+.2f} bp, upper bound {m + 1.645 * se:+.2f} bp)"
    return "UNDECIDED after 1,000 trades (never a pass)"


def evaluate(path, test):
    rows = list(csv.DictReader(open(path))) if os.path.exists(path) else []
    x = [float(r["net_bp_2x"]) for r in rows]; n = len(x)
    out = [f"## {test}: {n} closed trades"]
    if not n: return out + ["- no closed trades yet", ""]
    m = sum(x) / n; out.append(f"- mean net at 2x cost (paper-test model): {m:+.2f} bp per trade; wins {sum(v > 0 for v in x)}/{n}")
    out.append("- frozen rule: " + ("not evaluated before 100 trades" if n < 100 else ("PASS" if (sum(x[:100]) / 100 >= MIN_BP) else "FAIL") +
                                  f" (mean of first 100 = {sum(x[:100]) / 100:+.2f} bp; note: passes a zero-edge strategy about 35-45% of the time)"))
    out.append("- rule V2: " + v2(x))
    if test in ("GOLD_FVG", "OIL_FIB"):
        fees = [MAKER + (MAKER if r["reason"] == "target" else TAKER) for r in rows]; y = [a - b for a, b in zip(x, fees)]
        out.append(f"- with Hyperliquid base-tier fees (not modelled by the paper test): {sum(y) / n:+.2f} bp per trade; rule V2 on that: {v2(y)}")
    return out + [""]


def main():
    d = sys.argv[1]; lines = ["# Library paper tests: frozen rule vs rule V2 vs venue costs (read-only)", ""]
    for t in ("ETH_FIB", "OIL_FIB", "GOLD_FVG"): lines += evaluate(os.path.join(d, f"ledger_{t}.csv"), t)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
