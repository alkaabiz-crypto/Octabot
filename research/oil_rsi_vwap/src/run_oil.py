"""Run the pre-registered US oil RSI + VWAP study. Writes reports/results.json (tables are in README.md)."""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oil
import study as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIMARY_KEY = "V1_VWAP_MOMENTUM|BUY|TRAIL"


def evaluate(a, trades, d, ex, w0, w1, bench=True):
    rs = [t.r("primary") for t in trades]
    s = S.summary(rs)
    if s["trades"] < 2:
        return s
    s["ci95"] = S.boot_ci(rs)
    s["expectancy_stress_r"] = statistics.mean(t.r("stress") for t in trades)
    s["expectancy_spread_only_r"] = statistics.mean(t.r_gross for t in trades)
    s["avg_hold_hours"] = statistics.mean(t.hold_hours for t in trades)
    s["exit_reasons"] = {r: sum(t.reason == r for t in trades) for r in {t.reason for t in trades}}
    s["regimes"] = {}
    for reg in ("bull", "bear", "sideways", "undefined"):
        x = S.summary([t.r("primary") for t in trades if t.regime == reg])
        s["regimes"][reg] = {k: x.get(k) for k in ("trades", "expectancy_r", "t_stat", "win_rate_pct")}
    if bench:
        s["benchmark"] = S.random_benchmark(a, trades, d, ex, w0, w1)
    return s


def main():
    t0 = time.time()
    a = oil.OilAsset(os.path.join(ROOT, "data", "USOILm_15m.csv.gz"))
    w0, w_end = S.ts(2025, 1), a.e.t[-1] + 3600
    periods = [("2025-01..now", w0, w_end, True), ("2025", w0, S.ts(2026, 1), False), ("2026", S.ts(2026, 1), w_end, False)]
    out = {"meta": {"generated_utc": S.fmt(time.time()), "first_quote": S.fmt(a.q["t"][0]), "last_quote": S.fmt(a.q["t"][-1]),
                        "statistics_from": S.fmt(w0), "buy_and_hold_pct": (a.e.c[-1] / a.e.c[a.e_idx[min(t for t in a.e.t if t >= w0)]] - 1) * 100}}
    for rule in S.RULES:
        for dname, d in S.DIRECTIONS.items():
            for ex in S.EXITS:
                key = f"{rule}|{dname}|{ex}"
                out[key] = {}
                for pname, p0, p1, bench in periods:
                    tr = a.run(rule, d, ex, p0, p1)
                    out[key][pname] = evaluate(a, tr, d, ex, p0, p1, bench)
                s = out[key]["2025-01..now"]
                b = s.get("benchmark", {})
                print(f"{key:34} n={s['trades']:>4} win={s.get('win_rate_pct', 0):5.1f} PF={s.get('profit_factor') or 0:.2f} "
                      f"E={s.get('expectancy_r', 0):+.3f} t={s.get('t_stat') or 0:+.2f} rand={b.get('random_mean_r', 0):+.3f} p_rand={b.get('p_random', 1):.3f}", flush=True)
    adj = S.holm({k: out[k]["2025-01..now"].get("p_one_sided") for k in out if k != "meta"})
    for k in adj:
        out[k]["2025-01..now"]["p_holm_all_8"] = adj[k]
    s = out[PRIMARY_KEY]["2025-01..now"]
    fails = []
    if s["trades"] < 100:
        fails.append("fewer than 100 trades")
    if not (s.get("expectancy_r", -1) > 0 and (s.get("t_stat") or 0) >= 2):
        fails.append("expectancy not > 0 with t >= 2")
    if not s.get("benchmark", {}).get("p_random", 1) <= 0.05:
        fails.append("not better than matched random entry (p_random > 0.05)")
    if not s.get("expectancy_stress_r", -1) > 0:
        fails.append("expectancy <= 0 at stress cost")
    out["verdict"] = {"primary": PRIMARY_KEY, "transfers_to_oil": not fails, "failed": fails}
    with open(os.path.join(ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s; verdict: {out['verdict']}")


if __name__ == "__main__":
    main()
