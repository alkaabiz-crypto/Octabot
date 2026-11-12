# Causal impact assessment of the pending-order look-ahead (12 November 2026)

**Scope and constraints.**
- This continues the read-only audit in `AUDIT.md` (commit `12096071`), on branch `claude/dazzling-albattani-j6uys7`.
- **Nothing frozen was modified.**
  - The theory library and `library_forward` were read from a `git archive` extract of `origin/claude/download-skill-27d08k` (head `1a58ceea`).
  - Every frozen script was imported unchanged.
  - All replays ran in scratch storage.
- **Not modified:** the other session's branches, its Batch 2, the paper tests, their states, scheduled tasks and registries.
- **Not committed:** any raw data.
- `AUDIT.md` is left as it was. Section 10 lists where this assessment corrects it.

**Labels:** **[FACT]** verified fact (source code, data, logs, hashes); **[CALC]** calculation from the data; **[HYP]** hypothesis or interpretation; **[UNKNOWN]** not determined.

**Code and summary outputs are committed in `causal_impact/`** (same files; outputs under `causal_impact/results/`; no raw data). They originally ran from scratch storage. Directory: `/tmp/claude-0/-home-user-Octabot/673585c7-1020-5c5e-b0a9-ec953e6fb327/scratchpad/cia/scripts/`. SHA-256 prefixes:

| Script | SHA-256 | Purpose |
|---|---|---|
| `sim.py` | `59880c19` | independent simulator |
| `synthetic_tests.py` | `668fb3a1` | synthetic tests |
| `revalidate.py` | `715fd30a` | candidate revalidation |
| `screen_impact.py` | `44dc0d2f` | screen-level impact |
| `causality_scan.py` | `d6a9d860` | look-ahead scan, all theories |
| `causality_scan2.py` | `6ee44958` | high-power look-ahead scan |
| `stats_audit.py` | `c2d13064` | promotion-rule audit |
| `build_1m.py` | `375e49a8` | 1-minute bar rebuild |

Their JSON outputs are in the parent folder.

## 1. Executive summary

- **[FACT] The bug.** The frozen backtests of B9 (Fibonacci) and D4 (FVG), and the V1 minute verification, choose which pending limit order to trade using future prices. A newer order that fills first is ignored whenever an older order will fill later within its window. No real-time trader can follow that rule.
  - The **frozen forward tests do not do this**. They are causal, and their written rules (`FORWARD_RULES.md`) describe the causal rule.
  - The pre-registration requires decisions on closed candles. It never specified the frozen selection rule.
- **[CALC] Exact reproductions first.** All three frozen candidate results reproduce exactly on exact data, and so do all 42 affected screen combinations.
  - The gold and oil Exness 1-minute bars were rebuilt from the public tick archive with the library's own frozen bar builder. All 44 monthly tick files match the SHA-256 hashes recorded by the other session.
- **[CALC] Results with only the order selection made causal** (minute level, 2× costs):

| Candidate | Frozen 2025 / 2026 | Causal 2025 / 2026 | Forward-test model, its own costs (2025 / 2026) |
|---|---|---|---|
| ETH_FIB | +32.28 / +19.62 bp | **−19.95 / −9.73 bp** | −19.95 / −10.35 bp |
| OIL_FIB | +12.87 / +17.30 bp | **−2.54 / −9.64 bp** | −4.34 / −13.53 bp |
| GOLD_FVG | +4.78 / +10.97 bp | **−0.25 / +3.81 bp** | −1.99 / +2.17 bp |

- **[CALC] All four affected screen PASSes become FAIL** under causal selection: B9 on oil, ETH and BTC, and D4 on gold.
  - The other two PASSes (B7 on gold and Nasdaq) are not affected by this bug. They had already failed the frozen size test.
  - **No theory in the frozen library survives with a causal backtest.**
- **[CALC] Why the frozen backtest made money.** Trades that both rules take earn the same under both. ETH: +18.8 bp under both.
  - The frozen rule **swapped 388 trades averaging −38.8 bp** (taken causally) for **347 averaging +32.2 bp**, chosen with hindsight.
  - Oil: −21.0 → +10.5 bp. Gold: −18.2 → +5.3 bp.
- **[CALC] The forward pass rule is weak.** It requires mean ≥ +2 bp at 2× costs after 100 trades, with no significance test.
  - A strategy with zero true edge passes with probability **0.45** (ETH), **0.45** (oil) and **0.33–0.37** (gold).
  - At least one of the three zero-edge tests passes with probability **≈ 0.80**.
  - Even at the (negative) causal-backtest means, the chance is **≈ 0.56**.
  - The earlier "40–45%" figure is confirmed: ETH and oil are about 0.45, gold is lower (0.33–0.37).
- **[FACT] The new-discovery programme (batches 001 and 002) is not affected.** It is separate code with no pending orders.

