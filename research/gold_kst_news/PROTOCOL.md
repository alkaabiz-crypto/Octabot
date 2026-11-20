# Gold KST + session VWAP: exit optimisation and news rules (pre-registered)

Written before any result of this study was computed. Separate module; nothing in earlier studies, frozen strategies, data or forward-test ledgers is changed.

## Signal (fixed, not optimised)

Exness XAUUSDm, 1-hour candles built from 15-minute bid/ask data. BUY when KST (ROC 10/15/20/30, SMA 10/10/10/15, weights 1-4) crosses above its 9-period SMA at a candle close **and** that close is above the session VWAP. Entry at the ask on the next 15-minute open. BUY legs only, one position at a time. This is the variant `D|KST+F_SESSION_VWAP|BUY|FLIP` from earlier rounds.

## Exit options searched (part 1)

Every leg always closes at the next bearish KST cross (the original exit). On top of that, every combination of:

| Option | Values |
|---|---|
| Hard stop below entry | none, 1.5, 2, 3 × ATR14 |
| Trailing stop from the best hourly close | none, 2, 3, 4 × ATR14 |
| Move stop to entry after +2 × ATR | off, on |
| Time stop | none, 48 h, 120 h |
| "Leave when losing": exit if still below entry after | never, 6 h, 12 h |
| News rule (part 2) | none; block entries 2 h before to 1 h after an event; same plus close any open leg 30 min before the event; block entries in the 24 h before an event |

4 × 4 × 2 × 3 × 3 × 4 = 1,152 combinations.

## News events

High-impact US events whose dates were public in advance:
- **FOMC rate decisions**: the last day of each meeting, statement 14:00 New York time (2020-03-03 10:00 and 2020-03-15 17:00 for the emergency moves). Dates copied from federalreserve.gov.
- **US jobs report (NFP)** and **CPI**: 08:30 New York time on the actual release dates, taken from the vintage dates on ALFRED (St. Louis Fed). This replaces the BLS scheduling rule: bls.gov refuses automated access, and the ALFRED dates showed the rule was wrong in some months.
- Check: the release 15-minute candle in gold has a median range 2.9× (CPI), 3.1× (NFP) and 5.6× (FOMC) the same clock time on nearby days.
- Amendment, made before any grid result was computed: the event source changed from the NFP rule to ALFRED and CPI was added. Live use takes all high-impact USD events from the weekly economic calendar.

## Costs, measurement, benchmark

R = 2 × ATR14 at the signal candle. Primary cost: real Exness spread plus 0.02% slippage. Stress: 0.05% plus 0.02% per day held. The benchmark is random entry candles in the same calendar quarter, with the same number of legs and **the identical exit and news rules** (including the KST-cross exit), 200 runs. z = (strategy mean − random mean) / standard deviation of random means.

## Fit and test

- Fit: 2020-07-01 to 2024-12-31. Test: 2025-01-01 to the latest candle.
- **Pre-registered choice**: the combination with the highest fit-period z among those with at least 150 fit legs and positive fit expectancy at stress cost. Also reported, not chosen: the most profitable fit combination, and the original rule (no extra exits, no news rule).
- The test period has already been seen when the signal itself was picked in earlier rounds, so a good test result is weaker evidence than a fresh one. The chosen rule then starts a forward paper record on new data.
- The rule counts as an improvement only if, in the test period, it has expectancy > 0 at stress cost, z ≥ 1.645 against its own random benchmark, and a smaller worst drawdown than the original rule.

## Part 3: does the news tell the direction?

For each event: the direction of gold's first 15 minutes after the release (open of the release bar to its close). Enter in that direction at the next 15-minute open, exit 4 hours after the release, with a 2 × ATR stop. Compared with entries at the same time of day on random non-event days in the same quarter, the direction again taken from their own first 15 minutes. Fit 2020-07 to 2024-12, test 2025-01 to now, separately for FOMC and NFP. Also reported: whether gold's move after the event is larger than on normal days (useful for risk, not direction).

## Daily briefing

A daily scheduled run lists the coming 48 hours of high-impact USD events from the weekly calendar, gold's historical move size after each event type from this study, whether the news rule blocks a new entry, and the paper-trade state. It will not give direction forecasts unless part 3 confirms that one exists.
