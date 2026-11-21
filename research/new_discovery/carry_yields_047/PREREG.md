---
title: STR-047 crypto cash-and-carry and STR-048 yields→gold pre-registration
description: Funding-rate carry on BTC/ETH (long spot, short perpetual) and a 10-year-yield momentum rule for gold, both on free public data
sidebar_position: 1
---

# STR-047 and STR-048: pre-registration (2026-11-21, before any computation)

## STR-047: crypto cash-and-carry (funding carry)

- **Position:** buy spot BTC (or ETH) and short the same notional of the Binance USDT-M perpetual. The price moves cancel; the position **receives funding** when funding is positive (longs pay shorts) and pays when it is negative.
- **Data:** Binance public funding-rate history (data.binance.vision, every 8 hours), BTCUSDT and ETHUSDT, 2020-01 → 2026-10. US 3-month T-bill yield (FRED DTB3) as the hurdle, because the money is tied up.
- **A, always on:** hold the hedge continuously. Pay entry and exit costs once per calendar period: spot 0.10% + perp 0.05% per side.
- **B, conditional:**
  - **enter** when the trailing 7-day average funding, annualised, exceeds 10%;
  - **exit** when the trailing 3-day average turns negative;
  - each entry or exit costs 0.15% (both legs, one side).
- **Return:** funding received minus costs, as an annualised yield on the spot notional.
  - The basis change between spot and perp at entry and exit is ignored (assumed small).
  - The extra margin needed for the short, about +20% capital, is reported as an adjusted yield.
- **Verdict:**
  - **WORTH IT:** net yield above the T-bill yield in every period (EARLY 2020–2022, TRAIN 2023-01→2024-06, VALIDATION 2024-07→2025-06, TEST 2025-07→now).
  - **SOMETIMES:** above T-bills in some periods. **NOT WORTH IT:** never above them.
  - This is a yield comparison, not a forecast test. Risks not modelled: exchange failure, auto-deleveraging, funding spikes against the position.

## STR-048: 10-year Treasury yield → gold

- **Data:** FRED DGS10 (nominal 10-year yield) and DFII10 (10-year real yield). Exness XAUUSDm daily price at 16:00 New York (mid; costs from the spread).
- **Signal:** the change of the yield over the last 20 trading days, ending on day d.
  - FRED publishes d's value on d+1, so the trade is entered at the **16:00 New York gold price two trading days after d**.
  - **Yield fell → LONG gold; yield rose → SHORT gold.** Hold 20 trading days; no overlapping trades.
- **Variants:** **A** uses the nominal yield (DGS10). **B** uses the real yield (DFII10).
- **Costs:** 1.5 × median spread round trip (stress 3 ×). Swap is not modelled (noted).
- **Benchmark:** random sides on the same days, 1,000 sets.
- **Decision:**
  - **SCREEN-PASS:** net mean > 0 in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over the 2 variants, and ≥ 30 TEST trades.
    - About 12 trades a year means TEST has about 17, so a pass is impossible by design; the best possible verdict is **WATCH**.
  - **WATCH:** positive in every period. Otherwise **REJECTED**.