## 2. Exact scope of the bug

**[FACT] Mechanism.** The frozen loop works like this (`verify_minute.py` `b9`/`d4`/`run_limit`, and `theories.py` `b9`/`d4_fvg`):
1. Evaluate the signal at candle *i*.
2. Scan **the whole** 10-candle window for that order's first fill.
3. If it fills at candle *k*, take that trade and continue after its exit.
4. If not, move to *i + 1*.

Suppose a newer signal *i′* (with *i < i′ < k*) produced an order that fills at *k′ < k*.
- A real trader holding both orders is filled at *k′*.
- The backtest instead skips that fill, because it already knows order *i* fills later.
- When the older order never fills, the two rules agree.

So the whole bias comes from the cases where **an older order is still pending and fills later**.

**[FACT] The live state shows the effect.** At 19:16 UTC the OIL_FIB book held BUY limits at 85.1603 (made 17:00), 85.4059 (18:00) and 85.4491 (19:00), all with stop 84.203.
- A dip to about 85.40 fills the 85.4059 order in the forward test.
- The frozen backtest would take the deeper 85.1603 entry whenever price reaches it later. That is a better price, known only in hindsight, with the same stop.

**[CALC] How often the selection matters.** In the causal forward model, other orders were pending at the time of the fill in:
- ETH: 571 of 655 fills (87%);
- oil: 360 of 414;
- gold: 319 of 696.

Only 267 of the 614 frozen ETH trades (43%) are taken by the causal rule.

**[FACT] Specification status.**
- `PREREGISTRATION.md` §"Common execution rules": "Decisions are made on a closed candle". It does not say how to handle overlapping pending orders, or the 10-candle validity used for B9 and D4. F9 does specify "valid 20 candles".
- `FORWARD_RULES.md` states the causal rule ("several orders can be pending at once … the oldest pending order that fills is taken"). It then claims the rules were "copied unchanged" from the backtest, which is **false** for the selection rule.
- The backtest therefore violates the pre-registration's own decision-timing rule. The forward test is the faithful implementation.

## 3. Affected-strategy inventory (traced code paths)

All 63 executed theory IDs and the frozen verification scripts were read in full (the theory engines total 1,460 lines).

**Empirical check.** Every theory function was also run unchanged on synthetic markets, then re-run with the path after a cut replaced (§5, R4 and the scan):
- first scan: 63 theories, 228 combinations, 6 cuts each;
- second scan: 32 event-driven theories, 60 cuts each.

A causal theory can never change a decision taken before the cut.

### Affected

| Strategy / script | Code location | Execution logic | Look-ahead? | Severity | Revalidation needed / result |
|---|---|---|---|---|---|
| **B9 screen** (Fibonacci) | `theories.py` 222–234 | limit order, 10 candles; if unfilled, `i += 1` | **YES** [FACT]; empirical: 6 of 180 cuts changed past decisions | **HIGH** | Screen PASSes on oil, ETH and BTC → all **FAIL** causally [CALC] |
| **D4 screen** (FVG) | `theories.py` 387–398 | same | **YES** [FACT]; empirical: 3 of 18 cuts (first scan) | **HIGH** | Screen PASS on gold → **FAIL** [CALC] |
| **V1 / V3** minute verification | `verify_minute.py` 27–69 (`run_limit`, `b9`, `d4`) | same, minute fills | **YES** [FACT]; reproduced exactly by an explicit look-ahead re-implementation (R3) | **HIGH** | All three V1 passes → **FAIL** (§6) |
| **V2** neighbouring settings | `verify_neighbours.py` 15–42 | same | **YES** [FACT] | **HIGH** | Screen-level holdout-positive, frozen → causal: B9 ETH 9/9 → **1/9**; B9 BTC 3/9 → 0/9; B9 oil 9/9 → 9/9; D4 gold 9/9 → 9/9 [CALC] (see note) |
| Candidate statistics | `candidate_stats.py` | calls `verify_minute` | inherits | HIGH | Replaced by §6 |
| Missing-data sensitivity | `sensitivity_hole.py` | re-runs all theories | inherits for B9, D4, C3, C4 and F9 | MEDIUM | Verdicts for those IDs are superseded by §3 below |
| **C3** inside-bar break | `theories.py` 281–299 (`stop_break`, 5 candles) | stop bracket; if not triggered or ambiguous, `i += 1` | **YES**, by code structure [FACT]; not detected empirically in 360 cuts (low power) | LOW (measured) | 14 combinations; trade sets 90–100% identical; all FAIL under both rules |
| **C4** NR7 break | `theories.py` 302–303 (`stop_break`, 3 candles) | same | **YES**, by structure [FACT] | LOW | 7 combinations; 6 identical, BTC 61/62; all FAIL under both |
| **F9** order block | `theories_f.py` 115–135 | limit order, 20 candles; unfilled → continue | **YES**, by structure [FACT]; **missed by `AUDIT.md`** | LOW | 7 combinations; 86–93% identical; all FAIL under both |

