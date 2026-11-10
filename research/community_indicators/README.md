# Community-made indicators on oil, gold and BTC

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict: no community indicator gives reliable signals, and none reaches a reliable 70%

Eight of the most popular community-made TradingView indicators were re-implemented from their published open-source
logic, at their default settings:

- UT Bot Alerts
- SSL Channel
- Squeeze Momentum (LazyBear)
- WaveTrend (LazyBear)
- Chandelier Exit
- Hull Suite
- Range Filter
- QQE

Each was tested as BUY and SELL with three exits on US oil, gold and BTC: 144 signals in total. Every signal used real
Exness bid/ask fills. **None made money and beat random entry in both 2025 and 2026. None reached a 70% win rate in
both years.** Only 1 of 144 passed the 2025 stage, fewer than the roughly 7 expected from luck alone.

## Win rate follows the exit, not the indicator

Median win rate across all community signals and both years, next to random entries with the same exit:

| Market | Exit | Signals' win rate | Random entries' win rate | Signals' expectancy | Random expectancy |
|---|---|---|---|---|---|
| US oil | target half the stop | 63.4% | 63.1% | −0.063R | −0.061R |
| US oil | target = stop | 48.4% | 48.3% | −0.067R | −0.055R |
| US oil | trailing stop | 31.3% | 31.8% | −0.072R | −0.053R |
| Gold | target half the stop | 63.3% | 64.0% | −0.032R | −0.045R |
| Gold | target = stop | 48.0% | 49.5% | −0.056R | −0.032R |
| Gold | trailing stop | 34.3% | 33.8% | +0.031R | +0.033R |
| BTC | target half the stop | 64.1% | 64.3% | −0.035R | −0.033R |
| BTC | target = stop | 48.6% | 49.2% | −0.042R | −0.036R |
| BTC | trailing stop | 31.6% | 31.5% | −0.020R | −0.021R |

The indicators land within about a point of what random timing gets with the same exit. Gold's small positive figure
with the trailing stop comes from gold's 58% rise, and random entries match it. The best single win rate anywhere was
74%, in one year only.

## The closest calls

| Market | Signal | 2025 | 2026 | Why it is not reliable |
|---|---|---|---|---|
| Oil | Range Filter BUY, target half the stop | 97 trades, **71.1% win**, +0.053R, beat random (p = 0.049) | 83 trades, 66.3% win (random 66.1%), −0.012R | The only signal to pass 2025. It fell to random level in 2026 |
| Oil | Chandelier Exit BUY, target = stop | 107 trades, 52.3% win, +0.011R, did not beat random (p = 0.21) | 85 trades, 64.7% win, +0.274R, beat random (p = 0.02) | Strong in 2026 only, which fits luck |
| BTC | Chandelier Exit SELL, target = stop | 134 trades, 52.2%, +0.038R (p = 0.10) | 113 trades, 55.8%, +0.079R (p = 0.07) | Positive both years, but beat random in neither |
| Gold | WaveTrend BUY, trailing | 40 trades, 37.5%, +0.164R (p = 0.65) | 64 trades, 42.2%, +0.166R (p = 0.12) | Positive both years, in a strongly rising market. Random entries did about as well |

## Why other tools can claim 70%+ "accuracy"

Several popular community indicators **repaint**. LuxAlgo's Nadaraya-Watson Envelope is one: its default mode
recalculates past values, so its signals are redrawn in hindsight. Its publisher states this, and backtests of it are
known to look better than live results. ZigZag and fractal signals confirm a turn only after later candles. On a chart,
such signals look 80 to 90% right, but no one could have traded them in real time. They were excluded here for that reason.

Beyond repainting, the earlier scan showed two more effects:

- **A small target inflates the win rate.** A target a quarter of the stop gives random entries a 77 to 78% win rate
  on oil and gold, while they still lose money.
- **Some claims count only touches.** A signal is called "accurate" if the price ever touched the target, even after
  the stop was hit.

A claimed accuracy figure is checkable only with the full record: every signal's time, entry, stop and target, judged
against real prices with costs.

## Method in brief

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm, every bid and ask quote, as 15-minute candles. 2024 is warm-up only.
- **Indicators.** 1H bid candles; each indicator's published logic and default settings.
- **Fills and costs.** Buy at the ask, sell at the bid, plus 0.02% slippage.
- **Exits.** 1 × ATR target with a 2 × ATR stop; 2 × ATR target and stop; or a 2 × ATR stop with a 3 × ATR trail.
- **Reliable** means positive expectancy and beating matched random entry (p ≤ 0.05) in 2025, and again in 2026.

All 144 results are in [`reports/RESULTS.md`](reports/RESULTS.md). The engine reuses `research/indicator_scan` (read-only).

## Reproducing

```bash
cd research/community_indicators
python src/run_community.py                          # about 15 minutes
python -m unittest discover -s tests -p "test_*.py"
```
