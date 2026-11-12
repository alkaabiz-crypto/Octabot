# Batch 001 summary

Pre-registration: `PREREG.md` (commit `ceb74bd2`, made before any result). Results: `RESULTS.md` and `results/batch_001.json`. Registry: `../REGISTRY.csv`. One pre-set setting per idea, with no parameter search: 26 tests in total.

## What was tested

| ID | Idea (family) | Markets | Result in the untouched TEST period (2025-07 to 2026-11) | Decision |
|---|---|---|---|---|
| D001 | Statistical-arbitrage pairs: spread z-score reversion (new family) | Brent/WTI, EUR/USD–GBP/USD, Nasdaq/S&P | −5.2, +3.0 and −4.3 bp per trade. EUR/USD–GBP/USD had p 0.025 in TEST, but its VALIDATION period was negative (−1.1 bp) and it does not survive the correction. | REJECT ×3 |
| D002 | Cross-market relative strength, 11 markets (new family) | portfolio | −18.8 bp per week (Sharpe −0.34); TRAIN −40.9, VALID +11.7 | REJECT |
| D003 | Regime-adaptive trend / mean reversion by efficiency ratio (original combination) | 11 markets, 4h | Positive in TEST only for gold (+7.1), BTC (+5.3) and GBP/USD (+0.2), and none of those was positive in TRAIN. Strongly negative for both oils, Nasdaq and S&P. | REJECT ×11 |
| D004 | Walk-forward logistic model on 8 price features (machine learning) | 11 markets, 1h | Negative or about zero after costs in TEST for 9 of 11 markets. The positive ones, US oil (+3.0) and GBP/USD (+2.2, 55 trades), were negative in TRAIN. | REJECT ×11 |

Benjamini–Hochberg over the 26 TEST p-values: **0 significant**. No experiment was positive in all three periods, so none is a CANDIDATE or WATCH.

## Why they failed (what the data says)

- **Pairs.**
  - Over 120 hours, the spreads rarely reverted. 72–81% of trades in each pair ended on the time limit or the stop, not on a return to the mean.
  - The Brent/WTI CFD spread has **34 jump hours** (the brokers' futures rolls happen on different dates), and 17 of 113 trades span one. The two oil CFDs make a poor pair, because their rolls create artificial spread moves.
  - EUR/USD–GBP/USD is close to break-even before costs, and costs (about 1.6 bp per trade at stress) remove it.
- **Relative strength.**
  - Eleven markets are too few for a stable cross-section, and the long-short book swung hard (worst drawdown 50% of gross).
  - Equal-weight long-all made more in every period (+21 to +54 bp per week), because 2023–26 was a broad up-market. Ranking added nothing.
- **Regime-adaptive.**
  - The trend part made money only in gold (+10.9 bp) and BTC (+7.3) in TEST, and lost heavily in oil and US indices.
  - The range part was about zero or negative everywhere except Nasdaq (+3.9).
  - Switching between them did not make either part work.
- **Machine learning.**
  - The model traded about 20% of the hours, and its hits did not beat random signs on the same trades.
  - The eight price features hold little information about the next 4 hours beyond the spread cost. This is the same message as the earlier indicator scans, now with a multivariate model.

## Strongest results (none qualifies)

- **EUR/USD–GBP/USD pair:** TEST +3.0 bp, p 0.025, profit factor 1.53. Its VALIDATION period was negative, it is negative at stress cost (−5.7) and it fails the correction. It is recorded here and is **not** a candidate.
- **D003 trend part on gold:** +10.9 bp in TEST. It is information only, not a pre-registered decision. Gold's strong 2025–26 trend is the likely cause, as in earlier studies.

## Data limitations found

- No exchange volume, volume delta or order book exists in the Exness CFD feed. Order-flow ideas need another source.
- Oil CFD roll jumps make WTI/Brent spread work unreliable without a roll-adjusted futures series.
- Swaps are not in the data, and the stress cost is only a proxy.

## Next batch (batch 002): information this data has not covered

Price-only rules have now failed across both research branches: more than 100 families and roughly 100,000 market-variant tests. The best remaining chance is **new kinds of information**, not new transforms of the same candles:

1. **Crypto funding rates and basis** (Binance perpetual funding history, public). Hypothesis: extreme funding (crowded leverage) predicts reversal or carry returns. Evidence includes work on crypto carry, for example Schmeling, Schrimpf and Todorov (BIS, 2023), "Crypto carry".
2. **True order flow on BTC and ETH** (Binance public aggregated trades, signed by aggressor side). Hypothesis: persistent taker imbalance predicts the next hours (order-flow literature, for example Cont, Kukanov and Stoikov (2014)).
3. **The BTC options volatility risk premium** (Deribit DVOL index, public). Hypothesis: implied minus realised volatility predicts BTC returns or volatility.
4. **FX carry from interest-rate differentials** (FRED policy and 2-year yields). Hypothesis: the forward-premium puzzle (Lustig and Verdelhan) applied to EUR/USD, GBP/USD and USD/JPY.

Each will be pre-registered with one setting before it is run, with the same periods, costs and controls.
