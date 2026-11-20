# Pre-registered protocol: the requested indicators, each tested on its own

Written on 2026-11-10, before any result of this test was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

Every indicator is tested **separately**; no combinations. Group A is the three scripts in the user's screenshot.
Group B is the user's settings list, plus the items still untested from the earlier checklist.

## Group A: community scripts from the screenshot

**A1. Session VWAP Profile & Candle Delta (BigBeluga)**

TradingView is blocked from this environment, and the script has no published port, so it is rebuilt from its
documented parts:

- a session-anchored VWAP (UTC day for BTC; the session open after the daily break for oil and gold);
- volume-weighted standard deviation bands at 1σ and 2σ;
- a session volume profile.

The script itself is a charting tool without buy/sell rules, so two standard rules are tested:

- **A1a band reversion:** BUY when a 1H close crosses back above the −2σ band; SELL when it crosses back below +2σ.
- **A1b band breakout:** BUY when a 1H close crosses above +1σ; SELL when it crosses below −1σ.

**Candle delta cannot be tested.** It needs buyer versus seller volume, and Exness quotes carry no trade direction.

**A2. Squeeze Momentum (LazyBear), default settings**

Already tested with identical code, data and rules in `research/community_indicators`. Those results are reported and
not re-run.

**A3. Machine Learning: Lorentzian Classification (jdehorty), default settings**

The defaults are taken from the `advanced-ta` Python port (v0.1.8), read in this session:

- 8 neighbours and 2,000 bars back;
- features RSI(14, 2), WT(10, 11), CCI(20, 2), ADX(20, 2) and RSI(9, 2);
- volatility filter on, regime filter on at threshold −0.1, ADX filter off, EMA/SMA filters off;
- kernel filter on: rational-quadratic kernel with lookback 8, relative weight 8, regression level 25, smoothing off;
- the script's training label, exactly as in the original: the sign of the price change over the previous 4 bars;
- the original's approximate nearest-neighbour loop: Lorentzian distance, every bar whose loop index is not a multiple
  of 4, and the lastDistance rule.

Two deviations, both made to avoid look-ahead:

1. The port scales two features with the minimum and maximum of the whole data set, which leaks future information.
   The running historical minimum and maximum of the Pine original is used instead.
2. The neighbour search uses the 2,000 bars before each bar, so signals exist at every date, not only in the chart's
   last 2,000 bars.

Entries are the script's start-long and start-short conditions. Exits: the three standard exits, plus the script's own
**NATIVE** exit, which closes after 4 hourly bars (no stop).

## Group B: the settings list, each indicator alone

| # | Indicator and settings | BUY | SELL |
|---|---|---|---|
| B1 | EMA 20 / 50 / 200 pullback | EMA 50 > EMA 200 and close > EMA 200; the close crosses back above EMA 20 after closing below it | mirror |
| B2 | Session VWAP (default session) | close crosses above session VWAP | close crosses below |
| B3 | RSI 14, 30/70 | RSI crosses up through 30 | crosses down through 70 |
| B4 | RSI 14 divergence | a confirmed swing low (5 bars each side) below the previous swing low while RSI is higher (bullish divergence), on the confirmation bar | the mirror at swing highs |
| B5 | ADX 14, threshold 20 | ADX crosses above 20 with +DI > −DI | ADX crosses above 20 with −DI > +DI |
| B6 | ADX 14, threshold 25 | the same at 25 | the same at 25 |
| B7 | ATR 14 | **Not a signal.** ATR measures volatility, not direction. It sets the stop (2 × ATR) and target in every test. | |
| B8 | Squeeze Momentum (LazyBear default) | as A2: earlier results reported, not re-run | |
| B9 | Volume Profile, 70% value area, intraday, **US oil only** | (a) "80% rule": the price opens the session below the prior session's value-area low, and a 1H close crosses back above it; (b) acceptance breakout: a 1H close crosses above the prior session's value-area high | (a) the mirror at the value-area high; (b) a close crosses below the value-area low |
| B10 | Supertrend 10, 3 on BTC (untested there) | trend flips up | flips down |
| B11 | MACD 12/26/9 on BTC (untested there) | line crosses above signal | crosses below |

**Volume Profile construction.**

- The profile is built from the prior session's 15-minute candles, with each candle's tick count spread evenly over its
  high-low range.
- 50 rows span the session's range.
- The POC is the row with the most volume. The value area grows outward from the POC to 70% of the volume.
- Tick volume is used because a CFD has no exchange volume.

## Everything else as in `research/indicator_scan/PROTOCOL.md`

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm bid/ask, as 15-minute candles; signals on 1H bid candles. 2024 is
  warm-up only.
- **Exits.**
  - HW: 2 × ATR stop, 1 × ATR target, 24 h.
  - SYM: 2 × ATR target and stop, 48 h.
  - TRAIL: 2 × ATR stop, then a 3 × ATR trail.
  - NATIVE: A3 only.
- **Fills and costs.** Buy at the ask, sell at the bid, plus 0.02% slippage.
- **Selection** is 2025; **confirmation** is 2026 to the latest quote.
- **Reliable** means, in both periods:
  - at least 30 trades in 2025 and 20 in 2026;
  - expectancy > 0;
  - p_random ≤ 0.05 against 1,000 matched random-entry runs.

  **70%-worthy** means reliable, and also a win rate of at least 70% in both periods.
- **Untouched-data check.** Any variant that is reliable is re-tested on data never used to select it: BTC 2020–2024
  and ETH 2020–now on Binance (0.05% cost), or the 2019–2024 Exness history for oil. This check is pre-registered now,
  unlike round 2, where it was added afterwards.

About 190 variants are tested, so about 10 would pass the 2025 stage and about 0.5 both stages by chance. A pass
justifies only a frozen forward paper test.
