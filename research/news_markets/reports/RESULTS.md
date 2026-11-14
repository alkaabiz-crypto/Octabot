# Results: trading scheduled news across markets

14 markets, 225 market × event × strategy combinations. Strategies are judged against the same rule on normal days at the same clock time. Cells: events, win rate, expectancy, z.

## Headline

- Passed in the fit period: **15** (about 11 expected by luck).
- Confirmed in 2025-01 to now after the multiple-testing correction: **0**.
- Raw p ≤ 0.05 in the test period, before correction: 21 of 225 (about 11 expected by luck).

## Combinations that passed the fit period

| Market | Event | Strategy | Fit | Test | Test p |
|---|---|---|---|---|---|
| BTCUSDm | FOMC | break of release candle | 24, win 83%, +0.582R, z +5.61 | 9, win 11%, -0.555R, z -2.95 | 0.998 |
| BTCUSDm | FOMC | follow first 15 min | 36, win 61%, +0.512R, z +5.58 | 15, win 27%, -0.376R, z -2.80 | 0.997 |
| XAUUSDm | FOMC | follow first 15 min | 36, win 47%, +0.188R, z +5.57 | 15, win 40%, -0.025R, z +0.35 | 0.363 |
| XAGUSDm | CPI | follow first 15 min | 18, win 50%, +0.639R, z +4.21 | 22, win 59%, +0.334R, z +2.09 | 0.018 |
| BTCUSDm | FOMC | follow first 30 min | 36, win 58%, +0.366R, z +4.16 | 15, win 47%, -0.113R, z -0.60 | 0.725 |
| USDCADm | NFP | follow first 30 min | 18, win 67%, +0.635R, z +4.04 | 22, win 41%, -0.239R, z -0.21 | 0.583 |
| EURUSDm | CPI | buy 24 h before | 18, win 67%, +0.867R, z +4.01 | 22, win 41%, -0.173R, z -0.38 | 0.650 |
| XAUUSDm | FOMC | break of release candle | 28, win 43%, +0.077R, z +3.20 | 14, win 64%, +0.146R, z +2.01 | 0.022 |
| GBPUSDm | NFP | fade first 15 min | 18, win 44%, +0.592R, z +3.16 | 22, win 36%, -0.144R, z -0.06 | 0.523 |
| XAUUSDm | FOMC | fade first 15 min | 36, win 42%, +0.092R, z +3.04 | 15, win 40%, -0.161R, z -1.49 | 0.932 |
| XAGUSDm | CPI | follow first 30 min | 18, win 50%, +0.437R, z +2.93 | 22, win 45%, +0.027R, z +0.79 | 0.214 |
| USDJPYm | CPI | follow first 30 min | 18, win 50%, +0.291R, z +2.52 | 22, win 27%, -0.355R, z -1.80 | 0.964 |
| US30m | CPI | buy 24 h before | 18, win 50%, +0.635R, z +2.30 | 22, win 41%, +0.000R, z +0.11 | 0.455 |
| GBPUSDm | CPI | follow first 30 min | 18, win 39%, +0.233R, z +2.23 | 22, win 36%, -0.175R, z -0.11 | 0.546 |
| USOILm | FOMC | break of release candle | 19, win 47%, +0.067R, z +1.84 | 10, win 50%, +0.016R, z +0.78 | 0.217 |

## How much more each market moves after news (4 hours after the release, in ATR)

| Market | FOMC | CPI | NFP | EIA |
|---|---|---|---|---|
| BTCUSDm | 1.6 vs 0.6 (×2.5) | 1.8 vs 1.1 (×1.6) | 1.1 vs 1.1 (×1.0) | - |
| DE30m | 0.8 vs 0.4 (×2.2) | 1.7 vs 1.2 (×1.4) | 1.7 vs 1.2 (×1.5) | - |
| ETHUSDm | 1.2 vs 0.6 (×1.9) | 2.2 vs 1.1 (×2.0) | 1.6 vs 1.1 (×1.5) | - |
| EURUSDm | 2.3 vs 0.4 (×5.9) | 2.7 vs 1.1 (×2.5) | 2.4 vs 1.1 (×2.3) | - |
| GBPUSDm | 2.5 vs 0.4 (×5.8) | 2.3 vs 1.3 (×1.8) | 2.4 vs 1.3 (×1.9) | - |
| UKOILm | - | 1.2 vs 1.3 (×0.9) | 1.9 vs 1.3 (×1.4) | 1.2 vs 1.0 (×1.3) |
| US30m | 2.0 vs 0.7 (×3.1) | 2.8 vs 1.9 (×1.5) | 2.7 vs 1.8 (×1.5) | - |
| US500m | 1.7 vs 0.7 (×2.5) | 2.7 vs 1.7 (×1.6) | 2.9 vs 1.7 (×1.7) | - |
| USDCADm | 2.2 vs 0.5 (×4.4) | 2.4 vs 1.4 (×1.7) | 3.1 vs 1.4 (×2.3) | 1.1 vs 0.9 (×1.2) |
| USDJPYm | 2.7 vs 0.4 (×6.7) | 2.1 vs 1.0 (×2.1) | 1.9 vs 1.0 (×1.9) | - |
| USOILm | 0.6 vs 0.5 (×1.3) | 1.5 vs 1.4 (×1.0) | 1.6 vs 1.5 (×1.0) | 1.4 vs 1.1 (×1.3) |
| USTECm | 1.8 vs 0.6 (×2.9) | 2.1 vs 1.9 (×1.1) | 2.9 vs 1.9 (×1.6) | - |
| XAGUSDm | 1.7 vs 0.4 (×4.6) | 2.6 vs 1.3 (×2.0) | 2.4 vs 1.4 (×1.8) | - |
| XAUUSDm | 2.6 vs 0.4 (×7.2) | 2.2 vs 1.2 (×1.8) | 2.7 vs 1.2 (×2.1) | - |

