# Forward (prospective) test plan

Written and committed on **12 November 2026**. At that point no forward outcome existed:
- every paper-test ledger had 0 recorded trades;
- no news capture had run;
- no ADP-contrarian observation existed.

The retrospective ADP investigation is frozen (`FREEZE_NOTE.md`). The tests below read the frozen files but do not change them. All tests are **paper only: no orders are placed.**

## General rules (apply to every section)

- **Outcomes.** Each programme ends as exactly one of **PASS**, **FAIL** or **INCONCLUSIVE**, as defined in its section and in Part 4.
- **No rescue.** Thresholds are never lowered, tests are never extended beyond their stated N, and parameters are never changed after outcomes are seen.
- **What counts.** Net returns after the stated costs. Win rate alone never decides anything.
- **Missing data and execution failures.**
  - A scheduled run that fails is re-run. The paper tests replay deterministically from the Exness archive, so a late run loses nothing.
  - Archive data that is permanently missing is logged and excluded, never filled in or replaced.
  - A news capture that times out or is refused is logged as missing. It does not count toward N and is never re-created afterwards.
- **Locked code.** The code below is locked by SHA-256. A hash mismatch stops the affected test until it is reviewed.

| File (under `research/`) | SHA-256 |
|---|---|
| `news_surprise/live/capture.py` | `7e94219a21a81e0d399730673086a51e11a7bbc82c4754b32bf8a1efc14f7a87` |
| `news_surprise/live/evaluate.py` | `1181b2e01927ae52fba49c4967e3eedd5df65d9794372f3d50eb9ce835726b11` |
| `news_surprise/live/adp_contrarian_forward.py` | `58ba39dec3ea0de1cf9dd34f15f0aeff7c72ab547b3932cdae72a798d0f7e5bd` |
| `gold_kst_paper/src/briefing.py` (writes the consensus log) | `5a3460ff4bf1e1a4643bd7ce170c1ff51b9b4bd395975990e1b49fca590bf15e` |
| `pivot_reversal_paper/src/config.py` / `paper.py` | `dfb533bedcf490a8e969b35d5fe4e3387e1ce621d16f0f7ed814daf7226127f1` / `1011b085ac862533a382fbd5c27735c38aef695c12f335560b5b085cc17727b2` |
| `eth_pivot_paper/src/config.py` / `paper.py` | `129b9888c9d1ddcda8bae11632c1e08345f9c596cf8970c8d42eb6d02b630f28` / `9a262c49bfbf075dca6c41ce462764483e6c80c01e4f6c19593255277daa3768` |
| `gold_kst_paper/src/config.py` / `paper.py` | `4c0de3eab860919b84bf78aed9a394f8afa9d2cf800bff0a5e4e2c8743d75cdb` / `af9ff30d64fbeb393d48bea57fc860dd520dd59a5241132a47533755bbe6cb0f` |
| `gold_kst_risk_paper/src/config.py` / `paper.py` | `79fee3e0b79d0a22992f2a087271cd9c6fa21cf8638d971f49648aad3453ead0` / `97a653af939299dd28b0b2379e857c5f75df8cc8884555b5f211f5a897494ffd` |
| `audit/src/seq_held.py` (ETH benchmark) | `56cfd1b38a855ee067b9514a742fc8b15bd508b74d1c0d65eaf436090f222740` |

---

## A. Release capture: US jobs report, 4 December 2026

**Event.**
- BLS Employment Situation for November 2026.
- Release at **08:30:00 New York time = 13:30:00 UTC on 2026-12-04**. The date is from the St. Louis Fed release calendar and is checked against the weekly economic calendar before the run.

**Data sources.**
- *Actual figures.* BLS public API v2 (`https://api.bls.gov/publicAPI/v2/timeseries/data/`, POST, `latest=true`), with the user's key from the environment variable `BLS_API_KEY`.
  - Series `CES0000000001`: total nonfarm payrolls, seasonally adjusted, in thousands.
  - Series `LNS14000000`: unemployment rate.
- *Consensus.* The last forecast for "Non-Farm Employment Change" and "Unemployment Rate" logged in `data/consensus_log.csv` before 13:30:00 UTC. The source is the weekly economic-calendar feed, logged by the daily briefing.

**Instruments.** Exness XAUUSDm, EURUSDm, GBPUSDm and USDJPYm. Prices come from the Exness public tick archive, as every bid/ask quote with a UTC millisecond timestamp.

**Capture procedure (`live/capture.py`).**
1. A scheduled task starts at 13:12 UTC.
2. Before the release, the script caches the latest published payroll level and unemployment rate.
3. From T−15 s it polls the BLS API about once a second, for up to 5 minutes.
4. It records **first_seen**: the machine's UTC time of the first response showing the new reference month.
5. It estimates the clock offset from the BLS `Date` header. This is only accurate to about 1 s, and the estimate is stored.
6. Surprise score = (new level − cached prior level − payroll forecast) − 100 × (unemployment rate − its forecast), in thousands.

