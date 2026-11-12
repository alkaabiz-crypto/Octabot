# Theory library: final reconciliation and FREEZE (2026-11-12)

**The library is frozen as of this commit.**
- **No further retrospective searches**, new theory batches, parameter changes or optimisation of any tested strategy.
- **Historical outputs are kept unchanged**, and their SHA-256 hashes are in `FREEZE_MANIFEST.sha256`. `verify_freeze.py` checks them.
- **The forward paper tests continue with unchanged configurations.**
- **No strategy is called proven** from these historical returns. The only open question is whether the three candidates survive independent forward validation.

## 1. Oil data reconciliation (`../data_audit/oil_reconciliation.py`, `../data_audit/results/oil_reconciliation.json`)

**Instruments**

| Feed | Identity | Underlying |
|---|---|---|
| Exness **USOILm** | CFD, "US Crude Oil" | **WTI**, quoted from NYMEX CL futures. This is inferred from the data below. Exness's specification page blocks automated access, so the official spec could not be fetched, and this is labelled as an inference. |
| Hyperliquid **xyz:CL** | HIP-3 perpetual on the `xyz` (trade.xyz) dex. The API reports szDecimals 3, max leverage 20 and funding multiplier 0.5, with an oracle-priced mark. | **WTI**. Third-party roll calendars describe the oracle as blending the CME front and next contracts over business days 5–10 of each month ([loris.tools](https://loris.tools/rwa/roll-calendar), [hypercall.xyz](https://insights.hypercall.xyz/oil-perps-settlement-2026-04-11)). The official docs.trade.xyz spec was not retrieved, so this is unverified. A separate **xyz:BRENTOIL** market exists for Brent. |

**Benchmarks**
- **NYMEX WTI front month CL=F** and **ICE Brent front month BZ=F**, from Yahoo Finance daily data. The raw files are saved in `../data_audit/data/`.
- **FRED WTI spot** (DCOILWTICO) and **FRED Brent spot** (DCOILBRENTEU).
- EIA's front-month futures series cannot be used: **EIA stopped publishing NYMEX futures prices in April 2024**. Its RCLC1 file was updated on 2026-11-04, but its data ends on 2024-04-05.

**Level differences and return correlations, reported separately** (Exness at 14:30 New York, the NYMEX settlement time; Hyperliquid at 15:00 New York)

| Pair | Days | Median level diff | 5% / 95% | Max abs | Daily-return corr | Tracking error |
|---|---|---|---|---|---|---|
| **Exness USOILm vs WTI front month CL=F** | 456 | **−0.54%** | −3.41% / −0.07% | 8.0% | **0.985** | 0.55% |
| Exness USOILm vs Brent front month BZ=F | 456 | −6.14% | −11.9% / −4.1% | 13.8% | 0.961 | 0.79% |
| Exness USOILm vs FRED WTI **spot** | 453 | −1.81% | −7.23% / +0.08% | 10.6% | 0.933 | 1.12% |
| **Hyperliquid xyz:CL vs CL=F** | 144 | **−0.29%** | −4.21% / +0.45% | 5.3% | **0.953** | 0.99% |
| Hyperliquid xyz:BRENTOIL vs BZ=F | 144 | −1.75% | −6.06% / +0.37% | 7.1% | 0.949 | 1.08% |
| CL=F front month vs FRED WTI spot | 459 | −1.27% | −4.22% / +0.21% | 8.4% | 0.949 | 0.98% |
| CL=F (WTI) vs BZ=F (Brent) | 470 | −5.65% | −11.0% / −2.6% | 14.3% | 0.922 | 1.17% |
| Exness USOILm vs Hyperliquid xyz:CL, **hourly** (Apr–Oct 2026) | 3,068 hours | −0.56% | p95 abs 2.26% | 3.3% | **0.996 (hourly)** | — |

**Explanation of the 7–10% discrepancy reported earlier:**
- **Both feeds are WTI, not Brent.** They sit 4–12% below Brent every day, which is the 2026 WTI–Brent spread.
- **The earlier comparison used the wrong benchmark, FRED WTI spot**, which is the physical Cushing price. In 2026, front-month futures and spot diverged by up to 8.4%. Against the correct benchmark, the NYMEX front month, Exness differs by a median of −0.54% and its daily returns correlate at 0.985.
- **Exness's remaining gap** (5th percentile −3.4%, largest in days 11–19 of the month) fits a CFD that rolls to the next contract before the CL front month expires (around the 20th), while the market was backwardated. This is inferred from the data, not from the official spec.
- **Hyperliquid's residual gap** is the blended oracle roll plus 30 minutes of timing difference.
- **Conclusion:** there is no data error. The oil backtests and the oil forward feed track WTI futures.

## 2. Combination accounting (`results/inventory.csv`)

**Correction:** earlier messages said "64 theories". **63 theory IDs were executed.**

| Batch | IDs pre-registered | IDs run | Not run (pre-registered as not run) | Combinations |
|---|---|---|---|---|
| A–E | 40 | 39 | E5, best weekday (information only) | **290** |
| F | 13 | 12 | F13, golden pocket (duplicate of B9) | **126** |
| G | 14 | 12 | G11 pre-FOMC drift, G12 gold/silver ratio (information only, too few events) | **119** |
| **Total** | **67** | **63** | 4 | **535** |

- **A combination is one theory × one market × one timeframe**, using textbook default parameters. **There are no parameter variants in the 535.**
- **How the registry adds up:** registry entries expand to 537 combinations. Two are absent from the results (B1 RSI 15m on BTC and ETH), because there is no crypto data below 1h. Session and calendar theories run only on the markets they apply to. D1 and D2 have separate Exness (1m/15m) and crypto (1h) entries, but count as one ID each.
- **By market:** DE30, US500 and USTEC 79 each; gold and oil 76 each; BTC and ETH 73 each.
- **By timeframe:** 1h 297, 4h 126, 1d 63, 15m 25, 1m 19, 5m 5.
- **Batch G's 119:**
  - G3–G9: 7 theories × 7 markets × 2 timeframes = **98**;
  - G2 Dual Thrust (7 markets × 1h) = **7**;
  - G1 intraday momentum (5 Exness markets × 1m) = **5**;
  - G10 z-score (5 Exness × 15m) = **5**;
  - G13 and G14 (BTC, ETH × 1h) = **2 + 2**.

**Configurations outside the 535**
- **Verification only:** 6 candidates × 9 neighbouring settings = **54** (`verify_neighbours.py`), plus **3** minute-level re-implementations (`verify_minute.py`).
- **Separate pre-registered studies:**
  - ORB: 40 + 56 = 96 combinations, plus 2 tick-level re-tests (`../orb_study`);
  - Theory #2: 60 combinations, **0 PASS** (`../zone_reversal_study`);
  - session, exposure-control, trend-breadth, MOM50-breadth and DCA-mix studies.

## 3. Missing-data sensitivity (`sensitivity_hole.py`, `results/sensitivity_*.json`)

**The hole:** the Exness archive has no ticks from **2026-03-29 23:59 to 2026-04-01 00:00 UTC** for USOILm, DE30m, US500m and USTECm. The markets were open on those days.

**What the corrected rule does:**
- It drops any trade held across the hole, because stops and targets cannot be checked inside it.
- The prices on both sides are real, so the move across the hole was real market movement.

**The two versions:**
- `results/sensitivity_original_no_hole_rule.json` is the ORIGINAL, run with the hole rule switched off. It is preserved.
- `results/sensitivity_corrected.json` is CORRECTED.

**Findings:**
- **Affected:** **189 of 535 combinations**, every one losing exactly **1 holdout trade**, so **189 trades removed** in total. By market: DE30 49, USTEC 48, USOIL 46, US500 46.
  - *Correction:* the earlier figure of "131" counted batches A–F only, out of 416.
- **Verdicts:** **none changed.** The same 6 PASS before and after: B9 ETH, B9 USOIL, B9 BTC, D4 XAU, B7 XAU and B7 USTEC.
- **None of the three candidates is affected.** Gold has no hole, and no oil Fibonacci trade spanned it.
- **Largest changes**, all among low-trade, slow combinations, which shows how fragile those are:

| Combination | Mean bp (original → corrected) | 2026 rank (original → corrected) |
|---|---|---|
| A7 USOIL 1d | +661 → **−374** | 1 → 534 |
| A2 USOIL 4h | +413 → −404 | 6 → 535 |
| A11 USOIL 1d | +122 → −95 | 16 → 524 |
| A8 USOIL 4h | +76 → −92 | 29 → 523 |

- **Other metrics:** per-combination changes in total return, max drawdown, t-statistic and random-control percentile are in `results/sensitivity_summary.json`.
- **Average R:** not reported for the 535 combinations, because R is undefined for position strategies without a stop. bp of price is used instead. R is reported for the candidates below.

## 4 and 5. Candidate statistics (`candidate_stats.py`, `results/candidate_stats.json`)

**Source:** the strict minute-by-minute re-test (V1).
- **Limit fills** need one full spread of penetration, or 1 bp for ETH.
- **Costs** are at **2×**: ETH 0.05% of price per side, doubled; gold the Exness spread per minute, doubled.
- **"Simple sum"** adds the per-trade returns. **"Compounded"** puts the whole account in every trade, with no leverage.

**The +105% / +56% figures:**
- ETH made **+32.28 bp × 326 trades = +105.25%** and **+19.62 bp × 288 trades = +56.52%**.
- These are **simple sums of per-trade returns** (1 bp = 0.01%), not compounded growth.
- Compounded, they are **+165.0% / +69.4%**.

**Random benchmark:**
- The screen's control: **500 draws**, each with the same number of trades, the same sides (long/short) and the same holding durations in candles.
- Each draw places those trades at random start candles within the same period, open-to-open, with the same 2× costs (seed 20261112 + CRC32 of the key).
- The minute-level mean is ranked against that distribution. This is approximate, because the control is built from screen-level trades.
- For ETH, a random draw's median is about −20 bp, which is the round-trip cost at 2× (0.20%).

**Data cutoffs**
- **ETH:** the screen's 1h data ends **2026-11-09 23:00 UTC**. The 1-minute data runs **2025-01-01 00:00 → 2026-11-10 11:19 UTC**, because the download script had a hard-coded end date.
  - Truncating the minute-level 2026 period at the screen cutoff gives **287 trades, +19.09 bp, +54.8% simple / +66.5% compounded**.
- **Gold and oil (Exness):** data ends **2026-10-30 ~20:57 UTC**.
- **Periods:** 2025 = 2025-01-01..2025-12-31; 2026 = 2026-01-01..cutoff.

| 2× costs | **ETH Fibonacci 2025** | **ETH 2026** | **Gold FVG 2025** | **Gold FVG 2026** | Oil Fibonacci 2025 | Oil 2026 |
|---|---|---|---|---|---|---|
| Trades | 326 | 288 | 388 | 311 | 211 | 178 |
| Mean bp per trade | **+32.28** | **+19.62** | **+4.78** | **+10.97** | +12.87 | +17.30 |
| Median bp | +13.67 | +19.71 | −15.23 | −21.42 | +9.07 | −50.87 |
| 95% CI of the mean (bp) | +8.6 … +56.0 | **+0.8 … +38.5** | **−0.2 … +9.8** | +2.1 … +19.9 | −2.7 … +28.4 | −15.7 … +50.3 |
| t-statistic | 2.68 | 2.05 | 1.88 | 2.42 | 1.63 | 1.04 |
| Win rate | 51.5% | 52.4% | 39.9% | 42.1% | 51.7% | 46.1% |
| Average R (net) | +0.136 | +0.033 | +0.112 | +0.182 | +0.205 | +0.018 |
| Median risk (stop distance) | 170 bp | 114 bp | 25 bp | 38 bp | 83 bp | 144 bp |
| Profit factor | 1.42 | 1.34 | 1.27 | 1.44 | 1.29 | 1.22 |
| Simple sum | +105.3% | +56.5% | +18.6% | +34.1% | +27.2% | +30.8% |
| Compounded | +165.0% | +69.4% | +19.8% | +39.3% | +29.4% | +30.1% |
| Max drawdown (compounded) | **−23.7%** | **−20.4%** | −4.0% | −5.4% | −10.3% | −17.4% |
| Longest losing streak | 8 | 5 | 7 | 8 | 5 | 6 |
| Average hold | 10.8 h | 10.0 h | 7.7 h | 7.5 h | 15.2 h | 14.7 h |
| Random control: median / p95 (bp) | −20.7 / +4.8 | −19.4 / −0.9 | −0.1 / +3.9 | −1.1 / +7.1 | −5.4 / +8.6 | −2.9 / +22.8 |
| Minute-level mean percentile vs random | 100 | 100 | **98.0** | **98.8** | 98.6 | **89.0** |
| At 1× cost (mean bp / sum / compounded) | +42.3 / +137.8% / +266.7% | +29.6 / +85.3% / +125.8% | +5.3 / +20.4% / +22.0% | +11.6 / +36.0% / +42.0% | +15.8 / +33.4% / +37.7% | +20.1 / +35.8% / +36.8% |

**Gold FVG against ETH:**
- **Both beat the randomised control in both periods.** Gold sits at the 98.0th and 98.8th percentiles; ETH sits above every draw.
- **Gold's edge is small per trade** (+5 to +11 bp), with a 40% win rate on 2R targets and small drawdowns (−4 to −5%). Its **2025 confidence interval includes zero** (t = 1.88).
- **ETH's edge is larger per trade** (+20 to +32 bp), but with much larger risk per trade (median stop 1.1–1.7%) and drawdowns of about −20 to −24%. Its 2026 interval barely excludes zero (t = 2.05).
- **Feeds:** ETH's forward feed (Binance spot) is the same as its backtest feed. Gold's forward feed (Hyperliquid xyz:GOLD) differs from its backtest feed (Exness): the median level differs by about 0.1–0.2% and daily returns correlate at 0.996. Gold's forward costs (a 0.22 USD spread) are modelled, not taken from the feed.
- **The same rule (B9) did not hold everywhere:** it **failed on BTC** (3 of 9 neighbouring settings positive), and on oil it does not beat the random control in 2026.

**Multiple testing:**
- **535 combinations were screened.** A Bonferroni-corrected two-sided 5% test would need |t| ≥ about 3.9. **No candidate reaches that in either period.**
- The candidates were therefore selected from a large search. **Their historical statistics cannot establish an edge.** That is exactly why they are in forward validation.

## 6. Forward paper-test registry (state as of 2026-11-12 ~18:00 UTC)

| # | Test | Configuration (frozen) | Data source | Started (UTC) | Completed observations | Changes after start |
|---|---|---|---|---|---|---|
| 1 | Donchian 20 BTC (+ execution shadow) | `btc_breakout/forward/FROZEN.json` config fingerprint, `paper_trader.py`, `EVALUATION_RULES.md` | Binance BTCUSDT 1h (labelled BINANCE PROXY) | 2026-11-09 07:00 | 0 / 40 trades; 1 signal (rejected: 4H close below EMA200); 3.4 days | none (each file has a single commit, before the start) |
| 2 | TREND_ENS trend bot | `daily_signal_dca/forward/forward.py` | Binance BTCUSDT and ETHUSDT 1d | first decision at the 2026-11-10 close | 2 daily closes × 2 coins × 2 accounts = 8 ledger rows | none |
| 3 | Gold MOM50 + ATR | `gold_mom50_forward/FORWARD_RULES.md` + `forward.py` | Hyperliquid xyz:GOLD 1d | first decision at the 2026-11-11 close | 1 decision (FLAT), 0 / 20 trades | none |
| 4 | Oil Stochastic 4H | `oil_stoch_forward/FORWARD_RULES.md` + `forward.py` | Hyperliquid xyz:CL 4h/1m | 2026-11-11 08:26 | 0 / 100 trades | none |
| 5 | Gold Asian session | `gold_asia_forward/FORWARD_RULES.md` + `forward.py` | Hyperliquid xyz:GOLD 1m | 2026-11-12 00:03 (first entry 2026-11-12 22:05) | 0 / 100 trades | none |
| 6 | **GOLD_FVG** (candidate) | `library_forward/FORWARD_RULES.md` + `forward.py` | Hyperliquid xyz:GOLD 1h/1m | 2026-11-12 16:44 | 0 / 100 trades | see the note below |
| 7 | **OIL_FIB** (candidate) | same | Hyperliquid xyz:CL 1h/1m | 2026-11-12 16:44 | 0 / 100 trades (1 pending limit order) | see the note below |
| 8 (new) | **ETH_FIB** (candidate) | same, plus its addendum | Binance ETHUSDT spot 1h/1m | 2026-11-12 17:25 | 0 / 100 trades | added before its first candle |
| — | SignalPro tracker | `signal_tracking/signalpro/tracker.py` | Hyperliquid xyz:GOLD / xyz:CL 1m | 2026-11-10 | 31 user-supplied signals scored | the tracker's rule commits were all made on 2026-11-10, while logging the first batches |

**Note on tests 6 and 7:**
- **Commit `8e679a8c`** (17:25) changed `library_forward/forward.py` to add ETH_FIB. For GOLD_FVG and OIL_FIB the new `pen()` and `rt()` return the same fixed spread as before, so every formula is identical (`git diff d42cdbd5 8e679a8c`). A 120-hour dry run reproduced the same trades to the cent: gold had 6 trades for +50.48 USD at 1× and +49.16 USD at 2×; oil had 2 trades for −19.31 USD at 1×.
- **Before commit `d42cdbd5`** (16:45), a JSON serialisation cast (`int`/`float`) was added after the very first live run at 16:44. That run processed no trades, so the cast has no effect on results.
- **Conclusion:** no forward configuration was silently changed.

## 7. Freeze

- **`FREEZE_MANIFEST.sha256`** holds SHA-256 hashes for every library and verification script, all historical result files and pre-registrations, the data-audit files, and every forward test's frozen rules and code. Live state, ledger and report files are excluded, because they change every hour.
- **`verify_freeze.py`** recomputes the hashes and prints **FREEZE VIOLATION** on any change. It runs at the start of every hourly forward update.
- **Prohibited from now on:** new theory batches, retrospective searches, parameter changes and re-selection of candidates from historical data.
- **What the forward tests decide:** each candidate's evaluation comes **only** from its forward paper test, at 100 closed trades, using the pre-registered rule: mean net > 0 at 2× costs and ≥ 2 bp per trade.
