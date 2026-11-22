# Batch 2 research-protocol review (2026-11-12). REVIEW ONLY: nothing has been run.

**Scope.**
- **The programme under review** is the *New Discovery* programme on branch **`claude/dazzling-albattani-j6uys7`**: `research/new_discovery/` (`INSTRUMENTS.md`, `PROTOCOL.md`, `REGISTRY.md`, `batch_001/`).
- **It was read read-only.** Nothing on that branch, and no frozen experiment or result on this branch, was changed.
- **This review was written on `claude/download-skill-27d08k`**, the only branch this session may push to. Where Batch 2 will live is a decision for the user (see §9).
- **Checks run for this review:**
  - archive HEAD requests for the 11 symbols, 2025-01 to 2026-11;
  - one month (Oct 2026) of ticks for the 6 symbols without measured spreads, deleted after measurement;
  - reachability and coverage of each proposed Batch 2 source;
  - licence searches.
- **No experiment, signal or strategy was computed.**

## 1. The 11 existing markets (from `new_discovery/INSTRUMENTS.md`, verified here where stated)

**Provider for all 11:** the **Exness public tick archive** (`ticks.ex2archive.com`), Standard-account **CFD** bid/ask quotes. None of these are exchange prints.

| # | Exness symbol | Underlying (per INSTRUMENTS.md) | 2025-01..2026-11 months in archive (verified) | Median spread, own measurement | Known data problems |
|---|---|---|---|---|---|
| 1 | XAUUSDm | Spot gold CFD (USD/oz) | 23/23 | 0.16 USD ≈ 0.4 bp (2025-01..2026-10) | Holidays only (this branch's audit) |
| 2 | USOILm | CFD referenced to **NYMEX WTI** futures, broker-rolled | 23/23 | 0.018 USD ≈ 2 bp | **Archive hole 2026-03-30..31.** Roll jumps. Tracks CL=F at −0.54% median, daily corr 0.985 (`../data_audit/results/oil_reconciliation.json`). |
| 3 | UKOILm | CFD referenced to **ICE Brent** futures, broker-rolled. **Not interchangeable with USOILm.** | 23/23 | 0.013 USD = 1.27 bp (p95 3.86 bp), Oct 2026 only | Hole not yet checked. 34 Brent/WTI spread "jump hours" from mismatched rolls (batch_001). |
| 4 | BTCUSDm | Bitcoin CFD, 24/7 | 23/23 | 6.4 USD = **0.79 bp** (p95 1.18), Oct 2026 | Hole not checked. Broker quote, not an exchange book. |
| 5 | ETHUSDm | Ether CFD, 24/7 | 23/23 | 1.0 USD = **4.13 bp** (p95 4.47), Oct 2026 | Hole not checked. Spread is about 5× BTC's in bp. |
| 6 | EURUSDm | Spot FX CFD | 23/23 | 0.71 bp, Oct 2026 | Hole not checked |
| 7 | GBPUSDm | Spot FX CFD | 23/23 | 0.75 bp, Oct 2026 | Hole not checked |
| 8 | USDJPYm | Spot FX CFD | 23/23 | 0.63 bp, Oct 2026 | Hole not checked |
| 9 | US500m | S&P 500 index CFD (not the ES future) | 23/23 | 0.59 pt ≈ 0.8 bp | **Archive hole 2026-03-30..31** |
| 10 | USTECm | Nasdaq-100 index CFD (not NQ) | 23/23 | 1.92 pt ≈ 0.8 bp | **Hole 2026-03-30..31; Oct 2026 file ends on the 28th** |
| 11 | DE30m | DAX 40 index CFD (legacy name) | 23/23 | 1.6 pt ≈ 0.7 bp | **Archive hole 2026-03-30..31** |

**Missing fields for all 11:**
- **No volume.** The "ticks" field is a quote count.
- **No order book, no trade prints and no aggressor side.**
- **No overnight swap or financing history.** The Exness swap tables are not archived, and many UAE accounts are swap-free, which affects carry; see §4.
- **No official contract specifications or roll dates.** The Exness spec page blocks automated access.

**Pre-2025 coverage:** INSTRUMENTS.md lists XAU from 2020-01, USOIL from 2019-02, BTC from 2020-01, and the other symbols from 2023-01. This was **not re-verified here**, because pre-2025 data is excluded by the user's standing rule (§2.3).

**Licensing:**
- Exness describes its tick history as **"indicative and for informational purposes only."** No redistribution licence was found for `ticks.ex2archive.com`, which is a third-party mirror and not an Exness publication.
- **Treat it as personal research use only, with no redistribution.**

**Costs:** Standard account, spread only, no commission. **Swap is unknown**, and for crypto CFDs it can be large. Any multi-day hold therefore needs swap stress, and the current 0.02%/day proxy has not been validated.

## 2. Audit of the previously inspected period

### 2.1 What has already seen 2025-07 → present (and 2025-01 → present)

| Programme | Markets | Period inspected | How it was used |
|---|---|---|---|
| New Discovery batch_001 (other branch) | all 11 | **TEST 2025-07-01 → 2026-11** | 26 TEST p-values were computed and published. **`batch_001/SUMMARY.md` used those TEST outcomes to choose the Batch 2 families** ("price-only rules have now failed … the best remaining chance is new kinds of information"). |
| Other branch: multi_market, long_history, signal_comparison, gold KST, news studies | 33 Exness markets including all 11 | "Confirmation" 2025-01 → present | thousands of variants per market (README: about 100,000 market-variant tests) |
| This branch: theory library and earlier studies | XAU, USOIL, DE30, US500, USTEC, BTC, ETH (UKOIL and others in the MOM50 breadth study) | **2025-01 → 2026-10/11** | 535-combination screen, ORB (96), Theory #2 (60), session/exposure/breadth studies, oil-bot sweeps (8,400 + 360 + 48 settings), Donchian research, and others. Candidates were selected from this period. |

### 2.2 Verdict

- **2025-07 → present is not an independent holdout for Batch 2.** Its results were inspected, and those results shaped which hypotheses were chosen next. It must be labelled **"development / reused evaluation data"** from now on.
- **The same holds for 2025-01 → present** on every one of the 11 markets.
- **Seeing the target series counts as contamination.** Batch 2's *signal* data (funding, basis, aggressor flow, DVOL) has not been examined. But the *target* series (BTC/ETH CFD returns) has been examined heavily. Knowing the regime (for example the 2025–26 crypto decline) can bias hypothesis design, such as the choice of sign or holding period.
- **So no Batch 2 result computed on 2025-01 → present can be called out-of-sample or confirmatory.**

### 2.3 Conflict with the standing data rule

- **This conversation's standing user rule** is *"never use market data before 2025-01-01"*.
- **New Discovery's protocol uses data the rule excludes:** TRAIN 2023-01 → 2024-06 and VALIDATION 2024-07 → 2025-06.
- **Combined consequence:** if both are honoured, **no untouched historical data exists at all** for these 11 markets. Under that rule, the only independent evidence possible is **prospective, forward data**.
- **Decision needed from the user (§9).**

## 3. Additional markets: candidates only, not added

| Candidate | Why it might matter | Evidence of suitability | Status |
|---|---|---|---|
| **Binance USD-M perpetuals BTCUSDT and ETHUSDT** | The instrument that actually pays and receives funding. Needed for any funding or carry mechanism. | `data.binance.vision` monthly `fundingRate`, `premiumIndexKlines`, klines and aggTrades files exist for 2025-01 and 2026-10 (HTTP 206). The REST API `fapi.binance.com` returns **HTTP 451** from here. | Data looks available. **Executability for the user (jurisdiction, account type) is unverified.** Licence: Binance Vision terms, non-commercial, no hosting or redistribution. |
| **Binance COIN-M quarterly futures** (e.g. BTCUSD_YYMMDD) | Needed for a clean basis series | COIN-M klines exist (BTCUSD_PERP 1h checked) | Contract roll handling is needed. Same licence. |
| **Hyperliquid perps** (BTC, ETH; xyz:GOLD, xyz:CL, xyz:BRENTOIL) | Funding history and trade prints on non-crypto underlyings | The API serves funding, trades and candles. **The candle endpoint returns at most 5,000 bars** (xyz:CL 1h only from 2026-04-18 here). The xyz markets launched late 2025 / 2026. | Too short for development. Possible forward-only use. The licence was not found. |
| **Deribit BTC/ETH options** | The traded instrument behind DVOL | DVOL is public. Options history needs a paid vendor (for example Tardis or Amberdata). | Not executable for the user, so **signal only**. |

**None of these is added to experiments or portfolios without the user's approval.**

## 4. Data-quality and licensing assessment of the four proposed Batch 2 sources

| Source | Coverage verified here | Timestamp and completeness issues | Relevance to the traded instrument | Licence | Verdict |
|---|---|---|---|---|---|
| **1. Crypto funding and basis** (Binance Vision `fundingRate`, `premiumIndexKlines`, UM/CM klines) | Files for 2025-01 and 2026-10 present for BTCUSDT and ETHUSDT | Funding settles at 00/08/16 UTC. A rate may only be used **after** its settlement time; the "predicted" rate changes during the interval. The basis needs quarterly-contract rolls; record each roll date. Check for missing months. | **Mismatch.** Funding is paid on perpetuals, **not** on Exness BTC/ETH CFDs, which charge a broker swap instead. So: (a) *funding as a signal* traded on the CFD is testable; (b) *carry harvesting* is only testable on Binance perps, with real funding P&L, and is executable only if the user can trade them. | [Binance Vision Terms](https://data.binance.vision/Binance_Vision-Terms_of_Use.pdf): no licensing, hosting or commercial use. **Do not commit raw files.** | **Feasible as a signal (a).** (b) needs the user to confirm access. |
| **2. BTC/ETH order flow** (Binance Vision spot and UM `aggTrades`, with the `is_buyer_maker` aggressor flag) | 2025-01 spot BTCUSDT file present, **756 MB per month** | Binance reportedly moved spot archive timestamps to **microseconds from 2025-01-01**, which must be checked in-file. The ID sequence needs gap checks. The data covers **one venue only**. Clock alignment with the Exness feed is needed. | Signal from Binance, execution on the Exness CFD: a cross-venue lead–lag with unknown Exness latency. A one-minute decision delay and a next-quote fill are required. | Same Binance terms | **Feasible but heavy.** Stream-aggregate to 1-minute signed volume and discard the raw files (the disk allowance is limited). |
| **3. BTC options VRP** (Deribit `get_volatility_index_data`, DVOL) | BTC and ETH hourly from 2025-01 verified (BTC ≈ 60 on 2025-01-01) | Candles are labelled by their start, so use the close only after the bar ends. DVOL is a 30-day model index of option quotes and **not tradable**. Check its methodology for changes. Realised volatility from the Exness or Binance feed must match the horizon. | Signal only; the user cannot trade Deribit options through Exness | [Deribit terms](https://support.deribit.com/hc/en-us/articles/25944532191645-Deribit-Exchange-Membership-Terms-Deribit-FZE): market and derived data "**for personal use only**". **Do not redistribute or commit.** | **Feasible as a signal**, stored locally only |
| **4. FX carry** (FRED: DFF, SONIA IUDSOIA, ECB DFR, Japan IRSTCI01JPM156N) | Reachable. DFF to 2026-11-09, ECB DFR to 2026-11-12, **Japan series monthly only, last value 2026-09** | **Publication lag:** OECD monthly rates are published weeks after the observation date. Aligning them by observation date is look-ahead. Use policy decision dates and times, or the release date. | **A rate differential is not realised carry.** The realised carry of an Exness CFD is the **broker swap** (long and short swap points, triple on Wednesday, with a broker mark-up). That is not archived. **Many Exness accounts in the UAE are swap-free**, which means **zero carry**. Forward points have no free source. | FRED: series-specific; Fed and Treasury series are public domain, while the OECD series carries an attribution requirement | **Not testable as realised carry** with the available data. Only a *spot-return-only* "differential as directional signal" variant is possible, and it is a different hypothesis. **Recommend deferring** until the account's actual swap table (or swap-free status) is known. |

**Licence summary:**
- **Nothing from these Batch 2 sources may be committed to the repository.** Keep it in scratch storage with SHA-256 manifests only.
- **This repository's visibility could not be confirmed**: the GitHub search API returned no result for it.
- **It already contains third-party data:** Exness-derived bars and daily candles, Binance klines, Hyperliquid candles, and **two Yahoo Finance JSON files** in `../data_audit/data/`. Yahoo's terms generally prohibit redistribution.
- **These are hashed in the frozen manifest, so they were not removed.** The user must decide whether to keep them, which is acceptable only if the repository is private, or to relocate them and keep only their hashes (§9).

## 5. Proposed hypotheses (for approval; one pre-set setting each, no variants)

| ID | Hypothesis and mechanism | Evidence | Eligible markets | Inapplicable markets, and why |
|---|---|---|---|---|
| **H1** | **Funding extremes reverse.** Very high (or low) perp funding means crowded leveraged longs (or shorts), whose forced unwinds push the price the other way over the next 1–3 days. | crypto carry and leverage literature, for example [Schmeling, Schrimpf & Todorov (BIS 2023)](https://www.bis.org/publ/work1087.htm) | BTCUSDm, ETHUSDm (signal from Binance perps) | Gold, oils, FX, indices: no perpetual funding exists for these in the data |
| **H2** | **High basis predicts weak returns / crash risk.** A high annualised futures basis means heavy demand for leveraged longs, and the crypto-carry literature links it to later crashes. | Schmeling et al. (2023) | BTCUSDm, ETHUSDm | Same reason as H1 |
| **H3** | **Signed taker imbalance predicts short-horizon returns.** Persistent aggressive buying or selling over 1 hour carries information over the next 1–4 hours. | [Cont, Kukanov & Stoikov (2014)](https://doi.org/10.1093/jjfinec/nbt003) | BTCUSDm, ETHUSDm (flow from Binance) | Every non-crypto market: no aggressor-side trade data |
| **H4** | **The volatility risk premium predicts returns.** A high DVOL − realised-vol gap means investors are paying for crash insurance, and the premium is earned over the next 1–4 weeks. | Bollerslev, Tauchen & Zhou (2009) for equities; the crypto evidence is limited | BTCUSDm (BTC DVOL), ETHUSDm (ETH DVOL) | Every non-crypto market: no options-implied-volatility source |
| (H5) | **FX carry**: hold the higher-yield currency | Lustig & Verdelhan (2007), and others | EURUSDm, GBPUSDm, USDJPYm | All non-FX markets. **Deferred**, because realised carry (swap) cannot be measured (§4). |

**Primary tests:** 4 hypotheses × 2 markets = **8** (11 if H5 is approved later). Signals are always lagged to the information's real availability time. Execution is at the next executable Exness quote (ask for buys, bid for sells), with a 1-minute decision delay.

## 6. Pre-registration plan and multiple-testing correction

**What each experiment's `PREREG.md` commits, before any data for that signal is downloaded:**
- hypothesis, mechanism and evidence;
- eligible and ineligible markets, with reasons;
- **exact data sources, with file paths, SHA-256 hashes and licence notes**;
- signal formula and every parameter (one setting);
- the information-availability lag;
- entry, exit and position sizing;
- next-quote execution rules;
- **primary metric:** mean net return per trade in bp at primary cost, plus R where a stop exists;
- primary costs (real bid/ask + 0.5 × median spread) and stress costs (1.5 × median spread + swap proxy);
- benchmarks:
  - (i) random entry with the same sides and holding times;
  - (ii) a **time-shuffled signal placebo**, with the signal series block-permuted;
  - (iii) buy and hold;
- evaluation periods: development (labelled as previously inspected) and forward;
- the statistical correction;
- rejection criteria.

**The correction is split into three layers:**
- **Confirmatory layer, forward data only:** Holm–Bonferroni family-wise control at α = 0.05 over the **8** primary forward tests. The forward data has never been seen, so the program's earlier tests do not inflate the error rate on it, **provided the 8 hypotheses are fixed before the forward data exists.**
- **Exploratory layer, 2025+ development data:** results are reported with Benjamini–Hochberg over **the whole programme's cumulative count**, not per batch.
  - That count is about **100,000** market-variant tests on the other branch (its README), plus about **10,000** on this branch (8,400 oil-bot settings, 535 library combinations, 156 ORB/Theory #2, 54 neighbouring settings, and other studies).
  - In practice, **no development result can be significant.** Development results may only reject or flag, never confirm.
- **Registry:** every Batch 2 test is appended to a **programme-wide registry** that unifies both branches. This keeps the cumulative count of hypotheses and variants, and the history is never reset.

## 7. A genuinely independent validation plan

1. **Pre-register and lock.** Commit and push the 8 hypotheses with their full rules, hashes and analysis code. The commit time is T0.
2. **Embargo.** The forward period starts at the first 00:00 UTC that is at least 24 hours after T0. No data after T0 is downloaded or looked at before then.
3. **Paper forward test.** All 8 tests run in parallel with frozen code, guarded by a SHA-256 freeze check every hour, and paper only.
4. **Fixed evaluation horizon, with no peeking:**
   - **A power analysis comes first.** It uses development-period dispersion to estimate the trades needed to detect +5 bp per trade, or the economic minimum, at 80% power.
   - Hourly-signal tests (H3) may need **3–6 months**.
   - Daily or weekly signals (H1, H2, H4) may need **12–24 months**, because extreme-funding or VRP events are rare.
   - If that horizon is unacceptable, an **alpha-spending** plan (O'Brien–Fleming) is pre-registered instead of informal looks.
   - Running totals are reported for monitoring only, and no decision is taken before the horizon.
5. **Pass rule (forward data only):**
   - mean net > 0 at primary and stress cost;
   - beats the random-entry and placebo benchmarks;
   - survives Holm across the 8 tests;
   - at least the pre-registered minimum number of trades.
6. **An alternative "locked dataset" would breach the 2025 rule.** It would mean pre-2025 funding, basis and DVOL history, never examined for these signals, evaluated exactly once. That requires the user to lift the rule (§2.3) and to have someone independent hold the data. Without that, forward data is the only independent validation.

## 8. Weaknesses that could invalidate Batch 2 (self-critique)

1. **The target series was seen.** Even with new signal data, the hypothesis direction could be biased by knowing the 2025–26 crypto path. Only forward data removes this.
2. **Low power.** Rare-event signals (H1, H2, H4) may give too few forward trades for any decision within a year. A "fail" may just be inconclusive. That must be reported as such, never as a pass.
3. **Cross-venue mismatch.** The signals come from Binance and Deribit, while execution is on Exness CFDs. The basis, latency and broker quoting could erase short-horizon edges (especially H3). The Exness CFD's own price formation is unknown.
4. **Swap is unknown on Exness crypto CFDs.** It is not in the data and may be large or zero (swap-free), which dominates multi-day holds (H1, H2, H4).
5. **Timestamp traps:**
   - Binance's microsecond change;
   - funding known only at settlement;
   - DVOL bars labelled by their start;
   - FRED publication lags.
6. **Data revisions or removal.** The archives can change or disappear, and they are not ours to store. Results are reproducible only while the sources keep serving the same files (hash every file used).
7. **Researcher degrees of freedom.** Choosing 4 families out of many, and their thresholds, after a long search programme. Mitigation: one setting each, committed before download, and placebo benchmarks.
8. **Garden of forking paths across conversations.** Many earlier studies on both branches were prompted by earlier results. The programme-wide registry must count all of them, or the multiple-testing claims are wrong.
9. **Regime dependence.** The forward period is a single regime too. A pass shows survival in one more regime, not permanence.
10. **Licensing.** Using personal-use-only data (Deribit) or non-commercial data (Binance) for anything beyond personal research would breach the terms.

## 9. Decisions needed from the user before Batch 2 can be pre-registered

1. **The data rule:** does "never use data before 2025-01-01" still hold? It conflicts with New Discovery's 2023–2024 TRAIN/VALIDATION periods. If it holds, all historical work is development-only, and validation is forward-only.
2. **The branch:** where should Batch 2 live? It was designed on `claude/dazzling-albattani-j6uys7`, but this session can only push to `claude/download-skill-27d08k`.
3. **The hypotheses:** approve, change or drop H1–H4. For FX carry (H5), does the Exness account pay or charge swaps, or is it swap-free? Can the actual swap table be provided?
4. **Executability:** can the user actually trade Binance USD-M perpetuals? If not, H1 and H2 are signal-only, traded on Exness CFDs.
5. **Repository data:** is the repository private? Should the already-committed third-party price files, including the two Yahoo JSON files, stay, or be moved out with only their hashes kept?
6. **The forward horizon:** is it acceptable to wait **12–24 months** for a decision on the rare-event hypotheses?

**Nothing in Batch 2 will be downloaded, computed or run until these are answered and the user gives explicit approval.**
