# Programme-wide forward evaluation plan

**Authority:** the user's permission of 2026-11-12 to correct wrong rules or judgments.

**What does not change:** trading rules, frozen strategy files and ledgers. This plan only fixes **how results will be judged**.

**Implementation:** `forward_eval/evaluate.py`, frozen by fingerprint in `forward_eval/EVAL_MANIFEST.sha256`. The plan and the code must agree; if they ever differ, it is an error to be reported, not resolved silently.

**Revision history**
- **2026-11-12, first version:** 7 confirmatory tests, p ≤ 0.0071.
- **2026-11-12, this revision, still with zero forward trades in every test:**
  - The three library candidates are demoted to monitoring. Their historical edge was an order-handling look-ahead (`library_checks/README.md`).
  - H3 now faces the same programme-wide bar as the other tests (`batch2/AMENDMENT_2.md`). Before this, it used a looser Holm test at α = 0.05, which contradicted the plan.
  - Oil Stochastic's metric is stated correctly as bp.

## Confirmatory family: 4 tests (Bonferroni, one-sided random-timing p ≤ 0.05/4 = 0.0125)

| Test | Judged at | Metric |
|---|---|---|
| Donchian BTC (BINANCE PROXY) | trade 40 of the LIVE-executed trades | executable R per trade at 0.05% cost; it must also be > 0 at 0.10% |
| Oil Stochastic (Hyperliquid xyz:CL) | trade 100 | net bp per trade after the 0.02 USD/bbl spread |
| Batch 2 H3_BTC | its evaluation date (`batch2/AMENDMENT_1.md`, n_req 479, cap 2029-11-14) | net bp at pre-registered primary cost; stress must also be > 0 |
| Batch 2 H3_ETH | the same (n_req 697) | the same |

**A PASS also needs a clean independent audit** of the ledger. Until then the evaluator reports **PASS_PENDING_AUDIT**.

**A PASS means more paper testing at real Exness prices** (`data_audit/proxy_reconciliation`), never live money without the user's decision.

## Monitoring only (keep running and reporting; can never PASS)

| Test | Why |
|---|---|
| GOLD_FVG, OIL_FIB, ETH_FIB | Their historical edge came from look-ahead in order handling (`library_checks/README.md`). They are kept as plain observation. |
| TREND_ENS BTC and ETH | An allocation bot with a few changes a year; no test with useful power |
| Gold MOM50 | About 20 trades take years; too few to separate skill from gold's trend |
| Batch 2 H1, H2, H4 (6 tests) | Power: 25,000+ trades needed (`batch2/AMENDMENT_1.md`) |

## Operational rules (as implemented)

**Blind**
- Until a test is due, the evaluator shows only its progress count.
- No running statistics or p-values are produced for confirmatory tests.

**Random-timing benchmark** (Donchian and Oil Stochastic; 1,000 draws, seed 20261113 + CRC32 of the test ID + stage)
- Each real trade keeps its side, its exact holding time and its cost model.
- Its start is drawn uniformly among 1-minute candles between the test's start and the exit of the last evaluated trade.
- **Prices:**
  - Binance spot 1m for BTC, re-fetched at evaluation;
  - Hyperliquid 1m for xyz:CL, from the append-only archive `forward_eval/prices/`, because Hyperliquid serves only the last ≈ 3.5 days.
- Price coverage below 99% is flagged.
- p = (1 + number of draws with a mean ≥ the observed mean) / (1 + draws).

**Stage 1** (the first *target* trades)
- **PASS_PENDING_AUDIT:** the mean is > 0 at the stated cost, and p ≤ 0.0125.
- **FAIL:** the mean is ≤ 0, or p > 0.5.
- **INCONCLUSIVE:** anything else. The test continues to 2× target.

**Stage 2** (the first 2× target trades)
- **PASS_PENDING_AUDIT** under the same rules, otherwise **NOT_CONFIRMED**.
- There are no further looks.

**Donchian**
- Only trades with a LIVE execution record count (`btc_breakout/forward/EVALUATION_RULES.md`).
- The metric is (frozen exit − ask fill) / rule risk − 0.05% × ask / rule risk.
- Stage 1 is the verdict of trades 1–40 under that file. Stage 2 applies only if Stage 1 is INCONCLUSIVE.

**Batch 2 H3**
- Rules: the batch's own pre-registered B1 (random entry) and B2 (placebo) code.
- **PASS** needs all of:
  - B1 p ≤ 0.0125;
  - B2 p ≤ 0.05;
  - primary and stress means > 0;
  - n ≥ 30 and n ≥ n_req.
- **FAIL:** the primary mean is ≤ 0, or B1 p > 0.5.
- **INCONCLUSIVE:** anything else.
- If B2 cannot be drawn, the test cannot PASS.

## Checked on synthetic data (`forward_eval/selftest.py`, `selftest_extra.py`)

- Skilled (look-ahead) ledgers pass, and random ledgers do not.
- On 300 random ledgers the false-pass rate was 4/300 = 1.3%, which matches the 1.25% bar.
- The cost formulas reproduce the ledgers' own figures.
- The H3 dating and verdict logic work.

## Rules kept on review

- **No market data before 2025.** Older data cannot serve as an untouched test set, because the other branch's long-history studies already used it for BTC, oil and gold (`research/audit/reports/rescore/long_*.json` on `claude/dazzling-albattani-j6uys7`).
- **Paper only;** no circumventing geo-restrictions; no restricted raw data in the repository.
