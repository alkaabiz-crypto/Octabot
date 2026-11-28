# Indicator information test, batch IND-001: pre-registration (2026-11-13, before any computation)

The method is in `../../categories/INDICATORS.md`. Candidates come from `../../CANDIDATES.md`.

## Data

Exness 15-minute bid/ask candles, built into 1-hour mid candles (archived privately, `research_data_2026-11-13/`).

| Market | Periods |
|---|---|
| Gold (XAUUSDm) | EARLY 2020–2022, then TRAIN / VALIDATION / TEST |
| Oil (USOILm) | EARLY 2019–2022, then TRAIN / VALIDATION / TEST |
| BTC (BTCUSDm) | EARLY 2020–2022, then TRAIN / VALIDATION / TEST |
| S&P 500 (US500m) | 2023 → |
| EUR/USD (EURUSDm) | 2023 → |

- TRAIN 2023-01 → 2024-06; VALIDATION 2024-07 → 2025-06; TEST 2025-07 → 2026-11-09.
- IND-001 uses Coinbase and Binance hourly data (BTC only, 2020 →).

## Indicator values

Each is computed at a 1-hour candle close and oriented so that **higher = the usual bullish reading**.

| ID | Value *x* | Settings |
|---|---|---|
| IND-001 | Coinbase premium z | 720 h, as batch 003 H4 |
| IND-003 | KST − its signal line | 10/15/20/30, 10/10/10/15, signal 9 |
| IND-004 | (close − UTC-day VWAP of the mid) / ATR14 | VWAP is time-weighted: no volume in CFDs |
| IND-005 | RSI14 − 50 | |
| IND-006 | MACD histogram / close | 12, 26, 9 |
| IND-007 | ln(EMA9 / EMA21) | |
| IND-008 | Supertrend direction (±1) | 10, 3 |
| IND-009 | Parabolic SAR side (±1) | 0.02, 0.2 |
| IND-010 | ADX14 × sign(+DI − −DI) | |
| IND-011 | Donchian position: (close − low20) / (high20 − low20) − 0.5 | |
| IND-012 | (close − cloud midpoint) / ATR14 | Ichimoku 9, 26, 52 |
| IND-013 | Bollinger %B − 0.5 | 20, 2 |
| IND-014 | Stochastic %K − 50 | 14, 3 |
| IND-015 | CCI20 | |
| IND-016 | Williams %R14 + 50 | |
| IND-017 | −(Williams Vix Fix) | 22-bar; higher fear = bullish under its usual reading, so the sign is flipped to make higher = bullish |
| IND-018 | HAR realised-variance forecast (daily, as batch 002 E006) | **volatility target:** next-day realised variance |
| IND-020 | ln(close / close 20 bars ago) | |

**Not in this batch:**
- IND-002 (futures-curve slope): monthly data, covered by THE-009.
- IND-019 (HMM probability): needs a monthly refit; deferred.
- IND-021 (the group of ~2,950 variants): reported by the earlier scans; deferred.

## Statistics

**Targets.** The forward log return of the mid from the next candle's open, over *h* = 1, 4, 24 and 120 hourly candles. Samples are taken every *h* candles, so they do not overlap. IND-018 uses the next day's realised variance.

**Statistic.** Spearman IC per (indicator, market, horizon, period). One-sided p in the direction of the indicator's usual reading.

**Baseline.**
- The partial IC controlling for the last *h*-candle return: the rank residual of *x* regressed on that past return.
- If the IC is significant but the partial IC is not, the result is **REDUNDANT**.

**Count.** 16 direction indicators × 5 markets × 4 horizons = 320 TEST tests, plus IND-001 (BTC, 4 horizons) and IND-018 (5 markets): **329 tests**. Benjamini–Hochberg at 5% on the TEST p.

**Verdict per indicator** (across markets and horizons; the best horizon is reported, and every horizon counts in BH):

| Verdict | Conditions |
|---|---|
| **INFORMATIVE** | For some horizon: same IC sign in every available period, in ≥ 3 markets (≥ 2 periods for IND-001); TEST BH-significant in at least one market; partial IC also significant |
| **WEAK** | Same sign everywhere, but no BH-significant TEST |
| **REDUNDANT** | Significant IC, but the partial IC is not |
| **NONE** | Otherwise |

**No costs:** this is an information test, not a trading test.
