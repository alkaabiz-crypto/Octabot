# Batch 3 pre-registration: indicators, strategies, theories and their mixes

**Requested by the user on 2026-11-12:** "make 3 different parts: indicators, strategies, theories, test all of them and see if you can mix something up … don't make the tests too hard."

**Committed before any Batch 3 result was computed.** Paper research only.

**The data rule holds:** nothing before 2025-01-01.

**Frozen files are untouched.** This is a new batch in a new folder. The library freeze (`../theory_library/FREEZE.md`) is lifted for new searches only, at the user's request; frozen files and forward tests are unchanged.

## Design: easy search, fair confirmation

The search stage is deliberately lenient. The multiple-testing burden is carried only by the shortlist tested once on unseen data. That makes a real edge much easier to confirm than correcting for every combination searched, while keeping luck from passing as skill.

| Stage | Data | Rule |
|---|---|---|
| **1. Search** (all combinations) | 2025-01-01 → 2025-12-31 | **Kept:** ≥ 30 trades, mean net > 0 at 1× cost, profit factor > 1.0. **Ranked** by t-statistic. |
| **2. Shortlist** | — | The **top 30 per part** (90 in total). At most 3 per market × entry signal, so the list is not 30 copies of one idea. |
| **3. Confirmation** (each shortlisted item once) | 2026-01-01 → end of data (≈ 10 months, never used for selection) | **PASS** needs all of: one position at a time, ≥ 20 trades, mean net > 0 at **2× cost**, and a random-timing p-value that survives **Holm across the 90** at α = 0.05. |
| **4. Survivors** | — | A new forward paper test, rules frozen, under `../FORWARD_EVALUATION.md`. A historical pass alone is never called "proven". |

**Random-timing benchmark** (1,000 draws, seed 20261113 + CRC32 of the ID): the same number of trades, the same sides and the same exit rule, on random bars of the confirmation period. The one-sided p is (1 + number of draws with a mean ≥ the observed mean) / 1,001.

**Disclosed weakness:** these markets' 2025–26 prices were examined by earlier studies, so 2026 is "unused for selection here" but not untouched. Only forward data is fully independent, which is why step 4 exists.

## Data and execution (all parts)

**Markets:**
- Exness 1m bars, with per-minute spread: XAUUSDm, USOILm, US500m, USTECm, DE30m.
- Binance spot 1m as a proxy for the Exness CFDs: BTCUSDT and ETHUSDT. Exness spreads: BTC 0.79 bp, ETH 4.13 bp.

**Timeframes:** 15m, 1h and 4h, built from the 1m bars.

**Data gaps:** the known Exness archive gap of 2026-03-30/31 is in four markets. USTECm ends on 2026-10-28.

**Execution:**
- **Signal:** at a bar's close.
- **Entry:** at the **next bar's open** (market order). There are no limit-order entries, so the order-handling look-ahead found in the library cannot occur.
- **Stop first:** inside a bar, the stop is checked before the target. A gap through the stop fills at the open.
- **Target fill:** a target needs price to go one spread beyond it.

**Exits** (each combination is tested with all three):

| | Stop | Target | Max hold |
|---|---|---|---|
| X1 | 1.5 × ATR14 | 3 × ATR14 (2R) | 24 bars |
| X2 | 1.0 × ATR14 | 1.5 × ATR14 (1.5R) | 12 bars |
| X3 | — | — | time exit after 12 bars |

**Cost:**
- **1×** is the median round-trip spread of each market in bp of price.
- **2×** doubles it. Swap is not deducted.

## Part A: Indicators (combinations of up to 3)

