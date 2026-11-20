# STR-025 results: volatility-scaled sizing (IND-018) on STR-023 trades. **MIXED (2 of 4)**

Pre-registered in `PREREG.md` (commit `e5733d68`). Output `results.json`; script `run_str025.py`. Sized R is normalised to the same average exposure as unsized.

| Market / half | Trades | Mean R: unsized → sized | Mean/sd | Max drawdown (R) | Worst 20 trades (R) | Pass |
|---|---|---|---|---|---|---|
| BTC 2020-01 → 2023-06 | 597 | +0.146 → +0.178 | 0.072 → 0.081 | 24.6 → **25.4** | −14.1 → −14.2 | no |
| BTC 2023-07 → 2026-11 | 610 | +0.188 → +0.213 | 0.076 → 0.078 | 23.7 → **22.6** | −13.3 → −14.0 | yes |
| ETH 2020-01 → 2023-06 | 605 | +0.219 → +0.224 | 0.113 → 0.110 | 19.6 → **22.3** | −11.3 → −14.1 | no |
| ETH 2023-07 → 2026-11 | 598 | +0.120 → +0.146 | 0.054 → 0.058 | 35.2 → **32.3** | −14.4 → −16.5 | yes |

**Reading.**
- Sizing by the volatility forecast raised the average R slightly in all four samples, but did **not** reliably reduce drawdowns: lower in the two recent halves, higher in the two earlier ones.
- The likely reason: STR-023 already sizes by volatility. Its 1R is 2 × the current ATR, so a second volatility adjustment adds little.
- **Status:** MIXED. As pre-registered, it will be reported as a read-only shadow on STR-023's forward ledger once trades exist. Nothing changes in the forward test.
