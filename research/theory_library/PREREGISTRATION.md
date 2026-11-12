# Theory library: every common trading theory, one honest test, pre-registration

Committed **2026-11-12, before any of these rules were run on this data.** The user asked for every theory found online to be tested and organised into candidates.

**Honest scope:** thousands of variants exist online. This tests **the canonical, published version of 40 widely taught theories**, covering every major family. Each uses its **textbook default parameters**, and nothing is tuned. The sources are listed in `SOURCES.md`.

## Markets and data, all from 2025-01-01 onward

| Market | Data | Cost per side, 1× (2× is also reported) |
|---|---|---|
| Gold (XAUUSDm), US oil (USOILm), DAX (DE30m), S&P 500 (US500m), Nasdaq (USTECm) | Exness 1-minute mid bars from ticks (`../orb_study/build_bars.py`), built into 15m, 1h, 4h and 1d candles. A day runs 22:00–22:00 UTC. | half of the median spread in that bar |
| BTC, ETH | Binance 1h klines (`../daily_signal_dca/from_2025/data`), built into 4h and 1d | 0.05% (exchange taker fee level) |

- **Periods:** development **2025**, holdout **2026 (Jan–Oct/Nov)**.
- **Swap:** not deducted. This favours multi-day holds, and the report will flag it.

## Common execution rules

- **Decisions** are made on a closed candle, and fills happen at the **next candle's open**.
- **Stops and targets** are checked on later candles. If one candle touches both, the **stop counts first**.
- **Positions:** one at a time per theory and market. Shorts are allowed unless a theory says long-only.
- **Intraday theories** close at the end of their session or day.
- **Standard pattern exit (PX)**, used where a theory gives no exit of its own:
  - stop just beyond the pattern's extreme;
  - target **2R**;
  - time stop after 20 candles.
- **Unit:** net return per trade (bp of price), and the sum per period.

## The catalogue (40 theories)

**A. Trend and momentum**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| A1 | EMA 9/21 cross | 1h | always in, flipping at each cross |
| A2 | SMA 50/200 cross ("golden cross") | 4h | long when SMA50 > SMA200, short when below |
| A3 | MACD (12,26,9) signal cross | 1h, 4h | always in, flipping at each cross |
| A4 | Supertrend (10,3) | 1h, 4h | follow its direction |
| A5 | Parabolic SAR (0.02, 0.2) | 1h | follow its side |
| A6 | ADX/DMI (14) | 1h | long if ADX > 25 and +DI > −DI, short mirror; flat when ADX < 20 |
| A7 | Turtle system 1 | 1d, 4h | 20-candle breakout entry, 10-candle opposite breakout exit |
| A8 | Turtle system 2 | 4h | 55-candle breakout, 20-candle exit |
| A9 | Ichimoku (9,26,52) | 4h | long when close is above the cloud and Tenkan > Kijun; short mirror; exit when the close re-enters the cloud |
| A10 | Heikin-Ashi colour | 1h | follow the HA candle colour |
| A11 | Time-series momentum | 1d | hold the sign of the 20-day return, rebalanced daily |
| A12 | Bollinger/Keltner squeeze | 1h | BB(20,2) inside KC(20,1.5), then trade the first close outside BB in that direction; exit when the close crosses the 20-SMA |
| A13 | Larry Williams volatility breakout | intraday on 1h | buy stop at day open + 0.6 × previous day range, sell stop at open − 0.6 × range; exit at day end |

