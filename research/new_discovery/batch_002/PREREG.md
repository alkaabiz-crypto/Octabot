# Batch 002 pre-registration (committed before any result was computed)

Date: 2026-11-12. Protocol, costs and periods follow `../PROTOCOL.md`, with the amendments below. Each hypothesis has one pre-set setting; every market counts as a separate trial.

## Duplication check

None of these families appears in this branch's earlier work (batch 001, the 33-market scans, the gold KST, news and ADP studies). None appears in the frozen theory library (63 executed theory IDs, freeze commit `9c158d62`) or in the other session's ORB, session, zone and shortlist studies. They are also **not** the hypotheses in the other session's batch-2 review (`research/batch2_review/REVIEW.md` on branch `claude/download-skill-27d08k`, commit `d42eb9fa`), which covers funding, basis, order flow, the volatility risk premium and FX carry. That review awaits the user's decisions and is not pre-empted here.

## Amendments for this batch

- **The TEST period is labelled "reused evaluation data."** As that review points out, 2025-07 onward was already inspected in batch 001 for the same target price series. A positive TEST result here is therefore **screening evidence only**. Promotion additionally requires a forward period that begins after this commit.
- **Dependence-aware statistics.** Daily-return strategies (E005, E007) use a stationary block bootstrap (mean block length 20 days, 2,000 resamples). Forecast comparisons (E006) use a Diebold–Mariano test with a Newey–West variance (5 lags).
- **Data-rule note.** The other session follows a rule of using data from 2025-01-01 only. This program uses 2023-01 onward, so that a train / validation / test split is possible, and it also reports a 2025-onward slice for every test.

## E005 Volatility-managed exposure (11 markets, daily)

**Hypothesis.** Volatility clusters, but expected returns do not rise proportionally with volatility. Scaling exposure inversely to recent volatility therefore raises risk-adjusted returns compared with constant exposure.

**Evidence.** Moreira and Muir (2017, *Journal of Finance*), "Volatility-Managed Portfolios"; Harvey et al. (2018, *Journal of Portfolio Management*), "The Impact of Volatility Targeting". The criticism by Cederburg et al. (2020, *Journal of Financial Economics*) is noted: the gains often vanish out of sample.

**Rules.**
- Daily mid snapshots at 21:00 UTC, with r(t) the daily log return.
- σ̂(t) = √(EWMA of r², λ = 0.94) using data up to t.
- Weight w(t) = min(2, σ\*/σ̂(t)), where σ\* is the median σ̂ over TRAIN, computed on TRAIN only and fixed per market.
- The position is held from t to t+1 (long only).
- Costs: |Δw| × (half the median spread + slippage), plus stress financing on |w| per day.

**Benchmark.** Constant weight equal to the strategy's average weight in the same period, so exposure is the same on average.

**Statistic.** Sharpe(strategy) − Sharpe(benchmark), with a block-bootstrap one-sided p.

## E006 HAR-RV versus EWMA volatility forecasts (11 markets, daily)

**Hypothesis.** Volatility has long memory. A heterogeneous autoregressive model of realised variance (daily, weekly and monthly components) forecasts next-day variance better than the RiskMetrics EWMA. If so, it is a better building block for sizing and filters.

**Evidence.** Corsi (2009, *Journal of Financial Econometrics*); Andersen, Bollerslev, Diebold and Labys (2003, *Econometrica*).

**Rules.**
- RV(t) = sum of squared 15-minute mid log returns within the day (21:00 to 21:00 UTC).
- **HAR:** RV(t+1) = b0 + b1·RV(t) + b2·RVw(t) + b3·RVm(t), where RVw and RVm are the 5-day and 22-day means. Fitted by OLS, refitted monthly on an expanding window from 2023-01, with the first forecast in 2023-07.
- **EWMA:** σ²(t+1) = 0.94·σ²(t) + 0.06·r(t)² (daily close-to-close returns).

**Loss.** QLIKE = RV/F − ln(RV/F) − 1.

**Statistic.** The Diebold–Mariano test for HAR having lower loss, one-sided, Newey–West with 5 lags.

**Not a trading rule.** It is a "component" test.

## E007 Two-state hidden-Markov regime filter (11 markets, daily)

**Hypothesis.** Returns alternate between a calm, positive-drift regime and a turbulent, low or negative-drift regime. Holding only when the calm regime is likely improves risk-adjusted returns.

**Evidence.** Hamilton (1989, *Econometrica*); Nystrup, Madsen and Lindström (2017, *Quantitative Finance*), "Dynamic portfolio optimization across hidden market regimes"; Ang and Bekaert (2002).

**Rules.**
- A Gaussian HMM with 2 states, fitted by EM (Baum–Welch, 100 iterations, 3 starting points, best likelihood kept) on daily log returns. Refitted at the start of each month on all data before that month, and only from 250 days of history.
- At each day's close, the filtered probability (forward algorithm, using data up to t only) of the state with the higher fitted mean.
- Long 1 if that probability is above 0.5, else flat, held from t to t+1. Costs as E005.

**Benchmark.** A constant weight equal to the fraction of days invested.

**Statistic.** The Sharpe difference, with a block-bootstrap p.

## E008 BTC → ETH lead-lag (15-minute)

**Hypothesis.** BTC is the more liquid price-discovery asset. After a large BTC move in which ETH has lagged, ETH catches up over the next 15 minutes.

**Evidence.**
- Sifat, Mohamad and Mohamed Shariff (2019, *Research in International Business and Finance*) on lead-lag between Bitcoin and Ethereum.
- The literature on lead-lag in cryptocurrency price discovery, for example Brandvold et al. (2015).

**Rules.**
- At each common 15-minute close, z(BTC) = BTC's 15-minute log return / the sd of its previous 96 returns.
- **Long ETH** if z(BTC) ≥ 2 and r(ETH) < 0.5·r(BTC). **Short ETH** if z(BTC) ≤ −2 and r(ETH) > 0.5·r(BTC).
- Entry at the next 15-minute open, exit at the following one.

**Second test.** The mirror rule (ETH leads → trade BTC).

**Benchmark.** Random signs on the same trades.

## E009 Pre-holiday effect (S&P 500, Nasdaq 100, DAX)

**Hypothesis.** Returns on the last trading day before an exchange holiday are abnormally high (investor mood, short covering before closures).

**Evidence.** Ariel (1990, *Journal of Finance*); Kim and Park (1994, *Journal of Financial and Quantitative Analysis*). Later studies report decay, so the hypothesis may well fail.

**Rules.**
- Holiday calendars from `holidays.financial_holidays`: NYSE for US500m and USTECm, XETR for DE30m. The pre-holiday day is the last weekday before a holiday that is itself not a holiday.
- **US indices:** buy at the 15-minute open at 16:00 New York time on the day before the pre-holiday day, and sell at the 16:00 New York open on the pre-holiday day (close to close).
- **DAX:** the same, at 17:30 Berlin.

**Benchmark.** 1,000 runs of the same number of close-to-close long days drawn at random from the same period's ordinary trading days.

## Statistics and decision

- **Number of tests.** 11 (E005) + 11 (E006) + 11 (E007) + 2 (E008) + 3 (E009) = **38 TEST-period tests**, with Benjamini–Hochberg at 5%.
- **Decisions** follow `../PROTOCOL.md` section 10, with Sharpe differences in place of mean bp for E005 and E007, and loss differences for E006.
- **Labels.** Because TEST is reused data, anything that would have been a CANDIDATE is labelled **SCREEN-PASS**. It then needs a forward period before the robustness batch and paper testing.
