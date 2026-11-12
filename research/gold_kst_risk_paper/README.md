# Gold KST + session VWAP paper test with risk rules

This is a forward paper record of the same gold BUY signal as [../gold_kst_paper](../gold_kst_paper), with the risk rules the user chose on 2026-11-12:
- a hard stop loss 2 × ATR14 below entry;
- no new entry from 2 hours before to 1 hour after a FOMC, CPI or NFP release;
- any open trade closed 30 minutes before such a release.

Otherwise the trade is held until the bearish KST cross. It counts only trades entered from 2026-11-12 00:00 UTC. The rules are frozen in `src/config.py`, and the engine files are hash-checked. The decision comes at 200 trades, with a futility check at 100.

On history this version gave smaller worst losses than holding through news. Its profit was lower in 2020–24 and similar in 2025–26 (see [../gold_kst_news/README.md](../gold_kst_news/README.md)).

The historical release dates end on the study date. So each run also reads the week's high-impact USD FOMC, CPI and NFP times from the economic calendar and appends them to `ledger/news_events.csv`, which is append-only. The file was seeded with the December 2026 CPI and NFP dates from the St. Louis Fed release calendar. Unscheduled news, such as a sudden post or speech, can't be avoided in advance; the stop loss is the only protection against it.

`python src/paper.py` updates `ledger/`. This is a paper test only.
