---
title: TradingView batch 005 results
description: Non-direction built-ins tested as traders use them, 3-to-5-indicator combinations and ensembles; all rejected
sidebar_position: 2
---

# TradingView batch 005 results (2026-11-15)

Rules: [`PREREG.md`](PREREG.md) (commit cbede55a, before any computation). Script: `run_tv5.py`; numbers: `results.json`. The full review of every indicator is in [`INDICATOR_REVIEW.md`](INDICATOR_REVIEW.md) (built by `make_review.py` from the committed results).

## Bottom line

**120 tests (24 rules × 5 markets): 0 SCREEN-PASS, 118 REJECTED, 2 WATCH. No forward test follows.**

- **The "no direction" built-ins, used the way traders use them** (ATR breakout, Bollinger-width squeeze, Choppiness transition, Mass Index bulge, volume spikes and climaxes, ADR fade, low-volatility breakout, volume-profile 80% rule, causal Zig Zag, hour-of-week seasonality, moon phases): **all rejected.** Per-market results are in the review table.
  - The volume spike rule on BTC beat random entries in TEST (p = 0.004), but it lost in every earlier period.
  - The moon rule on EUR/USD was positive in all three periods (+2.6 to +7.0 bp per half-cycle), so it is WATCH. It has only 33 trades in TEST, p = 0.44, and is far too small to matter.
- **More indicators at once did not help.**
  - The 3 → 4 → 5 indicator stack (031a → b → c) got *worse* on every market as filters were added: fewer trades and lower averages (gold TEST +0.09R → −0.55R → −0.67R).
  - "One from each category" (trend + momentum + volume + volatility + structure; 031d/f), all 5 oscillators oversold at once (031e), and the vote of all 82 indicators (031g) were all negative or indistinguishable from random entries.
  - The data-chosen top 5 (031i/j) were chosen on TRAIN only. On US500 at 4 hours they were positive in every period (WATCH; TEST +0.08R, p = 0.07). Everywhere else they lost on new data. Almost all the indicators selected were used *backwards*: the short-term reversal again.

## TEST mean R per trade (after primary costs) for the combinations

| Rule | Gold | Oil | BTC | S&P 500 | EUR/USD |
|---|---|---|---|---|---|
| 031a 3 ind. (EMA 50/200 + RSI + OBV) | +0.09 | −0.07 | −0.13 | −0.01 | −0.16 |
| 031b 4 ind. (+ ADX) | −0.55 | −0.18 | −0.28 | +0.01 | −0.05 |
| 031c 5 ind. (+ VWAP) | −0.67 | −0.29 | −0.16 | +0.09 | +0.19 |
| 031d 5 categories, all agree | −0.00 | −0.02 | −0.16 | −0.10 | −0.15 |
| 031e 5 oscillators oversold | −0.18 | −0.24 | −0.06 | +0.05 | +0.24 |
| 031f 4 of 5 categories | +0.08 | −0.13 | −0.11 | +0.06 | −0.18 |
| 031g all 82 vote | +0.03 | −0.21 | −0.16 | −0.10 | −0.10 |
| 031h Donchian + volume + MFI | +0.01 | −0.10 | −0.07 | −0.21 | −0.21 |
| 031i data top-5 (4 h) | −0.11 | −0.09 | −0.20 | +0.08 | −0.02 |
| 031j data top-5 (24 h) | −0.16 | −0.37 | −0.15 | −0.07 | −0.00 |

The isolated positives (e.g. EUR/USD 031c +0.19R on 14 trades, 031e +0.24R) lost in the earlier periods and are within what 120 tests produce by chance.

## Checks

- **No look-ahead:** prefix invariance passed. Every signal of all 22 trade rules on the first 90% of gold's history is identical to the full-history run.
- **Volume:** Exness tick counts. BTC tick counts are sparse before 2023, so the BTC volume rules have few EARLY trades.
