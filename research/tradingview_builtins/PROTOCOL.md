# Pre-registered protocol: every TradingView built-in, plus the most-liked community scripts and combinations

Written on 2026-11-10, before any result of this phase was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Scope, and what "everything" means here

**TradingView built-ins.** TradingView's own list has 142 built-in scripts. All were downloaded except "Auto trend
detector" and "RelativeValue" (HTTP 401). `sources_manifest/manifest.json` lists them with SHA-256; the code itself
is TradingView's, so it is not committed.

**A. All 21 built-in strategies are replayed from their source at default settings**, with TradingView's own entry
and exit logic: market orders, stop orders, persistence and cancellation, reversals, and protective exits.

- Bar up/down
- Bollinger Bands (the "directed" variant is covered by the BUY/SELL split)
- Channel breakout
- Consecutive up/down
- Inside bar
- Keltner channels
- MACD
- Momentum
- Moving average crossover
- Outside bar
- Parabolic SAR
- Pivot extension
- Pivot reversal
- Price channel
- RSI
- Stochastic slow
- Supertrend
- Two moving averages crossover
- Volatility expansion-close
- Rob Booker ADX breakout
- **Technical ratings**: TradingView's TechnicalRating library, which averages 15 moving-average and 11 oscillator
  votes. It buys at rating > 0.5 and sells at < −0.5, with a 3 × ATR stop and a trail of 2 × ATR that activates after
  5 × ATR.

Not replayed: "Greedy strategy", which pyramids gap orders under intraday order limits.

**B. Every built-in indicator that gives a direction gets its standard textbook signal at TradingView's default
settings:**

- **Moving averages:** SMA 9, EMA 9, WMA 9, DEMA 9, TEMA 9, HMA 9, ALMA 9/0.85/6, KAMA 10/2/30, LSMA 25,
  McGinley 14, SMMA 7 and VWMA 20. BUY when the close crosses above the MA; SELL when it crosses below.
- **Moving average ribbon:** SMA 20/50/100/200 newly in bullish or bearish order.
- **Zero-line crossings:**
  - Awesome oscillator
  - BBTrend 20/50
  - Bull bear power 13
  - Chaikin money flow 20
  - Chaikin oscillator 3/10
  - Chande momentum 9
  - Coppock 10/14/11
  - DPO 21 (uncentred)
  - Ease of movement 14
  - Elder force 13
  - Price oscillator 12/26
  - ROC 9
  - Momentum 10
  - TRIX 18
  - SMI ergodic oscillator 20/5/5
  - Trend strength index 14
  - Woodies CCI 14
- **Signal-line crossings:** KST, Klinger 34/55/13, Price momentum oscillator 35/20/10, Relative vigor index 10,
  True strength index 25/13/13, Fisher transform 9.
- **Level crossings (oversold up / overbought down):** Bollinger %b 0/1, Connors RSI 3/2/100 at 10/90, MFI 14 at 20/80,
  Stochastic 14/1/3 at 20/80, Stochastic RSI 14/14/3/3 at 20/80, Stochastic momentum index 10/3/3 at ±40, Ultimate
  oscillator 7/14/28 at 30/70, Williams %R 14 at −80/−20, Rank correlation index 10 at ±80, CCI 20 at ±100,
  Relative volatility index 10 at 50.
- **Line crossings:** Aroon 14 (up versus down), DMI 14 (+DI versus −DI), Vortex 14, Williams alligator (lips versus
  teeth, with their forward offsets applied causally).
- **Flips or breaks:** Volatility stop 20/2, Chande Kroll stop 10/1/9, Envelope 20/10% re-entry, Linear regression
  channel 100/2σ re-entry, the TWAP (1D) cross, OBV / A-D / PVT crossing their SMA 20, NVI and PVI crossing their EMA 255.
- **RSI divergence indicator:** the built-in's regular bullish or bearish divergence.

Indicators already covered by a built-in strategy (MACD, RSI, Stochastic, Bollinger, Keltner, Donchian/Price channel,
Supertrend, Parabolic SAR, Momentum, MA crosses, Chandelier) are tested as strategies, not again. VWAP and Ichimoku
were tested in earlier rounds.

**Excluded, with the reason:**

| Reason | Built-ins |
|---|---|
| No direction | ATR, historical volatility, Bollinger BandWidth, choppiness, ulcer, average daily range, mass index, volume, relative volume at time, 24-hour volume |
| Market data not available | advance/decline, cumulative volume index, open interest, net and up/down volume (need lower-timeframe volume) |
| Repaint or confirm late | ZigZag, Williams fractal, pivot points high/low (covered by the pivot strategies) |
| Drawing or calendar tools | auto fib, pitchfork, key levels, price target, seasonality, moon phases, sessions, performance, gaps, visible average price, multi-time-period charts, median, Bollinger bars, chop zone, balance of power (unsmoothed bar ratio), Pring's special K, percentage volume oscillator (volume-only) |

**C. The most-liked open-source community scripts.**

- A likes ranking of 5,478 scripts was built from TradingView's search endpoint (`src/rank_community.py`).
- Most of the top 60 are already covered: Squeeze, WaveTrend, Coral Trend, MACD and RSI variants, Vix Fix, Ichimoku
  and stochastics.
- The top-liked ones with explicit entry rules that are not yet covered are ChartArt's double strategies, which are
  "signal plus confirmation" designs: Bollinger + RSI; MACD + SMA 200; Golden Cross SMA 200; MACD + Stochastic;
  Stochastic + RSI.
- Each is replayed from its source, as in A.

**D. Combinations ("signal plus entry condition").**

- Every single-signal variant from A to C that has positive expectancy in 2025 is combined with each of four
  pre-defined filters:
  1. the last closed 4H close above its EMA 200 (for BUY) or below it (for SELL);
  2. the daily close above or below its EMA 200;
  3. 1H ADX 14 > 20;
  4. 1H close above or below the session VWAP.
- The filters are fixed now and never tuned.

## Fills, costs, exits, benchmarks (as in earlier rounds)

- **Fills and costs.** Exness bid/ask at 15-minute resolution plus 0.02% slippage. R = 2 × ATR14 at entry, for
  comparability.
- **Exits.**
  - Strategies use their own exits. BUY means the long legs and SELL means the short legs.
  - Indicators use the three standard exits (HW, SYM, TRAIL), plus FLIP (hold to the opposite signal) where BUY and
    SELL alternate.
- **Benchmarks.**
  - Standard exits: matched random entry.
  - Strategy, FLIP and NATIVE legs: random entries in the same quarter, same direction, same holding time.
  - 1,000 runs each.

## Periods and decision rule

- **Selection** is 2025; **confirmation** is 2026 to the latest quote.
- A variant **passes** if, in both periods:
  - it has at least 30 trades in 2025 and 20 in 2026;
  - expectancy > 0;
  - p_random ≤ 0.05.
- **This phase tests roughly 1,500 to 2,500 variants, so about 4 to 6 would pass both years by luck alone.** Passing
  both years is therefore **not** enough.
- A signal counts as **found** only if it also passes the untouched-data check: expectancy > 0 and p_random ≤ 0.05 on
  data never used here.
  - US oil: Exness 2019-02 to 2024-12.
  - BTC: Binance 2020–2024, with 0.05% cost.
  - Gold: Exness 2020–2023, downloaded only if a gold variant needs it.
- **70% target.** A found signal with a win rate of at least 70% in all three periods is reported as meeting it.
- If nothing is found, the report says so plainly.
