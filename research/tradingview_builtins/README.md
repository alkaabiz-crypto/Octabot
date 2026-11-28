# Every TradingView built-in, the top community strategies, and signal + filter combinations

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict

**No TradingView indicator or strategy, built-in or community, gives reliable BUY or SELL signals on US oil, gold or
BTC. Adding an entry condition (a trend, strength or VWAP filter) does not change that.**

3,288 variants were tested across the three markets:

| Part | What was tested |
|---|---|
| A. Built-in strategies | All 21 of TradingView's built-in strategies, replayed from their Pine source, with their own entries, exits and stop orders, including Technical Ratings and Rob Booker's ADX breakout |
| B. Built-in indicators | 62 directional built-in indicators at their defaults (moving averages, oscillators, volume, channels, stops, divergence), BUY and SELL, three standard exits, plus hold-to-opposite-signal where signals alternate |
| C. Community strategies | ChartArt's most-liked double strategies (Bollinger + RSI, MACD + SMA 200, Golden Cross, MACD + Stochastic, Stochastic + RSI) |
| D. Signal + entry condition | Every variant that made money in 2025, combined with each of four fixed filters: 4H EMA 200 side, daily EMA 200 side, ADX 14 > 20, and session VWAP side |

The earlier rounds in this folder's siblings covered the most-liked community scripts (Lorentzian Classification,
Squeeze Momentum, UT Bot, Supertrend, SSL, Chandelier, HalfTrend, Range Filter, QQE MOD, WaveTrend, Coral Trend,
Waddah Attar, Vix Fix, SMC and others). None of them passed either.

## What happened

- **Passed 2025:** 96 of 3,288 variants beat random entry, *fewer* than the roughly 160 expected by luck alone.
- **Passed both 2025 and 2026:** 1. That is about what luck would produce: around 8 would be expected among this many tries.
- **That one failed on untouched data.** It was gold, BBTrend BUY with the ADX > 20 filter and a ±1R exit:

| Period | Trades | Win rate | Expectancy | p vs random |
|---|---|---|---|---|
| 2025 | 87 | 65.5% | +0.240R | 0.038 |
| 2026 | 70 | 57.1% | +0.124R | 0.038 |
| **2020–2023, never used before** | 354 | 49.7% | **−0.031R** | 0.32 |

On four years of data it had never seen, it won half its trades and lost money: a lucky pass, not an edge.

## The 70% win rate

Five filtered variants won 70% or more of their trades in both years (all with the short target, at half the stop
distance). For example, BTC Aroon BUY with the 4H EMA 200 filter won 70.1% and 72.6%. Random entry times with the
same exit won about 63 to 68% on the same market and years. None of the five beat random entry in both years.

Across all short-target variants, the median 2025 win rate equals the random-entry win rate almost exactly:

| Market | Median win rate: signals | Median win rate: random entries |
|---|---|---|
| US oil | 63.2% | 62.6% |
| Gold | 68.3% | 68.3% |
| BTC | 64.9% | 64.9% |

**A 70% win rate is something the exit produces, not the indicator.** A target smaller than the stop gives it to random
entries too, and they still lose money after costs.

## What this means

- Over this research programme, more than 4,000 indicator and strategy variants have now been tested, and none showed
  a repeatable hourly edge on these three markets.
- Claims of 70%+ accuracy from other tools should be checked for these four things: the stop and target sizes, costs,
  a record kept out-of-sample, and whether random entries with the same exit would do as well.
- The only candidate still standing is the earlier **VWAP momentum BUY with trailing stop on BTC/ETH**
  (`research/rsi_vwap_study`). It is narrow, unconfirmed, and worth no more than a frozen forward paper test.
- Nothing here justifies live trading.

## Method in brief

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm, every bid and ask quote, built into 15-minute bid/ask candles. Signals
  come from 1H candles. 2025 is used for selection and 2026 to now for confirmation.
- **Untouched-data check.** It applies to anything passing both years. It uses US oil 2019–2024 and gold 2020–2023
  (both Exness ticks), and BTC 2020–2024 (Binance, 0.05% cost).
- **Costs.** Real spread (buy at the ask, sell at the bid) plus 0.02% slippage.
- **Benchmarks.** Standard exits are compared with matched random entry. Strategy and hold-to-opposite legs are
  compared with random entries in the same quarter and direction, held exactly as long. 1,000 runs each.
- **Pass rule.** In both years: at least 30 and 20 trades, positive expectancy, and p ≤ 0.05 against random entry.
- **Implementation notes.**
  - Filters are applied at the signal bar. For strategies, a trade is kept only if its signal bar passes the filter.
  - ChartArt's strategies only reverse or close, so their trades are few and long.
  - Tests check that no signal, filter or strategy order uses future data.

Every variant is in [`reports/RESULTS.md`](reports/RESULTS.md).

## Reproducing

```bash
cd research/tradingview_builtins
python src/run_everything.py      # about 50 minutes on 3 cores; writes reports/results_<market>.json
UNTOUCHED_DIR=/path/to/untouched FROZEN_BTC_BREAKOUT=/path/to/frozen/research/btc_breakout python src/untouched.py
python src/write_report.py
python -m unittest discover -s tests -p "test_*.py"
```

The untouched data is rebuilt with `research/oil_rsi_vwap/src/build_bars.py` (USOILm 2019-02 to 2024-12, XAUUSDm
2020-01 to 2023-12). TradingView sources are not committed; `sources_manifest/` records what was fetched.