**Note on V2 for oil and gold.** Screen-level causal oil (+6.4 / +15.0 bp) and gold (+2.2 / +6.4 bp) stay positive in the holdout for all 9 settings, but they still fail the screen's random-control rule.
- [FACT] The screen fills a limit at a touch, with no spread penetration.
- [CALC] At minute level, with the frozen one-spread penetration, causal oil is negative and gold is about zero (§6).
- [HYP] The screen-level figures are therefore optimistic for limit entries, independently of this bug.

### Screen-level frozen vs causal (2× costs, dev 2025 / holdout 2026 mean bp)

[CALC] All 42 frozen rows reproduce `results/results.json` exactly. `screen_impact.json` holds every field.

| Combination | Frozen dev / hold, verdict | Causal dev / hold, verdict |
|---|---|---|
| B9 ETHUSDT 1h | +35.01 / +19.73, PASS | +0.56 / −3.13, **FAIL** |
| B9 USOILm 1h | +18.28 / +25.95, PASS | +6.42 / +15.00, **FAIL** (below the random 95th percentile) |
| B9 BTCUSDT 1h | +3.92 / +4.08, PASS (t = 0.54) | −7.11 / −12.36, **FAIL** |
| D4 XAUUSDm 1h | +5.61 / +11.71, PASS | +2.20 / +6.37, **FAIL** (below the random 95th percentile) |
| other B9 / D4 (10) | all FAIL | all FAIL; means lower in 19 of 20 period values |
| C3 (14), C4 (7), F9 (7) | all FAIL | all FAIL; small changes in both directions |

### Not affected by this bug (traced)

| Strategy | Why |
|---|---|
| All `from_positions` strategies: A1–A12; B1–B6; F1–F5; G3–G10 | Market entry at the next open from closed-candle decisions. |
| `px_trade` and market-entry strategies: B7, B10, C1, C2, C5, C6, D2, D5, D6, E1–E4, F6–F8, F10, **F11**, F12, G1, G13, G14 | Entry at the next open; one position; nothing pending. |
| B8 (pivot fade) | One first touch per day. **Separate issue:** stop and target are not checked on the fill candle (optimistic). B8 failed the screen. |
| A13, D1 (Asian range), G2 | Two-sided first touch per day. **Separate issue:** if one candle touches both sides, the trade or day is skipped. That is a same-candle (intrabar) decision, a different class of problem. Magnitude [UNKNOWN]. The scan cannot detect it. |
| D3 (Silver Bullet) | One setup per day; its limit is never retried. |
| Other frozen studies: `orb_study` (v1, v2), `zone_reversal_study`, `session_study` | One bracket per day or market entry, one position. ORB skips breaks on both sides of one bar (same-candle class). |
| Other paper traders (gold Asia, MOM50, oil stochastic, BTC breakout, daily DCA) | No limit or pending-order logic found by search and reading. [HYP] Not exhaustively traced. |

**[FACT] Two flags in the first scan were explained:**
- D4 is genuine.
- G7 is a bookkeeping artifact: `from_positions` drops a final position still open at the end of the data. Every pre-cut decision was identical.

## 4. Forward execution state machine (as implemented in `library_forward/forward.py`)

[FACT] From the code, confirmed by the synthetic tests (§5) and by reproducing the live books.

**At each new closed 1-minute candle *t*, in order:**
1. **Signal.**
   - Generated only if *t* is an hour boundary, no position is open, and *t* ≥ `next_check`.
   - The exchange 1-hour candle ending exactly at *t* must exist. If the minute at *t* is missing, that hour gets no signal.
   - The signal is computed from closed 1-hour candles only (FVG: the last 3 candles; Fibonacci: the last 50).
   - A signal **appends** a pending order: side, limit, stop, target, made = *t*, expires = *t* + 10 h (wall clock).
   - **No cap** on the number of pending orders: 7 were held in test C8. At most 10 are alive, because an order expiring at *t* is purged after a new one is appended.
   - Existing orders are never replaced by new signals.
2. **Fill** (only if flat).
   - Orders with *t* ≥ expires are purged.
   - Pending orders are scanned **oldest first**. The first whose condition holds on this minute is filled:
     - buy: low ≤ limit − penetration; sell: high ≥ limit + penetration;
     - penetration: gold and oil a fixed 0.22 or 0.02 USD; ETH 1 bp of the limit.
   - Fill price: min(open, limit) for a buy, max for a sell. A gap through the limit fills at the open.
   - **All other pending orders are cancelled.** At most one position.
