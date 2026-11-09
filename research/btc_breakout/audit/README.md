# Independent audit of the Donchian 20 forward paper test

`audit.py` independently re-checks the forward paper test, which is a BINANCE PROXY test, not Exness.

It is independent of the code it audits:

- It does not import `engine.py`, `paper_trader.py` or `daily_update.py`.
- It downloads its own Binance candles and re-implements the written strategy rules.
- It never modifies the ledgers.
- Its results are saved in `results/`.

```
python3 -I research/btc_breakout/audit/audit.py                  # audits research/btc_breakout/forward
python3 -I research/btc_breakout/audit/audit.py <dir> --label X  # audits another forward-test directory
```

Exit code: 0 means no CRITICAL findings and no DISCREPANCY findings. 1 means at least one of either.

## Checks

1. **Frozen code:** `engine.py`, `protocol.py`, `paper_trader.py` and `FROZEN.json` are unchanged since freeze commit `ce2e8c57`.
2. **Append-only history:** across every git revision, no row of `trades.csv` or `signals.csv` was removed or changed. The one allowed change is a PENDING signal being resolved.
3. **Per-trade arithmetic,** recomputed from the recorded entry, exit and stop values:
   - entry slippage, initial stop, risk in USD and position size;
   - gross R, and net R under all three cost scenarios;
   - modeled costs, P&L, the equity chain, drawdown and hold time;
   - the status totals.
4. **Timing and executions:**
   - each signal falls on a 1H close, each entry occurs at the signal close, and each exit falls on a 15m close;
   - no duplicate executions, no overlapping positions, and no trades before the forward start;
   - LONG trades only.
5. **Independent replay** from freshly downloaded candles:
   - every signal and its status, with nothing missing and nothing extra;
   - every entry, exit, R value and the open position;
   - the replay stops at the last 15m candle the paper trader actually saw.
6. **Candle integrity:**
   - the candles the paper trader recorded match Binance's data;
   - there are no gaps and no unfinished candles;
   - no recorded candle closes after the last processed 1H close.
7. **Look-ahead and repainting:**
   - every 4H filter value comes from a 4H candle closed at or before the signal;
   - each signal is recomputed from candles closed by that time only, and must come out the same.
8. **Execution realism:** reports entry slippage, stop gap fills, and the limits of the cost and intrabar assumptions.
9. **40-trade limit:** checks whether the limit is enforced in code. The pre-registered evaluation set is trades 1 to 40 only.
10. **Exactly-once processing:** the `run_log.csv` watermarks must be contiguous, must never move backwards, and the candle counts must add up.

## Validation of the audit itself (2026-11-09)

The audit was run on a dry-run copy of the paper trader covering 2026-09-01 to 2026-11-09. That period is past data and was used only to test the code, not as evidence.

- It independently reproduced all 21 trades and all 56 signals, with no differences in prices, R values or statuses.
- It caught a deliberately tampered `hold_hours` value (99.99 recorded against 33.75 recomputed).
- In a second test copy, it caught a falsified exit price (flagged by both the arithmetic check and the replay) and a falsified signal status. The results of that tamper test were deleted after the check.

## Known findings (not corrected; the frozen code is unchanged)

- **FINDING, 40-trade limit not enforced in code.** `paper_trader.py` keeps recording trades after trade 40. It labels the report COMPLETE only when there are at least 40 trades and the date is on or after 2027-05-09. Evaluation must use trades 1 to 40. The audit reports that subset.
- **FINDING, latent signal-label edge case.** A breakout whose 1H candle closes exactly at the previous trade's exit time is skipped by the engine, as intended: the engine only resumes on candles closing after the exit. However, `paper_trader.py` (line 98) checks `entry < signal_close < exit` strictly, so such a signal would be labeled `PENDING` instead of `REJECTED: position already open`. Trades and P&L are not affected. If it happens, the audit will report it as a DISCREPANCY.
- **WARNING, costs.** The 0.02%, 0.05% and 0.10% round-trip costs are hypothetical. Exness spread, commission and swap are unverified, and swap is not modeled.
- **WARNING, intrabar path.** Within each 15m candle, the stop is evaluated before the trailing update. This approximates the real path inside the candle.
