# Batch 2 Amendment 1: 2026-11-12, before E (2026-11-14 00:00 UTC)

**Authority:** the user's message of 2026-11-12: "If there is any rules or judgmenet u think was a fault or wrong judgment … i give u permisssion to do whatever you think is right".

**What does not change:** signals, thresholds, holds, costs, data, the 2025 rule, benchmarks and outcome definitions. No forward data has been processed, so no forward clock restarts.

## Change 1: confirmatory family = H3_BTC and H3_ETH only

**Why:** the development power calculation (`DEVELOPMENT_SUMMARY.md`) shows:
- H1, H2 and H4 would need 25,000–76,000 trades;
- they get 9–16 trades a year;
- so they can never reach a verdict.

Keeping them in the Holm family only weakens H3, the one hypothesis that can be tested.

**The basis is power, not returns.** The decision uses trade frequency and per-trade variance. H4_BTC, the best development result (+140 bp, p 0.08), is demoted too.

**Monitoring only:** H1_BTC, H1_ETH, H2_BTC, H2_ETH, H4_BTC and H4_ETH keep running unchanged. Their results are reported as monitoring and can never PASS.

**Confirmatory test:** Holm across the **2** H3 tests at α = 0.05.

## Change 2: H3 horizon

Using the same formula with α = 0.05/2 (z = 1.96) and δ unchanged:

| Test | n_req | Years at the development rate |
|---|---|---|
| H3_BTC | **479** | ≈ 1.5 |
| H3_ETH | **697** | ≈ 2.25 |

- **Evaluation date:** the later of reaching n_req and E + 6 months, **capped at E + 36 months**. The cap was 24 months, which is too short for H3_ETH.
- No interim decisions.
- `forward.py`'s REPORT shows the original n_req from `development.json`. **This table supersedes it** for H3.