**Execution assumption and measurement (`live/evaluate.py`, after the archive has the day).**
- **Direction.** Textbook, nothing fitted: a positive score means SELL XAUUSDm, EURUSDm and GBPUSDm, and BUY USDJPYm. A zero score means no trade.
- **Entry.** The first Exness quote at or after (first_seen corrected by the offset) + **0.5 s** of assumed order latency: ask for a BUY, bid for a SELL.
- **Exit.** The first quote at or after T + 900 s: bid for a BUY, ask for a SELL. No stop.
- **Risk unit.** R = 2 × the mid-price range from T−3600 s to T.
- **Recorded per market:**
  - seconds until first_seen;
  - the bid and ask at entry and at exit;
  - the spread at T−1 s, T+1 s and T+5 s;
  - the mid move at +1 s, +5 s, +30 s and +15 min, in R;
  - the result (r_achieved) and the theoretical 1-second result (r_theoretical_1s).

**Statistics.** One release is an observation, not a test. It is reported descriptively and cannot PASS or FAIL on its own. It is the first of the NFP capture programme below.

**NFP capture programme decision** (NFP only, never pooled with CPI). It is decided at **N = 12 captured releases with status ok**. Releases that are missing or refused do not count.
- **PASS** requires all of:
  - median first_seen latency of 1.0 s or less;
  - mean r_achieved above 0 averaged over the four markets, and in at least 3 of the 4;
  - a one-sided sign-flip p of 0.05 or less (surprise signs shuffled across releases, 2,000 times), using the four-market average per release;
  - a positive mean after subtracting one extra spread at entry.
- **FAIL** if any of:
  - the median latency is above 3.0 s after 6 captures (the setup cannot reach the window);
  - the mean r_achieved is 0 or below at N = 12;
  - the cumulative four-market average reaches −6R or worse at any point.
- **INCONCLUSIVE** otherwise at N = 12. The programme then stops; it is not extended.
- Power is low: 12 releases can only confirm a large effect.

## B. Release capture: US CPI, 10 December 2026 (separate protocol, not pooled with A)

**Event.**
- BLS Consumer Price Index for November 2026.
- Release at **08:30:00 New York time = 13:30:00 UTC on 2026-12-10**, from the St. Louis Fed release calendar, checked before the run.

**Data.**
- *Actual figures.* BLS API v2, series `CUSR0000SA0L1E` (core CPI index, seasonally adjusted).
- *Consensus.* The last "Core CPI m/m" forecast logged before 13:30:00 UTC.
- *Surprise.* The month-on-month change from the cached prior index, rounded to 0.1 (as BLS publishes it), minus the forecast. Zero means no trade.

**Instruments, capture, execution, measurement and statistics.** Identical to A, except that the BLS series and the consensus title are CPI's.

**CPI capture programme decision.** The same rules as the NFP programme, applied **separately** to CPI releases: N = 12; the same PASS, FAIL and INCONCLUSIVE definitions; −6R limit.

## C. Gold ADP-contrarian hypothesis (exploratory, pre-registered)

**Origin.** In the frozen robustness audit, 3 of 192 variants of reversed-direction gold trades had raw p ≤ 0.05 (`reports/adp_robustness.json`). None survived the multiple-testing correction. This is **an exploratory discovery, not an edge**.

The lowest-p variant is locked **exactly**, with no further historical search:

> `XAUUSDm | candles 2020-26 | entry T-30m | exit T+60m | reversed direction`. Historical: N = 72, mean +0.448R, median +0.202R, 10% trimmed mean +0.292R, sign-flip p 0.013.

**Locked rules** (implemented in `live/adp_contrarian_forward.py`, hash above):

| Item | Rule |
|---|---|
| Eligible events | Every BLS jobs report from 2026-12-04 on that appears in the consensus log. The first one is 2026-12-04, with ADP for November 2026 released 2026-12-02. |
| Signal | Sign of (ADP actual change − ADP consensus) for the ADP report on the jobs report's reference month. |
| ADP actual | ALFRED series `ADPMNUSNERSA`: the latest vintage dated before the jobs-report day, whose last observation is the reference month. Change = last − previous observation, in thousands. Otherwise the observation is missing. |
| ADP consensus | The last "ADP Non-Farm Employment Change" forecast in `data/consensus_log.csv` first seen before the ADP release. Otherwise the observation is missing. |
| Direction | Reversed textbook: ADP above consensus → **BUY** gold. ADP below consensus → **SELL** gold. ADP equal to consensus → no trade, logged. |
| Entry | Open of the Exness XAUUSDm 15-minute candle starting at **T−30 min** (T = 08:30:00 New York time): ask for a BUY, bid for a SELL. |
| Exit | Open of the 15-minute candle starting at **T+60 min**: bid for a BUY, ask for a SELL. No stop. |
| Risk unit and sizing | R = 2 × (highest bid high − lowest bid low) of the three 15-minute candles before entry. Fixed paper size of 1R per trade. |
| Costs | Primary: quoted Exness bid/ask only, as in the audit. Stress: minus one extra entry-candle spread. |
| Data and timestamps | Exness tick archive aggregated to 15-minute candles by `oil_rsi_vwap/src/build_bars.py`, in UTC. T comes from the consensus-log event time. |
| Maximum drawdown | FAIL immediately if cumulative primary R reaches **−8R** or worse (about 4 times the historical per-trade standard deviation of about 1.9R). |
| Minimum sample | A decision only at **N = 36** trades (about 3 years). Futility check at N = 24. |
| PASS | N = 36, mean r_primary > 0, mean r_stress > 0, **and** one-sided sign-flip p ≤ 0.05 (signal signs shuffled across releases, 2,000 times). |
| FAIL | The drawdown limit is breached, **or** mean r_primary ≤ 0 at N = 24, **or** at N = 36 either mean is 0 or below. |
| INCONCLUSIVE | Neither PASS nor FAIL at N = 36. The test then stops, with no extension. |

