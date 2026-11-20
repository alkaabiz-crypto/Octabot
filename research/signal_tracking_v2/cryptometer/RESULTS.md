---
title: SIG-005 CryptoMeter AI Screener results
description: 2,019 CryptoMeter AI calls (Dec 2024 to Nov 2026) scored with fixed exits on Binance prices; unprofitable and no better than random
sidebar_position: 2
---

# SIG-005 results (2026-11-20): UNPROFITABLE, CLAIM INACCURATE

Rules: [`PREREG.md`](PREREG.md) (commit adce5d6e) and Amendment 1 (commit a9671623), both before scoring. Scripts: `fetch_prices.py`, `score.py`, `check_15m.py`. Numbers: `results.json`, `check_15m.json`. The raw call list stays out of this public repository.

## Coverage

- 3,098 call rows from the site's 24-month history (2024-12-02 → 2026-11-11). 2,398 could be scored on Binance spot prices. 690 were on coins not traded on Binance spot, and 10 were too recent for 7 days.
- After removing the same coin–minute call repeated across exchanges: **2,019 unique calls**, nearly all BUY.
- Our entry (next 1h open) is a median 0.06–0.32% away from the site's entry price, so the entries match closely.

## Results: unique calls, after 0.10% per side

| | 2024-12 → 2025-06 (684) | 2025-07 → 2026-11 (1,335) |
|---|---|---|
| **Site's own method** (best price within 30 days) | +26.8% average, 91% "wins" | +30.5% average, 92% "wins" |
| **E1: stop −5%, target +10%, max 7 days** | **−0.83%** per call, 30% wins | **−0.56%** per call, 32% wins |
| Random entries (same coin, same rule) | −0.52% | −0.37% |
| p vs random | 0.88 | 0.88 |
| E2: hold 24 hours | −1.01%, 38% wins | −0.17%, 40% wins |
| E3: hold 7 days | −3.42%, 34% wins | −1.73%, 34% wins |

The all-rows results (duplicates included) are the same picture: E1 −0.92% and −0.45%.

## Verdict

- **UNPROFITABLE.** Every fixed exit loses in both periods.
- **No better than random.** The calls did slightly worse than buying the same coins at random times a month or two away (p 0.88).
- **CLAIM INACCURATE.** The site's "91% win rate, +27–30% average" comes from counting the best price reached in the following 30 days. With a real stop and target, about 30% of calls win and the average is negative. Almost any volatile coin reaches *some* higher price within 30 days, so the site's method counts nearly every call as a win whatever happens afterwards (random entries were not scored by the site's method here).

## 15-minute check (Amendment 1)

E1 re-scored on Binance **15-minute** candles over each unique 2025-07 → 2026-11 call's own 7 days: 1,335 calls, **−0.35% per call, 33% wins**. That is slightly less negative than on 1-hour candles (−0.56%, because finer candles resolve fewer stop-and-target-in-the-same-candle cases against the trade), and still a loss. The verdict is unchanged.
