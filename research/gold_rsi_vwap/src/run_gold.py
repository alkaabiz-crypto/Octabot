"""Run the pre-registered gold study with the US oil study's code (read-only). Writes reports/results.json."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "oil_rsi_vwap", "src"))
import oil
import run_oil
import study as S


def main():
    t0 = time.time()
    a = oil.OilAsset(os.path.join(ROOT, "data", "XAUUSDm_15m.csv.gz"))
    w0, w_end = S.ts(2025, 1), a.e.t[-1] + 3600
    first = next(i for i, t in enumerate(a.e.t) if t >= w0)
    periods = [("2025-01..now", w0, w_end, True), ("2025", w0, S.ts(2026, 1), False), ("2026", S.ts(2026, 1), w_end, False)]
    out = {"meta": {"generated_utc": S.fmt(time.time()), "first_quote": S.fmt(a.q["t"][0]), "last_quote": S.fmt(a.q["t"][-1]),
                        "statistics_from": S.fmt(w0), "buy_and_hold_pct": (a.e.c[-1] / a.e.o[first] - 1) * 100,
                        "sessions": a.session[-1]}}
    for rule in S.RULES:
        for dname, d in S.DIRECTIONS.items():
            for ex in S.EXITS:
                key = f"{rule}|{dname}|{ex}"
                out[key] = {p: run_oil.evaluate(a, a.run(rule, d, ex, p0, p1), d, ex, p0, p1, bench) for p, p0, p1, bench in periods}
                s = out[key]["2025-01..now"]
                b = s.get("benchmark", {})
                print(f"{key:34} n={s['trades']:>4} win={s.get('win_rate_pct', 0):5.1f} PF={s.get('profit_factor') or 0:.2f} "
                      f"E={s.get('expectancy_r', 0):+.3f} t={s.get('t_stat') or 0:+.2f} rand={b.get('random_mean_r', 0):+.3f} p_rand={b.get('p_random', 1):.3f}", flush=True)
    adj = S.holm({k: out[k]["2025-01..now"].get("p_one_sided") for k in out if k != "meta"})
    for k in adj:
        out[k]["2025-01..now"]["p_holm_all_8"] = adj[k]
    s = out[run_oil.PRIMARY_KEY]["2025-01..now"]
    fails = []
    if s["trades"] < 100:
        fails.append("fewer than 100 trades")
    if not (s.get("expectancy_r", -1) > 0 and (s.get("t_stat") or 0) >= 2):
        fails.append("expectancy not > 0 with t >= 2")
    if not s.get("benchmark", {}).get("p_random", 1) <= 0.05:
        fails.append("not better than matched random entry (p_random > 0.05)")
    if not s.get("expectancy_stress_r", -1) > 0:
        fails.append("expectancy <= 0 at stress cost")
    out["verdict"] = {"primary": run_oil.PRIMARY_KEY, "works_on_gold": not fails, "failed": fails}
    with open(os.path.join(ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s; verdict: {out['verdict']}")
    print(json.dumps(out["meta"]))


if __name__ == "__main__":
    main()
