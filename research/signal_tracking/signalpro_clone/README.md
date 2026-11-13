# SignalPro-style template clone: one-year Exness gold backtest

Research only. No orders were placed and no account was connected. The rules, the data window and the pass/fail test were fixed in `PREREGISTRATION.md` (commit `3cf5c210`) **before** any result was computed. Nothing was tuned after seeing results.

## Verdict: FAIL, no edge

The primary test was the breakout rule (D2) with the app's management (M1), net of spread. It failed all three pre-registered checks:

| Check | Result |
|---|---|
| Mean R > 0 | **−0.028 R** per signal: no |
| 95% bootstrap CI above 0 | **−0.067 to +0.012**: no |
| Beats random direction (95th percentile −0.007) | no; in fact slightly **worse** than the random median (−0.024) |

**Do not follow template-style signals like these.** This does not prove SignalPro's own picks are worthless, since its direction model is unknown. It does show that the level template alone carries no edge, and that a high win rate shown by this template is not evidence of profit.

## Why the app can look good while losing

The template **makes the win rate high by design:**
- TP1 is only 5 USD away, half the 10 USD stop.
- After TP1 the stop moves to entry.

| D2 + M1, net | Value |
|---|---|
| Signals | 1,704 (about 7 per trading day) |
| **Win rate** | **65%** |
| Median signal | +0.16 R (TP1, then out at breakeven) |
| Profit factor | 0.92 |
| Outcomes | 591 full stops (−1 R), 547 TP1 then breakeven, 409 TP2 then breakeven, 157 TP3 |

About two in three signals "win", but most wins are only +0.17 R or +0.5 R. One in three loses the full 1 R. An app that shows "TP1 Reached" and "SL at breakeven" will look successful almost every day while the account slowly shrinks.

## All results (12 months, Exness XAUUSDm ticks, per signal)

| Rule + management | Signals | Mean R net | 95% CI | Mean R gross (no spread) | Win rate net |
|---|---|---|---|---|---|
| **D2 breakout + M1 (app)**, primary | 1,704 | **−0.028** | −0.067 to +0.012 | −0.009 | 65% |
| D2 breakout + M2 (no breakeven) | 1,704 | −0.029 | −0.077 to +0.020 | −0.002 | 49% |
| D1 every-hour momentum + M1 | 5,627 | −0.027 | −0.050 to −0.005 | −0.006 | 65% |
| D1 every-hour momentum + M2 | 5,627 | −0.042 | −0.068 to −0.015 | −0.016 | 48% |
| Random direction + M1 (2,000 runs) | 5,627 | median −0.024 (5th–95th −0.040 to −0.007) | | | |

- **Before spread the template is about break-even**, which is what random entries with symmetric stops and targets give. The spread (median 0.24 USD at entry) turns that into a steady loss.
- **D1 loses with statistical significance** (t = −2.4 with breakeven, −3.1 without).
- D2 by side: BUY −0.043 R (888 signals), SELL −0.011 R (816). Both CIs include zero.
- **D2 monthly R:** positive in only 3 of 12 months: Dec +5.1, Jan +15.1, Jul +24.0. The other nine are −4 to −15.
- **Overlap:** 450 of the 1,704 D2 signals started while an earlier one was still open. Following every signal would therefore stack risk.

## Faithfulness of the copy

On the app's 9 logged gold signals, the template reproduces entry-relative TP1, TP2 and TP3 **exactly on 7**; SP-001 and SP-007 used wider targets. The stop is 10 USD on 7 of 9 visible stops. What could not be copied is when and in which direction the app signals. D1 and D2 are "follow the move" guesses based on the logged signals, not the app's model.

## Data and checks

- **Data:** Exness XAUUSDm ticks, 2025-11 to 2026-10.
  - 97,556,279 ticks; 0 with ask < bid; 0 out of order.
  - 202,607 exact duplicate ticks, which cannot change a first-touch result.
  - Zip SHA-256 values are in `results/results.json`.
- **Spread:** the archive spread is mostly fixed per month (median 0.16–0.36 USD). As with BTC, real spreads during news may be wider, so these net results are, if anything, optimistic.
- **Simulation:**
  - entry at the first tick after the hourly close (median latency 63 ms);
  - BUY at ask and SELL at bid; exits on the opposite side;
  - targets fill at their level; stops fill at the triggering tick;
  - 7-day timeout.
- **Independent re-check:** `verify_sample.py` recomputed 30 random D2 trades with a separate plain tick loop. **30 of 30 match.**
- **Not included:** swap (unknown; most signals close within hours) and commission (0 assumed, unverified). Both would only make the results worse.

## Reproduce

```
TICK_DIR=<dir with the 12 Exness_XAUUSDm zips> CACHE_DIR=<scratch dir> python3 -I study.py
CACHE_DIR=<same scratch dir> python3 -I verify_sample.py
```

Outputs: `results/results.json` (all statistics and data checks) and `results/D2_trades.csv` (every primary-test signal).
