# Session (time-of-day) study: pre-registration

Committed **2026-11-12, before running.**
- **Data:** Exness XAUUSDm and USOILm ticks, **2025-01 to 2026-10 only**, the same files and SHA-256 values as `../shortlist_2025`.
- **Execution:** the same model as `screen.py window_trades`. The long side buys the ask and sells the bid, at the first tick at or after each time, with 90 minutes' tolerance. Costs are run at **1× and 2× the real spread**.
- **Swap:** none is deducted. This favours the random controls, which can be open over the rollover, so it is conservative for the session rules.

## Why

The gold Asian-session rule passed the shortlist and is now in a forward paper test, but gold rose a lot in 2025–26. **A long-only rule can look good simply because gold went up.** This study checks whether the *time of day* matters, or whether any 9-hour long window would have done as well.

## Tests

**T1, the main test: gold Asia against random windows.**
- **Rule:** long 22:05 → 07:00 UTC, entries Sunday–Thursday. These are the frozen forward rules.
- **Control:** **1,000 random sets** with the same days and the same 9h55m holding time, but a start minute drawn uniformly over the day (seed 20261112).
- **Pass:** the rule's mean bp per trade at 2× cost is **above the 95th percentile** of the random sets.

**T2: gold Asia, year by year.**
- **Pass:** the mean bp per trade at 2× cost is **> 0 in 2025 and also > 0 in 2026 (Jan–Oct)**, each year on its own.

**T3: oil Asia.** The same window and the same random control as T1, on USOILm.
- **Long:** pass if above the random 95th percentile **and** > 0 at 2× cost in both years.
- **Short:** reported for information only.

**T4: hour-of-day map, for information only.**
- **What:** the mean mid-to-mid return of every UTC hour, Sunday 22:00 to Friday 21:00, for gold and for oil, shown separately for 2025 and 2026.
- **No rule is chosen from this map in this study.** Any idea from it needs its own pre-registration and a forward test.

## Consequences, fixed in advance

- **If T1 fails:** the gold Asia forward test keeps running unchanged, since its rules are frozen. But the report will say the backtest edge looks like gold's general rise and not a time-of-day effect.
- **If T3 passes:** an oil Asia forward paper test may be pre-registered separately. Nothing changes in this study.
