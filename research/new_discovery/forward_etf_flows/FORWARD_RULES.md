---
title: STR-046 ETF-flow forward paper test rules
description: One pre-registered rule from the STR-045 post-hoc hint (5-day ETF flow z, 20-day hold, BTC and ETH), tested only on new data from 2026-11-21
sidebar_position: 1
---

# STR-046: ETF-flow follow rule, forward PAPER test (rules fixed 2026-11-20)

## Why this exists

STR-045 (pre-registered, 1- and 5-day holds) was REJECTED. A post-hoc look at longer holds (`../str_045/longer_holds.json`, `momentum_control.json`) suggested that following unusual 5-day ETF flows for ~20 days may work. It had too few trades to trust and was not significant after correcting for 24 combinations. **One** rule is therefore frozen here and judged only on data that did not exist when it was chosen.

The cell chosen is not the best-looking one: 40–60-day holds looked bigger. It is a middle setting that was positive in both halves for both assets: BTC +0.5% / +3.8%, ETH +10.6% / +4.8% per trade.

## Rule (frozen)

- **Data:**
  - daily net flows of all US spot ETFs (cryptoetf.today public pages, bitcoin-etf-flows and ethereum-etf-flows);
  - Binance spot daily opens (BTCUSDT, ETHUSDT).
- **Signal day D** = a US flow day.
  - F5(D) = sum of the last 5 flow days' net flows.
  - z(D) = (F5(D) − mean of F5 over the previous 60 flow days) / their standard deviation.
- **Only the value first seen counts.** Each day's z is recorded in `signals.csv` the first time the run sees it; later data revisions never change a recorded signal.
- **Entry:** at the Binance daily open of D+2 (00:00 UTC). If z ≥ +1 → LONG; if z ≤ −1 → SHORT.
- **One position per asset at a time.** Signals while a position is open are ignored.
- **Exit:** the daily open 20 days after entry.
- **Cost:** 0.05% per side (stress 0.20%).
- **Forward period:** signal days from **2026-11-20** onward (first possible entry 2026-11-22).

## Decision (BTC and ETH trades pooled)

- **First look at 40 closed trades** (about 2 years at the historical rate):
  - **PASS:** mean net > 0 and t ≥ 2.0.
  - **FAIL:** mean net ≤ 0.
  - **INCONCLUSIVE:** otherwise; continue to 80 trades with the same rule.
- **Futility stop at 20 closed trades:** stop if mean net < −1% per trade.
- **Paper only. Never edit this file, the script or past ledger rows.**
