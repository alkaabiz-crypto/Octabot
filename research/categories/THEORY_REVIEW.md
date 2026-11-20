# Theory review: is each verdict based on the theory test, or only on a trading test? (2026-11-13)

The theory protocol (`THEORIES.md`) asks whether a **claim** is true: an effect measured against a matched baseline. A trading P&L test answers a different question. This review checks every THE candidate.

| ID | Claim | Evidence so far | Basis | Verdict stands? |
|---|---|---|---|---|
| THE-001 | Prev-day range zones + a signal candle predict direction | 60 rule variants, P&L vs a random control | P&L only | **Needs an event study** |
| THE-002 | Same-day opening-range zones + a signal candle predict direction | as THE-001 | P&L only | **Needs an event study** |
| THE-003 | A long wick (pin bar) predicts a reversal | C2 rule P&L on 4 timeframes | P&L only | **Needs an event study** |
| THE-004 | CME weekend gaps get filled | Fill (target) vs stop counts per gap, every period | Effect-based (fill outcome per event) | Yes: NOT SUPPORTED |
| THE-005 | Round numbers stop and reverse price | Event study: round vs half-grid levels | Event study | Yes: NOT SUPPORTED / DECAYED |
| THE-006 | Gold and silver fall around the London fix | Fix-window return vs random windows on the same days | Event study | Yes: DECAYED |
| THE-007 | Pre-FOMC drift | 24 h pre-FOMC return vs the same clock time on normal days | Event study | Yes: NOT SUPPORTED |
| THE-008 | Pre-holiday effect | Pre-holiday return vs random ordinary days | Event study | Yes: WATCH |
| THE-009 | Term-structure premium | Monthly premium by curve state | Effect-based | Yes: DECAYED |
| THE-010 | News reactions continue | Post-release rule vs the same clock on normal days | Event study | Yes: NOT SUPPORTED |
| THE-011 | BTC leads ETH | Laggard return after leader moves vs random signs | Effect-based | Yes: NOT SUPPORTED |
| THE-012 | Volatility-managed exposure improves Sharpe | Sharpe difference vs constant exposure | Effect-based (the claim is about Sharpe) | Yes: NOT SUPPORTED |
| THE-013 | Volatility has long memory | Forecast loss, HAR vs EWMA | Effect-based | Yes: WATCH |
| THE-014 | Coinbase premium = US demand leading BTC | Premium-conditioned returns vs random, 3 venues, ETH | Effect-based | Yes: PARTLY SUPPORTED |
| THE-015 | Calendar effects (turn of month, weekdays, overnight, weekend) | Library rule P&L vs the screen's weak random control | P&L only | **Needs an event study** |
| THE-016 | ICT/SMC: fair value gaps get filled, order blocks hold, liquidity sweeps reverse | Library rule P&L (FVG edge was look-ahead) | P&L only | **Needs an event study** |
| THE-017 | 1-hour reversal after overbought/oversold | Event study | Event study | Yes: NOT SUPPORTED |

**Action.** THE-001, THE-002, THE-003, THE-015 and THE-016 get pre-registered event studies (theory event batch 001), to finish goal G3 by 2026-12-15. Their current verdicts stay until then, marked "P&L-based".
