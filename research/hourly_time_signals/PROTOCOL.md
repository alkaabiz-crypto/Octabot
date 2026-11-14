# Pre-registered protocol: hourly time-of-day signals on oil, gold and BTC

Written on 2026-11-10, before any result of this test was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Question

Do the three hourly signals with published evidence work on Exness quotes after real costs?

## Signals (all times exact; US times follow US daylight saving)

| # | Signal | Source idea | Rule |
|---|---|---|---|
| **S1** | Oil intraday momentum | Gao, Han, Li & Zhou (2018); Wen et al. (2021) for crude | Each US trading day (Mon–Fri), take the "first half-hour" return: from the previous day's 14:30 New York price to today's 09:30 New York price. At 14:00 New York, enter in the direction of that return (BUY if positive, SELL if negative) and exit at 14:30 New York. |
| **S2a** | Gold Asian-hours long | Blose, Gondhalekar & Kort (2018); session studies | Each weekday (Mon–Fri), BUY at 00:00 UTC and exit at 07:00 UTC. |
| **S2b** | Gold US-hours short | Same papers (daytime gold returns negative) | Each weekday, SELL at 13:00 UTC and exit at 20:00 UTC. |
| **S3** | BTC late-evening long | Quantpedia hour-of-day study | Every day including weekends, BUY at 21:00 UTC and exit at 23:00 UTC. |

Prices are read at the open of the 15-minute candle that starts at each stated time. If that candle is missing (a
holiday or a session break), there is no trade that day.

## Fills and costs

- **Real bid/ask.** A BUY enters at the ask and exits at the bid; a SELL enters at the bid and exits at the ask.
- **Primary cost.** The measured spread plus 0.02% of price slippage per round trip.
- **Stress cost.** 0.05% slippage, plus 0.02% of price for any trade held across the daily rollover (21:00 UTC in
  northern summer, 22:00 UTC in winter). S3 always crosses it; S1, S2a and S2b never do.
- **Results** are in basis points (0.01%) of price per trade, net of costs.

## Benchmarks (1,000 runs each, seed 20261110)

- **S1:** the same days and the same window, but with a random direction on each day. This tests whether the sign of
  the first half-hour predicts the last half-hour.
- **S2a, S2b, S3:** the same days, the same direction and the same holding time, but starting at a random whole hour of
  that day. This tests whether these particular hours beat other hours, and controls for the market's overall trend.
  For example, gold rose 58%, so any long position made money.

p_random is the share of runs at least as good as the signal.

## Periods and pass rule

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm 15-minute bid/ask candles (the files of the earlier studies).
  2024 is warm-up only.
- **Selection:** 2025-01-01 to 2025-12-31. **Confirmation:** 2026-01-01 to the latest quote.
- **A signal is reliable** if, in both periods at primary cost:
  - mean net result > 0;
  - p_random ≤ 0.05;
  - at least 100 trades in 2025 and at least 60 in 2026.

Win rate, profit factor, t, and maximum drawdown are reported for every signal. Four signals are tested, so about one
pass in the first stage could be luck, which the confirmation stage guards against. Even a reliable signal would justify
only a frozen forward paper test.
