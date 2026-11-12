# Theory library: results

**64 theories** pre-registered in 3 batches (`PREREGISTRATION.md` and its addenda, sources in `SOURCES.md`):
- **A–E:** trend, mean reversion, candlestick patterns, sessions/ICT and calendar effects;
- **F:** popular TradingView, YouTube and smart-money strategies, plus chart patterns;
- **G:** academic anomalies, CTA systems and more indicators.

They were tested on **7 markets** (Exness gold, oil, DAX, S&P 500 and Nasdaq; Binance BTC and ETH), with data from 2025-01-01 only. That gives **535 combinations**.
- **Costs:** real spreads, with every result shown at 2× cost.
- **Comparison:** development 2025 against holdout Jan–Oct 2026.
- **Random control:** 500 draws with the same sides and holding times at random dates.

**All figures are mean net return per trade in bp (1 bp = 0.01%) at 2× costs.**

## Final candidates (survived every pre-registered check)

| Rank | Candidate | Screen 2025 / 2026 | 9 neighbouring settings | Strict minute-level re-test 2025 / 2026 | Total 2025 / 2026 (minute-level) | Status |
|---|---|---|---|---|---|---|
| 1 | **B9 Fibonacci 61.8% pullback, ETH 1h** | +35.0 / +19.7 (327 / 288 trades) | 9/9 positive | **+32.3 / +19.6** | **+105% / +56%** | candidate; forward PAPER test **ETH_FIB** started 2026-11-12 |
| 2 | **D4 fair-value-gap fill, gold 1h** | +5.6 / +11.7 (392 / 311) | 9/9 | **+4.8 / +11.0** | **+18.5% / +34.1%** | candidate; forward test **GOLD_FVG**. The only one above the random 95th percentile in both years at minute level. |
| 3 | **B9 Fibonacci pullback, US oil 1h** | +18.3 / +26.0 (217 / 181) | 9/9 | **+12.9 / +17.3** | **+27.2% / +30.8%** | weaker candidate: its 2026 minute-level result is **below** the random 95th percentile (+22.8); forward test **OIL_FIB** |
| — | B9 Fibonacci pullback, BTC 1h | +3.9 / +4.1 | **3/9** | — | — | **failed** (fragile) |
| — | B7 TWAP reversion, gold and Nasdaq 15m | +0.2 / +1.4 and +2.8 / +0.1 | 9/9 and 8/9 | — | — | **failed** the size test (< 2 bp) |

**Warning:** with 535 combinations, 1–2 false passes are expected by luck. None of these is proven, and only the forward tests can confirm them.

## Family summary

| Family | Combinations | Positive in 2026 (2× cost) | Positive in both years | Median 2026 bp per trade |
|---|---|---|---|---|
| calendar | 19 | 11 | 5 | +0.7 |
| meanrev | 83 | 28 | 19 | -3.5 |
| pattern | 49 | 17 | 8 | -3.7 |
| retail | 91 | 26 | 13 | -6.2 |
| session | 48 | 15 | 6 | -2.9 |
| smc_pattern | 35 | 14 | 7 | -3.2 |
| trend | 210 | 70 | 29 | -5.7 |
| **all** | **535** | **181** | **87** | **-4.2** |

**Reading it:** across all theories the typical result after costs is slightly **negative**. About 1 in 6 combinations was positive in both years, which is roughly what luck alone produces. The popular retail and YouTube strategies (family "retail") have one of the worst medians.

## Combinations positive in both years but rejected by the random control

These made money, but no more than random trades with the same direction and holding time. Their profit came from the market's direction, not the signal. Most also have very few trades. Top 15, ranked by the weaker of the two years:

| # | Theory | Market | TF | 2025 bp (trades) | 2026 bp (trades) | Random p95 2025 / 2026 | Screen |
|---|---|---|---|---|---|---|---|
| 1 | A2 | ETHUSDT | 4h | +787.4 (11) | +613.2 (9) | 1188.13 / 934.93 | FAIL |
| 2 | A7 | XAUUSDm | 1d | +156.2 (9) | +444.4 (2) | 628.27 / 1391.82 | FAIL |
| 3 | A2 | XAUUSDm | 4h | +190.2 (13) | +94.1 (4) | 529.0 / 718.46 | FAIL |
| 4 | E2 | XAUUSDm | 1d | +126.4 (11) | +89.5 (10) | 163.76 / 146.35 | FAIL |
| 5 | B2 | US500m | 1d | +100.0 (3) | +87.9 (12) | 181.77 / 71.58 | FAIL |
| 6 | A11 | ETHUSDT | 1d | +213.1 (41) | +75.8 (35) | 319.29 / 246.54 | FAIL |
| 7 | A4 | XAUUSDm | 4h | +63.2 (42) | +165.8 (25) | 101.75 / 157.35 | FAIL |
| 8 | B2 | USTECm | 1d | +61.7 (3) | +103.4 (9) | 248.94 / 144.49 | FAIL |
| 9 | C3 | XAUUSDm | 1d | +55.9 (18) | +70.3 (13) | 86.65 / 212.49 | FAIL |
| 10 | F1 | USTECm | 4h | +42.4 (22) | +63.3 (12) | 101.38 / 131.13 | FAIL |
| 11 | F10 | USTECm | 1d | +164.2 (4) | +39.0 (5) | 364.87 / 155.74 | FAIL |
| 12 | G4 | XAUUSDm | 4h | +36.3 (59) | +48.6 (53) | 70.41 / 74.77 | FAIL |
| 13 | E2 | DE30m | 1d | +36.3 (11) | +55.5 (10) | 107.68 / 81.35 | FAIL |
| 14 | G7 | BTCUSDT | 1d | +29.9 (21) | +337.4 (14) | 244.57 / 445.85 | FAIL |
| 15 | F12 | ETHUSDT | 1h | +30.6 (61) | +29.3 (57) | 43.09 / 33.95 | FAIL |

## Bugs found and fixed during testing (all before any conclusion)

1. **Inside-bar / NR7:** an infinite loop on a candle that broke both sides of the setup.
2. **Friday cash close:** missing at 16:00 New York on Exness, so the last bar before the close is now used.
3. **Look-ahead:** a target could fill on the same candle as an intrabar limit/stop fill. Fixed per the pre-registration; it removed 3 false passes. The earlier results are kept in `results/results_before_intrabar_fix.json`.
4. **Exness archive data hole** (30–31 March 2026, oil/DAX/S&P/Nasdaq; see `../data_audit`): trades held across it are dropped. No verdict changed.

Files: `engine.py`, `theories*.py`, `run.py`, `verify_neighbours.py`, `verify_minute.py`, `results/*.json`.
