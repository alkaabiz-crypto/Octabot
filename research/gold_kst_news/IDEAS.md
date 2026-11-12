# Round 2: entry ideas (pre-registered before the exit grid was read)

Written while the exit grid of PROTOCOL.md was still running, before any of its results were seen. Same data, costs, fit period (2020-07 to 2024-12) and test period (2025-01 to now).

## Part A: entry filters on the KST + session VWAP BUY signal

Each filter is added to the signal **on its own**, never combined. Each is run twice: with the original exit (hold to the bearish KST cross) and with the exit chosen by PROTOCOL.md. The benchmark is random entries with the same exits and filter-free timing.

| Idea | Rule, known at the signal close | Why it might help |
|---|---|---|
| SESSION_ASIA / LONDON / NY / LATE | entry hour 00–07 / 07–12 / 12–20 / 20–24 UTC | the literature finds gold rises in Asian hours and falls in Western hours |
| KST_BELOW_ZERO / KST_ABOVE_ZERO | the KST value at the cross is below / above 0 | buy early in a recovery vs. in an established trend |
| H4_KST_UP | the last closed 4-hour KST is above its signal line | higher-timeframe confirmation |
| DAILY_EMA50 | the last daily close is above its EMA50 | trend filter |
| VOL_HIGH / VOL_LOW | ATR14 above / below its 100-candle median | the edge may live in one volatility regime |
| NEAR_VWAP | close within 1 ATR above the session VWAP | avoid buying extended moves |
| NO_FRIDAY / NO_MONDAY | skip entries on that UTC weekday | weekend gap risk, Monday reversals |
| REAL_YIELD_FALLING | the 10-year real yield (FRED DFII10, the last value published before the signal day) is lower than 5 trading days earlier | gold's main macro driver |
| DOLLAR_FALLING | the broad dollar index (FRED DTWEXBGS, same lag) is lower than 5 trading days earlier | gold is priced in dollars |

## Part B: stand-alone time and event ideas

Long only, entry at the ask, exit at the bid, 2 × ATR stop, compared with random entries of the same length in the same quarter.

| Idea | Rule |
|---|---|
| ASIA_DRIFT | buy at 23:00 UTC, sell at 07:00 UTC, weekdays |
| PRE_FOMC | buy 24 h before the FOMC statement, sell 15 min before it |
| PRE_CPI / PRE_NFP | buy 24 h before the release, sell 15 min before it |

## Decision rule

A total of 15 filters × 2 exits plus 4 stand-alone ideas makes 34 tests. Benjamini–Hochberg at 5% is applied over the test-period p-values of the ideas that passed in fit (fit z ≥ 1.645 with positive fit expectancy at stress cost). An idea counts as confirmed only if it survives that and is profitable in the test period at stress cost. Ideas that are not confirmed are reported but not used.
