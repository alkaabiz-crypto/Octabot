"""Run the requested-indicator tests (PROTOCOL.md). Writes reports/results.json."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import requested as R
import run_scan
import study as S

COMMON = ["VWAP_BAND_REVERSION", "VWAP_BAND_BREAKOUT", "LORENTZIAN", "EMA_20_50_200_PULLBACK", "SESSION_VWAP_CROSS",
          "RSI14", "RSI_DIVERGENCE", "ADX14_20", "ADX14_25"]
MARKETS = {
    "USOILm": (os.path.join(R.RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"), False, COMMON + ["VP_80_RULE", "VP_BREAKOUT"]),
    "XAUUSDm": (os.path.join(R.RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz"), False, COMMON),
    "BTCUSDm": (os.path.join(R.RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz"), True, COMMON + ["SUPERTREND", "MACD"]),
}
EXITS = ("HW", "SYM", "TRAIL")


def main():
    t0 = time.time()
    out = {"meta": {"generated_utc": S.fmt(time.time()), "runs": run_scan.RUNS}}
    for mkt, (path, utc, names) in MARKETS.items():
        a = R.ReqAsset(path, utc_day_sessions=utc)
        end = a.e.t[-1] + 3600
        periods = {"selection 2025": (S.ts(2025, 1), S.ts(2026, 1)), "confirmation 2026": (S.ts(2026, 1), end)}
        out[mkt] = {}
        for ind in names:
            for d in (1, -1):
                dname = "BUY" if d > 0 else "SELL"
                sig = a.req_signals(ind, d)
                for ex in EXITS + (("NATIVE",) if ind == "LORENTZIAN" else ()):
                    key = f"{ind}|{dname}|{ex}"
                    res = {p: run_scan.evaluate(a, a.run_signals(sig, d, ex, w0, w1), d, ex, w0, w1) for p, (w0, w1) in periods.items()}
                    sel, con = res["selection 2025"], res["confirmation 2026"]
                    res["passes_selection"] = sel["trades"] >= 30 and sel.get("expectancy_r", -1) > 0 and sel.get("p_random", 1) <= 0.05
                    res["passes_confirmation"] = con["trades"] >= 20 and con.get("expectancy_r", -1) > 0 and con.get("p_random", 1) <= 0.05
                    res["reliable"] = res["passes_selection"] and res["passes_confirmation"]
                    res["win_rate_70_both"] = all(r.get("win_rate_pct", 0) >= 70 for r in (sel, con))
                    out[mkt][key] = res
                    print(f"{mkt} {key:36} sel n={sel['trades']:>4} win={sel.get('win_rate_pct', 0):5.1f} E={sel.get('expectancy_r', 0):+.3f} "
                          f"p={sel.get('p_random', 1):.3f} | conf n={con['trades']:>4} win={con.get('win_rate_pct', 0):5.1f} "
                          f"E={con.get('expectancy_r', 0):+.3f} p={con.get('p_random', 1):.3f}{'  RELIABLE' if res['reliable'] else ''}", flush=True)
    with open(os.path.join(R.ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
