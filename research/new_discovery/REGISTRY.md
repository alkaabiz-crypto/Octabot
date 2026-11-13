# Experiment registry

Every experiment, including failures, is listed. Full fields are in `REGISTRY.csv`. Effects are in bp per trade for trade rules, Sharpe differences for exposure rules, and QLIKE loss reductions for forecast tests (see each batch's RESULTS.md).

| ID | Batch | Name | Market | TF | Variants | TRAIN / VALID / TEST effect | TEST n | TEST p | BH | Decision | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D001-UKOILm/USOILm | 001 | Statistical-arbitrage pairs (spread z-score reversion) | UKOILm/USOILm | 1h | 1 | -10.06 / -8.4 / -5.23 | 47 | 0.2985 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D001-EURUSDm/GBPUSDm | 001 | Statistical-arbitrage pairs (spread z-score reversion) | EURUSDm/GBPUSDm | 1h | 1 | 6.44 / -1.12 / 3.04 | 46 | 0.0249 | False | REJECT | not positive in every period |
| D001-USTECm/US500m | 001 | Statistical-arbitrage pairs (spread z-score reversion) | USTECm/US500m | 1h | 1 | -12.92 / -1.81 / -4.26 | 46 | 0.6915 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D002-portfolio | 001 | Cross-market relative strength (risk-adjusted 60-day momentum) | portfolio | weekly | 1 | -40.91 / 11.73 / -18.77 | 64 | 0.7113 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-XAUUSDm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | XAUUSDm | 4h | 1 | -1.87 / -3.21 / 7.1 | 194 | 0.2208 | False | REJECT | not positive in every period |
| D003-USOILm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | USOILm | 4h | 1 | -10.61 / -2.95 / -30.45 | 222 | 0.96 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-UKOILm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | UKOILm | 4h | 1 | -26.89 / -29.75 / -37.43 | 194 | 0.9431 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-BTCUSDm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | BTCUSDm | 4h | 1 | 10.37 / -6.07 / 5.28 | 265 | 0.2308 | False | REJECT | not positive in every period |
| D003-ETHUSDm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | ETHUSDm | 4h | 1 | -6.96 / 23.84 / -10.29 | 242 | 0.5245 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-EURUSDm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | EURUSDm | 4h | 1 | -4.76 / -4.08 / -2.89 | 202 | 0.8212 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-GBPUSDm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | GBPUSDm | 4h | 1 | -7.54 / -4.16 / 0.24 | 183 | 0.1768 | False | REJECT | not positive in every period |
| D003-USDJPYm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | USDJPYm | 4h | 1 | -2.42 / -6.1 / -0.79 | 188 | 0.4386 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-US500m | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | US500m | 4h | 1 | -4.88 / 2.54 / -7.59 | 204 | 0.96 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-USTECm | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | USTECm | 4h | 1 | -6.66 / 4.89 / -15.04 | 189 | 0.988 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-DE30m | 001 | Regime-adaptive trend / mean reversion (efficiency ratio) | DE30m | 4h | 1 | 1.26 / 10.21 / -6.41 | 170 | 0.7682 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-XAUUSDm | 001 | Walk-forward logistic direction model (8 price features) | XAUUSDm | 1h | 1 | -3.73 / -0.37 / -1.26 | 611 | 0.5305 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-USOILm | 001 | Walk-forward logistic direction model (8 price features) | USOILm | 1h | 1 | -4.67 / -0.83 / 3.02 | 341 | 0.2048 | False | REJECT | not positive in every period |
| D004-UKOILm | 001 | Walk-forward logistic direction model (8 price features) | UKOILm | 1h | 1 | -22.79 / -25.68 / -12.32 | 304 | 0.3566 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-BTCUSDm | 001 | Walk-forward logistic direction model (8 price features) | BTCUSDm | 1h | 1 | -10.35 / -0.3 / -2.72 | 868 | 0.4256 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-ETHUSDm | 001 | Walk-forward logistic direction model (8 price features) | ETHUSDm | 1h | 1 | -18.13 / -7.48 / -12.05 | 1207 | 0.7652 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-EURUSDm | 001 | Walk-forward logistic direction model (8 price features) | EURUSDm | 1h | 1 | -1.06 / -1.64 / -0.04 | 214 | 0.0859 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-GBPUSDm | 001 | Walk-forward logistic direction model (8 price features) | GBPUSDm | 1h | 1 | -0.43 / -2.61 / 2.15 | 55 | 0.1868 | False | REJECT | not positive in every period |
| D004-USDJPYm | 001 | Walk-forward logistic direction model (8 price features) | USDJPYm | 1h | 1 | -0.68 / -0.53 / -0.41 | 784 | 0.2028 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-US500m | 001 | Walk-forward logistic direction model (8 price features) | US500m | 1h | 1 | -1.94 / -1.37 / -0.88 | 740 | 0.3497 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-USTECm | 001 | Walk-forward logistic direction model (8 price features) | USTECm | 1h | 1 | 0.44 / -1.5 / -1.18 | 779 | 0.5165 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-DE30m | 001 | Walk-forward logistic direction model (8 price features) | DE30m | 1h | 1 | -4.41 / -2.5 / -2.05 | 943 | 0.2188 | False | REJECT | not positive in every period; TEST mean <= 0 |
| E005-XAUUSDm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | XAUUSDm | 1d | 1 | -0.0258 / 0.264 / 0.4764 | 341 | 0.084 | False | REJECT | not positive in every period |
| E005-USOILm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | USOILm | 1d | 1 | -0.0139 / 0.1026 / 0.0481 | 251 | 0.4313 | False | REJECT | not positive in every period |
| E005-UKOILm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | UKOILm | 1d | 1 | -0.0639 / -0.0134 / -0.0438 | 338 | 0.5807 | False | REJECT | not positive in every period |
| E005-BTCUSDm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | BTCUSDm | 1d | 1 | -0.1327 / -0.1507 / -0.0298 | 493 | 0.6087 | False | REJECT | not positive in every period |
| E005-ETHUSDm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | ETHUSDm | 1d | 1 | 0.0329 / -0.1764 / -0.0802 | 495 | 0.6932 | False | REJECT | not positive in every period |
| E005-EURUSDm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | EURUSDm | 1d | 1 | -0.1148 / -0.1377 / -0.0714 | 352 | 0.6157 | False | REJECT | not positive in every period |
| E005-GBPUSDm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | GBPUSDm | 1d | 1 | -0.1693 / -0.0812 / -0.0601 | 354 | 0.6662 | False | REJECT | not positive in every period |
| E005-USDJPYm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | USDJPYm | 1d | 1 | 0.0369 / -0.2875 / -0.2773 | 354 | 0.9435 | False | REJECT | not positive in every period |
| E005-US500m | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | US500m | 1d | 1 | 0.0065 / -0.5279 / -0.6159 | 338 | 1.0 | False | REJECT | not positive in every period |
| E005-USTECm | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | USTECm | 1d | 1 | 0.1595 / -0.3396 / -0.3162 | 333 | 0.967 | False | REJECT | not positive in every period |
| E005-DE30m | 002 | Volatility-managed long exposure (EWMA 0.94, cap 2) | DE30m | 1d | 1 | 0.0129 / 0.0862 / -0.1817 | 291 | 0.9275 | False | REJECT | not positive in every period |
| E006-XAUUSDm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | XAUUSDm | 1d | 1 | 0.024 / 0.0943 / -0.0132 | 341 | 0.653 | False | REJECT | not positive in every period |
| E006-USOILm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | USOILm | 1d | 1 | 0.0141 / 0.0679 / -0.0467 | 251 | 0.6542 | False | REJECT | not positive in every period |
| E006-UKOILm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | UKOILm | 1d | 1 | -0.0018 / 0.0247 / 0.0711 | 338 | 0.0542 | False | REJECT | not positive in every period |
| E006-BTCUSDm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | BTCUSDm | 1d | 1 | 0.077 / 0.0471 / 0.0199 | 493 | 0.155 | False | WATCH | positive in all periods but not significant after correction |
| E006-ETHUSDm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | ETHUSDm | 1d | 1 | 0.049 / 0.038 / 0.054 | 495 | 0.0076 | False | WATCH | positive in all periods but not significant after correction |
| E006-EURUSDm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | EURUSDm | 1d | 1 | 0.007 / 0.0006 / 0.0026 | 352 | 0.4287 | False | WATCH | positive in all periods but not significant after correction |
| E006-GBPUSDm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | GBPUSDm | 1d | 1 | 0.0146 / 0.0144 / 0.003 | 354 | 0.3563 | False | WATCH | positive in all periods but not significant after correction |
| E006-USDJPYm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | USDJPYm | 1d | 1 | -0.001 / 0.1211 / 0.092 | 354 | 0.0677 | False | REJECT | not positive in every period |
| E006-US500m | 002 | HAR-RV vs EWMA next-day variance forecast (component) | US500m | 1d | 1 | 0.0295 / 0.2169 / 0.062 | 338 | 0.0048 | False | WATCH | positive in all periods but not significant after correction |
| E006-USTECm | 002 | HAR-RV vs EWMA next-day variance forecast (component) | USTECm | 1d | 1 | 0.0732 / 0.1562 / 0.022 | 333 | 0.113 | False | WATCH | positive in all periods but not significant after correction |
| E006-DE30m | 002 | HAR-RV vs EWMA next-day variance forecast (component) | DE30m | 1d | 1 | -0.0282 / 0.118 / 0.0974 | 291 | 0.0 | True | REJECT | not positive in every period |
| E007-XAUUSDm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | XAUUSDm | 1d | 1 | -0.785 / -0.6313 / -0.935 | 341 | 0.8971 | False | REJECT | not positive in every period |
| E007-USOILm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | USOILm | 1d | 1 |  /  / 0.8156 | 251 | 0.072 | False | REJECT | no exposure in some period (HMM needs 250 days, or stayed flat) |
| E007-UKOILm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | UKOILm | 1d | 1 | -0.3441 / -0.0167 / -0.5943 | 338 | 0.8051 | False | REJECT | not positive in every period |
| E007-BTCUSDm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | BTCUSDm | 1d | 1 | -0.339 / -0.1182 / 0.068 | 493 | 0.4393 | False | REJECT | not positive in every period |
| E007-ETHUSDm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | ETHUSDm | 1d | 1 | -0.5372 / 0.2187 / -0.5034 | 495 | 0.8706 | False | REJECT | not positive in every period |
| E007-EURUSDm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | EURUSDm | 1d | 1 | -1.3806 / -1.0405 / 0.3175 | 352 | 0.3963 | False | REJECT | not positive in every period |
| E007-GBPUSDm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | GBPUSDm | 1d | 1 | -0.8675 / 0.3576 / -0.1187 | 354 | 0.4578 | False | REJECT | not positive in every period |
| E007-USDJPYm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | USDJPYm | 1d | 1 | 0.9263 / 0.3311 / 0.0395 | 354 | 0.4688 | False | WATCH | positive in all periods but not significant after correction |
| E007-US500m | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | US500m | 1d | 1 |  / -0.8115 / -0.1722 | 338 | 0.8756 | False | REJECT | no exposure in some period (HMM needs 250 days, or stayed flat) |
| E007-USTECm | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | USTECm | 1d | 1 |  /  / 0.4113 | 333 | 0.3203 | False | REJECT | no exposure in some period (HMM needs 250 days, or stayed flat) |
| E007-DE30m | 002 | Two-state Gaussian HMM regime filter (long if P(bull)>0.5) | DE30m | 1d | 1 |  / 0.5645 / 0.0264 | 291 | 0.4518 | False | REJECT | no exposure in some period (HMM needs 250 days, or stayed flat) |
| E008-BTCUSDm->ETHUSDm | 002 | Crypto lead-lag: trade the laggard after a 2-sigma 15m move of the leader | BTCUSDm->ETHUSDm | 15m | 1 | -15.8681 / -18.4985 / -7.0321 | 128 | 0.3067 | False | REJECT | not positive in every period |
| E008-ETHUSDm->BTCUSDm | 002 | Crypto lead-lag: trade the laggard after a 2-sigma 15m move of the leader | ETHUSDm->BTCUSDm | 15m | 1 | -11.7714 / -6.8878 / -3.407 | 939 | 0.4525 | False | REJECT | not positive in every period |
| E009-US500m | 002 | Pre-holiday effect, close to close | US500m | 1d | 1 | 7.3362 / 14.0144 / 3.4976 | 13 | 0.5275 | False | WATCH | positive in all periods but not significant after correction; too few TEST trades |
| E009-USTECm | 002 | Pre-holiday effect, close to close | USTECm | 1d | 1 | 13.0521 / 18.6289 / 9.0397 | 12 | 0.4965 | False | WATCH | positive in all periods but not significant after correction; too few TEST trades |
| E009-DE30m | 002 | Pre-holiday effect, close to close | DE30m | 1d | 1 | 2.9679 / -42.1854 / 47.974 | 5 | 0.1109 | False | REJECT | not positive in every period |
| B003-H1-R1-XAUUSDm | 003 | Round-number rejection fade (Osler) | XAUUSDm | 15m | 1 | -2.4454 / -1.4848 / -1.4958 | 2019 | 0.705 | False | REJECT | not positive in every period |
| B003-H1-R2-XAUUSDm | 003 | Round-number crossing follow (Osler) | XAUUSDm | 15m | 1 | -1.2883 / -0.6035 / -0.0269 | 2798 | 0.052 | False | REJECT | not positive in every period |
| B003-H1-R1-USOILm | 003 | Round-number rejection fade (Osler) | USOILm | 15m | 1 | -7.4821 / -8.4051 / -0.9065 | 872 | 0.009 | False | REJECT | not positive in every period |
| B003-H1-R2-USOILm | 003 | Round-number crossing follow (Osler) | USOILm | 15m | 1 | -10.1293 / -3.9398 / -11.4088 | 1460 | 0.996 | False | REJECT | not positive in every period |
| B003-H1-R1-EURUSDm | 003 | Round-number rejection fade (Osler) | EURUSDm | 15m | 1 | -0.6466 / -2.0226 / -0.0962 | 179 | 0.018 | False | REJECT | not positive in every period |
| B003-H1-R2-EURUSDm | 003 | Round-number crossing follow (Osler) | EURUSDm | 15m | 1 | -0.6801 / -3.3294 / -1.3994 | 360 | 0.58 | False | REJECT | not positive in every period |
| B003-H1-R1-USDJPYm | 003 | Round-number rejection fade (Osler) | USDJPYm | 15m | 1 | -2.5672 / -1.2373 / -2.1843 | 296 | 0.946 | False | REJECT | not positive in every period |
| B003-H1-R2-USDJPYm | 003 | Round-number crossing follow (Osler) | USDJPYm | 15m | 1 | -0.8296 / -2.3149 / -1.1354 | 575 | 0.36 | False | REJECT | not positive in every period |
| B003-H1-R1-US500m | 003 | Round-number rejection fade (Osler) | US500m | 15m | 1 | -3.5646 / -1.9324 / -2.5415 | 448 | 0.914 | False | REJECT | not positive in every period |
| B003-H1-R2-US500m | 003 | Round-number crossing follow (Osler) | US500m | 15m | 1 | -2.715 / -2.983 / -1.5017 | 883 | 0.536 | False | REJECT | not positive in every period |
| B003-H1-R1-BTCUSDm | 003 | Round-number rejection fade (Osler) | BTCUSDm | 15m | 1 | -14.4051 / -5.6644 / -6.8507 | 1128 | 0.862 | False | REJECT | not positive in every period |
| B003-H1-R2-BTCUSDm | 003 | Round-number crossing follow (Osler) | BTCUSDm | 15m | 1 | -14.3044 / -9.0661 / -6.3108 | 1905 | 0.825 | False | REJECT | not positive in every period |
| B003-H2-XAUUSDm | 003 | London metal fix short (gold PM 15:00, silver 12:00) | XAUUSDm | 15m | 1 | -1.7764 / -0.5434 / 0.4779 | 352 | 0.138 | False | REJECT | not positive in every period |
| B003-H2-XAGUSDm | 003 | London metal fix short (gold PM 15:00, silver 12:00) | XAGUSDm | 15m | 1 | -21.7517 / -20.0131 / -11.3006 | 353 | 0.396 | False | REJECT | not positive in every period |
| B003-H3-BTCUSDm | 003 | BTC CME weekend gap fill (popular theory) | BTCUSDm | 15m | 1 | -83.2609 / -61.6743 / -49.3198 | 29 | 0.8422 | False | REJECT | not positive in every period |
| B003-H4-BTCUSDm | 003 | Coinbase premium z >= 2 -> follow 24 h | BTCUSDm | 1h signal / 15m execution | 1 | 5.6454 / 41.0932 / 37.2128 | 135 | 0.011 | False | WATCH | positive in every period incl. EARLY but not significant after BH |
