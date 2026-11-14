# Instruments

All prices are Exness **Standard-account CFD** quotes (symbols ending in `m`) from the public tick archive `https://ticks.ex2archive.com/ticks/<SYMBOL>/<YYYY>/<MM>/`. Ticks are aggregated to 15-minute bid/ask candles in UTC by `research/oil_rsi_vwap/src/build_bars.py`. These are broker CFD prices, **not** exchange futures or spot-market prints.

| Market | Exness symbol | What it is | Notes |
|---|---|---|---|
| Gold | XAUUSDm | Spot gold CFD, USD per troy ounce | Trades about 23 h on weekdays |
| WTI crude | USOILm | CFD referenced to **WTI crude futures**, rolled by the broker | Not spot oil and not a single futures contract. Roll adjustments can create jumps. |
| Brent crude | UKOILm | CFD referenced to **ICE Brent futures**, rolled by the broker | Different underlying, roll calendar and session from USOILm. It is **not** interchangeable with WTI. |
| Bitcoin | BTCUSDm | Crypto CFD, 24/7 | Broker price, not an exchange order book |
| Ether | ETHUSDm | Crypto CFD, 24/7 | Same |
| EUR/USD | EURUSDm | Spot FX CFD | |
| GBP/USD | GBPUSDm | Spot FX CFD | |
| USD/JPY | USDJPYm | Spot FX CFD | |
| S&P 500 | US500m | Index CFD on the S&P 500 | Not the ES future; broker quotes outside cash hours |
| Nasdaq 100 | USTECm | Index CFD on the Nasdaq 100 | Not the NQ future |
| DAX 40 | DE30m | Index CFD on the DAX 40 | Exness keeps the legacy name DE30 |

**History available here.** XAUUSDm from 2020-01, USOILm from 2019-02 and BTCUSDm from 2020-01. All other symbols from 2023-01. Every symbol runs to about 2026-11-10.

**Not available.** Exchange volume, order-book depth and true order flow. The CFD feed has only quote ticks; the `ticks` column is a quote count. Volume-delta and order-flow indicators therefore **cannot be tested** with this data.

**Swaps.** Overnight financing (swap) is not in the data. Primary costs assume none; the stress costs add 0.02% of notional per day.
