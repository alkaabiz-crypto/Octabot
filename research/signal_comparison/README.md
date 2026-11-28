# Signal comparison: three approaches on BTCUSDm and UKOILm

Paper research only. No orders were placed. This project is separate from the Donchian forward test
(`research/btc_breakout/`, other branch) and from the signal assistant (`research/btc_signal_assistant/`).
Neither was modified. One test imports the assistant read-only to prove that approach A2 here reproduces its
BUY and SELL decisions exactly.

## Verdict

**No approach produced reliable BUY or SELL recommendations on either market under the pre-registered rule.**

- **BTC BUY** is the only place with any positive evidence, and only with the trailing-stop exit. In the
  walk-forward all three approaches earned between +0.15R and +0.25R per trade, but none of those results
  survives correction for the 24 strategies tested. In the final test the ranking reversed: the combined
  system, best in the walk-forward, lost money, while the plain Donchian rule stayed positive.
- **The plain Donchian 20 + 4H EMA200 rule (A1) was the most consistent.** It was positive in both periods
  with almost the same size (+0.16R, then +0.20R). It is still not statistically significant here.
- **The combined indicator system (A2) is not more reliable than A1.** Its extra filters looked helpful in
  the walk-forward and then failed in the final test (-0.28R over 69 trades).
- **The voting system (A3)** was positive but weak in both BTC periods (+0.15R, then +0.08R). Its textbook
  version passes the rule mechanically; see the caveat below. It should not be read as a reliable signal.
- **SELL signals were unreliable everywhere**, for every approach, on both markets.
- **UKOIL: nothing works.** All 24 strategy variants lost money in the walk-forward. The measured Exness
  spread costs about 0.15R per trade, which is larger than any edge found.
- **None of the approaches predicts direction.** With a symmetric +1R / -1R exit, win rates stayed between
  39% and 55% and were never significantly better than random entries. Where money was made, it came from
  a few large winners (win rate about 31%), not from being right more often.

## Headline numbers

Primary cost (measured spread + 0.02% slippage), trailing-stop exit, BUY signals. `sel` uses walk-forward
parameter selection; `txt` uses textbook settings.

| Market | Approach | Period | Trades | Win rate | Profit factor | Expectancy | t | p | Max drawdown |
|---|---|---|---|---|---|---|---|---|---|
| BTC | A1 Donchian (txt) | walk-forward | 492 | 31.3% | 1.28 | +0.159R | 1.62 | 0.053 | 20.2R |
| BTC | A1 Donchian (txt) | final test | 99 | 32.3% | 1.35 | +0.198R | 0.66 | 0.256 | 11.2R |
| BTC | A2 Combined (txt) | walk-forward | 359 | 31.2% | 1.46 | +0.255R | 2.04 | 0.021 | 12.5R |
| BTC | A2 Combined (txt) | final test | 69 | 23.2% | 0.57 | -0.283R | -1.90 | 0.969 | 23.6R |
| BTC | A3 Voting (txt) | walk-forward | 746 | 33.1% | 1.32 | +0.172R | 2.21 | 0.014 | 39.4R |
| BTC | A3 Voting (txt) | final test | 169 | 32.0% | 1.13 | +0.075R | 0.37 | 0.356 | 24.8R |
| UKOIL | A1 Donchian (txt) | walk-forward | 215 | 24.2% | 0.42 | -0.378R | -5.11 | 1.000 | 84.7R |
| UKOIL | A1 Donchian (txt) | final test | 84 | 42.9% | 1.34 | +0.161R | 0.86 | 0.196 | 8.5R |
| UKOIL | A2 Combined (txt) | walk-forward | 130 | 29.2% | 0.53 | -0.291R | -2.97 | 0.998 | 38.3R |
| UKOIL | A2 Combined (txt) | final test | 61 | 44.3% | 1.45 | +0.202R | 0.89 | 0.188 | 6.6R |
| UKOIL | A3 Voting (txt) | walk-forward | 323 | 32.5% | 0.79 | -0.118R | -1.64 | 0.949 | 61.2R |
| UKOIL | A3 Voting (txt) | final test | 134 | 29.1% | 0.92 | -0.048R | -0.32 | 0.627 | 13.3R |

Every Holm-adjusted p-value in the final test is 1.00. The smallest adjusted p-value in the walk-forward is
0.32. All 96 result rows (both directions, both exits, selected and textbook, with confidence intervals,
random-entry comparison, cost scenarios and regime splits) are in [`reports/RESULTS.md`](reports/RESULTS.md).

## What the details show