## Every combination

| Market | Event | Strategy | Fit | Test |
|---|---|---|---|---|
| BTCUSDm | FOMC | follow first 15 min | 36, win 61%, +0.512R, z +5.58 | 15, win 27%, -0.376R, z -2.80 |
| BTCUSDm | FOMC | fade first 15 min | 36, win 22%, -0.537R, z -4.39 | 15, win 53%, +0.015R, z +0.29 |
| BTCUSDm | FOMC | follow first 30 min | 36, win 58%, +0.366R, z +4.16 | 15, win 47%, -0.113R, z -0.60 |
| BTCUSDm | FOMC | break of release candle | 24, win 83%, +0.582R, z +5.61 | 9, win 11%, -0.555R, z -2.95 |
| BTCUSDm | FOMC | buy 24 h before | 36, win 61%, +0.199R, z +0.48 | 15, win 47%, -0.103R, z -0.26 |
| BTCUSDm | CPI | follow first 15 min | 54, win 43%, -0.089R, z -0.19 | 21, win 52%, +0.048R, z +0.56 |
| BTCUSDm | CPI | fade first 15 min | 54, win 48%, -0.001R, z +0.39 | 21, win 48%, +0.062R, z +0.16 |
| BTCUSDm | CPI | follow first 30 min | 54, win 48%, -0.103R, z -0.33 | 21, win 43%, -0.106R, z -0.45 |
| BTCUSDm | CPI | break of release candle | 33, win 61%, +0.125R, z +1.30 | 12, win 67%, +0.223R, z +0.58 |
| BTCUSDm | CPI | buy 24 h before | 54, win 33%, -0.025R, z -0.20 | 21, win 33%, -0.228R, z -0.70 |
| BTCUSDm | NFP | follow first 15 min | 54, win 35%, -0.261R, z -1.51 | 22, win 36%, -0.163R, z -0.45 |
| BTCUSDm | NFP | fade first 15 min | 54, win 52%, +0.137R, z +1.60 | 22, win 55%, -0.055R, z -0.46 |
| BTCUSDm | NFP | follow first 30 min | 54, win 35%, -0.236R, z -1.38 | 22, win 41%, -0.199R, z -0.75 |
| BTCUSDm | NFP | break of release candle | 37, win 30%, -0.225R, z -1.34 | 11, win 36%, -0.090R, z -0.28 |
| BTCUSDm | NFP | buy 24 h before | 54, win 30%, -0.338R, z -1.49 | 22, win 36%, +0.121R, z +0.25 |
| DE30m | FOMC | follow first 15 min | 11, win 55%, +0.425R, z +5.35 | 15, win 33%, -0.273R, z -2.11 |
| DE30m | FOMC | fade first 15 min | 11, win 27%, -0.531R, z -4.11 | 15, win 47%, -0.051R, z +0.38 |
| DE30m | FOMC | follow first 30 min | 11, win 64%, +0.417R, z +5.23 | 15, win 27%, -0.378R, z -2.87 |
| DE30m | FOMC | break of release candle | 8, win 38%, +0.077R, z +1.78 | 12, win 17%, -0.393R, z -3.09 |
| DE30m | FOMC | buy 24 h before | 11, win 64%, +0.329R, z +1.02 | 15, win 33%, -0.346R, z -1.22 |
| DE30m | CPI | follow first 15 min | 18, win 50%, -0.098R, z +0.18 | 22, win 41%, -0.193R, z -0.50 |
| DE30m | CPI | fade first 15 min | 18, win 17%, -0.685R, z -3.15 | 22, win 50%, +0.037R, z +0.42 |
| DE30m | CPI | follow first 30 min | 18, win 44%, -0.085R, z +0.62 | 22, win 45%, +0.015R, z +0.88 |
| DE30m | CPI | break of release candle | 9, win 11%, -0.733R, z -2.82 | 10, win 50%, +0.155R, z +0.99 |
| DE30m | CPI | buy 24 h before | 18, win 50%, +0.248R, z +1.03 | 22, win 45%, +0.095R, z +0.09 |
| DE30m | NFP | follow first 15 min | 18, win 44%, -0.154R, z -0.05 | 21, win 43%, -0.175R, z -0.30 |
| DE30m | NFP | fade first 15 min | 18, win 33%, -0.234R, z -0.47 | 21, win 43%, -0.007R, z +0.14 |
| DE30m | NFP | follow first 30 min | 18, win 56%, -0.053R, z +0.81 | 21, win 48%, -0.206R, z -0.76 |
| DE30m | NFP | break of release candle | 8, win 62%, +0.121R, z +1.24 | 13, win 31%, -0.291R, z -1.19 |
| DE30m | NFP | buy 24 h before | 18, win 28%, -0.455R, z -1.43 | 20, win 35%, -0.230R, z -0.87 |
| ETHUSDm | FOMC | follow first 15 min | 12, win 67%, +0.475R, z +2.18 | 15, win 47%, -0.149R, z -0.24 |
| ETHUSDm | FOMC | fade first 15 min | 12, win 8%, -0.758R, z -3.77 | 15, win 53%, -0.153R, z -1.11 |
| ETHUSDm | FOMC | follow first 30 min | 12, win 67%, +0.399R, z +1.67 | 15, win 27%, -0.346R, z -2.11 |
| ETHUSDm | FOMC | break of release candle | 11, win 55%, +0.094R, z +0.43 | 8, win 25%, -0.512R, z -2.88 |
| ETHUSDm | FOMC | buy 24 h before | 12, win 17%, -0.314R, z -0.66 | 15, win 40%, -0.012R, z -0.07 |
| ETHUSDm | CPI | follow first 15 min | 18, win 33%, -0.298R, z -1.02 | 22, win 73%, +0.631R, z +2.90 |
| ETHUSDm | CPI | fade first 15 min | 18, win 56%, -0.004R, z +0.43 | 22, win 18%, -0.500R, z -3.16 |
| ETHUSDm | CPI | follow first 30 min | 18, win 33%, -0.331R, z -1.13 | 22, win 77%, +0.547R, z +2.56 |
| ETHUSDm | CPI | break of release candle | 8, win 38%, -0.137R, z -0.37 | 12, win 75%, +0.432R, z +1.09 |
| ETHUSDm | CPI | buy 24 h before | 18, win 28%, +0.064R, z +0.42 | 22, win 32%, -0.369R, z -0.89 |
| ETHUSDm | NFP | follow first 15 min | 18, win 56%, -0.023R, z +0.19 | 22, win 45%, -0.057R, z -0.18 |
| ETHUSDm | NFP | fade first 15 min | 18, win 33%, -0.277R, z -0.91 | 22, win 41%, -0.060R, z -0.49 |
| ETHUSDm | NFP | follow first 30 min | 18, win 39%, -0.251R, z -0.89 | 22, win 32%, -0.231R, z -1.02 |
| ETHUSDm | NFP | break of release candle | 6, win 67%, +0.170R, z +0.59 | 10, win 30%, -0.243R, z -0.99 |
| ETHUSDm | NFP | buy 24 h before | 18, win 28%, -0.257R, z -0.42 | 22, win 27%, -0.010R, z -0.09 |
| EURUSDm | FOMC | follow first 15 min | 12, win 50%, +0.192R, z +3.82 | 15, win 27%, -0.357R, z -2.58 |
| EURUSDm | FOMC | fade first 15 min | 12, win 25%, -0.597R, z -5.27 | 15, win 47%, +0.122R, z +3.10 |
| EURUSDm | FOMC | follow first 30 min | 12, win 50%, +0.035R, z +2.37 | 15, win 40%, -0.035R, z +0.90 |
| EURUSDm | FOMC | break of release candle | 9, win 44%, -0.023R, z +1.61 | 14, win 71%, +0.599R, z +9.08 |
| EURUSDm | FOMC | buy 24 h before | 12, win 42%, +0.172R, z +1.32 | 15, win 20%, -0.692R, z -1.68 |
| EURUSDm | CPI | follow first 15 min | 18, win 28%, -0.156R, z +0.42 | 22, win 41%, -0.304R, z -0.67 |
| EURUSDm | CPI | fade first 15 min | 18, win 33%, -0.166R, z -0.44 | 22, win 45%, +0.167R, z +1.54 |
| EURUSDm | CPI | follow first 30 min | 18, win 39%, +0.038R, z +1.11 | 22, win 32%, -0.404R, z -1.38 |
| EURUSDm | CPI | break of release candle | 8, win 62%, +0.706R, z +2.57 | 7, win 57%, -0.007R, z +0.50 |
| EURUSDm | CPI | buy 24 h before | 18, win 67%, +0.867R, z +4.01 | 22, win 41%, -0.173R, z -0.38 |
| EURUSDm | NFP | follow first 15 min | 18, win 44%, +0.020R, z +1.16 | 22, win 36%, -0.107R, z +0.61 |
| EURUSDm | NFP | fade first 15 min | 18, win 39%, +0.021R, z +0.62 | 22, win 41%, -0.168R, z -0.42 |
| EURUSDm | NFP | follow first 30 min | 18, win 39%, -0.201R, z +0.00 | 22, win 23%, -0.347R, z -0.96 |
| EURUSDm | NFP | break of release candle | 9, win 67%, +0.330R, z +1.54 | 9, win 22%, -0.054R, z +0.16 |
| EURUSDm | NFP | buy 24 h before | 18, win 39%, +0.035R, z +1.13 | 22, win 36%, -0.455R, z -1.29 |
| GBPUSDm | FOMC | follow first 15 min | 12, win 58%, +0.213R, z +4.58 | 15, win 53%, +0.146R, z +3.47 |
| GBPUSDm | FOMC | fade first 15 min | 12, win 25%, -0.570R, z -5.11 | 15, win 40%, -0.287R, z -1.98 |
| GBPUSDm | FOMC | follow first 30 min | 12, win 67%, +0.340R, z +6.39 | 15, win 53%, +0.153R, z +3.85 |
| GBPUSDm | FOMC | break of release candle | 7, win 43%, +0.025R, z +1.77 | 15, win 67%, +0.250R, z +6.02 |
| GBPUSDm | FOMC | buy 24 h before | 12, win 42%, +0.144R, z +0.90 | 15, win 20%, -0.656R, z -1.82 |
| GBPUSDm | CPI | follow first 15 min | 18, win 44%, -0.041R, z +1.09 | 22, win 32%, -0.102R, z +0.19 |
| GBPUSDm | CPI | fade first 15 min | 18, win 28%, -0.430R, z -1.82 | 22, win 50%, +0.281R, z +2.16 |
| GBPUSDm | CPI | follow first 30 min | 18, win 39%, +0.233R, z +2.23 | 22, win 36%, -0.175R, z -0.11 |
| GBPUSDm | CPI | break of release candle | 7, win 71%, +0.961R, z +3.88 | 8, win 38%, +0.062R, z +0.57 |
| GBPUSDm | CPI | buy 24 h before | 18, win 44%, +0.084R, z +1.14 | 22, win 45%, +0.036R, z -0.03 |
| GBPUSDm | NFP | follow first 15 min | 18, win 39%, +0.017R, z +1.18 | 22, win 32%, -0.214R, z -0.39 |
| GBPUSDm | NFP | fade first 15 min | 18, win 44%, +0.592R, z +3.16 | 22, win 36%, -0.144R, z -0.06 |
| GBPUSDm | NFP | follow first 30 min | 18, win 33%, -0.257R, z -0.21 | 22, win 32%, -0.265R, z -0.72 |
| GBPUSDm | NFP | break of release candle | 10, win 50%, +0.272R, z +1.76 | 9, win 11%, -0.584R, z -1.83 |
| GBPUSDm | NFP | buy 24 h before | 18, win 50%, +0.192R, z +1.60 | 22, win 27%, -0.407R, z -1.37 |
| UKOILm | FOMC | follow first 15 min | 12, win 50%, -0.119R, z +0.17 | 15, win 27%, -0.156R, z -0.24 |
| UKOILm | FOMC | fade first 15 min | 12, win 33%, -0.205R, z -0.21 | 15, win 60%, -0.088R, z +0.43 |
| UKOILm | FOMC | follow first 30 min | 12, win 50%, -0.125R, z +0.31 | 15, win 27%, -0.065R, z +0.30 |
| UKOILm | FOMC | break of release candle | 8, win 62%, +0.073R, z +1.50 | 9, win 33%, -0.040R, z +0.43 |
| UKOILm | FOMC | buy 24 h before | 12, win 42%, -0.049R, z +0.57 | 15, win 47%, +0.121R, z +0.49 |
| UKOILm | CPI | follow first 15 min | 18, win 39%, -0.222R, z -0.33 | 22, win 50%, +0.027R, z +0.38 |
| UKOILm | CPI | fade first 15 min | 18, win 22%, -0.537R, z -1.60 | 22, win 32%, -0.157R, z -0.06 |
| UKOILm | CPI | follow first 30 min | 18, win 22%, -0.431R, z -1.26 | 22, win 50%, +0.013R, z +0.71 |
| UKOILm | CPI | break of release candle | 16, win 19%, -0.504R, z -1.37 | 17, win 41%, -0.023R, z +0.32 |
| UKOILm | CPI | buy 24 h before | 18, win 33%, -0.168R, z +0.08 | 22, win 36%, -0.019R, z +0.44 |
| UKOILm | NFP | follow first 15 min | 18, win 44%, +0.047R, z +0.88 | 21, win 33%, -0.198R, z -0.68 |
| UKOILm | NFP | fade first 15 min | 18, win 39%, -0.289R, z -0.39 | 21, win 43%, -0.020R, z +0.51 |
| UKOILm | NFP | follow first 30 min | 18, win 50%, +0.049R, z +0.96 | 21, win 52%, +0.018R, z +0.69 |
| UKOILm | NFP | break of release candle | 14, win 50%, +0.202R, z +1.76 | 19, win 58%, +0.073R, z +1.04 |
| UKOILm | NFP | buy 24 h before | 18, win 28%, -0.203R, z -0.07 | 22, win 36%, +0.186R, z +1.22 |
| UKOILm | EIA | follow first 15 min | 63, win 46%, -0.140R, z +0.53 | 95, win 43%, -0.064R, z +0.37 |
| UKOILm | EIA | fade first 15 min | 63, win 30%, -0.234R, z -0.97 | 96, win 45%, -0.072R, z +1.02 |
| UKOILm | EIA | follow first 30 min | 63, win 37%, -0.233R, z -1.14 | 95, win 39%, -0.144R, z -0.48 |
| UKOILm | EIA | break of release candle | 46, win 41%, -0.101R, z -0.03 | 71, win 32%, -0.257R, z -1.65 |
| UKOILm | EIA | buy 24 h before | 63, win 37%, -0.160R, z +0.10 | 94, win 33%, -0.163R, z -0.84 |
| US30m | FOMC | follow first 15 min | 12, win 50%, +0.567R, z +3.36 | 15, win 40%, -0.001R, z +0.79 |
| US30m | FOMC | fade first 15 min | 12, win 25%, -0.580R, z -2.74 | 15, win 33%, -0.321R, z -1.73 |
| US30m | FOMC | follow first 30 min | 12, win 42%, +0.485R, z +3.42 | 15, win 47%, +0.107R, z +1.53 |
| US30m | FOMC | break of release candle | 9, win 44%, +0.509R, z +2.80 | 12, win 33%, -0.209R, z -0.83 |
| US30m | FOMC | buy 24 h before | 12, win 83%, +0.354R, z +1.26 | 15, win 67%, +0.044R, z -0.12 |
| US30m | CPI | follow first 15 min | 18, win 33%, -0.296R, z -0.46 | 22, win 36%, -0.159R, z -0.12 |
| US30m | CPI | fade first 15 min | 18, win 11%, -0.749R, z -2.38 | 22, win 36%, +0.048R, z +0.23 |
| US30m | CPI | follow first 30 min | 18, win 44%, -0.179R, z -0.26 | 22, win 41%, +0.061R, z +0.71 |
| US30m | CPI | break of release candle | 8, win 25%, -0.702R, z -1.43 | 6, win 33%, +0.140R, z +1.02 |
| US30m | CPI | buy 24 h before | 18, win 50%, +0.635R, z +2.30 | 22, win 41%, +0.000R, z +0.11 |
| US30m | NFP | follow first 15 min | 18, win 33%, -0.362R, z -0.71 | 21, win 38%, -0.182R, z -0.24 |
| US30m | NFP | fade first 15 min | 18, win 28%, -0.347R, z -0.68 | 21, win 48%, +0.149R, z +0.67 |
| US30m | NFP | follow first 30 min | 18, win 33%, -0.305R, z -0.66 | 21, win 38%, -0.243R, z -0.42 |
| US30m | NFP | break of release candle | 8, win 38%, -0.166R, z -0.04 | 12, win 42%, -0.314R, z -0.49 |
| US30m | NFP | buy 24 h before | 18, win 22%, -0.301R, z -0.46 | 22, win 32%, -0.025R, z +0.03 |
| US500m | FOMC | follow first 15 min | 12, win 33%, +0.318R, z +2.49 | 15, win 40%, -0.165R, z -0.18 |
| US500m | FOMC | fade first 15 min | 12, win 8%, -0.790R, z -3.32 | 15, win 27%, -0.647R, z -3.58 |
| US500m | FOMC | follow first 30 min | 12, win 42%, +0.365R, z +2.65 | 15, win 40%, -0.142R, z +0.06 |
| US500m | FOMC | break of release candle | 10, win 40%, +0.625R, z +3.07 | 11, win 18%, -0.436R, z -2.16 |
| US500m | FOMC | buy 24 h before | 12, win 58%, +0.220R, z +1.20 | 15, win 47%, -0.285R, z -0.93 |
| US500m | CPI | follow first 15 min | 18, win 28%, -0.216R, z -0.18 | 22, win 18%, -0.503R, z -1.42 |
| US500m | CPI | fade first 15 min | 18, win 22%, -0.235R, z -0.51 | 22, win 55%, +0.293R, z +1.01 |
| US500m | CPI | follow first 30 min | 18, win 33%, -0.358R, z -0.94 | 22, win 27%, -0.264R, z -0.31 |
| US500m | CPI | break of release candle | 7, win 57%, +0.117R, z +0.57 | 5, win 20%, -0.139R, z +0.44 |
| US500m | CPI | buy 24 h before | 18, win 39%, +0.245R, z +1.32 | 22, win 41%, +0.143R, z +0.81 |
| US500m | NFP | follow first 15 min | 18, win 22%, -0.547R, z -1.32 | 21, win 38%, -0.273R, z -0.54 |
| US500m | NFP | fade first 15 min | 18, win 33%, -0.003R, z +0.42 | 21, win 48%, +0.270R, z +0.88 |
| US500m | NFP | follow first 30 min | 18, win 22%, -0.658R, z -1.75 | 21, win 38%, -0.133R, z +0.15 |
| US500m | NFP | break of release candle | 6, win 33%, -0.347R, z -0.36 | 12, win 33%, -0.297R, z -0.59 |
| US500m | NFP | buy 24 h before | 18, win 28%, -0.173R, z +0.22 | 22, win 27%, -0.194R, z -0.26 |
| USDCADm | FOMC | follow first 15 min | 12, win 58%, +0.175R, z +3.61 | 15, win 53%, +0.150R, z +3.27 |
| USDCADm | FOMC | fade first 15 min | 12, win 33%, -0.469R, z -2.21 | 15, win 40%, -0.366R, z -1.93 |
| USDCADm | FOMC | follow first 30 min | 12, win 58%, +0.212R, z +4.13 | 15, win 53%, +0.118R, z +2.93 |
| USDCADm | FOMC | break of release candle | 8, win 25%, -0.234R, z -0.27 | 14, win 57%, +0.101R, z +3.12 |
| USDCADm | FOMC | buy 24 h before | 12, win 25%, -0.502R, z -1.08 | 15, win 60%, +0.198R, z +1.04 |
| USDCADm | CPI | follow first 15 min | 18, win 33%, -0.046R, z +0.80 | 22, win 27%, -0.391R, z -0.68 |
| USDCADm | CPI | fade first 15 min | 18, win 28%, -0.324R, z -0.60 | 22, win 36%, -0.234R, z -0.36 |
| USDCADm | CPI | follow first 30 min | 18, win 44%, +0.106R, z +1.25 | 22, win 32%, -0.489R, z -1.38 |
| USDCADm | CPI | break of release candle | 8, win 75%, +1.088R, z +4.41 | 13, win 31%, -0.590R, z -1.77 |
| USDCADm | CPI | buy 24 h before | 18, win 22%, -0.515R, z -1.41 | 22, win 41%, -0.305R, z -0.22 |
| USDCADm | NFP | follow first 15 min | 18, win 44%, +0.116R, z +1.59 | 22, win 32%, -0.404R, z -0.67 |
| USDCADm | NFP | fade first 15 min | 18, win 39%, +0.178R, z +1.40 | 22, win 50%, +0.121R, z +1.47 |
| USDCADm | NFP | follow first 30 min | 18, win 67%, +0.635R, z +4.04 | 22, win 41%, -0.239R, z -0.21 |
| USDCADm | NFP | break of release candle | 11, win 55%, +0.327R, z +2.05 | 12, win 42%, -0.169R, z +0.39 |
| USDCADm | NFP | buy 24 h before | 18, win 11%, -0.860R, z -2.45 | 22, win 50%, +0.206R, z +1.87 |
| USDCADm | EIA | follow first 15 min | 63, win 35%, -0.250R, z -0.11 | 96, win 39%, -0.232R, z -1.13 |
| USDCADm | EIA | fade first 15 min | 63, win 38%, -0.098R, z +1.05 | 96, win 46%, -0.123R, z +1.44 |
| USDCADm | EIA | follow first 30 min | 63, win 40%, -0.189R, z +0.67 | 94, win 43%, -0.151R, z +0.44 |
| USDCADm | EIA | break of release candle | 48, win 44%, -0.149R, z +1.71 | 86, win 50%, -0.036R, z +1.88 |
| USDCADm | EIA | buy 24 h before | 63, win 32%, -0.226R, z -0.65 | 95, win 39%, -0.223R, z -0.34 |
| USDJPYm | FOMC | follow first 15 min | 12, win 58%, +0.747R, z +9.55 | 15, win 40%, -0.223R, z -0.68 |
| USDJPYm | FOMC | fade first 15 min | 12, win 17%, -0.760R, z -5.74 | 15, win 47%, +0.171R, z +3.02 |
| USDJPYm | FOMC | follow first 30 min | 12, win 58%, +0.779R, z +10.58 | 15, win 40%, -0.311R, z -1.55 |
| USDJPYm | FOMC | break of release candle | 8, win 50%, -0.035R, z +1.98 | 14, win 71%, +0.364R, z +5.61 |
| USDJPYm | FOMC | buy 24 h before | 12, win 17%, -0.590R, z -1.50 | 15, win 33%, -0.149R, z -0.01 |
| USDJPYm | CPI | follow first 15 min | 18, win 50%, +0.012R, z +0.90 | 22, win 41%, -0.068R, z +0.28 |
| USDJPYm | CPI | fade first 15 min | 18, win 33%, -0.374R, z -1.25 | 22, win 36%, -0.198R, z -0.71 |
| USDJPYm | CPI | follow first 30 min | 18, win 50%, +0.291R, z +2.52 | 22, win 27%, -0.355R, z -1.80 |
| USDJPYm | CPI | break of release candle | 8, win 38%, -0.109R, z +0.36 | 12, win 58%, -0.035R, z +0.61 |
| USDJPYm | CPI | buy 24 h before | 18, win 56%, -0.000R, z +0.39 | 22, win 55%, +0.372R, z +1.82 |
| USDJPYm | NFP | follow first 15 min | 18, win 28%, -0.256R, z -0.58 | 22, win 41%, -0.207R, z -0.60 |
| USDJPYm | NFP | fade first 15 min | 18, win 50%, +0.076R, z +1.15 | 22, win 41%, -0.099R, z -0.22 |
| USDJPYm | NFP | follow first 30 min | 18, win 28%, -0.294R, z -0.73 | 22, win 32%, -0.262R, z -1.26 |
| USDJPYm | NFP | break of release candle | 9, win 33%, -0.273R, z -0.38 | 11, win 27%, -0.463R, z -1.76 |
| USDJPYm | NFP | buy 24 h before | 18, win 11%, -0.804R, z -2.12 | 22, win 55%, +0.250R, z +1.13 |
| USOILm | FOMC | follow first 15 min | 36, win 33%, -0.241R, z -2.27 | 15, win 33%, -0.152R, z -1.01 |
| USOILm | FOMC | fade first 15 min | 36, win 47%, +0.025R, z +2.06 | 15, win 60%, +0.045R, z +1.06 |
| USOILm | FOMC | follow first 30 min | 36, win 28%, -0.150R, z -0.95 | 15, win 53%, -0.019R, z -0.12 |
| USOILm | FOMC | break of release candle | 19, win 47%, +0.067R, z +1.84 | 10, win 50%, +0.016R, z +0.78 |
| USOILm | FOMC | buy 24 h before | 36, win 47%, +0.173R, z +1.40 | 15, win 53%, +0.220R, z +0.70 |
| USOILm | CPI | follow first 15 min | 54, win 33%, -0.246R, z -0.87 | 21, win 52%, +0.139R, z +0.79 |
| USOILm | CPI | fade first 15 min | 54, win 44%, -0.070R, z -0.12 | 21, win 43%, -0.158R, z -0.53 |
| USOILm | CPI | follow first 30 min | 54, win 24%, -0.434R, z -2.39 | 21, win 57%, +0.192R, z +1.26 |
| USOILm | CPI | break of release candle | 44, win 25%, -0.497R, z -2.54 | 18, win 39%, +0.067R, z +0.63 |
| USOILm | CPI | buy 24 h before | 54, win 37%, +0.045R, z +0.69 | 21, win 38%, +0.123R, z +0.72 |
| USOILm | NFP | follow first 15 min | 52, win 42%, -0.081R, z +0.37 | 21, win 38%, -0.117R, z -0.46 |
| USOILm | NFP | fade first 15 min | 52, win 44%, -0.063R, z -0.06 | 21, win 43%, +0.027R, z +0.28 |
| USOILm | NFP | follow first 30 min | 52, win 38%, -0.122R, z -0.01 | 21, win 57%, +0.132R, z +1.16 |
| USOILm | NFP | break of release candle | 41, win 41%, -0.113R, z -0.13 | 19, win 58%, +0.080R, z +0.84 |
| USOILm | NFP | buy 24 h before | 53, win 36%, +0.114R, z +0.98 | 22, win 41%, +0.222R, z +1.14 |
| USOILm | EIA | follow first 15 min | 193, win 51%, -0.027R, z +1.08 | 96, win 42%, -0.067R, z -0.70 |
| USOILm | EIA | fade first 15 min | 193, win 36%, -0.198R, z -1.65 | 96, win 51%, +0.075R, z +1.94 |
| USOILm | EIA | follow first 30 min | 193, win 48%, -0.053R, z +0.65 | 96, win 43%, -0.091R, z -0.91 |
| USOILm | EIA | break of release candle | 127, win 39%, -0.119R, z -0.81 | 76, win 38%, -0.131R, z -0.75 |
| USOILm | EIA | buy 24 h before | 193, win 39%, -0.114R, z -0.23 | 94, win 36%, -0.165R, z -1.18 |
| USTECm | FOMC | follow first 15 min | 12, win 58%, +0.559R, z +3.84 | 15, win 33%, -0.391R, z -2.02 |
| USTECm | FOMC | fade first 15 min | 12, win 17%, -0.587R, z -3.02 | 15, win 27%, -0.449R, z -2.61 |
| USTECm | FOMC | follow first 30 min | 12, win 58%, +0.661R, z +4.45 | 15, win 33%, -0.380R, z -2.16 |
| USTECm | FOMC | break of release candle | 9, win 44%, +0.545R, z +3.08 | 14, win 14%, -0.565R, z -4.03 |
| USTECm | FOMC | buy 24 h before | 12, win 42%, +0.229R, z +0.97 | 15, win 60%, -0.012R, z +0.10 |
| USTECm | CPI | follow first 15 min | 18, win 22%, -0.267R, z -0.71 | 21, win 29%, -0.207R, z -0.31 |
| USTECm | CPI | fade first 15 min | 18, win 39%, +0.285R, z +1.19 | 21, win 52%, +0.004R, z -0.51 |
| USTECm | CPI | follow first 30 min | 18, win 17%, -0.559R, z -2.08 | 21, win 38%, -0.096R, z +0.09 |
| USTECm | CPI | break of release candle | 6, win 33%, -0.085R, z -0.27 | 5, win 40%, +0.197R, z +0.80 |
| USTECm | CPI | buy 24 h before | 18, win 28%, -0.129R, z +0.06 | 21, win 38%, +0.054R, z +0.26 |
| USTECm | NFP | follow first 15 min | 18, win 33%, -0.180R, z -0.35 | 21, win 24%, -0.303R, z -0.61 |
| USTECm | NFP | fade first 15 min | 18, win 44%, +0.251R, z +0.88 | 21, win 43%, +0.241R, z +0.44 |
| USTECm | NFP | follow first 30 min | 18, win 22%, -0.387R, z -1.20 | 21, win 33%, -0.163R, z -0.32 |
| USTECm | NFP | break of release candle | 6, win 0%, -0.872R, z -1.55 | 14, win 29%, -0.243R, z -0.51 |
| USTECm | NFP | buy 24 h before | 18, win 39%, -0.106R, z +0.32 | 22, win 32%, -0.005R, z +0.08 |
| XAGUSDm | FOMC | follow first 15 min | 12, win 33%, -0.261R, z -0.83 | 15, win 40%, -0.195R, z -0.80 |
| XAGUSDm | FOMC | fade first 15 min | 12, win 17%, -0.587R, z -4.21 | 15, win 53%, -0.175R, z -0.88 |
| XAGUSDm | FOMC | follow first 30 min | 12, win 25%, -0.398R, z -2.58 | 15, win 53%, -0.013R, z +0.73 |
| XAGUSDm | FOMC | break of release candle | 10, win 40%, +0.089R, z +3.33 | 14, win 36%, -0.162R, z -0.46 |
| XAGUSDm | FOMC | buy 24 h before | 12, win 42%, -0.196R, z -0.30 | 15, win 40%, -0.204R, z -0.64 |
| XAGUSDm | CPI | follow first 15 min | 18, win 50%, +0.639R, z +4.21 | 22, win 59%, +0.334R, z +2.09 |
| XAGUSDm | CPI | fade first 15 min | 18, win 22%, -0.491R, z -1.41 | 22, win 36%, -0.272R, z -1.06 |
| XAGUSDm | CPI | follow first 30 min | 18, win 50%, +0.437R, z +2.93 | 22, win 45%, +0.027R, z +0.79 |
| XAGUSDm | CPI | break of release candle | 8, win 75%, +1.022R, z +4.22 | 13, win 54%, +0.183R, z +1.15 |
| XAGUSDm | CPI | buy 24 h before | 18, win 28%, -0.589R, z -1.10 | 22, win 41%, -0.137R, z -0.04 |
| XAGUSDm | NFP | follow first 15 min | 18, win 33%, -0.132R, z +0.59 | 21, win 24%, -0.372R, z -1.48 |
| XAGUSDm | NFP | fade first 15 min | 18, win 33%, -0.007R, z +0.72 | 21, win 62%, +0.290R, z +1.95 |
| XAGUSDm | NFP | follow first 30 min | 18, win 33%, -0.108R, z +0.64 | 21, win 24%, -0.363R, z -1.53 |
| XAGUSDm | NFP | break of release candle | 11, win 36%, -0.135R, z +0.68 | 9, win 44%, +0.058R, z +0.38 |
| XAGUSDm | NFP | buy 24 h before | 18, win 28%, -0.298R, z -0.13 | 21, win 38%, -0.012R, z +0.43 |
| XAUUSDm | FOMC | follow first 15 min | 36, win 47%, +0.188R, z +5.57 | 15, win 40%, -0.025R, z +0.35 |
| XAUUSDm | FOMC | fade first 15 min | 36, win 42%, +0.092R, z +3.04 | 15, win 40%, -0.161R, z -1.49 |
| XAUUSDm | FOMC | follow first 30 min | 36, win 42%, +0.027R, z +2.23 | 15, win 53%, +0.434R, z +5.14 |
| XAUUSDm | FOMC | break of release candle | 28, win 43%, +0.077R, z +3.20 | 14, win 64%, +0.146R, z +2.01 |
| XAUUSDm | FOMC | buy 24 h before | 36, win 53%, +0.222R, z +0.78 | 15, win 20%, -0.289R, z -1.33 |
| XAUUSDm | CPI | follow first 15 min | 54, win 43%, -0.089R, z -0.22 | 21, win 33%, -0.365R, z -1.85 |
| XAUUSDm | CPI | fade first 15 min | 54, win 35%, -0.054R, z +0.12 | 21, win 43%, +0.011R, z +0.35 |
| XAUUSDm | CPI | follow first 30 min | 54, win 41%, -0.121R, z -0.23 | 21, win 43%, -0.005R, z +0.37 |
| XAUUSDm | CPI | break of release candle | 31, win 45%, -0.104R, z -0.29 | 10, win 60%, +0.078R, z +0.46 |
| XAUUSDm | CPI | buy 24 h before | 54, win 30%, -0.385R, z -2.14 | 21, win 38%, -0.233R, z -1.13 |
| XAUUSDm | NFP | follow first 15 min | 52, win 40%, -0.112R, z -0.33 | 21, win 43%, +0.075R, z +0.61 |
| XAUUSDm | NFP | fade first 15 min | 52, win 40%, +0.054R, z +0.93 | 21, win 48%, -0.004R, z +0.27 |
| XAUUSDm | NFP | follow first 30 min | 52, win 40%, -0.115R, z -0.07 | 21, win 43%, +0.216R, z +1.52 |
| XAUUSDm | NFP | break of release candle | 30, win 43%, -0.000R, z +0.47 | 7, win 57%, +0.422R, z +1.25 |
| XAUUSDm | NFP | buy 24 h before | 53, win 26%, -0.267R, z -1.29 | 21, win 48%, -0.180R, z -0.93 |
