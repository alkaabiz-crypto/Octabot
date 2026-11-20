---
title: SIG-005 CryptoMeter AI Screener pre-registration
description: Fixed-exit scoring of every CryptoMeter AI Screener call, Dec 2024 to Nov 2026, against random entries
sidebar_position: 1
---

# SIG-005: CryptoMeter AI Screener calls (pre-registration, 2026-11-20, before any call is scored)

**Source.** cryptometer.io "AI Crypto Screener", Past Trades. The site's own history covers 24 months, 2024-12 → 2026-11, about 3,000 calls. The user gave permission to read it. Each call has a pair, exchange, side (BUY/SELL), entry price, timestamp, the site's "price reached" and its PNL.

**The site's own method** (from its risk notes): a long's profit is measured from entry to the **highest** price reached within up to 30 days. A loss is counted only if the price never went up and is lower now. This is the maximum favourable excursion. It cannot be traded and inflates results. The calls give no stop or exit.

## Scoring rules (fixed now)

- **Prices:** Binance spot 15-minute candles for the call's coin against USDT. Calls on coins not listed on Binance spot are skipped, and the coverage is reported.
- **Entry:** the open of the first 15m candle starting at or after the call timestamp. A "slippage check" reports the gap between the site's entry price and ours.
- **Exits** (all reported; E1 is primary):
  - **E1:** stop −5%, target +10% (2R), time exit after 7 days. SELL calls mirror this. The stop is checked first within a candle.
  - **E2:** time exit after 24 hours.
  - **E3:** time exit after 7 days.
- **Costs:** 0.10% per side (primary, typical altcoin taker fee plus spread); stress 0.25% per side.
- **The site's method reproduced:** maximum favourable excursion within 30 days, for comparison only.
- **Benchmark:** for each call, a random entry time for the same coin and side between 30 and 60 days before or after the call, with the same exit rule; 1,000 sets. p = share of sets with a mean ≥ the actual mean.
- **Periods:**
  - 2024-12 → 2025-06 = VALIDATION;
  - 2025-07 → 2026-11 = TEST (calls still open at the data end are excluded).

## Verdict (SIG category)

- **PROFITABLE:** E1 mean net > 0 in both periods, E1 stress mean > 0 in TEST, and E1 TEST p ≤ 0.05 vs random.
- **UNPROFITABLE:** E1 mean net ≤ 0 in TEST.
- **INCONCLUSIVE:** anything else.
- **CLAIM ACCURATE / INACCURATE:** whether the site's reported win rate is within 10 points of the E1 win rate.

**Data handling.** The raw call list is third-party data and stays out of this public repository (scratch / private archive). Only derived statistics are committed.
