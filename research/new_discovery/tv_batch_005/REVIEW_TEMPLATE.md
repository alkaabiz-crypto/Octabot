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
{{ROWS}}

## Built-ins without a direction, tested the way traders use them (batch 005)

These cannot predict direction on their own, so each was tested as the rule traders actually use it for (sources and exact rules in `PREREG.md`). The cells show the TEST-period result per trade after costs. For the first ten the unit is R (multiples of the 1.5-ATR stop); seasonality and moon are in bp per trade.

| Built-in, and how it is used | Gold | Oil | BTC | S&P 500 | EUR/USD | Decision |
|---|---|---|---|---|---|---|
{{NONDIR}}

## What cannot be tested at all, and why

- **Drawing tools** (Auto Fib Retracement/Extension, Auto Pitchfork, Auto Trendlines, Fib channels): their trading rules reduce to Fibonacci pullbacks and swing breaks. Those were tested as the OIL_FIB / ETH_FIB library rules and the swing, fractal and Zig Zag breaks here.
- **Zig Zag as drawn on TradingView** redraws its last line with future bars. Only the causal version (above) can be tested honestly.
- **Breadth** (Advance/Decline, Net Highs/Lows), **open interest** and **COT** need data that is not in the Exness feed.
- **Community scripts:** there are more than 100,000. The most liked (Squeeze Momentum, WaveTrend, QQE, SSL, UT Bot, Chandelier, Volumetric Order Blocks, SMC / FVG, Fibonacci tools, signal "buy/sell label" scripts) were tested in batch 003, STR-027 and the earlier library. Most others are re-mixes of the built-ins above.
