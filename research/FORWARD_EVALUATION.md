# Programme-wide forward evaluation plan (2026-11-12)

**Authority:** the user's permission of 2026-11-12 to correct wrong rules or judgments.

**What does not change:** trading rules, frozen files and ledgers. This plan only fixes **how results will be judged**. Until now, each older test had only a round-number trade count, with no stated pass test.

## Confirmatory family: 7 tests (Bonferroni, one-sided p ≤ 0.05/7 ≈ 0.0071)

| Test | Judged when | Primary metric |
|---|---|---|
| Donchian BTC (BINANCE PROXY) | 40 valid trades | mean R per trade (executable) |
| Oil Stochastic | 100 closed trades | mean net USD per trade |
| GOLD_FVG, OIL_FIB, ETH_FIB | 100 closed trades each | mean net bp per trade at **2× cost** |
| Batch 2 H3_BTC, H3_ETH | `batch2/AMENDMENT_1.md` | per the Batch 2 pre-registration |

**A test PASSES only if all of these hold:**
1. Its forward mean is > 0 at its stated cost (2× for the library candidates).
2. A **random-timing benchmark** beats it with p ≤ 0.0071. The benchmark uses the same sides and holding times at random start times inside the same forward period, with 1,000 draws.
3. An independent audit of the ledger is clean.

**Weak samples:** if the sample is complete but too weak (the 95% CI includes both 0 and an economically meaningful edge), the result is **INCONCLUSIVE**. The test keeps running to 2× the sample and is judged once more, with the same bar.

**A PASS means more paper testing at real Exness prices** (`data_audit/proxy_reconciliation`), never live money without the user's decision.

## Monitoring only (keep running and reporting; can never PASS)

| Test | Why |
|---|---|
| TREND_ENS BTC and ETH | Allocation bot, a few changes a year; no test with useful power |
| Gold MOM50 | About 20 trades take years; too few to separate skill from gold's trend |
| Batch 2 H1, H2, H4 (6 tests) | Power: 25,000+ trades needed (`batch2/AMENDMENT_1.md`) |

## Rules kept on review

- **No market data before 2025.** Older data cannot serve as an untouched test set, because the other branch's long-history studies already used it for BTC, oil and gold (`research/audit/reports/rescore/long_*.json` on `claude/dazzling-albattani-j6uys7`).
- **Paper only;** no circumventing geo-restrictions; no restricted raw data in the repository.

## Operational rules, as implemented in `forward_eval/evaluate.py` (frozen 2026-11-12, before any forward trade)

**Blind**
- Until a test is due, the evaluator shows only its progress count.
- No running p-values or statistics are produced for confirmatory tests.

**Random-timing benchmark** (1,000 draws, seed 20261113 + CRC32 of the test ID + stage):
- Each real trade keeps its side, its exact holding time and its cost model.
- Its start is drawn uniformly among 1-minute candles between the test's start and the exit of the last evaluated trade.
- Prices:
  - Binance spot 1m for BTC and ETH, re-fetched at evaluation;
  - Hyperliquid 1m for xyz:GOLD and xyz:CL, from the append-only archive `forward_eval/prices/`, since Hyperliquid serves only the last ≈ 3.5 days.
- If price coverage is below 99%, the result is flagged.
- p = (1 + number of draws with a mean ≥ the observed mean) / (1 + draws).

**Stage 1** (the first *target* trades):
- **PASS_PENDING_AUDIT:** the mean is above 0 at the stated cost, and p ≤ 0.0071. Donchian must also be above 0 at the 0.10% cost.
- **FAIL:** the mean is at or below 0, or p > 0.5.
- **INCONCLUSIVE:** anything else. The test continues to 2× target.

**Stage 2** (the first 2× target trades):
- **PASS_PENDING_AUDIT** under the same rules, otherwise **NOT_CONFIRMED**.
- There are no further looks.

**Donchian**
- Only trades with a LIVE execution record count (`btc_breakout/forward/EVALUATION_RULES.md`).
- The metric is executable R: (frozen exit − ask fill) / rule risk − 0.05% × ask / rule risk.
- Stage 1 is the verdict of trades 1–40 under that file. Stage 2 applies only if Stage 1 is INCONCLUSIVE.

**Batch 2 H3**
- Rules: `batch2/PREREGISTRATION.md` with `AMENDMENT_1.md`, using that batch's own B1/B2 code.
- **Holm** across H3_BTC and H3_ETH on B1. While only one of the two is due, it is compared with α/2 (conservative).
- If B2 cannot be drawn, the test cannot PASS.

**PASS_PENDING_AUDIT** becomes PASS only after the independent ledger audit is clean.

**Checked on synthetic data** (`forward_eval/selftest.py`, `selftest_extra.py`):
- skilled (look-ahead) ledgers pass, and random ledgers do not;
- on 300 random ledgers the false-pass rate was 2/300 = 0.7%, which matches the 0.0071 bar;
- the cost formulas reproduce the ledgers' own figures.
