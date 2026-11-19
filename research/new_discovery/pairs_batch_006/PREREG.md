---
title: Pairs and relative-value batch 006 pre-registration
description: Eight spread (pairs) mean-reversion trades and one crypto cross-sectional momentum rule, with fixed entry and exit rules
sidebar_position: 1
---

# Pairs / relative-value batch 006: pre-registration (2026-11-19, written before any computation)

The user asked to keep searching for strategies with clear entries and exits. Every earlier test was a bet on direction. This batch tests **market-neutral** trades: buy one market and sell a related one when their price ratio is stretched, and exit when it returns to normal. This is the classic statistical-arbitrage "pairs trading" (Gatev, Goetzmann & Rouwenhorst 2006).

## Pairs (STR-039a–h)

| ID | Long/short pair | Data | Daily price |
|---|---|---|---|
| a | Gold / Silver (XAUUSDm / XAGUSDm) | Exness 15m, 2023 → | 16:00 New York |
| b | US oil / Brent (USOILm / UKOILm) | Exness 15m, 2023 → | 16:00 New York |
| c | Nasdaq / S&P 500 (USTECm / US500m) | Exness 1m, 2019-08 → | 16:00 New York |
| d | Dow / S&P 500 (US30m / US500m) | Exness 1m, 2019-08 → | 16:00 New York |
| e | AUD / NZD (AUDUSDm / NZDUSDm) | Exness 15m, 2023 → | 16:00 New York |
| f | EUR / GBP (EURUSDm / GBPUSDm) | Exness 15m, 2023 → | 16:00 New York |
| g | DAX / Euro Stoxx 50 (DE30m / STOXX50m) | Exness 15m, 2023 → | 17:30 Berlin |
| h | BTC / ETH | Binance 1h, 2018 → | 00:00 UTC |

**Rules (identical for every pair, fixed now):**
- **Spread:** s = ln(A) − β · ln(B). β = OLS slope of ln(A) on ln(B) over the previous 60 daily prices (known before today).
- **z-score:** z = (s − mean of the previous 60 s) / their standard deviation, computed with today's price and the past 60 days only.
- **Entry at today's daily price:**
  - z > +2 → SHORT the spread (sell A, buy β × A-notional of B);
  - z < −2 → LONG the spread.
- **Exit:** z crosses 0 (take profit), or |z| > 4 (stop), or 20 trading days (time exit). Exits are checked at each daily price.
- **One trade at a time per pair.**
- **Return:** P&L on both legs divided by the notional of leg A, in bp.
- **Costs:** the Exness spread at entry and exit on both legs (stress 2 ×); BTC/ETH 0.05% per leg per side (stress 0.20%).
- **Swap is ignored**, because the two legs largely offset, and is noted in the results.

## Crypto cross-sectional momentum (STR-040)

- **Coins:** Exness BTC, ETH, SOL, BNB, XRP, LTC, ADA and BCH (15m, 2023 →).
- **Rebalance:** every Monday 00:00 UTC, rank the coins by their past 7-day return.
- **Positions:** LONG the top 2, SHORT the bottom 2, equal weight, held 7 days. This is short-term crypto momentum (Liu & Tsyvinski 2021).
- **Costs:** each coin's Exness spread at entry and exit.

## Evaluation

- **Periods:** EARLY (to 2022, only where data exists), TRAIN 2023-01 → 2024-06, VALIDATION 2024-07 → 2025-06, TEST 2025-07 → now.
- **Benchmark:**
  - pairs: random entry days with the same number of trades, the same sides and the same holding lengths, 1,000 sets;
  - STR-040: random selection of 2 long / 2 short coins each week, 1,000 sets.
- **SCREEN-PASS:** net mean > 0 in every period, TEST stress mean > 0, TEST p ≤ 0.05 after BH over the 9 tests, and ≥ 30 TEST trades (STR-040: ≥ 30 weeks).
- **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.

No parameter is changed after results are seen. All results are reported.
