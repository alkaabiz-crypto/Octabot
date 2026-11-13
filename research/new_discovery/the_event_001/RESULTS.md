# Theory event batch 001: results

Pre-registered in `PREREG.md` (commit `acfa0a68`). Script `run_events.py`, output `results.json`.

**A bug was fixed before any result was recorded.** The Exness trading-day index was wrong because pandas stored timestamps in seconds, so all data fell into one "day". It is fixed in the committed script, and verified: 1,770 distinct days for gold.

**Effect** = the mean signed forward return in the predicted direction (bp). For THE-016 it is the fill rate minus the matched random retrace rate (percentage points). The p-value is against a matched shuffle null.

| ID | Claim | Verdict | Key numbers |
|---|---|---|---|
| THE-001 | Previous-day zones + signal candle | **PARTLY SUPPORTED: S&P 500 only** | S&P 500: TRAIN +0.40 bp (p 0.02), VALIDATION +1.16 (0.009), TEST **+1.26 (p < 0.001)**, 12,739 TEST events. Gold, oil and BTC negative or zero; EUR/USD TRAIN only. |
| THE-002 | Same-day opening-range zones + signal candle | **DECAYED** | S&P 500 TRAIN +1.96 (p < 0.001), then −0.89 / −0.12; others negative or zero |
| THE-003 | Pin bar → reversal | **NOT SUPPORTED** | Gold, oil and EUR/USD positive in VALIDATION only; BTC negative in every period |
| THE-015a | Turn of the month positive | **DECAYED** | Gold EARLY +20.7 bp/day (p 0.02), S&P TRAIN +32.1 (0.03); not significant since; oil negative |
| THE-015b | Mondays weaker | **NOT SUPPORTED** | No market significant in the predicted direction |
| THE-016 | Fair value gaps get filled | **DECAYED** | BTC +1.9 / +1.4 / +1.8 / +0.95 pp in every period, significant only in EARLY (p 0.005); gold, oil, S&P and EUR/USD about 0 or negative |

**Caveats and reading.**
- **THE-001 on the S&P 500 is true but tiny.** The effect is about 1.3 bp per signal over 4 hours, below the S&P CFD's round-trip cost (about 1.7 bp).
- Signal candles occur on many consecutive 15-minute candles, so events overlap. A shuffle within the hour of day does not fully account for that, and the p-values are probably optimistic.
- The P&L test of the full Theory #2 rule on the S&P 500 lost money. So this does **not** make Theory #2 tradable. It supports only the narrow claim, on the S&P 500.
- BTC fair-value gaps fill slightly more often than chance in every period. The effect is small, and significant only in 2020–22.
