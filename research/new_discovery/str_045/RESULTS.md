---
title: STR-045 crypto ETF flow signal results
description: Daily US spot Bitcoin / Ethereum ETF net flows do not predict the next days' BTC / ETH returns once the reporting delay is respected
sidebar_position: 2
---

# STR-045 results (2026-11-20): REJECTED (BTC and ETH, 1-day and 5-day holds)

Rules: [`PREREG.md`](PREREG.md) (commit c43c1a06). Script: `run_str045.py`; numbers: `results.json`. Flow data are the daily net flows of all US spot ETFs from cryptoetf.today's public pages (BTC 2024-01-11 →, ETH 2024-07 →). Prices are Binance daily opens. Signals are acted on at 00:00 UTC two days after the flow day.

## Information coefficient: flow z-score vs the next return

| | 1-day return (val / test) | 5-day return (val / test) |
|---|---|---|
| BTC | −0.03 / +0.00 | −0.07 / +0.09 |
| ETH | −0.05 / −0.00 | +0.18 / −0.03 |

None is significant; all |t| < 1.1.

## FOLLOW rule (big inflow z ≥ +1 → long; big outflow z ≤ −1 → short), net of 0.05% per side

| | 1-day hold (val / test) | 5-day hold (val / test) |
|---|---|---|
| BTC | −0.31% / −0.04% (p 0.38) | −0.13% / +0.45% (p 0.22) |
| ETH | −0.39% / −0.24% (p 0.69) | −3.48% / +0.03% (p 0.47) |

## Verdict

- **REJECTED** everywhere. No version is positive in both periods, and none beats random days.
- **Fading the flows doesn't work either**: the opposite trade is only small and inconsistent (+0.11% / −0.16% for BTC over 1 day).
- **Why:** big ETF flows are widely reported and mostly *follow* price (investors buy after rises). By the time a day's flow is known, its information is already in the price. The headline "record outflows" is news about the past, not a forecast.

## Post-hoc: longer holds (user question, 2026-11-20)

- **Longer holds:** `longer_holds.py` / `.json` re-ran the follow rule with signals from 1-, 5- and 20-day summed flows and holds of 10/20/40/60 days (24 cells).
  - Many cells are positive, ETH especially (e.g. 5-day flow, 20-day hold: +6.7% per trade, +10.6% / +4.8% by half).
  - **None is significant after BH over the 24 cells**, and each has only 10–60 trades.
- **Momentum control:** `momentum_control.py` / `.json` ran the same rule on past price returns.
  - For 20-day windows, flows track price (correlation 0.66–0.75) and plain momentum does about as well. That part of the effect is momentum.
  - For 1- and 5-day flow windows, mainly on ETH, flows did better than momentum, and mostly stayed positive when flow and price disagreed.
- **The verdict above (pre-registered horizons) stays REJECTED.** The longer-hold hint is labelled post-hoc. One rule (5-day flow, 20-day hold, BTC + ETH) is frozen as a forward paper test, STR-046 (`../forward_etf_flows/`), judged only on new data from 2026-11-20.
