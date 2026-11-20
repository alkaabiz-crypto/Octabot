# SignalPro SP-032 to SP-035 scored on Exness prices (the user's broker), 2026-11-14

**Data.**
- Exness public tick archive, November 2026 files (XAUUSDm SHA-256 `4bbf5600…`, USOILm `6cca8ab6…`), to 2026-11-13 21:57 UTC.
- 1-minute mid bars built with the frozen `orb_study/build_bars.py` `bars()` function.
- Raw ticks are not committed.

**Scoring.** The frozen SignalPro tracker's own `score()` / `resolve()` / `r_full()` / `r_thirds()` functions (tracker SHA-256 `75a7aed5…`, unchanged), fed with the Exness bars instead of Hyperliquid.
- A = the app's distances from the Exness price at posting time; B = the app's absolute levels.
- Both ends of the posting window are scored. Stop first within a candle. "R thirds BE" = the app's displayed management (stop to entry after TP1).
- Per-variant output: `exness_scoring.json`.

| Signal | App claim (screenshot 21:37 UTC) | Exness result | Match? |
|---|---|---|---|
| SP-032 gold BUY 3894, TPs 3899/3904/3920 | TP1 reached, stop moved to breakeven | **Not scoreable:** the app shows only the moved stop (= entry), so the original risk is unknown | — |
| SP-033 gold BUY 3890, stop 3885, TPs 3895/3900/3920 | **Contradictory:** "Stop Loss Hit" in one screenshot, "TP1 Reached" in another, same minute | **STOP before any TP in all 4 variants (−1R).** At the app's level, entry triggered and the stop was hit at 13:46 UTC (early window) / 15:08 (late window). | Only the "Stop Loss Hit" screen matches; **"TP1 Reached" does not** |
| SP-034 gold BUY 3880, stop 3875, TPs 3885/3890/3910 | TP1 reached, stop moved to breakeven | **STOP before any TP in all 4 variants (−1R)**, e.g. at 13:51 / 15:32 UTC with the app's levels | **No** |
| SP-035 oil SELL 88.60, stop 89.10, TPs 88.1/87.6/85 | TP2 reached, stop at breakeven | The app's entry **88.60 never traded on Exness** in the posting window (mid high 88.59, spread about 0.014). With the app's distances from the actual price, TP1 and TP2 were hit and the trade is still open. | Only if the trade was entered **below** the app's stated entry |

**Price check at posting time.** Exness gold traded 3872.6–3906.1 (mid) during the posting windows, so the gold entry levels did trade. Exness gold was $6–18 above the app's entry when each window opened.

## Plain answer

- **On your broker's own prices, the app's two scoreable gold "wins" were losses.** Both hit their stop before reaching TP1.
- The oil signal's stated entry never traded on Exness.
- These four were all **retrospective** (outcome visible when captured), so this says nothing about the app's overall profitability. It does say that **the app's displayed outcomes do not match Exness prices** for these signals: **claims INACCURATE** for SP-033 and SP-034.

Paper evaluation only.
