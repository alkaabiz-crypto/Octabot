# STR-027: Volumetric Order Blocks + EMA 21/50 + 5-target trade management (pre-registered 2026-11-15, before any computation)

**User request.** Test three tools together:
1. an invite-only Buy/Sell script with ENTRY, SL and TP1–TP5 boxes;
2. Volumetric Order Blocks (BigBeluga / LuxAlgo style);
3. EMA trend lines.

**Categories.**
- The combination is a **strategy (STR-027)**, tested with `../../categories/STRATEGIES.md`.
- The order-block measurement is registered as **IND-035**.
- The private script is **SIG-004**. Its code is not public, so it **cannot be reproduced exactly**. Here its *trade management* is modelled (entry, stop, five targets, breakeven after TP1). The script itself can only be judged as a signal source, from screenshots taken when its signals appear.

## Rules (1-hour signals, 15-minute execution)

**Trend filter.** EMA21 vs EMA50 of 1-hour closes at the signal candle. Longs only if EMA21 > EMA50; shorts only if EMA21 < EMA50.

**Volumetric order block** (a fixed simplification of the public BigBeluga / LuxAlgo logic):
- A **swing high** at 1-hour candle *j* is the highest high of candles *j*−5…*j*+5. It is confirmed, and usable, only from candle *j*+5. Swing lows mirror this.
- **Bullish block:** a 1-hour close breaks above the latest confirmed swing high. The block is the **last bearish candle** (close < open) in the 20 candles before the break, after the swing high. Zone = that candle's [low, high].
- **Block volume** = the volume of that candle plus the next 2.
- **Buy share** = volume of the up-candles among those 3 ÷ block volume.
- A bullish block counts only if **buy share ≥ 50%**. Bearish blocks mirror this: a break below a swing low, the last bullish candle, and sell share ≥ 50%.
- A block is valid for **48 hours**, or until a 1-hour close beyond its far side (below the zone low for a bullish block).

**Entry** (the "BUY / SELL label"). A pending limit at the zone edge: the top for longs, the bottom for shorts.
- It fills on the first 15-minute candle that trades through it while the block is valid and no position is open.
- Fill price = the limit, or the candle open if price gapped through.
- **Newest replaces:** a new qualifying block in the trend direction replaces the pending one.
- One position at a time.

**Stop loss.** The far side of the zone. The trade is skipped if the risk is < 0.15% of price.

**Targets.** TP1…TP5 at 1R…5R; 20% of the position closes at each.
- After TP1 the stop moves to the entry (breakeven).
- **Time exit:** whatever remains after 72 hours closes at the 15-minute close.
- Within a candle the stop is checked first; targets are not checked on the fill candle.

All decisions use closed candles, and limits are pending orders handled causally (no look-ahead selection).

## Markets, data and costs

| Market | Data | Volume | Primary cost (round trip) | Stress |
|---|---|---|---|---|
| BTC, ETH | Binance 15m / 1h (frozen research data) | real | 0.05% | 0.20% (retail taker) |
| Gold, oil | Exness 15m bid/ask | **tick count** (a proxy; flagged) | 1.5 × median spread | 3 × median spread |

**Periods:** EARLY 2018-06 → 2022-12 (gold 2020→, oil 2019→); TRAIN 2023-01 → 2024-06; VALIDATION 2024-07 → 2025-06; TEST 2025-07 → 2026-11.

**R per trade** = the sum of the partial exits in R, minus cost / risk.

## Benchmark

Random entries: the same count and side per period, at random 15-minute opens, with the same risk in % and the same TP ladder, breakeven, time and stop rules. 1,000 sets; one-sided p. This asks whether the **order-block + EMA timing** adds anything beyond the trade management itself.

## Decision (per market; 4 tests; Benjamini–Hochberg on the TEST p)

| Label | Conditions |
|---|---|
| **SCREEN-PASS** | mean R > 0 at primary cost in every period; TEST mean > 0 at stress cost; TEST p ≤ 0.05 after BH; ≥ 30 TEST trades |
| **WATCH** | positive in every period, but not significant |
| **REJECTED** | otherwise |

A SCREEN-PASS earns a forward paper test.

## Diagnostics (reported, not deciding): "do they work better together?"

- **NO_EMA:** the same rule without the EMA filter.
- **NO_VOLUME:** the same rule without the 50% volume-share filter.

The mean R of each is compared with the full combination, per period.
