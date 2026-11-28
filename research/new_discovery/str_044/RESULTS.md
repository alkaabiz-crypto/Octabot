---
title: STR-044 liquidity-sweep entry results
description: "That stop hunt is your entry": buying after a sweep of equal lows (and selling after a sweep of equal highs) loses on BTC, ETH, gold, oil and the S&P 500
sidebar_position: 2
---

# STR-044 results (2026-11-20): REJECTED, both variants, all 5 markets

Rules: [`PREREG.md`](PREREG.md) (commit eac0a815). Script: `run_str044.py`; numbers: `results.json`.

## Mean R per trade after costs (win % in brackets), 2R target

| Variant | Market | to 2022 | 2023→mid-2024 | mid-2024→mid-2025 | Jul 2025→now | TEST p vs random |
|---|---|---|---|---|---|---|
| **A: sweep of equal lows/highs** (as in the reel) | BTC | −0.20 (30%) | +0.18 (43%) | −0.23 (28%) | −0.50 (20%) | 0.95 |
| | ETH | −0.30 (26%) | −0.11 (34%) | −0.31 (26%) | −0.09 (33%) | 0.55 |
| | Gold | +0.03 (35%) | −0.06 (33%) | −0.15 (30%) | −0.48 (18%) | 0.98 |
| | Oil | −0.27 (32%) | +0.20 (49%) | −0.47 (29%) | −0.30 (33%) | 0.50 |
| | S&P 500 | – | +0.18 (50%) | +0.15 (40%) | −0.23 (32%) | 0.75 |
| **B: sweep of any single swing** | BTC | −0.11 | −0.06 | −0.07 | −0.15 | 0.72 |
| | ETH | −0.16 | −0.13 | −0.13 | −0.10 | 0.62 |
| | Gold | −0.05 | −0.09 | −0.11 | −0.06 | 0.65 |
| | Oil | −0.31 | −0.32 | −0.38 | −0.35 | 0.75 |
| | S&P 500 | – | −0.06 | −0.00 | −0.12 | 0.71 |

## Verdict

- **REJECTED** everywhere. No market is positive in every period, and none beats random entries with the same stop and 2R target.
- **Equal lows** (variant A) produce far fewer setups: 14–80 a period. Results swing between good and bad periods (the S&P 500 was +0.18R and +0.15R, then −0.23R), which is what small samples do. In the latest period, all five markets lose.
- **Any single swing** (variant B) gives hundreds of trades per period and loses steadily: −0.06 to −0.38R. A swept low is not a reliable reversal point.
- **No look-ahead:** prefix invariance passed for both variants on BTC.
