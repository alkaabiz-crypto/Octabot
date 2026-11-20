---
title: STR-043 value-area (volume profile) strategy pre-registration
description: The two value-area scenarios from an Arabic Instagram reel (soualium): VAL/VAH wick rejection, and value-area breakout + FVG retest
sidebar_position: 1
---

# STR-043: "Value Area" reel, soualium (pre-registration, 2026-11-20, before any computation)

## Source

Two screen recordings of an Instagram reel by **soualium**, titled «أسرار "Value Area": كيف تتداول مثل المحترفين» ("Secrets of the Value Area: how to trade like the pros"), sent by the user on 2026-11-20.

The Arabic narration was transcribed locally with Whisper (small). In translation:
- Open TradingView, choose **Fixed Range Volume Profile**, and select the move **from the bottom to the top**.
- Make sure **VAH and VAL** are enabled. The area between them is the **value area**, where about **70% of volume** traded.
- **Scenario 1:** if price drops **below the value area low**, then comes back quickly with a **long lower wick** (a clear rejection of lower prices), **buy**, and **target the opposite edge of the value area**.
- **Scenario 2** ("the one most people miss, and the strongest"): if price does **not** bounce but **breaks the value area strongly**, leaving a **bearish fair value gap**, **do not enter directly**. **Wait** for price to **come back and test the gap**. If it touches it with a wick and rejects it, **sell**.
- The video ends by advertising the creator's auto-trading platform. Its "volume confirmation" step is not specified, so it is not modelled.

## Operational rules (fixed now; 1h signals, 15m execution)

- **Data:**
  - BTC, ETH: Binance with real volume, 2018 →.
  - Gold, oil: Exness with tick volume, long history.
  - S&P 500: Exness US500m with tick volume, 2023 →.
- **The move ("from the bottom to the top"):** swings with pivot length 10 on 1h, each confirmed 10 bars after it.
  - When a swing high is confirmed after a confirmed swing low, the profile covers that low → high (an up move).
  - When a swing low is confirmed after a swing high, it covers high → low (a down move).
  - The newest confirmed move replaces the previous profile. A profile is used for at most 120 1h bars after confirmation.
- **Volume profile:** 50 price bins over the move's range. Each 1h bar's volume is spread evenly over the bins its high–low covers.
  - **POC** = the bin with the most volume.
  - **Value area** = grow from the POC, adding the neighbouring bin with more volume, until it holds ≥ 70% of the volume. VAL is its bottom edge and VAH its top edge.
- **S1, wick rejection (LONG; SHORT mirrors at VAH):**
  - signal: a 1h candle with low < VAL and close > VAL, whose lower wick (min(open, close) − low) is ≥ 50% of its range;
  - entry: the next 1h open;
  - stop: candle low − 0.1 × ATR14;
  - target: VAH (skipped if the target is not above the entry).
- **S2, breakout + FVG retest (SHORT; LONG mirrors above VAH):**
  - **breakdown:** a 1h close below VAL by ≥ 0.5 × ATR14;
  - **bearish FVG:** a gap between bar k−2's low and bar k's high (high[k] < low[k−2]) formed from the breakdown bar to 2 bars after it;
  - **retest:** within the next 24 bars, a candle whose high reaches into the gap (≥ high[k]) and closes back below it (< high[k]);
  - entry: the next 1h open;
  - stop: max(retest high, gap top low[k−2]) + 0.1 × ATR14;
  - target: 2R (the video gives no target for S2).
- **Management (15m candles):** stop checked first; the target cannot hit on the entry candle; 72 h time exit; one position at a time. Skip if risk < 0.15% of price.
- **Costs:** BTC/ETH 0.05% per side (stress 0.20%); Exness 1.5 × median spread (stress 3 ×).
- **Benchmark:** random entries with the same count, sides, risk % and target distance, 1,000 sets.
- **Decision:**
  - **SCREEN-PASS:** mean R > 0 in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over the 10 (scenario × market) tests, and ≥ 30 TEST trades.
  - **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.
- **Look-ahead:** a prefix-invariance check.
