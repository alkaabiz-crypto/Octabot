# THE-017 event study: results. **NOT SUPPORTED**

Pre-registered in `PREREG.md` (commit `c420548e`). Output `results.json`; script `run_the017.py`.

**Effect** = next-hour return after oversold minus after overbought (Williams %R ≤ −80 / ≥ −20), in bp. The p-value is against labels shuffled within the same hour of day.

| Market | EARLY | TRAIN | VALIDATION | TEST (p) | Per event vs round-trip cost (TEST, bp) |
|---|---|---|---|---|---|
| BTC (discovery) | +1.80 | −0.09 | +5.16 | **−1.25** (0.82) | −0.59 vs 10.8 |
| EUR/USD (discovery) | — | +0.20 | +0.64 | +0.14 (0.34) | +0.08 vs 1.25 |
| Gold | +0.58 | −0.24 | +0.06 | −1.17 (0.84) | −0.57 vs 1.55 |
| Oil | −2.19 | −0.62 | −1.15 | +0.88 (0.36) | +0.28 vs 10.9 |
| S&P 500 | — | −0.08 | −1.59 | +0.06 (0.47) | −0.08 vs 1.71 |
| USD/JPY | — | −0.17 | −1.36 | −0.14 (0.68) | −0.02 vs 1.04 |
| GBP/USD | — | +0.58 | +0.26 | +0.39 (0.09) | +0.20 vs 1.22 |
| ETH | — | −1.45 | −5.05 | −1.24 (0.73) | −0.69 vs 12.2 |

**Verdict: NOT SUPPORTED.**
- The discovery markets do not hold in TEST: BTC is negative, and EUR/USD is positive but not significant.
- No replication market is significant.
- The small negative IC seen in IND batch 001 was a weak correlation across *all* readings. It does not show up as a reversal after extreme readings once time of day is matched.
- It would be untradable anyway: the per-event effect is ≤ 0.3 bp against 1–12 bp of costs.
