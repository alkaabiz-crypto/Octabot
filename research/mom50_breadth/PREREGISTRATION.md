# MOM50 breadth test: gold's MOM50 + ATR rule on 15 other Exness markets, pre-registration

Committed **2026-11-12, before any tick data for these markets was downloaded or looked at.**

## Why

Gold MOM50 + ATR (the gold MOM50 forward test) beat 93.6% of exposure-matched random timings on gold in 2025–26, which is not significant on its own (`../exposure_control`). Running the **identical rule on markets never used to build it** tests whether the timing generalises.

## Data

- **Source:** Exness public tick archive (`ticks.ex2archive.com`), **2025-01 to 2026-10 only**.
- **Markets:** XAGUSDm, XPTUSDm, XPDUSDm, UKOILm, XNGUSDm, US30m, US500m, USTECm, DE30m, UK100m, JP225m, HK50m, FR40m, AUS200m, STOXX50m. This list is fixed now. Gold is excluded because it is in-sample.
- **Daily candles:** built exactly as `../shortlist_2025/screen.py daily`:
  - mid price;
  - the trading day is the UTC date of t + 2h;
  - the spread is taken at the first tick of the day;
  - days with fewer than 100 ticks are dropped.
- **Missing data:** a market with fewer than 300 daily candles is dropped and reported. None is replaced.
- **Storage:** each monthly zip is processed and then deleted. Only the daily candles and each zip's SHA-256 are kept.

## Rule and engine, unchanged

- **Rule:** the `G_MOM50_ATR` loop from `screen.py gold`.
  - **Entry:** the close is above the close 50 days ago **and** the SMA20 is above its value 5 days earlier.
  - **Exit:** close < entry − 2×ATR14, **or** close < peak − 1.5×ATR14, **or** 30 days held.
- **Execution:** `run_daily` at **2× the real spread**, decided at the close and filled at the next open. Results are measured from day index 55, the same as for gold.

## Primary test

- **Statistic:** the mean across markets of the Sharpe ratio of daily equity returns from day 55, × √252.
- **Control:** 1,000 joint draws. In each draw, every market's active-period position series gets its own circular shift, uniform in [20, n − 20], with seed 20261112. The mean is then recalculated across markets.
- **Pass:** above the **95th percentile** of the draws.

**Information only:** each market's percentile against its own shifts, net return, buy and hold, max drop and number of trades.

## Consequences, fixed in advance

- **The gold MOM50 forward test continues unchanged** either way.
- **PASS:** the MOM50 idea gains real out-of-sample support.
- **FAIL:** its gold backtest edge is treated as unconfirmed, and the report says so.