3. **Exit**, checked on the same minute as the fill. The first that applies:
   1. stop gap (after the fill minute): exit at the open;
   2. stop (from the fill minute): exit at the stop;
   3. target (after the fill minute, with penetration): exit at the target;
   4. time: at the close of the last minute before fill-hour start + 21 h, i.e. 20 hours after the fill hour.
4. **After an exit:** `next_check` = the exit hour's start + 2 h.

**Costs.**
- Gold and oil: one fixed spread per round trip (2× for the main result). Hyperliquid fees and funding are **not modelled**.
- ETH: 0.05% × (entry + exit).

**Safety.** The test STOPS on a weekday 1-minute gap over 90 minutes while an order or position is active, or if the feed no longer reaches back to the cursor. Each minute is processed exactly once (cursor). Test D1 shows that hourly incremental runs, including repeated runs with no new data, equal one run, with no duplicate ledger rows.

**Live state reproduced.** [FACT] Replaying public data from each test's start, the simulator rebuilds the books held at 19:16 UTC:
- **ETH_FIB:** SELL 2044.4458 (made 18:00) and SELL 2034.8668 (19:00) — **exact match**.
- **OIL_FIB:** BUY 85.1603, 85.4059 and 85.4491 (17:00, 18:00, 19:00) — **exact match** when the replay starts from the live start minute (16:44), with Hyperliquid's native 1-hour candles.
  - **[FACT] Discrepancy found and resolved.** Building oil's hourly candles from minutes, and starting days earlier, gave a different book. The replay was already in a position at 17:00, so it placed no new orders.
- **GOLD_FVG:** an empty book (not re-derived).

**Backtest clock vs forward clock.** [FACT] The backtest counts the next 10 hourly candles that exist in the data. The forward test counts 10 wall-clock hours.
- They are identical for ETH, which has no gaps.
- They differ for gold and oil across daily breaks and weekends. [CALC] The two clocks give gold 2026 +3.81 bp (candle) vs +1.77 bp (wall clock).

## 5. Synthetic tests

[CALC] `synthetic_results.json`: **16 of 16 passed.** The three engines tested:
- **FROZEN:** `verify_minute`, unchanged;
- **FWD:** `forward.py`, unchanged (SHA-256 `1db10cc2…`, identical to the manifest entry);
- **SIM:** the independent simulator.

### Crafted cases

Signals are injected at chosen hours. The expected result is stated in advance, and SIM and FWD must both match it.

| ID | Case | Result |
|---|---|---|
| C1 | An older order is pending; a newer order fills first; the older one would fill later | Newer taken, older cancelled (the frozen rule would take the older one). PASS |
| C2 | An older order fills after a newer signal appeared | Older taken, newer cancelled. PASS |
| C3 | Two pending orders fill on the same minute | **Oldest** wins, even though the newer one has a better price. PASS |
| C4 | An order is first touched exactly at its expiry minute while a newer order is pending | Expired order not filled; the newer one fills later. PASS |
| C5 | Gap through the limit | Fill at the minute open (98.2 vs limit 99). PASS |
| C6 | Fill, stop and target on the same minute | Stop on the fill minute; the target is ignored on the fill minute. PASS |
| C7 | A signal while in a position; next check after an exit | Ignored; next order only from exit hour + 2 h. PASS |
| C8 | 7 pending orders at once | No cap; the oldest whose level is reached fills. PASS |
| F1 | Two genuine bullish FVGs, newer order fills in hour 4, older (deeper) in hour 5 | FROZEN takes the older one (05:19, 100.92). FWD and SIM take the newer one (04:20, 102.9). PASS |
| F2 | Same path, prices after 04:59 changed | The position FROZEN holds at 04:59 changes (none → long). SIM's does not. PASS |

### Randomized cases (40 seeds, 20-day random walks with gaps)

| ID | Test | Result |
|---|---|---|
| R1 | SIM (wall clock) vs `forward.py`, ETH-style fee rule | **Identical, trade for trade**: Fibonacci 40/40 seeds, FVG 40/40. PASS |
| R2 | SIM vs `forward.py`, fixed-spread rule (gold/oil style) | Identical, 40/40 seeds. PASS |
| R3 | SIM's explicit look-ahead selection vs frozen `verify_minute` | Identical, 40/40 seeds each. This shows **selection is the only difference** between the frozen backtest and the causal model. PASS |
| R4 | Prefix invariance: future after a mid-hour cut replaced | Pre-cut decisions changed in: FROZEN **9 of 240** cuts; SIM wall clock 0/240; SIM candle clock 0/240; FWD 0/80. PASS |
| R5 | Timeline invariants (1,523 SIM trades) | 0 fills before creation, 0 after expiry, 0 overlapping positions, 0 exits before the fill, 0 signals before `next_check`. PASS |
| D1 | `forward.py` run hourly in increments, plus 3 repeated runs, vs a single run | Identical ledgers; no duplicates. PASS |

