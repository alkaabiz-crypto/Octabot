---
title: STR-050 negatively correlated pairs pre-registration
description: Mean reversion and lead-lag on pairs that normally move in opposite directions (USD on opposite sides, or oil vs the CAD-quoted dollar)
sidebar_position: 1
---

# STR-050: negatively correlated pairs (pre-registration, 2026-11-22, before any computation)

**User request:** "can you test negative correlation".

**Pairs:** chosen on economic grounds before looking at the data. The US dollar sits on opposite sides of the quote, or oil is set against the CAD-quoted dollar. All are Exness 15-minute data, 2023 →, priced daily at 16:00 New York.

| ID | Pair | Why opposite |
|---|---|---|
| a | EUR/USD vs USD/CHF | USD is the quote in one and the base in the other |
| b | GBP/USD vs USD/CHF | same |
| c | Gold (XAU/USD) vs USD/CHF | gold is priced in USD; a stronger USD usually means lower gold and higher USD/CHF |
| d | Gold vs USD/JPY | same logic with JPY |
| e | US oil vs USD/CAD | Canada exports oil; oil up usually means CAD up, so USD/CAD down |

## Part 1: mean reversion

The STR-039 pairs engine, unchanged.
- **Hedge ratio:** β = OLS slope of ln(A) on ln(B) over the previous 60 days. For these pairs β is expected to be negative, so the "spread" ln(A) − β·ln(B) holds **both legs in the same direction**.
- **Entry:** |z| > 2, betting the spread reverts.
- **Exit:** z crosses 0, or |z| > 4 (stop), or 20 days.
- **Costs:** Exness spreads on both legs (stress 2 ×).
- **Benchmark:** random entry days with the same sides and holding lengths.
- **Report:** the actual average 60-day correlation of daily returns per pair and period, to confirm the relationship is negative.

## Part 2: lead–lag (IC only)

- For each pair and each direction (A → B and B → A): the rank correlation between one market's 16:00→16:00 return on day d and the other's return on day d+1.
- 10 ICs per period; TEST significance after BH over the 10.
- A significant IC that also holds in TRAIN and VALIDATION with the same sign would be turned into a rule **only in a separate, new pre-registration**.

## Decision (Part 1, per pair)

- **Periods:** TRAIN 2023-01 → 2024-06, VALIDATION 2024-07 → 2025-06, TEST 2025-07 → now.
- **SCREEN-PASS:** net mean > 0 in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over the 5 pairs, and ≥ 30 TEST trades.
- **WATCH:** positive in every period. Otherwise **REJECTED**.
