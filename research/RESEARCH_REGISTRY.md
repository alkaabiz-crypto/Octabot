# Programme-wide research registry (both branches): never reset

**Purpose:** to count every hypothesis and variant tested anywhere in this research programme, so that multiple-testing corrections use the true total. Counts marked "≈" are taken from the cited files and are approximate.

## Branch `claude/dazzling-albattani-j6uys7` (read-only from here)

| Item | Tests | Source |
|---|---|---|
| TradingView built-ins, ChartArt and community scripts with filters, 33 Exness markets (long_history / multi_market) | **≈ 100,000** market-variant tests | `research/new_discovery/README.md` on that branch ("roughly 100,000") |
| New Discovery batch_001 (D001–D004) | 26 | `research/new_discovery/REGISTRY.md` |
| Gold KST, news timing, news surprise, ADP, pivot/RSI-VWAP studies | not counted here; to be added from that branch's registries | that branch |

## Branch `claude/download-skill-27d08k` (this branch)

| Item | Tests | Source |
|---|---|---|
| Oil DCA bot: optimiser grid | 8,400 settings | `research/oil_dca_bot/optimize` |
| Oil bot: full sweep / app conditions / SL300 / smart entry / tuning | 360 + 48 + ≈ 20 + ≈ 14 + ≈ 30 | `research/oil_dca_bot/*` |
| Theory library screen | 535 | `research/theory_library/results/inventory.csv` |
| Theory library verification (neighbours + minute-level) | 54 + 3 | `research/theory_library/FREEZE.md` |
| ORB / school run (two interpretation sets) + tick re-tests | 96 + 2 | `research/orb_study` |
| Theory #2 zone reversal | 60 | `research/zone_reversal_study` |
| Session, exposure-control, trend-breadth, MOM50-breadth and DCA-mix studies | ≈ 3 + 7 + 36 + 15 + 7 | the respective READMEs |
| Shortlist 2025, daily signal DCA, Donchian research, SignalPro clone, others | ≈ 100 | the respective folders |
| **Subtotal** | **≈ 9,800** | |

## Batch 2 (this branch, pre-registered `research/batch2/PREREGISTRATION.md`)

| Item | Tests |
|---|---|
| Confirmatory forward tests (H1–H4 × BTC, ETH) | 8 |
| Development (exploratory) evaluations of the same 8 | 8, which do not add confirmatory tests |

## Batch 3 (this branch, `research/batch3/PREREGISTRATION.md`)

| Item | Tests |
|---|---|
| Search on 2025: indicators, strategies, theories, mixes × 7 markets × 3 TF × 3 exits | 238,728 |
| Confirmation on 2026 (shortlist) | 90 (0 passed) |

**Programme total ≈ 350,000 tests.** (It was ≈ 110,000 before Batch 3.) Development or historical results are corrected against this total. Confirmatory forward tests are judged under `FORWARD_EVALUATION.md` (4 tests, p ≤ 0.0125).

## Forward-test family (programme-wide correction)

**Current rule:** `FORWARD_EVALUATION.md`, revision of 2026-11-12.
- **Confirmatory family has 4 tests:** Donchian, Oil Stochastic, H3_BTC and H3_ETH.
- **Bar:** Bonferroni p ≤ 0.05/4 = 0.0125 against the random-timing benchmark.
- **Monitoring only, cannot PASS:**
  - GOLD_FVG, OIL_FIB and ETH_FIB: an order-handling look-ahead was found (`library_checks/README.md`);
  - TREND_ENS BTC and ETH;
  - Gold MOM50;
  - Batch 2 H1/H2/H4.
- **Stopped:** Gold Asia and SignalPro.

**Also counted:** the order-overlap re-check (3 candidates × 2 causal rules). It is a correctness check on fixed rules, not a new search.
