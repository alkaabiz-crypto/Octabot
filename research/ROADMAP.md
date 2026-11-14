# Roadmap: every step towards the goals (2026-11-14)

**Overall goal** ([`PLAN.md`](PLAN.md)): by **2027-11-30**, find at least one approach with a positive edge after realistic costs **on new data**, or show with documented evidence that none of the candidates has one. Paper trading only.

**Owner codes:** **C** = Claude (automatic or on request); **U** = you; **C+U** = both.

## G1: register every candidate — DONE (2026-11-13)

1. ✅ Define the four categories and their tests (`categories/`).
2. ✅ Number every past item (IND, STR, THE, SIG) in `CANDIDATES.md`.
3. ⏩ Ongoing: every new idea gets the next number in its category before it is tested. **Owner: C, from your suggestions.**

## G2: test every indicator — DONE for named candidates (2026-11-13)

1. ✅ IND batch 001: 17 indicators. 16 NONE; Coinbase premium WEAK; HAR volatility forecast INFORMATIVE.
2. ✅ IND batch 002: 14 indicators, all NONE.
3. ☐ IND batch 003 (optional, by 2026-11-30): the rest of the IND-021 group, about 10 more TradingView indicators you name or that are commonly used. Same test. **Owner: C.**
4. ☐ Use the one INFORMATIVE indicator (volatility forecast) only for risk: STR-025 shadow on STR-023 (step G5.6). **Owner: C.**

## G3: a verdict for every theory — DONE (2026-11-13)

1. ✅ Review which verdicts rested only on trading P&L (`categories/THEORY_REVIEW.md`).
2. ✅ Event studies: THE-005, THE-017, theory event batch 001 (THE-001/002/003/015/016).
3. ☐ Re-check the two partly supported theories on new data, once a quarter, starting 2027-02-15. **Owner: C.**
   - THE-001: S&P 500 zones + signal candle.
   - THE-014: Coinbase premium as USD-vs-USDT demand.
4. ☐ Test any new theory you send, using the event-study method, within one week of receiving it. **Owner: C+U.**

## G4: decide the signals category (SignalPro) — by 2027-01-31

1. ☐ **Tonight, 02:41 UTC:** score SP-032 to SP-035 on Exness prices (your broker's feed). Report whether the app's claims match. **Owner: C, scheduled.**
2. ☐ **Collect 50 PROSPECTIVE signals.** Screenshot each signal when it first appears ("Trade Active, 0/3"), with the phone clock visible, and send them in batches. **Owner: U** (about 3–6 a day → about 2–3 weeks).
3. ☐ Log each new screenshot the day it arrives (number, SHA-256, posting-time window). **Owner: C.**
4. ☐ Score every logged signal on Exness 1-minute prices once the archive updates (about a day later), with the frozen tracker rules. **Owner: C.**
5. ☐ Count the app's claim contradictions (e.g. "TP1 reached" vs Exness prices). **Owner: C.**
6. ☐ At 50 prospective signals: verdict PROFITABLE / UNPROFITABLE, plus CLAIMS ACCURATE / INACCURATE, against random entries with the same stops and targets. **Owner: C.**

## G5: every forward test reaches its decision — by 2027-11-30

1. ⏩ **Daily, automatic:** paper tests at 03:23 UTC; Coinbase premium (STR-008) at 04:47; STR-023 at 05:21. Each reports here. **Owner: C.**
2. ⏩ **Weekly, Mondays 05:13 UTC:** `STATUS_LATEST.md`, with trades, averages and anything due. **Owner: C.**
3. ☐ **First looks**, applied strictly by each test's pre-registered rule (pass, futility stop or continue). **Owner: C.**

   | Test | When | Rule |
   |---|---|---|
   | STR-023 (BTC, ETH) | at 100 trades each, about June 2027 | V2: NW t ≥ 2.50 and ≥ +0.05R |
   | STR-008 Coinbase premium | at 100 trades, about Nov 2027 | NW t ≥ 2.24 and ≥ +2 bp |
   | Gold KST ×2 | futility check at 100 legs | its own plan |
   | BTC/ETH Pivot Reversal | futility check at 200 legs | its own plan |
   | Library paper tests (other session) | at 100 trades | read-only evaluator: frozen rule vs V2 vs Hyperliquid fees |

4. ☐ **Venue check** for any test that passes: re-cost it with Exness swap and spreads, or Binance or Hyperliquid fees and funding. **Owner: C.**
5. ☐ **Decide on the three library paper tests:** keep (recommended) or stop. **Owner: U.**
6. ☐ **STR-025 shadow:** volatility-scaled sizing reported beside STR-023's forward results, from its first closed trades. **Owner: C.**
7. ☐ **Data safety:** each month, archive new forward ledgers and inputs to the private repository, and verify them from a fresh clone. **Owner: C.**

## G6: new strategies only from evidence — by 2027-02-28

1. ☐ List what qualifies. **Owner: C.**
   - Indicators: INFORMATIVE (so far only the volatility forecast, used for sizing).
   - Theories: SUPPORTED or PARTLY SUPPORTED (THE-001 on the S&P 500, THE-014).
2. ☐ For each, decide in writing whether it can become a tradable rule after costs. **Owner: C.** THE-001 is currently below costs, so probably not.
3. ☐ Turn at most **3** into pre-registered STR candidates, with a causal backtest (shared engine and gate tests) and, if it passes, a forward paper test. **Owner: C.**
4. ☐ Never more than 3, and never from a parameter search. **Owner: C.**

## G7: honesty check — monthly from 2026-12-01

1. ☐ Count every test run in the month (the whole family across both branches) and update the multiple-testing record. **Owner: C.**
2. ☐ Re-verify the frozen library (`verify_freeze.py`) and the archives (checksums). **Owner: C.**
3. ☐ Publish a monthly summary: what changed, what failed, what is still alive. **Owner: C.**

## Fixed dates

| Date | Step |
|---|---|
| 2026-11-14 02:41 UTC | Exness scoring of SP-032 to SP-035 (G4.1) |
| 2026-11-15 09:17 UTC | Read-only review of the other session's Batch 2 and the library paper tests |
| 2026-11-16 05:13 UTC | First weekly status (G5.2) |
| 2026-11-30 | Optional IND batch 003 (G2.3) |
| 2026-12-01 | First monthly honesty check (G7) |
| 2026-12-04 / 2026-12-10 | NFP and CPI captures (BLS key active) |
| 2027-01-31 | Signals verdict at 50 prospective (G4.6) |
| 2027-02-15 | First quarterly re-check of THE-001 and THE-014 (G3.3) |
| 2027-02-28 | At most 3 new evidence-based strategies (G6) |
| about 2027-06 | STR-023 first look (100 trades per market) |
| about 2027-11 | STR-008 first look (100 trades); overall-goal decision (2027-11-30) |

## What ends the programme early

- **Success:** any forward test reaches PASS and survives its venue check. It is then reported to you for a separate, reviewed decision. It is never traded automatically.
- **Clear negative:** every forward test hits its futility stop, and no new evidence-based candidate qualifies. That is reported as the documented answer: no candidate has an edge after costs on new data.
