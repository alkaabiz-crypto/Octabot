# Pre-registered protocol: indicator scan on US oil and gold

Written on 2026-11-10, before any result of this scan was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Question

Which popular indicators give the most reliable BUY and SELL signals on US oil (USOILm) and gold (XAUUSDm)? Can any
of them reach a **70%+ win rate while also making money** after real costs?

Win rate is reported for every signal. It is never judged alone, because the exit design largely sets it. A target
half the size of the stop wins about 2 of 3 trades even at random entry times, yet loses money once costs are paid.
Every signal is therefore compared with random entries that use the same exit.

## Data

- Exness USOILm and XAUUSDm, every bid and ask quote, as 15-minute bid/ask candles. The data files are those of
  `research/oil_rsi_vwap` and `research/gold_rsi_vwap`; the code is reused read-only.
- 2024-03 to 2024-12 is used for warm-up only.
- **Selection period: 2025-01-01 to 2025-12-31.**
- **Confirmation period: 2026-01-01 to the latest quote (2026-11-09).**

## Indicators (1H bid candles, textbook settings, nothing tuned)

| # | Indicator | BUY when | SELL when (mirror) |
|---|---|---|---|
| 1 | RSI 14 reversion | RSI crosses up through 30 | RSI crosses down through 70 |
| 2 | RSI 2 extreme | RSI 2 crosses below 10 | RSI 2 crosses above 90 |
| 3 | Bollinger 20, 2 re-entry | close back above the lower band after closing below it | close back below the upper band after closing above it |
| 4 | Stochastic 14, 3, 3 | %K crosses above %D with both below 20 | %K crosses below %D with both above 80 |
| 5 | MACD 12/26/9 | MACD line crosses above signal | crosses below |
| 6 | EMA 9/21 cross | EMA 9 crosses above EMA 21 | crosses below |
| 7 | Donchian 20 breakout | close crosses above the previous 20-bar high | crosses below the previous 20-bar low |
| 8 | VWAP momentum | close crosses above session VWAP with RSI 14 > 50 | crosses below with RSI 14 < 50 |
| 9 | Supertrend 10, 3 | trend flips up | trend flips down |
| 10 | CCI 20 | CCI crosses up through −100 | CCI crosses down through +100 |

## Exits (the same for signals and for random entries)

| Exit | Stop | Target | Time limit | Break-even win rate before costs |
|---|---|---|---|---|
| **HW** (high win rate) | 2 × ATR | 1 × ATR | 24 hours | about 67% |
| **SYM** | 2 × ATR | 2 × ATR | 48 hours | about 50% |
| **TRAIL** | 2 × ATR, then 3 × ATR trail | none | none | about 30 to 35% (trend following) |

10 indicators × 2 directions × 3 exits = 60 variants per market, 120 in total.

## Execution and costs

- **Entry.** At the next 15-minute candle after the signal: buy at the ask, sell at the bid.
- **Stops and targets.** Checked on the side of the quote that closes the position. If both are touched in one
  candle, the stop is assumed first.
- **One position at a time** per variant.
- **Primary cost.** The measured spread plus 0.02% of price slippage per round trip.
- **Stress cost.** Adds 0.05% slippage and 0.02% per day held for swaps (unverified).

## Evaluation (fixed now)

For every variant and both periods, report: trades, win rate, profit factor, expectancy (R), t, maximum drawdown,
the matched random entry's win rate and expectancy, and p_random (1,000 runs).

A **reliable signal** must pass both stages:

1. **Selection (2025):** at least 30 trades, expectancy > 0 at primary cost, and p_random ≤ 0.05.
2. **Confirmation (2026):** at least 20 trades, expectancy > 0 at primary cost, and p_random ≤ 0.05.

With 120 variants, about 6 would pass stage 1 by chance alone, which is why the confirmation stage is required.

A **70%-accurate signal that is worth using** must, in addition, have a win rate of at least 70% in both periods.

## Interpretation

Even a variant passing both stages would justify only a frozen forward paper test, not live trading. The
confirmation period is about 10 months, so a pass there is weak evidence on its own.