- **Regimes.** BTC BUY signals did not depend on a bull market the way one would expect. In the final
  test A1 made +0.66R per trade in the bear regime (38 trades, rallies inside a falling market) and lost
  -0.08R in the bull regime (57 trades). Sideways regimes were rare and mostly negative. Regime samples are
  small, so these are descriptions, not findings.
- **UKOIL final test.** A1 and A2 BUY were positive in the final test, during a +68% rise in oil and with
  much tighter spreads in 2026. This contradicts three and a half years of walk-forward losses and is not
  significant. It is not evidence of an edge.
- **Parameter selection did not help.** Choosing among fast, textbook and slow settings on past data gave
  results no better than textbook settings, on both markets. There is no sign that oil needs different
  indicator settings. The data says no tested setting overcomes oil's costs.
- **Costs.** BTC spread fell from about 0.21% of price in 2019 to about 0.02% in 2026, so old trades carry
  old costs. Replacing them with recent spreads raises BTC BUY expectancy by about 0.04R and changes no
  conclusion. Under the stress scenario the BTC BUY trailing results stay positive in the walk-forward.
- **The one mechanical pass.** A3 BUY with textbook settings and the trailing exit meets every pre-registered
  threshold. Its final-test result is +0.08R with t = 0.37, random entries did as well a third of the time,
  and its walk-forward p-value is 0.32 after Holm correction. One pass among 48 rows is what chance alone
  would produce. The primary, selected version of the same strategy fails.

## How the study was run

The full rules are in [`PROTOCOL.md`](PROTOCOL.md), written before any result existed.

- **Data.** Every bid/ask quote from the Exness public tick archive for BTCUSDm (2017-09 to 2026-11) and
  UKOILm (2020-01 to 2026-11), aggregated to hourly bid and ask candles. These are the instruments' own
  quotes, so the spread in the results is measured, not assumed. Checksums are in `data/SHA256SUMS`.
- **Approaches.** A1 is the Donchian breakout with the 4H EMA filter. A2 is the signal assistant's rule.
  A3 counts five indicator votes per timeframe and signals on a fresh alignment, with no breakout needed.
- **Parameters.** One time-scale factor (0.5, 1 or 2) applied to all look-backs, chosen per market and
  direction from past trades only, by t-statistic and never by return.
- **Execution.** Enter at the next hour's first quote, buying at the ask and selling at the bid. Stops
  trigger on the side of the quote that would actually close the position. Two exits: the trailing stop
  of the validated study, and a symmetric +1R / -1R exit that measures directional accuracy.
- **Testing.** Half-year walk-forward folds (11 for BTC from 2020, 7 for UKOIL from 2022), then a final
  test from 2025-07-01 to 2026-10-31. Stage 1 cannot load final-test candles. The parameter choices were
  locked with SHA-256 `bf391e23...fa3a`, committed and pushed, and the final test was then run once.
- **Statistics.** t-test and bootstrap interval on per-trade R, a 1,000-run random-entry benchmark with the
  same exit, Holm correction across the 24 strategies, and results split by bull, bear and sideways regime.

## Limitations

- Stops are checked on hourly candles. The earlier Donchian study used 15-minute candles, so fills differ slightly.
- Swaps and commission on Exness are unverified. They appear only in the hypothetical stress scenario.
- BTC history had been examined before for A1 and A2 (earlier study and the assistant's replay). No
  parameter was fitted there, but the BTC final period is not pristine for those two. A3 and all UKOIL
  data were new.
- The pass rule did not say whether it applies to the selected or the textbook variant. This was settled
  after stage 1 and before the final test: both are judged, the selected variant is primary, and both are shown.
- UKOIL has under seven years of data and one regime-heavy walk-forward (58% bear days).
- A final test of 50 to 170 trades cannot confirm an edge of 0.2R. It can only fail to contradict it.

## Recommendation

1. Keep the Donchian forward paper test running unchanged. It tests the one rule that stayed consistent.
2. Do not treat the signal assistant's BUY alerts as stronger than a plain Donchian breakout. This study
   found no reliability gain from the extra confirmations.
3. Do not act on SELL signals from any of the three approaches.
4. Do not trade UKOIL with any of these approaches.

## Reproducing

Python 3.13, standard library only.

```bash
cd research/signal_comparison
sha256sum -c data/SHA256SUMS
python -m unittest discover -s tests -p "test_*.py"   # 30 tests
python src/report.py                                   # rebuild reports/RESULTS.md from the result files
```

`src/run_walkforward.py` and `src/run_final.py <sha>` produced `reports/walkforward.json` and
`reports/final.json`. Both refuse to run again now that the final result exists. To repeat the study from
scratch, delete `reports/final.json` first. `src/fetch_exness.py` rebuilds the data from the tick archive.
Every trade is logged under `logs/`.
