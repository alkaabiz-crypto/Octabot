"""Run the original-script round (PROTOCOL.md). Writes reports/results.json."""
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ports as P
import run_scan
import study as S

MARKETS = {"USOILm": (os.path.join(P.RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"), False),
           "XAUUSDm": (os.path.join(P.RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz"), False),
           "BTCUSDm": (os.path.join(P.RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz"), True)}
FLIP_SCRIPTS = {"UT_BOT", "SSL_CHANNEL", "CHANDELIER_EXIT", "HALFTREND", "SUPERTREND_KIVANC", "RANGE_FILTER", "CORAL_TREND", "QQE_MOD"}
STANDARD = ("HW", "SYM", "TRAIL")


def eval_held(a, trades, w0, w1):
    rs = [t.r("primary") for t in trades]
    s = S.summary(rs)
    if s["trades"] < 2:
        return s
    s["expectancy_stress_r"] = statistics.mean(t.r("stress") for t in trades)
    s["avg_hold_hours"] = statistics.mean(t.hold_hours for t in trades)
    s.update(a.duration_benchmark(trades, w0, w1))
    return s


def verdict(res):
    sel, con = res["selection 2025"], res["confirmation 2026"]
    res["passes_selection"] = sel["trades"] >= 30 and sel.get("expectancy_r", -1) > 0 and sel.get("p_random", 1) <= 0.05
    res["passes_confirmation"] = con["trades"] >= 20 and con.get("expectancy_r", -1) > 0 and con.get("p_random", 1) <= 0.05
    res["reliable"] = res["passes_selection"] and res["passes_confirmation"]
    res["win_rate_70_both"] = all(r.get("win_rate_pct", 0) >= 70 for r in (sel, con))
    return res


def main():
    t0 = time.time()
    out = {"meta": {"generated_utc": S.fmt(time.time()), "runs": 1000}}
    for mkt, (path, crypto) in MARKETS.items():
        a = P.OriginalAsset(path, crypto=crypto)
        end = a.e.t[-1] + 3600
        periods = {"selection 2025": (S.ts(2025, 1), S.ts(2026, 1)), "confirmation 2026": (S.ts(2026, 1), end)}
        out[mkt] = {}
        for name, (buy, sell) in a.sig.items():
            for d, sig in ((1, buy), (-1, sell)):
                dname = "BUY" if d > 0 else "SELL"
                exits = list(STANDARD) + (["FLIP"] if name in FLIP_SCRIPTS else []) + (["NATIVE"] if name == "LORENTZIAN_V6" else [])
                for ex in exits:
                    key = f"{name}|{dname}|{ex}"
                    res = {}
                    for p, (w0, w1) in periods.items():
                        if ex in STANDARD:
                            res[p] = run_scan.evaluate(a, a.run_signals(sig, d, ex, w0, w1), d, ex, w0, w1)
                        elif ex == "FLIP":
                            res[p] = eval_held(a, a.flip_trades(name, d, w0, w1), w0, w1)
                        else:
                            res[p] = eval_held(a, a.run_signals(sig, d, "NATIVE", w0, w1), w0, w1)
                    out[mkt][key] = verdict(res)
                    sel, con = res["selection 2025"], res["confirmation 2026"]
                    print(f"{mkt} {key:40} sel n={sel['trades']:>4} win={sel.get('win_rate_pct', 0):5.1f} E={sel.get('expectancy_r', 0):+.3f} "
                          f"p={sel.get('p_random', 1):.3f} | conf n={con['trades']:>4} win={con.get('win_rate_pct', 0):5.1f} "
                          f"E={con.get('expectancy_r', 0):+.3f} p={con.get('p_random', 1):.3f}{'  RELIABLE' if res['reliable'] else ''}", flush=True)
    with open(os.path.join(P.ROOT, "reports", "results.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