**B. Mean reversion**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| B1 | RSI(14) 30/70 | 15m, 1h | long when RSI crosses back above 30, exit when RSI > 50; short mirror |
| B2 | Connors RSI(2) | 1d, 1h | long if close > SMA200 and RSI2 < 10, exit when close > SMA5; short mirror at RSI2 > 90 below SMA200 |
| B3 | Bollinger bounce (20,2) | 1h | close below the lower band → long, exit at the middle band; mirror |
| B4 | Stochastic (14,3,3) 20/80 | 1h | %K crosses %D below 20 → long, exit when %K > 50; mirror |
| B5 | CCI(20) ±100 | 1h | cross back above −100 → long, exit at CCI > 0; mirror |
| B6 | Williams %R(14) | 1h | cross back above −80 → long, exit at −50; mirror |
| B7 | Session-TWAP reversion | 15m, intraday | close > 2 sd above the session TWAP → short, target the TWAP, stop at 3 sd; mirror. Exness CFDs have no real volume, so TWAP stands in for VWAP. |
| B8 | Classic pivot points | 15m, intraday | fade a touch of R1 or S1 back to the pivot P, stop at R2 or S2 |
| B9 | Fibonacci 61.8% pullback | 1h | uptrend (close > SMA50), swing = last 20 candles' low → high; buy limit at 61.8% retracement, stop below the swing low, target the swing high; mirror |
| B10 | Turtle Soup | 1d | price makes a new 20-day low while the previous 20-day low is ≥ 4 days old, then closes back above it → long, using PX exits; mirror |

**C. Candlestick and price patterns, all using PX exits**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| C1 | Bullish/bearish engulfing | 1h | |
| C2 | Hammer / shooting star | 1h | wick ≥ 2× body, close in the outer third |
| C3 | Inside-bar breakout | 1h, 1d | trade the break of the mother bar |
| C4 | NR7 breakout | 1d | the narrowest range of 7 days, trade the break of its high or low |
| C5 | Morning / evening star (3 candles) | 1h | |
| C6 | Three white soldiers / three black crows | 1h | |

**D. Sessions, ICT and smart-money**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| D1 | Asian range breakout | 1-minute engine | range 00:00–07:00 UTC, trade the first break 07:00–12:00 UTC, stop at the other side, 1:1 target, exit 16:00 UTC |
| D2 | London Judas swing (ICT) | 15m | 07:00–10:00 UTC, the price runs above the Asian high and a 15m candle closes back inside → short, target the Asian low, stop at the sweep high; mirror |
| D3 | ICT Silver Bullet (simplified, objective) | 5m | 10:00–11:00 New York; a 3-candle fair value gap (FVG) in the direction of the 5m displacement after a sweep of the 09:30–10:00 high or low; limit entry at the FVG edge, stop beyond candle 1, target 2R, exit 12:00 New York |
| D4 | Generic FVG fill fade | 1h | when an FVG forms, place a limit order at its far edge to trade back with the gap's direction; stop beyond candle 1, 2R target |
| D5 | Index cash-open gap fade | US500/USTEC 09:30 New York, DE30 09:00 Berlin | gap = open − previous cash close; fade it toward the previous close; stop 1 × gap; exit at the cash close |
| D6 | Previous-day high/low breakout | 1h | the first close above the previous day's high → long, stop at the previous day's middle, 2R target; mirror |

**E. Calendar**

| ID | Theory | Rule |
|---|---|---|
| E1 | Turnaround Tuesday | indices: buy the Monday close if Monday fell, sell the Tuesday close |
| E2 | Turn of month | long from the last trading day's close to the close of the 3rd trading day |
| E3 | Overnight vs intraday | indices: long from the 16:00 New York close to the 09:30 open (DE30: 17:30 → 09:00 Berlin) |
| E4 | Crypto weekend | BTC/ETH: long Friday 00:00 UTC → Monday 00:00 UTC |
| E5 | Best-day-of-week | **information only**, no verdict: mean return per weekday |

The ORB and Theory #2 families have their own studies (`../orb_study`, `../zone_reversal_study`). They are included in the final candidate table, not re-run.

**Not testable without missing data, so listed and skipped:**
- volume profile / order flow (no real volume on CFDs);
- COT positioning (weekly, different source);
- Elliott waves, harmonics and pitchforks (no objective rule);
- news and sentiment models;
- funding/basis for BTC (no 2025+ funding history downloaded).

## Random control and verdict

- **Control:** for every theory × market × timeframe, **500 draws** with seed 20261112. Each draw keeps the same number of trades, the same sides and the same holding durations (in candles), but starts each trade at a random candle in the same period. Return is open-to-open over the same duration, with the same costs.
- **PASS needs all of:**
  - mean net return per trade > 0 at **2× costs in both** periods;
  - at least 30 holdout trades;
  - mean above the random **95th percentile in both** periods.
