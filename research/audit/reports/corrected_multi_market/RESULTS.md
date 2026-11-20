# Results: which indicators fit which markets

33 markets, 96930 market-variant pairs. Discovery 2023-07 to 2024-12; confirmation 2025-01 to the latest candle. Primary cost unless noted.

## Headline

- Per-market picks confirmed: **1 of 91** (raw p ≤ 0.05 in confirmation: 7, about 5 expected by luck).
- Per-class picks confirmed: **0 of 20**.
- Whole-sample check: 567 of 85748 pairs significant after BH (raw p ≤ 0.05: 5175, about 4287 expected by luck).

## Per-class picks (fitted on discovery, tested on 2025 to now)

| Class | Variant | Discovery z | Confirmation z | p | Markets positive in confirmation | Mean E in confirmation | Confirmed |
|---|---|---|---|---|---|---|---|
| forex | BOLLINGER_PCT_B + ADX>20 filter SELL, target ½ stop | +3.72 | +0.69 | 0.245 | 0/10 | -0.103R | no |
| forex | HMA_9 + ADX>20 filter SELL, target ½ stop | +3.63 | -1.01 | 0.843 | 0/10 | -0.116R | no |
| forex | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter SELL, target ½ stop | +3.39 | +0.72 | 0.237 | 0/10 | -0.103R | no |
| forex | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter SELL, hold to opposite signal | +3.21 | +1.09 | 0.137 | 2/10 | -0.080R | no |
| forex | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter SELL, ±1R | +3.07 | +1.14 | 0.128 | 1/10 | -0.099R | no |
| indices | QQE_MOD BUY, target ½ stop | +5.38 | +0.24 | 0.407 | 2/10 | -0.090R | no |
| indices | HMA_9 + daily EMA200 filter SELL, target ½ stop | +5.26 | +0.52 | 0.300 | 3/9 | -0.061R | no |
| indices | TRUE_STRENGTH_25_13_13 BUY, target ½ stop | +5.15 | -0.28 | 0.608 | 1/10 | -0.097R | no |
| indices | QQE_MOD + session VWAP filter BUY, target ½ stop | +5.07 | -0.04 | 0.516 | 2/10 | -0.092R | no |
| indices | WADDAH_ATTAR_ORIGINAL BUY, target ½ stop | +4.75 | +0.09 | 0.463 | 2/10 | -0.090R | no |
| crypto | RANGE_FILTER BUY, ±1R | +5.42 | +3.26 | 0.001 | 1/7 | -0.789R | no |
| crypto | KELTNER_CHANNELS BUY, strategy's own exits | +5.27 | -0.06 | 0.526 | 2/7 | -0.705R | no |
| crypto | RANGE_FILTER BUY, target ½ stop | +5.01 | +2.96 | 0.002 | 0/7 | -0.801R | no |
| crypto | VOLATILITY_EXPANSION_CLOSE + session VWAP filter BUY, strategy's own exits | +4.58 | +3.19 | 0.001 | 1/7 | -0.772R | no |
| crypto | PIVOT_REVERSAL BUY, strategy's own exits | +4.56 | +4.11 | 0.000 | 2/7 | -0.742R | no |
| commodities | KLINGER_34_55_13 + ADX>20 filter SELL, target ½ stop | +4.21 | -0.16 | 0.565 | 0/5 | -0.265R | no |
| commodities | TEMA_9 + ADX>20 filter SELL, target ½ stop | +4.03 | -0.27 | 0.608 | 0/5 | -0.274R | no |
| commodities | TEMA_9 + ADX>20 filter SELL, trailing stop | +3.99 | +0.75 | 0.227 | 0/5 | -0.299R | no |
| commodities | HMA_9 + ADX>20 filter SELL, trailing stop | +3.56 | +0.99 | 0.162 | 0/5 | -0.296R | no |
| commodities | ACCUM_DIST_VS_SMA20 + ADX>20 filter SELL, target ½ stop | +3.49 | -0.78 | 0.783 | 0/5 | -0.270R | no |

