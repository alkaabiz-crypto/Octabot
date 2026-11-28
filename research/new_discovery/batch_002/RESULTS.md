# Batch 002 results

Pre-registered in `PREREG.md`, with amendment 1 disclosed there. TEST is **reused evaluation data**, so a pass is only a SCREEN-PASS, which still needs a forward period.

**38 TEST-period tests, Benjamini–Hochberg at 5%: 1 significant** (E006 DE30m).

Effect metric: E005/E007 Sharpe difference against the constant-exposure benchmark; E006 QLIKE loss reduction (positive means HAR is better); E008/E009 mean net bp per trade.

| Exp | Market | TRAIN effect | VALID effect | TEST effect | TEST p | BH | Extra (TEST) | Decision |
|---|---|---|---|---|---|---|---|---|
| E005 | XAUUSDm | -0.026 | +0.264 | +0.476 | 0.084 | no | Sharpe 1.25 vs 0.77, exposure 0.60, max DD 18.4% | **REJECT** |
| E005 | USOILm | -0.014 | +0.103 | +0.048 | 0.431 | no | Sharpe 0.80 vs 0.75, exposure 0.75, max DD 24.6% | **REJECT** |
| E005 | UKOILm | -0.064 | -0.013 | -0.044 | 0.581 | no | Sharpe 0.71 vs 0.76, exposure 0.86, max DD 25.9% | **REJECT** |
| E005 | BTCUSDm | -0.133 | -0.151 | -0.030 | 0.609 | no | Sharpe -0.39 vs -0.36, exposure 1.20, max DD 87.2% | **REJECT** |
| E005 | ETHUSDm | +0.033 | -0.176 | -0.080 | 0.693 | no | Sharpe 0.01 vs 0.09, exposure 0.84, max DD 87.5% | **REJECT** |
| E005 | EURUSDm | -0.115 | -0.138 | -0.071 | 0.616 | no | Sharpe -0.71 vs -0.64, exposure 1.25, max DD 10.6% | **REJECT** |
| E005 | GBPUSDm | -0.169 | -0.081 | -0.060 | 0.666 | no | Sharpe -0.36 vs -0.30, exposure 1.21, max DD 6.9% | **REJECT** |
| E005 | USDJPYm | +0.037 | -0.288 | -0.277 | 0.944 | no | Sharpe 0.62 vs 0.90, exposure 1.17, max DD 9.2% | **REJECT** |
| E005 | US500m | +0.007 | -0.528 | -0.616 | 1.000 | no | Sharpe 0.54 vs 1.16, exposure 1.19, max DD 12.3% | **REJECT** |
| E005 | USTECm | +0.159 | -0.340 | -0.316 | 0.967 | no | Sharpe 0.55 vs 0.87, exposure 1.09, max DD 15.9% | **REJECT** |
| E005 | DE30m | +0.013 | +0.086 | -0.182 | 0.928 | no | Sharpe 0.48 vs 0.67, exposure 0.86, max DD 10.9% | **REJECT** |
| E006 | XAUUSDm | +0.024 | +0.094 | -0.013 | 0.653 | no | QLIKE EWMA 0.472 vs HAR 0.485, DM -0.39 | **REJECT** |
| E006 | USOILm | +0.014 | +0.068 | -0.047 | 0.654 | no | QLIKE EWMA 0.660 vs HAR 0.707, DM -0.40 | **REJECT** |
| E006 | UKOILm | -0.002 | +0.025 | +0.071 | 0.054 | no | QLIKE EWMA 0.544 vs HAR 0.473, DM +1.61 | **REJECT** |
| E006 | BTCUSDm | +0.077 | +0.047 | +0.020 | 0.155 | no | QLIKE EWMA 0.352 vs HAR 0.332, DM +1.02 | **WATCH** |
| E006 | ETHUSDm | +0.049 | +0.038 | +0.054 | 0.008 | no | QLIKE EWMA 0.365 vs HAR 0.311, DM +2.43 | **WATCH** |
| E006 | EURUSDm | +0.007 | +0.001 | +0.003 | 0.429 | no | QLIKE EWMA 0.398 vs HAR 0.395, DM +0.18 | **WATCH** |
| E006 | GBPUSDm | +0.015 | +0.014 | +0.003 | 0.356 | no | QLIKE EWMA 0.356 vs HAR 0.353, DM +0.37 | **WATCH** |
| E006 | USDJPYm | -0.001 | +0.121 | +0.092 | 0.068 | no | QLIKE EWMA 0.695 vs HAR 0.603, DM +1.49 | **REJECT** |
| E006 | US500m | +0.030 | +0.217 | +0.062 | 0.005 | no | QLIKE EWMA 0.593 vs HAR 0.531, DM +2.59 | **WATCH** |
| E006 | USTECm | +0.073 | +0.156 | +0.022 | 0.113 | no | QLIKE EWMA 0.568 vs HAR 0.546, DM +1.21 | **WATCH** |
| E006 | DE30m | -0.028 | +0.118 | +0.097 | 0.000 | yes | QLIKE EWMA 0.252 vs HAR 0.154, DM +4.11 | **REJECT** |
| E007 | XAUUSDm | -0.785 | -0.631 | -0.935 | 0.897 | no | Sharpe -0.17 vs 0.77, exposure 0.39, max DD 20.7% | **REJECT** |
| E007 | USOILm | n/a | n/a | +0.816 | 0.072 | no | Sharpe 1.57 vs 0.75, exposure 0.73, max DD 22.7% | **REJECT** |
| E007 | UKOILm | -0.344 | -0.017 | -0.594 | 0.805 | no | Sharpe 0.16 vs 0.76, exposure 0.53, max DD 25.8% | **REJECT** |
| E007 | BTCUSDm | -0.339 | -0.118 | +0.068 | 0.439 | no | Sharpe -0.29 vs -0.36, exposure 0.36, max DD 33.5% | **REJECT** |
| E007 | ETHUSDm | -0.537 | +0.219 | -0.503 | 0.871 | no | Sharpe -0.42 vs 0.09, exposure 0.50, max DD 75.6% | **REJECT** |
| E007 | EURUSDm | -1.381 | -1.040 | +0.318 | 0.396 | no | Sharpe -0.32 vs -0.64, exposure 0.04, max DD 2.1% | **REJECT** |
| E007 | GBPUSDm | -0.867 | +0.358 | -0.119 | 0.458 | no | Sharpe -0.42 vs -0.30, exposure 0.01, max DD 0.7% | **REJECT** |
| E007 | USDJPYm | +0.926 | +0.331 | +0.039 | 0.469 | no | Sharpe 0.94 vs 0.90, exposure 0.84, max DD 4.1% | **WATCH** |
| E007 | US500m | n/a | -0.811 | -0.172 | 0.876 | no | Sharpe 0.98 vs 1.16, exposure 0.92, max DD 9.1% | **REJECT** |
| E007 | USTECm | n/a | n/a | +0.411 | 0.320 | no | Sharpe 1.28 vs 0.87, exposure 0.02, max DD 1.0% | **REJECT** |
| E007 | DE30m | n/a | +0.565 | +0.026 | 0.452 | no | Sharpe 0.69 vs 0.67, exposure 0.93, max DD 10.8% | **REJECT** |
| E008 | BTCUSDm->ETHUSDm | -15.868 | -18.499 | -7.032 | 0.307 | no | n 128, stress -15.2 bp | **REJECT** |
| E008 | ETHUSDm->BTCUSDm | -11.771 | -6.888 | -3.407 | 0.453 | no | n 939, stress -6.8 bp | **REJECT** |
| E009 | US500m | +7.336 | +14.014 | +3.498 | 0.527 | no | n 13, stress +0.4 bp, ordinary-day mean +3.5 bp | **WATCH** |
| E009 | USTECm | +13.052 | +18.629 | +9.040 | 0.497 | no | n 12, stress +6.1 bp, ordinary-day mean +6.2 bp | **WATCH** |
| E009 | DE30m | +2.968 | -42.185 | +47.974 | 0.111 | no | n 5, stress +42.6 bp, ordinary-day mean -0.8 bp | **REJECT** |
