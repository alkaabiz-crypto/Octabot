---
title: TradingView batch 004 and best-market results
description: The remaining TradingView built-ins (all NONE) and a held-out test of which market each of 82 indicators works best in
sidebar_position: 2
---

# TradingView batch 004 + best market per indicator: results (2026-11-15)

Rules: [`PREREG.md`](PREREG.md) (commit 6b859610, before any computation). Script: `run_tv4.py`. Exness prices, 1h candles, costs 1.5 × the median spread.

## Bottom line

1. **The 40 remaining TradingView built-ins (IND-049 to IND-088) are all NONE** on gold, oil, BTC, the S&P 500 and EUR/USD. With batches 001–003, **every built-in TradingView indicator that gives a buy/sell direction has now been tested: 82 in all, and none is a usable signal.**
2. **"Which market does each indicator work best in"** (picked on 2023 → mid-2025, checked on July 2025 → now, across 33 markets and 3 horizons):
   - For **77 of 82 indicators, the "best market" was a small crypto coin (XRP, LTC, BCH, ETH) at 1 hour, used *backwards* (sell the buy signal).** This is one effect, the very short-term reversal found before (THE-017), not 77 different edges.
   - In 34 cases the reversal is still there statistically on new data (**HOLDS**). **But every one of them loses after costs** (−11 to −209 bp per trade), because the reversal is smaller than the spread on those coins.
   - Only 1 of the 82 picks is positive after costs on new data (RSI divergence on USD/JPY, 24 h, +3.4 bp, not significant).
3. **Exploratory (not pre-registered), "best market after costs":** choosing each indicator's market by after-cost profit on the old data instead:
   - every pick is a 24-hour horizon, mostly US indices (US30, USTEC, US500) and gold;
   - 27 of 82 are positive on new data, 55 negative;
   - **gold is the stand-out: all 10 indicators whose best market was gold stayed positive** (+1.6 to +12.0 bp per day). But buying and holding gold made +4.5 bp per day in the same period, and the differences are well within noise (standard error about 6–7 bp). They are mostly long during a strong gold rally.

**No indicator qualifies for a strategy or a forward test.**

## Every indicator: its best market and what happened on new data

Columns:
- **Best market (old data):** the market × horizon × direction with the strongest IC on 2023 → mid-2025.
- **TEST IC:** the IC of that pick on July 2025 → now, in the chosen direction.
- **TEST net bp:** after costs, per trade.
- **After-cost pick (exploratory):** the market chosen by after-cost profit on old data (24 h horizon), with its TEST net bp per day.

