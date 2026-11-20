---
title: STR-043 value-area reel results
description: Both value-area scenarios from the soualium reel (VAL/VAH wick rejection, and value-area break + FVG retest) on BTC, ETH, gold, oil and the S&P 500; rejected everywhere
sidebar_position: 2
---

# STR-043 results (2026-11-20): REJECTED, both scenarios, all 5 markets

Rules: [`PREREG.md`](PREREG.md) (commit 0ef74eaf, from the transcribed narration, before any computation). Script: `run_str043.py`; numbers: `results.json`.

## Mean R per trade after costs (win % in brackets)

| Scenario | Market | to 2022 | 2023→mid-2024 | mid-2024→mid-2025 | Jul 2025→now | TEST p vs random |
|---|---|---|---|---|---|---|
| **S1: wick rejection at VAL/VAH → other edge** | BTC | −0.09 (33%) | −0.24 (30%) | −0.16 (29%) | −0.06 (34%) | 0.27 |
| | ETH | −0.16 (29%) | −0.17 (30%) | −0.22 (27%) | +0.05 (35%) | 0.22 |
| | Gold | −0.08 (38%) | +0.14 (44%) | −0.01 (39%) | −0.33 (26%) | 0.99 |
| | Oil | −0.22 (30%) | −0.01 (36%) | −0.11 (33%) | −0.20 (37%) | 0.37 |
| | S&P 500 | – | −0.08 (39%) | −0.25 (35%) | −0.37 (31%) | 0.98 |
| **S2: strong break + FVG retest → 2R** | BTC | −0.11 (33%) | −0.12 (34%) | −0.06 (35%) | −0.08 (34%) | 0.40 |
| | ETH | −0.02 (35%) | −0.04 (36%) | −0.08 (33%) | −0.05 (34%) | 0.37 |
| | Gold | +0.05 (38%) | −0.05 (34%) | +0.03 (36%) | −0.05 (34%) | 0.63 |
| | Oil | −0.19 (34%) | −0.19 (36%) | −0.23 (34%) | −0.24 (33%) | 0.59 |
| | S&P 500 | – | −0.02 (37%) | +0.17 (41%) | −0.15 (32%) | 0.76 |

S1's targets (the opposite value-area edge) averaged about 2–3.4R away, so its win rates of 26–44% are below what those targets need.

## Verdict

- **REJECTED** for both scenarios on all five markets. None is positive in every period, and none beats random entries with the same risk and target (TEST p 0.22–0.99).
- **"The strongest scenario"** (S2, the break and FVG retest that "most people miss") loses on 4 of 5 markets in the latest period, and wins only about one trade in three with a 2R target. That is roughly breakeven before costs and a loss after them.
- **No look-ahead:** prefix invariance passed for both scenarios (1,119 and 2,724 signals identical on half of BTC's history).
- **Not tested:** the creator's paid platform and its unspecified "volume confirmation". The reel itself is an advertisement for that platform ("comment *volume*").
