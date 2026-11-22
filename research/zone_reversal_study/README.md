# Theory #2 (previous-day range zones + 15-minute signal candle): results

The rules were fixed in `PREREGISTRATION.md` before running. Exness 1-minute bars from 2025-01 to 2026-10, built into 15-minute candles. Markets: gold, oil, DAX, S&P and Nasdaq. Results are at 2× spread, development 2025 against holdout 2026, with a 500-draw random control.

**Verdict: 0 of 60 combinations passed.** Every combination had a **negative** mean R at 2× cost in both periods. The best holdout was gold Z50/S1/TM at −0.11 R per trade (2,326 trades). The pitchfork could not be tested exactly, because it is drawn by hand. It was replaced by 1R, 2R and previous-day-middle targets, as pre-registered.

Files: `study.py`, `results/results.json`. The random control was sped up in commit `dea898b1`: same draws, with candidate candles computed once per day.
