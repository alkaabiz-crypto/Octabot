# Theory-library survivors: forward PAPER test rules (frozen)

Written and committed **2026-11-12, before the first live candle was processed.** Fake money only. No orders, no accounts.

These are the two candidates that survived every check in `../theory_library/VERIFY_PREREG.md`: the screen, 9/9 neighbouring settings, the minimum size and the minute-level re-test. The rules are copied unchanged from `../theory_library/theories.py` (`d4_fvg`, `b9`) and `verify_minute.py`.

| Test | Theory | Market (forward feed) | Candle |
|---|---|---|---|
| **GOLD_FVG** | D4 fair-value-gap fill | Hyperliquid **xyz:GOLD** | 1h, UTC |
| **OIL_FIB** | B9 Fibonacci 61.8% pullback | Hyperliquid **xyz:CL** (WTI) | 1h, UTC |

The ETH Fibonacci candidate is added only if it passes its minute-level re-test (V1). That would be a separate commit, before its first live candle.

## Signals (checked at every closed 1h candle while flat)

**GOLD_FVG**
- **Long signal:** a bullish gap, where the low of candle i is above the high of candle i−2.
  - **Buy limit:** at the high of i−2.
  - **Stop:** the low of i−2.
  - **Target:** the limit + 2 × (limit − stop).
- **Short signal:** the mirror, a bearish gap where the high of i is below the low of i−2.

**OIL_FIB**
- **Swing:** over the last 20 closed candles, H = the highest high and L = the lowest low.
- **Long signal:** the close is above the SMA50 of 1h closes **and** the high came after the low.
  - **Buy limit:** at H − 0.618 × (H − L).
  - **Stop:** L.
  - **Target:** H.
- **Short signal:** the mirror, when the close is below the SMA50 and the low came after the high.

## Orders and fills (minute by minute, Hyperliquid 1m candles)

- **Order life:** each signal places a limit order **valid for the next 10 candles**. Several orders can be pending at once.
- **Which order fills:** the **oldest** pending order that fills is taken, and all the others are cancelled.
- **Fill rule:** a buy limit fills only if the 1-minute **low is at least one full spread below the limit**. Shorts mirror this. The fill price is the limit, or the 1-minute open if price gapped through it.
- **Stop:** checked from the fill minute. It fills at the stop, or at the open if price gapped through.
- **Target:** checked from the minute after the fill, with the same one-spread penetration.
- **Time stop:** exit at the close of the 20th 1h candle after the fill candle.
- **After an exit:** the next signal check is at the close of the candle after the exit candle.

## Costs and size

| | Gold | Oil |
|---|---|---|
| Spread (round trip) | **0.22 USD/oz** | **0.02 USD/bbl** |
| Basis | the mean Exness XAUUSDm entry spread measured in `../orb_study` | the median Exness USOILm spread |

- **2× costs** are reported alongside the normal costs.
- **Size:** one 0.01-lot unit, which is 1 oz of gold or 10 bbl of oil. Results are also shown in bp of price.
- **Swap:** not deducted, because it is unverified. Holds can cross the daily rollover.

## Operation and evaluation

- **Feed:** the Hyperliquid public API, hourly runs.
- **State:** `state_<test>.json` holds the last processed minute, the pending orders and the open position. Each minute is processed once.
- **Ledger:** `ledger_<test>.csv` is append-only.
- **STOPPED** if the 1-minute feed has a gap of more than 90 minutes on a weekday while an order or position is open, or if the feed no longer reaches back to the cursor.
- **Evaluation after 100 closed trades per test** (about 3 months for gold, about 5–6 months for oil).
- **Pass:** mean net > 0 **at 2× costs** and ≥ 2 bp per trade. Before that, nothing is called a result.
