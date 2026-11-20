---
title: Review of every TradingView indicator
description: What each TradingView indicator measures, how traders use it, what our tests found and the market where it did best
sidebar_position: 3
---

# Review of every TradingView indicator (2026-11-15)

This review covers the about 100 TradingView built-in indicators and the most popular community scripts. Each was tested in batches 001–005 on Exness prices with the pre-registered rules in each batch's `PREREG.md`.

**How to read the verdicts**
- **IND verdicts:** does the indicator's value predict the next 1, 4, 24 or 120 hours on gold, oil, BTC, the S&P 500 and EUR/USD, in every period, beyond what the past return already tells you? INFORMATIVE / WEAK / REDUNDANT / NONE.
- **Best market (held-out):** chosen on 2023 → mid-2025 among 33 markets × 3 horizons, then checked on July 2025 → now (batch 004).
- **Best after costs (exploratory):** the market with the best after-cost result on old data, and what it made on new data, per 24-hour trade. For comparison, buying and holding gold made +4.5 bp per day and the US indices about +4 bp per day in the same period.

**The overall answer:** no TradingView indicator, alone or combined, is a reliable buy/sell signal after costs on these markets.
- The one pattern every indicator shares is short-term reversal: over 1 hour, trend signals slightly predict the opposite move, most strongly on small coins. But that reversal is smaller than the spread.
- The best 24-hour results are on gold and US indices. They are mostly the long side of a strong 2025–26 rally, about the same as buying and holding.

## Indicators with a direction

