# Can scheduled news be traded? 14 markets

Can the big scheduled US releases be traded profitably on Exness, or do they mainly matter for risk? The releases are FOMC decisions, CPI, the jobs report (NFP) and, for oil, the weekly EIA inventory report.

Five rules were tested on each:
- follow the first 15 minutes;
- fade the first 15 minutes;
- follow the first 30 minutes;
- trade the break of the release candle;
- buy 24 hours before the release (the "pre-FOMC drift" known from US stocks).

All were tested on 14 markets: US and Brent oil, BTC, ETH, the S&P 500, Nasdaq, Dow, DAX, EUR/USD, USD/JPY, GBP/USD, USD/CAD, gold and silver. Each rule was compared with the same rule at the same clock time on normal days. It was fitted on data up to 2024 and judged on 2025-01 to now. The rules were written down first in [PROTOCOL.md](PROTOCOL.md); the tables are in [reports/RESULTS.md](reports/RESULTS.md).

## Result

**Nothing was confirmed: 0 of 225 combinations.** Fifteen passed the fit period, which is about what luck produces (11 expected). In 2025–26 most of them did nothing, or did the opposite.

- **BTC after FOMC.** Following the first 15 minutes looked like the best rule in the whole study: 61% wins, +0.51R per trade and z +5.6 in 2020–24. In 2025–26 it won 27% of trades and lost 0.38R per trade (z −2.8). The breakout rule on BTC flipped the same way. Patterns like this exist for a while, get traded away, and then reverse.
- **Silver after CPI** (follow the first 15 minutes) was the only fit passer that also did well in 2025–26: +0.33R on 22 releases, p 0.018. Across 15 candidates that is not enough to rule out luck. It is a lead, not a signal.
- **Oil after the EIA report.** None of the rules worked. Fading the first 15 minutes lost money in 2020–24, then made a little in 2025–26. That fits the research showing that the inventory reaction partly reverses within hours. The effect was too small and unstable to trade after spread.
- **The pre-FOMC drift** did not show up in Exness index CFDs: buying the S&P 500, Nasdaq or Dow 24 hours before FOMC did not beat normal days.

## Where news matters for risk

This is how much more each market moves in the 4 hours after the release than at the same time on a normal day:

- **FOMC** is the biggest risk event almost everywhere:
  - gold ×7, USD/JPY ×7, EUR/USD and GBP/USD ×6;
  - silver ×5, USD/CAD ×4;
  - US indices ×2.5 to ×3, BTC ×2.5.
- **CPI and NFP** roughly double the move in forex, metals, ETH and the indices.
- **US oil hardly reacts** to FOMC, CPI or NFP (×1.0 to ×1.3). Its own news is the EIA report (×1.3).
- **BTC ignores NFP** (×1.0) but reacts to FOMC and CPI.

So closing before news protects you most in gold, silver and forex at FOMC. It matters least in oil.

## Notes

- **Low power.** About 15 to 22 releases per type fall in 2025–26, so only large effects could be confirmed. "Not confirmed" means no evidence, not proof of nothing.
- **EIA dates.** 2025–26 uses EIA's published schedule. 2020–24 uses EIA's standard rule; 45 rule dates without a price reaction were dropped as likely moved releases.
- **Brent.** Exness Brent closes around 22:00 UTC, so it has too few FOMC releases with 4 hours of trading after them.
