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

**Programme total ≈ 110,000 tests.** Development or historical results are corrected against this total. Confirmatory forward tests are corrected within their pre-registered family (Holm across the 8).

## Forward-test family (programme-wide correction)

**Superseded on 2026-11-12 by `FORWARD_EVALUATION.md`:**
- The **confirmatory family has 7 tests:** Donchian, Oil Stochastic, GOLD_FVG, OIL_FIB, ETH_FIB, H3_BTC and H3_ETH.
- **Bar:** Bonferroni p ≤ 0.05/7 ≈ 0.0071 against the random-timing benchmark.
- **Monitoring only, cannot PASS:** TREND_ENS BTC and ETH, Gold MOM50, and Batch 2 H1/H2/H4 (6 tests).
- **Stopped:** Gold Asia and SignalPro.
