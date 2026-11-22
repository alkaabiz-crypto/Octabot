# Theory #2: day-range zones + 15-minute signal candle, pre-registration

Committed **2026-11-12, before any code was written or data looked at.** The user's description:
- use the day's high and low to judge where price is;
- use a 15-minute chart;
- take longs only in the "long area" and shorts only in the "short area";
- wait for a signal candlestick, and enter on the next candle;
- use a pitchfork to identify the actual trade.

## The discretionary part

An Andrews' pitchfork needs hand-picked pivots, and the user did not give the pivot rule. It **cannot be backtested exactly**. Below, the pitchfork is replaced by three objective targets, and the report will say that this is a substitute.

## Data, 2025-01 to 2026-10 only

- **Source:** Exness 1-minute mid bars with their median spread, the same files as `../orb_study`. They are built into **15-minute candles** aligned to the UTC clock.
- **Markets:** XAUUSDm, USOILm, DE30m, US500m and USTECm.
- **Trading day:** the UTC date of t + 2h, the Exness day used throughout this repository. The day's high and low are those of the **previous trading day**, because the current day's high and low are not known until the day ends.

## Zones (2 versions)

With the previous day's high PH, low PL and height W = PH − PL:

| Version | Long area | Short area |
|---|---|---|
| Z50 | below the middle, close < PL + 0.5W | above the middle, close > PL + 0.5W |
| Z25 | the bottom quarter, close < PL + 0.25W | the top quarter, close > PH − 0.25W |

## Signal candle (2 versions), on 15-minute candles

| Version | Long signal | Short signal |
|---|---|---|
| S1 | any **bullish** candle (close > open) that closes in the long area | any bearish candle that closes in the short area |
| S2 | a **rejection** candle in the long area: bullish, with the lower wick ≥ 2× the body | the mirror: bearish, with the upper wick ≥ 2× the body |

## Entry, stop and target

- **Entry:** the **open of the next 15-minute candle**, ± half spread.
- **Stop:** just beyond the signal candle, at its low for a long and its high for a short. Fill at the stop ∓ half spread; a gap fills at the bar's level, with the stop counted first.

**Target (3 versions, standing in for the pitchfork):**

| Version | Target |
|---|---|
| T1 | 1R |
| T2 | 2R |
| TM | the previous day's middle, PL + 0.5W (mean reversion inside yesterday's range). Signals where the middle is not on the profitable side of the entry are skipped. |

## Trading rules

- **One position at a time.**
- **Unclosed trades** close at the end of the trading day (21:55 UTC).
- **No new entries** after 20:00 UTC.
- **Skipped:** days with no previous-day range, and signal candles whose stop distance is ≤ 2× the spread.
- **Costs:** results at 1× and 2× the median spread. Swap is 0, since all trades are intraday.

## Evaluation

The same as the ORB study:
- **Periods:** development 2025, holdout Jan–Oct 2026.
- **Unit:** R per trade.
- **Random control:** 500 draws. Each uses the same days and the same stop distances, entered at a random 15-minute candle open in the same day window, in a random direction, with the same target rule (TM uses the distance to the previous day's middle).
- **PASS needs all of:**
  - mean R > 0 at 2× spread in **both** periods;
  - at least 100 holdout trades;
  - mean R above the random 95th percentile in **both** periods.
- **Combinations:** 5 markets × 2 zones × 2 signals × 3 targets = **60**. About 0.15 false passes are expected.
- **Confirmation:** any PASS must be re-checked on raw ticks, with real gap fills, before it is reported as a candidate.
