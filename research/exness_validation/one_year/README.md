# One-year Exness BTCUSDm validation of the frozen Donchian 20 strategy

This is research only. Nothing here is a live or broker execution. It is kept separate from the Binance forward test, which is labelled BINANCE PROXY and continues unchanged; its trades are never counted as Exness trades.

## Setup

| Item | Value |
|---|---|
| Primary period | 2025-11-01 00:00 to 2026-11-01 00:00 UTC (signal candle closes in this window). Older data is used only for warm-up. |
| Instrument and data | Exness **BTCUSDm** bid/ask ticks from the public Exness tick archive: 36,683,952 ticks, 0 with ask < bid, 0 out of order. All 12 monthly zip SHA256 values match `../data/manifest.csv`. |
| Strategy | Frozen engine `research/btc_breakout/src/engine.py` (unchanged): Donchian 20 BUY, closed-4H EMA200 filter, ATR14 Wilder, 2 ATR initial stop, 3 ATR trailing stop, 0.5% risk. Signals are computed on Exness **bid** candles. |
| Execution | **Simulated from historical ticks, not broker fills.** Entry is at the ask of the first tick after the signal-candle close (median delay 0.3 s). Exit is at the bid of the first tick at or below the stop. Spread is paid by buying at the ask and selling at the bid. |
| Parity | A candle-level re-implementation reproduces the frozen engine's 64 trades exactly (0 differences). |
| Costs | Spread: **measured** (median 10 USD at entry). Exit slippage beyond the stop: **measured** (median 2.6 USD, max 21.5 USD). Commission: 0 on the Standard account, as advertised but **unverified**. Swap and overnight admin fee: **unknown**, so only break-even values and hypothetical sensitivities are shown. |

## Primary results (Exness tick replay, entry at the first tick after the candle close)

| Metric | Value |
|---|---|
| Trades | 64 (all exits by stop) |
| Win rate | 35.9% |
| Profit factor | 1.74 |
| Expectancy / average R | **+0.383 R** |
| 95% CI (t) | **-0.49 to +1.26 R** |
| 95% CI (bootstrap) | **-0.27 to +1.40 R** |
| t-statistic | 0.86 (**not significant**) |
| Median trade | **-0.57 R** |
| Expectancy without the single largest trade | **-0.03 R** |
| Expectancy without the top 3 trades | **-0.17 R** |
| Max drawdown (0.5% risk per trade) | 4.58% |
| Longest losing streak | 8 |
| Net return (0.5% risk per trade, compounding) | +11.98% |
| Buy and hold BTCUSDm (bid) | -29.3% |

The largest trade was entered on 2026-08-19 at 14:00 UTC and made **+26.4 R**, which is 108% of the year's total R. The rally from 65k to 79k is genuine; Binance shows the same move. The trade only triggered on Exness, though, because its signal candle closed **17 USD** above the 20-candle high. Binance's slightly different prices did not trigger at that hour.

### Variants