## 6. Frozen vs causal revalidation (candidates)

### Data

- **[FACT] ETH.** Binance ETHUSDT spot 1-minute klines, from the public monthly and daily files at `data.binance.vision`.
  - 2025-01-01 00:00 to **2026-11-10 11:19 UTC** (the frozen cutoff): 977,000 minutes, no gaps.
  - The common-cutoff subset keeps 2026 trades exiting before 2026-11-10 00:00. The last hourly screen candle is 2026-11-09 23:00.
- **[FACT] Gold and oil.** Exness XAUUSDm and USOILm **1-minute** mid bars with the per-minute median spread.
  - Rebuilt from the public monthly tick zips (`ticks.ex2archive.com`, 2025-01 to 2026-10) with the frozen `orb_study/build_bars.py` `bars()` function, unchanged.
  - All **44 of 44** monthly zip SHA-256 hashes equal those recorded in `research/shortlist_2025/results/results.json` on the other branch.
  - Gold: 648,069 minutes, 2025-01-01 23:05 to 2026-10-30 20:57. Oil: 636,623 minutes, 23:11 to 20:56.
  - This is the library's own resolution. **It is not tick-level validation.** Fills at the order of events inside a minute are not resolved.
- **[FACT] Indices** (DE30m, US500m, USTECm) were rebuilt the same way, for the screen only. Their zip hashes were not cross-checked against a record (none was found). The exact reproduction of every screen row validates them.

**Engines** (`revalidate.json`):
- **FROZEN:** `verify_minute`, unchanged.
- **CAUSAL_CANDLE:** identical except the selection rule (the minimal correction).
- **CAUSAL_WALL:** the forward state machine, with the backtest's per-minute costs.
- **FORWARD_COSTS:** the forward state machine, with `forward.py`'s fill and cost rules.
- [FACT] For all three markets, SIM's look-ahead mode equals FROZEN trade for trade.
- For ETH, FORWARD_COSTS equals the earlier replay of the frozen `forward.py` itself (354 trades / −19.95 bp; 300 / −10.35 bp).

### Results

[CALC] 2× costs. CIs are 95%: the t interval, then a stationary block bootstrap (mean block of 5 trades, 4,000 resamples). The NW t uses Newey–West with 5 lags. Drawdown is of compounded equity at trade closes, with the whole account in each trade. Exposure is the share of data minutes in a position.

| Market / period | Engine | Trades | 1× bp | 2× bp | Win | PF | Cost bp | Max DD | Exposure | t / NW t | 95% CI (t; bootstrap) bp |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ETH 2025 | FROZEN | 326 | +42.28 | **+32.28** | 0.515 | 1.42 | 20.0 | −23.7% | 40% | 2.68 / 2.67 | 8.7…55.9; 7.9…57.8 |
| ETH 2025 | CAUSAL | 354 | −9.96 | **−19.95** | 0.401 | 0.79 | 20.0 | −61.5% | 38% | −1.88 / −1.78 | −40.7…0.8; −42.0…2.2 |
| ETH 2026 | FROZEN | 288 | +29.62 | **+19.62** | 0.524 | 1.34 | 20.0 | −20.4% | 39% | 2.05 / 1.82 | 0.9…38.4; −0.6…43.2 |
| ETH 2026 | CAUSAL | 301 | +0.26 | **−9.73** | 0.419 | 0.86 | 20.0 | −42.7% | 37% | −1.05 / −0.97 | −27.9…8.4; −28.3…9.9 |
| ETH 2026 common cutoff | FROZEN / CAUSAL | 287 / 300 | | **+19.09 / −10.34** | | 1.33 / 0.85 | | | | 1.99 / −1.12 | |
| ETH full | FROZEN | 614 | +36.34 | +26.35 | 0.520 | 1.39 | 20.0 | −23.7% | 40% | 3.37 / 3.21 | 11.0…41.7 |
| ETH full | CAUSAL | 655 | −5.26 | **−15.26** | 0.409 | 0.82 | 20.0 | −69.7% | 37% | −2.14 / −2.00 | −29.2…−1.3; −29.8…−0.2 |
| Oil 2025 | FROZEN | 211 | +15.81 | **+12.87** | 0.517 | 1.29 | 5.9 | −10.3% | 36% | 1.63 / 1.84 | −2.6…28.3 |
| Oil 2025 | CAUSAL | 225 | +0.38 | **−2.54** | 0.440 | 0.95 | 5.9 | −20.5% | 33% | −0.36 | −16.3…11.2 |
| Oil 2026 | FROZEN | 178 | +20.09 | **+17.30** | 0.461 | 1.22 | 5.6 | −17.4% | 35% | 1.04 / 1.20 | −15.4…50.0 |
| Oil 2026 | CAUSAL | 186 | −6.89 | **−9.64** | 0.398 | 0.89 | 5.5 | −29.8% | 32% | −0.65 | −38.7…19.4 |
| Oil full | CAUSAL | 411 | −2.91 | −5.75 | 0.421 | 0.91 | 5.7 | −32.2% | 33% | −0.75 | −20.9…9.4 |
| Gold 2025 | FROZEN | 388 | +5.26 | **+4.78** | 0.399 | 1.27 | 1.0 | −4.0% | 31% | 1.88 / 2.13 | −0.2…9.8 |
| Gold 2025 | CAUSAL | 402 | +0.23 | **−0.25** | 0.348 | 0.99 | 1.0 | −9.0% | 32% | −0.10 | −5.1…4.6 |
| Gold 2026 | FROZEN | 311 | +11.59 | **+10.97** | 0.421 | 1.44 | 1.2 | −5.4% | 31% | 2.42 / 2.42 | 2.1…19.8 |
| Gold 2026 | CAUSAL | 316 | +4.42 | **+3.81** | 0.370 | 1.13 | 1.2 | −11.2% | 31% | 0.86 / 0.95 | −4.9…12.5 |
| Gold full | CAUSAL | 718 | +2.07 | +1.53 | 0.358 | 1.06 | 1.1 | −11.2% | 31% | 0.64 | −3.2…6.2 |

