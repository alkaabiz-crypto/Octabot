# Community-made indicators, round 2: oil, gold and BTC

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict: no reliable signal, and none reaches 70%

Nine more widely used community signals were tested from their open-source logic, at their default settings, each as
BUY and SELL with three exits, on US oil, gold and BTC. That is 153 variants on Exness bid/ask quotes:

- HalfTrend
- Coral Trend
- Waddah Attar Explosion
- Williams Vix Fix
- Ichimoku Tenkan/Kijun cross
- Parabolic SAR
- Schaff Trend Cycle
- Heikin Ashi flip
- Smart Money Concepts structure breaks

**One variant passed both 2025 and 2026: Williams Vix Fix BUY with the trailing exit, on BTC. It then failed on data it
had never seen.** None reached a 70% win rate in both years.

## The one pass, checked on untouched data

| Test | Trades | Vix Fix expectancy | Random entry | p vs random |
|---|---|---|---|---|
| BTC 2025 (selection, Exness) | 227 | +0.178R | | **0.002** |
| BTC 2026 (confirmation, Exness) | 197 | +0.157R | | **0.046** |
| **BTC 2020–2024 (Binance, never used to pick it)** | 1,194 | +0.102R | +0.113R | **0.67** |
| **ETH 2020–now (Binance, never used to pick it)** | 1,629 | +0.061R | +0.097R | **0.95** |

On five earlier years of BTC and seven years of ETH, the signal did no better than random entries with the same
trailing stop. The Binance figures use spread-free prices with a 0.05% round-trip cost. There are other warning signs too:

- Its 5 best trades are 85% of the 2025–26 profit. Without them it earns +0.03R.
- Its 2026 p-value (0.046) was only just under the bar.

**Expect this pass by chance.** Across this round and the two earlier scans, about 400 signals have gone through the
two-year test. With no real edge anywhere, roughly one would pass both years by luck, and that is what happened.

These checks were added after the result was seen. They are in `src/diagnostics_vixfix.py` and
`reports/diagnostics_vixfix.json`.

## Win rate follows the exit again

Median win rate across all round-2 signals and both years, next to random entries with the same exit:

| Market | Target half the stop | Target = stop | Trailing stop |
|---|---|---|---|
| US oil: signals / random | 63.6% / 63.1% | 49.6% / 48.6% | 33.2% / 31.8% |
| Gold: signals / random | 67.0% / 64.0% | 52.1% / 49.5% | 36.6% / 33.8% |
| BTC: signals / random | 64.3% / 64.3% | 49.3% / 49.9% | 31.4% / 31.9% |

Gold signals ran slightly above random, but only in a market that rose 58% in this period. No gold signal beat random
in both years.

### Other near misses (passed one year, failed the other)

| Market | Signal | 2025 | 2026 |
|---|---|---|---|
| Oil | Waddah Attar BUY, target half the stop | 67.7% win, beat random (p = 0.018) | 63.7% win, below random |
| Oil | SMC structure break SELL, target = stop | 55.1% win, beat random (p = 0.032) | 46.2% win, lost money |
| Gold | SMC structure break BUY, target = stop | 62.8% win, +0.23R, beat random (p = 0.037) | 49.1% win, lost money |
| BTC | Parabolic SAR SELL, target = stop | 51.8% win, beat random (p = 0.032) | not significant (p = 0.12) |

The SMC structure-break signals, the most popular community tool for gold, showed the pattern most clearly. A strong
2025 was followed by losses in 2026.

## Where this leaves the search

Across all studies so far, no hourly signal tested has a reliable, repeatable edge on oil, gold or BTC. That covers
standard indicators, 17 community indicators, hourly time effects, RSI/VWAP and Donchian breakouts. The best remaining
research candidate is still VWAP momentum BUY on BTC/ETH (`research/rsi_vwap_study`), and even that is unproven.

## Reproducing

```bash
cd research/community_indicators_2
python src/run_community2.py                                     # about 16 minutes
FROZEN_BTC_BREAKOUT=<frozen research/btc_breakout> python src/diagnostics_vixfix.py
python -m unittest discover -s tests -p "test_*.py"
```

All 153 results are in [`reports/RESULTS.md`](reports/RESULTS.md).
