# Trend breadth test: TREND_ENS on 18 other coins, pre-registration

Committed **2026-11-12, before any data for these coins was downloaded or looked at.**

## Why

TREND_ENS (the forward trend bot) beat 90–94% of random timings on BTC and ETH in 2025–26 (`../exposure_control`), which is not significant on its own. Running the **same frozen rule on coins never used to build it** adds out-of-sample evidence without breaking the rule of no data before 2025.

## Data

- **Source:** Binance spot daily klines (`data-api.binance.vision`), **from 2025-01-01** to the last fully closed day.
- **Coins:** BNB, SOL, XRP, DOGE, ADA, TRX, LINK, AVAX, DOT, LTC, BCH, XLM, UNI, ATOM, ETC, FIL, NEAR, APT, all quoted in USDT. This list is the large, long-listed coins, fixed now.
- **Missing coins:** any coin with fewer than 600 daily candles is dropped and reported. None is replaced.

## Rule and engine, unchanged

- **Rule:** TREND_ENS, as in `../daily_signal_dca/from_2025/run.py signals`. The coin share is the share of the available SMA20/50/100/200 that the close is above. Warm-up NaN counts as 0, as in the erratum fix.
- **Execution:** the lump engine in `../daily_signal_dca/study.py lump`, with a 0.1% fee. Each decision is made at the close and filled at the next open.

## Primary test

- **Statistic:** the **mean across coins of the annualised Sharpe ratio** of daily returns over the full period.
- **Control:** 1,000 draws. In each draw, every coin's position series gets its own circular shift of a whole number of days, uniform in [20, n − 20], with seed 20261112. The mean Sharpe is then recalculated across coins.
- **Pass:** the rule's mean Sharpe is **above the 95th percentile** of the 1,000 draws.

## Secondary, information only

- Per-coin results: the percentile against that coin's own shifts, the return, buy and hold, and the max drop.
- The same test for SMA50.
- The share of coins where TREND_ENS beat buy and hold, and the share where its max drop was smaller.

## Consequences, fixed in advance

- **PASS:** the trend bot gets stronger evidence. The forward test continues, and nothing goes live before it completes.
- **FAIL:** the trend bot's 2025–26 backtest edge is treated as unconfirmed. The forward test continues unchanged.
