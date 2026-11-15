---
title: STR-027 results
description: Volumetric order blocks + EMA 21/50 + TP1–TP5 management, tested as pre-registered
sidebar_position: 2
---

# STR-027 results (2026-11-15): REJECTED on all four markets

Rules exactly as in [`PREREG.md`](PREREG.md) (commit b096254b, written before any computation). Script: `run_str027.py`; raw numbers: `results.json`. R = profit in units of the initial risk, after costs (primary: 0.05% crypto, 1.5× median spread on Exness; stress: 0.20% / 3× spread).

## The combined system (FULL)

| Market | Period | Trades | Mean R | Mean R (stress) | Win % | Random entries, mean R | p vs random |
|---|---|---|---|---|---|---|---|
| BTC | EARLY | 574 | −0.171 | −0.417 | 46.0 | −0.098 | 0.93 |
| BTC | TRAIN | 141 | −0.187 | −0.595 | 36.9 | −0.126 | 0.73 |
| BTC | VALIDATION | 118 | −0.108 | −0.425 | 42.4 | −0.093 | 0.54 |
| BTC | TEST | 152 | −0.112 | −0.509 | 47.4 | −0.117 | 0.47 |
| ETH | EARLY | 551 | −0.160 | −0.347 | 47.7 | −0.044 | 0.98 |
| ETH | TRAIN | 162 | −0.136 | −0.461 | 45.7 | −0.091 | 0.68 |
| ETH | VALIDATION | 123 | +0.008 | −0.233 | 52.8 | −0.068 | 0.27 |
| ETH | TEST | 156 | −0.027 | −0.308 | 53.2 | −0.059 | 0.37 |
| Gold | EARLY | 171 | −0.233 | −0.295 | 45.0 | −0.061 | 0.96 |
| Gold | TRAIN | 61 | +0.057 | −0.010 | 50.8 | +0.000 | 0.38 |
| Gold | VALIDATION | 58 | +0.164 | +0.102 | 55.2 | −0.009 | 0.16 |
| Gold | TEST | 86 | −0.139 | −0.190 | 44.2 | −0.052 | 0.72 |
| Oil | EARLY | 286 | −0.385 | −0.631 | 33.9 | −0.238 | 0.98 |
| Oil | TRAIN | 114 | −0.409 | −0.695 | 35.1 | −0.311 | 0.80 |
| Oil | VALIDATION | 55 | −0.249 | −0.506 | 41.8 | −0.257 | 0.49 |
| Oil | TEST | 86 | −0.327 | −0.540 | 30.2 | −0.195 | 0.83 |

**Decision: REJECTED for BTC, ETH, gold and oil.** No market is positive in every period, and no TEST result beats random entries with the same stops, targets and management (all p ≥ 0.37). No forward test follows.

The "win %" looks reasonable (about 45–53%) because TP1 at 1R moves the stop to breakeven, so many trades end as small wins or zero. But the losers are full −1R, and the later targets (TP3–TP5) are rarely reached, so the average stays negative. The random entries show the same pattern: most of the "look" of a good system comes from the trade management, not from where the order blocks put the entry.

## Do the three tools work better together? (diagnostics, not deciding)

TEST-period mean R, primary costs:

| Market | All three (FULL) | Without the EMA filter | Without the volume filter |
|---|---|---|---|
| BTC | −0.112 | −0.024 | −0.153 |
| ETH | −0.027 | −0.082 | −0.021 |
| Gold | −0.139 | +0.049 | −0.114 |
| Oil | −0.327 | −0.276 | −0.331 |

- **The EMA 21/50 trend filter did not help:** removing it was better in 3 of 4 markets.
- **The volume (buy/sell share) filter made little difference:** it removed only a few blocks, and the results moved both ways.
- None of the variants is positive across periods, so there is no sign that the combination is better than its parts.

## Checks

- **Causality:** a prefix-invariance check passed. Blocks computed on the first half of BTC's history are identical to the first-half blocks from the full history (776/776), and the first 562 trades are identical when the later 15m data is removed.
- **Volume:** BTC and ETH use real Binance volume. Gold and oil use Exness tick counts (the only volume a CFD feed has), as pre-registered.
- **What this does not test:** the invite-only "Buy/Sell Signal & Trade Management" script itself. Its rules are private, so it can only be judged from its signals, captured as they appear (SIG-004, the same method as SignalPro).
