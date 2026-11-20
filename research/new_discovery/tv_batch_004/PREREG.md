---
title: TradingView batch 004 and best-market study pre-registration
description: The remaining TradingView built-in indicators, and a held-out test of which market each indicator works best in
sidebar_position: 1
---

# TradingView batch 004 + "best market per indicator": pre-registration (2026-11-15, before any computation)

User request: "search the indicators for which market does it do best in and I want every indicator in TradingView tested".

## What "every indicator" can mean here

TradingView has about 100 built-in indicators (its Help Center lists about 208 built-in articles, including drawing tools and variants) and well over 100,000 community scripts. tradingview.com is not reachable from this environment, so the list below is the standard built-in set. **Every built-in that gives a buy/sell direction from price or volume is tested.** The following cannot be tested as a direction signal and are listed as such:

- **Volatility or volume level only (no direction):** ATR, ADR, Historical Volatility, Bollinger Band Width, Choppiness Index, Mass Index, Volume, Volume Oscillator, Relative Volume at Time, 24-hour Volume. Volatility forecasting was tested separately (IND-018).
- **Drawing or chart tools:** Auto Fib Retracement/Extension, Auto Pitchfork, Auto Trendlines, Volume Profile (all variants), Visible Average Price, Linear Regression Channel drawing (tested as a position value instead), Multi-Time Period Charts, Moon Phases, Seasonality.
- **Repaints (uses future bars):** Zig Zag. Not testable causally.
- **Needs data we do not have:** Advance/Decline Line and Ratio, Net Highs/Lows (stock-market breadth); Open Interest; COT; Correlation Coefficient and Ratio (needs a second symbol, partly covered by earlier cross-market studies).
- **Already tested (batches 001–003):** RSI, MACD, EMA/SMA cross, Supertrend, Parabolic SAR, ADX/DMI, Donchian, Ichimoku, Bollinger %B, Stochastic, CCI, Williams %R, KST, VWAP, Aroon, Vortex, TRIX, KAMA, Williams Alligator, Hull MA, Keltner, Heikin-Ashi, Awesome Oscillator, Ultimate Oscillator, ROC, Fisher Transform, Bull Bear Power (Elder ray), Connors RSI, Coppock Curve, DPO, Least Squares MA, and the community scripts in batch 003.

**Volume:** Exness gives tick counts (number of price updates) instead of traded volume. Volume-based indicators use tick counts, the usual substitute for CFDs and forex.

## Part A: new built-ins (IND-049 to IND-088), TradingView default settings

ALMA (9, 0.85, 6) slope; Balance of Power (14); BBTrend (20, 50); Chaikin Money Flow (20); Chaikin Oscillator (3, 10); Accumulation/Distribution 14-bar change; Chande Kroll Stop state (10, 1, 9); Chande Momentum Oscillator (9); Chop Zone (EMA 34 angle); Trend Strength Index (14); DEMA (9) slope; TEMA (9) slope; Ease of Movement (14); Elder Force Index (13); Envelope position (20, 10%); Guppy MMA spread; Linear regression position (100); McGinley Dynamic (14) position; Momentum (10); Money Flow Index (14); Net Volume (14); OBV vs its EMA 20; PPO histogram (12, 26, 9); Price Volume Trend 14-bar change; Rank Correlation Index (9); Relative Vigor Index (10) minus signal; Relative Volatility Index (10, 14); SMI Ergodic Oscillator (5, 20, 5); Stochastic RSI (14, 14, 3, 3); Stochastic Momentum Index (10, 3, 3); Smoothed MA (7) slope; Technical Ratings (the average of TradingView's moving-average and oscillator votes); True Strength Index (25, 13) minus signal; Volatility Stop state (20, 2); VWMA (20) minus SMA (20); Williams Fractals breakout state; Woodies CCI (turbo 6); Klinger Oscillator (34, 55, 13) minus signal; daily standard pivot position; RSI divergence (pivots 5/5, range 5–60 bars, held 10 bars).

Test: the IND batch 001 IC machinery, unchanged, on the same five markets (gold, oil, BTC, S&P 500, EUR/USD), with the same verdicts.

## Part B: which market does each indicator work best in (held-out)

- **Indicators:** every price/volume indicator from batches 001–004 (about 83).
- **Markets:** all 33 Exness markets with 15m data (metals, oil, gas, crypto, indices, forex).
- **Horizons:** 1, 4 and 24 hours.
- **Selection (on old data only):** for each indicator, compute the IC on TRAIN + VALIDATION (2023-01 → 2025-06) for every market × horizon. The pick is the market × horizon with the largest |t|. The sign is kept, so a contrarian use counts.
- **Check (on new data):** the IC of that one pick on TEST (2025-07 → now), in the direction chosen.
  - **HOLDS:** same direction, and one-sided p ≤ 0.05 after BH over all indicators.
  - **SAME DIRECTION, NOT SIGNIFICANT** or **REVERSED** otherwise.
- **After costs (reported, not deciding):** a trade in the direction of sign(indicator) at each sample point for h hours, minus 1.5 × that market's median spread. TEST net bp per trade.
- Picking the best of about 200 market × horizon cells on old data always produces impressive-looking numbers. Only the TEST column counts.

No parameter is changed after results are seen. All results are reported.
