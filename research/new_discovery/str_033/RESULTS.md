---
title: STR-033 QuantLab NY-open candle results
description: First 5-minute candle after the New York open + EMA 12, held 6 hours, on the Nasdaq 100 (Exness USTECm) 2019-08 to 2026-10
sidebar_position: 2
---

# STR-033 results (2026-11-17): REJECTED (all three variants), claim not reproduced

Rules: [`PREREG.md`](PREREG.md) (commit d07740c4). Data: Exness USTECm 1-minute mid prices and spreads, built from the public tick archive (`build_data.py`; the archive starts 2019-08). Script: `run_str033.py`; numbers: `results.json`.

**One correction before the results were read.** The pre-registration defines the random-direction benchmark with the *same stop distance* as the actual trade. The first run's code used the opposite candle end for the random side instead, which unfairly penalises random trades. It was fixed to match the pre-registration. The strategy's own trades are unchanged by this fix. The always-long comparison uses its own natural stop (the candle low).

## Variant A (as described: candle colour and EMA 12 agree), 1,565 trades

| Period | Trades | Mean R after costs | Mean R stress | Win % | Random direction, mean R | p vs random |
|---|---|---|---|---|---|---|
| 2019-08 → 2022 | 743 | +0.04 | −0.16 | 26% | −0.08 | 0.04 |
| 2023 → mid-2024 | 322 | **−0.05** | −0.24 | 23% | −0.03 | 0.58 |
| mid-2024 → mid-2025 | 214 | +0.35 | +0.27 | 25% | +0.22 | 0.25 |
| July 2025 → Oct 2026 | 286 | +0.14 | +0.11 | 30% | −0.04 | 0.03 |

- **At 1% risk per trade, compounded:** **+113%** from 2019-08 to 2026-10, with a **maximum drawdown of −38%**.
- **By year:** 2019 −12%, 2020 −13%, 2021 +14%, 2022 +26%, 2023 −12%, 2024 +29%, 2025 +76%, 2026 −3%.
- **Win rate 23–30%.** It is a few large winners (the 6-hour hold against a tight stop at the first candle's other end) and many small losses.

## Variants B and C

- **B** (direction from the EMA only): **−1%** total, max drawdown −76%. Negative in two periods.
- **C** (A without a stop): with no stop, "1% risk" has no meaning. Measured against the candle's range it swings wildly (−84% total). Negative in two periods.

## Verdict

- **REJECTED for all three variants:** none is positive in every period. Variant A lost in 2023 → mid-2024, and the best TEST p (0.03) is not significant after correcting for the 3 variants.
- **The claim (+505.8% since 2019 at 1% risk) is not reproduced:** about +113% on Exness prices and spreads, with a −38% drawdown, and most of the gain came in 2025.
  - Their number may use futures (NQ) with lower costs, a different stop or exit, or other filters they did not show.
  - "Running live on a funded account" cannot be checked.
- **A real but small effect:** following the first candle's direction beat a random direction on the same days in two of four periods (p 0.04 and 0.03). This is the known opening-range momentum effect. It is not consistent enough, and it is too costly, to pass.
