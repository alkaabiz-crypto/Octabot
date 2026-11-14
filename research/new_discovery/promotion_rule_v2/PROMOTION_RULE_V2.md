# Paper-test decision rule V2 (proposal, 12 November 2026)

**Status.** This is a **new, separately documented** decision rule. It does **not** change `research/library_forward/FORWARD_RULES.md` or any frozen file.
- The frozen rule keeps being reported exactly as written.
- V2 is reported **next to** it.

**When it was written.** Before any of the three library paper tests had a closed trade: ETH_FIB, OIL_FIB and GOLD_FVG had 0 of 100 at 19:16 UTC.

**Why it is needed** (`research/audits/library_candidates/CAUSAL_IMPACT_ASSESSMENT.md` §7). The frozen rule passes a test after 100 trades if the mean net is ≥ +2 bp at 2× costs.
- With zero true edge, that happens with probability **0.45** (ETH), **0.45** (oil) and **0.35** (gold).
- With the three tests run together, the chance is **0.80**.
- So a frozen-rule pass is not evidence of an edge.

## The rule

**Applies to** the three library paper tests. The **family is 3 tests**, and any test added later must be declared before its first trade.

**Data.** Each test's ledger column `net_bp_2x` (net per trade at 2× costs), in ledger order. No trade is excluded.

**Looks.** Evaluation happens only at **100, 300, 600 and 1,000** closed trades. There are no other looks.

At each look, with *m* the mean and *se* the Newey–West standard error of the mean (5 lags):

| Outcome | Condition |
|---|---|
| **PASS** | *m* / *se* ≥ **2.87** and *m* ≥ +2 bp |
| **STOP (futility)** | *m* + 1.645 · *se* < +2 bp, i.e. even the optimistic one-sided 95% bound is below +2 bp |
| **CONTINUE** | otherwise; after 1,000 trades without a decision, **UNDECIDED** (never a pass) |

**Where 2.87 comes from.** It is the one-sided normal quantile for α = 0.05 / (3 tests × 4 looks) = 0.0042 (Bonferroni across tests and looks). That keeps the family-wise false-pass rate below 5%.

**Also reported, but not deciding:** the frozen-rule verdict at 100 trades; a stationary block-bootstrap p-value; the win rate; drawdown.

**What a PASS means.** A V2 pass is evidence that a test has a real edge at 2× costs on new data. It is still **not** an instruction to trade real money. That would need a separate decision, with execution costs and fees on the actual venue.

## Operating characteristics

[CALC] From `operating_characteristics.py` → `operating_characteristics.json`. Paths of 1,000 trades were resampled (stationary block bootstrap, mean block 5) from each candidate's causal forward-model trades, re-centred to the true mean shown; 4,000 paths each.

| True mean per trade | ETH (sd 182.5 bp) | Oil (sd 151.9 bp) | Gold (sd 59.9 bp) |
|---|---|---|---|
| **0 bp: V2 false pass** | **1.8%** | **2.1%** | **0.85%** |
| 0 bp: frozen rule passes at 100 trades | 45.8% | 45.1% | 34.8% |
| 0 bp: V2 futility stop | 23% | 21% | 46% |
| +5 bp: V2 pass | 6% | 12% | **62%** |
| +10 bp: V2 pass | 22% | 45% | **99.9%** |
| +20 bp: V2 pass | 78% | 97% | 100% |
| causal backtest mean (−15.6 / −8.4 / −0.2 bp): V2 pass | 0.1% | 0.1% | 0.7% |
| same, V2 futility stop by 1,000 trades | 92% | 85% | 49% |

Family false-pass probability with all three at zero edge: 1 − (0.982 × 0.979 × 0.992) ≈ **4.7%**, against 80% under the frozen rule.

**Reading.**
- Gold's low volatility means a real edge of +5 to +10 bp would be detected within a few hundred trades.
- ETH and oil are so noisy that only an edge of about +20 bp per trade could be confirmed within 1,000 trades. At their trade rates, that is roughly 2–3 years.
- If the causal backtests are right, all three are most likely to end in a futility stop.

## Not changed by this document

- The forward test code, rules, states and ledgers.
- The frozen rule's own verdicts, which keep being reported.
- Any other paper test (Donchian, gold Asia, MOM50, oil stochastic, trend ensemble). Those have their own rules; this family does not include them.
