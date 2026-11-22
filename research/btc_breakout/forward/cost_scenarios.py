"""Cost-scenario performance report for the Donchian 20 forward paper test (BINANCE PROXY, paper only).

This script reads the ledger only. It never modifies trades.csv, signals.csv or any frozen file.

- Scope: forward-test trades 1-40 (the evaluation set, see EVALUATION_RULES.md). Trades 41+ are listed separately.
  The script refuses to run on any directory whose FROZEN.json is not the real forward test (for example a dry-run copy).
- Costs: no Exness cost is verified (see EXNESS_COSTS.md). The three scenarios below are HYPOTHETICAL round-trip
  costs, as % of price, covering spread, commission and slippage together:
      optimistic 0.02% | moderate 0.05% | pessimistic 0.10%
  UNKNOWN and NOT MODELLED in any scenario: Exness overnight swap (including triple swap on Fridays), any overnight
  admin fee on swap-free accounts, and the actual Exness spread and commission for the user's account.
- Verdict: none. No profitability verdict is produced before trade 40 has closed and the independent audit passes.
"""
import csv, json, math, os, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REAL_FORWARD_START = "2026-11-09 07:00"
REAL_FORWARD_START_TS = 1794207600  # 2026-11-09 07:00 UTC
SCENARIOS = [("optimistic", "R_net_low", "0.02% round trip"), ("moderate", "R_net_mid", "0.05% round trip"),
             ("pessimistic", "R_net_high", "0.10% round trip")]
RISK, EVAL_N = 0.005, 40


def metrics(rs, start_equity):
    if not rs:
        return dict(trades=0)
    eq = peak = start_equity; mdd = 0.0; streak = worst = 0
    for r in rs:
        eq *= 1 + RISK * r; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
        streak = streak + 1 if r <= 0 else 0; worst = max(worst, streak)
    w = [r for r in rs if r > 0]; l = [r for r in rs if r <= 0]
    m = statistics.mean(rs); sd = statistics.stdev(rs) if len(rs) > 1 else 0
    return dict(trades=len(rs), expectancy_R=round(m, 4), t_stat=round(m / (sd / math.sqrt(len(rs))), 2) if sd else None,
                profit_factor=round(sum(w) / -sum(l), 3) if l and sum(l) < 0 else None,
                win_rate_pct=round(len(w) / len(rs) * 100, 1),
                avg_win_loss_rr=round(statistics.mean(w) / -statistics.mean(l), 2) if w and l and statistics.mean(l) < 0 else None,
                cumulative_return_pct=round((eq / start_equity - 1) * 100, 2), max_drawdown_pct=round(mdd * 100, 2),
                max_losing_streak=worst)


def main():
    frozen = json.load(open(os.path.join(HERE, "FROZEN.json")))
    cfg = frozen["config"]
    if (cfg["forward_start_utc"] != REAL_FORWARD_START or cfg["forward_start"] != REAL_FORWARD_START_TS
            or cfg["venue"] != "BINANCE_PROXY"):
        raise SystemExit("REFUSED: this is not the real forward-test directory (dry-run or modified copy)")
    start_eq = frozen["config"]["start_equity_usd"]
    p = os.path.join(HERE, "trades.csv")
    trades = list(csv.DictReader(open(p))) if os.path.exists(p) else []
    ev, post = trades[:EVAL_N], trades[EVAL_N:]
    res = {name: metrics([float(t[col]) for t in ev], start_eq) for name, col, _ in SCENARIOS}
    gross = metrics([float(t["R_gross"]) for t in ev], start_eq)
    now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    out = dict(generated_utc=now, venue="BINANCE_PROXY (not Exness)", evaluation_set=f"forward trades 1-{EVAL_N}",
               evaluation_trades_completed=len(ev), post_evaluation_trades=len(post), verdict="NONE - fewer than 40 trades" if len(ev) < EVAL_N
               else "NOT AUTOMATIC - requires independent audit (0 CRITICAL / 0 DISCREPANCY) before any verdict",
               cost_status="NO EXNESS COST VERIFIED; all scenarios are HYPOTHETICAL",
               not_modelled=["Exness overnight swap (incl. Friday triple swap)", "overnight admin fee on swap-free accounts",
                             "actual Exness spread/commission for the account"],
               gross_zero_cost=gross, scenarios={n: dict(assumption=f"HYPOTHETICAL {d}", **res[n]) for n, _, d in SCENARIOS})
    json.dump(out, open(os.path.join(HERE, "cost_scenarios.json"), "w"), indent=1)
    rows = [("gross (no costs)", "-", gross)] + [(f"{n} - HYPOTHETICAL", d, res[n]) for n, _, d in SCENARIOS]
    md = [f"# Cost scenarios - forward test trades 1-{EVAL_N} (BINANCE PROXY, not Exness)", "",
          f"Generated {now} UTC. Evaluation trades completed: **{len(ev)} / {EVAL_N}**. Post-evaluation trades (excluded): {len(post)}.", "",
          f"**Verdict: {out['verdict']}.**", "",
          "**Cost status:** no Exness cost is verified (see EXNESS_COSTS.md). Every scenario is a HYPOTHETICAL round-trip cost "
          "covering spread, commission and slippage. **Not modelled in any scenario (unknown):** overnight swap (incl. Friday triple swap), "
          "overnight admin fee on swap-free accounts, actual Exness spread/commission.", "",
          "| Scenario | Round-trip cost | Trades | Expectancy R | t | PF | Win % | Avg win/loss | Cum. return % | Max DD % | Max losing streak |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, d, m in rows:
        md.append(f"| {name} | {d} | {m.get('trades', 0)} | {m.get('expectancy_R')} | {m.get('t_stat')} | {m.get('profit_factor')} | "
                  f"{m.get('win_rate_pct')} | {m.get('avg_win_loss_rr')} | {m.get('cumulative_return_pct')} | {m.get('max_drawdown_pct')} | {m.get('max_losing_streak')} |")
    md += ["", "Dry-run and historical research results are deliberately excluded from this file."]
    open(os.path.join(HERE, "COST_SCENARIOS.md"), "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
