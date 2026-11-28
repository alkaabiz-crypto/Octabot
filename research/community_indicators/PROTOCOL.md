# Pre-registered protocol: community-made indicators on oil, gold and BTC

Written on 2026-11-10, before any result of this test was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Question

Do popular community-made TradingView indicators give reliable BUY or SELL signals on US oil (USOILm), gold (XAUUSDm)
and BTC (BTCUSDm)? Does any reach a 70%+ win rate while also making money after real costs?

## Indicators: open-source, non-repainting, published default settings

Each is re-implemented from its published open-source logic, at the author's default settings. Nothing is tuned.

| # | Indicator (author) | BUY when | SELL when |
|---|---|---|---|
| 1 | UT Bot Alerts (QuantNomad / HPotter / Yo_adriiiiaan), key value 1, ATR 10 | close crosses above the ATR trailing stop | close crosses below it |
| 2 | SSL Channel (ErwinBeckers), period 10 | the channel flips up (close above the SMA of highs) | it flips down |
| 3 | Squeeze Momentum (LazyBear), BB 20/2, KC 20/1.5 | squeeze releases with momentum > 0 | squeeze releases with momentum < 0 |
| 4 | WaveTrend (LazyBear), 10/21, level 53 | WT1 crosses above WT2 while WT1 < −53 | WT1 crosses below WT2 while WT1 > 53 |
| 5 | Chandelier Exit (everget), ATR 22 × 3, close-based | direction flips up | direction flips down |
| 6 | Hull Suite (InSilico), HMA 55 | HMA turns up (HMA > HMA two bars back) | HMA turns down |
| 7 | Range Filter (DonovanWall / Guikroth), period 100, multiplier 3 | first close above a rising filter | first close below a falling filter |
| 8 | QQE (colinmck-style signals), RSI 14, smoothing 5, factor 4.238 | smoothed RSI crosses above the QQE trailing line | crosses below it |

**Excluded on purpose:**

- **Nadaraya-Watson Envelope (LuxAlgo).** It repaints in its default mode, so its signals are redrawn after the fact.
- **ZigZag and fractals.** They confirm turns only after later candles.
- **Lorentzian Classification.** It is a machine-learning script with many settings, not a fixed indicator.

Repainting indicators show very high "accuracy" on a chart that cannot be reproduced in real time.

## Everything else is the same as `research/indicator_scan/PROTOCOL.md`

- **Data.** Exness bid and ask quotes as 15-minute candles. 1H bid candles are used for signals.
  - Oil and gold: the files from `research/oil_rsi_vwap` and `research/gold_rsi_vwap`.
  - BTC: `data/BTCUSDm_15m.csv.gz`, built the same way, from 2024-03 to the latest quote.
  - 2024 is warm-up only.
- **Exits.**
  - HW: 2 × ATR stop, 1 × ATR target, 24 h (break-even win rate about 67%).
  - SYM: 2 × ATR target and stop, 48 h.
  - TRAIL: 2 × ATR stop, then a 3 × ATR trail.
- **Fills and costs.** Buy at the ask, sell at the bid, with real spreads, plus 0.02% slippage.
- **Periods.** Selection is 2025. Confirmation is 2026 to the latest quote.
- **Reliable** means at least 30 trades in 2025 and at least 20 in 2026, with expectancy > 0 and p_random ≤ 0.05 (1,000
  matched random-entry runs) in **both** periods.
- **70%-worthy** means reliable, and also a win rate of at least 70% in both periods.

8 indicators × 2 directions × 3 exits × 3 markets = 144 variants. About 7 would pass the 2025 stage by chance. Even a
variant that passes both stages justifies only a frozen forward paper test.

Disclosure: BTC 2025 to 2026 has been examined in earlier studies with other indicators. These community indicators
have not been tested on any market before.
