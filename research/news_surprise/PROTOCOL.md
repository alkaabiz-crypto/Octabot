# Does the news itself tell which market will rise? (pre-registered)

Written before any result was computed. This is a separate module, and nothing in earlier studies is changed.

## The idea

Markets move on the surprise in a release, not on the release itself. Free consensus forecasts are not available historically:
- ForexFactory and FXStreet block automated access;
- TradingEconomics ended free access.

The surprise is therefore measured against the data's own recent past, using only the numbers **as first published**. These are ALFRED vintages from the St. Louis Fed: the value a trader saw at 08:30 New York time on release day.

| Release | Surprise score (known at the release) | "Hot" means |
|---|---|---|
| CPI | core CPI (CPILFESL) month-on-month change minus the average of the previous 6 months' changes, all from the release-day vintage | inflation above trend |
| NFP | payroll (PAYEMS) monthly change minus the average of the previous 3 changes, minus 100,000 × the change in the unemployment rate (UNRATE), each from the release-day vintage | jobs stronger than trend |

FOMC is left out. The decision is almost always expected, and the surprise needs fed-funds futures prices, which are not freely available.

## Strategy

At the release, take the sign of the surprise score. Enter at the next 15-minute open, 15 minutes after the release (an earlier entry would not be realistic). Hold until 4 hours after the release, with a 2 × ATR stop. Real Exness bid/ask plus 0.02% slippage (stress: 0.05% plus 0.02% per day).

Each market's direction for a hot reading is **learned in the fit period**: the sign of the average 4-hour move after hot readings minus the move after cool readings. That direction is then frozen for the test. For reference, the textbook expectation is that hot readings mean a stronger dollar and higher yields:
- gold, silver, EUR/USD, GBP/USD, stock indices, BTC and ETH fall;
- USD/JPY and USD/CAD rise;
- oil has no clear prior.

Variants: **ALL** trades every release. **BIG** trades only when the size of the score is above its fit-period median.

## Markets, periods, benchmark

- Markets: the same 14 as `research/news_markets`. Fit: 2020-07 to 2024-12 (2023-07 for markets with data from 2023). Test: 2025-01 to now.
- Benchmark: a permutation test. The surprise signs are shuffled among the same release days 2,000 times, which tests whether the surprise adds anything beyond the release-day move itself. One-sided p.
- Also reported: how often the first 15-minute move agrees with the surprise sign. This checks that the score captures what the market reacts to.

## Decision rule

There are 2 releases × 14 markets × 2 variants = 56 tests. Benjamini–Hochberg at 5% is applied over the test p-values of the combinations that passed fit (fit p ≤ 0.05, positive fit expectancy at stress cost, at least 15 trades). A combination is confirmed only if it survives that and is profitable at stress cost in the test period.

## Forward record

The weekly calendar shows a consensus forecast for each upcoming release. From now on the daily briefing will store the forecast, and the actual will be added when it is published. This builds a real consensus-surprise history for a later test.

## Addendum (after the 15-minute results were seen): how fast would you have to be?

The 15-minute test showed that the surprise sign predicts the direction of the **first** 15-minute candle, especially for NFP. This addendum asks whether a retail trader can capture that, using Exness tick data (every bid/ask quote).

- Markets: gold, EUR/USD, GBP/USD, USD/JPY.
- Releases: NFP and CPI, 2025-01 to now.
- Direction is the **textbook mapping**, so nothing is fitted: a hot reading means BUY USD/JPY and SELL gold, EUR/USD and GBP/USD.
- Entry at the first quote at least 1, 5, 15, 30, 60, 180 or 900 seconds after 08:30:00 New York time, at the ask for a buy and the bid for a sell.
- Exit at the first quote 15 minutes or 60 minutes after the release, at the bid for a buy and the ask for a sell. No stop.
- Result in pips-equivalent R (2 × ATR14 of the hour before), with real spread and no extra slippage.
- Reported as the average and the win rate at each delay, with a sign-flip test: the same trades with the surprise signs shuffled, 2,000 times.
- This shows how quickly the move happens. It is not a strategy to trade: real execution at release time also suffers requotes and slippage that tick data does not show.

## Addendum 2 (2026-11-12): the real consensus surprise

A free historical source of consensus forecasts turned up: a public Hugging Face dataset copied from the Investing.com calendar. It has the actual, forecast and previous values for US NFP, the unemployment rate and core CPI from 2020-02 to 2026-06. The extract is kept in `data/consensus_investing.csv`.

Every test above is repeated with the **consensus surprise** in place of the trend proxy. Nothing else changes: the same markets, strategies, fit and test split, permutation benchmark, decision rule and tick-delay test.
- **CPI:** core CPI month-on-month, actual minus forecast. An exact match means no trade.
- **NFP:** payrolls actual minus forecast (in thousands), minus 100 × (unemployment actual minus forecast). Zero means no trade.

The test period ends 2026-06, where the dataset ends. Results are written to `reports/*_consensus.*`.

## Addendum 3 (2026-11-12): out-of-sample check of the one lead

**The lead.** In 2025-01 to 2026-06, gold kept drifting in the textbook direction after the jobs report even for late entries. A strong surprise means SELL gold, a weak one means BUY. This showed with both surprise measures: entries at 30 s and 180 s, held to 15 minutes, gave about +0.2R. These results were seen before this check was written.

**The check.** One pre-specified test on gold tick data that has not been looked at: NFP releases from **2020-03 to 2024-12**, using the consensus surprise.
- Entry at the first quote at least 30 seconds after 08:30:00 (primary), and separately at least 180 seconds after (secondary).
- Exit at the first quote 15 minutes after the release.
- Real bid/ask, no stop. Sign-flip test with 2,000 shuffles, one-sided.

**Decision.** The lead holds only if the primary test has p ≤ 0.05 and positive expectancy, and the secondary has positive expectancy. If it fails, the lead is dropped.
