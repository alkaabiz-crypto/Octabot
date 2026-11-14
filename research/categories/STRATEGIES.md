# Category protocol: Strategies (STR)

**Definition.** A complete, executable rule: entry, exit, stop, sizing and execution assumptions.

**Question.** Does it make money after realistic costs, on data it was not designed on?

## Test, in stages; each must pass before the next

1. **Pre-registration.** The rules are written and committed before any result.
2. **Causal backtest.**
   - Limit and stop orders go through the shared engine `new_discovery/src/causal_orders.py`, whose gate tests must pass.
   - Execution at bid/ask, plus 0.5× median spread (primary) and 1.5× plus 0.02% per day (stress).
   - Periods TRAIN / VALIDATION / TEST, plus any untouched older period.
   - Random-entry benchmark with the same count, sides and holding time. Benjamini–Hochberg across the batch.
   - **Pass** → SCREEN-PASS (TEST is reused data).
3. **Forward paper test** on new data, judged by rule V2 (`new_discovery/promotion_rule_v2/`):
   - Newey–West t ≥ the critical value, and mean ≥ +2 bp, at 100 / 300 / 600 / 1,000 trades;
   - a futility stop is allowed.
4. **Venue check.** Re-cost with the real venue's fees, funding and swap.
5. **VALIDATED** only after stages 3 and 4. Even then, real money is a separate decision outside this plan.

**Verdicts:** VALIDATED / WATCH (positive but not yet proven) / RUNNING / REJECTED.
