"""Run the pre-registered indicator scan (PROTOCOL.md). Writes reports/results.json and reports/RESULTS.md."""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scan
import study as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_RESEARCH = os.path.dirname(ROOT)
MARKETS = {"USOILm": os.path.join(REPO_RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"),
           "XAUUSDm": os.path.join(REPO_RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz")}
RUNS = 1000


def evaluate(a, trades, d, ex, w0, w1):
    rs = [t.r("primary") for t in trades]
    s = S.summary(rs)
    if s["trades"] < 2:
        return s
    s["expectancy_stress_r"] = statistics.mean(t.r("stress") for t in trades)
    pool = [t for t in a.table(d, ex) if t is not None and w0 <= t.entry_time < w1]
    s["random_win_rate_pct"] = sum(t.r("primary") > 0 for t in pool) / len(pool) * 100
    b = S.random_benchmark(a, trades, d, ex, w0, w1, runs=RUNS)
    s["random_mean_r"], s["p_random"] = b["random_mean_r"], b["p_random"]
    return s


def main():
    t0 = time.time()
    out = {"meta": {"generated_utc": S.fmt(time.time()), "runs": RUNS}}
    for mkt, path in MARKETS.items():
        a = scan.ScanAsset(path)
        end = a.e.t[-1] + 3600
        periods = {"selection 2025": (S.ts(2025, 1), S.ts(2026, 1)), "confirmation 2026": (S.ts(2026, 1), end)}
        out[mkt] = {}
        for ind in scan.INDICATORS:
            for dname, d in S.DIRECTIONS.items():
                sig = a.scan_signals(ind, d)
                for ex in scan.EXITS:
                    key = f"{ind}|{dname}|{ex}"
                    res = {p: evaluate(a, a.run_signals(sig, d, ex, w0, w1), d, ex, w0, w1) for p, (w0, w1) in periods.items()}
                    sel, con = res["selection 2025"], res["confirmation 2026"]
                    res["passes_selection"] = sel["trades"] >= 30 and sel.get("expectancy_r", -1) > 0 and sel.get("p_random", 1) <= 0.05
                    res["passes_confirmation"] = con["trades"] >= 20 and con.get("expectancy_r", -1) > 0 and con.get("p_random", 1) <= 0.05
                    res["reliable"] = res["passes_selection"] and res["passes_confirmation"]
                    res["win_rate_70_both"] = all(r.get("win_rate_pct", 0) >= 70 for r in (sel, con))
                    out[mkt][key] = res
                    print(f"{mkt} {key:30} sel n={sel['trades']:>4} win={sel.get('win_rate_pct', 0):5.1f} E={sel.get('expectancy_r', 0):+.3f} "
                          f"p={sel.get('p_random', 1):.3f} | conf n={con['trades']:>4} win={con.get('win_rate_pct', 0):5.1f} "
                          f"E={con.get('expectancy_r', 0):+.3f} p={con.get('p_random', 1):.3f}{'  RELIABLE' if res['reliable'] else ''}", flush=True)
    with open(os.path.join(ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
