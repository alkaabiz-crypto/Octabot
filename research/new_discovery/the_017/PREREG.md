# THE-017 event study: short-horizon reversal after overbought/oversold readings (pre-registered 2026-11-13, before computation)

**Claim.** After an hourly close with an overbought reading, the next hour's return is lower, and after an oversold reading it is higher, than after other hours. Found exploratorily in IND batch 001 on BTC and EUR/USD. Method: `../../categories/THEORIES.md`.

## Events and measurement

- **Reading:** Williams %R (14) on 1-hour mid candles (the IND-016 formula).
  - **Overbought:** %R ≥ −20.
  - **Oversold:** %R ≤ −80. Standard thresholds, fixed now.
- **Measurement:** the next-hour log return from the next candle's open.
- **Effect** = mean(next-hour return | oversold) − mean(next-hour return | overbought), in bp. The theory predicts **> 0**.
- **Matched null:** the event labels are shuffled 2,000 times **within the same UTC hour of day** and the same period. That keeps the time-of-day pattern and the event counts. One-sided p.
- **Dependence:** a Newey–West t on the per-event signed return series (oversold +r, overbought −r), in time order, is also reported.

## Markets and periods

- **Discovery** (where it was found): BTCUSDm, EURUSDm.
- **Replication** (not inspected for this pattern):
  - XAUUSDm, USOILm, US500m, USDJPYm, GBPUSDm, ETHUSDm;
  - Exness 15-minute bid/ask files built into 1-hour mid candles.
- **Periods:** EARLY (to 2022, BTC, gold and oil only), TRAIN 2023-01 → 2024-06, VALIDATION 2024-07 → 2025-06, TEST 2025-07 →.

## Verdict

| Verdict | Conditions |
|---|---|
| **SUPPORTED** | Both discovery markets have effect > 0 in every available period, with TEST p ≤ 0.05; **and** ≥ 3 of the 6 replication markets have TEST effect > 0 with p ≤ 0.05 (Benjamini–Hochberg across the 6) |
| **PARTLY SUPPORTED** | Discovery holds, but replication is < 3 markets |
| **DECAYED** | Significant in older periods, not in TEST |
| **NOT SUPPORTED** | Otherwise |

## Tradability (reported, does not change the verdict)

- **Effect per event:** half the effect (a trader takes one side per event), in bp.
- **Cost:** the market's median round-trip spread plus 0.5× spread slippage, in bp.
- If the effect per event is below that cost, the theory may be true but **not tradable** as a 1-hour trade.
