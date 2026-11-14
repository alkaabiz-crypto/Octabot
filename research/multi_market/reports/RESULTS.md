# Results: which indicators fit which markets

33 markets, 96930 market-variant pairs. Discovery 2023-07 to 2024-12; confirmation 2025-01 to the latest candle. Primary cost unless noted.

## Headline

- Per-market picks confirmed: **0 of 88** (raw p ≤ 0.05 in confirmation: 8, about 4 expected by luck).
- Per-class picks confirmed: **0 of 20**.
- Whole-sample check: 548 of 85748 pairs significant after BH (raw p ≤ 0.05: 4439, about 4287 expected by luck).

## Per-class picks (fitted on discovery, tested on 2025 to now)

| Class | Variant | Discovery z | Confirmation z | p | Markets positive in confirmation | Mean E in confirmation | Confirmed |
|---|---|---|---|---|---|---|---|
| forex | BOLLINGER_PCT_B + ADX>20 filter SELL, target ½ stop | +3.72 | +0.69 | 0.245 | 0/10 | -0.164R | no |
| forex | HMA_9 + ADX>20 filter SELL, target ½ stop | +3.63 | -1.01 | 0.843 | 0/10 | -0.177R | no |
| forex | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter SELL, target ½ stop | +3.39 | +0.72 | 0.237 | 0/10 | -0.164R | no |
| forex | CHAIKIN_MONEY_FLOW_20 + ADX>20 filter SELL, ±1R | +3.07 | +1.14 | 0.128 | 0/10 | -0.160R | no |
| forex | CHAIKIN_OSC_3_10 BUY, target ½ stop | +3.06 | +1.09 | 0.139 | 0/10 | -0.159R | no |
| indices | QQE_MOD BUY, target ½ stop | +5.38 | +0.24 | 0.407 | 1/10 | -0.103R | no |
| indices | HMA_9 + daily EMA200 filter SELL, target ½ stop | +5.26 | +0.52 | 0.300 | 2/9 | -0.074R | no |
| indices | TRUE_STRENGTH_25_13_13 BUY, target ½ stop | +5.15 | -0.28 | 0.608 | 1/10 | -0.110R | no |
| indices | QQE_MOD + session VWAP filter BUY, target ½ stop | +5.07 | -0.04 | 0.516 | 1/10 | -0.105R | no |
| indices | WADDAH_ATTAR_ORIGINAL BUY, target ½ stop | +4.75 | +0.09 | 0.463 | 0/10 | -0.103R | no |
| crypto | RANGE_FILTER BUY, ±1R | +5.42 | +3.26 | 0.001 | 1/7 | -0.514R | no |
| crypto | RANGE_FILTER BUY, target ½ stop | +5.01 | +2.96 | 0.002 | 0/7 | -0.526R | no |
| crypto | WILLIAMS_ALLIGATOR + ADX>20 filter BUY, target ½ stop | +4.49 | -0.14 | 0.555 | 0/7 | -0.582R | no |
| crypto | WADDAH_ATTAR_ORIGINAL SELL, ±1R | +4.34 | +2.47 | 0.007 | 0/6 | -0.393R | no |
| crypto | SUPERTREND_KIVANC BUY, target ½ stop | +4.33 | -0.35 | 0.636 | 0/7 | -0.620R | no |
| commodities | KLINGER_34_55_13 + ADX>20 filter SELL, target ½ stop | +4.21 | -0.16 | 0.565 | 0/5 | -0.195R | no |
| commodities | TEMA_9 + ADX>20 filter SELL, target ½ stop | +4.03 | -0.27 | 0.608 | 0/5 | -0.204R | no |
| commodities | TEMA_9 + ADX>20 filter SELL, trailing stop | +3.99 | +0.75 | 0.227 | 0/5 | -0.229R | no |
| commodities | HMA_9 + ADX>20 filter SELL, trailing stop | +3.56 | +0.99 | 0.162 | 0/5 | -0.226R | no |
| commodities | ACCUM_DIST_VS_SMA20 + ADX>20 filter SELL, target ½ stop | +3.49 | -0.78 | 0.783 | 0/5 | -0.200R | no |

## Per-market picks

