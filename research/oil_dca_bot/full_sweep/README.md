# Oil bot full sweep: results

The rules were fixed in `PREREGISTRATION.md` (commit `e81b47c5`) before running.
- **Grid:** 12 entry conditions × 5 timeframes (15m, 30m, 1H, 4H, 1D) × 6 app-allowed exits (TP 100/200/300, SL 300/500) = **360 combinations.**
- **Data and costs:** Exness USOILm, real spread and 2×, swap 0.

## Verdict: FAIL, choosing the "best" settings from the past did not work on new data

**Top 5 picked on 2025 only, then checked on Jan–Oct 2026:**

| Combination | 2025 (1× / 2×) | 2026 (1× / 2×) | 2026 trades | Random 90th pct | Verdict |
|---|---|---|---|---|---|
| 15m Bollinger, TP200/SL500 | +248 / +398 | +361 / +40 | 174 | +708 | FAIL |
| 1H MFI, TP200/SL500 | +305 / +290 | −21 / −11 | 71 | +649 | FAIL |
| 30m MFI, TP200/SL300 | +245 / +276 | −76 / −99 | 127 | +721 | FAIL |
| 15m Ultimate Osc, TP300/SL300 | +332 / +273 | +113 / +14 | 100 | +483 | FAIL |
| 4H Stochastic, TP200/SL500 | +269 / +266 | −282 / −352 | 63 | +735 | FAIL |

- **The best five of 2025:** three lost in 2026. The other two were roughly flat at double costs.
- **Across all 360:** only **43.6%** were positive in 2026 at 2×. Only **47 (13%)** were positive in both years at both cost levels, which is about what luck alone produces.

## Patterns across all 360 (median 2026 net at 2×, USD)

| Group | Results |
|---|---|
| **Timeframe** | 15m −122, 30m −103, 1H −63, **4H ≈ 0, 1D +11**. Shorter timeframes lose more, because spread costs pile up. |
| **Condition** | EMA200 +117, ADX +125, SMA200 +79 (trend indicators did well in 2026 but mostly lost in 2025). Oscillators were mostly negative: Stochastic −168, Bollinger −129. |

**The winning condition changes from year to year:** oscillators led in 2025, trend indicators in 2026. Settings that look best in hindsight don't carry forward.

## Practical guidance

- **Use 4H or 1D,** never 15m or 30m.
- **No setting is proven.** The **MFI 4H + TP 100 / SL 300** setting already given to the user is among the 47 positive in both years (2025 +113, 2026 +265). It agrees with the earlier, separate study, but this sweep does not confirm it beyond luck. **Demo only.**
