# RSI + VWAP entries on US crude oil (USOILm), 2025-01 to now

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any oil result existed. The period
was changed on request to 2025-01 onward, also before any result. Nothing in the earlier studies, the signal assistant
or the frozen Donchian forward test was changed.

## Verdict: RSI + VWAP entries do not work on US oil

**The BTC/ETH candidate does not transfer.** VWAP momentum BUY with the trailing exit made −0.008R per trade over
263 trades, and random entries under the same conditions did slightly better (+0.018R). It fails the pre-registered
test. None of the other seven RSI + VWAP variants showed an edge either. All Holm-adjusted p-values are 1.0, and none
beats random entry.

The sample is short. About 22 months gives a 95% interval of −0.18R to +0.18R for the main rule, so an edge the size
of BTC's (+0.17R) cannot be completely ruled out. But the best estimate is zero, and there is nothing here to support
trading it.

## Data and costs

- **Data.** Exness USOILm, every bid and ask quote, aggregated to 15-minute bid/ask candles. Statistics cover
  2025-01-01 to 2026-11-09. 2024-03 to 2024-12 was used only to warm up the indicators.
- **Market context.** Oil rose 19% over the period. 2025 was mostly a bear regime; 2026 was mostly a bull regime.
- **Fills.** Real spread: buy at the ask, sell at the bid, stops on the side that closes the position. The median
  spread was 0.027% of price.
- **Costs.** Primary: plus 0.02% slippage. Stress: plus 0.05% slippage and 0.02% per day held for swaps, which are
  unverified for Exness oil.
- **Indicators.** VWAP is anchored at each session open (22:00 or 23:00 UTC) and weighted by tick counts, because a CFD
  has no exchange volume. RSI 14 and ATR 14 use textbook settings, with nothing tuned to oil.

## Results, 2025-01 to now (primary cost)

| Variant | Trades | Win rate | Profit factor | Expectancy | 95% CI | t | Random entry | p vs random | Max drawdown | Stress cost |
|---|---|---|---|---|---|---|---|---|---|---|
| **VWAP momentum BUY, trail (primary)** | 263 | 36.1% | 0.98 | −0.008R | −0.18 to +0.18 | −0.09 | +0.018R | 0.67 | 26.2R (12.5%) | −0.053R |
| VWAP momentum BUY, ±1R | 368 | 51.4% | 1.03 | +0.016R | −0.09 to +0.12 | 0.31 | −0.008R | 0.28 | 9.7R (5.0%) | −0.019R |
| VWAP momentum SELL, trail | 255 | 31.0% | 0.83 | −0.101R | −0.28 to +0.09 | −1.07 | −0.084R | 0.60 | 47.7R (21.5%) | −0.146R |
| VWAP momentum SELL, ±1R | 343 | 44.6% | 0.76 | −0.132R | −0.24 to −0.03 | −2.48 | −0.093R | 0.81 | 49.8R (22.3%) | −0.167R |
| RSI reversion BUY, trail | 87 | 32.2% | 0.63 | −0.196R | −0.41 to +0.04 | −1.73 | −0.063R | 0.82 | 17.1R (8.3%) | −0.237R |
| RSI reversion BUY, ±1R | 87 | 51.7% | 1.07 | +0.031R | −0.17 to +0.23 | 0.30 | −0.028R | 0.26 | 7.2R (3.5%) | −0.001R |
| RSI reversion SELL, trail | 105 | 30.5% | 0.90 | −0.064R | −0.38 to +0.28 | −0.38 | −0.122R | 0.32 | 28.1R (13.2%) | −0.111R |
| RSI reversion SELL, ±1R | 104 | 46.2% | 0.76 | −0.135R | −0.36 to +0.08 | −1.20 | −0.111R | 0.59 | 18.5R (9.0%) | −0.170R |

1R is 2 × ATR14 at entry. Drawdown percentages assume 0.5% risk per trade. "p vs random" is the share of 2,000
matched random-entry runs that did at least as well.

### The primary rule by year and regime

| Slice | Trades | Expectancy |
|---|---|---|
| 2025 | 138 | −0.136R |
| 2026 | 125 | +0.132R (depends on its 5 best trades; −0.12R without them) |
| Bull regime | 100 | −0.025R |
| Bear regime | 126 | −0.072R |
| Sideways regime | 37 | +0.251R (too few trades to mean anything) |

The rule lost in 2025, gained in 2026 only through a handful of trades, and lost in both bull and bear regimes.

## What this means

- **Don't use RSI + VWAP entries on US oil**, in either direction.
- **The BTC/ETH result looks crypto-specific**, or simply lucky. Oil gave no support to it. That is consistent with the
  earlier signal comparison study, where no tested approach worked on UK oil either.
- A longer oil history (the archive goes back to 2019) would narrow the interval. But that would be a new study with
  its own pre-registration, not a re-run of this one.

## Reproducing

```bash
cd research/oil_rsi_vwap
python src/build_bars.py USOILm 2024-03 2026-11 data/USOILm_15m.csv.gz /tmp/usoil_parts   # rebuilds the data
python src/run_oil.py                                     # about 1 minute; writes reports/results.json
python -m unittest discover -s tests -p "test_*.py"
```

The engine reuses the indicator, statistics and random-benchmark code of `research/rsi_vwap_study` (read-only).
All random procedures use seed 20261110.
