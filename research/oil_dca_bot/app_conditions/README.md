# Oil bot: which single app entry condition is best? Results

The rules were fixed in `PREREGISTRATION.md` (commit `bfe90be9`) before running. Exness USOILm ticks, development **2025**, holdout **Jan–Oct 2026**. That is 24 conditions (12 indicators × 1H/4H) × 2 exit sets = 48 combinations.

## Verdict

**None passed the full pre-registered test.** Three were positive in **both** periods at **1× and 2× spread** with small drawdowns. They failed only because they did not beat the 90th percentile of random-direction results (+208.72 USD) in the holdout. **All three are the same idea: on the 4H chart, buy when oversold and sell when overbought, with simple exits.**

| Condition (4H) + simple exits (no extra orders, TP 100, SL 100) | 2025 net (1× / 2×) | 2026 net (1× / 2×) | Max drop | Win rate | Baskets 2025 / 2026 |
|---|---|---|---|---|---|
| **Stochastic(14,3,3)**: BUY %K<20 & %K>%D, SELL %K>80 & %K<%D | **+207 / +182** | **+162 / +90** | **58 / 79 USD** | 59% / 55% | 117 / 200 |
| MFI(14): BUY <20, SELL >80 | +20 / +41 | +198 / +149 | 71 / 89 | 52% / 58% | 66 / 103 |
| Bollinger(20,2): BUY below lower band, SELL above upper | +86 / +94 | +62 / +19 | 70 / 166 | 54% / 52% | 109 / 198 |
| RSI(14): BUY <30, SELL >70 | −44 / −38 | +246 / +209 | 102 / 107 | 48% / 58% | 85 / 178 |
| Indicators Summary (the user's current, 1H) + simple exits | −27 / −92 | −327 / −710 | 175 / 411 | 50% / 48% | 308 / 1,102 |
| Indicators Summary (1H) + **user's grid** | −244 / −588 | −1,564 / −2,634 | 547 / 1,763 | 95% / 94% | 1,159 / 2,538 |

All amounts are USD for a 0.01-lot base position.

## What this means

- **The user's intuition is right in one way.** The trend and summary indicators (Indicators Summary, EMA, SMA, MACD, Parabolic SAR, ADX) chase moves and often sell after a drop: 25–55% of their sells came in the bottom 20% of the 20-day range. All of them lost in the 2026 holdout.
- **The oscillator family works better on oil in 2025–26.** On the 4H chart, these sell into rallies and buy into dips. Their sells at the bottom: about **0%**.
- **Your grid exits lose with every condition.** Averaging plus a 15-pip target gives a 95% win rate and a net loss.
- **Luck warning:** 3 of 48 combinations positive in both periods could partly be luck. But all three are the same mean-reversion idea on 4H, which makes a real but modest effect more plausible. It is not proven: it failed the random-control bar.

## Recommended settings for a DEMO test only

| Setting | Value |
|---|---|
| Entry condition | **Stochastic**, **4H** timeframe, %K 14, %D 3, smoothing 3, levels 20/80 (if the app lets you choose them) |
| Initial order | 0.01 lot |
| Extra orders | **0** |
| Take profit | **100 pips**, trailing TP 4 pips |
| Stop loss | **ON, 100 pips** |
| Smart Protection | On, as now |

Judge it after **about 100 trades**. The backtest equivalent was roughly **+90 to +200 USD per 10 months per 0.01 lot**, with a max drop under 100 USD. Expect less live.

Files: `study.py`, `results/results.json` (all 48 combinations).
