# Trend breadth test: results

The rules were fixed in `PREREGISTRATION.md` (commit `72a4a0fd`) before any coin data was downloaded.
- **Coins:** 18 Binance coins, daily candles from 2025-01-01 to 2026-11-11 (680 days each). None was dropped.
- **Rule:** the frozen TREND_ENS rule, with a 0.1% fee.

## Verdict: FAIL, and clearly

| | TREND_ENS (primary) | SMA50 (information only) |
|---|---|---|
| Mean Sharpe across 18 coins | **−0.58** | −0.28 |
| Random timing with the same exposure: median / 95th pct | −0.32 / −0.13 | −0.29 / −0.08 |
| Rule percentile against random timing | **0.8** | 51.4 |
| Median per-coin percentile | 38 | 50 |
| Coins where it beat buy and hold | 16 of 18 | 16 of 18 |
| Coins where its max drop was smaller | 17 of 18 | 18 of 18 |
| Average return (buy and hold) | −38.6% (−58.5%) | −27.3% (−58.5%) |

## What this means

- **On coins it was never tuned on, TREND_ENS's timing was worse than random**, at the 0.8th percentile.
  - In the 2025–26 alt-coin bear market it kept buying after bounces and selling after drops. That pattern is called whipsaw.
  - SMA50 timing was exactly at chance.
- **It still "beat buy and hold" on 16 of 18 coins, but only because it was out of the market 55–75% of the time while those coins fell 50–90%.**
  - Any rule that holds less coin does that in a falling market.
  - It is not skill.
- **This changes the picture for the trend bot.** Its BTC/ETH result (89–94th percentile) does not carry over to other coins. Taken together, the evidence that its *timing* adds value in 2025–26 is **weak**. What it reliably does is **cut exposure and therefore drops**.
- **The forward paper test keeps running unchanged,** since its rules are frozen. It should be read as a risk-reduction tool, not a profit engine.
- **For real money,** plain DCA with no leverage remains the honest default. Holding less (for example 50% of the money you'd invest) cuts drops just as reliably as the trend rule did here, with no timing risk.

Files: `study.py`, `results/results.json`, `data/` (Binance daily candles from 2025-01-01).