| Variant | Trades | Expectancy R | PF | 95% CI (t) |
|---|---|---|---|---|
| Entry 8 minutes after the close (this worker's real latency) | 64 | +0.389 | 1.75 | -0.47 to +1.25 |
| Clean-data trades only | 64 | +0.383 | 1.74 | -0.49 to +1.26 |
| Frozen engine on Exness bid candles, no spread | 64 | +0.400 | 1.78 | -0.48 to +1.28 |
| Frozen engine on Binance, no costs | 64 | +0.483 | 1.98 | -0.44 to +1.41 |
| Frozen engine on Binance, 0.05% round trip (hypothetical) | 64 | +0.423 | 1.79 | -0.50 to +1.35 |

### Monthly R (by exit month)

| Month | 2025-11 | 12 | 2026-01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trades | 0 | 0 | 5 | 0 | 5 | 8 | 8 | 0 | 6 | 10 | 12 | 10 |
| Sum R | 0 | 0 | +3.72 | 0 | +0.39 | +2.60 | -3.45 | 0 | -0.63 | **+22.46** | +2.28 | -2.84 |

Months with no trades had the 4H trend filter down, so the strategy stayed out.

### Market regime (daily close vs EMA200 and its slope, measured at entry)

| Regime | Trades | Expectancy R | PF |
|---|---|---|---|
| Bear | 38 | +0.68 | 2.36 (includes the +26.4 R trade) |
| Bull | 22 | -0.03 | 0.96 |
| Sideways | 4 | -0.19 | 0.54 |

### Matched random-entry benchmark

The benchmark uses 1,000 runs with the same number of entry attempts and the same execution model: ask fill at the 15m open, stop triggered on the bid. Under that model the strategy's expectancy is +0.389 R.

| Benchmark | Median | 5th–95th percentile | Strategy percentile |
|---|---|---|---|
| Random entries, any hour | -0.03 | -0.23 to +0.31 | 97.8 |
| Random entries, only hours with the 4H trend up | +0.14 | -0.11 to +0.57 | **78.0** |

Most of the advantage over random entry comes from the 4H trend filter. The Donchian breakout timing itself is not distinguishable from random entry during uptrends.

### Costs that could not be verified (sensitivities are HYPOTHETICAL)

- 41 of 64 trades were held over the assumed daily rollover, for 64 swap-days in total. The assumed rollover is 21:00 UTC from April to October and 22:00 UTC from November to March, triple on Friday, taken from unverified secondary sources.
- Break-even swap is about **0.34% of notional per swap-day**. At hypothetical swaps of 0.01%, 0.02% and 0.05% per day, expectancy falls to +0.372, +0.361 and +0.327 R.
- Hypothetical commission of 2, 4 and 8 USD per lot round trip gives +0.380, +0.377 and +0.371 R. Position sizes are small, so this impact is small.

## Exness vs Binance (independent runs, same frozen engine)

- **Breakout signals:** 270 on Exness vs 278 on Binance. 263 fall in the same hour, 7 are Exness-only and 15 are Binance-only. There is 1 trend-filter disagreement (2026-04-06 10:00).
- **Trades:** 64 vs 64. 59 share the same entry hour and 45 share the same exit time.
- **Prices:** the median entry-price difference is -0.037% (Exness bid below Binance). The median absolute R difference on matched trades is 0.025 R.
- **Conclusion:** the two instruments mostly agree but are **not interchangeable**. Small price differences change which marginal breakouts trigger, and with this strategy one marginal signal can decide the year.

## Data quality (no interpolation)

Missing Exness periods in the window, including warm-up from about 2025-09:

| Start (UTC) | End (UTC) | Missing 15m bars |
|---|---|---|
| 2025-11-30 18:30 | 2025-12-01 00:00 | 22 |
| 2025-12-06 07:15 | 2025-12-06 07:30 | 1 |
| 2025-12-13 07:30 | 2025-12-13 08:00 | 2 |
| 2026-03-30 00:00 | 2026-04-01 00:00 | **192** (two whole days) |

Two breakout signals had a Donchian lookback that crossed a gap: 2025-12-06 15:00 and 2026-04-01 07:00. Both were already **rejected by the 4H trend filter**, so neither affected a trade. No trade was entered, held or exited across a gap, and no trailing update was skipped. The clean-data assessment is therefore identical to the full result. The 4H EMA200 window contains the gaps, a minor long-memory effect that changed no trend-filter decision.

## Decision

**Category 2: promising but insufficient evidence.** It is also suitable for continued controlled forward testing (category 4), on paper only.

- **For:** on the actual instrument, with measured spreads and tick-level fills, the one-year result was positive: +0.38 R per trade and +12% at 0.5% risk, while BTC fell 29%. Drawdown stayed low at 4.6%. This is consistent with the earlier Binance research.
- **Against:**
  - The result is not statistically significant: t = 0.86, and both 95% confidence intervals include zero.
  - It rests on a single +26 R trade. Without it, expectancy is -0.03 R and the median trade is -0.57 R.
  - The breakout timing does not beat random entries taken during 4H uptrends (78th percentile).
  - Swap and commission are unverified.
- **Not shown:** a measurable, independent edge from the breakout rule. **Not justified:** live trading.
- **Next step, if pursued:** continue the controlled paper forward test. Add an Exness-specific forward record using Exness ticks from the archive as each month is published, and verify real swap and commission from the MT5 Specification. Judge on the pre-registered 40 valid trades. Expect that 40 trades may still not be enough to separate a true edge from luck in a strategy this dependent on rare large winners.
