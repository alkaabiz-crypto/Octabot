---
title: STR-050 negatively correlated pairs results
description: Mean reversion and lead-lag on five economically opposite pairs; no reliable edge, GBP/USD vs USD/CHF on WATCH with tiny samples
sidebar_position: 2
---

# STR-050 results (2026-11-22)

Rules: [`PREREG.md`](PREREG.md) (commit 2d575c3d), written before any computation. Script: `run_negcorr.py`. Numbers: `results.json`.

## Part 1: mean reversion (|z| > 2, exit at z = 0, stop |z| > 4, max 20 days, Exness spreads on both legs)

Cells show trades, mean net bp per trade, and the average 60-day correlation of daily returns.

| Pair | TRAIN | VALIDATION | TEST (p vs random) | Decision |
|---|---|---|---|---|
| a EUR/USD vs USD/CHF (β −0.78) | 11, +47, −0.76 | 11, −17, −0.73 | 8, −13 (0.65), −0.87 | REJECTED |
| b GBP/USD vs USD/CHF (β −0.69) | 11, +13, −0.70 | 12, +47, −0.53 | 8, +2 (0.49), −0.73 | **WATCH** |
| c Gold vs USD/CHF (β −1.06) | 9, −67, −0.48 | 10, −78, −0.24 | 12, −16 (0.36), −0.48 | REJECTED |
| d Gold vs USD/JPY (β −0.45) | 12, −59, −0.44 | 9, +110, −0.24 | 15, +215 (0.055), −0.29 | REJECTED |
| e US oil vs USD/CAD (β −1.48) | 9, +156, −0.30 | 6, +82, −0.12 | 13, −16 (0.44), −0.03 | REJECTED |

- **The relationships are real.** The currency pairs were strongly negative throughout (−0.5 to −0.9). Gold against the dollar pairs was moderately negative.
- **Oil vs USD/CAD has faded.** The correlation fell from −0.30 to almost zero in TEST, so that pair no longer behaves as an opposite pair.
- **Reversion after a break does not pay reliably.** Only GBP/USD–USD/CHF was positive in every period, and its TEST average (+2 bp on 8 trades) is indistinguishable from random entries.
- **Gold–USD/JPY looked good recently** (+110 and +215 bp), but it lost in TRAIN and misses significance after correcting for 5 pairs. It is REJECTED under the fixed rules.
- **Too few trades.** About 8–15 trades per period is far below the 30 required, so nothing could pass in any case.

## Part 2: lead–lag (does one market's day predict the other's next day?)

- **None of the 10 TEST ICs is significant after BH.** Every |t| in TEST is below 1.5.
- Several keep the same sign in all three periods (for example EUR/USD → USD/CHF), but the ICs are at most about 0.07, too small to cover costs.
- The two larger ICs (gold ↔ USD/CHF and USD/JPY → gold, about 0.15 in VALIDATION) did not repeat in TEST.
- No follow-up rule is registered.

## Verdict

- **Negative correlation is a good description of how these markets move together, but not a trading edge on its own.**
- When the usual opposite relationship breaks, it does not snap back reliably enough to beat costs.
- One market's move does not predict the other's next day.
- GBP/USD–USD/CHF stays on WATCH only; it has too few trades to judge.
