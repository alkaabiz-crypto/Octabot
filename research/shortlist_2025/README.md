# Research shortlist screen on 2025+ data

The rules, costs and screen were fixed in `PREREGISTRATION.md` (commit `1d0c7f6e`) before any result was computed. Nothing was tuned. All data starts on 2025-01-01:
- **Gold and US oil:** Exness XAUUSDm and USOILm bid/ask ticks, 2025-01 to 2026-10 (156.8M gold ticks, 45.5M oil ticks).
- **BTC and ETH:** Binance daily candles, 2025-01 to 2026-11-09.

**This is a screen, not proof.** Each rule has under two years of data, and a "consistent" label only qualifies it for a forward **paper** test.

## Verdicts

| Market | Rule | Net, 1× costs | Net, 2× costs | Max drop | Trades | Buy and hold, same window | Verdict |
|---|---|---|---|---|---|---|---|
| Gold | **MOM50 + ATR exits** (Forecast-to-Fill template) | **+49.1%** | **+49.0%** | **−13.4%** | 17 | +32.0%, max drop −27.0% | **CONSISTENT** |
| Gold | **Long only 22:00–07:00 UTC (Asian session)** | **+20.0%** | **+16.6%** | −15.0% | 472 | — | **CONSISTENT**, ⚠ overnight swap not deducted |
| Gold | Long only 13:00–21:00 UTC (US session) | +1.3% | −1.1% | −18.9% | 398 | — | not confirmed |
| Gold | Close above 200-day SMA (from 2025-10-10) | +6.6% | +6.6% | −22.1% | 2 | +1.1%, max drop −27.0% | not confirmed (too few trades) |
| Gold | Sep/Nov only (control) | +10.7% | +10.7% | −8.0% | 3 | +51.4% | not confirmed, as expected |
| US oil | 1/3/12-month momentum blend, long/short (from 2026-02) | +12.9% | +12.8% | −29.1% | 3 | +60.6% | not confirmed |
| US oil | Turtle 55/20 breakout, long/short | −6.3% | −6.8% | −32.2% | 9 | +52.0% | not confirmed |
| US oil | Intraday momentum (first 30 min → last 30 min, New York time) | −14.8% | −24.4% | −24.4% | 456 | — | not confirmed: **wrong direction**, 44% wins |
| BTC | **Close above SMA50** | **+28.6%** | **+23.5%** | −26.9% | 20 | −21.0%, max drop −53.0% | **CONSISTENT** |
| BTC | Donchian ensemble, 5–360 days (no leverage) | −6.3% | −7.8% | −14.9% | 285 | −21.0% | not confirmed |
| BTC | MAX20, hold next day | +6.6% | −1.2% | −14.9% | 38 | −21.0% | not confirmed |
| BTC | MAX10, hold next day | −6.7% | −16.9% | −17.2% | 58 | −21.0% | not confirmed |
| BTC | MIN10 (control) | −9.5% | −20.3% | −32.0% | 64 | −21.0% | not confirmed, as expected |
| ETH | **Donchian ensemble** (no leverage) | **+4.2%** | **+3.1%** | −12.0% | 257 | −36.8%, max drop −67.6% | **CONSISTENT** (low exposure, 9%) |
| ETH | Close above SMA50 | +151.2% | +146.7% | −30.1% | 9 | −36.8% | not confirmed (9 trades, under 10) |
| ETH | **MAX20, hold next day** | +9.5% | +2.5% | −31.1% | 33 | −36.8% | **CONSISTENT**, marginal at 2× |
| ETH | **MAX10, hold next day** | +37.8% | +24.9% | −22.6% | 49 | −36.8% | **CONSISTENT** |
| ETH | MIN10 (control) | −17.8% | −26.7% | −38.8% | 58 | −36.8% | not confirmed, as expected |

**Not testable under the 2025+ data rule:** gold's 24-month momentum and 36/48-month moving-average rules (rank 1 in the research), and the 10-month SMA. They need 10–48 months of history.

## Reading the results

- **Gold:** the momentum-entry rule with an ATR stop, a trailing stop and a 30-day exit beat buy and hold (+49% vs +32%) with half the drop. That held at double the real spread, because it trades only 17 times.
  - **Asian-hours-only** gold was positive (+20%), but it holds every night across the daily rollover. **Exness swap is not deducted**, so this result is likely overstated.
  - The US-session version is about zero, which matches the published "overnight up, day down" pattern.
- **US oil:**
  - **Nothing passed.** The best oil-specific published rule (intraday momentum) went the **wrong way**, with 44% wins.
  - Slow trend had too few trades to judge.
  - Buy and hold won (+40–60%) because oil rallied.
- **Crypto:**
  - Every trend filter avoided most of the 2025–26 fall (BTC −21%, ETH −37%).
  - The published Donchian ensemble was tiny at no leverage: average exposure was only 9–16%.
  - The bitcoin MAX rules lose at 2× costs, while ETH's held up.
  - Mixed coin-by-coin results like these are what short samples look like.
- **Controls** (Sep/Nov gold, buy-the-low crypto) failed, as they should. That supports the engine, not the rules.

## What qualifies for a forward paper test

1. **Gold MOM50 + ATR exits**: the strongest result and fully specified.
2. **BTC close above SMA50**: overlaps the TREND_ENS paper bot already running.
3. **ETH MAX10, ETH Donchian ensemble**: weaker, single-coin.
4. **Gold Asian session**: only after the real Exness swap cost is known.

Files: `screen.py`, `results/results.json` (all numbers, data checks and SHA-256 values).
