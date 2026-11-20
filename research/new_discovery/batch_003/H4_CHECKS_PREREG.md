# H4 (Coinbase premium) extra checks: pre-registration (2026-11-13, before any data for them was computed)

Two single-test checks of the batch 003 H4 rule. Its threshold (|z| ≥ 2), window (720 hours), 24-hour hold and one-position rule are **unchanged**. H4's own decision (WATCH) and its forward paper test are unaffected by either outcome.

## Check A: untouched earlier period, 2017-09 → 2019-12

**Data.** Coinbase BTC-USD and Binance BTCUSDT hourly (public APIs). Binance spot starts on 2017-08-17. The first 720 hours are warm-up for *z*, so signals run from about 2017-09-17 to 2019-12-31 inclusive. This programme has never evaluated those years.

**Execution.** Exness data does not cover these years, so trades use Binance prices.
- Entry at the **open of the first Binance hourly candle at or after the signal hour's close**; exit at the open of the hourly candle 24 hours later.
- **Costs:** Binance spot fee 0.10% per side (primary); 0.20% per side reported.

**Benchmark.** 1,000 random sets with the same count, sides and 24-hour hold, at random hourly opens in the same period. One-sided p.

| Label | Conditions |
|---|---|
| **CONFIRMED** | mean net > 0 at the primary cost, p ≤ 0.05, ≥ 30 trades |
| **POSITIVE, NOT SIGNIFICANT** | mean > 0, p > 0.05 |
| **NOT CONFIRMED** | mean ≤ 0 |

## Check B: a different second venue (Bitstamp instead of Binance), 2020-01 → latest

*prem* = ln(Coinbase BTC-USD close / **Bitstamp BTC-USD** close), hourly, same start times. Both are US-dollar venues, so the Binance USDT/USD basis plays no part. Everything else is exactly as in H4: *z*, signals, Exness BTCUSDm execution, costs, benchmark, and the periods EARLY 2020–2022, TRAIN, VALIDATION and TEST.

| Label | Conditions |
|---|---|
| **REPLICATED** | mean > 0 in all four periods; TEST stress > 0; TEST p ≤ 0.05; ≥ 30 TEST trades |
| **PARTIAL** | positive in all four periods, but TEST p > 0.05 |
| **NOT REPLICATED** | otherwise |

Hourly candles missing on one venue are dropped from both, as in H4.
