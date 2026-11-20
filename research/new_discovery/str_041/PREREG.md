---
title: STR-041 liquidity sweep + structure shift + dominance + OTE pre-registration
description: The user's four-part idea (liquidity zones, buyer/seller dominance, market structure, optimal entry) as one fixed rule set
sidebar_position: 1
---

# STR-041: liquidity sweep → market-structure shift → dominance → optimal trade entry (pre-registration, 2026-11-19, before any computation)

**Source.** The user asked for an indicator combining "liquidity zones, buyer/seller dominance, market structure, optimal signal". No single TradingView script with that name was found (web search 2026-11-19). The four parts are the standard Smart-Money / ICT concepts, each covered by several scripts:
- liquidity zones above/below confirmed swings (e.g. "Liquidity Zones (Pivot-based)");
- buyer/seller dominance from up-volume vs down-volume ("Buyside & Sellside" delta candles, "Liquidity Pressure Map");
- break of structure / change of character ("Market Structure & Liquidity");
- the Optimal Trade Entry zone at a 61.8–78.6% retracement ("ICT SMC Liquidity Grabs and OTE Zones").

They are combined here in the order ICT teaches them.

## Rules (LONG; SHORT mirrors everything)

- **Data:** 1h candles for signals and 15m candles for fills and management.
  - BTC and ETH: Binance with real volume, 2018 →.
  - Gold and oil: Exness with tick volume, long history.
  - S&P 500: Exness US500m with tick volume, 2023 →.
- **Swings:** pivot length 5 (a swing is confirmed 5 bars after it).
- **1. Liquidity sweep:** a 1h candle trades below the latest confirmed swing low and closes back above it. L* = that candle's low.
- **2. Market-structure shift (CHoCH):** within the next 24 1h bars, a 1h close above the latest confirmed swing high. The impulse leg runs from L* to H* (the highest high from the sweep to the CHoCH candle).
- **3. Buyer dominance:** over the bars from the sweep to the CHoCH, up-candle volume / total volume ≥ 0.55.
- **4. Optimal trade entry:** a limit buy at the 70.5% retracement, H* − 0.705 × (H* − L*), placed at the CHoCH close and valid 24 hours. It fills on 15m candles at min(open, limit). A newer setup replaces a pending one. One position at a time.
- **Stop:** L* − 0.1 × ATR14(1h). Skip if the risk is below 0.15% of price.
- **Target:** 2R. **Time exit:** 72 h. On the fill candle, the stop counts but the target does not. The stop is checked first.
- **Variants** (all reported, BH over all):
  - **A** = all four parts, target 2R;
  - **B** = A without the dominance filter (to see if dominance adds anything);
  - **C** = A with the target at H*, "internal liquidity" (sweeps run toward the opposite liquidity).
- **Costs:** BTC/ETH 0.05% per side (stress 0.20%); Exness 1.5 × median spread (stress 3 ×).
- **Benchmark:** random entries with the same count, sides, risk % and management, 1,000 sets.
- **Decision:**
  - **SCREEN-PASS:** mean R > 0 in every period, TEST stress > 0, TEST p ≤ 0.05 after BH over all (variant × market) tests, and ≥ 30 TEST trades → forward paper test.
  - **WATCH:** positive in every period without the rest. Otherwise **REJECTED**.
- **Look-ahead check:** a prefix-invariance check, as in STR-027.
