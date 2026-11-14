# Historical replay of the assistant's rules

Generated on 2026-11-09 with `python replay.py` on Binance BTCUSDT closed candles. The live decision
function was run at every closed 1H candle, using only candles closed by then.

**This is descriptive. It simulates no entries, exits, stops, sizing or costs, so it says nothing about
profitability, and the t-statistics are optimistic because consecutive signals overlap.**

## What the numbers show

- Over the full history (Dec 2018 to Nov 2026) a BUY signal fired on about 1.3% of candles, roughly
  one every three days. After a BUY the **mean** 48h move (+0.66%) was about twice the unconditional
  mean (+0.32%), but the **median** was close to zero (+0.01% vs +0.17%) and the share of positive
  outcomes (50%) was below the unconditional share (52.6%). In words: most breakouts fizzled, and the
  higher mean comes from a minority of large continuations. That is the usual trend-following shape and
  matches the separate Donchian study (about a third of trades win). Whether the large moves can be
  captured depends entirely on the exit rule, which this replay does not model.
- SELL signals were followed, on average, by **rising** prices (+0.28% mean at 24h, 58.5% positive),
  so bearish breakdowns did not predict further declines in this data. This agrees with the separate
  study, where every short variant failed. Treat SELL as "do not hold longs", not as a short entry.
- In the most recent 13 months (fixture period, a falling market) BUY signals were followed by
  negative average moves at every horizon (-0.61% mean at 48h, 39% positive). The rule set did not
  protect against a bear market and nothing here suggests it will.
- Confidence labels are rule agreement. Nothing in this replay shows that HIGH-agreement signals did
  better than MEDIUM or LOW ones, and no such claim is made.

Conclusion: there is no statistical evidence that this combined rule set is profitable. The only
component with out-of-sample support is the Donchian 20 long breakout with the 4H EMA200 filter
(separate study). Forward paper testing is the next step before anything else.

## Full history, 2900 days (2018-12-14 to 2026-11-09)

```
Replay of 69239 closed 1H candles, 2018-12-14 09:00 to 2026-11-09 19:00 UTC. Descriptive only: no trades, stops or costs simulated.

Recommendation frequency
  BUY       900  (  1.3% of candles)
  SELL      685  (  1.0% of candles)
  WAIT    64966  ( 93.8% of candles)
  AVOID    2688  (  3.9% of candles)

BUY signals: 900
  after a BUY signal                    |  all candles (unconditional)
   horizon      n    mean%  median%   pos%      t  |   horizon      n    mean%  median%   pos%      t
       4h    900    0.085   -0.073   46.1   1.67  |       4h  69235    0.026    0.018   51.2   5.39
      12h    900    0.222   -0.003   49.9   2.80  |      12h  69227    0.078    0.043   51.7   9.39
      24h    900    0.368    0.005   50.0   3.14  |      24h  69215    0.159    0.088   52.2  13.22
      48h    900    0.664    0.010   50.0   4.08  |      48h  69191    0.316    0.171   52.6  18.84
  Overlapping horizons make these samples dependent; t is optimistic. Mean forward return is not expectancy per trade.

SELL signals: 685
  after a SELL signal                    |  all candles (unconditional)
   horizon      n    mean%  median%   pos%      t  |   horizon      n    mean%  median%   pos%      t
       4h    685    0.077    0.143   57.5   1.11  |       4h  69235    0.026    0.018   51.2   5.39
      12h    685    0.091    0.198   54.6   0.92  |      12h  69227    0.078    0.043   51.7   9.39
      24h    685    0.278    0.405   58.5   1.96  |      24h  69215    0.159    0.088   52.2  13.22
      48h    685    0.104    0.247   54.6   0.56  |      48h  69191    0.316    0.171   52.6  18.84
  Overlapping horizons make these samples dependent; t is optimistic. Mean forward return is not expectancy per trade.

BUY signals by confidence label: HIGH 289, LOW 123, MEDIUM 488

Verdict on profitability: NONE. This replay cannot establish an edge. Use the forward paper test procedure for that.
```

## Fixture period, 400 days (2025-10-18 to 2026-11-09)

```
Replay of 9299 closed 1H candles, 2025-10-18 09:00 to 2026-11-09 19:00 UTC. Descriptive only: no trades, stops or costs simulated.

Recommendation frequency
  BUY        72  (  0.8% of candles)
  SELL      140  (  1.5% of candles)
  WAIT     8235  ( 88.6% of candles)
  AVOID     852  (  9.2% of candles)

BUY signals: 72
  after a BUY signal                    |  all candles (unconditional)
   horizon      n    mean%  median%   pos%      t  |   horizon      n    mean%  median%   pos%      t
       4h     72    0.006   -0.006   50.0   0.08  |       4h   9295   -0.011    0.003   50.3  -1.16
      12h     72   -0.105   -0.148   40.3  -0.60  |      12h   9287   -0.034    0.010   50.4  -2.09
      24h     72   -0.281   -0.398   38.9  -1.27  |      24h   9275   -0.068    0.006   50.1  -2.91
      48h     72   -0.608   -0.867   38.9  -2.26  |      48h   9251   -0.136   -0.072   48.9  -4.14
  Overlapping horizons make these samples dependent; t is optimistic. Mean forward return is not expectancy per trade.

SELL signals: 140
  after a SELL signal                    |  all candles (unconditional)
   horizon      n    mean%  median%   pos%      t  |   horizon      n    mean%  median%   pos%      t
       4h    140   -0.100    0.078   55.0  -0.81  |       4h   9295   -0.011    0.003   50.3  -1.16
      12h    140   -0.029    0.211   53.6  -0.17  |      12h   9287   -0.034    0.010   50.4  -2.09
      24h    140   -0.100    0.152   52.1  -0.41  |      24h   9275   -0.068    0.006   50.1  -2.91
      48h    140   -0.725   -0.616   42.1  -2.17  |      48h   9251   -0.136   -0.072   48.9  -4.14
  Overlapping horizons make these samples dependent; t is optimistic. Mean forward return is not expectancy per trade.

BUY signals by confidence label: HIGH 19, LOW 18, MEDIUM 35

Verdict on profitability: NONE. This replay cannot establish an edge. Use the forward paper test procedure for that.
```
