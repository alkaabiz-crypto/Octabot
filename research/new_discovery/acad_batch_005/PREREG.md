---
title: Academic strategy batch 005 pre-registration
description: Five published, evidence-backed strategies (intraday momentum, overnight drift, pre-FOMC drift, turn of the month, Bitcoin intraday momentum) on Exness prices
sidebar_position: 1
---

# Academic batch 005: pre-registration (2026-11-18, written before any computation)

The user asked to "search for strategies using everything in your power and test them". This batch takes five effects that are published in peer-reviewed research and that this programme has **not** tested before. Each is checked on Exness prices with Exness spreads, 2019 → 2026.

Sources (web search, 2026-11-18):
- Gao, Han, Li & Zhou (2018, *Journal of Financial Economics*), "Market intraday momentum", and a 16-country extension (University of Reading).
- Shen, Urquhart & Wang (2022, *Financial Review*), Bitcoin intraday time-series momentum.
- Lucca & Moench (2015), the pre-FOMC drift, with Ignatieva & Ohashi (2025, *Applied Economics*) finding it still present.
- The overnight ("night") effect literature.
- Xu & McConnell (2006), the turn-of-the-month effect.

## Data

- **Exness 1-minute mid prices and median spreads** for US500m, USTECm, US30m and DE30m:
  - 2019-08 → 2024-12 built from the public tick archive (`build_data.py`, same method as STR-033);
  - 2025-01 → 2026-10 from the existing causal-impact 1-minute build (US500m, USTECm, DE30m);
  - US30m for 2025+ from the Exness 15-minute files.
- **BTC:** Binance BTCUSDT 15-minute bars (2018-06 →), with cost 0.05% per side (primary) and 0.20% (stress).
- **Gold (XAUUSDm):** Exness 15-minute bars (turn of the month only).
- **Costs (Exness):** the quoted spread at entry and exit (half each side). Stress = 2 × spread.
- **Swap** (overnight financing) is not in the data. Holding-period rules report the break-even swap instead: the swap per night that would cancel the edge.

## Strategies (all times in exchange-local time with daylight saving; US = America/New_York, DAX = Europe/Berlin)

| ID | Strategy | Rule | Markets |
|---|---|---|---|
| STR-034 | Intraday momentum (Gao et al.) | r1 = return from the previous trading day's 16:00 close to today's 10:00. At 15:30, go LONG if r1 > 0 and SHORT if r1 < 0; exit at 16:00 | US500, USTEC, US30 |
| STR-034-DAX | The same for the DAX | previous 17:30 close → 09:30 today; trade 17:00 → 17:30 | DE30 |
| STR-035 | Bitcoin intraday momentum (Shen et al.) | r1 = 00:00 → 00:30 UTC return (UTC day). At 23:30 UTC, trade in its sign; exit at 24:00 | BTC |
| STR-036 | Overnight drift | LONG at 16:00 (the cash close), exit at the next trading day's 09:30 open, every trading day | US500, USTEC, US30 |
| STR-037 | Pre-FOMC drift (Lucca & Moench) | LONG at 14:00 the trading day before each **scheduled** FOMC announcement day (Federal Reserve calendar; unscheduled meetings and notation votes excluded), exit at 13:55 on the announcement day | US500, USTEC, US30 |
| STR-038 | Turn of the month (Xu & McConnell) | LONG from the close of the second-to-last trading day of the month to the close of the 3rd trading day of the next month (US close 16:00; gold uses the 16:00 New York price; BTC uses 00:00 UTC days) | US500, USTEC, US30, gold, BTC |

Prices are the 1-minute mid at the stated minute (or the nearest earlier minute within 5 minutes). If missing, the day is skipped.

## Evaluation (per strategy × market)

- **Measure:** net return per trade in basis points, after spread (stress: 2 × spread; BTC 0.05% / 0.20% per side).
- **Periods:** EARLY (2019-08 → 2022), TRAIN 2023-01 → 2024-06, VALIDATION 2024-07 → 2025-06, TEST 2025-07 → now.
- **Benchmark:**
  - STR-034 / 035: the same windows with a random direction, 1,000 sets.
  - STR-036 / 037 / 038 (long-only): the market's average return over windows of the same length on all other days (excess return). The test is a one-sided t on the excess.
- **SCREEN-PASS:** net mean > 0 in every period, TEST stress mean > 0, TEST p ≤ 0.05 after BH over all 15 (strategy × market) tests in this batch, and ≥ 30 TEST trades.
  - STR-037 has only about 8 events a year, so it cannot reach 30 TEST trades. It can be at most WATCH, by design.
  - STR-038 has 12 a year, so it is also at most WATCH.
- **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.
- For holding-period rules (036, 038), the report adds the break-even swap. A pass would also need a venue check with real Exness swap rates before any forward test.

No parameter is changed after results are seen. All results are reported.
