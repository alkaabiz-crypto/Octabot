# Batch 003 results

Pre-registered in `PREREG.md` (commit `f0fb5698`, before any code). TEST is reused evaluation data; EARLY (2019/2020–2022) had never been evaluated by this programme.

**16 TEST tests, Benjamini–Hochberg at 5%: 0 significant.**

| Test | Market | EARLY | TRAIN | VALID | TEST mean bp (n) | TEST stress | TEST p | BH | Decision |
|---|---|---|---|---|---|---|---|---|---|
| H1-R1 | XAUUSDm | -3.68 | -2.45 | -1.48 | -1.50 (2019) | -2.63 | 0.705 | no | **REJECT** |
| H1-R2 | XAUUSDm | -2.94 | -1.29 | -0.60 | -0.03 (2798) | -1.17 | 0.052 | no | **REJECT** |
| H1-R1 | USOILm | -18.79 | -7.48 | -8.41 | -0.91 (872) | -8.29 | 0.009 | no | **REJECT** |
| H1-R2 | USOILm | -17.61 | -10.13 | -3.94 | -11.41 (1460) | -18.79 | 0.996 | no | **REJECT** |
| H1-R1 | EURUSDm | — | -0.65 | -2.02 | -0.10 (179) | -1.06 | 0.018 | no | **REJECT** |
| H1-R2 | EURUSDm | — | -0.68 | -3.33 | -1.40 (360) | -2.33 | 0.580 | no | **REJECT** |
| H1-R1 | USDJPYm | — | -2.57 | -1.24 | -2.18 (296) | -2.97 | 0.946 | no | **REJECT** |
| H1-R2 | USDJPYm | — | -0.83 | -2.31 | -1.14 (575) | -1.92 | 0.360 | no | **REJECT** |
| H1-R1 | US500m | — | -3.56 | -1.93 | -2.54 (448) | -3.80 | 0.914 | no | **REJECT** |
| H1-R2 | US500m | — | -2.71 | -2.98 | -1.50 (883) | -2.75 | 0.536 | no | **REJECT** |
| H1-R1 | BTCUSDm | -14.87 | -14.41 | -5.66 | -6.85 (1128) | -14.15 | 0.862 | no | **REJECT** |
| H1-R2 | BTCUSDm | -27.21 | -14.30 | -9.07 | -6.31 (1905) | -13.61 | 0.825 | no | **REJECT** |
| H2 | XAUUSDm | -2.22 | -1.78 | -0.54 | +0.48 (352) | -0.60 | 0.138 | no | **REJECT** |
| H2 | XAGUSDm | — | -21.75 | -20.01 | -11.30 (353) | -24.87 | 0.396 | no | **REJECT** |
| H3 | BTCUSDm | -24.17 | -83.26 | -61.67 | -49.32 (29) | -58.17 | 0.842 | no | **REJECT** |
| H4 | BTCUSDm | +33.61 | +5.65 | +41.09 | +37.21 (135) | +27.98 | 0.011 | no | **WATCH** |

## Reading

- **H1, round numbers:** all 12 rejected. They lose in nearly every period, and badly in oil and BTC. Whatever order clustering exists at round levels is far smaller than the spread.
- **H2, metal fixes:** rejected. Gold is about zero in every period (−2.2 to +0.5 bp); the pre-2015 effect is not visible. Silver loses 11–22 bp, mostly through its spread.
- **H3, the "CME gap fill":** clearly rejected. It loses in every period (−24 to −83 bp per trade).
  - Gaps of 1% or more were far more often followed by moves *away* from the Friday close than by fills within a 1:1 bracket.
  - The popular claim does not survive a fair test.
- **H4, Coinbase premium:** **WATCH**.
  - It is positive in all four periods, including the never-used EARLY years: +33.6 bp, 329 trades, benchmark p 0.006.
  - In TEST: +37.2 bp, 135 trades, p 0.011, still +28 bp at stress cost.
  - It does not survive BH across the 16 tests (threshold 0.0031 for the best p). Its per-trade spread is large (the TEST 95% CI is −2 to +77 bp).

## Exploratory diagnostics for H4 (after the result; they do not change the decision)

