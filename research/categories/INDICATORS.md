# Category protocol: Indicators (IND)

**Definition.** A measurement computed from market data. It makes no trading decision by itself.

**Question.** Does it carry information about future price moves (or, for volatility indicators, future volatility)?

## Test: the information coefficient (IC)

1. **Orientation.** Each indicator is turned into a number *x* at each candle close, oriented so that "higher" means its usual bullish reading. The orientation is fixed in the pre-registration.
2. **Target.**
   - Direction indicators: the forward log return over *h* ∈ {1h, 4h, 1d, 5d}, from the next candle's open. There is no overlap: samples are taken every *h*.
   - Volatility indicators: the forward absolute return or realised volatility.
3. **Statistic.** Spearman rank correlation (IC), per market, horizon and period (TRAIN / VALIDATION / TEST, plus EARLY where the data exist). The p-value comes from the t of the IC on non-overlapping samples.
4. **Baseline.**
   - The market's own last-period return. The indicator's IC is reported with and without it (partial IC).
   - An indicator that only re-states recent returns is labelled **REDUNDANT**.
5. **Multiple testing.** Benjamini–Hochberg at 5% across every TEST-period (indicator × market × horizon) test in the batch.

## Verdicts

| Verdict | Conditions |
|---|---|
| **INFORMATIVE** | Same IC sign in every available period; TEST p ≤ 0.05 after BH; partial IC also significant; in ≥ 3 markets, or in ≥ 2 periods for a single-market indicator |
| **WEAK** | Same sign in every period, but not significant after BH, or in only 1–2 markets |
| **REDUNDANT** | Significant IC, but the partial IC is not |
| **NONE** | Otherwise |

**No costs.** An indicator is not a trade. Costs come in when an INFORMATIVE indicator is turned into a pre-registered STR candidate.
