# Daily signal DCA bot (spot, 1x, buys and sells): pre-registration

Written and committed **2026-11-10, before any result was computed.** Research only: paper and backtest, no orders.

## Goal

A bot that trades at most once a day, **spot only, with no leverage**. It either holds the coin or holds cash, and decides from signals that have published evidence. It is tested in two ways:
- **lump sum:** the whole starting capital is used from day 1;
- **DCA:** a fixed amount is added every day, and the signal decides whether the pot sits in the coin or in cash.

## Signals (taken from the literature, not tuned here)

| ID | Rule (daily closes, UTC) | Source |
|---|---|---|
| **TREND_ENS (primary)** | Position = share of {SMA20, SMA50, SMA100, SMA200} that the close is above (0, 25, 50, 75 or 100% in the coin). Averaging the four avoids picking a single lookback. | Detzel et al. 2020; Grayscale "The Trend is Your Friend" 2023 |
| SMA50 | 100% in the coin when the close is above SMA50, otherwise cash | as above |
| SMA200 | 100% in the coin when the close is above SMA200, otherwise cash | as above |
| MAX10 | In the coin after a close at a new 10-day high; out after a close at a new 10-day low | Quantpedia, "Trend-following and Mean-reversion in Bitcoin" |
| MOM1 | In the coin tomorrow if today's return > 0 | Zaremba et al. 2021: large coins show daily momentum |
| REV_RSI2 | Buy when RSI(2) < 10; sell when RSI(2) > 70 | Connors-style reversal, a contrarian control |
| HOUR_21_23 | Hold the coin only from 21:00 to 23:00 UTC every day (hourly data) | Padyšák and Vojtko, via Quantpedia |
| TREND_ENS_VOL | TREND_ENS × min(1, 50% / realised 30-day volatility, annualised) | volatility management, a labelled overlay |

## Execution and costs

- **Timing:** each signal is computed on the daily close, and the trade happens at the next day's open. For HOUR_21_23 the trades are at the 21:00 and 23:00 hourly opens.
- **Fees:**
  - main case: **0.1% per side**, the Binance spot taker fee;
  - stress test: 0.2%;
  - HOUR_21_23 is also shown at 0.02% (maker fee).
- **Cash earns nothing.** Position changes are traded only by the amount they change.

## Data and periods

- **Data:** Binance BTCUSDT and ETHUSDT daily candles (and hourly for HOUR_21_23), from `data-api.binance.vision`.
- **Periods:**
  - signals start **2018-01-01**, after enough history for SMA200;
  - full period to **2026-11-01**;
  - **early half: 2018–2021;**
  - **late half: 2022-01-01 to 2026-11-01**, mostly after the cited studies were published, which makes it the honest out-of-sample period.
- **ETH:** run with identical rules and no retuning, as a robustness check.
- **DCA version:** 10 USD is added every day.
  - benchmark: plain daily DCA, buying 10 USD of the coin every day and never selling;
  - each signal: the pot is in the coin or in cash according to the signal.

## Pass/fail (primary = TREND_ENS on BTC at 0.1%, lump sum), decided now

It passes only if **both** hold in **both** halves:
1. its Sharpe ratio (daily returns, annualised, risk-free rate 0) is above buy-and-hold's;
2. its max drawdown is smaller than buy-and-hold's.

**In addition,** the same two conditions must hold for TREND_ENS on **ETH** in the **late half**.

- Every other signal is reported but **cannot rescue** a failed primary.
- **A pass** would justify a **paper or demo** forward test of TREND_ENS as the bot's rule, never immediate live money.
- **A fail** means the honest answer is plain DCA with no signal.