**Entry triggers** are events on a closed bar (long and mirror short):
- RSI(14) crosses 30/70;
- RSI(2) < 10 / > 90;
- MACD/signal cross;
- MACD zero cross;
- EMA 9/21 cross;
- EMA 50/200 cross;
- close crosses EMA50;
- Stochastic(14,3,3) %K/%D cross below 20 / above 80;
- CCI(20) crosses ±100;
- Bollinger(20,2): close back inside after closing outside;
- Bollinger breakout (close outside);
- Donchian(20) breakout;
- Keltner(20, 2 ATR) breakout;
- Supertrend(10,3) flip;
- Parabolic SAR flip;
- DI+/DI− cross;
- Williams %R(14) crosses −80/−20;
- Ichimoku Tenkan/Kijun cross;
- Heikin-Ashi colour flip;
- ROC(10) zero cross;
- Aroon(25) up/down cross;
- TRIX(15) signal cross;
- Awesome Oscillator zero cross;
- CMO(14) crosses ±50;
- Ultimate Oscillator crosses 30/70;
- **wick-rejection candle** ("John Wick": wick ≥ 2 × body and ≥ 60% of the range, close away from the wick).

**Filters** are states that must agree with the trade side:
- close vs EMA200;
- EMA50 vs EMA200;
- ADX(14) > 25;
- ADX(14) < 20;
- RSI(14) vs 50;
- MACD vs 0;
- Supertrend direction;
- close vs session VWAP (daily anchored);
- higher-timeframe trend (EMA of 4× the period);
- Ichimoku: price vs cloud;
- Bollinger width in the lowest 20% of the last 100 bars (squeeze);
- London/New York session hours (07–20 UTC);
- close vs SMA20;
- the 3-bar slope of EMA20.

**Combinations:** each trigger alone, with any 1 filter, and with any 2 filters.

## Part B: Strategies (published rule sets, taken as described)

1. Golden/death cross (EMA50/200).
2. MACD cross with the EMA200 trend.
3. Connors RSI(2): close above SMA200 and RSI2 < 10 (mirror short).
4. Bollinger + RSI: close below the lower band and RSI < 30 (mirror).
5. Supertrend flip with EMA200.
6. Triple EMA 9/21/55 alignment.
7. Stochastic cross from oversold in an EMA200 uptrend.
8. Ichimoku TK cross above or below the cloud.
9. Turtle Donchian-20 breakout.
10. BB-inside-Keltner squeeze breakout.
11. PSAR flip with EMA200.
12. Heikin-Ashi flip with EMA50.
13. DI cross with ADX > 25.
14. CCI ±100 with EMA200.
15. Williams %R pullback in an EMA50 trend.
16. Inside-bar breakout in the EMA50 trend.
17. Engulfing candle on the EMA50 side of the trend.
18. VWAP cross with EMA200.
19. MACD cross with RSI > 50 (mirror < 50).
20. EMA ribbon (8/13/21/34) pullback to EMA21.
21. Awesome Oscillator zero cross with EMA200.
22. Aroon cross with EMA200.
23. Three white soldiers / three black crows.
24. RSI regular divergence (14-bar).
25. Keltner pullback in an ADX > 25 trend.

## Part C: Theories (price action, smart-money concepts, the user's theories) and mixes

**Entry triggers:**
- **T1, the user's Theory #2:** price trades into the previous day's high or low and the bar closes back inside, giving a reversal.
- **T2:** a fair value gap forms (3-candle gap), traded in the gap's direction.
- **T3:** liquidity sweep: the bar's high exceeds the 20-bar high, then it closes below it (mirror).
- **T4:** break of structure: a close beyond the last 5-bar fractal swing.
- **T5:** opening-range breakout: the first hour of the main session (index and cash-market hours; 00:00 UTC for crypto).
- **T6:** Asian-range (00–07 UTC) breakout during 07–12 UTC.
- **T7:** a causal Fibonacci 0.618 pullback: after a 20-bar swing in the SMA50 direction, the close re-crosses the 0.618 level in the trend direction.
- **T8:** previous week's high or low breakout.
- **T9:** a 2σ deviation from session VWAP reverts (close back inside).

**Mixes:** each theory alone; plus the wick-rejection confirmation on the signal bar; plus any 1 or 2 Part A filters; plus wick confirmation with 1 filter. This is the user's "Theory #2 + indicators + John Wick" idea.

## Accounting

Every combination searched is counted in `../RESEARCH_REGISTRY.md`. Confirmation is corrected over the 90 shortlisted items, which is valid because the 2026 period was not used to choose them.
