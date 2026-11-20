# Pre-registered protocol: which indicators fit which markets (forex, stock indices, crypto, commodities)

Written on 2026-11-11, before any result for the new markets was computed. Paper research only. Nothing in earlier
studies, the signal assistant, the Donchian forward test or the Pivot Reversal paper test is changed.

## Question

Across 33 Exness markets, do some indicators fit some markets, or some kinds of market, in a way that holds up on new
data? "Fitted" here means chosen on one period and then confirmed on a later one, never just the best backtest.

## Markets (Exness bid/ask ticks, 15-minute candles, 1H signals)

| Class | Markets |
|---|---|
| Forex | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURJPY, GBPJPY, EURGBP |
| Stock indices | US500, USTEC, US30, DE30, UK100, JP225, FR40, AUS200, HK50, STOXX50 |
| Crypto | BTCUSD, ETHUSD, XRPUSD, LTCUSD, SOLUSD, BCHUSD, ADAUSD, BNBUSD |
| Commodities | US oil, UK oil, natural gas, gold, silver |

All symbols carry Exness's "m" suffix. A market is used only for the months the archive has, and missing months are
reported.

## Periods

- **Warm-up:** 2023-01 to 2023-06.
- **Discovery:** 2023-07-01 to 2024-12-31. This is where indicators are fitted to markets.
- **Confirmation:** 2025-01-01 to the latest candle, the period requested.

US oil, gold and BTC 2025 to 2026 were already examined in earlier rounds, so their confirmation results are reported
but flagged. The other 30 markets are new.

## Variants

These are the same variants as `research/long_history/PROTOCOL.md`, about 2,950 per market (the "6000+" list
comprises these 2,950 plus duplicates and not-portable scripts):

- all TradingView built-in strategies;
- ChartArt's double strategies;
- the 62 directional built-in indicators;
- the 11 original community scripts;
- each of the above alone and with each of the four fixed filters.

Every variant uses default settings and the same exits, fills, costs and random-entry benchmarks (200 runs, z-score).
The daily-EMA200 filter needs about 200 trading days, so it trades less early in discovery.

## Fitting and confirmation (fixed now)

1. **Per-market fit.** In each market, the **5 variants with the highest z against random entry in discovery** are
   chosen. Each must have at least 100 trades, positive expectancy, and positive expectancy at stress cost.
2. **Per-class fit.** For each class, a variant's discovery z-scores are combined across the class's markets
   (Stouffer: the sum of z over √k, counting markets with at least 30 trades). The top 5 per class are chosen.
3. **Confirmation.** Only the chosen variants are tested on 2025-01 to now.
   - A per-market pick is **confirmed** if it has at least 50 trades, expectancy > 0 at primary and stress cost, and
     p ≤ 0.05 against random entry after a Benjamini–Hochberg correction over all per-market picks.
   - A per-class pick is **confirmed** if its combined confirmation z gives p ≤ 0.05 after BH over all class picks,
     and expectancy is positive in a majority of the class's markets.
4. **Whole-sample check.** BH at 5% over every variant and market for 2023-07 to now, as in `research/long_history`.

## What counts as a finding

Only a confirmed pick counts. A confirmed pick justifies a frozen forward paper test of that indicator on that market
or class, not live trading.

**Expected by luck:** if nothing works, about 1 in 20 picks will show raw p ≤ 0.05 in confirmation. BH keeps the share
of false confirmations among those it accepts at about 5%.
