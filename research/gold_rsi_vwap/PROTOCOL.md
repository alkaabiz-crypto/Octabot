# Pre-registered protocol: RSI + VWAP entries on gold (XAUUSDm)

Written on 2026-11-10, before any XAUUSDm quote was downloaded or any result was computed. Paper research only.
Nothing in the earlier studies, the signal assistant or the frozen Donchian forward test is changed.

## Question

Does the BTC/ETH candidate, **VWAP momentum BUY with the trailing-stop exit**, work on gold? It did not transfer to
US oil (`research/oil_rsi_vwap`). The other seven RSI + VWAP variants are reported as exploratory results only.

## Everything is identical to the US oil study

The rules, indicators, execution, costs, benchmark and pass rule are exactly those of
`research/oil_rsi_vwap/PROTOCOL.md`. The same code is used (`research/oil_rsi_vwap/src/oil.py`, read-only). Only the
symbol changes. In brief:

- **Data.** Exness XAUUSDm, every bid and ask quote, aggregated to 15-minute bid/ask candles. Indicators warm up on
  2024-03 to 2024-12. **Statistics run from 2025-01-01 to the latest quote.**
- **Indicators.** RSI 14 and ATR 14 on 1H bid candles. VWAP is anchored at each session open (the first candle after
  a gap of at least one hour) and weighted by tick count. Textbook settings, with nothing tuned to gold.
- **Rules.**
  - V1 VWAP momentum: the close crosses session VWAP, with RSI on the same side of 50.
  - V2 RSI reversion: RSI crosses back through 30 (or 70), with the close on the far side of VWAP.
  - Each rule is tested as BUY and as SELL, with a trailing exit (2 × ATR stop, 3 × ATR trail) and with a ±1R exit
    (48-hour limit). That gives 8 variants.
- **Fills and costs.**
  - Entry at the next 15-minute candle: buy at the ask, sell at the bid. Stops use the side that closes the position.
  - Primary cost: the measured spread plus 0.02% slippage.
  - Stress cost: the measured spread, plus 0.05% slippage, plus 0.02% of price per day held for swaps (unverified).
- **Benchmark.** Matched random entry, 2,000 runs.

## Pass rule

**Primary hypothesis: V1 VWAP momentum, BUY, TRAIL.** It is a single test with no adjustment. It works on gold only
if, from 2025-01 to the latest quote at primary cost:

- there are at least 100 trades;
- expectancy is above 0 with t ≥ 2;
- p_random ≤ 0.05;
- expectancy is above 0 at stress cost.

The other 7 variants get Holm-adjusted p-values across all 8 and cannot produce a recommendation.

### Two warnings written before any result

1. **Power.** About 22 months is short. If gold had BTC's edge (+0.17R, standard deviation about 2.3R), a pass would
   occur only about 15 to 25% of the time. A fail would be weak evidence against the rule.
2. **Market context.** If gold rose strongly over the period, random long entries will also profit. That is why the
   rule is judged against matched random entry, not against zero alone.

Even a pass would justify only a frozen forward paper test, never live trading.
