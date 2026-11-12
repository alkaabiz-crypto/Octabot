# Data audit (2026-11-12)

**Every price source used in this repository was checked**, internally and against independent public sources. Data from 2025-01-01 only. Scripts: `audit.py` and `forward_health.py`. Full numbers: `results/audit.json` and `results/forward_health.json`.

## Against independent sources

| Our data | Independent source | Median level difference | 95th pct of the absolute difference | Daily-return correlation | Verdict |
|---|---|---|---|---|---|
| Exness gold (XAUUSDm) | Kraken PAXG / Binance PAXG (gold tokens) | −0.09% / −0.11% | 0.68% / 0.69% | 0.990 / 0.992 | ✅ |
| Exness S&P 500 (US500m) at 16:00 New York | FRED SP500 official close | +0.09% | 0.22% | 0.997 | ✅ |
| Exness Nasdaq (USTECm) at 16:00 New York | FRED NASDAQ100 | +0.08% | 0.23% | 0.997 | ✅ |
| Binance BTC / ETH (repo files) | Coinbase and Kraken | ≈ 0.02% | ≈ 0.15% | 0.9999 | ✅ |
| Binance BTC / ETH (repo files) | Binance live API | 0.00% | 0.00% | 1.0000 | ✅ identical |
| Hyperliquid xyz:GOLD (forward tests) | Kraken PAXG | +0.14% | 0.40% | 0.996 | ✅ |
| Exness oil (USOILm) | **Hyperliquid xyz:CL**, hour by hour (Apr–Oct 2026) | −0.56% | 2.26% | **0.996** (hourly) | ✅ |
| Exness oil / Hyperliquid oil | FRED WTI **spot** (Cushing) | −1.8% / −2.3% | 7.2% / 7.5% | 0.93 / 0.72 | ⚠️ expected, not an error |

**Why oil differs from FRED:**
- FRED's WTI series is the **physical spot** price at Cushing, while both trading platforms follow the **futures** contract and roll it monthly. In 2026, spot and futures were far apart.
- FRED's own WTI and Brent differ by up to 27%.
- The two futures-based feeds, Exness and Hyperliquid, agree with each other hour by hour (correlation 0.996).
- So there is no data error, and the user's app screenshots show the same oil level as these feeds.

## Internal checks on the Exness 1-minute bars

- **No bad bars:** no duplicate or unsorted minutes, no zero or negative prices, no bars with high < low, and no negative spreads.
- **Large 1-minute moves:** these are mostly Sunday reopens and 08:30 New York data releases. Oil in 2026 had several 7–11% weekend gaps. The gaps are consistent with the hourly Hyperliquid feed and with the volatile 2026 oil market.
- **Weekday gaps longer than 3 hours:** holidays (Thanksgiving, Christmas, New Year, Easter, 1 May for the DAX), **plus one real hole.**

## Problems found and what was done

| Problem | Cause | Fix |
|---|---|---|
| **No data for 30–31 March 2026** for USOILm, DE30m, US500m and USTECm (gold is complete) | **The Exness archive itself:** the re-downloaded March 2026 files end on Sunday 29 March at 23:59. The S&P file is byte-identical to the one used. | The theory library drops any trade held across the hole, because stops and targets cannot be checked inside it. 131 combinations lost one trade each, and **no verdict changed**. Intraday studies (ORB, sessions) had no trades on those days. The 1 April prices are real, so the move across the hole is real market movement. |
| **USTECm data ends 28 October 2026** | The Exness archive's October file ends on the 28th; it is identical on re-download | The holdout simply ends 2 days earlier for Nasdaq. |
| The audit's own Coinbase download looped | A moving "now" end date | Fixed, using a fixed end date. |

## Forward paper tests (live)

All 7 are healthy. Every one is up to date (its last processed minute is under 2.5 hours old), its saved totals match its ledger exactly, and there are no duplicate rows (`results/forward_health.json`).
