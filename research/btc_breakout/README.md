# BTC volatility-compression / breakout research

Paper research only. No live orders were placed and no account settings were changed.

## Verdict

**A candidate edge passed every pre-registered test, but the evidence is moderate, not proven.**

The surviving strategies are long-only 1H breakouts, taken only when the 4H trend is up, and exited with an ATR trailing stop. Three closely related variants passed both the walk-forward test and the untouched holdout:

- Bollinger squeeze breakout, long, trailing stop
- Donchian 20 breakout, long, trailing stop
- Donchian 20 breakout with volume confirmation, long, trailing stop

Up to 80% of these variants' entries are the same trades, so they are one idea, not three independent edges.

Everything else failed: all shorts, every 15-minute variant, and every fixed-target variant except one long that later failed the holdout.

Do not go live on this result. The next step is forward paper trading (see the recommendation at the end).

## Data

- **Source:** Binance BTCUSDT spot klines for 2018-06-01 to 2026-11-08 at 15m, 1h, 4h and 1d, downloaded from `data-api.binance.vision`, Binance's official public mirror.
- **Files:** `data/btc_*.json.gz`. The SHA256 checksums of the uncompressed files are in `data/SHA256SUMS`.
- **Exness:** BTCUSDm price history was not available. Exness's website blocks automated access with a Cloudflare challenge, so its spread, commission, swap and contract size could not be verified.
- **Costs used:** round-trip costs are hypothetical scenarios of 0.02%, 0.05% and 0.10% of price. Swaps are excluded.
- **Gaps:** short Binance trading halts are left as gaps in the data.

## Protocol

The rules were written before any results were produced. See `src/protocol.py`.

- **Variants:** 6 entry models with textbook parameters and no optimisation, giving 48 variants (2 timeframes × long or short × fixed or trailing stop).
- **Entry:** at the next 15m open after a closed signal candle.
- **Walk-forward:** 11 half-year windows from 2020H1 to 2025H1. Nothing was fitted, so every window is out-of-sample.
- **Holdout:** 2025-07-01 to 2026-11-08 was evaluated once, only after the pass list was locked. The SHA256 of the locked list was `4a59ccd5…`.
- **Pass rule:**
  - walk-forward at mid cost: at least 60 trades, expectancy above 0 with t ≥ 2.0, profit factor at least 1.2, positive in at least 7 of 11 windows, and expectancy still above 0 at high cost;
  - holdout: expectancy above 0, profit factor at least 1.1, and at least 10 trades.
- **Overlap note:** earlier Supertrend research phases used part of the holdout period. The breakout models had never been run on any period before this study.

## Results: the 3 survivors (mid cost 0.05% unless stated; 0.5% of equity risked per trade)

| Variant | Period | Trades | Net return | Profit factor | Expectancy (R) | t | Max drawdown | Win rate | Avg hold | Expectancy at high cost |
|---|---|---|---|---|---|---|---|---|---|---|
| BB squeeze, long, trail | Walk-forward | 274 | +64.8% | 1.68 | +0.38 | 2.40 | 8.5% | 34% | 22h | +0.34 |
| | Holdout | 52 | +4.5% | 1.34 | +0.18 | 0.76 | 4.5% | 40% | 22h | +0.11 |
| Donchian 20, long, trail | Walk-forward | 471 | +64.0% | 1.42 | +0.22 | 2.20 | 9.9% | 34% | 23h | +0.18 |
| | Holdout | 99 | +11.7% | 1.43 | +0.25 | 0.77 | 5.4% | 33% | 21h | +0.18 |
| Donchian 20 + volume, long, trail | Walk-forward | 377 | +71.4% | 1.58 | +0.30 | 2.52 | 5.5% | 35% | 23h | +0.26 |
| | Holdout | 81 | +11.3% | 1.50 | +0.29 | 0.76 | 4.1% | 35% | 19h | +0.23 |

### Baselines

| Baseline | Walk-forward 2020H1 to 2025H1 | Holdout |
|---|---|---|
| Buy and hold BTC | +1,389% (max drawdown 77%) | **−29.2%** (max drawdown 53%) |
| No trade | 0% | 0% |

In the bull years the strategies earned far less than buy and hold, but with roughly a tenth of the drawdown. In the falling holdout they made money while BTC lost 29%.