**The forward model** (wall clock), 2025 / 2026 / full, 2× bp:

| Market | Backtest costs | Forward costs |
|---|---|---|
| ETH | −19.95 / −10.34 / −15.55 | −19.95 / −10.35 / −15.55 |
| Oil | −3.56 / −10.86 / −6.78 | −4.34 / −13.53 / −8.42 |
| Gold | −1.65 / +1.77 / −0.14 | −1.99 / +2.17 / −0.16 |

**Reading the results:**
- **[CALC]** No candidate meets the frozen candidate criterion (> 0 and ≥ 2 bp at 2× costs in both periods) under any causal model.
- Gold 2026 is the only causal period above +2 bp, and only under the candle clock (+3.81). It is not significant (t 0.86).
- Causal ETH over the full period is **significantly negative**: the bootstrap upper bound is −0.2 bp.

**[CALC] Adversarial robustness: other causal execution policies.** Two disclosed alternatives (not a parameter search), candle clock, 2× bp, 2025 / 2026:

| Market | Keep oldest, ignore new signals | Newest replaces older | `forward.py` rule |
|---|---|---|---|
| ETH | −15.18 / −26.73 | −21.36 / −10.79 | −19.95 / −9.73 |
| Oil | −11.23 / −32.10 | −2.96 / −17.30 | −2.54 / −9.64 |
| Gold | +0.09 / +2.04 | −0.25 / +4.06 | −0.25 / +3.81 |

No causal policy restores the frozen edge. [HYP] The prefix test (R4) shows that no causal policy can reproduce the frozen trade set.

**[CALC] Mechanism decomposition** (2× bp per trade, `stats_audit.json`):

| Market | Common trades: frozen / causal | Frozen-only | Causal-only |
|---|---|---|---|
| ETH | 267 trades: +18.78 / +18.98 | 347: +32.17 | 388: **−38.81** |
| Oil | 149: +21.94 / +21.03 | 240: +10.53 | 262: **−20.98** |
| Gold | 537: +8.20 / +8.20 | 162: +5.34 | 181: **−18.24** |

The frozen rule discards exactly the trades a real trader would have suffered.
- [HYP] The common trades are positive in all three markets, but they are not a tradable subset. Which trades are "common" is known only in hindsight.

**Not reproduced or unresolved:**
- [UNKNOWN] Intrabar ordering inside a minute.
- [UNKNOWN] Hyperliquid prices, fees and funding versus Exness, for the gold and oil paper tests.
- [UNKNOWN] Exness swap. Not deducted anywhere, per the frozen rules.

## 7. Statistical promotion-rule audit

### Forward pass rule

[FACT] After **100** closed trades (a single look), it requires mean net ≥ +2 bp at 2× costs. There is no significance test, and no correction for running three tests.

[CALC] `stats_audit.json`. Trade returns are drawn from each candidate's causal forward-model distribution, re-centred to the stated true mean:

| P(pass) | ETH (sd 182.5 bp) | Oil (sd 151.9) | Gold (sd 59.9) |
|---|---|---|---|
| true mean 0: normal / iid bootstrap / block bootstrap | 0.456 / 0.445 / 0.453 | 0.448 / 0.452 / 0.445 | 0.369 / 0.361 / 0.331 |
| true mean = causal backtest mean (−15.6 / −8.4 / −0.2 bp) | 0.17 / 0.16 / 0.18 | 0.25 / 0.25 / 0.22 | 0.36 / 0.35 / 0.32 |
| true mean +10 bp | 0.67 / 0.66 / 0.65 | 0.70 / 0.71 / 0.73 | 0.91 / 0.91 / 0.94 |
| trades for 80% power, one-sided 5%, +10 bp edge | 2,061 | 1,427 | 223 |

