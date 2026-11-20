---
title: STR-042 market making simulation results
description: A simple 1-second market maker on BTC and ETH perpetuals loses money at every spread and fee level, because it is filled mostly when the price runs through it
sidebar_position: 2
---

# STR-042 results (2026-11-20): REJECTED (all 6 settings)

Rules: [`PREREG.md`](PREREG.md) (commit 5ecdc018). Script: `run_mm.py`. Daily numbers: `daily_results.csv`; summary: `results.json`. 48 days per market, 2024-12 → 2026-11, Binance USDT-M trade data.

## Average P&L per day, in basis points of one unit's notional (one unit = $1,000, at most ±5 units)

| Market | Half-spread | Fills per day (val / test) | Before fees | Maker 0.02% | Maker 0% (best case) |
|---|---|---|---|---|---|
| BTC | 2 bp | 1,597 / 2,624 | −1,220 / −2,324 | −4,455 / −7,536 | −1,224 / −2,327 |
| BTC | 5 bp | 107 / 257 | −48 / −153 | −268 / −665 | −52 / −156 |
| BTC | 10 bp | 13 / 30 | −15 / +4 | −45 / −58 | −19 / +2 |
| ETH | 2 bp | 5,651 / 6,432 | −4,173 / −5,373 | −15,477 / −18,095 | −4,177 / −5,376 |
| ETH | 5 bp | 460 / 855 | −253 / −689 | −1,175 / −2,375 | −256 / −692 |
| ETH | 10 bp | 63 / 129 | −30 / −59 | −159 / −316 | −33 / −62 |

For scale: −1,000 bp per day is a loss of $100 a day per $1,000 unit.

## Reading

- **REJECTED everywhere.** It loses even **before** fees, in all but one cell (BTC 10 bp in TEST, +4 bp/day, about 30 fills a day, which turns negative with fees).
- **Why: adverse selection.** A slow quote (updated once a second) gets filled mostly when the price is moving **through** it. It buys just before the price falls further and sells just before it rises. The tighter the quote, the more often this happens, and the larger the loss.
- **What real market makers do differently:**
  - they update quotes in microseconds;
  - they sit at the front of the queue at the best bid/ask;
  - they pay zero or negative (rebate) maker fees at top volume tiers;
  - they pull quotes before large moves.

  This simulation cannot represent any of that. Retail-speed market making is not a viable strategy, and professional market making needs infrastructure (co-location, order-book feeds, exchange fee tiers) far beyond a paper test.
- **Fill-rule check (post-hoc):** a version counting a fill when a trade merely *touches* the quote (`results_touch.json`) gave practically identical numbers. Computed quote prices almost never equal a traded price exactly, so this check does not bound the result from above. A proper upper bound would need full order-book (Level-2) data, which is not freely available historically.
- **Not possible on Exness at all**: CFDs have no order book to quote into.
