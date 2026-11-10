# RSI + VWAP entries: pre-registered test on BTC, replicated on ETH

Paper research only. The rules, costs, benchmark and pass rule were committed in [`PROTOCOL.md`](PROTOCOL.md)
(commit `7f39b9a5`) before any result existed. Nothing in the earlier studies, the signal assistant or the frozen
Donchian forward test was changed.

## Verdict: one promising entry, not yet an edge

Of the 8 pre-registered variants, **one passed: VWAP momentum BUY with the trailing-stop exit.** The 1H close crosses
above the daily (00:00 UTC) VWAP while RSI 14 is above 50; the exit is the 2 × ATR stop with a 3 × ATR trail.
It passed on BTC and replicated on ETH. It is the best-supported entry found in this research so far, and it deserves
a forward paper test. **It does not justify live trading.**

The other 7 failed. All four RSI-reversion rules (RSI crossing back from 30 or 70 against VWAP) lost money on both
markets. VWAP momentum SELL had no edge.

## The passing variant

Primary cost 0.05% per round trip; 1R = 2 × ATR14 at entry.

| Market | Period | Trades | Win rate | Profit factor | Expectancy | 95% CI | t | Random entry | p vs random | Max drawdown |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2020-01 to 2026-11 | 1,207 | 33.0% | 1.31 | +0.167R | +0.04 to +0.30 | 2.57 | +0.104R | 0.039 | 24.6R (12.1%) |
| BTC | 2020-01 to 2025-06 | 969 | 32.7% | 1.30 | +0.166R | +0.04 to +0.30 | 2.40 | +0.120R | 0.099 | 24.6R (12.1%) |
| BTC | 2025-07 to 2026-11 | 238 | 34.0% | 1.33 | +0.171R | −0.11 to +0.57 | 0.99 | +0.042R | 0.081 | 23.7R (11.4%) |
| **ETH (replication)** | 2020-01 to 2026-11 | 1,203 | 34.1% | 1.32 | +0.170R | +0.05 to +0.29 | 2.81 | +0.108R | **0.025** | 35.2R (16.4%) |

Drawdown percentages assume 0.5% of equity risked per trade. The "random entry" column is the same exit, costs,
one-position rule and trades per quarter, with entries at random hours (2,000 runs).

### Why it is more convincing than the Donchian breakout

- **It beats matched random entry** on BTC and on ETH. The Donchian breakout did not (p about 0.25).
- **It is positive in every regime** on both markets. BTC: bull +0.14R, bear +0.20R, sideways +0.22R.
  ETH: bull +0.13R, bear +0.27R, sideways +0.03R.
- **It does not hang on a few trades.** Without its 5 best trades it still averages +0.09R on BTC and +0.10R on ETH.
  The Donchian breakout went negative without its best 10.
- **It holds up to execution.** With the measured Exness BTCUSDm spread plus 0.02% slippage it averages +0.14R, and
  +0.18R since 2024. Entering 15 minutes late still gives +0.16R.
- **Most years are positive.** On BTC, 6 of 7 years were positive (2021: −0.04R); on ETH, all 7 were.

### Why it is not yet an edge

- **The margin over random entry is small:** about +0.06R per trade. Neither BTC sub-period beats random entry on its own.
- **The entry does not predict direction.** With the symmetric exit (+1R / −1R), the same entry has no edge. The
  profit appears only with the trailing stop, which lets the occasional strong move run.
- **Significance is borderline.** The Holm-adjusted p is 0.042 against a 0.05 bar. Across the whole research
  programme, at least 80 strategy variants have now been tested. A Bonferroni correction over all of them gives p = 0.42.
- **ETH is only partly independent of BTC.** A third of ETH entries fall within an hour of a BTC entry, and
  monthly results correlate at 0.52.
- **Swaps are unverified.** The break-even is about 0.19% of price per swap-day, and 63% of trades are held over a rollover.
- **Confirming it forward takes years.** At 176 trades a year on BTC:
  - confirming the absolute +0.17R needs about 1,480 trades, roughly 8 years;
  - confirming the +0.06R margin over random entry needs about 10,400 trades.

## Recommendation

1. Treat VWAP momentum BUY as a **research candidate**, not a signal to trade.
2. If you want to pursue it, start a **separate, frozen forward paper test**. Use the sequential protocol of
   `research/donchian_validation/PROTOCOL.md`, run it on BTC and ETH, and judge it against matched random entry.
   Run it alongside the Donchian test, not as a replacement.
3. Do not adjust the RSI or VWAP settings to improve the backtest. That would undo the value of this pre-registered test.
4. Do not use VWAP momentum SELL or any RSI-reversion rule.
5. Get the Exness BTCUSDm swap and commission terms from MT5 before considering any live use.

## Files and reproducing

| Path | Contents |
|---|---|
| `PROTOCOL.md` | Pre-registered rules, committed before the results |
| `src/study.py` | Indicators, session VWAP, entry rules, trade simulation, statistics, matched random benchmark |
| `src/run_study.py` | Runs the 8 variants and applies the pass rule; writes `reports/results.json` and `reports/RESULTS.md` |
| `src/diagnostics.py` | Post-hoc checks of the passing variant (labelled as such); writes `reports/diagnostics.json` |
| `src/fetch_binance.py` | Downloads the ETHUSDT candles |
| `data/` | ETHUSDT 15m, 1H and 1D candles (gzipped) with `SHA256SUMS` |
| `reports/RESULTS.md` | All 8 variants, every period, regimes, and the pass-rule table |

```bash
# BTC data: the frozen research checkout (see research/donchian_validation/README.md)
export FROZEN_BTC_BREAKOUT=/path/to/frozen/research/btc_breakout
mkdir -p /tmp/eth && for f in data/*.gz; do gunzip -c $f > /tmp/eth/$(basename ${f%.gz}); done
(cd /tmp/eth && sha256sum -c $OLDPWD/data/SHA256SUMS)
export ETH_DATA=/tmp/eth
python src/run_study.py        # about 20 minutes
python src/diagnostics.py
python -m unittest discover -s tests -p "test_*.py"
```

All random procedures use seed 20261110.
