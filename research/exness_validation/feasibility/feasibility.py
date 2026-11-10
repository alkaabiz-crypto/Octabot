"""Position-sizing feasibility for the frozen Donchian 20 strategy on Exness BTCUSDm (arithmetic on the committed
one-year tick-replay ledger; no new backtest). The MT5 symbol specification is NOT available, so contract size,
minimum volume, volume step, maximum volume, leverage and account currency are UNVERIFIED ASSUMPTIONS, shown as
scenarios. Starting equity: 10,000 AED = 2,722.94 USD paper (the user's demo balance is unknown)."""
import csv, json, math, os, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
L = list(csv.DictReader(open(os.path.join(HERE, "..", "one_year", "trades", "tick_replay_trades.csv"))))
EQ0, RISK = 10000 / 3.6725, 0.005
SCEN = {"A: 1 BTC/lot, min 0.01, step 0.01 (unverified secondary sources)": (1.0, 0.01, 0.01),
        "B: 1 BTC/lot, min 0.1, step 0.1 (stress)": (1.0, 0.1, 0.1)}
eq = EQ0; rows = []
for t in L:
    entry, risk_btc, R = float(t["entry_ask"]), float(t["risk"]), float(t["R_net"])
    risk_usd = eq * RISK; vol_btc = risk_usd / risk_btc; notional = vol_btc * entry
    rows.append(dict(entry=t["entry_time"], equity=eq, risk_usd=risk_usd, risk_per_btc=risk_btc, required_btc=vol_btc,
                     notional_usd=notional, notional_x_equity=notional / eq, R=R, entry_px=entry))
    eq *= 1 + RISK * R
out = {"required_volume_btc": dict(min=round(min(r["required_btc"] for r in rows), 5), median=round(statistics.median(r["required_btc"] for r in rows), 5),
                                   max=round(max(r["required_btc"] for r in rows), 5)),
       "notional_as_multiple_of_equity": dict(min=round(min(r["notional_x_equity"] for r in rows), 3), median=round(statistics.median(r["notional_x_equity"] for r in rows), 3),
                                              max=round(max(r["notional_x_equity"] for r in rows), 3)),
       "note": "notional < 1 x equity means the position fits even at 1:1 leverage (no borrowing); actual margin depends on the UNVERIFIED leverage",
       "scenarios": {}}
for name, (cs, vmin, step) in SCEN.items():
    dev, infeasible, res = [], 0, []
    for r in rows:
        lots = math.floor(r["required_btc"] / cs / step + 1e-9) * step
        if lots < vmin: infeasible += 1; res.append(None); continue
        actual_risk = lots * cs * r["risk_per_btc"]; dev.append(actual_risk / r["risk_usd"] - 1); res.append(actual_risk)
    out["scenarios"][name] = dict(trades_feasible=len(rows) - infeasible, trades_below_min_volume=infeasible,
                                  risk_deviation_pct=dict(min=round(min(dev) * 100, 1), median=round(statistics.median(dev) * 100, 1), max=round(max(dev) * 100, 1)) if dev else None)
a = next(r for r in rows if r["R"] > 20)
cs, vmin, step = SCEN["A: 1 BTC/lot, min 0.01, step 0.01 (unverified secondary sources)"]
lots = math.floor(a["required_btc"] / step + 1e-9) * step
out["aug19_trade"] = dict(entry_utc=a["entry"], equity_before=round(a["equity"], 2), theoretical_risk_usd=round(a["risk_usd"], 2), entry_ask=a["entry_px"],
                          risk_per_btc=round(a["risk_per_btc"], 2), required_btc=round(a["required_btc"], 5), notional_usd=round(a["notional_usd"], 2),
                          notional_x_equity=round(a["notional_x_equity"], 3), R=round(a["R"], 3),
                          scenario_A_lots=round(lots, 2), scenario_A_actual_risk_usd=round(lots * a["risk_per_btc"], 2),
                          scenario_A_pnl_usd=round(lots * a["risk_per_btc"] * a["R"], 2), theoretical_pnl_usd=round(a["risk_usd"] * a["R"], 2),
                          scenario_B_lots=0.0 if a["required_btc"] < 0.1 else math.floor(a["required_btc"] * 10) / 10)
json.dump(out, open(os.path.join(HERE, "feasibility_results.json"), "w"), indent=1); print(json.dumps(out, indent=1))
