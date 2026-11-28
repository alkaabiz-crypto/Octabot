# Audit of all tests (2026-11-12)

The user asked for a full check of every earlier test: were there mistakes, and were the tests fair, or too hard? This folder holds the checks, the fixes and the corrected results. The original studies are left untouched, and the corrected numbers sit beside them.

## What was checked and what was found

| # | Check | Result |
|---|---|---|
| 1 | **Look-ahead.** The raw 15-minute file was cut at random points. Every signal and every closed trade known at the cut had to match the full-data run. The test covered 62 built-in indicators, 11 community indicators and 26 strategies, on gold and BTC (`lookahead.py`). | **No problems.** Nothing uses future data. |
| 2 | **Benchmark calibration, fixed exits** (target, ±1R, trailing). Random signals with no information were scored like real ones (`null_calibration.py`). | **Correct.** z had sd 0.97–1.04, and 1–5% of random signals were flagged. |
| 2b | **Benchmark calibration, held legs** (hold to the opposite signal, strategies' own exits, 4-bar hold). | **Mistake: too strict.** z had sd only 0.68–0.79, so real edges were understated by about 25–45%. Independent random draws overlap each other, while real held legs run back-to-back. The **fix** is a sequential, non-overlapping benchmark using the strategy's own leg lengths (`seq_held.py`). Its calibration: sd 0.98 on gold (5% flagged) and 1.06 on BTC (9% flagged, slightly lenient). A time-shift version was tried first and rejected (sd 0.71 on gold). |
| 2c | Gold KST study benchmark (`null_calibration_gold_engine.py`). | Acceptable: sd 0.86–0.97. |
| 2d | News-study benchmark (`null_calibration_news.py`). | Acceptable, slightly lenient: sd 0.98–1.20. Nothing passed anyway. |
| 3 | **Costs** (`costs.py`). The fixed extra slippage of 0.02% (stress 0.05%) of price was compared with the real Exness spread. | **Mistake: too strict for forex, indices and gold.** EUR/USD paid 0.09R of slippage against a 0.03R spread; US30 paid 0.05R against 0.01R; gold 0.027R against 0.005R. The **fix** ties slippage to the spread: 0.5× normally, 1.5× under stress. The edge-versus-random scores are unaffected, because the benchmark pays the same costs. Altcoin spreads (0.24–1.86R) and natural gas (0.69R) really are that large, which confirms those markets are untradeable on 15-minute charts. |
| 4 | **Rules that were too strict.** Several early studies required p ≤ 0.05 in 2025 **and** separately in 2026. | Too strict for short samples. The requested indicators and the indicator scan were **re-run on the single 2025-01-to-now window** (`pooled_2025.py`, 372 variants) with the fixes. **Still nothing passes:** 9 raw p ≤ 0.05, where luck gives about 19. The best was Donchian 20 BUY on gold with the half-stop target: 71% wins, +0.08R, z 2.3. |
| 5 | **News timing** (`feed_lag.py`). Is the "1-second edge" an Exness quirk? | Mostly the market itself. Binance BTC also needs about 1.2 s to move 0.1% after a release, and Exness trails Binance by 0.15–1.25 s. The news write-up was corrected. |
| 6 | **Daily briefing.** | **Bug fixed.** Any "FOMC" title, including minutes and speeches, was treated as a rate decision. It now matches only the decision. The direction note was also updated to the news-surprise results. |
| 7 | **Data files.** | Already fixed earlier today: release-date files and the BTC paper ledger were hidden by the repo's `*.csv` ignore rule. |

## Corrected results

All 45,794 held-leg results of the long-history and 33-market studies were re-scored with the fixed benchmark (`rescore_held.py`). Every result's costs were re-based (`patch_and_report.py`). The **unchanged** report scripts of both studies were then run on the patched copies. Output is in `reports/corrected_long_history/` and `reports/corrected_multi_market/`.

- **Long history (2019/2020 to now; oil, gold, BTC; 8,810 variants).** Before, 0 passed. Now **1 passes every rule**: **BTC Pivot Reversal BUY** (TradingView's built-in strategy, its own exits).
  - 1,405 trades, 34% wins, +0.17R per trade (+0.14R at stress cost), against +0.01R for random entries.
  - z 4.35, false-discovery significant, positive in 6 of 7 years (2022: −0.04R).
- **33 markets (fit 2023-07 to 2024-12, test 2025-01 to now).** Before, 0 of 88 per-market picks were confirmed. Now **1 of 91**: **ETH Pivot Reversal BUY**.
  - In the test period: 404 trades, 35% wins, +0.16R per trade (+0.12R at stress), z 3.18.
  - The per-class picks are still 0 of 20.
- **Robustness** (`pivot_robustness.py`, 5 seeds × 2,000 runs).
  - BTC: z 4.43–4.68. Dividing by the benchmark's slight leniency on BTC (1.056) gives z 4.27.
  - ETH test period: z 3.17–3.30, or 3.04 after the same adjustment.
  - Both are near the edge of the multiple-testing threshold, so treat them as **the strongest candidate found, not proof**.
  - BTC and ETH move together, so they are not fully independent evidence.

**What did not change.** The gold KST + VWAP study, the news studies and the requested-indicator results keep their verdicts. Gold's best held-leg variants (KST BUY, Momentum BUY, Coppock BUY) now reach z 3.8–4.0, but they stay below the false-discovery threshold.

## What follows from this

- The BTC Pivot Reversal paper test (frozen 2026-11-11) keeps its rules. Its final decision uses the old, conservative benchmark. A note in its README asks for the corrected score to be reported beside it.
- A new **ETH Pivot Reversal paper test** started on 2026-11-12, with the corrected benchmark in its frozen decision rule (`../eth_pivot_paper`).
- No live trading is recommended. A real edge has to show up on data no test has seen.
