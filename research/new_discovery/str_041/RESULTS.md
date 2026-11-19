---
title: STR-041 liquidity sweep + structure + dominance + OTE results
description: The ICT-style four-part setup on BTC, ETH, gold, oil and the S&P 500; rejected everywhere
sidebar_position: 2
---

# STR-041 results (2026-11-19): REJECTED on all 5 markets, all 3 variants

Rules: [`PREREG.md`](PREREG.md) (commit b34de584). Script: `run_str041.py`; numbers: `results.json`.

## Mean R per trade after costs (win % in brackets), variant A (all four parts, 2R target)

| Market | to 2022 | 2023→mid-2024 | mid-2024→mid-2025 | Jul 2025→now | TEST p vs random |
|---|---|---|---|---|---|
| BTC | −0.13 (31%) | −0.06 (36%) | −0.20 (29%) | −0.16 (32%) | 0.72 |
| ETH | −0.26 (26%) | +0.02 (37%) | −0.03 (35%) | −0.04 (35%) | 0.55 |
| Gold | −0.16 (30%) | −0.08 (33%) | +0.05 (37%) | −0.01 (35%) | 0.46 |
| Oil | −0.28 (30%) | −0.04 (39%) | −0.44 (26%) | −0.18 (33%) | 0.48 |
| S&P 500 | – | +0.21 (43%) | −0.28 (26%) | −0.12 (32%) | 0.60 |

- **Variant B (without the buyer/seller dominance filter):** about the same, slightly worse on most markets. The dominance filter adds little.
- **Variant C (target at the leg high, "internal liquidity"):** about the same, slightly worse on most markets.
- **No market is positive in every period, and none beats random entries** (TEST p 0.33–0.81). The win rate of 26–43% with a 2R target is roughly what random entries with the same stop and target achieve.
- **No look-ahead:** prefix invariance passed (setups detected on half of BTC's history are identical to the full-history run).
