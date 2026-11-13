# Theory library: verification of the screen passes, pre-registration

Committed **2026-11-12, after the screen and before running these checks.**

## What happened first

The first screen found 9 passes. 8 of them used limit or stop orders, so the cause was investigated:
- **The bug:** `manage` let the **target** fill on the same candle as an intrabar limit or stop fill. The candle's high or low may have printed before the fill, so this was look-ahead.
- **It broke the pre-registration,** which says "stops and targets are checked on later candles".
- **The fix:** `intrabar=True`, committed with this file. The stop is still checked on the fill candle, which is conservative.
- **Re-run:** the screen gave **6 passes** (`results/results.json`). The pre-fix results are kept in `results/results_before_intrabar_fix.json`.

## Candidates to verify

| Theory | Market and timeframe |
|---|---|
| B9 Fibonacci 61.8% pullback | USOILm 1h, ETHUSDT 1h, BTCUSDT 1h |
| D4 FVG fill | XAUUSDm 1h |
| B7 session-TWAP reversion | XAUUSDm 15m, USTECm 15m |

## Checks (all must pass for a candidate to survive)

**V1. Independent re-implementation on 1-minute data, written separately from `theories.py`.**
- **Signals:** the same as before, computed from 1h (or 15m) candles built from 1-minute bars.
- **Fills and exits:** simulated **minute by minute**, which settles the order of events inside each candle.
  - A buy limit fills only when the 1-minute **low trades below the limit by at least one full spread**, at the limit price. This allows for queueing and touch-only fills.
  - Stops fill at the level, or at the 1-minute open if price gaps through it.
  - Targets are limit fills.
- **Data:** Exness markets use the existing 1-minute bars. **BTC and ETH use Binance 1-minute klines downloaded from 2025-01-01** (`data-api.binance.vision`), with the 0.05% fee per side.
- **Pass:** mean net > 0 at 2× costs in **both** 2025 and 2026.

**V2. Neighbouring parameters (each run with the screen engine).**
- **B9:** Fibonacci level 0.5 / 0.618 / 0.786 × swing lookback 15 / 20 / 25 candles, which is 9 versions including the original.
- **D4:** limit validity 5 / 10 / 15 candles × target 1.5R / 2R / 2.5R, which is 9 versions.
- **B7:** band 1.5 / 2 / 2.5 sd × minimum candles 6 / 8 / 10, which is 9 versions.
- **Pass:** at least 7 of the 9 versions have holdout mean > 0 at 2× costs.

**V3. Economic size.** Mean net at 2× costs ≥ 2 bp per trade in both periods. Edges below that are too small to survive real-world slippage.

## Survivors

Each survivor gets a frozen forward paper test, with rules written before its first live candle. No real-money recommendation is made before that forward test has enough trades.