**Power.** If the true effect equalled the historical +0.45R, with a standard deviation of about 1.9R, power at N = 36 would be only about 40%. If the historical figure is inflated by selection, which is likely, power is lower still. An INCONCLUSIVE outcome is the most likely result even if a modest effect exists. That is accepted, and the rules will not be loosened.

## D. Existing paper tests

**Shared rules.**
- **Configuration and ledgers.** The frozen configuration and code are as hashed above. Ledgers are append-only, and each test counts trades from 2026-11-12 00:00 UTC.
- **Costs.** All decisions use net R after costs: real Exness bid/ask plus each test's frozen slippage (0.02% of price), and stress cost at 0.05% plus 0.02% per day.
  - The audit found the frozen slippage conservative for forex, indices and gold. It stays as frozen, so these tests are, if anything, harder to pass.
- **Drawdown limits.** These were added by this plan before any trade existed. Each is 1.5 × the rule's worst historical drawdown up to 2026-11-11 (`audit/reports/paper_drawdowns.json`). Breaching one means FAIL.
- **New INCONCLUSIVE category.** This plan adds INCONCLUSIVE for a final result that is positive but does not meet the significance bar. The PASS criteria of the frozen protocols are unchanged.
- **Missing data.** Data the Exness archive permanently lacks is excluded. Legs touching such a gap are kept as the frozen engine produces them; the engine exits at the next available quote. A run that fails is re-run.

| Test | Frozen configuration | Minimum N | Evidence to continue | PASS | FAIL | INCONCLUSIVE | Drawdown limit | Approx. power if the historical mean holds |
|---|---|---|---|---|---|---|---|---|
| BTC Pivot Reversal BUY (`pivot_reversal_paper`) | TradingView Pivot Reversal (4/2), 1H, BUY legs, own exits | 400 legs (about 1.8 years) | Mean R > 0 at 200 legs (frozen futility rule) | At 400: mean > 0 at primary and stress cost and p ≤ 0.05 against the frozen benchmark (`fast_bench.held`). The calibrated `seq_held` p is reported beside it but does not decide. | Futility at 200, or stress mean ≤ 0 at 400, or drawdown breach | At 400: both means > 0 but p > 0.05 | **−49R** (historical worst 32.6R) | ~40% |
| ETH Pivot Reversal BUY (`eth_pivot_paper`) | As BTC, on ETHUSDm | 400 legs | Mean R > 0 at 200 legs | At 400: both means > 0 and p ≤ 0.05 against `seq_held` (frozen) | As BTC | As BTC | **−37R** (historical worst 24.7R) | ~30% |
| Gold KST + VWAP, 48 h time stop (`gold_kst_paper`, primary track) | KST(10,15,20,30/10,10,10,15; signal 9) crossing up with close above session VWAP, 1H; exit at the bearish cross or after 48 h | 200 legs (about 1.6 years) | Mean R > 0 at 100 legs | At 200: both means > 0 and p ≤ 0.05 against the frozen gold-engine benchmark | Futility at 100, or a mean ≤ 0 at 200, or drawdown breach | At 200: both means > 0 but p > 0.05 | **−37R** (historical worst 24.4R) | ~45% |
| Gold KST shadow tracks (original exit, DOLLAR_FALLING, VOL_LOW) | Frozen in the same config | — | — | **No decision**: comparison only | — | — | — | — |
| Gold KST + VWAP with 2×ATR stop and close before news (`gold_kst_risk_paper`) | As the gold primary signal, plus a 2×ATR stop, no entry from 2 h before to 1 h after FOMC/CPI/NFP, and closing 30 min before them | 200 legs | Mean R > 0 at 100 legs | As the gold primary track | As the gold primary track | As the gold primary track | **−58R** (historical worst 38.7R) | ~30% |

The power figures use each rule's historical mean and per-trade standard deviation (`audit/reports/paper_drawdowns.json`). The historical means come from studies with heavy selection, so true power is probably lower.

## Part 4. What the three outcomes mean

- **PASS:** enough prospective evidence under these pre-registered criteria. Even then, a PASS only justifies a separately reviewed, small live trial, not full live trading.
- **FAIL:** the criteria were not met at the decision point, or a defined risk limit was breached. A failed test is not re-run with new parameters under the same name.
- **INCONCLUSIVE:** too few observations, or too little power, to decide. It is not a weak PASS and is not reported as one.

An exploratory pattern, such as section C, is never called a proven trading edge, whatever its interim results.
