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

**Rule:** a forward result counts as evidence only if it survives **Bonferroni across every forward test that was running when it was evaluated.** It is not enough to clear only its own batch's correction.

This rule adds a stricter way to interpret results. No trading rule, sample target or ledger changes.

**Forward tests running from 2026-11-12: 16**
- Donchian BTC (BINANCE PROXY)
- TREND_ENS BTC and ETH
- Gold MOM50
- Oil Stochastic
- GOLD_FVG, OIL_FIB and ETH_FIB
- Batch 2 H1–H4 on BTC and ETH: 8 tests, from 2026-11-14

**Stopped on 2026-11-12, by the user's decision:**
- Gold Asia, before any entry. Its benchmark showed no edge.
- SignalPro tracking, since all signals were resolved.

So a single forward test needs a one-sided p ≤ 0.05/16 ≈ 0.0031 against its random benchmark.
