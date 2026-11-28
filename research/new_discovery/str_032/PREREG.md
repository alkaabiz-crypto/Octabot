---
title: STR-032 GainzAlgo-style pre-registration
description: An approximation of GainzAlgo V2 Alpha from its publicly known logic (engulfing candle + RSI condition, TP/SL, no repeated signals)
sidebar_position: 1
---

# STR-032: "GainzAlgo-style" engulfing + RSI (pre-registration, 2026-11-17, before any computation)

**Why an approximation.** The user asked to test GainzAlgo V2 Alpha, with permission to reach TradingView. Every GainzAlgo script page on TradingView (V2 Alpha IDs EpDRTgnC, QBeXchhm, DvMPRFU2; V2 Proficient H1NJOM1j; Pro StUgp6lM) now returns 404, and a TradingView search for "gainzalgo" finds no script. The real code is therefore unavailable.

**What is publicly known** (search snippets of the former open-source listing, and vendor pages):
- a SELL needs a bearish engulfing candle and `rsi > 100 - rsi_index_param`; a BUY mirrors this;
- it shows TP and SL levels;
- it has a "disable repeating signals" option.

The vendor also mentions EMA, ATR and ADX, without rules. This test uses only the known parts, so it is **not** GainzAlgo itself.

## Rules

- **Data:** Exness 1h candles (mid prices) for XAUUSDm, USOILm, BTCUSDm, US500m, EURUSDm. Periods EARLY / TRAIN / VALIDATION / TEST.
- **BUY signal at a 1h close:** bullish engulfing (this candle is up, the previous is down, this body covers the previous body: open ≤ previous close and close ≥ previous open) and RSI 14 < k. **SELL:** the mirror (bearish engulfing and RSI 14 > 100 − k).
- **k:** the default is unknown, so two variants are reported: **k = 50** (A) and **k = 30** (B).
- **Disable repeating signals:** a BUY is ignored until a SELL has occurred since the last BUY, and vice versa.
- **Entry and management:** next 1h open. SL 1.5 × ATR14, TP 3 × ATR14 (2R), 48 h time exit, one position at a time (the run_tv3 engine, unchanged).
- **Costs:** 1.5 × (stress 3 ×) the median spread.
- **Benchmark:** random entries with the same count, sides and management.
- **Decision:** SCREEN-PASS if positive in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over the 10 (variant × market) tests, and ≥ 30 TEST trades. Otherwise WATCH (positive in every period) or REJECTED.
