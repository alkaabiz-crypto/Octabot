# Indicator information test, batch IND-001: results

Pre-registered in `PREREG.md` (commit `d4d38609`). Method: `../../categories/INDICATORS.md`. Output: `results.json`; script `run_ind.py`. Data: Exness hourly mid prices (gold, oil, BTC, S&P 500, EUR/USD), 2019/2020 → 2026-11-09.

**329 TEST tests; 5 significant after Benjamini–Hochberg, all of them IND-018.**

| ID | Indicator | Verdict (pre-registered, "usual" bullish orientation) |
|---|---|---|
| IND-001 | Coinbase premium z (BTC) | **WEAK.** At 5 days the same positive sign in every period (IC +0.000 / +0.060 / +0.054 / +0.078), not significant. At 1–24 h it is positive in EARLY, TRAIN and VALIDATION, and slightly negative in TEST. |
| IND-003 | KST − signal | NONE |
| IND-004 | Distance from the daily VWAP | NONE (contrarian, see below) |
| IND-005 | RSI14 | NONE (contrarian) |
| IND-006 | MACD histogram | NONE |
| IND-007 | EMA 9/21 | NONE |
| IND-008 | Supertrend | NONE |
| IND-009 | Parabolic SAR | NONE |
| IND-010 | ADX × direction | NONE |
| IND-011 | Donchian position | NONE (contrarian) |
| IND-012 | Ichimoku cloud distance | NONE |
| IND-013 | Bollinger %B | NONE (contrarian) |
| IND-014 | Stochastic %K | NONE (contrarian) |
| IND-015 | CCI | NONE (contrarian) |
| IND-016 | Williams %R | NONE (contrarian) |
| IND-017 | Williams Vix Fix | NONE |
| IND-018 | HAR volatility forecast | **INFORMATIVE**: it predicts next-day volatility in all 5 markets, all periods, BH-significant. This is a volatility (risk) indicator, not a direction indicator. |
| IND-020 | 20-hour momentum | NONE |

**Plain reading.** None of the classic indicators carries reliable information about the **direction** of the next 1 hour to 5 days in the trend-following way traders use them. Volatility, by contrast, is predictable.

## Exploratory, after the result (does not change any verdict): the indicators work *backwards* at 1 hour

- 124 indicator × market × horizon combinations have a **negative** IC in every period. They are mostly oscillators at the 1-hour horizon, on BTC and EUR/USD.
- **BTC 1h examples** (EARLY / TRAIN / VALIDATION / TEST IC):

  | Indicator | IC by period |
  |---|---|
  | Williams %R | −0.058 / −0.068 / −0.053 / −0.039 |
  | Donchian position | −0.053 / −0.057 / −0.048 / −0.035 |
  | RSI14 | −0.038 / −0.052 / −0.040 / −0.031 |

- **Not just the last move reversing:** the partial IC, controlling for the past hour's return, stays −0.02 to −0.04 and significant in most periods.
- **Meaning:** overbought → slightly lower next hour, and the reverse. This is short-term reversal.
- **Size:** about 1–2 bp per hour on BTC, probably below trading costs. Registered as theory candidate **THE-017** for a proper pre-registered test. It is not a strategy.
