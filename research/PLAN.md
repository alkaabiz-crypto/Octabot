# Research plan (SMART), 13 November 2026

## Overall goal

Find, **by 2027-11-30**, at least one trading approach that keeps a **positive edge after realistic costs on new data** (data it was not chosen on), judged by a pre-registered rule. Or show, with documented evidence, that none of the candidates has one.
- **Paper trading only.** Real money is a separate decision that is never made inside this plan.

## The four categories

The categories are different concepts, so each is defined, tested and judged differently. Every item is a **candidate** with a permanent number. The register is in [`CANDIDATES.md`](CANDIDATES.md).

| | **Indicators (IND)** | **Strategies (STR)** | **Theories (THE)** | **Signals (SIG)** |
|---|---|---|---|---|
| **What it is** | A **measurement** computed from data, e.g. RSI, KST, VWAP distance, Coinbase premium z, futures-curve slope. It makes no decision on its own. | A **complete trading rule**: entry, exit, stop, size, costs. It can be traded exactly as written. | A **claim about how markets behave**, e.g. "CME gaps get filled", "round numbers act as support", "gold falls at the London fix". | **Calls made by someone else**, e.g. the SignalPro app: an entry, stop and targets that we did not design. |
| **Question asked** | Does it carry **information** about future price moves? | Does it **make money** after costs, on data it was not built on? | Is the claim **true**, and is it still true? | Are the provider's calls **profitable**, and are its reported results **accurate**? |
| **How it is tested** | **Information test:** rank correlation (IC) between the indicator and the next 1h / 4h / 1d / 5d returns, per market and period, against a baseline of the market's own recent returns. Dependence-aware t-statistics, Benjamini–Hochberg. No costs, because it is not a trade. | **Trading test:** causal backtest on the shared engine (`new_discovery/src/causal_orders.py`; the prefix-invariance gate must pass); bid/ask plus 2× costs; TRAIN / VALIDATION / TEST plus an untouched period; random-entry benchmark; BH. **Then a forward paper test** judged by rule V2, then the venue's real fees. | **Event study:** measure exactly what the claim predicts (e.g. how often the gap fills) against what happens at random times with the same conditions. Effect size first; then replication in other markets and older periods. | **Prospective audit:** only signals captured **before** any outcome count. Each is scored on the **broker's own prices** (Exness) with fixed rules, compared with random entries using the same stops and targets, and checked against the app's own claims. |
| **Verdicts** | INFORMATIVE / WEAK / NONE | VALIDATED (forward pass) / WATCH / REJECTED | SUPPORTED / DECAYED (true before, not now) / NOT SUPPORTED | PROFITABLE / UNPROFITABLE / NOT YET DECIDABLE, plus a CLAIMS ACCURATE / INACCURATE flag |
| **Minimum evidence** | ≥ 3 markets or ≥ 2 periods with the same IC sign, holdout p ≤ 0.05 after BH | Forward paper test reaches a V2 PASS (100+ trades) | ≥ 100 events; replicated in at least one other market or period | ≥ 50 prospective signals |
| **What a positive result leads to** | It may be used inside a **new STR candidate** (pre-registered) | A separately reviewed decision; never automatic live trading | It may become a **new STR candidate** (pre-registered) | Nothing automatic; a report to you |

**Common rules for every category.**
- Pre-register before testing.
- Never tune after seeing results.
- Report failures as well as successes.
- Keep raw data private; never claim more than the evidence shows.

## SMART goals and deadlines

| # | Goal (Specific, Measurable) | Achievable because | Deadline |
|---|---|---|---|
| G1 | **Register every existing item** as a numbered candidate in its category, with its current verdict | All past results are already in the repository | **2026-11-14** |
| G2 | **Indicators:** run the information test on every indicator candidate (IND-001 to IND-021) across gold, oil, S&P 500, EUR/USD and BTC | Data archived; one pre-registered batch | **2026-11-30** |
| G3 | **Theories:** give every theory candidate a verdict (SUPPORTED / DECAYED / NOT SUPPORTED) using the event-study method, including the 10 already tested | Most need only re-reading results in event-study terms; the rest need one batch | **2026-12-15** |
| G4 | **Signals:** collect **50 prospective** SignalPro signals (screenshots taken at "Trade Active, 0/3"), score them on Exness prices | About 3–6 free signals a day; scoring is automatic once the Exness archive updates | **2027-01-31** |
| G5 | **Strategies:** every running forward paper test reaches its first decision look, or a futility stop, under its pre-registered rule | All are already running daily | **2027-11-30** (Coinbase premium ≈ 100 trades) |
| G6 | **New strategies from the evidence:** any IND rated INFORMATIVE or THE rated SUPPORTED becomes at most **3** new pre-registered STR candidates, each with a forward paper test | Only built on evidence, never on a search | **2027-02-28** |
| G7 | **Monthly honesty check:** count every test run (the whole family) and update the multiple-testing record | A weekly status refresh already runs | Monthly, first on **2026-12-01** |