- At least one of three zero-edge tests passes: **0.797**.
- At least one of three passes at the causal-backtest means: **0.564**.
- **Verdict.** The earlier "40–45%" is correct in method for ETH and oil, and it does reflect the actual single-look procedure. Gold is lower (≈ 0.33–0.37), because the forward-model sd (60 bp) is below the 80 bp used before. The rule cannot separate a zero edge from a real one at n = 100.

### Random benchmark (`engine.random_control`, 500 draws)

[FACT]

| Attribute | Matched? |
|---|---|
| Direction | yes (same sides) |
| Holding period | yes (same candle counts) |
| Costs | yes (same 2× half-spread formula) |
| Period | yes |
| Signal timing | **no** (uniform random starts) |
| Entry mechanism | **no** (open, vs limit or stop) |
| Exits | **no** (time only, vs stop/target) |
| One-position constraint | **no** (random draws overlap; the strategy never does) |
| Selection over 535 combinations | **not corrected** |

- **[CALC] Calibration failure.** The 95th percentile is often **below zero** (B9 BTC holdout −7.33 bp; ETH −0.92 bp).
  - "Beats random" can therefore pass a strategy indistinguishable from zero: **B9 BTC passed with t = 0.54 in both periods.**
- [FACT] It cannot detect order-selection look-ahead, because the bias is in which trades are taken.

### Serial dependence

- [CALC] Newey–West and block-bootstrap results are in §6.
- In `AUDIT.md`, the frozen ETH 2026 Ljung–Box Q(5) of 14.05 was significant. Causal results stay insignificant or negative under every method.
- The CI depends on the bootstrap block length. `AUDIT.md` used a mean block of 10, this assessment uses 5. Frozen ETH 2026 gives −3.2…+44.8 vs −0.6…+43.2. Both include zero.

### Multiple testing

[FACT] The frozen screen reports Bonferroni |t| ≥ ~3.9 for 535 combinations. The actual family on the same 2025–2026 data in the frozen research, from result files, is at least:

| Study | Configurations |
|---|---|
| Theory screen | 535 (plus 2 earlier full runs of 416) |
| V2 neighbours | 54 |
| V1 minute verification | 3 |
| ORB | 40 + 56 |
| Zone reversal | 60 |
| `oil_dca_bot` | 360 + 96 + 18 + 28, plus tuning grids |
| SignalPro | 10 |
| Shortlist, session and other studies | further tests |

- **Total:** at least about 1,260 distinct configurations, plus repeated looks. Bonferroni |z| is about 4.1.
- [CALC] The best frozen candidate statistic is ETH's full-sample t of 3.37 (Newey–West 3.21). It is below that threshold **even with the look-ahead**.
- No correction covers the whole family.

### Sample sizes

[CALC] The per-year standard errors are 9–12 bp for ETH, 7–16 bp for oil and 2.5–4.5 bp for gold. One year of data cannot resolve edges of 2–10 bp, except perhaps for gold.

### Recommended alternatives (not implemented; the frozen rules are unchanged)

These would need a **new, separately pre-registered** decision document. `FORWARD_RULES.md` would not be edited.
- (a) Pass only if a one-sided block-bootstrap p-value is below 0.05 at 2× costs **and** mean ≥ 2 bp.
- (b) Size each test from a power calculation using the observed sd (above), and say in advance that ETH and oil cannot be validated within a practical horizon.
- (c) Control the family across all concurrent paper tests, for example with Holm.
- (d) Replace the random control with a matched null: random limit levels through the same fill, stop, target and one-position machinery, plus a sign-flip test, compared against zero and against the maximum over the searched combinations.

## 8. Discovery programme status

[FACT]
- `research/new_discovery/batch_001` (D001–D004) and `batch_002` (E005–E009) use their own code (`src/common.py`, `run_batch.py`). They import nothing from the theory library, and they place **no limit or pending orders**.
- Positions are decided at a candle's completion time and executed at the first 15-minute open at or after it. The pairs code in `leg_returns` was checked.
- They do **not** share this bug. Their own limitations (TEST is reused evaluation data, the EWMA scaling in E006) are recorded in their results files.
- No new batch was launched.
- The other session's Batch 2 was neither inspected nor touched. Whether it shares the flaw is [UNKNOWN].

## 9. Verification passes and discrepancies

**Pass 1: source.**
- [FACT] All 90 freeze-manifest files were checked by `sha256sum -c` against the manifest taken from commit `9c158d62` itself. `verify_freeze.py` also reports intact.
- Code paths were read in full.
- ETH and oil live books were reproduced from public feeds. Tick SHA-256s match 44 of 44.

