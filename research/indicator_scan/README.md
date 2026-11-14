# Indicator scan on US oil and gold

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict

**No indicator gives reliable signals on US oil or gold, and none gives a reliable 70%+ win rate that also makes
money.** 120 signals were tested: 10 popular indicators, BUY and SELL, three exit designs, on both markets. Each had to
make money in 2025 and confirm it in 2026, beating random entry both times. **None did.**

The result agrees with published research. Technical trading rules on crude oil and other commodity futures look
profitable in-sample, but the profit mostly disappears after correcting for data snooping and testing out-of-sample
with costs. ([CXO Advisory summary of Marshall et al.](https://www.cxoadvisory.com/technical-trading/does-technical-trading-work-with-commodity-futures/);
[crude oil futures study](https://www.cxoadvisory.com/commodity-futures/performance-of-technical-trading-rules-for-crude-oil-futures/).)
For gold, the positive high-frequency result found is gross of costs
([summary](https://www.cxoadvisory.com/technical-trading/high-frequency-technical-trading-of-gold-and-silver/)).

## Why "70% accurate" is mostly set by the exit, not the indicator

Win rate is controlled by where the target sits relative to the stop. With the target at half the stop distance,
**random entry times already win about 63 to 64% of trades.** Median result across all signals and both periods:

| Exit | Median win rate: signals | Median win rate: random entries | Median expectancy: signals | Median expectancy: random |
|---|---|---|---|---|
| Oil, target half the stop (HW) | 63.1% | 63.1% | −0.053R | −0.059R |
| Oil, target equals stop (SYM) | 49.2% | 48.3% | −0.029R | −0.054R |
| Oil, trailing stop (TRAIL) | 33.6% | 31.8% | −0.022R | −0.018R |
| Gold, HW | 65.4% | 64.0% | −0.012R | −0.044R |
| Gold, SYM | 50.0% | 49.5% | +0.023R | −0.033R |
| Gold, TRAIL | 35.1% | 33.8% | +0.008R | +0.042R |

The indicators barely move the win rate away from what random entry gets with the same exit.

A smaller target pushes "accuracy" higher without any skill. A post-hoc check used random entry times from 2025 to now,
with the target at a quarter of the stop distance (0.5 × ATR target, 2 × ATR stop):

| Market | Random BUY entries | Win rate | Expectancy |
|---|---|---|---|
| US oil | 10,430 | **77.3%** | −0.036R |
| Gold | 10,497 | **78.3%** | −0.036R |

Random entries win more than three trades in four and still lose money. A small win paid often does not cover the
occasional full stop plus costs. The low win rate of the earlier BTC strategies came from their trailing exit, not
from bad entries.

**So a 70%+ accuracy claim means nothing without the stop and target sizes, the costs, and an out-of-sample trade
record.** Without those, it cannot be checked. Typical reasons such claims do not hold up:

- the target is much smaller than the stop;
- losing signals are left open, or are not counted;
- results are in-sample;
- "accurate" means the price touched the target at some point, rather than before the stop.

## What came closest

| Market | Signal | 2025 | 2026 | Why it is not reliable |
|---|---|---|---|---|
| Gold | Donchian 20 BUY, HW exit | 258 trades, **72.1% win**, +0.050R | 149 trades, **70.5% win**, +0.048R | The only 70%+ signal in both years. But in 2025, random long entries with the same exit won 68.3% (gold was rallying), so it did not beat random (p = 0.16). At stress cost it is about zero. |
| Oil | Stochastic BUY, trailing exit | 147 trades, 36% win, +0.126R, beat random (p = 0.005) | 113 trades, 39% win, +0.052R, did not beat random (p = 0.45) | Did not confirm in 2026 |
| Oil | MACD BUY, HW exit | 197 trades, 70.1% win, +0.045R, beat random (p = 0.013) | 182 trades, 62.6% win, −0.045R | Win rate and profit both fell in 2026 |
| Oil | MACD BUY, SYM exit | 186 trades, 54% win, +0.053R, beat random (p = 0.031) | 166 trades, 53% win, +0.065R, did not beat random (p = 0.48) | Did not confirm in 2026 |

Three oil signals passed the 2025 test. About six would be expected by chance among 120, and none of the three
confirmed in 2026. No gold signal passed 2025.

The gold Donchian HW signal is the one worth watching. It is the same breakout entry as the frozen BTC strategy, with
a short target. If you want to pursue it, it needs its own frozen forward paper test. It must not be tuned, and it is
not a live signal.

## Method in brief

- **Data.** Exness USOILm and XAUUSDm, every bid and ask quote, 2025-01 to 2026-11-09 (2024 used only for warm-up).
- **Indicators.** RSI 14 reversion, RSI 2 extremes, Bollinger 20/2 re-entry, Stochastic 14/3/3, MACD 12/26/9,
  EMA 9/21 cross, Donchian 20 breakout, VWAP momentum, Supertrend 10/3 and CCI 20, all at textbook settings on 1H candles.
- **Exits.** Target half the stop (HW), target equal to the stop (SYM), or trailing stop (TRAIL). Stops are 2 × ATR.
- **Costs.** Real spread (buy at the ask, sell at the bid), plus 0.02% slippage.
- **Reliable** means beating matched random entry (p ≤ 0.05) with positive expectancy in 2025, and again in 2026.

Every result is in [`reports/RESULTS.md`](reports/RESULTS.md).

## Reproducing

```bash
cd research/indicator_scan
python src/run_scan.py                               # about 10 minutes
python -m unittest discover -s tests -p "test_*.py"
```
