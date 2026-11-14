# Pre-registered protocol: community-made indicators, round 2 (oil, gold, BTC)

Written on 2026-11-10, before any result of this test was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Selection of indicators

A deeper search found no independent ranking of community indicators by real performance:

- TradingView's own "Top" sort ranks by popularity only.
- Most "best indicator for gold" pages are vendors' own claims, or invite-only scripts whose logic cannot be inspected.

So the next nine **widely used, open-source, non-repainting** community signals not yet tested are used here, at the
authors' default settings, with nothing tuned.

| # | Indicator (author) | Defaults | BUY when | SELL when |
|---|---|---|---|---|
| 1 | HalfTrend (everget) | amplitude 2, channel deviation 2, ATR 100 | trend flips up | trend flips down |
| 2 | Coral Trend (LazyBear) | smoothing 21, constant D 0.4 | Coral line turns up | turns down |
| 3 | Waddah Attar Explosion (LazyBear) | sensitivity 150, MACD 20/40, BB 20/2, dead zone 3.7 × RMA(TR, 100) | first bar where the up column exceeds both the explosion line and the dead zone | the same for the down column |
| 4 | Williams Vix Fix (ChrisMoody) | 22, BB 20/2, lookback 50, percentile 0.85 | first bar at or above the upper band or range high (a "fear spike"; BUY only, as designed) | not used |
| 5 | Ichimoku TK cross | 9 / 26 / 52, cloud from 26 bars back | Tenkan crosses above Kijun with close above the cloud | Tenkan crosses below Kijun with close below the cloud |
| 6 | Parabolic SAR | 0.02 / 0.02 / 0.2 | SAR flips below price | SAR flips above price |
| 7 | Schaff Trend Cycle | cycle 10, MACD 23/50, factor 0.5 | STC crosses up through 25 | STC crosses down through 75 |
| 8 | Heikin Ashi flip | none | first bullish Heikin Ashi candle after a bearish one | first bearish after a bullish one |
| 9 | Smart Money Concepts structure break (LuxAlgo-style internal structure) | swing length 5 | close breaks above the latest confirmed swing high | close breaks below the latest confirmed swing low |

All swings and pivots are confirmed only after their right-hand bars have closed, so nothing repaints. Every
indicator is checked by a no-look-ahead test before any result is computed.

## Everything else is identical to `research/community_indicators/PROTOCOL.md`

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm bid/ask, as 15-minute candles. Signals use 1H bid candles. 2024 is
  warm-up only.
- **Exits.**
  - HW: 2 × ATR stop, 1 × ATR target, 24 h.
  - SYM: 2 × ATR target and stop, 48 h.
  - TRAIL: 2 × ATR stop, then a 3 × ATR trail.
- **Fills and costs.** Buy at the ask, sell at the bid, plus 0.02% slippage.
- **Selection** is 2025; **confirmation** is 2026 to the latest quote.
- **Reliable** means, in both periods:
  - at least 30 trades in 2025 and 20 in 2026;
  - expectancy > 0;
  - p_random ≤ 0.05 against 1,000 matched random-entry runs.
- **70%-worthy** means reliable, and also a win rate of at least 70% in both periods.

17 signals × 3 exits × 3 markets = 153 variants. About 8 would pass the 2025 stage by chance, which the 2026 stage
guards against. A pass justifies only a frozen forward paper test.