- **Both sides contribute:** longs +43.5 bp (306 trades), shorts +18.1 bp (396).
- **Not short-term momentum.** The same rule driven by the z-score of BTC's own last-hour return (same threshold and hold) was positive in EARLY and TRAIN (+14, +16 bp) and negative in VALIDATION and TEST (−28, −18 bp). The premium's correlation with the last 1-hour return is 0.08, and with the last 24 hours 0.19.
- **Holds against the price.** Signals where the premium and the last-hour price move disagree in sign still gave +34 bp (TEST, 103) and +40 bp (VALIDATION, 65), but only +3 to +7 bp in TRAIN and EARLY.
- **Timing checks passed:**
  - Exness candle timestamps are bar starts: the open at *t* matches Binance at *t* (5 bp), not *t* + 1 h (17 bp).
  - Coinbase's and Binance's hourly candles align at the same *t* (4 bp, against 24 bp shifted by an hour).
  - Signals use the hourly close, and entries the next Exness open after it.

**Next step:** a WATCH is not promoted. Because H4 is the strongest result in the programme so far, it gets a **separately pre-registered forward paper observation** on new data (`../forward_h4/`), judged by rule V2. The batch decision stays WATCH.

## ETH replication of H4 (pre-registered in `REPLICATION_ETH_PREREG.md`, commit `e07c72a3`)

**Result: NOT REPLICATED.** `results/replication_eth.json`, script `replicate_eth.py`. Data: Coinbase ETH-USD and Binance ETHUSDT hourly; Exness ETHUSDm 15m.

| Period | Trades | Mean net (bp) | Stress (bp) | p vs random |
|---|---|---|---|---|
| TRAIN 2023-01 → 2024-06 | 136 | +20.19 | +10.04 | 0.046 |
| VALIDATION 2024-07 → 2025-06 | 90 | +78.51 | +68.36 | 0.008 |
| TEST 2025-07 → | 146 | **−8.00** | −18.18 | 0.471 |

**Reading.**
- The same rule worked on ETH in 2023–mid 2025, and failed in the most recent 16 months. The BTC result held in that same period.
- This weakens the case for H4 as a general "US demand" effect: it may be BTC-specific, regime-dependent, or partly luck.
- H4 stays **WATCH**. Its forward paper test continues unchanged, and it is now the deciding evidence.

## Pre-registered H4 checks (`H4_CHECKS_PREREG.md`, commit `0ffa6a90`; script `h4_checks.py`; output `results/h4_checks.json`)

### Check A: untouched 2017-09 → 2019-12, Binance hourly prices, 0.10% per side. **CONFIRMED**

| Trades | Mean net (bp) | At 2× fee | 95% CI (t) | Win % | p vs random | 2017 / 2018 / 2019 | Longs / shorts |
|---|---|---|---|---|---|---|---|
| 190 | **+80.3** | +60.3 | +11.6 … +149.0 | 53.2 | **< 0.001** (0 of 1,000) | +164 (33) / +33 (87) / +99 (70) | +116 (81) / +54 (109) |

### Check B: Bitstamp (USD) instead of Binance (USDT) as the second venue, Exness execution. **NOT REPLICATED**

| Period | Trades | Mean (bp) | Stress (bp) | p |
|---|---|---|---|---|
| EARLY 2020–22 | 418 | +2.68 | −6.54 | 0.173 |
| TRAIN | 266 | −9.11 | −18.33 | 0.558 |
| VALIDATION | 187 | +28.05 | +18.83 | 0.033 |
| TEST | 244 | −18.28 | −27.50 | 0.823 |

## What the H4 evidence now says

| Evidence | Result |
|---|---|
| BTC, Coinbase vs Binance, 2017–2019 (never used) | **+80 bp**, p < 0.001 |
| BTC, 2020–2022 (never used) | +34 bp, p 0.006 |
| BTC, 2023 → mid-2024 | +6 bp, p 0.22 |
| BTC, mid-2024 → mid-2025 | +41 bp, p 0.03 |
| BTC, mid-2025 → now | +37 bp, p 0.011 |
| ETH, same rule | +20 / +79 / **−8** bp: not replicated |
| BTC, Coinbase vs Bitstamp (both USD) | mixed: not replicated |

**Reading.**
- [CALC] On BTC, the rule as defined (Coinbase USD against Binance USDT) has been positive in every period since 2017 across about 890 trades. Its 2017–2019 result is strong, but it shrinks over time and is thin after retail fees.
- [HYP] The effect is **specific to the Coinbase-vs-Binance-USDT comparison**: it fails against another USD venue. It is therefore probably about **US-dollar demand against offshore USDT demand**, partly a USDT premium signal, rather than "Coinbase buying" alone.
- It did not carry over to ETH in the last 16 months.
- **Decision unchanged.** H4 remains WATCH by its batch rule, and the forward paper test decides. No rule or parameter was changed after any of these results.
