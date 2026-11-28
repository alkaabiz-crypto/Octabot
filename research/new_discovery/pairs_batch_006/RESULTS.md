---
title: Pairs and relative-value batch 006 results
description: Eight pairs mean-reversion trades and crypto cross-sectional momentum; pairs all rejected, crypto momentum on watch with a fading edge
sidebar_position: 2
---

# Pairs / relative-value batch 006 results (2026-11-19)

Rules: [`PREREG.md`](PREREG.md) (commit 9caaef8e, before any computation). Script: `run_pairs6.py`; numbers: `results.json`.

**Bottom line: 0 SCREEN-PASS, 8 REJECTED, 1 WATCH (crypto weekly momentum, with a shrinking edge).** No forward test follows.

## One deviation (data only, disclosed)

STR-040 (crypto momentum) was pre-registered on Exness crypto 15-minute files, but those files cannot support it:
- they have no BTC;
- ADA ends in 2024-08;
- SOL and BNB have a 418-day gap.

The first run therefore had 0 TEST weeks. Its partial TRAIN number (+41 bp, 77 weeks) was seen before the switch.

The rules were left unchanged, and only the data source was switched: Binance daily opens for all 8 coins, 2020 →, at 0.05% per side (stress 0.20%, as for BTC/ETH elsewhere). Treat STR-040 with that in mind.

## Pairs (STR-039): net bp per trade after both legs' spreads; random-entry mean in brackets

| Pair | 2019-08→2022 | 2023→mid-2024 | mid-2024→mid-2025 | Jul 2025→now | TEST p |
|---|---|---|---|---|---|
| a Gold / Silver | – | −81 (+0) | −153 (−167) | −184 (−21) | 0.90 |
| b US oil / Brent | – | +6 (−23) | −1 (−20) | +50 (−19) | 0.08 |
| c Nasdaq / S&P 500 | −57 (−14) | +52 (−3) | −11 (−9) | −1 (−10) | 0.43 |
| d Dow / S&P 500 | −31 (−6) | −40 (−21) | +56 (−8) | −50 (+2) | 0.87 |
| e AUD / NZD | – | +76 (−1) | −7 (−6) | −46 (−45) | 0.51 |
| f EUR / GBP | – | +21 (−6) | −4 (−11) | +10 (−4) | 0.26 |
| g DAX / Euro Stoxx 50 | – | −69 (−23) | −103 (−117) | −38 (−12) | 0.67 |
| h BTC / ETH | −409 (+10) | +207 (−64) | −89 (−260) | −40 (−31) | 0.52 |

- **Every pair is REJECTED.** None is positive in all periods.
- With the classic ±2σ entry and exit at the mean, these pairs trade only about 6–25 times per period (about 12-day holds). Many stretched spreads kept stretching: gold/silver lost on every period, as the ratio trended strongly in 2024–26.
- US oil vs Brent and EUR/GBP come closest (positive in 2 of 3 periods). With 8–15 trades per period, that is far from evidence.

## Crypto cross-sectional momentum (STR-040): long the 2 best, short the 2 worst coins of the past week

| Period | Weeks | Net bp per week | Stress (0.20%/side) | Random picks | p vs random |
|---|---|---|---|---|---|
| 2020-08 → 2022 | 123 | **+104** | +44 | −19 | 0.12 |
| 2023 → mid-2024 | 78 | **+52** | −8 | −18 | 0.23 |
| mid-2024 → mid-2025 | 53 | **+31** | −29 | −20 | 0.33 |
| Jul 2025 → now | 71 | **+18** | −42 | −20 | 0.27 |

**WATCH, not a pass.** It is positive in every period and beats random coin picks in every period, which is the documented short-term crypto momentum (Liu & Tsyvinski). But:
- **the edge has shrunk steadily** (+104 → +52 → +31 → +18 bp per week);
- no period is statistically significant;
- at the stress cost of 0.20% per side it loses in every period since 2023;
- it needs shorting altcoins, which is only possible on a futures venue (with funding costs) or as CFDs (with swap).
