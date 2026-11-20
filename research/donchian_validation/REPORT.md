# Independent validation: Donchian 20 BUY on BTC

Date: 2026-11-10. Paper research only. No order was placed, and no account was connected.

## Verdict: reject as a trading edge

The Donchian 20 breakout does not show a genuine, repeatable timing edge, and it should not be developed further or
traded live.

The decisive test is new in this validation. Random entries taken under the same 4H trend filter, with the same exit
rule, costs, one-position rule and number of trades, earn almost as much as the breakout signal. The breakout adds
about +0.04R per trade over random timing. That is not statistically distinguishable from zero, and confirming it
would take about 24,000 trades.

The strategy's positive backtest is real arithmetic, but it is not explained by the breakout. It is the reward for
being long BTC while the trend filter is on, with a trailing stop, during 2020 to 2026. Three other findings point the
same way:

- **Not robust to multiple testing.** The candidate was chosen from 48 variants. After accounting for that choice the
  development-period evidence is no longer significant (family-wise p = 0.14).
- **Profit is concentrated.** Removing the 10 best of 570 trades, under 2%, removes all profit. The positive holdout
  result is one trade.
- **Regime-dependent.** The holdout profit came from rallies inside a bear market; in bull-regime holdout trades it lost money.

This does not prove the breakout is worthless. It means the available evidence is consistent with no timing edge,
and no feasible forward test can show otherwise. The forward paper test continues unchanged as committed, as an
operational exercise and a cheap way to catch a much better result than expected.

## 1. Forward paper test: continuing unchanged

The 40-trade paper test is running exactly as frozen. An hourly scheduled task owned by the session that created it
runs `daily_update.py` and commits to branch `claude/download-skill-27d08k`. It is enabled, with its next run at
01:06 UTC. The latest recorded update, at 00:15 UTC on 2026-11-10, shows 0 trades and 0 signals so far.

This validation did not run, modify or duplicate it. Running it from a second session would process the same
candles twice and push to a branch this session does not own. The frozen files were verified byte for byte against
the freeze commit `ce2e8c57` before every analysis.

## 2. Backtest audit

All figures use the frozen engine and data, read from commit `f1798b71`. A replica of the trade simulator was
written for the sensitivity tests. It reproduces all 570 frozen-engine trades exactly: entries, exits, R values
and regime labels, across all 11 walk-forward windows, the holdout and a continuous run.

Baseline (continuous run, Binance research data, 0.05% round-trip cost):

| Period | Trades | Win rate | Profit factor | Expectancy | 95% CI | t | p | Max drawdown | Longest losing streak |
|---|---|---|---|---|---|---|---|---|---|
| Development 2020-01 to 2025-06 | 471 | 34.4% | 1.42 | +0.222R | +0.03 to +0.43 | 2.20 | 0.014 | 20.5R (9.9%) | 10 |
| Holdout 2025-07 to 2026-11 | 99 | 33.3% | 1.43 | +0.246R | −0.25 to +0.98 | 0.77 | 0.22 | 11.0R (5.4%) | 8 |
| All | 570 | 34.2% | 1.42 | +0.226R | +0.04 to +0.43 | 2.26 | 0.012 | 26.6R (12.6%) | 10 |

The same frozen rules on Exness BTCUSDm bid/ask quotes, paying the real spread plus 0.02% slippage:

| Period | Trades | Win rate | Profit factor | Expectancy | 95% CI | t | p |
|---|---|---|---|---|---|---|---|
| Development | 492 | 31.3% | 1.28 | +0.159R | −0.02 to +0.36 | 1.62 | 0.053 |
| Holdout | 99 | 32.3% | 1.35 | +0.198R | −0.27 to +0.90 | 0.66 | 0.26 |
| All | 591 | 31.5% | 1.29 | +0.165R | −0.01 to +0.36 | 1.73 | 0.042 |

Drawdown percentages assume 0.5% of equity risked per trade, as in the frozen test.

