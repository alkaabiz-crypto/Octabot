"""Run the pre-registered hourly signals (PROTOCOL.md). Writes reports/results.json."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hourly as HR

PATHS = {"USOILm": os.path.join(HR.RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"),
         "XAUUSDm": os.path.join(HR.RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz"),
         "BTCUSDm": os.path.join(HR.RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz")}


def main():
    quotes = {m: HR.Quotes(p) for m, p in PATHS.items()}
    out = {"meta": {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "runs": HR.RUNS}}
    for name, (mkt, plan_fn) in HR.SIGNALS.items():
        qt = quotes[mkt]
        end = qt.q["t"][-1] + 900
        res = {}
        for pname, w0, w1 in (("selection 2025", HR.S.ts(2025, 1), HR.S.ts(2026, 1)), ("confirmation 2026", HR.S.ts(2026, 1), end)):
            res[pname] = HR.evaluate(name, qt, plan_fn(qt, w0, w1))
            r = res[pname]
            print(f"{name:26} {pname:18} n={r['trades']:>4} win={r.get('win_rate_pct', 0):5.1f}% mean={r.get('mean_bps', 0):+6.2f}bps "
                  f"t={r.get('t_stat') or 0:+.2f} random={r.get('random_mean_bps', 0):+6.2f} p_rand={r.get('p_random', 1):.3f} "
                  f"stress={r.get('stress_mean_bps', 0):+6.2f}", flush=True)
        sel, con = res["selection 2025"], res["confirmation 2026"]
        res["reliable"] = (sel["trades"] >= 100 and sel.get("mean_bps", -1) > 0 and sel.get("p_random", 1) <= 0.05
                           and con["trades"] >= 60 and con.get("mean_bps", -1) > 0 and con.get("p_random", 1) <= 0.05)
        out[name] = res
    with open(os.path.join(HR.ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print({k: v["reliable"] for k, v in out.items() if k != "meta"})


if __name__ == "__main__":
    main()
