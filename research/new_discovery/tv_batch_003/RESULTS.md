---
title: TradingView batch 003 results
description: 13 more TradingView indicators and 10 popular double/triple combinations on gold, oil, BTC, S&P 500 and EUR/USD
sidebar_position: 2
---

# TradingView batch 003 results (2026-11-15)

Rules: [`PREREG.md`](PREREG.md) (commit 2de01b2a, before any computation). Script: `run_tv3.py`; numbers: `results.json`. Exness prices, 1h candles, costs 1.5× (stress 3×) the median spread. Periods: EARLY (to 2022), TRAIN 2023-01→2024-06, VALIDATION 2024-07→2025-06, TEST 2025-07→now.

## Bottom line

- **Indicators: all 13 are NONE.** None predicts returns consistently in 3 or more markets. Several trend-type ones (SSL, UT Bot, Chandelier, QQE, WaveTrend) are consistently *slightly negative* at 1–4 hours on gold and BTC — the same short-term reversal seen in batches 001–002.
- **Combinations: 0 of 50 pass.** 49 are REJECTED, and 1 is WATCH (EMA 50/200 + MACD on the S&P 500: positive in all three periods, but only 45 TEST trades, TEST p = 0.32 vs random).
- **No forward test** is started.

## Combinations: TEST-period mean R per trade (after primary costs), with p vs random entries

| Combination | Gold | Oil | BTC | S&P 500 | EUR/USD |
|---|---|---|---|---|---|
| a. EMA 9/21 + RSI + MACD | +0.02 (0.38) | −0.13 | −0.21 | −0.07 | −0.08 |
| b. VWAP + EMA 9 + RSI | +0.04 (0.34) | −0.11 | −0.12 | −0.02 | −0.14 |
| c. MACD + Bollinger | +0.06 (0.27) | −0.19 | −0.05 | −0.04 | −0.11 |
| d. Squeeze Momentum + EMA 200 | −0.03 | −0.21 | −0.04 | −0.00 | −0.36 |
| e. SSL + WaveTrend | +0.14 (0.13) | −0.33 | −0.08 | +0.01 | +0.02 (0.05) |
| f. UT Bot + EMA 200 | +0.09 (0.16) | −0.16 | −0.06 | −0.12 | −0.17 |
| g. Supertrend + RSI + EMA 200 | +0.07 (0.27) | +0.06 (0.08) | −0.20 | −0.02 | −0.29 |
| h. MACD + RSI + Stochastic | +0.05 (0.23) | −0.04 | −0.11 | −0.04 | −0.11 |
| i. Bollinger + RSI reversion | −0.17 | −0.22 | −0.06 | −0.02 | +0.17 (0.01) |
| j. EMA 50/200 + MACD | −0.00 | +0.12 (0.13) | −0.14 | +0.05 (0.32) | −0.14 |

Each cell has 45–490 TEST trades. Stop 1.5 ATR, target 2R, 48-hour time exit for every combination.

**What stands out, and why it still fails:**
- **Gold:** 7 of 10 combinations are positive in TEST. But none is positive in all four periods, and none beats random entries (best p = 0.13). Gold rose strongly in 2025–26, so long-side trend signals look good in TEST, and random longs did nearly as well.
- **EUR/USD Bollinger + RSI reversion:** TEST +0.17R, p = 0.01, but it lost in TRAIN and VALIDATION, and p = 0.01 is not significant after correcting for 50 tests.
- **Oil and BTC:** almost everything loses after costs.

## Indicators (IND-036 to IND-048)

| ID | Indicator | Verdict |
|---|---|---|
| IND-036 | Squeeze Momentum [LazyBear] | NONE (slightly negative on BTC 1–24 h) |
| IND-037 | WaveTrend [LazyBear] | NONE |
| IND-038 | QQE Mod | NONE |
| IND-039 | SSL channel | NONE (negative on gold and BTC, short horizons) |
| IND-040 | UT Bot alerts | NONE |
| IND-041 | Chandelier exit | NONE |
| IND-042 | Schaff Trend Cycle | NONE |
| IND-043 | Coppock curve | NONE |
| IND-044 | Detrended price oscillator | NONE (positive in every period on gold and EUR/USD at 1 h, not significant) |
| IND-045 | Least-squares MA slope | NONE |
| IND-046 | Connors RSI | NONE |
| IND-047 | Laguerre RSI | NONE |
| IND-048 | Choppiness-filtered momentum | NONE |

## Checks

- **No look-ahead:** prefix-invariance passed. Every indicator and combination signal computed on the first half of gold's history is identical to the same bars computed on the full history.
- **Count:** 50 combination tests and the IC tests in `results.json` are added to the G7 test count.
