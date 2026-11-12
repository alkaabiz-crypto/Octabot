# Experiment registry

Every experiment, including failures, is listed. Full fields (rules, parameters, data, costs, periods and reasons) are in `REGISTRY.csv`.

| ID | Name | Market | TF | Variants | TRAIN / VALID / TEST mean bp | TEST stress bp | TEST n | TEST p | BH | Decision | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D001-UKOILm/USOILm | Statistical-arbitrage pairs (spread z-score reversion) | UKOILm/USOILm | 1h | 1 | -10.06 / -8.4 / -5.23 | -21.16 | 47 | 0.2985 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D001-EURUSDm/GBPUSDm | Statistical-arbitrage pairs (spread z-score reversion) | EURUSDm/GBPUSDm | 1h | 1 | 6.44 / -1.12 / 3.04 | -5.75 | 46 | 0.0249 | False | REJECT | not positive in every period |
| D001-USTECm/US500m | Statistical-arbitrage pairs (spread z-score reversion) | USTECm/US500m | 1h | 1 | -12.92 / -1.81 / -4.26 | -13.61 | 46 | 0.6915 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D002-portfolio | Cross-market relative strength (risk-adjusted 60-day momentum) | portfolio | weekly | 1 | -40.91 / 11.73 / -18.77 | -49.54 | 64 | 0.7113 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-XAUUSDm | Regime-adaptive trend / mean reversion (efficiency ratio) | XAUUSDm | 4h | 1 | -1.87 / -3.21 / 7.1 | 4.8 | 194 | 0.2208 | False | REJECT | not positive in every period |
| D003-USOILm | Regime-adaptive trend / mean reversion (efficiency ratio) | USOILm | 4h | 1 | -10.61 / -2.95 / -30.45 | -34.79 | 222 | 0.96 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-UKOILm | Regime-adaptive trend / mean reversion (efficiency ratio) | UKOILm | 4h | 1 | -26.89 / -29.75 / -37.43 | -52.26 | 194 | 0.9431 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-BTCUSDm | Regime-adaptive trend / mean reversion (efficiency ratio) | BTCUSDm | 4h | 1 | 10.37 / -6.07 / 5.28 | 0.81 | 265 | 0.2308 | False | REJECT | not positive in every period |
| D003-ETHUSDm | Regime-adaptive trend / mean reversion (efficiency ratio) | ETHUSDm | 4h | 1 | -6.96 / 23.84 / -10.29 | -19.69 | 242 | 0.5245 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-EURUSDm | Regime-adaptive trend / mean reversion (efficiency ratio) | EURUSDm | 4h | 1 | -4.76 / -4.08 / -2.89 | -5.23 | 202 | 0.8212 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-GBPUSDm | Regime-adaptive trend / mean reversion (efficiency ratio) | GBPUSDm | 4h | 1 | -7.54 / -4.16 / 0.24 | -2.32 | 183 | 0.1768 | False | REJECT | not positive in every period |
| D003-USDJPYm | Regime-adaptive trend / mean reversion (efficiency ratio) | USDJPYm | 4h | 1 | -2.42 / -6.1 / -0.79 | -3.15 | 188 | 0.4386 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-US500m | Regime-adaptive trend / mean reversion (efficiency ratio) | US500m | 4h | 1 | -4.88 / 2.54 / -7.59 | -10.27 | 204 | 0.96 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-USTECm | Regime-adaptive trend / mean reversion (efficiency ratio) | USTECm | 4h | 1 | -6.66 / 4.89 / -15.04 | -17.65 | 189 | 0.988 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D003-DE30m | Regime-adaptive trend / mean reversion (efficiency ratio) | DE30m | 4h | 1 | 1.26 / 10.21 / -6.41 | -11.23 | 170 | 0.7682 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-XAUUSDm | Walk-forward logistic direction model (8 price features) | XAUUSDm | 1h | 1 | -3.73 / -0.37 / -1.26 | -2.43 | 611 | 0.5305 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-USOILm | Walk-forward logistic direction model (8 price features) | USOILm | 1h | 1 | -4.67 / -0.83 / 3.02 | -0.35 | 341 | 0.2048 | False | REJECT | not positive in every period |
| D004-UKOILm | Walk-forward logistic direction model (8 price features) | UKOILm | 1h | 1 | -22.79 / -25.68 / -12.32 | -26.03 | 304 | 0.3566 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-BTCUSDm | Walk-forward logistic direction model (8 price features) | BTCUSDm | 1h | 1 | -10.35 / -0.3 / -2.72 | -6.44 | 868 | 0.4256 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-ETHUSDm | Walk-forward logistic direction model (8 price features) | ETHUSDm | 1h | 1 | -18.13 / -7.48 / -12.05 | -20.54 | 1207 | 0.7652 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-EURUSDm | Walk-forward logistic direction model (8 price features) | EURUSDm | 1h | 1 | -1.06 / -1.64 / -0.04 | -1.47 | 214 | 0.0859 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-GBPUSDm | Walk-forward logistic direction model (8 price features) | GBPUSDm | 1h | 1 | -0.43 / -2.61 / 2.15 | 0.93 | 55 | 0.1868 | False | REJECT | not positive in every period |
| D004-USDJPYm | Walk-forward logistic direction model (8 price features) | USDJPYm | 1h | 1 | -0.68 / -0.53 / -0.41 | -1.44 | 784 | 0.2028 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-US500m | Walk-forward logistic direction model (8 price features) | US500m | 1h | 1 | -1.94 / -1.37 / -0.88 | -2.66 | 740 | 0.3497 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-USTECm | Walk-forward logistic direction model (8 price features) | USTECm | 1h | 1 | 0.44 / -1.5 / -1.18 | -2.79 | 779 | 0.5165 | False | REJECT | not positive in every period; TEST mean <= 0 |
| D004-DE30m | Walk-forward logistic direction model (8 price features) | DE30m | 1h | 1 | -4.41 / -2.5 / -2.05 | -6.05 | 943 | 0.2188 | False | REJECT | not positive in every period; TEST mean <= 0 |
