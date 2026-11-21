---
title: STR-047 crypto cash-and-carry and STR-048 yields→gold results
description: Funding carry earned 15-22% a year in 2020-22 but has fallen below T-bill rates; the yield-momentum gold rule is not consistent
sidebar_position: 2
---

# STR-047 and STR-048 results (2026-11-21)

Rules: [`PREREG.md`](PREREG.md) (commit 3bb1e387). Script: `run.py`; numbers: `results.json`. Data:
- Binance funding history, 2020-01 → 2026-10;
- FRED DTB3, DGS10 and DFII10;
- Exness gold at 16:00 New York, 2020 →.

## STR-047: cash-and-carry (long spot, short perpetual), net yield per year

Margin-adjusted: capital = 1.2 × notional.

| Period | BTC always on | BTC conditional | ETH always on | ETH conditional | T-bill (hurdle) |
|---|---|---|---|---|---|
| 2020 → 2022 | **14.4%** | 12.6% | **18.2%** | 17.6% | 1.5% |
| 2023 → mid-2024 | **8.6%** | 7.8% | **9.0%** | 7.7% | 5.1% |
| mid-2024 → mid-2025 | 5.0% | 3.5% | **5.6%** | 3.5% | 4.5% |
| Jul 2025 → now | 3.3% | 0.9% | 2.5% | 0.3% | **3.8%** |

**Verdict: SOMETIMES.**
- Funding carry was excellent in 2020–2022 (14–18% a year, far above cash rates) and still beat T-bills in 2023–24.
- **It has shrunk steadily.** Since mid-2025 it pays **less than a risk-free T-bill**: 2.5–3.3% against 3.8%. In this period, funding was negative on 16–21% of days.
- The conditional version (only when funding is high) was worse in every period. It mostly sat out (14–18% of the time in TEST) and paid entry and exit costs.
- **Why it shrank:** this trade became very popular (spot-ETF basis trades, funds and exchange "earn" products), so the payment fell.
- **Not modelled:** exchange failure, forced deleveraging, and basis swings at entry and exit. These are real risks that make the current 2–3% even less attractive than T-bills.

## STR-048: 10-year yield momentum → gold (yield down → long gold, 20 trading days)

| Variant | 2020 → 2022 | 2023 → mid-2024 | mid-2024 → mid-2025 | Jul 2025 → now | TEST p |
|---|---|---|---|---|---|
| A: nominal yield (DGS10) | +0.41% (33) | **−1.06%** (17) | +1.06% (12) | +1.22% (14) | 0.18 |
| B: real yield (DFII10) | +0.89% (33) | **−1.15%** (17) | +0.59% (12) | +0.26% (14) | 0.44 |

Per-trade net % (number of trades in brackets).

**Verdict: REJECTED.**
- Both variants lost in 2023 → mid-2024. That was the period when gold rose strongly *despite* higher yields, as central banks bought gold, and the old "yields up, gold down" link broke.
- The other periods are positive but not significant, with only 12–33 trades each.
