# Does the news itself tell which market will rise?

This study asks whether the content of the jobs report (NFP) and CPI, meaning whether the number came in "hot" or "cool", tells which way each market will move, and whether a trader can profit from that.

Sections 1–3 measure the surprise against the data's own recent trend, using the numbers **as first published that morning** (ALFRED vintages from the St. Louis Fed).
- **CPI:** the core monthly change against its previous 6-month average.
- **NFP:** the payroll change against its previous 3-month average, adjusted for the change in unemployment.

The rules are in [PROTOCOL.md](PROTOCOL.md) (written before the results); the numbers are in `reports/`.

## 1. Yes, the surprise tells the direction of the first move

From 2025-01 to now, the first 15 minutes after the jobs report moved the way the surprise pointed in:

| Market | Strong jobs report means | First 15 minutes agreed |
|---|---|---|
| EUR/USD | down | 82% |
| GBP/USD | down | 82% |
| Gold | down | 81% |
| USD/JPY | up | 77% |
| BTC | down | 77% |
| USD/CAD | up | 68% |
| ETH | down | 68% |

CPI is weaker: 50–68% agreement. The surprise measured against trend is a rough stand-in for the real consensus surprise.

## 2. But the move is over within seconds

Exness tick data, which records every bid and ask quote, shows how fast the move happens. For EUR/USD after NFP:
- by 1 second after 08:30:00, about 1% of the 15-minute move had happened;
- by 2 seconds, 59%;
- by 5 seconds, 85%.

For gold it was 1%, 33% and 42% at 1, 2 and 5 seconds.

Trading in the textbook direction, on the actual number, at real Exness bid/ask, and holding for 15 minutes:

| Entry after the release | EUR/USD NFP | GBP/USD NFP | USD/JPY NFP | Gold NFP |
|---|---|---|---|---|
| 1 second | +1.06R, 82% wins | +0.87R, 77% | +0.86R, 73% | +0.77R, 81% |
| 5 seconds | +0.05R, 36% | −0.02R, 36% | +0.06R, 41% | +0.30R, 62% |
| 30 seconds | +0.08R | +0.10R | +0.06R | +0.21R |
| 3 minutes | +0.14R | +0.13R | +0.09R | +0.16R |
| 15 minutes, held 1 h | −0.13R | −0.06R | 0.00R | −0.16R |

R is 2 × ATR14 (about 1 hour of normal movement). There are 21–22 releases per market. For CPI, every entry from 5 seconds on lost money in all four markets.

So the information is valuable only within **about 1 second**. That would mean having the number and an order filled before Exness's price updates. Professional firms do this with direct data feeds and co-located servers. A retail trader reading the headline is several seconds too late, and brokers widen spreads, requote or reject orders at release time. Exness's terms also forbid trading that exploits price delays.

Gold shows a small leftover drift for a few minutes after the jobs report: +0.16R to +0.30R for entries between 5 seconds and 3 minutes, held 15 minutes. That is 21 releases inside a test of many delays, so it is a lead, not a signal, and real fills at that moment would be worse than the tick quotes.

## 3. Trading the 4 hours after the first 15 minutes does not work

Entering 15 minutes after the release in the surprise direction, for 4 hours with a 2 × ATR stop, was tested on 14 markets. The direction was learned in 2020–24 and tested on 2025–26. **0 of 56 combinations were confirmed.** Five forex combinations looked good in 2020–24. For example, after hot CPI, buy USD/CAD: +0.57R per trade, p 0.004. All five faded in 2025–26.

## 4. Repeated with the real consensus forecasts

A free source of historical consensus forecasts turned up: a public Hugging Face dataset copied from the Investing.com calendar. It covers NFP, the unemployment rate and core CPI from 2020-02 to 2026-06. All tests were rerun with the true surprise, actual minus forecast. The conclusion did not change.

- **Direction is even clearer in the first second.** After CPI, EUR/USD went the surprise's way in 92% of releases (12 releases), and USD/JPY in 83%. After NFP the figures were 71–82%.
- **From 5 seconds on it is gone in forex.** EUR/USD, GBP/USD and USD/JPY CPI entries at 5 to 30 seconds lost about 0.2–0.3R per trade.
- **The 4-hour strategy: 0 of 56 confirmed** with the real surprise as well.
- **The one lead was dropped.** Gold kept drifting in the surprise direction for a few minutes after NFP in 2025–26: +0.24R for an entry 30 seconds after the release, held 15 minutes. It was checked on 56 earlier releases (2020-03 to 2024-12) that had never been looked at. It gave −0.01R (p 0.31) for the 30-second entry and −0.02R for the 3-minute entry. It worked in 2021–2023 and failed in 2020 and 2024.

## What the daily briefing now does

Since 2026-11-12, the briefing logs the market's consensus forecast for every high-impact US release in `data/consensus_log.csv`. Over time this builds the real forecast history that no free source offers. Later studies can then measure the true surprise rather than the trend proxy used here.