**Pass 2: recalculation.**
- [CALC] Every frozen number was reproduced exactly: ETH 326 / 288 / 287; oil 211 / 178; gold 388 / 311; 42 of 42 screen rows.
- Causal ETH agrees across three implementations: the earlier `audit_eth_fib.py` (354 / −19.95; 301 / −9.73), the new simulator, and the frozen `forward.py` replay (354 / −19.95; 300 / −10.35).

**Pass 3: timeline.** [CALC] R4, R5 and D1. No future-dependence, duplicate processing, timestamp or state inconsistency was found in the causal engines or in `forward.py`. The look-ahead is confirmed in the frozen engines.

**Pass 4: adversarial.**

| Challenge | Outcome |
|---|---|
| "The pre-registration specified the frozen rule" | Rejected. It specifies decisions on closed candles and is silent on overlapping orders. |
| "The forward test is the deviation" | Rejected. Its written rules describe the causal rule, and it reproduces the live books. |
| "Another causal policy rescues the edge" | Rejected: 2 alternatives, all ≤ +4 bp, none passes. |
| "The 15-minute approximation drove `AUDIT.md`'s gold/oil conclusion" | Corrected: exact 1-minute data makes oil **worse** (−2.5 / −9.6 bp vs +2.8 / +0.1). |
| "C3, C4 and F9 must be badly affected too" | Not supported: measured impact is small and no verdict changes. |
| "The scan proves C3, C4 and F9 are causal" | Not supported: the scan lacks power, so their status rests on code structure. |
| "Hindsight selection is all the edge" | Supported: trades common to both rules earn the same under both. |

**Discrepancies documented:**
- The oil book differed under minute-built candles and an early start (resolved, §4).
- G7 scan flag: an artifact.
- D4 detection varies between scans: power.
- Bootstrap block length differs between documents.
- The wall clock and candle clock differ for gold and oil.

## 10. Corrections to `AUDIT.md` (that document is left unchanged)

1. **F11 is not affected.** It enters at market; its `done` flag only controls the loop. **F9 is affected** and was missed. C4 also uses `stop_break`.
2. **Gold and oil causal figures** from the 15-minute approximation (gold −0.04 / +4.71; oil +2.75 / +0.06) are **superseded** by exact 1-minute data: gold −0.25 / +3.81; oil −2.54 / −9.64 (candle clock).
3. The **"one order at a time" column is not the forward model.** It is the keep-oldest alternative policy (§6).
4. **Mechanism wording.** The bias arises when an older pending order fills *later* than a newer order. When the older order never fills, the frozen and causal rules agree.
5. **Gold's zero-edge pass probability** is ≈ 0.33–0.37, not ≈ 0.40.

## 11. Data and licensing limitations

- [FACT] Binance and Exness data are third-party data. They are kept in scratch storage only and **not committed** (public repository).
  - Binance public data terms apply.
  - The Exness tick archive's terms were **not verified** [UNKNOWN].
  - Hyperliquid's public API was used only to check the live books.
- **Hashes identify files; they do not preserve them.** The scratch data will disappear with this session's container.
  - The Exness archive (earlier package, verified 388 of 388 files) still awaits a private repository from the user.
  - Exness data ends on 2026-10-30. Gold and oil results after that date are [UNKNOWN].
- [UNKNOWN] The magnitude of the same-candle ambiguity rules (A13, D1, G2, `stop_break`, ORB) and of B8's unchecked fill candle.

## 12. Recommended remediation (none implemented; each needs your authorisation)

1. **Record an erratum, without editing frozen files.** Add a pointer from the library's documentation to this assessment in a separate, clearly labelled commit. The frozen hashes stay valid.
2. **Paper tests.**
   - Keep ETH_FIB, OIL_FIB and GOLD_FVG running **unchanged**: they are valid causal tests. Re-label their prior expectation as "causal backtest ≤ 0" (§6).
   - Do **not** treat a pass under the frozen rule as validation (§7).
   - Whether to stop them is your decision. No change has been made.
3. **Causal re-screen as a new, labelled study.**
   - Re-run B9, D4, C3, C4 and F9 with causal selection, minute-level fills and penetration. Report it alongside the frozen screen.
   - It reuses inspected data, so it is screening only, with no promotion.
4. **Engine fix for future research.**
   - Use a single causal order-book module shared by backtests and forward tests.
   - Gate it with the prefix-invariance test (R4) and the frozen-vs-forward equivalence test (R1) before any result is reported.
5. **Pre-register a new promotion rule** (§7, items a–d), separately.
6. **Open items:**
   - audit the same-candle ambiguity rules on 1-minute data;
   - check B8's fill-candle stop;
   - model Hyperliquid fees and funding for the gold and oil paper tests;
   - inspect the other session's Batch 2 for pending-order logic, only if you ask.
