# Daily signal DCA bot: data from 2025-01-01 only

**User instruction (2026-11-10): never use data before January 2025.** Every candle here starts on 2025-01-01 (Binance BTCUSDT and ETHUSDT, through 2026-11-09). The rules and costs are the same as in `../PREREGISTRATION.md`, with one forced change: a moving average is left out of TREND_ENS until it has enough post-2025 history. SMA200 therefore only starts voting in mid-July 2025.

## Results (lump sum, 0.1% fee, 2025-01-01 to 2026-11-09, about 22 months)

| Signal | BTC return | BTC max drop | ETH return | ETH max drop |
|---|---|---|---|---|
| **TREND_ENS (primary)** | **+1.2%** | **−22.1%** | **+40.9%** | **−33.4%** |
| TREND_ENS + vol targeting | +8.0% | −21.9% | +38.6% | −25.9% |
| SMA50 | +28.5% | −25.5% | +151.2% | −29.5% |
| SMA200 (only active from mid-2025) | −8.5% | −19.7% | −21.7% | −41.7% |
| MAX10 | −0.4% | −23.7% | −1.6% | −46.3% |
| MOM1 (follow yesterday) | −36.5% | −39.7% | −43.8% | −55.3% |
| REV_RSI2 (buy dips) | −2.6% | −32.2% | +48.2% (+99% in 2025, −26% in 2026) | −37.3% |
| Hours 21–23 UTC, 0.1% fee | −66.1% | | −57.4% | |
| **Buy and hold** | **−20.9%** | **−53.0%** | **−36.7%** | **−67.5%** |

**By year, TREND_ENS:**
- BTC: −7.4% in 2025 (buy and hold −7.4%) and +9.3% in 2026 (buy and hold −14.6%).
- ETH: +37.9% in 2025 (buy and hold −11.7%) and +2.2% in 2026 (buy and hold −28.4%).

## DCA version (10 USD a day from 2025-01-01; 6,770 USD put in)

| | BTC final | BTC worst point | ETH final | ETH worst point |
|---|---|---|---|---|
| Plain daily DCA | 5,915 (**−12.6%**) | −36.5% | 5,819 (**−14.0%**) | −40.0% |
| **TREND_ENS DCA** | 7,122 (**+5.2%**) | **−8.9%** | 7,722 (**+14.1%**) | **−10.5%** |
| SMA50 DCA | 7,762 (+14.7%) | −10.7% | 10,405 (+53.7%) | −2.2% |

## Reading this honestly

- In this window both coins **fell** (BTC −21%, ETH −37%). The trend bot's value was **staying out of most of the fall.** It ended flat to positive, with less than half of buy and hold's drop.
- **SMA50 looks best here, but choosing it now would be hindsight.** TREND_ENS was the pre-registered primary, and SMA50 had a −51% drop in the 2022–26 test. Over a short window, single-average rules swing a lot.
- **22 months is short:** about 110 position changes, in one market regime. These results support a forward paper test, not live money.
- **Fast signals** (MOM1, the 21–23 UTC hours) lose heavily after fees, as in the longer test.

Files: `run.py`, `data/*_from2025.csv.gz`, `results/results.json`.