- **Multiple testing:** about 400 combinations, so roughly 1 false PASS is expected. **Every PASS is a candidate only**, and must survive:
  1. an **independent re-implementation** of its rules;
  2. ±1 step **neighbour parameters**, which must also be positive in the holdout;
  3. for intraday entries, a **tick-level fill check**.

## Output

1. **A candidate league table:** every combination, ranked by holdout net at 2× costs, with its verdict.
2. **Family summaries:** the share of each family positive in the holdout, against the random median.
3. **Survivors:** a frozen forward paper test is proposed for each one.

## Addendum 1: batch F, popular retail, TradingView, YouTube and smart-money strategies

Committed **2026-11-12, before running and before the main library run.** The user asked for a wider internet search. Same data, costs, controls and PASS bar as above. Default parameters only.

**Swing points:** a swing (fractal) high or low is the highest or lowest candle of the 5 centred on it. It is **only known 2 candles later**, so no future data is used.

**Indicator and trend strategies**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| F1 | Squeeze Momentum (LazyBear, the most-liked TradingView indicator) | 1h, 4h | BB(20,2) inside KC(20,1.5) = squeeze on. When the squeeze turns off, trade in the direction of the momentum value. Momentum is the 20-candle linear-regression value of close − mean(mid of the 20-candle high/low, SMA20). Exit when momentum changes sign. |
| F2 | UT Bot (key 1, ATR 10) | 1h, 4h | ATR trailing stop that flips with price; follow its side |
| F3 | Chandelier Exit (22, 3) | 1h, 4h | long stop = highest high(22) − 3·ATR(22); short stop = lowest low(22) + 3·ATR(22). Go long when the close crosses above the short stop, short when it crosses below the long stop. |
| F4 | SSL channel (10) | 1h, 4h | +1 if close > SMA10 of highs, −1 if close < SMA10 of lows, else hold the previous side; follow |
| F5 | Hull MA (55) slope | 1h, 4h | long while HMA is rising, short while falling |
| F6 | 200 EMA + MACD (viral YouTube version) | 1h | long when close > EMA200 and MACD crosses above its signal line below zero; stop = lowest low of the last 10 candles; target 1.5R; mirror |
| F7 | RSI(14) divergence | 1h | bullish: the newest swing low is below the previous one (within 30 candles), RSI at that swing is higher than at the previous one, and RSI < 40 → long next open; standard pattern exit with stop at the swing low; mirror |
| F8 | EMA20 pullback in trend | 1h | EMA50 > EMA200, the low touches EMA20 and the close is above it → long; standard pattern exit with stop at the candle low; mirror |

**Smart-money and chart patterns**

| ID | Theory | Timeframe | Rule |
|---|---|---|---|
| F9 | SMC order block after a break of structure | 1h | a close above the last swing high is a BOS up. The order block is the last bearish candle before the candle that broke. Limit buy at the OB high, valid 20 candles; stop below the OB low; 2R; mirror. |
| F10 | Double bottom / top breakout | 1h, 1d | two swing lows within 0.5·ATR(14) of each other, 5–40 candles apart. Neckline = the highest high between them. A close above the neckline → long; stop below the lower low; target = the measured move; 20-candle time stop. Mirror. |
| F11 | 1-2-3 reversal | 1h | swing low (1), the next swing high (2), then a higher swing low (3). A close above 2 → long; stop below 3; 2R; mirror. |
| F12 | Head and shoulders / inverse | 1h | three swing highs where the middle one is ≥ 0.5·ATR above both outer ones and the outer ones are within 1·ATR of each other. Neckline = the lowest low between them. A close below the neckline → short; stop above the right shoulder; target = the measured move; mirror. |
| F13 | Golden pocket (61.8–65%) | — | **Not run.** It is the same as B9 within its tolerance. Listed for completeness. |

- **Combinations:** about 150 new, about 550 in total. Under the two-period PASS bar, about 1.4 false PASSes are expected across everything.
- **Sources:** added to `SOURCES.md`.
