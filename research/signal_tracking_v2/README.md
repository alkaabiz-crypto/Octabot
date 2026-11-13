# SignalPro tracking, restarted in this branch (2026-11-13)

**Why here.** The original tracker lives on the other session's branch (`research/signal_tracking/signalpro/`). It was stopped there on 2026-11-12 ("can be restarted for new screenshots unchanged"), and that branch is not modified from this session.
- The frozen `tracker.py` (SHA-256 `75a7aed5…`, identical to the freeze manifest) was run **unchanged** on a scratch copy of that folder, with four new signals appended.
- `signals.csv`, `outcomes.csv` and `REPORT.md` here are its outputs. They include all 35 signals; SP-001 to SP-031 are unchanged.

## New signals (screenshots 01:37 UAE 2026-11-14 = 21:37 UTC 2026-11-13; all RETROSPECTIVE)

| ID | Signal | App status | Hyperliquid result (frozen method) |
|---|---|---|---|
| SP-032 | XAUUSD BUY 3894, TPs 3899/3904/3920 | TP1 reached, stop moved to breakeven | Not scoreable: the original stop is not shown |
| SP-033 | XAUUSD BUY 3890, stop 3885, TPs 3895/3900/3920 | **Contradictory:** "Stop Loss Hit" and "TP1 Reached" in two screenshots of the same minute (logged once) | Stop in all 4 variants (−1R), but the feed gap ($7–10) is larger than the stop ($5) |
| SP-034 | XAUUSD BUY 3880, stop 3875, TPs 3885/3890/3910 | TP1 reached | Stop in all 4 variants (−1R); feed gap $17–20, flagged GAP>STOP |
| SP-035 | USOIL SELL 88.60, stop 89.10, TPs 88.1/87.6/85 | TP2 reached | The app's entry never traded on Hyperliquid (about 0.5–0.8 lower). With the app's distances, TP1 and TP2 were hit; still open. |

**Reading.** Hyperliquid's gold perpetual was $7–20 away from the app's prices at posting time, which is more than the $5 stops. So the Hyperliquid scoring cannot settle these gold signals. The app evidently quotes another feed, most likely Exness's.

**Next.** The signals will be re-scored on Exness 1-minute bars (the user's broker feed) once the Exness tick archive includes 2026-11-13, using the frozen tracker's resolution rules. That scoring is scheduled for 2026-11-14.

**To get evidence that counts:** screenshot signals as soon as they are posted (0/3 hit, "Trade Active"). Those are PROSPECTIVE. Signals captured after the outcome is visible (RETROSPECTIVE) cannot show whether the app is profitable, because of selection bias.
