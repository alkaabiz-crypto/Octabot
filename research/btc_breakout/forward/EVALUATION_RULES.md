# Evaluation rules: Donchian 20 forward paper test

These rules were written on 2026-11-09, before any forward trade existed (0 trades recorded). They define how the forward test is judged. They do **not** change the frozen strategy, `paper_trader.py` or any recorded result.

## Evaluation set

1. **The evaluation set is trades 1 to 40 of `trades.csv`, in recorded order.** Trades 41 and later are still recorded, because the paper trader does not stop at 40 (see audit finding "40-trade limit"). They are excluded from the verdict and reported separately as post-evaluation observations.
2. No verdict on profitability (positive, negative or "edge confirmed") is given before trade 40 has closed. Interim daily reports show progress and running metrics only.
3. If trade 40 closes before 2027-05-09, the verdict is still computed on trades 1 to 40. Data collection continues to the six-month mark as supplementary observation. The `COMPLETE` label in `REPORT.md`, which requires both 40 trades and the date 2027-05-09, is informational. **This file governs the verdict.**
4. If fewer than 40 trades have closed by 2027-05-09, the test continues until trade 40. No early verdict is given.

## Verdict calculation

The verdict is computed by a separate script from the unchanged ledgers, never by editing them. For trades 1 to 40 it reports:

- expectancy in R, profit factor, win rate, average win/loss R:R, maximum drawdown, longest losing streak and cumulative return;
- each of these at the 0.02%, 0.05% and 0.10% hypothetical cost scenarios, labelled BINANCE PROXY.

**Positive after realistic costs** means expectancy is above 0 at 0.05%, and also at 0.10%, with the t-statistic reported alongside. With 40 trades, a positive result is weak evidence on its own; the report must say so.

If verified Exness costs (spread, commission, swap, admin fee) become available, they are applied as an additional, separately labelled analysis on the same 40 trades.

## Integrity requirements for a valid verdict

- The independent audit (`../audit/audit.py`) reports 0 CRITICAL and 0 DISCREPANCY findings on the final ledgers. If it does not, every finding is reported, and the verdict is marked as provisional until it is resolved.
- Frozen files are unchanged since commit `ce2e8c57`, and the ledger history is append-only.
