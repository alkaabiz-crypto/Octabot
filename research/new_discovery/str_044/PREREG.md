---
title: STR-044 liquidity-sweep entry pre-registration
description: "That stop hunt is your entry" (keepssy_fx, Instagram): buy after a sweep of equal lows, sell after a sweep of equal highs
sidebar_position: 1
---

# STR-044: liquidity-sweep entry (pre-registration, 2026-11-20, before any computation)

## Source

The Instagram reel from the user's first link (2026-11-17), readable now: **keepssy_fx**, "Lesson 06: Liquidity Entry" (#marketstructure #smc #fvg #liquidity).
- The video needs a login.
- Its cover reads: **"That stop hunt is your entry: Liquidity sweep"**, with a chart of **equal lows with stop-losses (SL) below them**, a **sweep** below that level, then a rally.
- This is a stand-alone version of step 1 of STR-041, without its structure-shift, dominance and OTE conditions.

## Rules (1h signals, 15m execution; LONG shown, SHORT mirrors with equal highs)

- **Data:**
  - BTC, ETH: Binance with real volume, 2018 →.
  - Gold, oil: Exness, long history.
  - S&P 500: Exness US500m, 2023 →.
- **Swings:** pivot length 5 on 1h (confirmed 5 bars after).
- **Equal lows (liquidity pool):** at least two confirmed swing lows within the last 100 1h bars whose lows are within 0.1 × ATR14 of each other. The pool level = the lowest of them. A pool is used once.
- **Sweep entry:** a 1h candle trades below the pool level and closes back above it → **BUY at the next 1h open**.
- **Stop:** the sweep candle's low − 0.1 × ATR14. **Target:** 2R. **Time exit:** 72 h. Stop checked first; no target on the entry candle; one position at a time. Skip if risk < 0.15% of price.
- **Variant B:** any single confirmed swing low (no "equal lows" requirement). It shows whether the equal-lows condition adds anything.
- **Costs:** BTC/ETH 0.05% per side (stress 0.20%); Exness 1.5 × median spread (stress 3 ×).
- **Benchmark:** random entries with the same count, sides, risk % and 2R target, 1,000 sets.
- **Decision:**
  - **SCREEN-PASS:** mean R > 0 in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over 10 (variant × market) tests, and ≥ 30 TEST trades.
  - **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.
- **Look-ahead:** a prefix-invariance check.
