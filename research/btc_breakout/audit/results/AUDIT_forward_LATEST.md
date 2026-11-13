# Independent audit - forward - 2026-11-13 01:10 UTC

BINANCE PROXY (not Exness). Ledgers were not modified.

- Forward dir: `research/btc_breakout/forward` | last processed 1H close: 2026-11-13 01:00
- Trades recorded 0 vs independent 0 | signals recorded 1 vs independent 1
- Findings: {'CRITICAL': 0, 'DISCREPANCY': 0, 'MINOR': 0, 'FINDING': 1, 'WARNING': 2, 'INFO': 2}

| Severity | Check | Detail |
|---|---|---|
| INFO | entry slippage model | entries fill at the next 15m open; observed open-vs-signal-close differences over 0 trades: max /0.00/ USD. No extra queue/latency slippage is modeled beyond the cost scenarios. |
| INFO | stop gap fills | 0 of 0 independent exits filled at a gapped 15m open below the stop (modeled). |
| WARNING | cost assumptions | Round-trip costs are HYPOTHETICAL scenarios (0.02% / 0.05% / 0.10% of price) covering spread, commission and slippage together. Exness BTCUSDm spread, commission and swap could not be verified (site blocks automated access). Overnight swap is NOT modeled even though the average hold is ~20h. Binance top-of-book spread is not representative of Exness CFD spreads. |
| WARNING | intrabar assumption | Within one 15m candle the exact path is unknown; the replay assumes the stop is evaluated before the trailing update, matching the research engine. This is conservative for longs but not exact. |
| FINDING | 40-trade limit | The paper trader does NOT stop at 40 trades: it keeps recording trades after trade 40 and only labels the report COMPLETE when >= 40 trades AND date >= 2027-05-09. The 40-trade limit is not enforced in code. Evaluation should use trades 1-40 only (this audit reports that subset separately); the frozen code was not changed. |
