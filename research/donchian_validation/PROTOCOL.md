# Prospective validation protocol: Donchian 20 BUY (BTC)

Pre-registered on 2026-11-10, before the forward paper test recorded its first trade (0 trades, 0 signals at 00:15 UTC).

This protocol is an evaluation layer on top of the frozen forward paper test. It changes nothing in that test:
not the rules, parameters, code, ledgers, schedule or its own `EVALUATION_RULES.md`. It is applied read-only by
`src/evaluate_forward.py`. Forward results are never used to choose or change any parameter.

## What is being tested

**Primary question (relative edge).** Does the Donchian breakout trigger choose better entry moments than random
entry under identical conditions? "Identical" means the same 4H trend-filter state, the same exit rule, the same
costs, one position at a time, and the same number of trades in the same period. Without this, a positive result
could just be the reward for being long BTC in a rising market.

**Secondary question (absolute edge).** Is the expectancy after all costs above zero?

Both questions are needed. A strategy can be profitable without having a timing edge, if the market rose while it
was invested. It can also have a timing edge and still lose money once costs are paid.

## Why 40 trades cannot decide anything

One trade's result has a standard deviation of about 2.3R. The edge being looked for is about 0.15 to 0.2R.
After 40 trades, the uncertainty of the average is about ±0.7R, several times larger than the edge itself.

Simulated from the real trade distribution:

| If the true edge is... | Chance the 40-trade average is negative | Chance it beats the backtest average |
|---|---|---|
| as large as the backtest (+0.165R) | 36% | 45% |
| zero | 55% | 30% |

A good strategy and a worthless one produce overlapping 40-trade results. Trade 40 is therefore an operational
checkpoint only (see below), never a profitability verdict and never permission to trade live.

## How many trades would be enough

Trades needed for 80% power at a one-sided 2.5% significance level. The forward test produces about 86 trades
per year.

| True effect | Trades needed | Years at 86 trades/year |
|---|---|---|
| Absolute +0.25R | 701 | 8 |
| Absolute +0.20R | 1,096 | 13 |
| Absolute +0.15R | 1,948 | 23 |
| Absolute +0.10R | 4,381 | 51 |
| Relative +0.30R over random entry | 423 | 5 |
| Relative +0.15R over random entry | 1,689 | 20 |
| Relative +0.04R over random entry (the size measured in the validation) | 23,752 | 275 |

These numbers are the core of the protocol. At the edge size the backtest actually supports, a paper test cannot
confirm the strategy within any useful time. What it can do in a few years is reject it, or reveal that it is
much better than the backtest suggested.

## Design

- **Looks:** after every 40 completed trades, in recorded order (40, 80, ..., 480). Nothing is evaluated between looks.
- **Maximum length:** 480 trades, about 5.6 years. This is the longest horizon at which a paper test still informs a
  decision. It gives 76% power for a +0.30R relative edge and only about 25% for +0.15R.
- **Efficacy boundaries:** O'Brien-Fleming shape, calibrated by simulation so the chance of a false "edge found"
  over all looks is 2.5%, one-sided. They are very strict early and relax towards the end.
- **Futility boundaries:** calibrated to lose at most 10% power at the design effect. They are non-binding, and
  none applies at the 40-trade checkpoint.
- **Harm boundary:** if cumulative R falls below −20R by trade 40, or the drawdown exceeds 22R × √(n/40), stop.
  Results that bad happen less than 1% of the time if the backtest were right.
- **Statistic:** the mean of `R_net_mid` from the forward ledger (Binance proxy, 0.05% round-trip cost). The relative
  test compares it with the mean of matched random entries over the same forward period. These are rebuilt from the
  same candles with seed 20261110 and 2,000 runs.

Stopping boundaries, expressed as the average R per trade at each look:

