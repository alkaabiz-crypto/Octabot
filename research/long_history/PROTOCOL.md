# Pre-registered protocol: every indicator on the full available history

Written on 2026-11-11, before any result of this study was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Why this study exists

The earlier rounds judged each signal on one year at a time (2025, then 2026), about 100 to 150 trades per year.

A sanity check run before this protocol planted fake signals with a known edge into the US oil 2025 data:

- signals that guessed the next 24 hours' direction right **60%** of the time were *not* reliably detected (p = 0.07 to 0.57);
- signals that were right **70%** of the time were detected in 2 of 3 trials;
- signals right **80%** of the time were detected in 3 of 3;
- pure coin-flip signals were rejected (p = 0.24 to 0.91).

So the test is sound, but one year is too short to see a modest edge. This study uses all the history available
(about 6 to 7.5 years per market), which gives each signal several times more trades. It replaces the year-by-year
gates with a single full-history test that is corrected for the number of signals tried.

An independent library (pandas_ta) was also used to cross-check the indicator formulas. These matched exactly: RSI,
ATR, EMA, WMA, HMA, DEMA, TEMA, LSMA, MACD, Stochastic, Williams %R, ADX, ±DI, Awesome Oscillator, Ultimate
Oscillator, ROC, Momentum and Bollinger (population standard deviation, as TradingView uses). CCI matches TradingView's
formula. pandas_ta's CCI differs from TradingView's.

## Data (Exness bid/ask ticks, 15-minute candles)

| Market | History | Test period |
|---|---|---|
| US oil (USOILm) | 2019-02 to 2026-11 | 2019-07-01 to the last candle |
| Gold (XAUUSDm) | 2020-01 to 2026-11 | 2020-07-01 to the last candle |
| BTC (BTCUSDm) | 2020-01 to 2026-11 | 2020-07-01 to the last candle |

- The first months are warm-up only.
- 2025 and 2026 were used for selection in earlier rounds. That is harmless here, because nothing is selected: every
  variant is tested and the correction counts all of them.
- BTC's price history was studied heavily in earlier rounds (on Binance data), so **BTC results are exploratory**.

## Variants (all at default settings, nothing tuned)

1. The 21 TradingView built-in strategies and ChartArt's 5 double strategies, BUY legs and SELL legs, with their own
   exits.
2. The 62 directional built-in indicators.
3. The 11 original community scripts of `research/tradingview_originals`.

Groups 2 and 3 use the standard exits (HW, SYM, TRAIL), plus FLIP where signals alternate, plus NATIVE for Lorentzian.

Each of the above is also combined with each of the four fixed filters of `research/tradingview_builtins/PROTOCOL.md`:

- 4H EMA 200 side;
- daily EMA 200 side;
- ADX 14 > 20;
- session VWAP side.

Every variant is filtered; there is no pre-selection.

Costs, fills, R and the benchmarks are as in the earlier rounds. Random runs are 200 per variant, and significance uses
the z-score of the variant's expectancy against the distribution of random-run means.

## Pass rule (fixed now)

A variant **passes** only if, over its market's test period at primary cost:

1. it has at least 200 trades;
2. its expectancy is above 0 at primary cost and at stress cost;
3. it beats matched random entry, with one-sided p from the z-score, after a **Benjamini–Hochberg false-discovery
   correction at 5% across every variant in all three markets**;
4. it is consistent:
   - expectancy is above 0 in both halves of the test period;
   - expectancy is above 0 in at least two thirds of the calendar years that have 10 or more trades.

**70%-worthy** means passing and also winning at least 70% of trades.

Passing justifies only a frozen forward paper test, never live trading on its own.