| ID | Indicator | What it measures | How traders use it | Verdict | Best market (held-out) | Best after costs (exploratory) |
|---|---|---|---|---|---|---|
| IND-003 | KST (Know Sure Thing) | weighted sum of four smoothed rates of change | buy when KST crosses above its signal line | NONE | LTCUSD h1 (contrarian): same direction, not significant, -209 bp after costs | USTEC 24h contra: +5.4 bp |
| IND-004 | Distance from session/daily VWAP | distance of price from the volume-weighted average price of the session | buy above VWAP / sell below; pullbacks to VWAP | NONE | XRPUSD h1 (contrarian): holds, -41 bp after costs | USDJPY 24h follow: -0.1 bp |
| IND-005 | RSI (14, 2) | speed of recent gains vs losses, 0–100 | buy below 30 (oversold), sell above 70; or 50-line trend filter | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | USTEC 24h contra: +4.8 bp |
| IND-006 | MACD | difference of a fast and slow EMA, and its signal line | buy when MACD crosses above signal or zero | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h contra: -2.5 bp |
| IND-007 | Moving-average trend (EMA 9/21, SMA 50/2 | fast vs slow moving average | buy on golden cross (fast above slow) | NONE | BCHUSD h1 (contrarian): holds, -53 bp after costs | US30 24h follow: -6.7 bp |
| IND-008 | Supertrend | ATR trailing line that flips with trend | buy when it flips below price | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | USDJPY 24h contra: +0.9 bp |
| IND-009 | Parabolic SAR | accelerating trailing stop dots | buy when dots flip below price | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -1.8 bp |
| IND-010 | ADX / DMI | trend strength (ADX) and direction (+DI/−DI) | trade the DI direction only when ADX > 20–25 | NONE | LTCUSD h1 (contrarian): holds, -209 bp after costs | US30 24h follow: -5.7 bp |
| IND-011 | Donchian channel position | where price sits in its 20-bar high–low range | buy breakouts of the 20-bar high (turtle rule) | NONE | LTCUSD h1 (contrarian): holds, -209 bp after costs | US30 24h follow: -4.2 bp |
| IND-012 | Ichimoku cloud | cloud of mid-range averages, five lines | buy above the cloud, Tenkan/Kijun crosses | NONE | BCHUSD h1 (contrarian): holds, -53 bp after costs | XAUUSD 24h follow: +1.6 bp |
| IND-013 | Bollinger %B and squeeze | price position inside 2-standard-deviation bands | fade the bands in ranges; breakouts after a squeeze | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -7.0 bp |
| IND-014 | Stochastic | close vs recent high–low range, 0–100 | buy %K crossing up from below 20 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -42 bp after costs | USTEC 24h follow: -11.4 bp |
| IND-015 | CCI | deviation of typical price from its average | buy below −100, sell above +100 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -3.9 bp |
| IND-016 | Williams %R | inverse of Stochastic, −100–0 | buy below −80, sell above −20 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -12.6 bp |
| IND-017 | Williams Vix Fix | synthetic VIX: distance from 22-bar high close | spikes mark panic lows → buy | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h contra: +5.2 bp |
| IND-020 | 20-day momentum (time-series) | 20-day price change | time-series momentum: long if positive | NONE | BCHUSD h1 (contrarian): holds, -54 bp after costs | XAUUSD 24h follow: +3.0 bp |
| IND-022 | Aroon oscillator (25) | bars since highest high vs lowest low | buy when Aroon Up crosses above Down | NONE | ETHUSD h1 (contrarian): same direction, not significant, -13 bp after costs | US30 24h follow: -10.7 bp |
| IND-023 | Vortex (14) | upward vs downward movement over 14 bars | buy when VI+ crosses above VI− | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -12.0 bp |
| IND-024 | TRIX (15) | rate of change of a triple-smoothed EMA | buy on zero or signal cross | NONE | BCHUSD h4 (contrarian): same direction, not significant, -54 bp after costs | US30 24h follow: -14.1 bp |
| IND-025 | KAMA slope | adaptive average that speeds up in trends | trade its slope / price crossing it | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | USTEC 24h follow: -13.8 bp |
| IND-026 | Williams Alligator | three shifted smoothed averages (jaw, teeth, lips) | trade when the lines open in order; sleep when tangled | NONE | BCHUSD h4 (contrarian): same direction, not significant, -55 bp after costs | BTCUSD 24h follow: -24.4 bp |
| IND-027 | Hull MA (55) slope | low-lag weighted moving average | trade its colour (slope) change | NONE | ETHUSD h1 (contrarian): same direction, not significant, -13 bp after costs | AUDUSD 24h contra: +0.0 bp |
| IND-028 | Keltner position | price vs EMA ± ATR channel | breakouts outside the channel; mean reversion inside | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USDJPY 24h follow: +1.0 bp |
| IND-029 | Heikin-Ashi colour run | smoothed candle colour | stay in while candles keep one colour | NONE | XRPUSD h1 (contrarian): holds, -41 bp after costs | US30 24h follow: -6.6 bp |
| IND-030 | Awesome Oscillator | 5- vs 34-bar midpoint average | saucer and zero-line cross signals | NONE | BCHUSD h1 (contrarian): holds, -54 bp after costs | AUDUSD 24h contra: -2.4 bp |
| IND-031 | Ultimate Oscillator | buying pressure over 7/14/28 bars | divergence buys below 30 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -40 bp after costs | US500 24h contra: -1.7 bp |
| IND-032 | Rate of change (12) | percent change over 12 bars | zero-line cross / extremes | NONE | XRPUSD h1 (contrarian): same direction, not significant, -40 bp after costs | US500 24h follow: -7.0 bp |
| IND-033 | Fisher transform (10) | price turned into a normal-like distribution | turning points at extremes | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | XAUUSD 24h follow: +5.1 bp |
| IND-034 | Elder ray (13) | high and low vs EMA 13 (bull/bear power) | buy when bear power rises below zero in an uptrend | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -5.8 bp |
| IND-036 | Squeeze Momentum [LazyBear] | Bollinger inside Keltner (squeeze) + momentum histogram | trade the first bar after the squeeze fires, in the momentum direction | NONE | ETHUSD h1 (contrarian): holds, -13 bp after costs | XAUUSD 24h follow: +11.2 bp |
| IND-037 | WaveTrend [LazyBear] | channel-index oscillator with two lines | buy wt1/wt2 cross below −53 (oversold) | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h contra: -2.1 bp |
| IND-038 | QQE Mod | smoothed RSI with a volatility trailing line | buy when it crosses above the line / 50 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -40 bp after costs | US500 24h contra: -0.6 bp |
| IND-039 | SSL channel (10) | moving averages of highs and lows, flip channel | buy when price closes above the high average | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -2.0 bp |
| IND-040 | UT Bot alerts | ATR trailing stop (key value 1) | buy when price crosses above the trail | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -0.1 bp |
| IND-041 | Chandelier exit (22,3) | ATR stop from the 22-bar extreme | used as a trailing exit and flip signal | NONE | ETHUSD h1 (contrarian): holds, -13 bp after costs | USTEC 24h contra: +11.8 bp |
| IND-042 | Schaff Trend Cycle | MACD put through a double stochastic | buy when it rises from below 25 | NONE | XRPUSD h1 (contrarian): reversed, -41 bp after costs | US30 24h follow: +1.6 bp |
| IND-043 | Coppock curve | long-term smoothed rate of change | buy when it turns up from below zero (bottoms) | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | US30 24h follow: -4.0 bp |
| IND-044 | Detrended price oscillator (20) | price vs a shifted moving average (cycles) | cycle tops and bottoms | NONE | XRPUSD h4 (follow): same direction, not significant, -37 bp after costs | USTEC 24h follow: +3.6 bp |
| IND-045 | Least-squares MA (50) slope | end point of a linear regression line | trend slope / crosses | NONE | BCHUSD h1 (contrarian): holds, -53 bp after costs | US500 24h contra: +3.6 bp |
| IND-046 | Connors RSI | RSI 3 + streak RSI + percent rank | buy below 10, sell above 90 (short-term reversal) | NONE | BTCUSD h1 (contrarian): holds, -11 bp after costs | ETHUSD 24h contra: -15.9 bp |
| IND-047 | Laguerre RSI | RSI on a four-stage Laguerre filter | buy when it rises above 0.2 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -42 bp after costs | US500 24h contra: -1.6 bp |
| IND-048 | Choppiness-filtered momentum | momentum only in trending (non-choppy) periods | trend filter for momentum | NONE | XRPUSD h1 (contrarian): same direction, not significant, -39 bp after costs | BTCUSD 24h follow: -65.6 bp |
| IND-049 | ALMA slope | Gaussian-weighted moving average | trade its slope / price crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -14.8 bp |
| IND-050 | Balance of Power | close minus open relative to range | buyers vs sellers control; above zero bullish | NONE | XRPUSD h1 (contrarian): same direction, not significant, -42 bp after costs | XAUUSD 24h follow: +12.0 bp |
| IND-051 | BBTrend | short vs long Bollinger band spread | positive = uptrend expansion | NONE | BCHUSD h4 (contrarian): same direction, not significant, -56 bp after costs | USTEC 24h follow: -1.5 bp |
| IND-052 | Chaikin Money Flow | volume-weighted close location over 20 bars | buy when CMF > 0 (accumulation) | NONE | BTCUSD h1 (contrarian): holds, -11 bp after costs | DE30 24h follow: -6.5 bp |
| IND-053 | Chaikin Oscillator | momentum of accumulation/distribution | buy on zero-line cross up | NONE | BTCUSD h1 (contrarian): holds, -11 bp after costs | USTEC 24h follow: +2.2 bp |
| IND-054 | Accumulation/Distribution | running sum of volume-weighted close location | confirm trends; divergences | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -12.4 bp |
| IND-055 | Chande Kroll Stop | ATR stop pair from recent extremes | flip signals and trailing stops | NONE | ETHUSD h1 (contrarian): holds, -13 bp after costs | US30 24h follow: -5.3 bp |
| IND-056 | Chande Momentum Osc. | up minus down moves, ±100 | buy below −50, sell above +50 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -4.6 bp |
| IND-057 | Chop Zone | EMA 34 angle colour bands | trade in the colour's direction | NONE | BCHUSD h1 (contrarian): holds, -53 bp after costs | US500 24h contra: +3.8 bp |
| IND-058 | Trend Strength Index | correlation of price with time | trend strength / direction | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -15.5 bp |
| IND-059 | DEMA slope | double-smoothed EMA with less lag | slope and crosses | NONE | XRPUSD h1 (contrarian): holds, -40 bp after costs | ETHUSD 24h contra: -21.5 bp |
| IND-060 | TEMA slope | triple-smoothed EMA with less lag | slope and crosses | NONE | XRPUSD h1 (contrarian): holds, -41 bp after costs | US30 24h contra: -4.5 bp |
| IND-061 | Ease of Movement | price change per unit of volume | buy when above zero (easy upward movement) | NONE | LTCUSD h1 (contrarian): holds, -209 bp after costs | GBPJPY 24h contra: -2.5 bp |
| IND-062 | Elder Force Index | price change × volume | buy dips in force during uptrends | NONE | XRPUSD h1 (contrarian): holds, -41 bp after costs | GBPJPY 24h contra: -2.4 bp |
| IND-063 | Envelope | price vs a ±% band around an average | fade the bands or trade breakouts | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US30 24h follow: -7.0 bp |
| IND-064 | Guppy MMA | short vs long groups of EMAs | trade when the groups separate in one direction | NONE | LTCUSD h1 (contrarian): holds, -209 bp after costs | US30 24h follow: -10.0 bp |
| IND-065 | Linear regression position | distance from a 100-bar regression line | fade the channel edges | NONE | BCHUSD h1 (contrarian): holds, -54 bp after costs | USTEC 24h contra: +8.2 bp |
| IND-066 | McGinley Dynamic | self-adjusting average | price above it = bullish | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | US30 24h follow: -6.9 bp |
| IND-067 | Momentum | price minus price n bars ago | zero-line cross | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | US500 24h follow: -8.8 bp |
| IND-068 | Money Flow Index | volume-weighted RSI | buy below 20, sell above 80 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | BTCUSD 24h follow: +2.2 bp |
| IND-069 | Net Volume | up-volume minus down-volume | positive = buying pressure | NONE | LTCUSD h1 (contrarian): holds, -209 bp after costs | USTEC 24h follow: -1.7 bp |
| IND-070 | On-Balance Volume | running sum of signed volume | rising OBV confirms an uptrend; divergences | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | UKOIL 24h follow: -11.1 bp |
| IND-071 | PPO | MACD in percent | signal-line crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h contra: -2.5 bp |
| IND-072 | Price Volume Trend | running sum of % change × volume | confirm trends | NONE | BCHUSD h1 (contrarian): holds, -54 bp after costs | USOIL 24h contra: -16.6 bp |
| IND-073 | Rank Correlation Index | rank correlation of price with time (RCI) | buy when it turns up from −80 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | XAUUSD 24h follow: +7.0 bp |
| IND-074 | Relative Vigor Index | close vs open relative to range | signal-line crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -39 bp after costs | ETHUSD 24h contra: -19.6 bp |
| IND-075 | Relative Volatility Index | RSI computed on volatility | trend confirmation above/below 50 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | XAUUSD 24h follow: +2.8 bp |
| IND-076 | SMI Ergodic | double-smoothed momentum (TSI-like) | signal-line crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -40 bp after costs | USTEC 24h contra: -7.9 bp |
| IND-077 | Stochastic RSI | Stochastic applied to RSI | buy %K cross up from below 20 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | XAUUSD 24h follow: +5.0 bp |
| IND-078 | Stochastic Momentum Index | close vs mid of the range, smoothed | buy below −40, sell above +40 | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h follow: -6.5 bp |
| IND-079 | Smoothed MA slope | Wilder smoothed average | slope / crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | US500 24h contra: +4.2 bp |
| IND-080 | Technical Ratings | TradingView's buy/sell vote of 15 MAs and 11 oscillators | Strong Buy / Strong Sell readings | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | XAUUSD 24h follow: +10.3 bp |
| IND-081 | True Strength Index | double-smoothed momentum | signal-line and zero crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -41 bp after costs | USTEC 24h contra: -1.8 bp |
| IND-082 | Volatility Stop | ATR trailing stop on closes | flip signals | NONE | ETHUSD h1 (contrarian): same direction, not significant, -13 bp after costs | US30 24h follow: -1.8 bp |
| IND-083 | VWMA vs SMA | volume-weighted vs simple average | VWMA above SMA = volume backs the move | NONE | BCHUSD h1 (contrarian): same direction, not significant, -53 bp after costs | US500 24h contra: -0.3 bp |
| IND-084 | Williams Fractals | 5-bar swing highs/lows | buy breaks above the last up-fractal | NONE | LTCUSD h1 (contrarian): holds, -208 bp after costs | US30 24h follow: -1.7 bp |
| IND-085 | Woodies CCI | CCI 14 with turbo CCI 6 (Woodie's system) | zero-line rejects and trend lines on CCI | NONE | XRPUSD h1 (contrarian): holds, -41 bp after costs | XAUUSD 24h follow: +4.7 bp |
| IND-086 | Klinger Oscillator | long-term money flow from volume | signal-line crosses | NONE | XRPUSD h1 (contrarian): same direction, not significant, -40 bp after costs | US30 24h contra: +5.8 bp |
| IND-087 | Standard pivot points | yesterday's (H+L+C)/3 and support/resistance levels | buy above the pivot, targets at R1/R2 | NONE | BCHUSD h1 (contrarian): holds, -54 bp after costs | US500 24h contra: +4.6 bp |
| IND-088 | RSI divergence | price makes a new low but RSI doesn't | buy bullish divergence | NONE | USDJPY h24 (follow): same direction, not significant, +3 bp after costs | BNBUSD 24h follow: -23.5 bp |

## Built-ins without a direction, tested the way traders use them (batch 005)

These cannot predict direction on their own, so each was tested as the rule traders actually use it for (sources and exact rules in `PREREG.md`). The cells show the TEST-period result per trade after costs. For the first ten the unit is R (multiples of the 1.5-ATR stop); seasonality and moon are in bp per trade.

| Built-in, and how it is used | Gold | Oil | BTC | S&P 500 | EUR/USD | Decision |
|---|---|---|---|---|---|---|
| ATR (volatility breakout) | +0.00R | -0.22R | -0.07R | -0.01R | -0.16R | REJECTED |
| Bollinger Band Width (squeeze breakout) | -0.24R | +0.15R | -0.18R | -0.09R | +0.07R | REJECTED |
| Choppiness Index (chop→trend) | +0.11R | -0.11R | -0.07R | -0.24R | +0.01R | REJECTED |
| Mass Index (reversal bulge) | -0.07R | -0.05R | -0.11R | -0.13R | -0.21R | REJECTED |
| Volume / Relative Volume (spike follows candle) | +0.10R | -0.17R | +0.06R | -0.13R | -0.13R | REJECTED |
| Volume (climax fade) | -0.12R | -0.17R | -0.19R | -0.04R | -0.09R | REJECTED |
| Average Daily Range (exhaustion fade) | -0.76R | -0.26R | -0.20R | +0.28R | +0.16R | REJECTED |
| Historical Volatility (calm→breakout) | -0.15R | -0.02R | -0.27R | +0.01R | -0.06R | REJECTED |
| Volume Profile (value-area re-entry, 80% rule) | +0.19R | -0.31R | -0.12R | +0.05R | -0.13R | REJECTED |
| Zig Zag (causal swing break) | +0.11R | -0.03R | -0.14R | -0.16R | -0.22R | REJECTED |
| Seasonality (best/worst hour of week) | -0.89 bp | -13.09 bp | -9.75 bp | -2.22 bp | -1.50 bp | REJECTED |
| Moon Phases (Dichev–Janes) | -34.08 bp | +96.13 bp | -61.20 bp | -19.50 bp | +2.62 bp | REJECTED, WATCH |

## What cannot be tested at all, and why

- **Drawing tools** (Auto Fib Retracement/Extension, Auto Pitchfork, Auto Trendlines, Fib channels): their trading rules reduce to Fibonacci pullbacks and swing breaks. Those were tested as the OIL_FIB / ETH_FIB library rules and the swing, fractal and Zig Zag breaks here.
- **Zig Zag as drawn on TradingView** redraws its last line with future bars. Only the causal version (above) can be tested honestly.
- **Breadth** (Advance/Decline, Net Highs/Lows), **open interest** and **COT** need data that is not in the Exness feed.
- **Community scripts:** there are more than 100,000. The most liked (Squeeze Momentum, WaveTrend, QQE, SSL, UT Bot, Chandelier, Volumetric Order Blocks, SMC / FVG, Fibonacci tools, signal "buy/sell label" scripts) were tested in batch 003, STR-027 and the earlier library. Most others are re-mixes of the built-ins above.
