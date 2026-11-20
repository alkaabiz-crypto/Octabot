# Batch 001 pre-registration (committed before any result was computed)

Date: 2026-11-12. The protocol, costs, periods, benchmarks and decision rules are in `../PROTOCOL.md`. Each experiment below has exactly one pre-set parameter setting. Each family was checked as untested in both research branches (see `../README.md`).

## D001 Statistical-arbitrage pairs (spread mean reversion)

**Hypothesis.** Some pairs are tied by economics, so deviations of their relative price tend to revert, because arbitrageurs and hedgers close the gap:
- Brent and WTI: physical arbitrage and transport costs;
- EUR/USD and GBP/USD: both priced against the same USD and with correlated European economies;
- S&P 500 and Nasdaq 100: overlapping constituents.

**Evidence.**
- Gatev, Goetzmann and Rouwenhorst (2006, *Review of Financial Studies*), "Pairs Trading: Performance of a Relative-Value Arbitrage Rule".
- Vidyamurthy (2004), *Pairs Trading*.
- On the Brent–WTI spread: Büyükşahin et al. (2013), "Physical markets, paper markets and the WTI-Brent spread", *Energy Journal*.

**Pairs (A/B).** UKOILm/USOILm, EURUSDm/GBPUSDm, USTECm/US500m.

**Rules.**
- *Signal.* 1-hour mid closes, using only hours where both legs have a candle. Spread s = ln(A) − ln(B), equal notional on each leg. z = (s − mean)/sd over the previous 480 hourly bars, with the current bar included in neither.
- *Entry.* When z ≥ +2: **sell A, buy B**. When z ≤ −2: **buy A, sell B**. Entry at the next 15-minute open of both legs.
- *Exit*, at the first of:
  - z crosses 0;
  - |z| ≥ 4 (stop);
  - 120 hours held.

  Execution at the next 15-minute open. One position at a time per pair.
- *Return.* The average of the two legs' returns (each at its own bid/ask), in bp of gross notional.

**Benchmark.** 1,000 runs. In each run, every actual trade's direction and holding time is placed at a random hourly start within the same period.

**Simple benchmark.** None: the pair is market-neutral.

**Diagnostics** (no effect on the decision): oil roll jumps, meaning hours where |Δs| exceeds 6 × its rolling sd. They are reported together with how many trades span them.

## D002 Cross-market relative strength (11 markets)

**Hypothesis.** Assets that recently outperformed, measured on a risk-adjusted basis, keep outperforming over the following weeks. The suggested causes are slow information diffusion and investor flows.

**Evidence.**
- Asness, Moskowitz and Pedersen (2013, *Journal of Finance*), "Value and Momentum Everywhere".
- Moskowitz, Ooi and Pedersen (2012, *Journal of Financial Economics*), "Time Series Momentum", on the cross-section of futures.

**Rules.**
- *Snapshots.* Daily mid at 21:00 UTC (the close of the 20:45 candle). Days with fewer than 8 markets quoted are skipped.
- *Signal.* Each Monday, for every market with 61 daily snapshots: score = 60-day log return / (sd of daily log returns over the same 60 days × √60).
- *Positions.*
  - Long the top 3 by score, short the bottom 3.
  - Inverse-volatility weights, scaled so each side totals 1 (gross 2).
  - Held until the next Monday 21:00 UTC.
- *Costs.* Charged on weight changes only: (half the median spread + slippage) as a fraction of price, times the weight change, per market.
- *Metric.* Weekly portfolio return.

**Benchmark.** 1,000 runs in which the market ranks are shuffled every week, with the same weighting rules.

**Simple benchmarks.** Equal-weight long all, and the long top-3 side alone.

## D003 Regime-adaptive trend / mean reversion (11 markets, 4-hour)

**Hypothesis.** Trend-following works when price moves efficiently in one direction, and mean reversion works in choppy markets. Switching between them by regime should beat using either one always. This is an original combination; its parts are well documented.

**Evidence.**
- Kaufman (2013), *Trading Systems and Methods*, on the efficiency ratio.
- Documented regime dependence of trend and reversal profits, for example Daniel and Moskowitz (2016, *Journal of Financial Economics*) on momentum crashes in choppy rebounds.

**Rules.** 4-hour mid candles (UTC-aligned, 00/04/08/12/16/20). At each close:
- Efficiency ratio ER = |c(t) − c(t−20)| / Σ|c(i) − c(i−1)| over the last 20 candles.
- **Trend regime** (ER ≥ 0.35): position = sign(c(t) − c(t−20)).
- **Range regime** (ER ≤ 0.15): z = (c(t) − SMA20)/sd20. Short if z ≥ 1.5, long if z ≤ −1.5, otherwise flat.
- **Otherwise**: flat.

The position applies from the next 15-minute open to the following 4-hour candle's open. Consecutive candles in the same direction are one trade, and costs are paid only when the position changes.

**Benchmark.** 1,000 runs in which each trade's sign is flipped at random, with timing and length unchanged.

**Information only**: the trend-only and range-only parts reported separately.

## D004 Walk-forward machine-learning direction model (11 markets, 1-hour)

**Hypothesis.** A simple, regularised model that combines several weak price features (momentum, volatility, efficiency, distance from the recent mean, time of day) might predict the next few hours' direction better than any one indicator. This is the "combination of indicators" idea, tested honestly with walk-forward training.

**Evidence.**
- Gu, Kelly and Xiu (2020, *Review of Financial Studies*), "Empirical Asset Pricing via Machine Learning": machine-learning gains come mainly from combining many weak signals.
- Krauss, Do and Huck (2017).

The scepticism about short-horizon predictability is noted too.

**Rules.**
- *Features* at each 1-hour mid close:
  - log returns over 1, 4 and 24 hours;
  - sd of 1-hour returns over 24 hours;
  - efficiency ratio over 20 hours;
  - (close − mean of the last 24 closes) / that sd;
  - sin and cos of the UTC hour.
- *Target.* The sign of the log return from the next open to the open 4 hours later.
- *Model.* L2-regularised logistic regression (λ = 1, standardised features). Refit at the start of every calendar month on all data before that month (expanding window, from 2023-01). The first predictions are for 2023-07, which lie in TRAIN.
- *Trade.*
  - Long if the predicted probability is ≥ 0.55, short if it is ≤ 0.45.
  - Entry at the next 15-minute open, exit 4 hours later.
  - No new trade while one is open.

**Benchmark.** Random signs on the same trades, 1,000 runs.

## Statistics and decision

- **Tests.** D001 (3 pairs), D002 (1 portfolio), D003 (11 markets) and D004 (11 markets) give 26 TEST-period p-values. They get Benjamini–Hochberg at 5%, and the decision rules of `../PROTOCOL.md` section 10.
- **Also reported, without affecting decisions:**
  - each result's 2025-01-onward slice, because the other research branch works only with data from 2025;
  - profit factor, max drawdown and the 95% CI of the mean.
