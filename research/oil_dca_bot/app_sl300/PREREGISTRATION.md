# Oil bot with the app's minimum 300-pip stop: pre-registration

Committed **2026-11-11, before running.** The user's app (screenshot 12:32 UAE) rejects stops below **300 pips**.
- **Pip check:** the app shows 88 pips = +8.80 USD at 0.01 lot, so 1 pip = 0.01 USD of price. That matches the model.
- **What changes:** only the exits. Same data, periods, costs and pass rules as `../app_conditions`.

## Exits tested (all with no extra orders, 0.01 lot, 4-pip trailing after TP)

| ID | TP | SL |
|---|---|---|
| S1 | 100 pips | 300 pips |
| S2 | 200 pips | 300 pips |
| S3 | 300 pips | 300 pips |

## Entries

The three 4H oscillators that were positive in both periods in `../app_conditions`: **Stochastic, MFI, Bollinger**. That gives 3 entries × 3 exits = 9 combinations.

## Pass (judged on the holdout)

1. net > 0 in the development period (2025) and the holdout (Jan–Oct 2026), at 1× and 2× spread;
2. holdout max drawdown < 408 USD;
3. at least 30 holdout baskets.

**Random control:** random direction with the same exit, 200 runs. The rule's holdout net must beat its **90th percentile**.

The best passing combination by holdout net at 2× becomes the recommended app setting. If none passes, the answer is that the app's 300-pip minimum stop removes the edge.
