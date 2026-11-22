"""Health check of every forward paper test: is each one up to date, and do its saved totals match its ledger?

Usage: python3 -I forward_health.py
"""
import csv, json, os, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); now = time.time()
age_h = lambda ms: round((now * 1000 - ms) / 3_600_000, 2)


def rows(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def main():
    out = {}
    s = json.load(open(os.path.join(ROOT, "gold_asia_forward", "state.json"))); led = rows(os.path.join(ROOT, "gold_asia_forward", "ledger.csv"))
    out["gold_asia"] = dict(cursor_age_h=age_h(s["cursor"]), trades_state=s["trades"], trades_ledger=len(led),
                            totals_match=abs(s["oz_cum_2x"] - sum(float(r["net_usd_per_oz_2x"]) for r in led)) < 0.05)
    s = json.load(open(os.path.join(ROOT, "oil_stoch_forward", "state.json"))); led = rows(os.path.join(ROOT, "oil_stoch_forward", "ledger.csv"))
    out["oil_stochastic"] = dict(cursor_age_h=age_h(s["cursor"]), trades_state=s["trades"], trades_ledger=len(led), totals_match=abs(s["pnl"] - sum(float(r["pnl_usd"]) for r in led)) < 0.05)
    for t in ("GOLD_FVG", "OIL_FIB"):
        s = json.load(open(os.path.join(ROOT, "library_forward", f"state_{t}.json"))); led = rows(os.path.join(ROOT, "library_forward", f"ledger_{t}.csv"))
        out[f"library_{t}"] = dict(cursor_age_h=age_h(s["cursor"]), trades_state=s["trades"], trades_ledger=len(led),
                                   totals_match=abs(s["net2"] - sum(float(r["net_usd_2x"]) for r in led)) < 0.05)
    s = json.load(open(os.path.join(ROOT, "gold_mom50_forward", "state.json"))); led = rows(os.path.join(ROOT, "gold_mom50_forward", "ledger.csv"))
    out["gold_mom50"] = dict(state_keys=sorted(s)[:8], ledger_rows=len(led), last_close=led[-1]["close_date"] if led else None)
    led = rows(os.path.join(ROOT, "daily_signal_dca", "forward", "ledger.csv"))
    out["trend_bot"] = dict(ledger_rows=len(led), last_close=led[-1]["close_date"] if led else None, duplicate_rows=len(led) - len({(r["close_date"], r["symbol"], r["account"]) for r in led}))
    sig = rows(os.path.join(ROOT, "btc_breakout", "forward", "signals.csv")); tr = rows(os.path.join(ROOT, "btc_breakout", "forward", "trades.csv"))
    out["donchian"] = dict(signals=len(sig), trades=len(tr), duplicate_signals=len(sig) - len({r["signal_close_utc"] for r in sig}))
    for k, v in out.items(): print(k, v)
    flags = [k for k, v in out.items() if (v.get("cursor_age_h", 0) > 2.5) or v.get("totals_match") is False or v.get("duplicate_rows", 0) or v.get("duplicate_signals", 0)
             or ("trades_state" in v and v["trades_state"] != v["trades_ledger"])]
    print("PROBLEMS:", flags or "none")
    json.dump(dict(checked_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results=out, problems=flags),
              open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "forward_health.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