| Audit item | Finding | Impact |
|---|---|---|
| **Look-ahead bias** | None found. The 4H filter was re-implemented independently and agrees on every bar. 90 decisions were rebuilt from data truncated at the decision time, with 0 mismatches. Every entry is at the signal candle's close, and trailing stops use only closed 1H candles. | None |
| **Data leakage** | No numeric leakage. There is selection leakage: the forward candidate was picked after the holdout had been seen, from three survivors. The same 2025-07 to 2026-11 period was reused as the "final test" of the signal comparison study, and earlier Supertrend research also used part of it. The holdout is not an untouched confirmation. | Holdout p-values are optimistic |
| **Overlapping trades** | None. One position at a time, and 0 trades were cut short by window ends. | None |
| **Dependence between trades** | No serial correlation in results (Ljung-Box p = 0.53 development, 0.98 holdout). A runs test is borderline in development only (p = 0.047). Trades cluster in time (variance 18 against a mean of 7 per month), but a month-block bootstrap gives intervals no wider than the plain bootstrap. | Not inflating significance |
| **Multiple testing** | Ranked 5th of 48 variants by monthly t. Single-test p = 0.004 to 0.014, but White's Reality Check over the 48 gives p = 0.14, Holm 0.60 and Bonferroni 0.67. Six of the 48 variants reached t ≥ 2. The real family is larger still: a 36-setting neighbourhood, the 24-strategy comparison and earlier phases are not counted. | **Not significant after correction** |
| **Regime dependence** | See section 3. Positive in 10 of 14 half-years, negative in 2022 and 2025. | Material |
| **Execution assumptions** | The research assumes instant entry at the signal close and stop fills exactly at the stop price, at 15-minute resolution. See section 4. | About −0.06 to −0.10R |

## 3. Concentration of profits and regimes

| Period | Total R | Top 5 trades | Top 5 as share of net profit | Trades whose removal makes total ≤ 0 | Expectancy without top 5 |
|---|---|---|---|---|---|
| Development | +104.4R | +64.7R | 62% | 10 (2.1% of trades) | +0.085R (t 1.07) |
| Holdout | +24.4R | +45.7R | 188% | **1** | −0.227R (t −1.92) |
| All | +128.7R | +82.9R | 64% | 11 (1.9%) | +0.081R (t 1.12) |

The holdout is profitable only because of one trade: the entry on 2026-08-19, +28.1R in 46 hours. It appears in
both the Binance and Exness data. Without it, the holdout expectancy is −0.04R.

Long-tailed profits are normal for trend following, and the random-entry benchmark below shows the same shape.
The concentration is therefore not a defect in itself. But it means the result rests on rare events, and any
period without one loses money.

| Regime at entry | Development | Holdout | All |
|---|---|---|---|
| Bull | +0.20R (382 trades) | **−0.05R (56)** | +0.17R (438) |
| Bear | +0.46R (60) | +0.69R (39) | +0.55R (99) |
| Sideways | +0.00R (29) | +0.08R (4) | +0.01R (33) |

| Year | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Expectancy | +0.47R | +0.13R | −0.09R | +0.51R | +0.17R | −0.21R | +0.42R |
| Trades | 103 | 86 | 36 | 89 | 104 | 88 | 64 |

No regime result is individually significant. All 95% intervals include zero. Profitability did not survive the
bull regime in the holdout, and sideways markets contribute nothing.

## 4. All-in trading costs

| Cost item | Evidence | Effect per trade |
|---|---|---|
| **Bid/ask spread** | Measured from every Exness BTCUSDm quote. The median fell from 0.21% of price in 2019 to 0.017% in 2026. | 0.06R average in development, 0.02R in the holdout |
| **Commission** | Standard account: none (unverified; Exness pages block automated access). A Raw-type 8 USD per lot round trip would cost: | −0.02R |
| **Swap** | **Unverified.** 60% of trades are held over a rollover, averaging 1.16 swap-days including Friday triples. | Break-even at about **0.21% of price per swap-day** |
| **Admin fee** | Reported but unverified: 50 USD per lot per night on swap-free BTC. Applied once per swap-day, it would remove nearly all of the edge. | +0.165R → **+0.02R** |
| **Slippage on stops** | Not in the research model. 0.05% or 0.10% of price on every stop exit costs: | −0.04R or −0.08R |
| **Execution delay** | Measured from ticks on 254 Exness entries since 2024: the ask rises after a breakout. A delay of 5 to 60 seconds costs 0.02R. Entering 15 minutes late costs about 0.05R on both data sources. | −0.02R (seconds), −0.05R (15 min) |

Realistic all-in estimate: Exness quotes, 0.02% slippage, 0.05% stop slippage and no swap. That gives +0.125R per
trade over all 591 trades (t = 1.30), and +0.139R in the holdout (t = 0.46). Any swap or admin fee comes on top.

## 5. Matched random-entry benchmark (decisive)

Random entries were generated with everything matched except the breakout trigger:

- the same 4H filter state (only hours when the 4H close is above its EMA200);
- the same exit rule (2 × ATR stop, 3 × ATR trail, identical simulation);
- the same costs;
- one position at a time, walking forward in time exactly as the strategy does;
- the same number of trades in every calendar quarter;
- 2,000 runs, with a fixed seed.

