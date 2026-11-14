# Pre-registered protocol: RSI + VWAP entries

Written on 2026-11-10 at about 06:40 UTC, before any result of this study was computed. Paper research only. Nothing in
`research/btc_breakout`, `research/btc_signal_assistant`, `research/signal_comparison` or
`research/donchian_validation` is changed. The frozen Donchian forward test keeps running untouched.

## Question

Do entries chosen with RSI and VWAP pick better moments than random entry, after realistic costs, on BTC? Does the
answer replicate on ETH?

## Indicators (1H candles, textbook settings, never tuned)

- **RSI 14**: Wilder's RSI on 1H closes.
- **Session VWAP**: anchored at 00:00 UTC each day. It is the cumulative sum of typical price × volume, divided by
  cumulative volume, over that day's closed 1H candles up to and including the current one. Typical price is
  (high + low + close) / 3. Volume is the Binance base-asset volume.
- **ATR 14**: Wilder's ATR on 1H candles, used only to size the stop.

## Entry rules (signal on a closed 1H candle)

| Rule | BUY | SELL |
|---|---|---|
| **V1 VWAP momentum** | Close crosses above the session VWAP (the previous candle, in the same session, closed at or below it) and RSI 14 > 50 | Close crosses below VWAP and RSI 14 < 50 |
| **V2 RSI reversion below VWAP** | RSI 14 crosses up through 30 (previous < 30, current ≥ 30) and close < session VWAP | RSI 14 crosses down through 70 and close > session VWAP |

There is no trend filter. The request was RSI and VWAP only, and adding filters would multiply the variants tested.

## Execution and exits (identical for every variant and for the random benchmark)

- Entry at the open of the first 15m candle after the signal close. One position at a time per variant.
- Risk 1R = 2 × ATR14 of the signal candle. Stops are checked on every 15m candle: lows for BUY, highs for SELL.
  A gap through the stop fills at the 15m open.
- **TRAIL exit**: after each 1H close, move the stop to the best close since entry ∓ 3 × ATR14, never backwards.
  This is the frozen Donchian exit.
- **SYM exit**: target +1R (2 × ATR), stop −1R, or exit at the close after 48 hours. If target and stop are both
  touched in one 15m candle, the stop is assumed first. Without an edge, this exit wins about half the time before costs.

So there are 2 rules × 2 directions × 2 exits = **8 variants**. Nothing else is tested.

## Costs

Binance prices carry no broker spread, so costs are added per round trip as a share of price.

- **Primary**: 0.05%.
- **Stress**: 0.10%.

Both are hypothetical; Exness BTCUSDm spreads in 2025 and 2026 were about 0.02%, before slippage and swaps.

## Data and periods

- **BTCUSDT, 2020-01-01 to 2026-11-08**: the frozen Binance research data (15m, 1H, 1D). It is reported in two parts:
  development (to 2025-06) and the 2025-07 onward period. BTC history has been examined many times in earlier studies,
  so **BTC results are exploratory**. They cannot be a clean test.
- **ETHUSDT, 2020-01-01 to the last closed candle**: downloaded from Binance for this study. No earlier study used ETH,
  so **ETH is the replication test**. The rules apply to it unchanged.

## Benchmark

Matched random entry: the same direction, exit, costs and one-position rule, and the same number of trades in every
calendar quarter. It uses 2,000 runs, walking forward in time (the unbiased sampler from `research/donchian_validation`).
p_random is the share of runs whose expectancy is at least the variant's.

## Reported per variant

Trades, win rate, profit factor, expectancy (R) with a bootstrap 95% interval, t-statistic and one-sided p,
Holm-adjusted p across the 8 variants, p_random, maximum drawdown (R, and % at 0.5% risk per trade), the share of
profit from the top 5 trades, and results by daily-EMA200 regime (bull / bear / sideways) and by year.

## Pass rule (fixed now)

A variant is a **candidate for prospective testing** only if it passes both stages:

1. **BTC 2020 to 2026, primary cost**: at least 100 trades, expectancy > 0 with t ≥ 2, Holm-adjusted p ≤ 0.05,
   p_random ≤ 0.05, and expectancy > 0 at stress cost.
2. **ETH replication, primary cost**: at least 50 trades, expectancy > 0, and p_random ≤ 0.05.

Passing would justify a forward paper test under the sequential design of `research/donchian_validation/PROTOCOL.md`.
It would **not** justify live trading. If nothing passes, the finding is that RSI + VWAP entries show no reliable edge.
