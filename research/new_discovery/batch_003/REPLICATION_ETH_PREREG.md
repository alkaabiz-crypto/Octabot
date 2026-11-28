# Batch 003 H4 replication on ETH: pre-registration (2026-11-13, before any ETH data was downloaded or computed)

**Purpose.** An independent replication of the H4 Coinbase-premium result (WATCH in `RESULTS.md`), on a market the rule was not developed on. This is **one test**. Every rule and parameter is identical to `PREREG.md` H4; only the asset changes.

**Rule.**
- *prem* = ln(Coinbase ETH-USD hourly close / Binance ETHUSDT hourly close), for candles of the same start time.
- *z* is computed against the previous 720 hours, excluding the current one.
- *z* ≥ 2 → long ETH for 24 h; *z* ≤ −2 → short. One position at a time.
- Execution on Exness ETHUSDm 15-minute bid/ask: entry at the first open at or after the hourly close; exit at the first open at or after entry + 24 h.
- Costs as the protocol: primary 0.5× median spread; stress 1.5× plus 0.02% per day.

**Data.** Exness ETHUSDm runs from 2023-01 only, so there is no EARLY period. The periods are TRAIN, VALIDATION and TEST, as in the protocol.

**Benchmark.** 1,000 random sets with the same count, sides and 24-hour hold. One-sided p.

**Decision.** A single test, so no multiple-testing correction within it.

| Label | Conditions |
|---|---|
| **REPLICATED** | mean > 0 in TRAIN, VALIDATION and TEST; TEST stress mean > 0; TEST p ≤ 0.05; ≥ 30 TEST trades |
| **PARTIAL** | positive in all three periods, but TEST p > 0.05 |
| **NOT REPLICATED** | otherwise |

**Effect on H4.** H4's own decision stays WATCH whatever happens here. Its forward paper test (`../forward_h4/`) is unaffected.
