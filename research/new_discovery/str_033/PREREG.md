---
title: STR-033 Quantlab NY-open candle pre-registration
description: First 5-minute candle after the New York open, direction filtered by the 12 EMA, held 6 hours (Instagram quant_labde claim)
sidebar_position: 1
---

# STR-033: "QuantLab" first 5-minute candle + EMA 12 (pre-registration, 2026-11-17, before any computation)

## Source

An Instagram reel by **quant_labde**, from a screenshot the user sent on 2026-11-17. The caption:

> "Our algo waits for the New York open, reads the first 5-minute candle and trades the direction. Above the 12 EMA: long. Below: short. Since 2019: +505.8% at 1% risk per trade. And it's running live on a funded account right now."

The hashtags (#nasdaq, #futurestrading) point to the Nasdaq 100. The full code is offered only via comments or a bio link, so the ambiguous details are fixed here before any data is seen. Three variants are reported.

## Data

- **Market:** Exness USTECm (Nasdaq 100 CFD). 1-minute bid/ask built from the Exness tick archive, from the first available month (2019-07/08) to 2026-10-28. Raw data stays out of the repository.
- **Prices:** mid prices for signals; costs from the actual spread.

## Rules

- **NY open:** 09:30 America/New_York (follows US daylight saving). **First candle:** the 5-minute candle 09:30–09:35, from 1-minute bars.
- **EMA 12:** on continuous 5-minute closes (all Exness trading hours). It is read at the 09:35 close.
- **Signal:**
  - **A (primary):** LONG if the first candle is bullish (close > open) **and** closes above EMA 12. SHORT if bearish **and** closes below EMA 12. Otherwise no trade.
  - **B:** direction from the close vs EMA 12 only (candle colour ignored).
- **Entry:** the 09:35 1-minute open.
- **Stop** (needed for "1% risk"): the opposite end of the first 5-minute candle (its low for a long, high for a short). Checked on 1-minute bars; a gap through it fills at the open.
  - Variant **C** = A with no stop.
- **Exit:** 6 hours after entry (the 15:35 New York 1-minute open), or the stop.
- **Costs:** the round-trip spread at entry and exit (the actual quoted spread at those minutes), stress = 2 ×.
- **Results reported:**
  - R per trade, where risk = |entry − stop| plus the spread at entry; days with risk below 0.02% of price are skipped;
  - per-trade % (for C);
  - compounded equity at 1% risk per trade from 2019, to compare with the +505.8% claim;
  - win rate and maximum drawdown.

## Benchmarks

- **Random direction:** the same days, entry, exit and stop distance, but a random side; 1,000 sets. p = share of sets with a mean ≥ the actual mean.
- **Always long:** the same days with a long trade. The Nasdaq rose strongly in 2019–2026, so a "long-most-days" rule can look good just from the trend.

## Decision (per variant)

- **SCREEN-PASS:** mean R > 0 in every period (EARLY 2019–2022, TRAIN, VALIDATION, TEST), TEST stress mean > 0, TEST p ≤ 0.05 vs random direction after BH over the three variants, ≥ 30 TEST trades → forward paper test.
- **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.
- **Source screenshot:** kept out of this public repository, because it shows other Instagram users' names and pictures. SHA-256 8dad3f7a5701b93d20cffccdc4282d7416deee0919b1fb8b239fa19be39636a5.
