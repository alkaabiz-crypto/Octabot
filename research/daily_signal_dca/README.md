# Daily signal DCA bot (spot, 1x): results

Research only: backtest, no orders. The rules, signals and pass/fail test were fixed in `PREREGISTRATION.md` (commit `79267e2f`) before any result was computed. Nothing was tuned.

## Verdict: the primary signal PASSED its pre-registered test

**Primary signal TREND_ENS:** each day, hold 25% of the pot in the coin for each of SMA20, SMA50, SMA100 and SMA200 that the daily close is above. The rest is held in USDT. Fee 0.1% per side; trades at the next day's open.

| Lump sum, 0.1% fee | Sharpe early (2018–21) | Max drop early | Sharpe late (2022–26) | Max drop late | Return late |
|---|---|---|---|---|---|
| **BTC TREND_ENS** | **1.14** | **−47.5%** | **0.76** | **−32.1%** | **+143%** |
| BTC buy and hold | 0.79 | −81.2% | 0.46 | −66.9% | +67% |
| **ETH TREND_ENS** | 1.28 | −50.7% | **0.55** | **−36.9%** | **+93%** |
| ETH buy and hold | 0.92 | −94.0% | 0.19 | −74.0% | −39% |

All three pre-registered checks passed: BTC early, BTC late, ETH late. **In full (2018-01 to 2026-10), BTC TREND_ENS gave a CAGR of +34.1% with a −52.3% max drop, against +21.6% and −81.2% for buy and hold.** At 0.2% fees: +31.4%.

## DCA version (10 USD added every day; the signal decides coin or cash)

| Late period 2022-01 to 2026-10 (17,640 USD put in) | Final value | Profit | Worst point vs money put in |
|---|---|---|---|
| **BTC: plain daily DCA (never sell)** | 32,025 | +81.6% | **−48.5%** |
| **BTC: TREND_ENS DCA** | 32,012 | +81.5% | **−18.3%** |
| ETH: plain daily DCA | 18,208 | +3.2% | −60.3% |
| **ETH: TREND_ENS DCA** | 29,440 | **+66.9%** | −16.7% |

On BTC in the late period, the signal gave **the same profit as plain DCA, with less than half the worst drop**. On ETH it turned a flat result into +67%.

## All signals (lump sum, 0.1% fee, Sharpe early / late)

| Signal | BTC | ETH | Note |
|---|---|---|---|
| **TREND_ENS (4-SMA ensemble)** | 1.14 / 0.76 | 1.28 / 0.55 | primary; passes |
| TREND_ENS + vol targeting | 1.27 / 0.80 | 1.55 / 0.58 | smallest drops (BTC −29% late) but about 3× more trades |
| SMA50 only | 1.36 / 0.75 | 1.21 / 0.76 | late max drop −51% (BTC) |
| SMA200 only | 0.65 / 0.90 | 0.93 / 0.51 | few trades, slow to react |
| MAX10 (Quantpedia breakout) | 0.64 / 0.58 | 1.31 / 0.46 | weaker |
| MOM1 (follow yesterday) | −0.54 / −0.14 | 0.01 / −0.45 | **loses heavily:** fees and noise |
| REV_RSI2 (buy dips) | 0.28 / −0.02 | 0.04 / 0.17 | about zero |
| HOUR 21–23 UTC (2 h a day) | 0.1% fee: **−94% late** | −92% late | dead after fees; at 0.02% maker fees, Sharpe falls from 1.1 (early) to 0.15 (late), so the effect has faded |
| Buy and hold | 0.79 / 0.46 | 0.92 / 0.19 | benchmark |

**The edge comes from being in cash during the big bear markets** (2018, 2022), not from predicting the next day. On average the bot holds the coin about 52% of the time, so in strong bull runs it lags buy and hold. Fast daily signals (MOM1, RSI2, the hour-of-day effect) **lose money after fees.**

## Checks

- **Independent recalculation:** a vectorised recomputation reproduces the engine exactly (BTC total +1,236.59%, max drop −52.34%).
- **No look-ahead:** adding one extra day of delay gives a similar result (+1,315%). The edge does not depend on same-day information.
- **Data:** Binance BTCUSDT and ETHUSDT daily candles, 2017-08-17 to 2026-10-31, with no gaps. Stored in `data/` together with the hourly data.
- **Limits:**
  - Backtest only. Two coins, one exchange, about 9 years containing 2–3 boom-and-bust cycles.
  - Fees are modelled, but slippage on large orders is not.
  - Trend rules can lose in long sideways chop, and will lag in strong bull years.

## The bot rule, as it would be configured

- **When:** once a day, after the 00:00 UTC daily close.
- **Signal:** count how many of SMA20, SMA50, SMA100 and SMA200 (daily closes) the BTC close is above.
- **Position:** target coin share = count × 25%; the rest is held in USDT. Trade only the difference, at market (0.1% fee). That works out to a change roughly every 5 days on average.
- **DCA option:** add a fixed amount every day, and apply the same target share to the whole pot.
- **No leverage, no shorting, spot only.**

**Next step (pre-registered consequence of the pass):** a forward paper test, before any real money.
