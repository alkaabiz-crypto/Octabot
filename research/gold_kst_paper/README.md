# Gold KST + session VWAP paper test and daily briefing

This is a forward paper record of the gold BUY signal studied in [../gold_kst_news](../gold_kst_news). It uses only data after 2026-11-12 00:00 UTC, which no earlier test has seen. The rules are frozen in `src/config.py`, and the engine files are hash-checked on every run.

- **Primary track.** BUY when KST crosses above its signal line on the 1-hour chart while price is above the session VWAP. Exit at the bearish KST cross or after 48 hours, whichever comes first. This is the exit that the pre-registered grid chose.
- **Shadow tracks, kept for comparison only.** The original rule with no time stop. Also the two nearest misses of round 2: entering only while the broad dollar index is falling, and entering only in below-median volatility. They are recorded so that fresh data can show whether they hold up. No decision depends on them.
- **Decision.** The verdict comes at 200 primary legs, about 1.7 years. It passes only with positive expectancy at both normal and stress cost and p ≤ 0.05 against random entries that use the same exits. There is a futility check at 100 legs.

`python src/paper.py` rebuilds candles from the Exness tick archive and updates `ledger/`. The archive lags by about a day, so this is a record, not a live alert. `python src/briefing.py` writes `ledger/BRIEFING.md`. It covers high-impact events in the next 48 hours, gold's measured move size after each US event type, and the paper state.

The briefing does not forecast direction. The study found no reliable way to tell from FOMC, CPI or NFP news whether gold will rise or fall. What the news does tell you is that the move will usually be larger than normal.
