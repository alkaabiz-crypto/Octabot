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