## Per-market picks

| Class | Market | Variant | Discovery: trades, win, E, z | Confirmation: trades, win, E, E stress, z, p | Confirmed |
|---|---|---|---|---|---|
| forex | AUDUSDm | CONNORS_RSI_3_2_100 + ADX>20 filter SELL, trailing stop | 112, 37%, +0.339R, +4.04 | 134, 25%, -0.243R, -0.365R, -0.47, 0.682 | no |
| forex | AUDUSDm | BIGBELUGA_SESSION_VWAP + ADX>20 filter SELL, target ½ stop | 111, 74%, +0.109R, +3.84 | 158, 55%, -0.170R, -0.232R, -1.60, 0.946 | no |
| forex | AUDUSDm | CONNORS_RSI_3_2_100 SELL, trailing stop | 160, 37%, +0.239R, +3.79 | 181, 27%, -0.252R, -0.372R, -1.09, 0.862 | no |
| forex | AUDUSDm | HALFTREND + ADX>20 filter BUY, ±1R | 125, 57%, +0.141R, +3.57 | 169, 47%, -0.069R, -0.153R, +0.52, 0.303 | no |
| forex | AUDUSDm | WILLIAMS_ALLIGATOR + ADX>20 filter BUY, trailing stop | 118, 38%, +0.169R, +3.25 | 133, 35%, +0.022R, -0.118R, +0.83, 0.204 | no |
| forex | EURJPYm | CHANDE_MOMENTUM_9 + daily EMA200 filter SELL, target ½ stop | 107, 71%, +0.100R, +2.54 | 120, 62%, -0.030R, -0.071R, +0.33, 0.369 | no |
| forex | EURJPYm | ROC_9 + daily EMA200 filter SELL, target ½ stop | 107, 71%, +0.100R, +2.54 | 120, 62%, -0.030R, -0.071R, +0.33, 0.369 | no |
| forex | EURJPYm | SUPERTREND_KIVANC BUY, target ½ stop | 114, 70%, +0.064R, +2.44 | 155, 63%, -0.018R, -0.103R, +1.05, 0.146 | no |
| forex | EURJPYm | CHANDE_MOMENTUM_9 + 4H EMA200 filter SELL, target ½ stop | 139, 68%, +0.051R, +2.11 | 190, 59%, -0.091R, -0.157R, +0.28, 0.389 | no |
| forex | EURJPYm | ROC_9 + 4H EMA200 filter SELL, target ½ stop | 139, 68%, +0.051R, +2.11 | 190, 59%, -0.091R, -0.157R, +0.28, 0.389 | no |
| forex | EURUSDm | LINREG_CHANNEL_100_2 + ADX>20 filter SELL, ±1R | 103, 55%, +0.133R, +2.72 | 145, 50%, -0.010R, -0.079R, +0.40, 0.345 | no |
| forex | EURUSDm | CCI_20 + session VWAP filter BUY, ±1R | 101, 56%, +0.104R, +2.40 | 152, 47%, -0.056R, -0.128R, +0.68, 0.248 | no |
| forex | EURUSDm | LORENTZIAN_V6 + session VWAP filter SELL, 4-bar hold | 114, 39%, +0.055R, +1.59 | 132, 42%, -0.007R, -0.062R, +0.87, 0.193 | no |
| forex | GBPJPYm | DEMA_9 + daily EMA200 filter SELL, target ½ stop | 116, 68%, +0.068R, +2.48 | 223, 60%, -0.072R, -0.108R, -0.39, 0.651 | no |
| forex | GBPJPYm | KST + daily EMA200 filter BUY, ±1R | 171, 54%, +0.091R, +2.47 | 227, 48%, -0.039R, -0.139R, +1.10, 0.136 | no |
| forex | GBPJPYm | DPO_21 + session VWAP filter BUY, trailing stop | 150, 40%, +0.231R, +2.42 | 189, 34%, +0.036R, -0.104R, +1.49, 0.068 | no |
| forex | GBPJPYm | OUTSIDE_BAR BUY, strategy's own exits | 252, 46%, +0.157R, +2.37 | 323, 39%, +0.028R, -0.095R, +1.09, 0.138 | no |
| forex | GBPJPYm | SMA_9 + session VWAP filter BUY, trailing stop | 202, 40%, +0.164R, +2.35 | 255, 32%, -0.079R, -0.216R, -0.37, 0.643 | no |
| forex | GBPUSDm | CHAIKIN_OSC_3_10 + 4H EMA200 filter BUY, trailing stop | 134, 32%, +0.168R, +1.44 | 203, 26%, -0.095R, -0.226R, -1.34, 0.911 | no |
| forex | GBPUSDm | WOODIES_CCI_14 + 4H EMA200 filter BUY, trailing stop | 137, 32%, +0.161R, +1.26 | 203, 22%, -0.170R, -0.298R, -2.70, 0.997 | no |
| forex | GBPUSDm | INSIDE_BAR + 4H EMA200 filter SELL, strategy's own exits | 158, 46%, +0.138R, +0.75 | 155, 41%, -0.147R, -0.248R, -0.94, 0.827 | no |
| forex | NZDUSDm | NVI_VS_EMA255 SELL, hold to opposite signal | 109, 38%, +0.251R, +1.72 | 152, 23%, -0.257R, -0.474R, -0.88, 0.810 | no |
| forex | USDCADm | VOLATILITY_STOP_20_2 + ADX>20 filter BUY, hold to opposite signal | 135, 39%, +0.214R, +1.56 | 186, 32%, -0.112R, -0.302R, -0.15, 0.559 | no |
| forex | USDCADm | STOCHASTIC_SLOW BUY, strategy's own exits | 102, 68%, +0.385R, +1.33 | 121, 56%, -0.220R, -0.618R, -0.48, 0.683 | no |
| forex | USDCHFm | WILLIAMS_ALLIGATOR + ADX>20 filter SELL, hold to opposite signal | 134, 37%, +0.155R, +2.17 | 163, 29%, -0.212R, -0.339R, -1.23, 0.892 | no |
| forex | USDCHFm | BBTREND_20_50 + 4H EMA200 filter SELL, hold to opposite signal | 110, 41%, +0.178R, +1.06 | 184, 41%, -0.035R, -0.166R, -0.29, 0.615 | no |
| forex | USDCHFm | PIVOT_REVERSAL + 4H EMA200 filter SELL, strategy's own exits | 104, 31%, +0.223R, +0.63 | 160, 24%, -0.092R, -0.250R, -0.73, 0.766 | no |
| forex | USDJPYm | CORAL_TREND SELL, hold to opposite signal | 202, 32%, +0.148R, +3.25 | 275, 28%, +0.014R, -0.097R, +1.09, 0.138 | no |
| forex | USDJPYm | RELATIVE_VOLATILITY_10 + session VWAP filter SELL, hold to opposite signal | 363, 22%, +0.051R, +3.02 | 535, 19%, -0.070R, -0.106R, -0.51, 0.695 | no |
| forex | USDJPYm | ACCUM_DIST_VS_SMA20 + 4H EMA200 filter SELL, target ½ stop | 129, 74%, +0.133R, +2.98 | 187, 57%, -0.114R, -0.138R, -1.95, 0.975 | no |
| forex | USDJPYm | CHAIKIN_MONEY_FLOW_20 BUY, hold to opposite signal | 369, 33%, +0.119R, +2.96 | 489, 36%, +0.030R, -0.067R, +1.63, 0.052 | no |
| forex | USDJPYm | ACCUM_DIST_VS_SMA20 BUY, hold to opposite signal | 485, 32%, +0.097R, +2.94 | 654, 30%, +0.007R, -0.071R, +1.66, 0.048 | no |
| indices | DE30m | PIVOT_REVERSAL + session VWAP filter SELL, strategy's own exits | 153, 35%, +0.186R, +3.47 | 207, 33%, +0.004R, -0.065R, +1.10, 0.135 | no |
| indices | DE30m | VWMA_20 BUY, ±1R | 284, 58%, +0.115R, +3.46 | 389, 49%, -0.037R, -0.070R, -0.30, 0.618 | no |
| indices | DE30m | WADDAH_ATTAR_ORIGINAL + session VWAP filter BUY, ±1R | 337, 57%, +0.104R, +3.37 | 448, 50%, -0.012R, -0.045R, +0.23, 0.408 | no |
| indices | DE30m | WOODIES_CCI_14 + daily EMA200 filter BUY, target ½ stop | 269, 71%, +0.050R, +3.28 | 446, 64%, -0.035R, -0.064R, -0.35, 0.638 | no |
| indices | DE30m | WADDAH_ATTAR_ORIGINAL BUY, ±1R | 347, 56%, +0.095R, +3.28 | 457, 50%, -0.010R, -0.042R, +0.33, 0.371 | no |
| indices | FR40m | TRUE_STRENGTH_25_13_13 + ADX>20 filter SELL, hold to opposite signal | 153, 41%, +0.236R, +3.12 | 183, 29%, -0.220R, -0.343R, -0.16, 0.565 | no |
| indices | FR40m | PRICE_MOMENTUM_OSC_35_20_10 + ADX>20 filter SELL, hold to opposite signal | 144, 35%, +0.158R, +2.55 | 168, 29%, -0.327R, -0.455R, -1.21, 0.887 | no |
| indices | FR40m | DMI_14 + ADX>20 filter SELL, hold to opposite signal | 138, 30%, +0.136R, +2.51 | 155, 24%, -0.225R, -0.335R, -0.45, 0.674 | no |
| indices | JP225m | PARABOLIC_SAR BUY, strategy's own exits | 382, 41%, +0.091R, +3.32 | 497, 41%, +0.061R, +0.024R, +0.92, 0.179 | no |
| indices | JP225m | PARABOLIC_SAR + session VWAP filter BUY, strategy's own exits | 246, 43%, +0.163R, +3.05 | 323, 41%, +0.050R, +0.014R, +0.33, 0.372 | no |
| indices | JP225m | PRICE_MOMENTUM_OSC_35_20_10 + 4H EMA200 filter BUY, target ½ stop | 142, 74%, +0.098R, +2.94 | 173, 71%, +0.060R, +0.029R, +1.84, 0.033 | no |
| indices | JP225m | PRICE_MOMENTUM_OSC_35_20_10 BUY, target ½ stop | 236, 70%, +0.039R, +2.90 | 276, 69%, +0.034R, +0.008R, +1.81, 0.035 | no |
| indices | JP225m | PRICE_MOMENTUM_OSC_35_20_10 + daily EMA200 filter BUY, target ½ stop | 187, 72%, +0.068R, +2.64 | 230, 69%, +0.034R, +0.008R, +1.15, 0.125 | no |
| indices | US30m | WILLIAMS_PCT_R_14 + 4H EMA200 filter SELL, target ½ stop | 114, 72%, +0.091R, +3.11 | 137, 57%, -0.109R, -0.116R, -1.39, 0.918 | no |
| indices | US30m | QQE_MOD + daily EMA200 filter BUY, target ½ stop | 235, 71%, +0.063R, +2.77 | 298, 71%, +0.076R, +0.045R, +2.22, 0.013 | no |
| indices | US30m | LSMA_25 + 4H EMA200 filter BUY, ±1R | 306, 57%, +0.123R, +2.62 | 346, 51%, +0.013R, -0.031R, -0.24, 0.595 | no |
| indices | US30m | LSMA_25 + daily EMA200 filter BUY, ±1R | 349, 55%, +0.092R, +2.33 | 442, 52%, +0.033R, -0.005R, +0.56, 0.286 | no |
| indices | US30m | CONNORS_RSI_3_2_100 + ADX>20 filter BUY, ±1R | 107, 58%, +0.150R, +2.23 | 157, 52%, +0.038R, +0.009R, +0.27, 0.392 | no |
| indices | US500m | KST + ADX>20 filter BUY, trailing stop | 136, 38%, +0.312R, +2.18 | 182, 32%, -0.028R, -0.097R, -0.27, 0.606 | no |
| indices | US500m | KST + session VWAP filter BUY, trailing stop | 152, 39%, +0.301R, +2.11 | 218, 34%, -0.020R, -0.095R, -0.06, 0.523 | no |
| indices | US500m | INSIDE_BAR + ADX>20 filter BUY, strategy's own exits | 218, 48%, +0.169R, +1.85 | 300, 50%, +0.032R, -0.034R, -0.01, 0.503 | no |
| indices | US500m | RANGE_FILTER BUY, ±1R | 133, 53%, +0.048R, +1.56 | 167, 54%, +0.058R, +0.027R, +1.45, 0.073 | no |
| indices | US500m | PIVOT_REVERSAL BUY, strategy's own exits | 249, 41%, +0.148R, +1.52 | 293, 37%, -0.005R, -0.088R, -0.58, 0.719 | no |
| indices | USTECm | PIVOT_REVERSAL BUY, strategy's own exits | 239, 39%, +0.297R, +2.73 | 288, 41%, +0.048R, -0.013R, -0.24, 0.594 | no |
| indices | USTECm | TRUE_STRENGTH_25_13_13 + session VWAP filter SELL, hold to opposite signal | 217, 36%, +0.085R, +2.69 | 302, 31%, -0.059R, -0.112R, +0.46, 0.322 | no |
| indices | USTECm | MOMENTUM_10 + session VWAP filter BUY, hold to opposite signal | 526, 30%, +0.086R, +2.69 | 583, 33%, -0.023R, -0.058R, -0.98, 0.836 | no |
| indices | USTECm | KST + session VWAP filter BUY, ±1R | 179, 57%, +0.115R, +2.62 | 232, 54%, +0.050R, +0.015R, +1.55, 0.061 | no |
| indices | USTECm | KST + ADX>20 filter BUY, ±1R | 156, 58%, +0.133R, +2.60 | 194, 52%, +0.001R, -0.030R, +0.72, 0.237 | no |
| crypto | BNBUSDm | AWESOME_OSC + ADX>20 filter BUY, hold to opposite signal | 106, 25%, +0.289R, +3.54 | 93, 27%, -0.389R, -0.653R, -0.28, 0.609 | no |
| crypto | BNBUSDm | SUPERTREND BUY, strategy's own exits | 111, 32%, +0.361R, +3.18 | 108, 31%, -0.299R, -0.574R, +0.09, 0.466 | no |
| crypto | BTCUSDm (seen in earlier rounds) | AWESOME_OSC BUY, ±1R | 251, 57%, +0.112R, +2.72 | 303, 49%, -0.027R, -0.057R, -0.24, 0.594 | no |
| crypto | BTCUSDm (seen in earlier rounds) | EASE_OF_MOVEMENT_14 BUY, hold to opposite signal | 652, 32%, +0.098R, +2.68 | 821, 32%, -0.015R, -0.044R, +0.45, 0.325 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND + ADX>20 filter BUY, ±1R | 163, 59%, +0.154R, +2.47 | 217, 47%, -0.086R, -0.113R, -1.10, 0.864 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND BUY, ±1R | 277, 55%, +0.083R, +2.36 | 337, 48%, -0.047R, -0.075R, -0.58, 0.721 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND BUY, trailing stop | 261, 38%, +0.343R, +2.31 | 324, 32%, +0.044R, +0.008R, +0.46, 0.322 | no |
| crypto | ETHUSDm | PRICE_MOMENTUM_OSC_35_20_10 + ADX>20 filter SELL, ±1R | 211, 55%, +0.085R, +3.23 | 274, 55%, +0.081R, +0.044R, +2.94, 0.002 | no |
| crypto | ETHUSDm | BOLLINGER_PCT_B + daily EMA200 filter SELL, target ½ stop | 100, 73%, +0.077R, +2.68 | 248, 65%, -0.024R, -0.062R, +0.53, 0.297 | no |
| crypto | ETHUSDm | CORAL_TREND + ADX>20 filter SELL, ±1R | 163, 54%, +0.054R, +2.28 | 216, 50%, -0.023R, -0.060R, +0.63, 0.265 | no |
| crypto | ETHUSDm | PIVOT_REVERSAL BUY, strategy's own exits | 337, 34%, +0.086R, +1.97 | 404, 35%, +0.164R, +0.118R, +3.18, 0.001 | **yes** |
| crypto | ETHUSDm | PRICE_MOMENTUM_OSC_35_20_10 + session VWAP filter SELL, ±1R | 127, 54%, +0.065R, +1.96 | 228, 52%, +0.019R, -0.019R, +1.44, 0.076 | no |
| crypto | SOLUSDm | PRICE_OSC_12_26 + session VWAP filter BUY, hold to opposite signal | 113, 32%, +0.350R, +2.15 | 101, 21%, -0.418R, -0.773R, +0.74, 0.229 | no |
| crypto | XRPUSDm | PRICE_CHANNEL BUY, strategy's own exits | 207, 31%, +0.432R, +2.73 | 242, 29%, -0.107R, -0.405R, +3.13, 0.001 | no |
| crypto | XRPUSDm | PRICE_CHANNEL + session VWAP filter BUY, strategy's own exits | 147, 30%, +0.528R, +2.29 | 98, 28%, -0.536R, -0.832R, -0.32, 0.627 | no |
| crypto | XRPUSDm | PRICE_OSC_12_26 + ADX>20 filter BUY, hold to opposite signal | 136, 25%, +0.323R, +1.55 | 108, 22%, -0.575R, -0.865R, -0.63, 0.736 | no |
| crypto | XRPUSDm | PRICE_CHANNEL + daily EMA200 filter BUY, strategy's own exits | 103, 29%, +0.456R, +1.51 | 115, 33%, -0.088R, -0.383R, +0.91, 0.182 | no |
| crypto | XRPUSDm | TRIX_18 BUY, hold to opposite signal | 141, 28%, +0.366R, +1.20 | 164, 20%, -0.252R, -0.555R, +0.94, 0.173 | no |
| commodities | UKOILm | BBTREND_20_50 + ADX>20 filter SELL, hold to opposite signal | 105, 45%, +0.175R, +2.57 | 178, 47%, -0.201R, -0.338R, +0.14, 0.444 | no |
| commodities | USOILm (seen in earlier rounds) | BULL_BEAR_POWER_13 + ADX>20 filter SELL, target ½ stop | 255, 71%, +0.062R, +3.23 | 337, 64%, -0.044R, -0.071R, +0.32, 0.373 | no |
| commodities | USOILm (seen in earlier rounds) | WOODIES_CCI_14 + ADX>20 filter SELL, target ½ stop | 250, 71%, +0.055R, +2.90 | 335, 64%, -0.043R, -0.070R, +0.33, 0.372 | no |
| commodities | USOILm (seen in earlier rounds) | BIGBELUGA_SESSION_VWAP SELL, trailing stop | 174, 34%, +0.124R, +2.90 | 207, 29%, -0.048R, -0.089R, +0.52, 0.300 | no |
| commodities | USOILm (seen in earlier rounds) | WOODIES_CCI_14 + 4H EMA200 filter SELL, target ½ stop | 187, 72%, +0.081R, +2.74 | 239, 59%, -0.121R, -0.152R, -1.68, 0.954 | no |
| commodities | USOILm (seen in earlier rounds) | RANGE_FILTER + session VWAP filter BUY, target ½ stop | 127, 72%, +0.092R, +2.70 | 168, 70%, +0.039R, +0.013R, +1.01, 0.157 | no |
| commodities | XAGUSDm | RANGE_FILTER + session VWAP filter BUY, hold to opposite signal | 119, 37%, +0.112R, +0.89 | 157, 38%, +0.160R, +0.082R, +0.01, 0.494 | no |
| commodities | XAGUSDm | RANGE_FILTER BUY, hold to opposite signal | 120, 37%, +0.106R, +0.82 | 161, 38%, +0.145R, +0.069R, +0.04, 0.485 | no |
| commodities | XAUUSDm (seen in earlier rounds) | INSIDE_BAR BUY, strategy's own exits | 366, 50%, +0.202R, +2.62 | 441, 50%, +0.085R, +0.056R, -0.17, 0.568 | no |
| commodities | XAUUSDm (seen in earlier rounds) | HMA_9 + session VWAP filter BUY, trailing stop | 250, 38%, +0.278R, +2.56 | 290, 36%, +0.235R, +0.187R, +0.65, 0.257 | no |
| commodities | XAUUSDm (seen in earlier rounds) | INSIDE_BAR + session VWAP filter SELL, strategy's own exits | 184, 48%, +0.076R, +2.55 | 228, 46%, -0.013R, -0.039R, +1.15, 0.126 | no |
| commodities | XAUUSDm (seen in earlier rounds) | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter BUY, hold to opposite signal | 218, 41%, +0.262R, +2.40 | 335, 37%, +0.092R, +0.067R, +0.80, 0.212 | no |
| commodities | XAUUSDm (seen in earlier rounds) | BBTREND_20_50 BUY, hold to opposite signal | 217, 50%, +0.318R, +2.39 | 257, 48%, +0.192R, +0.146R, +0.77, 0.221 | no |

