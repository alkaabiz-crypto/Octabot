---
title: TradingView batch 005 pre-registration
description: Buy/sell rules for the built-ins that have no direction, 3-to-5-indicator combinations and ensembles, and a review of every indicator
sidebar_position: 1
---

# TradingView batch 005: pre-registration (2026-11-15, written before any computation)

User request: test the built-ins that "cannot be tested as buy/sell signals" the way traders actually use them, combine up to 5 or more indicators at once, and review every indicator.

**Common setup** (as in batch 003): Exness 1h candles (mid prices), markets XAUUSDm, USOILm, BTCUSDm, US500m, EURUSDm. The signal is known at a 1h close, and entry is at the next open. Management for every rule unless stated: stop 1.5 × ATR14, target 3 × ATR14 (2R), 48-hour time exit, one position at a time. Costs 1.5 × the median spread (stress 3 ×). Random-entry benchmark (same count, sides and management; 1,000 sets). Volume = Exness tick counts.

## Part A: rules for the built-ins without a direction (STR-030a–l)

How traders use each, from the web search on 2026-11-15 (Wikipedia, LuxAlgo, TradingSim, Quantified Strategies, MQL5 and WH SelfInvest on Larry Williams, the LuxAlgo 80%-rule page, CXO Advisory on Dichev & Janes):

| ID | Built-in | How it is used for buy/sell | LONG rule (SHORT mirrors) |
|---|---|---|---|
| STR-030a | ATR | Larry Williams volatility breakout | close > previous close + 1.0 × ATR14 |
| STR-030b | Bollinger Band Width | squeeze, then breakout | BBW was at its lowest of 120 bars within the last 5 bars, and the close crosses above the upper band |
| STR-030c | Choppiness Index | chop → trend transition | CHOP14 crosses below 38.2 after being above 61.8 within 20 bars; direction = sign of the 14-bar change |
| STR-030d | Mass Index | reversal bulge | MI (9, 25) rose above 27 and within 10 bars falls below 26.5; trade against the EMA 9 direction of the last 9 bars |
| STR-030e | Volume / Relative Volume | volume spike confirms the candle | volume > 2 × its 20-bar average and close > open |
| STR-030f | Volume / Relative Volume | volume climax = exhaustion (the opposite reading) | the same spike with close < open → LONG (fade) |
| STR-030g | Average Daily Range | ADR exhaustion fade | the price is more than 1.5 × ADR14 below today's open (first time today) → LONG |
| STR-030h | Historical Volatility | low volatility, then breakout | HV10 / HV100 < 0.5 and the close breaks the 20-bar high |
| STR-030i | Volume Profile | value-area re-entry (the "80% rule") | the prior UTC day's value area (70% of tick volume around the POC, from hourly typical prices); today opens below VAL and an hourly close is back inside → LONG, target VAH; once per day |
| STR-030j | Zig Zag (causal version) | break of the last confirmed swing | swings confirmed only after a 2 × ATR reversal; close above the last confirmed swing high |
| STR-030k | Seasonality | best/worst hour of the week | the hours of the week in the top/bottom 10% of average returns on TRAIN → LONG/SHORT for 1 hour (own management: 1-hour hold) |
| STR-030l | Moon Phases | Dichev & Janes lunar effect | LONG the half cycle around the new moon, SHORT the full-moon half; one trade per half cycle at the daily 00:00 open |

Not testable even this way: drawing tools (Auto Fib, pitchfork, trendlines; their rules are the Fibonacci, swing and channel rules tested elsewhere), breadth, open interest and COT (no data here).

## Part B: combinations of 3 to 5+ indicators (STR-031a–j)

| ID | Indicators | LONG trigger (first bar the condition is true) |
|---|---|---|
| STR-031a | 3: EMA 50/200 + RSI + OBV | EMA 50 > EMA 200, RSI 14 crosses above 50, OBV > its EMA 20 |
| STR-031b | 4: 031a + ADX | as 031a, and ADX > 25 with +DI > −DI |
| STR-031c | 5: 031b + VWAP | as 031b, and close > session VWAP |
| STR-031d | 5, one per category: Supertrend (trend), MACD (momentum), Chaikin Money Flow (volume), BB width rising (volatility), daily pivot (structure) | all 5 bullish (Supertrend up, MACD hist > 0, CMF > 0, BBW > its 20-bar mean, close > pivot) |
| STR-031e | 5 oversold oscillators: RSI, Stochastic, Bollinger, Williams %R, CCI | all 5 oversold (RSI < 30, %K < 20, close < lower band, %R < −80, CCI < −100) |
| STR-031f | 4-of-5 vote of 031d | at least 4 of the 5 bullish |
| STR-031g | all 82 directional indicators vote | the share of bullish minus bearish indicators crosses above +0.5 |
| STR-031h | 3 volume-confirmed breakout: Donchian + relative volume + MFI | close above the 20-bar high, volume > 1.5 × its 20-bar average, MFI > 50 |
| STR-031i | top 5 chosen by data, 4 h | per market, the 5 indicators with the highest |IC| at 4 h on TRAIN only (sign kept); composite = mean of their 500-bar rolling z-scores; LONG when it crosses above +1 |
| STR-031j | top 5 chosen by data, 24 h | as 031i with the 24 h IC |

## Decision (all of Part A and Part B)

- **SCREEN-PASS:** mean R > 0 in every period, TEST stress mean > 0, TEST p ≤ 0.05 after BH over every (rule × market) TEST p-value in this batch, and ≥ 30 TEST trades.
  - For 030k and 031i–j, TRAIN is the selection period, so "every period" means every period except TRAIN.
  - For 030k and 030l the TEST p is a one-sided t-test of the net returns (the null is zero), not the random benchmark.
- Positive in every period without the rest = WATCH. Otherwise REJECTED. A SCREEN-PASS goes to a forward paper test.

## Part C: review of every indicator (not a test)

`INDICATOR_REVIEW.md`: for each of the about 100 built-ins and the main community scripts, what it measures, how traders use it, what we tested and the verdict, and its best market from batch 004.

No parameter is changed after results are seen. All results are reported.
