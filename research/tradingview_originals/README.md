# Original TradingView scripts on US oil, gold and BTC

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict

**None of the original TradingView scripts gives reliable signals on US oil, gold or BTC.** This round tested the
scripts exactly as their authors wrote them, ported line by line from the Pine sources downloaded from TradingView:

- Lorentzian Classification (jdehorty);
- BigBeluga Session VWAP;
- UT Bot, SSL Channel, Chandelier Exit, HalfTrend and Supertrend (KivancOzbilgic);
- Range Filter (guikroth), Coral Trend, QQE MOD and Waddah Attar Explosion.

That makes 252 variants: each script, BUY and SELL, three standard exits, plus each script's own exit (stop-and-reverse,
or Lorentzian's 4-bar hold). **Only 1 of 252 beat random entry in 2025, where about 13 would be expected by luck alone,
and it did not repeat in 2026.** Nothing reached the untouched-data check, because nothing passed both years.

| Closest result | 2025 | 2026 |
|---|---|---|
| Oil, Range Filter BUY, target half the stop | 97 trades, 71.1% win, +0.053R, beat random (p = 0.049) | 83 trades, 66.3% win, −0.012R, did not beat random (p = 0.63) |

## About the 70% win rate

Thirteen variants won 70% or more of trades in one of the two years, mostly the short-target exit on oil and gold.
None did it in both years while also beating random entry. Random entry times with the same exit already win about
63 to 66%, so a 70% figure on its own says almost nothing about the indicator.

Lorentzian Classification came closest to a repeatable 70%. With the short-target exit on gold, it won 69.0% in 2025
and 73.2% in 2026 (BUY). Random entries with that exit won about 64 to 68%, and the difference was not significant in
either year.

## Why the scripts look better on TradingView

- **Repainting.** Some of these scripts can show a signal on a candle that is still forming, then remove it. This test
  used only closed 1H candles, so every signal shown is one you could actually have acted on.
- **Stop-and-reverse charts hide the losing streaks.** Charts mark the winning flips. Chop produces many small losses
  in a row, and those are easy to overlook.
- **Costs.** Here every trade paid the real Exness spread plus slippage. TradingView's default strategy tester charges
  nothing.

## Method in brief

- **Data.** Exness USOILm, XAUUSDm and BTCUSDm, every bid and ask quote, built into 15-minute bid/ask candles. Signals
  come from 1H candles. 2025 is used for selection and 2026 to now for confirmation.
- **Benchmarks.** Standard exits are compared with matched random entry. Each script's own exit is compared with
  random entries in the same quarter and direction, held exactly as long.
- **Reliable** means positive expectancy and beating random (p ≤ 0.05) in both years, with at least 30 and 20 trades.

Every variant is in [`reports/RESULTS.md`](reports/RESULTS.md).

## Reproducing

The Pine sources are not committed (they belong to their authors). `src/fetch_pine.py` downloads them, and
`sources_manifest/manifest.json` records what was fetched.

```bash
python src/fetch_pine.py           # optional: re-download the original sources
python src/run_originals.py        # about 20 minutes; writes reports/results.json
python src/write_report.py         # writes reports/RESULTS.md
python -m unittest discover -s tests -p "test_*.py"
```
