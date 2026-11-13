# Batch 2 development results (EXPLORATORY ONLY: cannot PASS)

**Data and run**
- Window: 2025-01-01 to T0 (2026-11-12 19:10 UTC).
- These BTC and ETH prices had already been examined by earlier studies, so the results are exploratory only.
- This is run 2. Run 1 lacked the archived Deribit quarterlies and is kept as `results/*SUPERSEDED*` (see `IMPLEMENTATION_NOTES.md`).
- Data checks: 980,350 one-minute candles per coin with no gaps, no hourly gaps, and 11 quarterly futures per coin. Hyperliquid funding has 2 gaps over 1 h per coin.

**Mean net return per trade, in bp, at primary cost**

| Test | Trades | Mean (primary) | Mean (stress) | B1 random p | B2 placebo p | n_req | Trades per year | Years to n_req |
|---|---|---|---|---|---|---|---|---|
| H1_BTC funding | 24 | −19.1 | −35.3 | 0.54 | 0.55 | 48,977 | 12.9 | ≈ 3,800 |
| H1_ETH | 17 | −132.9 | −154.1 | 0.80 | 0.84 | 29,814 | 9.1 | ≈ 3,300 |
| H2_BTC basis | 27 | −46.4 | −82.6 | 0.60 | 0.62 | 25,504 | 14.5 | ≈ 1,760 |
| H2_ETH | 30 | −112.0 | −153.2 | 0.65 | 0.75 | 51,856 | 16.1 | ≈ 3,200 |
| H3_BTC taker flow | 581 | −5.7 | −7.7 | 0.85 | 0.84 | 681 | 311.5 | 2.2 |
| H3_ETH | 577 | −5.3 | −12.3 | 0.39 | 0.44 | 990 | 309.3 | 3.2 |
| H4_BTC vol premium | 24 | +140.1 | +103.9 | 0.08 | 0.08 | 26,766 | 12.9 | ≈ 2,075 |
| H4_ETH | 24 | −14.1 | −55.3 | 0.46 | 0.51 | 76,279 | 12.9 | ≈ 5,900 |

**Reading**
- **No test is significant, even before any correction.** The smallest p is H4_BTC's 0.08. Seven of the 8 tests are negative after costs.
- Benjamini–Hochberg correction across the programme's ≈ 110,000 tests makes this certain.

## Power finding (reported, not acted on: the rules are unchanged)

The pre-registered δ is a 10 bp edge, while trades held for several days have a standard deviation of 300–1,000 bp. So:

**H1, H2 and H4 (all 6 tests)**
- These tests need tens of thousands of trades, but get only about 9–16 a year.
- At the 24-month cap they will have about 18–32 trades.
- By the pre-registered rules they will almost certainly be **INCONCLUSIVE**: n_req is not reached. For H1 and H4, n is also likely below 30.
- They cannot reach a verdict in any useful time. Treat them as monitoring only.

**H3 (2 tests)**
- H3 is the only hypothesis that can be tested: it gets about 310 trades a year.
- n_req is 681 for BTC and 990 for ETH, which is about 2.2 and 3.2 years.
- Under the 24-month cap, these too will most likely end INCONCLUSIVE, unless the effect is large.
- H3 was negative in development.

Any change to δ, the cap or the tests would need a dated amendment to `PREREGISTRATION.md`, with a new forward clock for each changed test. It would also be informed by these development numbers, so it would not be fully blind. That is the user's decision.
