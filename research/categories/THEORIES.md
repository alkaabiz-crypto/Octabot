# Category protocol: Theories (THE)

**Definition.** A claim about how markets behave, independent of any one trading rule. Examples: "CME gaps fill", "round numbers act as support", "gold falls at the London fix".

**Question.** Is the claim true, and is it still true now?

## Test: an event study

1. **Prediction.** Write down exactly what the claim predicts and measure that, not a trading P&L. Examples:
   - the probability that the gap fills within *N* hours;
   - the frequency of reversal at a round level;
   - the average move in the window.
2. **Matched null.** The same measurement at random times with the same conditions: same session, volatility bucket and distance.
3. **Effect size.** Report the difference from the null with a dependence-aware confidence interval. Require ≥ 100 events.
4. **Replication.** In at least one other market or period, including an older period where data exist.
5. **Decay check.** Report the effect by era (for example before and after publication, or before and after 2015).

## Verdicts

| Verdict | Conditions |
|---|---|
| **SUPPORTED** | Effect in the predicted direction, significant, and replicated |
| **DECAYED** | Supported in older data, absent recently |
| **PARTLY SUPPORTED** | Holds in some markets or definitions, not others |
| **NOT SUPPORTED** | Otherwise |

**What a SUPPORTED or PARTLY SUPPORTED theory leads to.** It may become a new, pre-registered STR candidate. Whether it is *tradable* after costs is a strategy question, not a theory question.
