---
title: STR-032 GainzAlgo-style results
description: Engulfing candle + RSI condition with TP/SL (public GainzAlgo logic); rejected on all markets
sidebar_position: 2
---

# STR-032 results (2026-11-17): REJECTED on all 5 markets, both variants

Rules: [`PREREG.md`](PREREG.md) (commit caa44e75). Script: `run_str032.py`; numbers: `results.json`. **This is an approximation from GainzAlgo's publicly known logic, not GainzAlgo itself.** The real scripts have been removed from TradingView.

## Variant A (k = 50: engulfing + RSI on the "right" side of 50): mean R per trade after costs (win %)

| Market | EARLY | TRAIN | VALIDATION | TEST | TEST p vs random |
|---|---|---|---|---|---|
| Gold | −0.27 (27%) | −0.11 (32%) | −0.07 (33%) | −0.16 (29%) | 0.87 |
| Oil | −0.17 (32%) | −0.16 (34%) | +0.00 (39%) | +0.00 (38%) | 0.20 |
| BTC | −0.16 (33%) | −0.04 (38%) | −0.21 (31%) | −0.12 (35%) | 0.47 |
| S&P 500 | – | −0.06 (34%) | −0.31 (25%) | +0.15 (41%) | 0.08 |
| EUR/USD | – | −0.12 (33%) | −0.10 (33%) | +0.14 (41%) | 0.03 |

## Variant B (k = 30: engulfing at an RSI extreme)

Too rare to judge: 3–23 trades per period. It is negative or mixed everywhere.

## Reading

- **No market is positive in every period.** The two TEST positives (S&P 500 and EUR/USD) followed losing TRAIN and VALIDATION periods. EUR/USD p = 0.03 is not significant after correcting for 10 tests.
- **Win rates of 25–41% with a 2R target lose after costs.** A 2R target needs about 36% winners just to break even before costs.
- **What this does not test:** the paid GainzAlgo V2 Alpha. Its full rules are private. The only fair test of the real product is prospective screenshots of its signals, scored on Exness prices (the SIG method).