The resulting exposure is close to the strategy's: time in market within 6%, and 78% of trades in the bull regime
against 77% for the strategy.

| Data, period | Strategy | Random entry (mean) | Random, 5th to 95th percentile | Excess | Probability random does as well |
|---|---|---|---|---|---|
| Binance, development | +0.222R | +0.182R | +0.08 to +0.29 | +0.040R | 0.27 |
| Binance, holdout | +0.246R | +0.171R | −0.07 to +0.49 | +0.075R | 0.31 |
| Binance, all | +0.226R | +0.180R | +0.08 to +0.28 | +0.046R | 0.23 |
| Exness quotes, all | +0.141R | +0.104R | +0.01 to +0.20 | +0.037R | 0.25 |
| Binance, all, no trend filter | +0.226R | +0.165R | +0.06 to +0.27 | +0.061R | 0.18 |

Random entries even had a slightly higher win rate (34.9% against 34.2%). Year by year, strategy and random entries
rise and fall together. The strategy is never significantly better in any year, and in 2025 it did worse
(−0.21R against +0.01R). Even random entries without the trend filter earn about the same, so neither the breakout
nor the filter shows a measurable contribution. The return comes from long exposure with a trailing stop on this
particular BTC price path.

A first version of this benchmark was wrong, and the error flattered the strategy. It drew random hours and then
discarded any that overlapped an accepted trade. That systematically discards long trades, which are the big
winners, and it showed the strategy beating random entry by +0.31R with p = 0.0005. The corrected benchmark walks
forward in time like the strategy. A test in `tests/` now demonstrates the bias. The signal comparison study's
random benchmark accepted trades in time order, so it did not have this bias, and its result for this strategy was
consistent: random entry did as well 12% of the time.

## 6. Prospective validation protocol

The full pre-registered protocol is in [`PROTOCOL.md`](PROTOCOL.md). The essentials:

- **40 trades is an operational checkpoint only.** If the true edge equals the backtest's, a 40-trade average is
  still negative 36% of the time. With no edge at all, it beats the backtest average 30% of the time.
- **The sample size follows from the uncertainty, not a round number.** One trade's result varies by about 2.3R.
  Confirming a +0.15R absolute edge needs about 1,950 trades, or 23 years. Confirming the measured +0.04R timing
  edge needs about 24,000 trades.
- **Design.** Looks every 40 trades, up to 480 (about 5.6 years). Efficacy boundaries control false positives at
  2.5%. Futility and harm boundaries allow an early rejection. If there is no timing edge, the test stops by trade
  240 (about 3 years) with 53% probability.
- **Sufficient evidence for a small live pilot** requires all three of: the relative-edge boundary crossed, absolute
  expectancy above zero at verified Exness costs, and no harm boundary. Anything less is "continue" or "reject".
- `src/evaluate_forward.py` applies the protocol to the forward ledger read-only. Today it reports 0 of 40 trades,
  so no look has been reached.

## 7. Recommendation

1. **Reject the Donchian breakout as a trading edge.** Do not trade it live. Do not tune it either: changing the
   channel length or stops would add to the multiple-testing problem, not fix it.
2. **Let the forward paper test run to its 40-trade checkpoint unchanged**, and judge it only by `PROTOCOL.md`.
   It cannot rescue the strategy at trade 40.
3. **If research continues,** the hypothesis that deserves testing is not the breakout. It is whether trend-filtered
   long exposure with a trailing stop beats simpler exposure to BTC, such as buy-and-hold at the same average risk.
   That is a new hypothesis. It needs its own pre-registration and data not used here, such as other assets or the
   forward period. Note that this exposure lost money in 2022 and 2025.
4. **Before any future live use of anything,** obtain the BTCUSDm swap, commission and admin-fee terms from MT5.
   A plausible swap or admin fee could exceed the whole historical edge.

## Limitations

- Stops are evaluated on 15-minute candles. Real fills during fast moves can be worse; this is partly covered by the stop-slippage scenarios.
- The random benchmark uses the same BTC price path as the strategy. It answers whether the trigger timed entries
  better than chance on this path. It cannot say whether the path itself, a 1,400% rise in development, will repeat.
- Exness swap, commission and admin fee are unverified. The Exness public tick archive may differ slightly from
  the quotes on a given account type.
- Regime labels come from the daily EMA200. Bear-regime samples are small.

## Reproducing

See [`README.md`](README.md). Every number in this report comes from `reports/validation.json`,
`reports/protocol_design.json` and `reports/tick_latency.json`.
