# Pre-registered protocol: RSI + VWAP entries on US crude oil (USOILm)

Written on 2026-11-10 at about 08:00 UTC, before any USOILm candle was downloaded or any result was computed. The period was changed at about 08:10 UTC, still before any result. Paper
research only. Nothing in the earlier studies, the signal assistant or the frozen Donchian forward test is changed.

## Question

The BTC/ETH study (`research/rsi_vwap_study`) found one candidate: **VWAP momentum BUY with the trailing-stop exit.**
Does that rule work on US crude oil, a market it was never tested on? The other seven RSI + VWAP variants are run as
well, but only as exploratory results.

The textbook settings are applied unchanged. They are not assumed to suit oil: the point is to find out whether they
do, without tuning anything to oil.

## Data

- **Source.** The Exness public tick archive, symbol USOILm, every bid and ask quote from 2024-03 to the latest
  available quote in November 2026. Quotes are aggregated into 15-minute bid and ask candles with tick counts. 1H and daily candles
  are built from the 15-minute bid candles on UTC boundaries. Nothing is interpolated.
- **Statistics period: 2025-01-01 to the last available candle.** This was changed on request, before any oil result
  was computed (the first draft used 2020 onward). 2024-03 to 2024-12 is used only to warm up the indicators. No
  trade is entered or counted before 2025-01-01. The daily EMA200 behind the regime labels needs about 10 months
  of history.
  - Results are also shown separately for 2025 and 2026, for description only.

### Power warning (written before any result)

About 22 months of data is short. Suppose oil had the same edge as BTC (+0.17R per trade, standard deviation about
2.3R) and produced 150 to 300 trades. The expected t-statistic would then be about 0.9 to 1.3, so the t ≥ 2 rule
would pass only about 15 to 25% of the time. **A pass would be meaningful; a fail would be weak evidence against the
rule, not proof that it does not work.**

## Indicators (1H bid candles, textbook settings)

- **RSI 14**: Wilder's RSI.
- **ATR 14**: Wilder's ATR, used only to size the stop.
- **Session VWAP.** Oil trades in sessions with a daily break, so VWAP is anchored at each session open. A new
  session starts at the first 1H candle after a gap of at least 1 hour with no candle. Weights are the tick counts:
  "tick volume", because a CFD has no exchange volume. Typical price is (high + low + close) / 3.

## Entry rules and exits

These are identical to `research/rsi_vwap_study/PROTOCOL.md`, with "same session" meaning the session defined above.

| Rule | BUY | SELL |
|---|---|---|
| **V1 VWAP momentum** | Close crosses above session VWAP and RSI 14 > 50 | Close crosses below session VWAP and RSI 14 < 50 |
| **V2 RSI reversion** | RSI 14 crosses up through 30 and close < session VWAP | RSI 14 crosses down through 70 and close > session VWAP |

- **TRAIL exit**: 2 × ATR stop, then a 3 × ATR trail at each 1H close.
- **SYM exit**: +1R target, −1R stop, or 48 hours.

2 rules × 2 directions × 2 exits = 8 variants.

## Execution and costs (real bid/ask)

- **Entry.** At the first 15-minute candle after the signal close. BUY pays the ask open; SELL receives the bid open.
- **Stops.** A BUY is closed at the bid, so its stops trigger and fill on bid prices. A SELL is closed at the ask, so
  its stops use ask prices. A gap through the stop fills at the candle's opening quote.
- **Measured spread.** Included in every result through these fills.
- **Primary cost.** The measured spread plus 0.02% of price slippage per round trip.
- **Stress cost.** The measured spread, plus 0.05% slippage, plus 0.02% of price per calendar day held for swaps.
  Exness oil swaps are unverified.

## Benchmark

Matched random entry: the same direction, exit, costs and one-position rule, and the same trades per calendar
quarter. 2,000 runs, using the sequential sampler.

## Pass rule (fixed now)

**Primary hypothesis: V1 VWAP momentum, BUY, TRAIL.** It is a single pre-specified test, so there is no
multiple-testing adjustment. It **transfers to oil** only if, over 2025-01 to the last candle at primary cost:

- there are at least 100 trades;
- expectancy is above 0 with t ≥ 2;
- p_random ≤ 0.05;
- expectancy is above 0 at stress cost.

The other 7 variants are exploratory. They are reported with Holm-adjusted p-values across all 8, and none of them
can produce a recommendation from this study alone.

Even a pass would only justify a frozen forward paper test, not live trading.
