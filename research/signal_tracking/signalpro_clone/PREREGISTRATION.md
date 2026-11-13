# SignalPro-style template clone: pre-registration

Written and committed **2026-11-10, before any backtest result was computed.** Research only: no orders, no account connection, nothing live.

## What is being tested

SignalPro's own model cannot be copied: it is proprietary and runs on their servers. What *can* be copied is the level template it visibly applies. The 12 logged signals (`../signalpro/signals.csv`) show it consistently:

| Part | Template (from the 12 signals) |
|---|---|
| Entry | the current price at posting |
| TP1 | 5 USD from entry (50 "pips") on all 12 |
| TP2 | 10 USD from entry on 11 of 12 |
| TP3 | a round 10-USD level at least 30 USD away (fits 11 of 12) |
| Stop | 10 USD on 7 of 9 visible stops (others 13–20) |
| Management | 1/3 closed at each TP, stop moved to entry after TP1 |

The unknown part is **when and in which direction** the app signals. The signals so far went with the latest move, so the test asks: *does this template, applied to simple "follow the move" direction rules, make money on real Exness gold prices after spread?*

## Data

Exness **XAUUSDm** bid/ask ticks from the public archive `https://ticks.ex2archive.com/ticks/XAUUSDm/YYYY/MM/Exness_XAUUSDm_YYYY_MM.zip`, **2025-11 to 2026-10** (12 months, the same window as the BTC one-year study). 1-hour bid candles are built from the ticks in UTC. SHA-256 values of the zips are recorded. Missing data is never interpolated.

## Rules (fixed; nothing is tuned)

Evaluated at every closed 1-hour candle that has ticks within 60 seconds after its close (otherwise skipped, for example at weekends).

**Direction rules**
- **D1 candle momentum:** BUY if the hour closed above its open, SELL if below, nothing if equal.
- **D2 breakout momentum (primary):** SELL if the close is below the lowest low of the previous 3 hourly candles. BUY if the close is above their highest high. Nothing otherwise.
- **Random-direction benchmark:** the same template on every eligible hour, with a random BUY or SELL; 2,000 seeded runs. This shows what the template earns with no direction skill.

**Entry and levels**
- Entry at the first tick after the candle close: BUY at the ask, SELL at the bid. The real fill is used, without rounding.
- Stop 10 USD from the fill. TP1 is 5 USD, TP2 10 USD. TP3 is the round 10-USD level at least 30 USD away: BUY `ceil((E+30)/10)*10`, SELL `floor((E-30)/10)*10`.

**Exits (tick by tick, in exact tick order)**
- A BUY exits on the bid; a SELL exits on the ask.
- Targets fill at their level, as limit orders. Stops fill at the price of the tick that triggers them, so gap slippage is included.
- After 7 days, any open part closes at market.

**Management**
- **M1 (primary, the app's):** 1/3 of the position at each TP, with the stop moved to the fill price after TP1.
- **M2:** 1/3 at each TP; the stop is never moved.

**Overlap:** each signal is scored independently, as the app presents them. Overlapping signals are reported, not removed.

**Costs:** spread is real (bid/ask from the ticks). Commission is 0, as advertised for Exness Standard, **unverified**. Swap is **unknown** and not deducted. A **gross** run at mid prices (no spread) is also reported, to show how much the spread costs.

**R:** profit divided by the 10 USD initial risk.

## Pass/fail, decided now

The primary test is **D2 + M1, net of spread**. It passes only if **all** of these hold:
1. mean R > 0;
2. the 95% bootstrap CI of mean R is entirely above 0;
3. mean R is above the 95th percentile of the random-direction benchmark (M1, net).

Every other combination is reported but cannot rescue a failed primary test. A pass would justify only a **forward paper test**, never live trading. A fail means: **do not follow template-style signals of this kind.**
