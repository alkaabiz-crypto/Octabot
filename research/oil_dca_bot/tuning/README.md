# Oil DCA bot: settings search with an out-of-sample test

The rules were fixed in `PREREGISTRATION.md` (commit `ae0f0052`) before any result was computed.
- **Tuned on:** 2025-11 to 2026-04.
- **Tested unchanged on:** 2026-05 to 2026-10.
- **Settings:** 336 combinations, all available in the user's bot app.

## Verdict: FAIL, no setting was shown to work

| | Train (Nov–Apr) | Test (May–Oct) |
|---|---|---|
| **Best train setting:** TP 100 pips, 1 extra order, step 63, basket stop 100 USD, trend filter, 15m | **+590 USD** | **−588 USD** |
| Random direction, same setting (200 runs) | | median +95, 95th percentile +1,257 |
| User's current settings + 50 USD stop, with / without trend filter | −1,023 / −1,966 | −1,405 / −960 |

- **Pre-registered checks:** test net > 0: **no**. Drawdown < half of gross profit: yes. Beats random p95: **no**. The setting did **worse than random direction** in the test half.
- **Only 6% of the 336 settings made money in both halves** (14% in train, 25% in test). The best test settings in hindsight all **lost** in train, for example −2,578 in train against +844 in test. Results flip between periods, which is what luck looks like, not an edge.
- **The top 10 train settings in test:** five lost, between −103 and −1,441. The other five were roughly flat, between +7 and +114.

## Patterns across all 336 (median net USD, train / test)

| Setting | Values (median net, train / test) |
|---|---|
| Extra orders | **0: −75 / +25**, 1: −590 / −411, 2: −632 / −434 |
| Take profit | 15 pips: −576 / −322 … **100 pips: −216 / −114** |
| Trend filter | off: −762 / −314; on: −308 / −352 |

- **Adding orders against the move is what loses money.** Without extra orders the bot is roughly break-even before swap, which is what random trading with a stop gives. It is not an edge.
- **Larger targets lose less** than the 15-pip target.
- **No combination turns the bot into a reliable earner.**

## Recommendation

1. **Stop running the bot with real money.** The current settings lost in both halves of the year.
2. **If you keep experimenting, use a demo account,** with no extra orders, a larger take profit and a hard stop. That is the least-bad shape, but it only reaches about break-even.
3. Do not raise lot size or leverage to "win back" losses.

Files: `tune.py`, `results/grid.csv` (all 336 settings, train and test), `results/results.json`.
