---
title: STR-049 NY-open candle + EMA 12 + trailing stop results
description: Loses on Exness because the opening spread is about 4.9 points; with zero cost it reproduces the claim, and with futures-like costs it is positive every period but no better than a random direction recently
sidebar_position: 2
---

# STR-049 results (2026-11-22): REJECTED on Exness; the claim reproduces only without costs

Rules: [`PREREG.md`](PREREG.md) (commit 689522dc). Script: `run_str049.py`; numbers: `results.json`. Post-hoc cost checks: `cost_sensitivity.json`, `cost_sensitivity_periods.json`. Data: Exness USTECm, 1,764 trading days, 2019-08 → 2026-10.

## Pre-registered result (Exness prices and the actual spread at entry and exit)

| Trailing stop | Win % | Profit factor | 1% risk, compounded | Max drawdown | Decision |
|---|---|---|---|---|---|
| T1: under the last 5m candle (as drawn) | 33% | 0.79 | **−87%** | −91% | REJECTED |
| T2: 2 × ATR behind the best close | 31% | 0.93 | **−65%** | −79% | REJECTED |
| T3: exit on a close across EMA 12 | 29% | 0.89 | **−82%** | −85% | REJECTED |

**The claim:** +982%, profit factor 1.29, 57% wins, max drawdown < 20%.

## Why: costs (post-hoc checks, not decisions)

- **The Exness USTEC spread at 09:35 New York is a median 4.9 points.** The first candle's range (the risk) is small, so the spread alone costs a large slice of R on every trade.

| Round-trip cost | T1 | **T2** | T3 |
|---|---|---|---|
| **0 (no costs)** | +209%, PF 1.19 | **+753%, PF 1.29**, DD −23% | +347%, PF 1.20 |
| 0.5 point (about Nasdaq futures) | +116%, PF 1.13 | **+497%, PF 1.24**, DD −26% | +213%, PF 1.15 |
| 1.0 point | +51%, PF 1.08 | **+318%, PF 1.19**, DD −28% | +119%, PF 1.11 |
| Exness actual (~5 points) | −87% | −65% | −82% |

**With zero costs, T2 reproduces the post almost exactly:** PF 1.29 and +753% vs the claimed 982%. The claimed 57% win rate does not reproduce; every variant wins about 31–36%. Their backtest most likely ignored costs (TradingView's default) or used a different exit.

**T2 at futures-like costs, by period (mean R; random direction in brackets):**
- 2019-08 → 2022: +0.12 (+0.02), p 0.01
- 2023 → mid-2024: +0.10 (+0.02), p 0.14
- mid-2024 → mid-2025: +0.27 (+0.10), p 0.06
- Jul 2025 → now: +0.04 (+0.04), **p 0.50**

It is positive in every period. But in the latest period, **a random direction with the same trailing stop does just as well**. Recently the gain comes from the trailing exit catching big trend days on the Nasdaq, not from the EMA 12 direction call. 2020 and 2026 were losing years.

## Verdict

- **REJECTED for trading on Exness** (the user's broker). The opening spread makes it lose 65–87% at 1% risk.
- The "+982%" is reproducible only **without trading costs**.
- On a low-cost venue (Nasdaq futures) it would have been positive in every period. However:
  - this is post-hoc;
  - the direction signal has not beaten a random direction since mid-2025;
  - it would need its own pre-registered forward test on futures-like costs before counting for anything.
