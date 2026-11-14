# The requested indicators, each tested on its own

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed. No indicators were combined.

## Verdict: none of them gives reliable signals, and none reaches 70% in both years

Every indicator from the screenshot and the settings list was tested separately on US oil, gold and BTC, using
Exness bid/ask quotes. That is 192 variants, each as BUY and SELL with three exits. Volume Profile was tested on US
oil only, as requested.

**No variant made money and beat random entry in both 2025 and 2026. None reached a 70% win rate in both years.**
Only 1 of 192 passed the 2025 stage, where about 10 would be expected by luck alone. The pre-registered check on
older data was therefore not needed.

## Results by indicator

| Indicator (your settings) | US oil | Gold | BTC | Verdict |
|---|---|---|---|---|
| **Session VWAP + standard deviation bands** (BigBeluga-style), band reversion | fail | fail | passed 2026 only | Not reliable |
| **Session VWAP + standard deviation bands**, band breakout | passed 2025 only | passed 2026 only | passed 2026 only | Not reliable |
| **Squeeze Momentum (LazyBear default)**, tested earlier with identical settings | fail | fail | fail | Not reliable |
| **Lorentzian Classification (jdehorty defaults)** | fail | passed 2026 only | fail | Not reliable |
| **EMA 20 / 50 / 200** pullback | passed 2026 only | passed 2026 only | fail | Not reliable |
| **Session VWAP (default session)**, cross | fail | fail | fail | Not reliable |
| **RSI 14** (30 / 70) | passed 2026 only | fail | fail | Not reliable |
| **RSI 14 divergence** | fail | fail | fail | Not reliable |
| **ADX 14, threshold 20** | fail | fail | fail | Not reliable |
| **ADX 14, threshold 25** | fail | passed 2026 only | passed 2026 only | Not reliable |
| **Volume Profile, 70% value area** (US oil), "80% rule" | fail | | | Not reliable |
| **Volume Profile, 70% value area** (US oil), breakout | fail | | | Not reliable |
| **Supertrend 10, 3** (BTC) | | | fail (0 of 12 periods positive) | Not reliable |
| **MACD 12/26/9** (BTC) | | | fail | Not reliable |
| **ATR 14** | Volatility only, not a direction signal. It set every stop and target here. | | | Not applicable |

"Fail" means it beat random entry in neither year. "Passed 2026 only" means it lost or matched random in 2025 and
beat it in 2026. 14 of the 15 one-year passes came in 2026, so it looks like a market phase, not a lasting edge.

**Candle delta, from the BigBeluga script, could not be tested.** It needs buyer versus seller volume, which Exness
quotes do not record.

## How "70%+" shows up, then disappears

The highest win rate in the whole test was **84.8%: ADX 14 (threshold 25) BUY on gold**, with a target half the stop,
over 33 trades in 2026. In 2025 the same signal won only 59.3% and lost money. The Lorentzian BUY on gold went from
69.1% in 2025 to 76.8% in 2026.

A short run like that is easy to show as proof of "80% accuracy". Over two years, neither signal beat random entries.

Median win rate across all signals and both years, next to random entries with the same exit:

| Exit | Oil: signals / random | Gold: signals / random | BTC: signals / random |
|---|---|---|---|
| Target half the stop | 63.5% / 63.1% | 65.0% / 64.0% | 64.4% / 64.3% |
| Target = stop | 49.0% / 48.3% | 49.8% / 49.5% | 48.7% / 49.2% |
| Trailing stop | 33.2% / 31.8% | 35.3% / 33.8% | 31.8% / 31.5% |
| Lorentzian's own 4-hour exit | 45.4% / 46.2% | 46.5% / 47.4% | 45.9% / 47.0% |

Once again the win rate follows the exit, not the indicator.

## Notes on the two scripts from the screenshot

- **Lorentzian Classification.** Rebuilt from the `advanced-ta` Python port's defaults: 8 neighbours, 2,000 bars, the
  five default features, volatility and regime filters, and the kernel filter. Two changes were made to avoid
  look-ahead:
  - That port scales two features using the whole data set's minimum and maximum, which leaks future information. A
    backtest using the port directly would look better than reality. This test uses the Pine original's running minimum
    and maximum instead.
  - The neighbour search uses the 2,000 bars before each bar.

  Its signals did no better than random on any market.
- **Session VWAP Profile (BigBeluga).** TradingView pages are blocked from this environment, so the script was rebuilt
  from its documented parts: session VWAP, volume-weighted standard deviation bands, and a session profile. It is a
  charting tool, so standard band-reversion and band-breakout rules were tested.

## Reproducing

```bash
cd research/requested_indicators
python src/run_requested.py                          # about 22 minutes
python -m unittest discover -s tests -p "test_*.py"
```

All 192 results are in [`reports/RESULTS.md`](reports/RESULTS.md).
