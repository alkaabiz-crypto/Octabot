# Test count (G7 honesty check), 2026-11-14 10:15 UTC

Every evaluated configuration counts. Several are rough counts, documented in the script, and the total is a lower-bound order of magnitude.

| Branch | What | Tests / configurations |
|---|---|---|
| this branch | discovery batches 001–004, user theories, H4 checks (REGISTRY.md rows) | 82 |
| this branch | IND batches 001–002 (TEST tests) | 599 |
| this branch | theory event studies THE-005, THE-017, event batch 001 (TEST tests) | 50 |
| this branch | STR-023 replication, STR-025, STR-026, H4 ETH/A/B/C checks | 11 |
| this branch | earlier studies: news_markets 225, news_surprise 56, indicator scans (multi_market ~2,950 variants × 33 markets fitted picks 108; long_history ~2,640 per market × 3), TradingView/community/requested scans | 8,709 |
| other branch | theory library screen 535 + earlier runs 2 × 416 + V2 54 + V1 3 | 1,424 |
| other branch | ORB 96, zone 60, oil_dca_bot 502, signal clone 10, shortlist / session / Batch 2 (~30) | 698 |
| **Total** | | **11,573** |

- **Bonferroni threshold** for the whole family (two-sided 5%): |z| ≥ **4.60**.
- **No result in the programme reaches it.** The strongest single results are the H4 2017–19 period (p < 0.001; 1,000 random draws, so the resolution floor is 0.001) and the HAR volatility forecast (a volatility, not direction, result).
- **How to read this:** with this many tests, about 5% of truly useless ideas pass any single 5% test. That is why every result must survive a **forward test on new data** before it counts.