| ID | Indicator | Best market (old data) | TEST IC | TEST net bp | Verdict | After-cost pick (exploratory) | Its TEST net bp |
|---|---|---|---|---|---|---|---|
| IND-003 | KST (Know Sure Thing) | LTCUSD h1 contrarian | +0.014 | -209.4 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | +5.4 |
| IND-004 | Distance from session/daily VWAP | XRPUSD h1 contrarian | +0.025 | -41.2 | HOLDS | USDJPY follow | -0.1 |
| IND-005 | RSI (14, 2) | LTCUSD h1 contrarian | +0.048 | -208.4 | HOLDS | USTEC contra | +4.8 |
| IND-006 | MACD | XRPUSD h1 contrarian | +0.007 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | -2.5 |
| IND-007 | Moving-average trend (EMA 9/21, SMA 50/2 | BCHUSD h1 contrarian | +0.035 | -53.4 | HOLDS | US30 follow | -6.7 |
| IND-008 | Supertrend | LTCUSD h1 contrarian | +0.027 | -208.4 | HOLDS | USDJPY contra | +0.9 |
| IND-009 | Parabolic SAR | XRPUSD h1 contrarian | +0.004 | -40.9 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -1.8 |
| IND-010 | ADX / DMI | LTCUSD h1 contrarian | +0.029 | -208.9 | HOLDS | US30 follow | -5.7 |
| IND-011 | Donchian channel position | LTCUSD h1 contrarian | +0.053 | -208.6 | HOLDS | US30 follow | -4.2 |
| IND-012 | Ichimoku cloud | BCHUSD h1 contrarian | +0.035 | -53.4 | HOLDS | XAUUSD follow | +1.6 |
| IND-013 | Bollinger %B and squeeze | XRPUSD h1 contrarian | +0.014 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -7.0 |
| IND-014 | Stochastic | XRPUSD h1 contrarian | +0.007 | -41.7 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -11.4 |
| IND-015 | CCI | XRPUSD h1 contrarian | +0.012 | -41.3 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -3.9 |
| IND-016 | Williams %R | XRPUSD h1 contrarian | +0.015 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -12.6 |
| IND-017 | Williams Vix Fix | XRPUSD h1 contrarian | +0.003 | -40.8 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | +5.2 |
| IND-020 | 20-day momentum (time-series) | BCHUSD h1 contrarian | +0.038 | -53.7 | HOLDS | XAUUSD follow | +3.0 |
| IND-022 | Aroon oscillator (25) | ETHUSD h1 contrarian | +0.009 | -13.2 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -10.7 |
| IND-023 | Vortex (14) | XRPUSD h1 contrarian | +0.011 | -41.0 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -12.0 |
| IND-024 | TRIX (15) | BCHUSD h4 contrarian | +0.035 | -53.7 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -14.1 |
| IND-025 | KAMA slope | LTCUSD h1 contrarian | +0.051 | -208.0 | HOLDS | USTEC follow | -13.8 |
| IND-026 | Williams Alligator | BCHUSD h4 contrarian | +0.022 | -55.0 | SAME DIRECTION, NOT SIGNIFICANT | BTCUSD follow | -24.4 |
| IND-027 | Hull MA (55) slope | ETHUSD h1 contrarian | +0.017 | -12.9 | SAME DIRECTION, NOT SIGNIFICANT | AUDUSD contra | +0.0 |
| IND-028 | Keltner position | XRPUSD h1 contrarian | +0.018 | -41.0 | SAME DIRECTION, NOT SIGNIFICANT | USDJPY follow | +1.0 |
| IND-029 | Heikin-Ashi colour run | XRPUSD h1 contrarian | +0.021 | -40.6 | HOLDS | US30 follow | -6.6 |
| IND-030 | Awesome Oscillator | BCHUSD h1 contrarian | +0.025 | -53.7 | HOLDS | AUDUSD contra | -2.4 |
| IND-031 | Ultimate Oscillator | XRPUSD h1 contrarian | +0.019 | -40.2 | SAME DIRECTION, NOT SIGNIFICANT | US500 contra | -1.7 |
| IND-032 | Rate of change (12) | XRPUSD h1 contrarian | +0.017 | -40.5 | SAME DIRECTION, NOT SIGNIFICANT | US500 follow | -7.0 |
| IND-033 | Fisher transform (10) | XRPUSD h1 contrarian | +0.003 | -41.2 | SAME DIRECTION, NOT SIGNIFICANT | XAUUSD follow | +5.1 |
| IND-034 | Elder ray (13) | XRPUSD h1 contrarian | +0.018 | -41.0 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -5.8 |
| IND-036 | Squeeze Momentum [LazyBear] | ETHUSD h1 contrarian | +0.021 | -12.6 | HOLDS | XAUUSD follow | +11.2 |
| IND-037 | WaveTrend [LazyBear] | XRPUSD h1 contrarian | +0.011 | -40.6 | SAME DIRECTION, NOT SIGNIFICANT | US30 contra | -2.1 |
| IND-038 | QQE Mod | XRPUSD h1 contrarian | +0.007 | -40.4 | SAME DIRECTION, NOT SIGNIFICANT | US500 contra | -0.6 |
| IND-039 | SSL channel (10) | XRPUSD h1 contrarian | +0.011 | -40.9 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -2.0 |
| IND-040 | UT Bot alerts | XRPUSD h1 contrarian | +0.001 | -41.4 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -0.1 |
| IND-041 | Chandelier exit (22,3) | ETHUSD h1 contrarian | +0.020 | -12.5 | HOLDS | USTEC contra | +11.8 |
| IND-042 | Schaff Trend Cycle | XRPUSD h1 contrarian | -0.001 | -41.0 | REVERSED | US30 follow | +1.6 |
| IND-043 | Coppock curve | LTCUSD h1 contrarian | +0.031 | -208.1 | HOLDS | US30 follow | -4.0 |
| IND-044 | Detrended price oscillator (20) | XRPUSD h4 follow | +0.024 | -36.9 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | +3.6 |
| IND-045 | Least-squares MA (50) slope | BCHUSD h1 contrarian | +0.039 | -53.4 | HOLDS | US500 contra | +3.6 |
| IND-046 | Connors RSI | BTCUSD h1 contrarian | +0.038 | -10.9 | HOLDS | ETHUSD contra | -15.9 |
| IND-047 | Laguerre RSI | XRPUSD h1 contrarian | +0.009 | -41.6 | SAME DIRECTION, NOT SIGNIFICANT | US500 contra | -1.6 |
| IND-048 | Choppiness-filtered momentum | XRPUSD h1 contrarian | +0.015 | -38.7 | SAME DIRECTION, NOT SIGNIFICANT | BTCUSD follow | -65.6 |
| IND-049 | ALMA slope | XRPUSD h1 contrarian | +0.018 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -14.8 |
| IND-050 | Balance of Power | XRPUSD h1 contrarian | +0.005 | -41.7 | SAME DIRECTION, NOT SIGNIFICANT | XAUUSD follow | +12.0 |
| IND-051 | BBTrend | BCHUSD h4 contrarian | +0.027 | -55.7 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -1.5 |
| IND-052 | Chaikin Money Flow | BTCUSD h1 contrarian | +0.027 | -10.7 | HOLDS | DE30 follow | -6.5 |
| IND-053 | Chaikin Oscillator | BTCUSD h1 contrarian | +0.036 | -10.5 | HOLDS | USTEC follow | +2.2 |
| IND-054 | Accumulation/Distribution | XRPUSD h1 contrarian | +0.013 | -40.6 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -12.4 |
| IND-055 | Chande Kroll Stop | ETHUSD h1 contrarian | +0.026 | -12.9 | HOLDS | US30 follow | -5.3 |
| IND-056 | Chande Momentum Osc. | XRPUSD h1 contrarian | +0.011 | -40.5 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -4.6 |
| IND-057 | Chop Zone | BCHUSD h1 contrarian | +0.045 | -53.5 | HOLDS | US500 contra | +3.8 |
| IND-058 | Trend Strength Index | XRPUSD h1 contrarian | +0.009 | -41.0 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -15.5 |
| IND-059 | DEMA slope | XRPUSD h1 contrarian | +0.023 | -40.0 | HOLDS | ETHUSD contra | -21.5 |
| IND-060 | TEMA slope | XRPUSD h1 contrarian | +0.024 | -40.6 | HOLDS | US30 contra | -4.5 |
| IND-061 | Ease of Movement | LTCUSD h1 contrarian | +0.033 | -208.6 | HOLDS | GBPJPY contra | -2.5 |
| IND-062 | Elder Force Index | XRPUSD h1 contrarian | +0.021 | -40.8 | HOLDS | GBPJPY contra | -2.4 |
| IND-063 | Envelope | XRPUSD h1 contrarian | +0.015 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -7.0 |
| IND-064 | Guppy MMA | LTCUSD h1 contrarian | +0.034 | -208.9 | HOLDS | US30 follow | -10.0 |
| IND-065 | Linear regression position | BCHUSD h1 contrarian | +0.032 | -53.6 | HOLDS | USTEC contra | +8.2 |
| IND-066 | McGinley Dynamic | LTCUSD h1 contrarian | +0.053 | -208.2 | HOLDS | US30 follow | -6.9 |
| IND-067 | Momentum | LTCUSD h1 contrarian | +0.039 | -208.1 | HOLDS | US500 follow | -8.8 |
| IND-068 | Money Flow Index | XRPUSD h1 contrarian | +0.006 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | BTCUSD follow | +2.2 |
| IND-069 | Net Volume | LTCUSD h1 contrarian | +0.026 | -209.4 | HOLDS | USTEC follow | -1.7 |
| IND-070 | On-Balance Volume | XRPUSD h1 contrarian | +0.013 | -41.4 | SAME DIRECTION, NOT SIGNIFICANT | UKOIL follow | -11.1 |
| IND-071 | PPO | XRPUSD h1 contrarian | +0.007 | -41.2 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | -2.5 |
| IND-072 | Price Volume Trend | BCHUSD h1 contrarian | +0.033 | -53.9 | HOLDS | USOIL contra | -16.6 |
| IND-073 | Rank Correlation Index | XRPUSD h1 contrarian | +0.011 | -40.9 | SAME DIRECTION, NOT SIGNIFICANT | XAUUSD follow | +7.0 |
| IND-074 | Relative Vigor Index | XRPUSD h1 contrarian | +0.017 | -39.0 | SAME DIRECTION, NOT SIGNIFICANT | ETHUSD contra | -19.6 |
| IND-075 | Relative Volatility Index | XRPUSD h1 contrarian | +0.011 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | XAUUSD follow | +2.8 |
| IND-076 | SMI Ergodic | XRPUSD h1 contrarian | +0.013 | -40.1 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | -7.9 |
| IND-077 | Stochastic RSI | XRPUSD h1 contrarian | +0.007 | -40.9 | SAME DIRECTION, NOT SIGNIFICANT | XAUUSD follow | +5.0 |
| IND-078 | Stochastic Momentum Index | XRPUSD h1 contrarian | +0.007 | -41.0 | SAME DIRECTION, NOT SIGNIFICANT | USTEC follow | -6.5 |
| IND-079 | Smoothed MA slope | XRPUSD h1 contrarian | +0.019 | -41.2 | SAME DIRECTION, NOT SIGNIFICANT | US500 contra | +4.2 |
| IND-080 | Technical Ratings | LTCUSD h1 contrarian | +0.038 | -208.2 | HOLDS | XAUUSD follow | +10.3 |
| IND-081 | True Strength Index | XRPUSD h1 contrarian | +0.005 | -41.1 | SAME DIRECTION, NOT SIGNIFICANT | USTEC contra | -1.8 |
| IND-082 | Volatility Stop | ETHUSD h1 contrarian | +0.017 | -13.0 | SAME DIRECTION, NOT SIGNIFICANT | US30 follow | -1.8 |
| IND-083 | VWMA vs SMA | BCHUSD h1 contrarian | +0.019 | -53.5 | SAME DIRECTION, NOT SIGNIFICANT | US500 contra | -0.3 |
| IND-084 | Williams Fractals | LTCUSD h1 contrarian | +0.031 | -208.5 | HOLDS | US30 follow | -1.7 |
| IND-085 | Woodies CCI | XRPUSD h1 contrarian | +0.026 | -40.8 | HOLDS | XAUUSD follow | +4.7 |
| IND-086 | Klinger Oscillator | XRPUSD h1 contrarian | +0.012 | -39.8 | SAME DIRECTION, NOT SIGNIFICANT | US30 contra | +5.8 |
| IND-087 | Standard pivot points | BCHUSD h1 contrarian | +0.040 | -53.9 | HOLDS | US500 contra | +4.6 |
| IND-088 | RSI divergence | USDJPY h24 follow | +0.078 | +3.4 | SAME DIRECTION, NOT SIGNIFICANT | BNBUSD follow | -23.5 |
## Notes

- **Part A (5 markets, IND test):** 40 indicators × 5 markets × 4 horizons, all NONE. As in earlier batches, most trend-type indicators are slightly *negative* at 1–4 h on gold, oil and BTC (short-term reversal). Volume-based indicators (Chaikin, MFI, OBV, Klinger and others) use Exness tick counts.
- **Not testable as a direction signal:** ATR, ADR, Historical Volatility, BB Width, Choppiness, Mass Index and the volume-level indicators (no direction); drawing tools (auto Fib, pitchfork, trendlines, volume profile); Zig Zag (it repaints with future bars); breadth, open interest and COT (no data). See `PREREG.md`.
- **Community scripts:** TradingView has more than 100,000. The most popular ones were covered in batch 003 and STR-027, and earlier scans tested about 2,950 variants. Testing literally all of them is not possible, and most are re-mixes of the built-ins tested here.
- Files: `results_A.json` (Part A), `results_B.json` (pre-registered picks), `results_B_exploratory_net.json` (after-cost picks). The 7,872 individual market × horizon cells are kept in scratch, not committed.
