---
title: STR-042 market making simulation pre-registration
description: A simple two-sided market maker on BTC and ETH perpetual futures, simulated on Binance trade-by-trade data with a conservative fill rule
sidebar_position: 1
---

# STR-042: market making on BTC / ETH perpetuals (pre-registration, 2026-11-20, before any computation)

**User request:** "do the strategy market making".

**Venue note.** Market making needs a public order book where your own limit orders rest. It is **not possible on Exness**: CFD market-maker broker, you always pay its spread. This test uses Binance USDT-M perpetual futures (maker fee 0.02% at the standard tier). The results apply to such exchanges only.

## Data

- **Source:** Binance public `aggTrades` (data.binance.vision), every trade with its price and time.
- **Markets:** BTCUSDT and ETHUSDT perpetuals.
- **Days:** the 1st and the 15th of every month from 2024-12-01 to 2026-11-15 (48 days per market).
- **Handling:** raw files are processed in scratch and deleted; only daily results are kept.

## The market maker (fixed now)

- **Clock:** 1-second steps. The reference price is the last trade price of the previous second, so there is a one-second reaction delay.
- **Quotes:** a bid at ref × (1 − h) and an ask at ref × (1 + h), both shifted by −(inventory / L) × h × ref. When long, both quotes move down to sell more readily, and the reverse when short.
- **Half-spread variants:** **h = 2, 5, 10 basis points**.
- **Inventory limit:** **L = 5** units, each a fixed notional. No new bid at +5 and no new ask at −5.
- **Fill rule (conservative on queue position):**
  - our bid fills (buy 1 unit) only if some trade in the next second prints **strictly below** our bid;
  - our ask fills only if a trade prints strictly above it;
  - both can fill in the same second.
- **End of day:** any inventory is closed at the last price, paying the taker fee (0.05%).
- **Fees:** maker **0.02%** per fill (primary, Binance standard), **0.015%** (Hyperliquid base tier), **0%** (best case: top VIP tier or a maker-rebate venue).
- **Not modelled:** funding payments (inventory is small and short-lived), order-book depth, queue priority beyond the trade-through rule, exchange outages.

## Measures and decision

- **Daily P&L** in basis points of one unit's notional, split into spread captured and inventory gains/losses (adverse selection). Fill counts are also reported.
- **Periods:** VALIDATION days 2024-12 → 2025-06; TEST days 2025-07 → 2026-11.
- **SCREEN-PASS** (per market × h, primary fee 0.02%): mean daily P&L > 0 in both periods, TEST t ≥ 2 across days, BH over the 6 (market × h) tests.
- **Even a pass is only "promising in simulation".** Real queues, latency and adverse selection are worse than this model. The next step would be a live paper simulation on order-book data, never real money first.