| Class | Market | Variant | Discovery: trades, win, E, z | Confirmation: trades, win, E, E stress, z, p | Confirmed |
|---|---|---|---|---|---|
| forex | AUDUSDm | CONNORS_RSI_3_2_100 + ADX>20 filter SELL, trailing stop | 112, 37%, +0.294R, +4.04 | 134, 25%, -0.288R, -0.466R, -0.47, 0.682 | no |
| forex | AUDUSDm | CONNORS_RSI_3_2_100 SELL, trailing stop | 160, 37%, +0.194R, +3.79 | 181, 27%, -0.297R, -0.473R, -1.09, 0.862 | no |
| forex | AUDUSDm | NVI_VS_EMA255 SELL, hold to opposite signal | 113, 34%, +0.233R, +1.04 | 148, 24%, -0.474R, -0.680R, -2.05, 0.980 | no |
| forex | GBPJPYm | CHAIKIN_MONEY_FLOW_20 + 4H EMA200 filter SELL, hold to opposite signal | 115, 30%, +0.162R, +1.75 | 189, 28%, -0.196R, -0.319R, -0.96, 0.832 | no |
| forex | GBPJPYm | CHANDELIER_EXIT + session VWAP filter BUY, hold to opposite signal | 114, 42%, +0.249R, +1.27 | 140, 36%, -0.019R, -0.283R, +0.19, 0.426 | no |
| forex | USDJPYm | CHAIKIN_OSC_3_10 + session VWAP filter BUY, trailing stop | 154, 40%, +0.223R, +2.44 | 178, 36%, +0.040R, -0.175R, +2.12, 0.017 | no |
| forex | USDJPYm | PRICE_OSC_12_26 + session VWAP filter BUY, trailing stop | 119, 40%, +0.215R, +2.01 | 147, 31%, -0.177R, -0.386R, -0.61, 0.729 | no |
| forex | USDJPYm | WILLIAMS_ALLIGATOR + 4H EMA200 filter BUY, trailing stop | 140, 40%, +0.247R, +1.96 | 166, 33%, -0.126R, -0.372R, -0.56, 0.711 | no |
| forex | USDJPYm | CHAIKIN_OSC_3_10 + 4H EMA200 filter SELL, hold to opposite signal | 145, 30%, +0.204R, +1.71 | 231, 31%, -0.061R, -0.173R, -0.10, 0.542 | no |
| forex | USDJPYm | ACCUM_DIST_VS_SMA20 + 4H EMA200 filter SELL, hold to opposite signal | 164, 35%, +0.158R, +1.55 | 257, 28%, -0.094R, -0.201R, -0.55, 0.709 | no |
| indices | DE30m | WADDAH_ATTAR_ORIGINAL + session VWAP filter BUY, trailing stop | 227, 39%, +0.282R, +3.02 | 306, 35%, -0.012R, -0.116R, +0.29, 0.384 | no |
| indices | DE30m | VWMA_20 + ADX>20 filter BUY, ±1R | 183, 60%, +0.121R, +2.98 | 263, 50%, -0.036R, -0.114R, +0.39, 0.349 | no |
| indices | DE30m | WADDAH_ATTAR_ORIGINAL BUY, trailing stop | 229, 38%, +0.268R, +2.92 | 311, 35%, -0.008R, -0.112R, +0.34, 0.368 | no |
| indices | DE30m | PIVOT_REVERSAL + session VWAP filter SELL, strategy's own exits | 153, 35%, +0.154R, +2.72 | 207, 33%, -0.029R, -0.142R, +1.10, 0.136 | no |
| indices | DE30m | VWMA_20 BUY, trailing stop | 236, 37%, +0.246R, +2.36 | 332, 33%, -0.022R, -0.125R, +0.08, 0.469 | no |
| indices | FR40m | TRUE_STRENGTH_25_13_13 + ADX>20 filter SELL, hold to opposite signal | 153, 41%, +0.236R, +2.72 | 183, 29%, -0.219R, -0.321R, -0.01, 0.504 | no |
| indices | FR40m | PRICE_MOMENTUM_OSC_35_20_10 + ADX>20 filter SELL, hold to opposite signal | 144, 35%, +0.159R, +2.15 | 168, 29%, -0.327R, -0.433R, -0.82, 0.793 | no |
| indices | FR40m | DMI_14 + ADX>20 filter SELL, hold to opposite signal | 138, 30%, +0.137R, +1.48 | 155, 24%, -0.225R, -0.313R, -0.09, 0.537 | no |
| indices | HK50m | RANK_CORRELATION_10 + ADX>20 filter SELL, trailing stop | 172, 35%, +0.093R, +2.90 | 212, 29%, -0.159R, -0.239R, +0.27, 0.394 | no |
| indices | HK50m | EASE_OF_MOVEMENT_14 + session VWAP filter SELL, trailing stop | 176, 38%, +0.087R, +2.84 | 221, 27%, -0.172R, -0.251R, -0.35, 0.635 | no |
| indices | HK50m | DMI_14 + session VWAP filter BUY, trailing stop | 161, 30%, +0.104R, +2.53 | 214, 34%, -0.061R, -0.144R, +1.19, 0.117 | no |
| indices | HK50m | DMI_14 BUY, trailing stop | 187, 30%, +0.082R, +2.53 | 263, 32%, -0.084R, -0.166R, +0.96, 0.169 | no |
| indices | HK50m | EASE_OF_MOVEMENT_14 + ADX>20 filter SELL, trailing stop | 156, 35%, +0.089R, +2.47 | 200, 29%, -0.076R, -0.156R, +1.10, 0.135 | no |
| indices | JP225m | PRICE_MOMENTUM_OSC_35_20_10 + 4H EMA200 filter BUY, target ½ stop | 142, 74%, +0.081R, +2.94 | 173, 71%, +0.043R, -0.009R, +1.84, 0.033 | no |
| indices | JP225m | PARABOLIC_SAR + session VWAP filter BUY, strategy's own exits | 246, 43%, +0.146R, +1.94 | 323, 41%, +0.034R, -0.024R, +0.16, 0.437 | no |
| indices | JP225m | BBTREND_20_50 + session VWAP filter BUY, ±1R | 121, 55%, +0.083R, +1.84 | 153, 50%, +0.004R, -0.050R, +0.49, 0.311 | no |
| indices | JP225m | PARABOLIC_SAR BUY, strategy's own exits | 382, 41%, +0.074R, +1.56 | 497, 41%, +0.044R, -0.014R, +0.28, 0.391 | no |
| indices | JP225m | CHANDE_MOMENTUM_9 + session VWAP filter BUY, trailing stop | 234, 36%, +0.119R, +1.39 | 318, 34%, +0.051R, -0.016R, +0.10, 0.458 | no |
| indices | US30m | MFI_14 + ADX>20 filter BUY, ±1R | 100, 60%, +0.119R, +1.83 | 187, 47%, -0.106R, -0.201R, -1.17, 0.878 | no |
| indices | US30m | CONNORS_RSI_3_2_100 + daily EMA200 filter BUY, trailing stop | 112, 36%, +0.161R, +1.16 | 160, 33%, +0.102R, -0.019R, +1.58, 0.057 | no |
| indices | US30m | BBTREND_20_50 + ADX>20 filter BUY, hold to opposite signal | 132, 51%, +0.272R, +1.16 | 185, 45%, +0.079R, -0.056R, +0.13, 0.447 | no |
| indices | US30m | CONNORS_RSI_3_2_100 BUY, trailing stop | 135, 38%, +0.156R, +1.14 | 190, 35%, +0.129R, +0.015R, +2.43, 0.007 | no |
| indices | US30m | BBTREND_20_50 BUY, trailing stop | 163, 32%, +0.172R, +1.03 | 217, 32%, -0.089R, -0.203R, -0.98, 0.837 | no |
| indices | US500m | KST + ADX>20 filter BUY, trailing stop | 136, 38%, +0.275R, +2.18 | 182, 32%, -0.064R, -0.183R, -0.27, 0.606 | no |
| indices | US500m | KST + session VWAP filter BUY, trailing stop | 152, 39%, +0.265R, +2.11 | 218, 34%, -0.057R, -0.181R, -0.06, 0.523 | no |
| indices | US500m | CHANDELIER_EXIT + ADX>20 filter BUY, trailing stop | 108, 38%, +0.272R, +1.43 | 134, 30%, -0.187R, -0.290R, -1.39, 0.918 | no |
| indices | US500m | CORAL_TREND + ADX>20 filter BUY, trailing stop | 113, 34%, +0.258R, +1.42 | 141, 30%, -0.092R, -0.209R, -0.42, 0.662 | no |
| indices | US500m | QQE_MOD + ADX>20 filter BUY, trailing stop | 142, 35%, +0.244R, +1.38 | 178, 33%, -0.030R, -0.151R, +0.11, 0.456 | no |
| indices | USTECm | KST + session VWAP filter BUY, ±1R | 179, 57%, +0.090R, +2.62 | 232, 54%, +0.024R, -0.046R, +1.55, 0.061 | no |
| indices | USTECm | KST + ADX>20 filter BUY, ±1R | 156, 58%, +0.108R, +2.60 | 194, 52%, -0.025R, -0.091R, +0.72, 0.237 | no |
| indices | USTECm | WILLIAMS_ALLIGATOR + session VWAP filter SELL, trailing stop | 127, 31%, +0.228R, +2.50 | 176, 30%, -0.144R, -0.231R, -0.68, 0.753 | no |
| indices | USTECm | PRICE_MOMENTUM_OSC_35_20_10 + ADX>20 filter BUY, ±1R | 149, 57%, +0.078R, +2.08 | 192, 47%, -0.077R, -0.144R, -0.16, 0.563 | no |
| indices | USTECm | LSMA_25 + session VWAP filter BUY, trailing stop | 254, 37%, +0.177R, +1.79 | 313, 34%, +0.005R, -0.078R, +0.55, 0.291 | no |
| crypto | BCHUSDm | LINREG_CHANNEL_100_2 BUY, trailing stop | 176, 31%, +0.106R, +3.34 | 215, 13%, -1.608R, -1.627R, +0.67, 0.251 | no |
| crypto | BCHUSDm | LINREG_CHANNEL_100_2 + daily EMA200 filter BUY, trailing stop | 131, 30%, +0.117R, +3.00 | 70, 26%, -0.380R, -0.402R, +0.77, 0.220 | no |
| crypto | BCHUSDm | LINREG_CHANNEL_100_2 + session VWAP filter BUY, trailing stop | 111, 31%, +0.178R, +2.99 | 76, 21%, -1.023R, -1.044R, +1.48, 0.069 | no |
| crypto | BCHUSDm | LINREG_CHANNEL_100_2 + ADX>20 filter BUY, trailing stop | 151, 32%, +0.087R, +2.82 | 186, 13%, -1.562R, -1.580R, +1.19, 0.117 | no |
| crypto | BCHUSDm | WILLIAMS_ALLIGATOR + session VWAP filter SELL, ±1R | 102, 58%, +0.150R, +2.57 | 279, 10%, -2.333R, -2.351R, -3.29, 0.999 | no |
| crypto | BNBUSDm | AWESOME_OSC + ADX>20 filter BUY, target ½ stop | 103, 48%, +0.092R, +3.31 | 90, 44%, -0.338R, -0.370R, -0.86, 0.805 | no |
| crypto | BNBUSDm | SUPERTREND_KIVANC BUY, trailing stop | 111, 23%, +0.350R, +2.39 | 107, 25%, -0.201R, -0.243R, +0.52, 0.301 | no |
| crypto | BNBUSDm | WILLIAMS_ALLIGATOR + ADX>20 filter BUY, trailing stop | 142, 23%, +0.190R, +2.38 | 129, 21%, -0.369R, -0.409R, -0.92, 0.822 | no |
| crypto | BNBUSDm | WILLIAMS_ALLIGATOR + ADX>20 filter BUY, hold to opposite signal | 167, 26%, +0.319R, +2.34 | 147, 27%, -0.268R, -0.308R, -0.05, 0.518 | no |
| crypto | BNBUSDm | CHANDELIER_EXIT BUY, trailing stop | 151, 21%, +0.118R, +1.88 | 149, 23%, -0.308R, -0.347R, -0.46, 0.678 | no |
| crypto | BTCUSDm (seen in earlier rounds) | AWESOME_OSC BUY, ±1R | 251, 57%, +0.104R, +2.72 | 303, 49%, -0.035R, -0.073R, -0.24, 0.594 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND + ADX>20 filter BUY, ±1R | 163, 59%, +0.146R, +2.47 | 217, 47%, -0.094R, -0.130R, -1.10, 0.864 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND BUY, ±1R | 277, 55%, +0.074R, +2.36 | 337, 48%, -0.055R, -0.091R, -0.58, 0.721 | no |
| crypto | BTCUSDm (seen in earlier rounds) | CORAL_TREND BUY, trailing stop | 261, 38%, +0.335R, +2.31 | 324, 32%, +0.036R, -0.009R, +0.46, 0.322 | no |
| crypto | BTCUSDm (seen in earlier rounds) | AWESOME_OSC BUY, trailing stop | 240, 36%, +0.321R, +2.30 | 301, 32%, +0.054R, +0.009R, +0.70, 0.242 | no |
| crypto | ETHUSDm | PRICE_MOMENTUM_OSC_35_20_10 + ADX>20 filter SELL, ±1R | 211, 55%, +0.089R, +3.23 | 274, 55%, +0.085R, +0.063R, +2.94, 0.002 | no |
| crypto | ETHUSDm | BOLLINGER_PCT_B + daily EMA200 filter SELL, target ½ stop | 100, 73%, +0.081R, +2.68 | 248, 65%, -0.020R, -0.043R, +0.53, 0.297 | no |
| crypto | ETHUSDm | TRUE_STRENGTH_25_13_13 + ADX>20 filter SELL, ±1R | 261, 52%, +0.027R, +2.63 | 316, 51%, +0.018R, -0.005R, +1.47, 0.071 | no |
| crypto | ETHUSDm | QQE_MOD + ADX>20 filter SELL, ±1R | 250, 52%, +0.031R, +2.36 | 304, 53%, +0.062R, +0.039R, +2.23, 0.013 | no |
| crypto | ETHUSDm | CORAL_TREND + ADX>20 filter SELL, ±1R | 163, 54%, +0.058R, +2.28 | 216, 50%, -0.018R, -0.041R, +0.63, 0.265 | no |
| crypto | SOLUSDm | DPO_21 BUY, trailing stop | 220, 33%, +0.160R, +2.96 | 229, 18%, -0.503R, -0.529R, -1.00, 0.842 | no |
| crypto | SOLUSDm | COPPOCK_10_14_11 BUY, trailing stop | 197, 34%, +0.193R, +2.78 | 201, 18%, -0.442R, -0.467R, -0.16, 0.563 | no |
| crypto | SOLUSDm | WILLIAMS_ALLIGATOR + daily EMA200 filter BUY, trailing stop | 185, 32%, +0.207R, +2.65 | 58, 21%, -0.354R, -0.379R, +0.55, 0.291 | no |
| crypto | SOLUSDm | CORAL_TREND + daily EMA200 filter BUY, trailing stop | 159, 35%, +0.202R, +2.56 | 55, 24%, -0.334R, -0.358R, +0.76, 0.223 | no |
| crypto | SOLUSDm | WILLIAMS_ALLIGATOR BUY, trailing stop | 219, 31%, +0.144R, +2.55 | 220, 15%, -0.562R, -0.587R, -1.89, 0.971 | no |
| crypto | XRPUSDm | PIVOT_REVERSAL + session VWAP filter BUY, strategy's own exits | 239, 29%, +0.378R, +2.15 | 147, 20%, -0.146R, -0.175R, +1.19, 0.116 | no |
| crypto | XRPUSDm | PRICE_CHANNEL + session VWAP filter BUY, strategy's own exits | 147, 30%, +0.656R, +2.05 | 98, 28%, -0.408R, -0.441R, -0.28, 0.610 | no |
| crypto | XRPUSDm | PIVOT_REVERSAL BUY, strategy's own exits | 333, 30%, +0.276R, +2.04 | 372, 25%, -0.074R, -0.104R, +2.61, 0.004 | no |
| crypto | XRPUSDm | PRICE_CHANNEL BUY, strategy's own exits | 207, 31%, +0.560R, +2.03 | 242, 29%, +0.022R, -0.015R, +2.15, 0.016 | no |
| crypto | XRPUSDm | VOLATILITY_STOP_20_2 BUY, trailing stop | 291, 31%, +0.104R, +1.77 | 360, 22%, -0.217R, -0.241R, +1.19, 0.117 | no |
| commodities | UKOILm | BBTREND_20_50 + ADX>20 filter SELL, hold to opposite signal | 105, 45%, +0.215R, +2.13 | 178, 47%, -0.161R, -0.208R, +0.07, 0.472 | no |
| commodities | USOILm (seen in earlier rounds) | BULL_BEAR_POWER_13 + ADX>20 filter SELL, target ½ stop | 255, 71%, +0.056R, +3.23 | 337, 64%, -0.050R, -0.080R, +0.32, 0.373 | no |
| commodities | USOILm (seen in earlier rounds) | WOODIES_CCI_14 + ADX>20 filter SELL, target ½ stop | 250, 71%, +0.049R, +2.90 | 335, 64%, -0.049R, -0.079R, +0.33, 0.372 | no |
| commodities | USOILm (seen in earlier rounds) | BIGBELUGA_SESSION_VWAP SELL, trailing stop | 174, 34%, +0.118R, +2.90 | 207, 29%, -0.054R, -0.098R, +0.52, 0.300 | no |
| commodities | USOILm (seen in earlier rounds) | WOODIES_CCI_14 + 4H EMA200 filter SELL, target ½ stop | 187, 72%, +0.075R, +2.74 | 239, 59%, -0.127R, -0.161R, -1.68, 0.954 | no |
| commodities | USOILm (seen in earlier rounds) | RANGE_FILTER + session VWAP filter BUY, target ½ stop | 127, 72%, +0.086R, +2.70 | 168, 70%, +0.033R, +0.004R, +1.01, 0.157 | no |
| commodities | XAGUSDm | RANGE_FILTER + session VWAP filter BUY, trailing stop | 120, 32%, +0.076R, +1.86 | 154, 36%, +0.106R, +0.062R, +0.72, 0.235 | no |
| commodities | XAGUSDm | RANGE_FILTER BUY, trailing stop | 121, 32%, +0.070R, +1.85 | 158, 36%, +0.097R, +0.055R, +0.74, 0.230 | no |
| commodities | XAGUSDm | RANGE_FILTER + session VWAP filter BUY, hold to opposite signal | 119, 37%, +0.118R, +0.45 | 157, 38%, +0.165R, +0.107R, -0.26, 0.601 | no |
| commodities | XAGUSDm | RANGE_FILTER BUY, hold to opposite signal | 120, 37%, +0.112R, +0.39 | 161, 38%, +0.151R, +0.093R, -0.33, 0.627 | no |
| commodities | XAUUSDm (seen in earlier rounds) | HMA_9 + session VWAP filter BUY, trailing stop | 250, 38%, +0.254R, +2.56 | 290, 36%, +0.210R, +0.128R, +0.65, 0.257 | no |
| commodities | XAUUSDm (seen in earlier rounds) | ACCUM_DIST_VS_SMA20 + session VWAP filter BUY, ±1R | 258, 57%, +0.103R, +2.32 | 307, 51%, +0.004R, -0.056R, -0.14, 0.555 | no |
| commodities | XAUUSDm (seen in earlier rounds) | RELATIVE_VOLATILITY_10 + daily EMA200 filter BUY, ±1R | 376, 57%, +0.092R, +2.23 | 409, 50%, -0.017R, -0.081R, -1.86, 0.968 | no |
| commodities | XAUUSDm (seen in earlier rounds) | BBTREND_20_50 + session VWAP filter BUY, ±1R | 107, 60%, +0.188R, +2.02 | 140, 63%, +0.225R, +0.164R, +2.69, 0.004 | no |
| commodities | XAUUSDm (seen in earlier rounds) | VORTEX_14 + session VWAP filter BUY, trailing stop | 221, 39%, +0.265R, +1.98 | 255, 34%, +0.128R, +0.047R, -0.71, 0.761 | no |

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
