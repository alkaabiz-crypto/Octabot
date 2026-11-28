# THE-005 event study: results

Pre-registered in `PREREG.md` (commit `70d8c380`). Output `results.json`; script `run_the005.py`. Data: Exness 15-minute mid candles.

**Effect** = rate at round levels minus rate at half-grid ("ordinary") levels, in percentage points. One-sided p in the predicted direction.

## (a) Reversal at round levels: **NOT SUPPORTED**

| Market | EARLY | TRAIN | VALIDATION | TEST (p) | TEST events (round) |
|---|---|---|---|---|---|
| Gold | −3.64 | −0.63 | −2.80 | −0.98 (0.79) | 3,066 |
| Oil | −0.77 | +1.14 | −0.20 | +1.45 (0.21) | 1,479 |
| EUR/USD | — | −2.76 | +6.63 | −5.90 (0.84) | 129 |
| USD/JPY | — | +0.56 | +4.56 | −0.24 (0.53) | 421 |
| S&P 500 | — | +1.63 | +0.39 | −4.98 (0.98) | 786 |
| BTC | −5.67 | −3.32 | −2.62 | −4.01 (0.99) | 2,000 |

Round levels do **not** turn price around more often than ordinary levels. On BTC and gold they do so *less* often, consistently across periods.

## (b) Acceleration after crossing a round level: **DECAYED**

| Market | EARLY | TRAIN | VALIDATION | TEST (p) |
|---|---|---|---|---|
| Gold | **+2.19 (p 0.03)** | **+4.13 (p 0.008)** | +1.60 | −0.36 (0.65) |
| Oil | +1.36 | −1.96 | +0.43 | −0.90 |
| EUR/USD | — | +2.53 | −3.69 | +0.91 |
| USD/JPY | — | +1.00 | −5.88 | −0.29 |
| S&P 500 | — | +1.78 | −0.00 | +2.52 (0.15) |
| BTC | +0.49 | +1.09 | +2.32 (0.06) | +1.92 (0.09) |

**Reading.**
- On gold, moves continued past round levels more often in 2020–2024, consistent with stop-loss clustering, but not since mid-2025.
- BTC is weakly positive in every period, but never significant.
- No market qualifies for SUPPORTED.
