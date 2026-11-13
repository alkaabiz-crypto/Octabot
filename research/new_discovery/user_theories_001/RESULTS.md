# User theories 001: results

Both tests followed `PREREG.md` (SHA-256 `95164f98…`, hashed 2026-11-12 23:24:09 UTC, before any result). They reuse 2025–2026 data that earlier studies had already inspected, so even a PASS would only have been screening evidence.

## Test A: Theory #2b, zones from the same day's opening range

**Verdict: 0 of 60 combinations passed.**
- **All 60** had a negative mean R at 2× costs **in both** 2025 and 2026.
- At 1× costs, 58 of 60 were negative in both periods. The other two (US500m Z50/S2/TM and Z25/S2/TM) were positive in **one** period only.
- In total, 158,971 trades were simulated across the two periods.

| Market | Best holdout at 2× (mean R per trade) | Version | Holdout trades |
|---|---|---|---|
| Gold | −0.115 | Z25 / S2 / T2 | 589 |
| Oil | −0.153 | Z25 / S1 / T2 | 1,457 |
| DAX | −0.132 | Z50 / S1 / T2 | 1,744 |
| S&P 500 | −0.309 | Z25 / S1 / T1 | 1,785 |
| Nasdaq | −0.167 | Z25 / S1 / TM | 1,248 |

**Compared with the frozen Theory #2** (previous day's range): that was 0 of 60 as well, with a best holdout of gold Z50/S1/TM at −0.11R. Using the same day's opening range instead of yesterday's range does not change the conclusion.

**Implementation.**
- `theory2b.py` is the frozen `zone_reversal_study/study.py` with only the range and the signal window changed (the diff is in the commit).
- The range uses bars before 07:00 UTC only, and every signal candle opens at 07:00 or later, so there is no look-ahead.
- It was run through a resumable driver that calls the study's own `job()` per combination (seeds are per combination, so the results are identical to `main()`).
- Output: `results/theory2b.json`.

**Base-code check (in progress).** The unmodified frozen `study.py` was re-run on the same rebuilt bars. So far **40 of 60 combinations are identical** to the frozen `results/results.json`, in every field (trades, mean R, win rate, random 95th percentile, verdict). The remaining 20 are still running.

## Test B: wick rejection ("John Wick's theory"), frozen C2 on new timeframes

**Verdict: 0 of 19 new combinations passed; 0 significant after Benjamini–Hochberg correction.**
- On **15-minute** candles it lost in all 5 markets and both years, by a significant margin in most. Examples, iid t at 2×: DAX −10.9 / −6.9; S&P −4.9 / −6.5; oil −8.2 / −1.5.
- 4h and 1d have few trades. They are positive in at most one period, never both.
- The 1h reference re-run reproduces the frozen screen exactly (7 of 7, all FAIL).
- Output: `results/wick_test.json`.

## Conclusion

Neither theory has an edge in the tested form, before or after costs. Both were run at the library's resolution (Exness 1-minute bars). The pitchfork part of the original Theory #2 remains untested, because it needs hand-drawn pivots.