### Market regimes (mid cost)

| Variant | Walk-forward bull / bear / sideways, E[R] (trades) | Holdout bull / bear / sideways, E[R] (trades) |
|---|---|---|
| BB squeeze | +0.35 (226) / +0.80 (32) / +0.04 (16) | +0.21 (26) / +0.15 (23) / +0.10 (3) |
| Donchian 20 | +0.20 (382) / +0.46 (60) / +0.01 (29) | −0.05 (56) / +0.69 (39) / +0.08 (4) |
| Donchian 20 + volume | +0.28 (301) / +0.40 (51) / +0.27 (25) | −0.07 (46) / +0.84 (32) / −0.01 (3) |

Regime is labelled from the daily chart, while trades only need the 4H trend to be up. As a result, bear-regime trades are rallies inside a falling market. In the holdout, those rallies produced most of the Donchian profit.

## Robustness

- **Parameter neighbourhood** (diagnostic only, not used to choose anything): 36 settings around the defaults were tested, with Donchian length 15/20/30/40, initial stop 1.5/2.0/2.5 × ATR and trail 2/3/4 × ATR. **All 36 were positive in both walk-forward and holdout.** The result sits on a broad plateau, not a spike.
- **Tail dependence:** removing the top 5% of trades turns expectancy negative (from −0.09R to −0.22R). Those top 5% supply 100–170% of total profit. This pattern is normal for trend-following, but it means the long losing stretches in between have to be survived.
- **Significance:** walk-forward t is 2.2–2.5. Holdout t is only about 0.8, because the holdout sample is small. With 48 variants tested, about 1 would pass the walk-forward rule by chance.
- **Look-ahead and repainting:**
  - 92,105 higher-timeframe lookups all used closed candles;
  - 41,131 entries all occurred after the signal candle closed;
  - regime labels used only closed daily candles;
  - a truncation test (40 bars × 3 signals plus ATR, recomputed on history up to each bar) found 0 differences.
- **Independent verification:** a separately written pandas/numpy implementation reproduced every survivor trade exactly, with 0 mismatches across 326, 570 and 458 trades.

## Files

| Path | Contents |
|---|---|
| `src/protocol.py` | Pre-registered rules |
| `src/engine.py` | Backtest engine. Its optional parameters exist only for the neighbourhood diagnostic, and the defaults reproduce the locked run byte for byte. |
| `src/run_walkforward.py` | Stage 1. Writes `reports/walkforward_results.json` and `reports/LOCKED_pass_list.json`. |
| `src/run_holdout.py <sha256>` | Stage 2. Refuses to run if the locked list has changed. Writes `reports/holdout_results.json`. |
| `src/robustness.py` | Stage 3 diagnostics. Writes `reports/robustness.json`. |
| `src/verify_independent.py` | Independent re-implementation and repainting test |
| `src/fetch_klines.py` | Re-downloads the dataset from Binance |
| `logs/walkforward/*.csv`, `logs/holdout/*.csv` | Every trade of every variant |

### Reproducing the results

Use Python 3.13 with `pandas`, `numpy` and `ta` installed (the last two are needed for verification).

```
gunzip -k data/*.json.gz && sha256sum -c data/SHA256SUMS
python src/run_walkforward.py
python src/run_holdout.py 4a59ccd5b8be4e5dab20915f11b0e4fdbb63e928c6eeae4c9d86718c41f1dda1
python src/robustness.py
python src/verify_independent.py
```

## Recommendation

1. **Keep live trading off.** The holdout result alone is not statistically significant, and Exness costs and swaps are unverified.
2. **Forward paper-trade one variant: the Donchian 20 long breakout with 4H trend filter and trailing stop.** It was chosen for simplicity (the fewest rules), not for return. Run it for at least 6 months or 40 trades, and track it against the expected range: expectancy around +0.2R and a win rate around 33%, with losing streaks of 10 or more trades being normal.
3. **Before going live, get the real BTCUSDm specification from MT5** (spread, commission, swap, contract size and minimum lot), and re-run the tests with those costs. Swaps matter, because the average hold is about 20 hours.
4. **Do not add shorts or 15-minute entries.** Both failed clearly.
