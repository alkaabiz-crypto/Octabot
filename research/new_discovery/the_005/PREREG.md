# THE-005 event study: do round numbers stop and reverse price more often? (pre-registered 2026-11-13, before computation)

**Claims** (Osler 2000, 2003):
- **(a) Reversal:** price reverses more often at round levels than at other levels, because take-profit orders cluster there.
- **(b) Acceleration:** after a round level is crossed, the move continues more often, because stop-losses cluster just beyond it.

Batch 003 tested only trading P&L. This test measures the claims themselves (`../../categories/THEORIES.md`).

## Levels

- **Round grid** (as batch 003): gold 10 USD; oil 1 USD; EUR/USD 0.0100; USD/JPY 1.00; S&P 500 50 points; BTC 1,000 USD.
- **Matched null:** the levels shifted by half a grid step (e.g. 3905 for gold). Same spacing, same price region, not round.

## Events (15-minute mid candles)

- **Touch from below** of level *L*: the previous 8 highs are all below *L*, and the current high is ≥ *L*. Touches from above mirror this.
- **(a) Reversal outcome:** with *d* = 0.25 × grid, over the next 16 candles (4 h), does price trade back to *L* − *d* before it reaches *L* + *d* (mirrored from above)?
  - It counts 1 if it reverses first, 0 if it continues first. Neither within 4 h → excluded.
- **(b) Crossing:** a candle **closes** beyond *L* after 8 closes on the other side. **Outcome:** does it reach *L* ± *d* (continuation) before *L* ∓ *d*?

## Statistics

- **Effect (a):** the reversal rate at round levels minus the rate at null levels.
- **Effect (b):** the continuation rate at round levels minus the rate at null levels.
- Both are tested with a two-proportion z-test, one-sided in the predicted direction (> 0), per market and period.
- **Periods:** EARLY (to 2022: gold, oil, BTC), TRAIN, VALIDATION, TEST.

## Verdict, per claim (a) and (b)

| Verdict | Conditions |
|---|---|
| **SUPPORTED** | TEST effect > 0 with p ≤ 0.05 after Benjamini–Hochberg across the 6 markets, in ≥ 4 markets, and the effect is > 0 in every earlier period for those markets |
| **PARTLY SUPPORTED** | 1–3 markets |
| **DECAYED** | Significant only in EARLY / TRAIN |
| **NOT SUPPORTED** | Otherwise |

**Tradability is not part of this test.** Batch 003 already showed the trading rules lose after costs.
