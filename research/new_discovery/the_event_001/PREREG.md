# Theory event batch 001: pre-registration (2026-11-13, before computation)

Event studies for THE-001, THE-002, THE-003, THE-015 and THE-016, whose verdicts so far rest only on trading P&L (`../../categories/THEORY_REVIEW.md`). Method: `../../categories/THEORIES.md`.

**Common settings.**
- **Data:** Exness 15-minute bid/ask candles (mid prices).
- **Markets:** gold, oil, S&P 500, EUR/USD, BTC.
- **Periods:** EARLY (to 2022: gold, oil, BTC), TRAIN, VALIDATION, TEST.
- **Measurement:** the *signed* forward return (in the predicted direction), from the next candle's open, in bp.
- **Null:** the same event labels shuffled 2,000 times **within the same UTC hour of day** and period; for THE-015, within the same period. One-sided p.

## Claims, events and predictions

| ID | Claim | Event | Prediction (signed) | Horizon |
|---|---|---|---|---|
| THE-001 | Previous-day zones + a signal candle | 15-minute candle, 00:00–20:00 UTC. A **bullish** candle (close > open) closing **below** the previous day's mid-range is a long event; a bearish candle closing above it is a short event. | the next move is in the event's direction | 4 h (16 candles) |
| THE-002 | Same-day opening-range zones + a signal candle | As THE-001, but the zones come from today's 22:00–07:00 UTC opening range, and only candles opening ≥ 07:00 count | as THE-001 | 4 h |
| THE-003 | Pin bar → reversal | 1-hour candle. **Bullish pin:** lower wick ≥ 2 × body, body in the top third of the range. **Bearish pin:** mirror. | the next move is in the pin's direction | 4 h |
| THE-015a | Turn of the month is positive | daily (21:00 UTC) returns on the last trading day and the first 3 trading days of each month | turn-of-month mean > other days' mean (long only) | 1 day |
| THE-015b | Monday effect | daily returns on Mondays | Monday mean < other days' mean (signed: −) | 1 day |
| THE-016 | Fair value gaps get filled | 1-hour bullish FVG (low *i* > high *i*−2), and bearish mirror | price trades back to the gap edge within 10 candles **more often** than it retraces the same ATR-scaled distance at random hours (matched: same period and hour of day, 20 random draws per event) | 10 h |

**THE-016's effect** = the fill rate at FVGs minus the matched random retrace rate, in percentage points (two-proportion z-test).

## Verdict per theory

| Verdict | Conditions |
|---|---|
| **SUPPORTED** | TEST effect > 0 with p ≤ 0.05 after Benjamini–Hochberg across all (theory × market) TEST tests, in ≥ 3 markets, and > 0 in every earlier period in those markets |
| **PARTLY SUPPORTED** | 1–2 markets |
| **DECAYED** | Significant (p ≤ 0.05) in EARLY or TRAIN only |
| **NOT SUPPORTED** | Otherwise |

**Count:** 6 claims × 5 markets = **30 TEST tests**.
