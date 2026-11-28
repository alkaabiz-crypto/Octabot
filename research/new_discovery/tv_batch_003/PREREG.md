---
title: TradingView batch 003 pre-registration
description: 13 more TradingView indicators (IND test) and 10 popular double/triple combinations (STR screen), rules fixed before computation
sidebar_position: 1
---

# TradingView batch 003: pre-registration (2026-11-15, written before any computation)

Requested by the user: "search the internet for best indicators for each market and if there is a double or triple indicator to use at one time, test it". Sources searched on 2026-11-15: TradingView community script pages (Squeeze Momentum [LazyBear] is the most-liked script), guide articles on the best gold, Bitcoin and crude-oil indicators, the LuxAlgo crude-oil MACD/RSI/Stoch script, and a Mudrex crude-oil VWAP + EMA 9 + RSI guide. None reported an independent, after-cost test.

**Data and periods.** Exness 15m bid/ask (mid prices) built into 1h candles: XAUUSDm, USOILm, BTCUSDm, US500m, EURUSDm, the same five markets as IND batches 001–002. Periods are EARLY / TRAIN / VALIDATION / TEST, as before.

## Part A: indicators (IND test, `categories/INDICATORS.md`, unchanged machinery from IND batch 001)

| ID | Indicator | Value tested |
|---|---|---|
| IND-036 | Squeeze Momentum [LazyBear] (20, BB 2.0, KC 1.5) | momentum value (linreg of close − midline), ÷ ATR |
| IND-037 | WaveTrend [LazyBear] (10, 21) | wt1 − wt2 |
| IND-038 | QQE Mod (RSI 6, smoothing 5, factor 4.236) | smoothed RSI − QQE trailing line |
| IND-039 | SSL channel (10) | direction state (+1 / −1) |
| IND-040 | UT Bot alerts (key 1, ATR 10) | sign of close − ATR trailing stop |
| IND-041 | Chandelier exit (22, 3) | direction state |
| IND-042 | Schaff Trend Cycle (10, 23, 50) | STC − 50 |
| IND-043 | Coppock curve (WMA 10 of ROC 14 + ROC 11) | value |
| IND-044 | Detrended price oscillator (20) | value ÷ ATR |
| IND-045 | Least-squares MA (50) slope | log slope |
| IND-046 | Connors RSI (3, 2, 100) | value − 50 |
| IND-047 | Laguerre RSI (gamma 0.5) | value − 0.5 |
| IND-048 | Chop-filtered momentum: ROC 12 × (Choppiness 14 < 38.2) | value |

IC at horizons 1/4/24/120 hours from the next open; partial IC on the past return; BH over every TEST test in the batch; verdicts INFORMATIVE / WEAK / REDUNDANT / NONE exactly as IND batch 002.

## Part B: combinations (STR-028a to STR-028j, STR screen)

Each combination gives a LONG trigger; SHORT is the mirror. A signal is known at a 1h close; entry at the next 1h open.

| ID | Combination (source) | LONG trigger at a 1h close |
|---|---|---|
| STR-028a | EMA 9/21 cross + RSI 14 + MACD (RSI+MA+MACD "confidence score" idea) | EMA 9 crosses above EMA 21, RSI > 50, MACD histogram > 0 |
| STR-028b | VWAP + EMA 9 + RSI 14 (crude-oil intraday guide) | close crosses above EMA 9, close > session VWAP (00:00 UTC), RSI > 50 |
| STR-028c | MACD + Bollinger (WTI community idea) | MACD (12,26,9) crosses above signal, close > BB(20) middle |
| STR-028d | Squeeze Momentum + EMA 200 | first bar the squeeze is off (BB outside KC) after ≥ 1 bar on, momentum > 0, close > EMA 200 |
| STR-028e | SSL + WaveTrend (community strategy) | wt1 crosses above wt2 with wt1 < 0, SSL direction up |
| STR-028f | UT Bot + EMA 200 | close crosses above the UT Bot trailing stop, close > EMA 200 |
| STR-028g | Supertrend (10,3) + RSI 14 + EMA 200 | Supertrend flips up, RSI > 50, close > EMA 200 |
| STR-028h | MACD + RSI + Stochastic (LuxAlgo crude-oil script) | Stoch (14,3,3) %K crosses above %D, MACD histogram > 0, RSI > 50 |
| STR-028i | Bollinger + RSI reversion | close < lower BB(20, 2) and RSI 14 < 30 (first bar both true) |
| STR-028j | EMA 50/200 + MACD (BTC trend guide) | EMA 50 crosses above EMA 200, MACD line > 0 |

**Common management (fixed for every combination, not tuned):** stop 1.5 × ATR14 (at the signal close), target 3 × ATR14 (2R), time exit after 48 hours. Managed on 1h candles: stop checked before the target in the same candle; a gap through the stop fills at the open. One position per combination and market; signals while in a trade are ignored.

**Costs:** primary 1.5 × the market's median Exness spread (round trip), stress 3 ×.

**Benchmark:** random entry hours in the same period, with the same number of trades, the same sides and the same management; 1,000 sets; p = share of sets with a mean ≥ the actual mean.

**Decision per combination and market:** SCREEN-PASS if the mean R is > 0 in every period, the TEST stress mean is > 0, the TEST p ≤ 0.05 after BH over all 50 (combination × market) TEST p-values, and there are ≥ 30 TEST trades. Positive in every period but failing the rest = WATCH. Otherwise REJECTED. A SCREEN-PASS goes to a forward paper test with these rules, unchanged.

No parameter is changed after results are seen. All results are reported, including failures.