## Markets

| Market | Class | Data from | Data to |
|---|---|---|---|
| AUDUSDm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| EURGBPm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| EURJPYm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| EURUSDm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| GBPJPYm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| GBPUSDm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| NZDUSDm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| USDCADm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| USDCHFm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| USDJPYm | forex | 2023-01-01 22:00 | 2026-11-10 23:00 |
| AUS200m | indices | 2023-01-02 23:00 | 2026-11-10 23:00 |
| DE30m | indices | 2023-01-02 00:00 | 2026-11-10 23:00 |
| FR40m | indices | 2023-01-02 07:00 | 2026-11-10 23:00 |
| HK50m | indices | 2023-01-03 01:00 | 2026-11-10 23:00 |
| JP225m | indices | 2023-01-03 00:00 | 2026-11-10 23:00 |
| STOXX50m | indices | 2023-01-02 00:00 | 2026-11-10 23:00 |
| UK100m | indices | 2023-01-03 01:00 | 2026-11-10 23:00 |
| US30m | indices | 2023-01-02 23:00 | 2026-11-10 23:00 |
| US500m | indices | 2023-01-02 23:00 | 2026-11-10 23:00 |
| USTECm | indices | 2023-01-02 23:00 | 2026-11-09 23:00 |
| ADAUSDm | crypto | 2023-01-01 00:00 | 2024-08-08 12:00 |
| BCHUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| BNBUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| BTCUSDm | crypto | 2020-01-01 00:00 | 2026-11-09 23:00 |
| ETHUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| LTCUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| SOLUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| XRPUSDm | crypto | 2023-01-01 00:00 | 2026-11-10 23:00 |
| UKOILm | commodities | 2023-01-03 01:00 | 2026-11-10 21:00 |
| USOILm | commodities | 2019-02-18 13:00 | 2026-11-09 23:00 |
| XAGUSDm | commodities | 2023-01-02 23:00 | 2026-11-10 23:00 |
| XAUUSDm | commodities | 2020-01-02 01:00 | 2026-11-09 23:00 |
| XNGUSDm | commodities | 2023-01-02 23:00 | 2026-11-10 23:00 |
