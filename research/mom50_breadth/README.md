# MOM50 breadth test: results

The rules were fixed in `PREREGISTRATION.md` (commit `9c060202`) before any of this data was downloaded.
- **Markets:** 15 Exness markets, ticks from 2025-01 to 2026-10, built into daily candles (450–474 days each). None was dropped.
- **Rule:** gold's frozen MOM50 + ATR rule, at 2× the real spread.

## Verdict: FAIL, clearly

| | Result |
|---|---|
| Mean Sharpe across the 15 markets | **−0.11** |
| Random timing with the same exposure: median / 95th pct | +0.18 / +0.38 |
| **Rule percentile against random timing** | **0.3** |
| Buy-and-hold mean Sharpe | +0.62 |
| Markets where the rule beat its own random shifts (above the 50th percentile) | 4 of 15 |
| Markets where it beat buy and hold | 1 of 15 (US natural gas, where both lost) |

| Market | Rule net | Buy & hold | Percentile vs own shifts | Trades |
|---|---|---|---|---|
| Silver | +11.2% | +54.3% | 44 | 18 |
| Platinum | −7.8% | +49.0% | 57 | 18 |
| Palladium | −50.7% | +4.7% | 62 | 16 |
| Brent oil | +41.7% | +57.1% | 70 | 12 |
| Natural gas | −41.3% | −28.5% | 49 | 16 |
| Dow (US30) | +7.6% | +24.6% | 33 | 15 |
| S&P 500 | +4.2% | +35.2% | 7 | 20 |
| Nasdaq (USTEC) | +2.8% | +50.1% | 8 | 19 |
| DAX (DE30) | −17.8% | +11.8% | 0.4 | 21 |
| FTSE (UK100) | −3.0% | +23.1% | 0.8 | 19 |
| Nikkei (JP225) | +34.1% | +69.1% | 47 | 21 |
| Hang Seng | −9.5% | −2.4% | 37 | 18 |
| CAC (FR40) | −11.1% | −2.6% | 14 | 16 |
| ASX (AUS200) | −7.7% | +12.5% | 3 | 15 |
| STOXX50 | −4.1% | +12.2% | 23 | 15 |

## What this means

- **On markets it was not built on, the rule's timing was much worse than random.** It lagged buy and hold almost everywhere.
  - The tight ATR exits sell after normal pullbacks, and the 50-day entry buys late. That pattern is called whipsaw.
- **Gold's +49% backtest (93.6th percentile on gold) looks like one lucky fit to gold's 2025–26 path, not a general edge.**
- **The gold MOM50 forward paper test keeps running unchanged,** since its rules are frozen. The recommendation is withdrawn: it should **not** be used on a demo or with money on the strength of the backtest.

Files: `build.py` (tick download → daily candles; zips deleted, SHA-256 kept in `data/*_sha256.json`), `study.py`, `results/results.json`, `data/*_daily.csv`.
