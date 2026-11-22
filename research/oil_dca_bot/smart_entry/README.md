# Oil bot "smart entry" study: results

The rules were fixed in `PREREGISTRATION.md` (commit `93be5a65`) before running. Exness USOILm ticks, development period **2025**, holdout **Jan–Oct 2026**. Real spread (also at 2×), swap 0.

## Verdict: FAIL, no entry rule fixes the bot

All 14 combinations of entry rule and exit set failed the pre-registered test. The best was **E4** (the user's rating plus "no selling at the bottom / no buying at the top / only with the 4H trend") with the **simple exits** (no extra orders, TP 100 pips, stop 100 pips):
- holdout: **+208 USD** (+17 at 2× spread), max drawdown 219 USD;
- development: −54 USD.

It fails because the development period lost money.

## What the data shows (holdout, 1× spread)

| Entry | User's grid exits (X1) | Simple exits (X2) | Sells at the bottom* | Against the 4H trend |
|---|---|---|---|---|
| E0, user's current rating | −1,564 | −327 | 30% | 33% |
| E1, trend only | −2,199 | +42 | 53% | 0% |
| E2, trend, 2 timeframes | −1,454 | +58 | 64% | 0% |
| E3, buy dips / sell rallies in trend | −318 | −10 | 36% | 0% |
| **E4, rating + bottom/top/trend guards** | −958 | **+208** | **0%** | **0%** |
| E5, breakout in trend | −950 | −50 | 70% | 0% |
| E6, MACD in trend | −314 | −47 | 62% | 0% |
| Random direction (median of 200) | −1,438 | −138 | — | — |

\* Share of SELLs opened in the lowest 20% of the last 20 days' range.

1. **The grid exits lose with every entry.** That includes random entries (median −1,438). A 15-pip target with averaging-down against the move loses more each time price trends, whichever direction the bot started in. **The exits are the main problem, not the entry.**
2. **"Not selling at the bottom" isn't enough on its own.** The guards cut bottom-selling and against-trend trades to 0%, and that is the best combination. But sticking to the trend means selling near recent lows during downtrends (53–70% for the trend rules). That is normal for trend-following, and on its own it doesn't produce profit.
3. **No entry predicts oil's next 1–2% move.** With the simple 1:1 exits, every entry wins about 48–53% of the time. That is coin-flip territory, and the spread turns it into a small loss.
4. **The guards stop the specific mistake the user saw.** The guarded rating with simple exits was the least-bad combination, but it isn't proven profitable.

## Recommendation

- Keep the real bot off. No rule here earns real money.
- **If the user wants to keep experimenting, on a demo account only:**
  - entry: Indicators Summary plus the three guards (no SELL in the bottom 20% of the 20-day range, no BUY in the top 20%, trade only with the 4H EMA200 trend);
  - **no extra orders**;
  - TP 100 pips with 4-pip trailing;
  - **stop loss ON at 100 pips**.

  Judge it after 100+ trades. Expect roughly break-even.
- The money-making tests are elsewhere: the gold momentum rule and the BTC/ETH trend bot, both on paper.

Files: `study.py`, `results/results.json`.
