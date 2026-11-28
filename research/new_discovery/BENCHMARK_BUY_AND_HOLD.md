# Buy-and-hold reference (12 November 2026)

**What this is.** The "do nothing clever" benchmark that any strategy in this repository should be compared with.
- Price change from the first to the last available price in each period.
- The data are the same ones used by the audits and screens: Exness 1-minute mid bars (rebuilt from the public tick archive with the frozen bar builder), Binance ETHUSDT 1m and BTCUSDT 1h.
- Not committed (third-party data).

| Market | 2025 | 2026 (to last data) | Full period | Max drawdown (full) |
|---|---|---|---|---|
| Gold (XAUUSDm) | +64.5% | −10.3% (to 10-30) | +47.6% | −30.8% |
| WTI oil (USOILm) | −20.1% | +78.1% | +42.3% | −40.6% |
| DAX (DE30m) | +24.2% | +4.8% | +30.2% | −19.6% |
| S&P 500 (US500m) | +16.1% | +10.7% | +28.6% | −21.9% |
| Nasdaq 100 (USTECm) | +19.8% | +17.0% (to 10-28) | +40.1% | −26.5% |
| ETH (Binance spot) | −11.0% | −29.5% (to 11-10) | −37.3% | −69.5% |
| BTC (Binance spot) | −7.2% | −14.0% (to 11-09) | −20.2% | −53.7% |

## Caveats, all material

- **Price returns only.** Dividends, interest and fees are excluded.
- **Holding a CFD long costs daily swap (financing).** For index and gold CFDs that is typically several percent a year, which this table **does not deduct**. Owning a cheap index fund or the spot asset avoids most of it. [UNKNOWN] Exness's actual swap rates were not retrieved.
- **One period, chosen by the data available, not a forecast.** Buy-and-hold lost heavily on ETH and BTC over the same months, with drawdowns of 54–70%.
- **Hindsight.** The best market in this table is known only afterwards. The fair benchmark is a diversified, pre-chosen allocation, sized to a drawdown the holder can tolerate.

## Why it matters

In this period, a passive S&P 500 or Nasdaq holding gained 29–40% with drawdowns of 22–27%. None of the tested active strategies has a validated edge after the causal correction (`research/audits/library_candidates/CAUSAL_IMPACT_ASSESSMENT.md`). A strategy is only worth running with real money if it beats this kind of benchmark after its own costs, on data it was not selected on.