## How progress is reported

- **`research/STATUS_LATEST.md`:** every Monday (scheduled task).
- **`research/CANDIDATES.md`:** updated whenever a candidate's verdict changes.
- **`research/ROADMAP.md`:** every step towards each goal, with owner and date.
- **Daily reports:** paper tests 03:23 UTC; Coinbase premium 04:47 UTC.
- **Each category's protocol** is in `research/categories/`.

## What you can do to help

1. **Signals (most valuable):** screenshot a SignalPro signal **the moment it appears** ("Trade Active, 0/3"), with the clock visible. Without those, the signal category cannot reach a verdict.
2. **New ideas:** send any indicator, strategy, theory or signal source. I will give it a number in the right category and test it with that category's method.

## Progress and work queue (updated 2026-11-13)

**Done.**
- **G1:** the register is complete (`CANDIDATES.md`).
- **G2, first batch:** IND batch 001 tested 17 indicators.
  - **16 NONE.**
  - IND-001 Coinbase premium **WEAK**.
  - IND-018 HAR volatility forecast **INFORMATIVE**.
  - An exploratory contrarian pattern at 1 h was registered as THE-017.

**Next, in order.** Each is pre-registered before it runs.

| # | Category | Candidate | Action |
|---|---|---|---|
| 1 | SIG | SIG-001/002 | Score SP-032 to SP-035 on Exness prices (scheduled 2026-11-14 02:41 UTC); keep collecting **prospective** screenshots |
| 2 | STR | STR-023 VWAP momentum BUY (BTC, replicated on ETH) | It has never been forward-tested: pre-register a forward paper test on Binance prices with realistic fees, judged by rule V2 |
| 3 | THE | THE-017 short-horizon reversal | Event study with a matched null, replication across markets and eras, then a cost check |
| 4 | THE | THE-005 round numbers | Event study of the effect size (reversal probability at round levels against random levels), as the theory protocol requires; only the trading P&L has been tested so far |
| 5 | THE | THE-001 to THE-016 | Restate each verdict in event-study terms where the original test was a P&L test |
| 6 | IND | IND-019 HMM, IND-021 group | Information test, IND batch 002 |
| 7 | STR | from INFORMATIVE / SUPPORTED results | At most 3 new pre-registered strategy candidates (G6) |

## Progress update (2026-11-13, later)

| Goal | Status |
|---|---|
| **G2, indicators** | **Done** for the named candidates: IND batches 001–002 tested 31 indicators. 29 NONE; IND-001 (Coinbase premium) WEAK; IND-018 (HAR volatility forecast) INFORMATIVE for volatility. Only the remainder of the IND-021 group is left. |
| **G3, theories** | **Done, 17 days early.** All 17 theories now have a verdict based on the theory test (`categories/THEORY_REVIEW.md`, THE-005, THE-017, theory event batch 001). Only THE-001 (S&P 500, below costs) and THE-014 (USD-vs-USDT premium) are partly supported. |
| **G5, strategies** | Forward tests running: STR-008 (Coinbase premium) and **STR-023 (VWAP momentum BUY; started 2026-11-14)**, plus the daily paper tests. STR-025 (volatility sizing) is MIXED: a shadow on STR-023 only. |
| **G4, signals** | SP-032 to SP-035 Exness scoring scheduled for 2026-11-14 02:41 UTC; prospective screenshots needed from the user. |

| **G6, new strategies from evidence** | **Done 2026-11-14.** Three items qualified (IND-018, THE-001, THE-014). THE-001 is not tradable after costs; IND-018 is sizing only (STR-025 shadow); THE-014 → STR-026, rejected at the screen (TEST p 0.09). No new forward test. See `new_discovery/G6_DECISIONS.md`. |
