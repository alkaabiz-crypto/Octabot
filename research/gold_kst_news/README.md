# Gold KST + session VWAP: exits, news and entry ideas

Can the best gold signal from the earlier rounds be improved? That signal is a 1-hour KST bullish cross while price is above the session VWAP, held until the bearish cross. This study tried better exits, news rules and entry filters. The rules were written down first ([PROTOCOL.md](PROTOCOL.md) and [IDEAS.md](IDEAS.md)). Everything was fitted on 2020-07 to 2024-12 and then judged on 2025-01 to now, against random entries that use the same exits and costs. The tables are in [reports/RESULTS.md](reports/RESULTS.md); the raw numbers are in `reports/*.json`.

## Exits (1,152 combinations)

The study tried hard stops, trailing stops, breakeven, time stops, "leave if still losing after N hours" and four news rules, in every combination. **No option clearly helped.** Averaged over everything else, each option moved the results by less than the noise.

The pre-registered pick, the combination with the best 2020–24 edge over random, was the original rule plus a **48-hour time stop**. On 2025 to now it narrowly met its bar: z 1.65 against a required 1.645, and a worst drawdown of 8R against 9R. It still made less money than the original rule (+71R against +89R). In practice the original "hold to the opposite cross" exit is as good as anything tried.

Two facts put the profit in context. In 2020–24 the signal was only slightly better than random at normal cost, and about break-even at stress cost. Most of its 2025–26 profit came from gold's strong uptrend, which random BUY entries also captured.

## News

The FOMC, CPI and NFP release dates are the official ones: the Federal Reserve for FOMC, and ALFRED vintage dates for CPI and NFP.

- **Avoiding news.** No entry around news, closing before news, and no entry in the 24 hours before news all made no reliable difference.
- **Direction from news.** Following or fading gold's first 15 minutes after the release, held for 4 hours, looked strong for FOMC in 2020–24 (z 4.6 on 36 meetings). It vanished in 2025–26 (z 0.2 on 15). CPI and NFP showed nothing either way. **The news does not tell you whether gold will rise or fall.**
- **Size.** In the 4 hours after the release, gold moves about 2.9× ATR after FOMC (against 0.5× at the same time on normal days), 2.4× after NFP (against 1.2×) and 1.5× after CPI (against 1.1×). That is useful for sizing and stop placement, not for direction.
- **Stand-alone event trades.** Holding gold through the 24 hours before FOMC, CPI or NFP, or through the Asian session (the overnight effect reported in the literature), lost money or was flat after costs.

## Entry filters (round 2)

The study tested 15 filters on their own: sessions, KST position relative to zero, 4-hour KST, daily EMA50, volatility regime, distance from VWAP, weekday, falling real yields and a falling dollar. Ten passed in 2020–24, but **none survived 2025–26** after the multiple-testing correction.

The nearest misses were "dollar index falling over the last 5 days" (test +0.52R per trade, p 0.04) and "volatility below its median" (+0.52R, p 0.06). Both are now recorded as shadow tracks in the paper test. Entries in the Asian session lost money in 2020–24 but were the best of all in 2025–26. That flip is a warning about how unstable these patterns are.

## Do the near misses work elsewhere? (part C)

The two near misses were checked on markets that played no part in choosing them, from 2023-07 to now. **Neither carried over.**

- **Silver.** The dollar filter halved the number of trades and nearly doubled the profit per trade (+0.18R against +0.10R). It also cut the worst drawdown from 47R to 13R. But it did not beat random entries convincingly (p 0.13).
- **EUR/USD.** The KST signal loses money with or without the filters, because of spread.

## What happens next

The frozen paper test in [../gold_kst_paper](../gold_kst_paper) records the signal on new data from 2026-11-12. A daily briefing lists the coming high-impact events and their usual move size.
