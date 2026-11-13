# Session (time-of-day) study: results

The rules were fixed in `PREREGISTRATION.md` (commit `1d93830c`) before running. Data: Exness XAUUSDm and USOILm ticks, Jan 2025 to Oct 2026. Costs use the real spread, at 1× and 2×.

## Verdict

| Test | Result | Verdict |
|---|---|---|
| **T1:** gold Asia (long 22:05 → 07:00) against 1,000 random 9h55m long windows on the same days | Rule **+4.32 bp** per trade at 2× cost. Random: median +3.62, 95th percentile +9.24. The rule sits at the **57th percentile**. | **FAIL** |
| **T2:** gold Asia, each year at 2× cost | 2025 **+6.84 bp** (257 trades); 2026 **+1.31 bp** (215 trades, t = 0.17) | PASS, but 2026 is about zero |
| **T3:** oil Asia long | **−8.08 bp** at 2× cost, 30th percentile of random | **FAIL** |
| Oil Asia short (information only) | −4.00 bp at 2× cost, 62nd percentile | — |

## What this means

- **The gold Asian-session backtest was not a time-of-day edge.** Any random 9-hour long window in 2025–26 made about the same, because **gold rose strongly**.
  - The rule did no better than chance timing.
  - In 2026 its edge is close to zero.
- **This corrects my earlier report.** I called gold Asia "the strongest result not yet tested live". That was wrong: it passed the cost and break-reopening checks but not a random-timing control, which I had not run until now.
- **The forward paper test keeps running unchanged**, because its rules are frozen, but expect it to track gold's direction.
  - If gold falls, it will lose.
  - It is **not** recommended for a demo or for real money.
- **Oil has no Asian-session effect** in either direction.
- **Hour-of-day map** (`results/results.json`, `hour_map`): no gold or oil hour is consistently positive or negative in both 2025 and 2026.
  - The few hours with |t| ≥ 2 do not repeat across years, which is what noise looks like.
  - No rule is taken from the map.

## The lesson for every long-only test

A long-only rule must beat **random timing with the same exposure**, not just cash or zero. This control is now pre-registered for the gold MOM50 and trend-bot backtests in `../exposure_control/`.

Files: `study.py`, `results/results.json`.
