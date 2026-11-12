# Experimental protocol (every experiment)

1. **Hypothesis and mechanism.** Why the edge might exist and who is on the other side, with supporting evidence or references.
2. **Mechanical rules.** Exact entry, exit, risk and parameters, recorded in the batch `PREREG.md` and **committed before any result is computed**. One setting per idea in the first test; no parameter search.
3. **Data checks.** Availability, gaps and instrument specifics (for example oil roll jumps), checked and reported.
4. **No look-ahead.** Signals use only data up to the bar close. Execution is at the next 15-minute candle's open, at the ask for a buy and the bid for a sell. No repainting indicators. Machine-learning models are trained only on data before the prediction period (walk-forward).
5. **Costs.**
   - Primary: real bid/ask plus slippage of 0.5 × the market's median spread per round trip.
   - Stress: 1.5 × median spread, plus 0.02% of notional per day held.
6. **Periods.** These are fixed for the whole program until changed by a dated amendment. Each trade belongs to the period of its entry.
   - TRAIN: 2023-01-01 to 2024-06-30.
   - VALIDATION: 2024-07-01 to 2025-06-30.
   - TEST: 2025-07-01 to the latest candle. TEST is reported, but no decision or parameter may be changed after seeing it.
7. **Benchmarks.** Each experiment states a random benchmark that keeps its exposure but removes its information (random entries with the same holding times, or random signs on the same trades), plus a simple benchmark (buy and hold, or equal weight).
8. **Multiple testing.** Benjamini–Hochberg at 5% over all TEST-period p-values of the batch.
9. **Report.** Trades, mean net return (bp of notional and R where defined), win rate, profit factor, max drawdown, a 95% CI of the mean, Sharpe for portfolios, p against the benchmark, and results by period and by market regime where relevant.
10. **Decisions.**
    - **CANDIDATE:** mean net > 0 at primary cost in all three periods, mean > 0 at stress cost in TEST, TEST p ≤ 0.05 against the random benchmark, survives the batch BH, and at least 30 TEST trades (or 52 TEST rebalances for portfolios).
    - **WATCH:** positive in all three periods but not significant.
    - **REJECT:** otherwise.
    - A CANDIDATE then needs a separate robustness batch (neighbouring parameters, other markets, cost doubling, sub-periods) before any paper test.
11. **Registry.** Every experiment and variant is recorded, including failures, in `REGISTRY.csv`.
