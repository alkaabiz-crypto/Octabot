# Operational reconciliation, 12 November 2026 (about 17:45 UTC)

This document records the state of operations at the time of writing. It changes no frozen research, historical result or strategy parameter. Facts were taken from:
- the repository branches;
- the scheduler, through the scheduled-task API;
- hash checks run at the time of writing.

## 1. Paper-test registry

Two separate Claude sessions run paper tests in this repository, on **different branches**:
- **Session A** works on branch `claude/download-skill-27d08k`, with an hourly scheduled task.
- **Session B**, the session that wrote this document, works on branch `claude/dazzling-albattani-j6uys7`, with a daily scheduled task. Its `research/news_surprise/FORWARD_TEST_PLAN.md` covers only session B's tests.

The "seven previously healthy paper tests" are session A's hourly set. Counting the library survivors as one item, they are: Donchian BTC, SignalPro, TREND_ENS, Gold MOM50, Oil Stochastic, Gold Asia, and the library survivors (GOLD_FVG, OIL_FIB and, from 17:25 UTC today, ETH_FIB).

| # | Strategy | Session / branch | Status | Exact configuration (frozen in) | Start (UTC) | Completed trades (latest report) | In FORWARD_TEST_PLAN.md |
|---|---|---|---|---|---|---|---|
| 1 | Donchian 20 BTC long (Binance proxy) | A / download-skill | Active | M2_DONCHIAN20, 1H entry, 4H trend, long, 2×ATR initial stop, 3×ATR trail, 0.5% risk (`btc_breakout/forward/FROZEN.json`) | 2026-11-09 07:00 | 0 / 40 (2026-11-12 17:28) | No: session A's own rules (`EVALUATION_RULES.md`) |
| 2 | SignalPro free-signal tracking | A | Active | Tracking of a third-party app's signals, not our strategy (`signal_tracking/signalpro/`) | 2026-11-09 | 31 signals logged (3 prospective, 28 retrospective) | No |
| 3 | TREND_ENS daily bot, BTC and ETH | A | Active | Coin share = share of SMA20/50/100/200 below the close, spot, 0.1% fee (`daily_signal_dca/forward/`) | first decision at the 2026-11-10 close | 8 ledger rows (no trade-based sample) | No |
| 4 | Gold MOM50 + ATR exits | A | Active | Hyperliquid xyz:GOLD daily, long/flat (`gold_mom50_forward/FORWARD_RULES.md`) | first decision at the 2026-11-11 close | 0 / 20 | No |
| 5 | Oil Stochastic 4H | A | Active | Hyperliquid xyz:CL, Stoch(14,3,3) 4H, TP 100 pips + 4 trailing, SL 100 pips (`oil_stoch_forward/FORWARD_RULES.md`) | 2026-11-11 08:26 | 0 / 100 | No |
| 6 | Gold Asian-session long | A | Active | Hyperliquid xyz:GOLD 1m, long 22:05–07:00 UTC, Sun–Thu (`gold_asia_forward/FORWARD_RULES.md`) | 2026-11-12 00:03 (first entry 22:05) | 0 / 100 | No |
| 7a | Library survivor GOLD_FVG | A | Active | xyz:GOLD, 1h fair-value-gap signals, minute limit fills (`library_forward/FORWARD_RULES.md`) | 2026-11-12 16:44 | 0 / 100 | No |
| 7b | **Library survivor OIL_FIB (oil Fibonacci)** | A | Active | xyz:CL, 1h Fibonacci signals, minute limit fills (same file) | 2026-11-12 16:44 | 0 / 100 (1 pending limit order) | No |
| 7c | Library survivor ETH_FIB | A | Active (added 17:25 UTC today) | Binance ETHUSDT spot (same file) | 2026-11-12 17:25 | 0 / 100 | No |
| 8 | **BTC Pivot Reversal BUY** | B / dazzling-albattani | Active | TradingView Pivot Reversal (4/2), 1H, BUY legs, own exits (`pivot_reversal_paper/src/config.py`) | 2026-11-12 00:00 | 0 / 400 | **Yes** (section D) |
| 9 | ETH Pivot Reversal BUY | B | Active | As #8, on ETHUSDm, calibrated benchmark (`eth_pivot_paper/src/config.py`) | 2026-11-12 00:00 | 0 / 400 | **Yes** (D) |
| 10 | **Gold KST + session VWAP, 48 h time stop** | B | Active | KST(10,15,20,30 / 10,10,10,15; signal 9) up-cross with close above session VWAP; exit at the bearish cross or after 48 h (`gold_kst_paper/src/config.py`, primary track) | 2026-11-12 00:00 | 0 / 200 | **Yes** (D) |
| 10s | Gold KST shadow tracks: original exit, DOLLAR_FALLING, VOL_LOW | B | Active, comparison only | Same config file | 2026-11-12 00:00 | 0 | Recorded, no decision |
| 11 | **Gold KST + VWAP, 2×ATR stop and close before news** | B | Active | As #10, plus a 2×ATR stop and the FOMC/CPI/NFP block and close (`gold_kst_risk_paper/src/config.py`) | 2026-11-12 00:00 | 0 / 200 | **Yes** (D) |
| 12 | NFP release capture | B | Scheduled | `news_surprise/live/capture.py` + `evaluate.py` | first run 2026-12-04 | 0 | **Yes** (A) |
| 13 | CPI release capture | B | Scheduled | same | first run 2026-12-10 | 0 | **Yes** (B), separate from #12 |
| 14 | Gold ADP-contrarian (exploratory) | B | Scheduled | `news_surprise/live/adp_contrarian_forward.py` | first eligible 2026-12-04 | 0 / 36 | **Yes** (C) |

