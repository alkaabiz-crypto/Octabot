# User theories 001: pre-registration (written 2026-11-12, before any code or result for these tests)

Two theories described by the user. Nothing frozen is changed. Theory #2b is a new study; it does not replace the frozen Theory #2 (`research/zone_reversal_study`, other branch). The wick test calls the frozen library function `theories.c2` unchanged.

**Data:** the same sources as the frozen library.
- Exness XAUUSDm, USOILm, DE30m, US500m and USTECm 1-minute mid bars with their median spread, 2025-01-01 to 2026-10-30.
  - Rebuilt from the public monthly tick zips with the frozen `orb_study/build_bars.py` `bars()` function.
  - The gold and oil zip SHA-256s match the hashes recorded by the other session.
  - With these bars, the frozen screen rows are reproduced exactly (`CAUSAL_IMPACT_ASSESSMENT.md`).
- Binance BTCUSDT and ETHUSDT 1h (the library's own files). Crypto has no 15-minute data, so 15m is not run for crypto.
- **Periods:** development 2025; holdout 2026-01 to 2026-10. Both periods were already used by earlier studies, so a PASS is **screening evidence only** and would need a forward period.

## Test A: Theory #2b, day-range zones from the SAME day's opening range

**User's description:** use the day's high and low (the same day, not the previous day) to judge where price is; 15-minute chart; longs only in the long area and shorts only in the short area; wait for a signal candle; enter on the next candle. The user chose the **opening range** interpretation. The day's final high and low cannot be used, because they are unknown until the day ends.

**Rules:** identical to the frozen Theory #2 (`zone_reversal_study/PREREGISTRATION.md`), except for the range and the trading window.
- **Trading day:** the Exness day, which starts at 22:00 UTC (the UTC date of t + 2h).
- **Opening range:** the high OH and low OL of all 1-minute bars from the start of the trading day up to 07:00 UTC (the Asian session). The range needs at least 120 one-minute bars, and W = OH − OL > 0.
- **Signal candles:** 15-minute candles that open at or after 07:00 UTC, with the next candle (the entry) opening no later than 20:00 UTC.
- **Zones:**

  | Version | Long area | Short area |
  |---|---|---|
  | Z50 | close < OL + 0.5W | close > OL + 0.5W |
  | Z25 | close < OL + 0.25W | close > OH − 0.25W |

- **Signal candles:** S1 is any bullish (bearish) candle closing in the long (short) area. S2 is a rejection candle: bullish, lower wick ≥ 2× the body (mirror for shorts).
- **Entry:** the next 15-minute open ± half spread.
- **Stop:** beyond the signal candle. Skip if the stop distance is ≤ 2× the spread.
- **Targets:** T1 = 1R; T2 = 2R; TM = the opening-range middle (skip if it is not on the profitable side).
- **Positions:** one at a time; close at the end of the trading day; costs at 1× and 2× the median spread.
- **Random control and PASS rule:** exactly as the frozen Theory #2.
  - Random control: 500 draws, same days and stop distances, random 15m entry in the same window, random direction.
  - PASS: mean R > 0 at 2× in both periods, ≥ 100 holdout trades, and above the random 95th percentile in both periods.
- **Combinations:** 5 markets × 2 zones × 2 signals × 3 targets = **60**.

## Test B: "John Wick's theory", wick rejection candles

**User's choice:** candle wick rejection. A long lower wick means buyers rejected lower prices (go long); mirror for shorts.

**Rule:** the frozen library's **C2** (pin bar / hammer), called unchanged (`theories.py` `c2` + `px_trade`).
- **Long:** lower wick ≥ 2× the body, and the body in the top third of the range. Short is the mirror.
- **Entry:** next candle open.
- **Stop:** the wick extreme.
- **Target:** 2R.
- **Time stop:** 20 candles.
- **Costs:** the library's half spread per side (crypto 0.05% per side), reported at 1× and 2×.

**Timeframes:**
- 1h was already tested in the frozen screen (all 7 FAIL). It is re-run only as a reference, and **does not count as new**.
- **New:** 15m, 4h and 1d on the 5 Exness markets; 4h and 1d on BTC and ETH. That is **19 new combinations** (15 Exness + 4 crypto), plus 7 reference.

**Evaluation:** the frozen screen's rule (`run.py`), with the same 500-draw random control and seeds formula.
- PASS: mean > 0 at 2× in both periods, ≥ 30 holdout trades, and above the random 95th percentile in both periods.
- Also reported: the iid t, a Newey–West t (5 lags) and Benjamini–Hochberg at 5% across the 19 new tests, using one-sided t p-values on the holdout.
- **Known weakness:** the random control's 95th percentile can sit below zero (see `CAUSAL_IMPACT_ASSESSMENT.md` §7), so the t-statistics are reported alongside it.

## Look-ahead check

Both tests enter at the next candle's open with one position at a time. No pending orders, so they are **not exposed** to the order-selection bug.

## Multiple testing

79 new tests (60 + 19). About 0.15 + 0.05 false passes are expected under the frozen rules. Any PASS is a screen result only.