| Trades | Absolute: edge found if mean ≥ | Absolute: futility if mean < | Relative: edge found if excess ≥ | Relative: futility if excess < |
|---|---|---|---|---|
| 40 | +2.88R | none | +2.71R | none |
| 80 | +1.44R | −0.77R | +1.35R | −0.62R |
| 120 | +0.96R | −0.47R | +0.90R | −0.31R |
| 160 | +0.72R | −0.31R | +0.68R | −0.16R |
| 200 | +0.58R | −0.22R | +0.54R | −0.07R |
| 240 | +0.48R | −0.16R | +0.45R | −0.01R |
| 280 | +0.41R | −0.11R | +0.39R | +0.04R |
| 320 | +0.36R | −0.08R | +0.34R | +0.07R |
| 360 | +0.32R | −0.06R | +0.30R | +0.10R |
| 400 | +0.29R | −0.03R | +0.27R | +0.12R |
| 440 | +0.26R | −0.02R | +0.25R | +0.13R |
| 480 | +0.24R | +0.24R | +0.23R | +0.23R |

The exact z-boundaries are in `reports/protocol_design.json`. `src/evaluate_forward.py` uses those values.

Simulated operating characteristics of the relative test:

| Truth | Edge found within 480 trades | Average trades until stopping | Stopped by 240 trades |
|---|---|---|---|
| No timing edge | 2.4% (false positive) | 270 | 53% |
| +0.30R timing edge | 76% | 359 | 18% |
| +0.15R timing edge | 26% | 439 | n/a |

## What evidence is sufficient, and why

| Outcome | Requires | Meaning |
|---|---|---|
| **Reject** | Relative futility crossed, or harm boundary crossed, or 480 trades without relative efficacy | Stop developing this strategy. |
| **Continue paper testing** | No boundary crossed | No decision is possible yet. |
| **Consider a small live pilot** | Relative efficacy crossed, AND absolute expectancy above zero at the lower one-sided 90% bound using verified Exness costs (spread, commission, swap or admin fee), AND no harm boundary crossed | Evidence that the trigger adds value beyond market exposure, and that it survives real costs. The pilot would be a new pre-registered study at minimum size. |
| **Edge established** | Absolute efficacy crossed at verified costs | Strong evidence. For edges of +0.15R this needs about 2,000 trades, so it is not expected within the test horizon. |

The relative test comes first because the validation found that random entries under the same filter and exit
earn almost as much as the strategy. Profit without a timing edge is the reward for holding BTC through rises.
That reward is available more cheaply and more transparently by other means, and it disappears in falling markets.
The absolute test at verified costs comes second, because a timing edge smaller than the costs is useless. Neither
is replaced by a fixed trade count: the boundaries already account for how uncertain the average is at each sample size.

## 40-trade operational checkpoint

At trade 40 (about six months), review only:

1. **Integrity:** the independent audit reports 0 CRITICAL and 0 DISCREPANCY findings. The candles match Binance. The ledgers are append-only.
2. **Execution fidelity:** compare each paper entry with the Exness ask at the same moment, using the monthly tick
   archive. The validation measured about +0.02R of extra cost from a 5 to 60 second delay. Material differences mean the cost model must be revised.
3. **Costs:** record the real BTCUSDm specification from MT5. This covers commission, swap long, the triple-swap day,
   swap-free status and any admin fee. The validation's break-even is about 0.21% of price per swap-day. A $50 per lot
   per night admin fee would remove most of the historical edge.
4. **Harm boundary** only. No efficacy or futility decision is taken at 40 trades.

Outcomes allowed at trade 40: continue, pause to fix an operational problem, or stop on harm. Not allowed: a
profitability verdict, a parameter change, or live trading.

## Rules against data snooping

- The frozen rules, parameters and ledgers are never changed. A bug found in the paper trader is reported, not fixed in place.
- Forward data is never used to tune anything, including the trend filter, the channel length, the stops or the costs.
- Any new idea suggested by forward results is a new hypothesis. It needs its own pre-registration and data not used
  here. The forward period cannot serve as its test.
- Trades after the final look of a stopped test, or beyond 480, are reported as observations only.