**Retired:** nothing. One scheduled task was replaced (section 2). **Paused:** nothing.

**Why "Oil Fibonacci disappeared" and "BTC appeared".**
- Oil Fibonacci (#7b) has not disappeared. It is a session-A test, still active on session A's branch and in session A's hourly task. The forward plan never listed it, because that plan covers only session B's tests.
- The BTC test in the plan is #8, **BTC Pivot Reversal**. It is a different strategy from session A's Donchian BTC test (#1).
- The plan's **two gold strategies** are #10 (KST + VWAP with a 48 h time stop) and #11 (KST + VWAP with a 2×ATR stop and closing before news).
- Session A's gold tests (#4 MOM50, #6 Asia session, #7a FVG) are separate and not covered by the plan.

## 2. Daily scheduler (session B)

| Item | Fact |
|---|---|
| Scheduler type | Claude Code cloud **scheduled task** (`trig_01UqSPZw4PFwwXdS4wkQbtEW`), persistent-session mode: it fires into session B's conversation. It is not a cron job inside a container. |
| Frequency and timezone | Cron `23 3 * * *`, **UTC**: daily at 03:23 UTC. |
| Created / next run | Created 2026-11-12 11:40 UTC. **Next run: 2026-11-13 03:23 UTC.** |
| Last three successful executions | **None yet.** This task has never run. Its predecessor (`trig_0189ubBsyWt4iFTJqUVDS4Ht`, deleted 2026-11-12) ran once at 2026-11-12 03:23 UTC. The scheduler logged that as "succeeded", but the push was refused (no repository access in a fresh session), and the gold test failed because data files were missing from git. Both causes were fixed, which is why the task was replaced. **No end-to-end successful daily run has happened yet.** |
| Hash verification (run by hand at this reconciliation) | `FREEZE_NOTE.md`: 25 files, 0 problems. `FORWARD_TEST_PLAN.md`: 13 files, 0 problems. Paper-test engine hashes (`FROZEN_SHA256` in each config): BTC 7, ETH 8, gold 6, gold-risk 6 files, 0 problems. From the next run on, the task repeats this check before running anything. |
| Failure notification | **None outside this conversation.** Persistent-session tasks do not send phone or email notifications. Run results and errors appear as a turn in this conversation, and the scheduler records the delivery status (`last_run`). Nothing alerts the user if a run is silently missed. The user has to look at this conversation, or at the branch's commit log for the daily "Paper tests and briefing: daily update" commit. |
| One-off tasks | `trig_01BZEiJKeXqKRfFHEXWgpqod` (NFP capture, 2026-12-04 13:12 UTC) and `trig_01B3Re5UuB9LNhpTz936Kjzm` (CPI capture, 2026-12-10 13:12 UTC). Neither has run yet. |
| Session A's hourly task, for reference | `trig_019s7cpaoJzJGHtojowwjnT4`, cron `6 * * * *` UTC. Its latest successful runs are evidenced by commits on its branch at 2026-11-12 15:12, 16:11 and 17:28 UTC. |

## 3. Data preservation

The external data behind the frozen ADP investigation is **not archived in durable storage**. It sits only in session B's temporary scratch storage, which is deleted when the container is recycled:
- the Kaggle US calendar, the Kaggle global calendar and the Hugging Face calendar (51 MB);
- Exness 15-minute candles for gold, EUR/USD, GBP/USD and USD/JPY (11 MB);
- 384 Exness tick-window caches (119 MB).

It was not added to the repository because:
- the calendar copies come from Investing.com, whose terms restrict redistribution;
- the Kaggle and Hugging Face licences are not stated;
- adding about 180 MB of data would also change the repository the user asked to leave stable.

**Consequence: exact future reproduction is not guaranteed.**
- The frozen hashes (`news_surprise/reports/adp_data_manifest.csv`) prove what the data *was*, but cannot bring it back.
- Rebuilding from the original sources reproduces the results **only if** those sources still serve identical files:
  - the same Kaggle dataset versions;
  - the same Hugging Face revision;
  - the Exness tick archive unchanged.
- Any change would show up as a hash mismatch against the manifest.
- The repository does contain the ADP-relevant extracts the code reads directly (`data/consensus_investing.csv`, `data/consensus_investing_2015_2024.csv`) and all result files.

The user can archive the scratch files to storage they control if exact reproduction is wanted. It was not done here.

## 4. ADP sample: the two shutdown-delayed reports

| BLS jobs report | BLS publication (official) | Reference month matched | ADP report used | ADP publication (official) | Last ADP vintage before the BLS release (ALFRED `ADPMNUSNERSA`) | ADP surprise used |
|---|---|---|---|---|---|---|
| September 2025 (delayed) | 2025-11-20 08:30 New York = **13:30 UTC** | 2025-09 | ADP September 2025 | 2025-10-01 08:15 New York = **12:15 UTC** | Vintage dated 2025-10-01 shows Sep = 134,526,000 against Aug 134,558,000, so −32K. Unchanged through the 2025-11-19 vintage, except that Sep was revised to 134,529,000 in the Oct report, which does not affect the Sep headline. | −32K against forecast +52K |
| November 2025 (delayed; October payrolls released the same day without a forecast) | 2025-12-16 08:30 New York = **13:30 UTC** | 2025-11 | ADP November 2025 | 2025-12-03 08:15 New York = **13:15 UTC** | Vintage dated 2025-12-03 shows Nov = 134,544,000 against Oct 134,576,000, so −32K. Unchanged through the 2025-12-15 vintage. | −32K against forecast +5K |

**No look-ahead.** Each ADP report was public 50 and 13 days before its BLS release, and its value equals the ALFRED vintage published before the BLS release.

For 2025-12-16, the calendar also lists "Nonfarm Payrolls (Oct)" (−105K) with no forecast. It has no surprise, so it is not used. The matched observation is November (actual 64K against forecast 51K). The calendar file's own times are New York time + 4 h, not UTC; the official times above are used instead.

**The samples stay separate.**
- Addendum 5: N = 120, 0–7-day window, results in `news_surprise/reports/adp_preposition.json`.
- Audit: N = 122, reference-month pairing, in `adp_robustness.json`.
- The two differ exactly by these two releases.

## 5. News captures

- **4 December (NFP) and 10 December (CPI) are separate experiments**, each with its own N = 12 programme. They are never pooled (`FORWARD_TEST_PLAN.md`, sections A and B).
- **Each capture answers a technical question first:** whether the BLS figure was received, and how many seconds after 08:30:00.
- **The paper trade is a second, separate measurement:** the executable Exness prices at that latency. A successful capture is not evidence of a profitable strategy.
- **Twelve releases** per programme can show at most whether a large effect is plausible. A PASS under that plan would justify further prospective testing, not a claim of profitability.

## Change freeze

After this reconciliation, session B makes no further changes to the research system. That covers code, configs, frozen files, plans and scheduled tasks. The only exceptions are the scheduled runs themselves, which append to ledgers, and fixes the user explicitly authorises. New evidence comes only from the prospective tests.
