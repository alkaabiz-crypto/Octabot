# Independent audit - DRYRUN_TEST_past_period - 2026-11-09 07:31 UTC

BINANCE PROXY (not Exness). Ledgers were not modified.

- Forward dir: `../../../tmp/claude-0/-home-user-Octabot/5b2bd987-32bf-569e-9423-8a60d237f685/scratchpad/fwtest/btc_breakout/forward` | last processed 1H close: 2026-11-09 06:00
- Trades recorded 21 vs independent 21 | signals recorded 56 vs independent 56
- Findings: {'CRITICAL': 0, 'DISCREPANCY': 1, 'MINOR': 0, 'FINDING': 1, 'WARNING': 2, 'INFO': 3}

| Severity | Check | Detail |
|---|---|---|
| INFO | frozen files | not a repository forward directory: git history checks skipped |
| DISCREPANCY | trade 1 hold_hours | recorded 99.99 vs independent 33.75 (diff 66.24) |
| INFO | entry slippage model | entries fill at the next 15m open; observed open-vs-signal-close differences over 21 trades: max /0.01/ USD. No extra queue/latency slippage is modeled beyond the cost scenarios. |
| INFO | stop gap fills | 0 of 21 independent exits filled at a gapped 15m open below the stop (modeled). |
| WARNING | cost assumptions | Round-trip costs are HYPOTHETICAL scenarios (0.02% / 0.05% / 0.10% of price) covering spread, commission and slippage together. Exness BTCUSDm spread, commission and swap could not be verified (site blocks automated access). Overnight swap is NOT modeled even though the average hold is ~20h. Binance top-of-book spread is not representative of Exness CFD spreads. |
| WARNING | intrabar assumption | Within one 15m candle the exact path is unknown; the replay assumes the stop is evaluated before the trailing update, matching the research engine. This is conservative for longs but not exact. |
| FINDING | 40-trade limit | The paper trader does NOT stop at 40 trades: it keeps recording trades after trade 40 and only labels the report COMPLETE when >= 40 trades AND date >= 2027-05-09. The 40-trade limit is not enforced in code. Evaluation should use trades 1-40 only (this audit reports that subset separately); the frozen code was not changed. |
