"""Trade-level analysis of the reproduced one-year Exness tick-replay ledger (spread paid via ask-in/bid-out; exit slippage
from ticks; commission 0 = Standard advertised, unverified; swaps unknown -> not deducted)."""
import csv, json, statistics, sys
L = list(csv.DictReader(open(sys.argv[1]))); R = [float(t["R_net"]) for t in L]; n = len(R); tot = sum(R)
i_top = max(range(n), key=lambda k: R[k]); top = L[i_top]
w = [r for r in R if r > 0]; l = [r for r in R if r <= 0]
eq = peak = 1.0; mdd = 0.0
for r in R: eq *= 1 + 0.005 * r; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
rest = R[:i_top] + R[i_top + 1:]; wr = [r for r in rest if r > 0]; lr = [r for r in rest if r <= 0]
out = dict(trades=n, total_R=round(tot, 4), expectancy_R=round(tot / n, 4),
           top_trade=dict(rank_by_R=1, trade_number=i_top + 1, signal_close=top["signal_close"], entry_time=top["entry_time"], entry_ask=float(top["entry_ask"]),
                          spread_at_entry=float(top["spread_entry"]), initial_stop=round(float(top["initial_stop"]), 2), final_stop=round(float(top["final_stop"]), 2),
                          exit_time=top["exit_time"], exit_bid=float(top["exit_bid"]), hold_hours=round(float(top["hold_h"]), 2), risk_per_btc=round(float(top["risk"]), 2),
                          R=round(R[i_top], 4), share_of_total_R_pct=round(R[i_top] / tot * 100, 1), swap_days_assumed=int(top["swap_days"])),
           reconciliation=dict(formula_all=f"{round(tot, 4)} / {n} = {round(tot / n, 4)}",
                               formula_without_top=f"({round(tot, 4)} - {round(R[i_top], 4)}) / {n - 1} = {round((tot - R[i_top]) / (n - 1), 4)}"),
           after_spread_and_slippage=dict(win_rate_pct=round(len(w) / n * 100, 1), profit_factor=round(sum(w) / -sum(l), 3), avg_win_R=round(statistics.mean(w), 4),
                                          avg_loss_R=round(statistics.mean(l), 4), avg_win_loss_ratio=round(statistics.mean(w) / -statistics.mean(l), 3),
                                          median_R=round(statistics.median(R), 4), max_drawdown_pct_at_0_5pct_risk=round(mdd * 100, 2), wins=len(w), losses=len(l)),
           without_top_trade=dict(trades=n - 1, expectancy_R=round(statistics.mean(rest), 4), profit_factor=round(sum(wr) / -sum(lr), 3), win_rate_pct=round(len(wr) / (n - 1) * 100, 1)),
           cost_status="spread and exit slippage MEASURED from Exness ticks (spread is a fixed per-period value in this archive); commission assumed 0 (UNVERIFIED); swaps UNKNOWN, not deducted")
json.dump(out, open(sys.argv[2], "w"), indent=1); print(json.dumps(out, indent=1))
