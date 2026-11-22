# Oil DCA bot: wide optimisation (8,400 settings) with monthly walk-forward validation

The rules were fixed in `PREREGISTRATION.md` (commit `90b93a85`) before any result was computed. Data: Exness USOILm ticks, 2025-11 to 2026-10. Runtime: 579 s.

## Verdict: FAIL, no settings survived out-of-sample

**Walk-forward:** each month, the setting with the best return/drawdown over the *previous 3 months* was picked, then traded the next month.

| Month | Out-of-sample USD | Setting picked (TP / trailing / extra orders / step / stop / direction / timeframe) |
|---|---|---|
| 2026-02 | 0.00 | 30 / 4 / 0 / – / 100 / fade / 1h |
| 2026-03 | **−336.84** | 150 / 4 / 1 / 100 / 50 / fade / 1h |
| 2026-04 | −89.67 | 150 / 4 / 2 / 250 / 200 / rating / 15m |
| 2026-05 | +186.59 | 150 / 4 / 2 / 150 / 200 / rating / 15m |
| 2026-06 | +35.36 | 150 / 4 / 2 / 250 / 200 / rating / 15m |
| 2026-07 | +69.40 | 150 / 4 / 0 / – / 200 / fade / 1h |
| 2026-08 | +35.44 | 150 / 4 / 2 / 63 / 50 / rating / 1h |
| 2026-09 | **−408.92** | 150 / 4 / 1 / 63 / 25 / rating / 1h |
| 2026-10 | **−262.43** | 60 / 4 / 2 / 63 / 100 / rating / 1h |
| **Total** | **−771.07** | 4 of 9 months positive; out-of-sample max drawdown 904 USD |

All three pre-registered checks failed:
- out-of-sample net > 0: **no**;
- at least 6 of 9 months positive: **no** (4);
- drawdown below 2 × net: **no**.

## Why the "best settings" can't be trusted

- **The best full-year setting in hindsight made +2,635 USD:** TP 150, trailing 4, 2 extra orders, step 100, stop 200, rating, 1h. But it was picked *after* seeing the whole year, and the walk-forward shows that settings picked this way do not hold up the following month.
- **Only 17.8% of the 8,400 settings were profitable over the full year.** Only **1.5% (about 128) were profitable in all 4 quarters.** Among 8,400 tries, that many can come from luck alone.
- **The user's current settings (with a −50 USD stop) lost in every direction mode:** from −1,730 (fade) to −3,366 (always BUY) for the year.

## Consistent patterns (median net USD across all settings)

| Setting | Least bad | Worst |
|---|---|---|
| Take profit | 100–150 pips (−495 / −458) | 15–30 pips (about −1,095) |
| Trailing | 4 pips (−547) | plain TP (−1,068) |
| Extra orders | **0 (−122)** | 1–3 (−743 to −889) |
| Basket stop | 200 USD (−315) | 50 USD (−1,087) |
| Timeframe | 1h (−540) | 15m (−1,132) |
| Direction | always BUY (−298) | always SELL (−2,171) |

- **Each of these makes the bot lose less, but none makes it reliably profitable.**
- The always-BUY vs always-SELL gap mostly reflects oil's path over this year. It is not a rule that will repeat.

## Recommendation

1. **No setting can be recommended for real money.**
2. If the user wants to keep experimenting, pre-register **one** candidate from the least-bad shape and run it **forward on a demo account only**, judging it after a fixed number of baskets. The candidate: 1h, TP 100–150 pips with 4-pip trailing, 0–1 extra orders with a wide step, and a stop of about 200 USD sized to the account.
3. Stop the current live settings. They lost in every variant tested.

Files: `optimize.py`, `results/all_settings.csv` (every setting with full-year and quarterly P&L), `results/results.json` (walk-forward detail).
