# Indicator information test, batch IND-002: pre-registration (2026-11-13, before computation)

Same method, data, markets, periods, horizons, partial-IC baseline and verdict rules as `../ind_batch_001/PREREG.md`. The code imports batch 001's functions unchanged.

## New candidates

Added to `../../CANDIDATES.md` as **IND-022 to IND-034**: popular TradingView indicators from the IND-021 group. **IND-019** is also tested.

Each value is oriented so that higher = the usual bullish reading.

| ID | Indicator | Value *x* |
|---|---|---|
| IND-019 | Two-state Gaussian HMM | P(high-mean state) − 0.5, on daily 21:00 UTC returns. Refitted monthly once 250 days exist (batch 002 code); forward-filtered. **Daily horizons only:** 1d, 5d. |
| IND-022 | Aroon oscillator (25) | Aroon up − Aroon down |
| IND-023 | Vortex (14) | VI+ − VI− |
| IND-024 | TRIX (15) | 100 × the 1-bar change of the triple EMA |
| IND-025 | KAMA (10, 2, 30) slope | ln(KAMA / KAMA 1 bar ago) |
| IND-026 | Williams Alligator | (lips − jaw) / ATR14. Lips = SMMA5 shifted 3, jaw = SMMA13 shifted 8. |
| IND-027 | Hull MA (55) slope | ln(HMA / HMA 1 bar ago) |
| IND-028 | Keltner position | (close − EMA20) / (2 × ATR20) |
| IND-029 | Heikin-Ashi colour run | Signed count of consecutive same-colour HA candles, capped at ±10 |
| IND-030 | Awesome Oscillator | (SMA5 − SMA34 of the median price) / ATR14 |
| IND-031 | Ultimate Oscillator (7, 14, 28) | value − 50 |
| IND-032 | Rate of change (12) | ROC12 |
| IND-033 | Fisher transform (10) | value |
| IND-034 | Elder ray (13) | (bull power + bear power) / ATR14 |

**Excluded (volume-based; CFDs have no real volume):** OBV, MFI, VWMA.

## Tests and decision

- **Count:** 13 indicators × 5 markets × 4 horizons = 260 TEST tests, plus IND-019 (5 markets × 2 daily horizons) = **270**.
- **Correction:** Benjamini–Hochberg at 5% within this batch.
- **Verdicts:** INFORMATIVE / WEAK / REDUNDANT / NONE, as batch 001.
