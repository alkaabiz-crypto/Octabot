# User's USOIL DCA bot (#16): rebuild and one-year Exness tick backtest

Research only. The real bot and account were never touched, and no orders were placed. The rules and variants were fixed in `PREREGISTRATION.md` (commit `708a9a5e`) before any result was computed.

## Verdict: the bot loses money over a full year, in every variant

| Variant (2025-11 to 2026-10, real Exness USOILm bid/ask) | Baskets | Win rate | Avg win | Avg loss | **Net USD** | Max drawdown USD | Worst basket |
|---|---|---|---|---|---|---|---|
| **V0 as configured (stop loss off)** | 107 | 99% | +2.64 | — | **−2,242** (one basket still open) | **3,204** | stuck **281 days**, −2,522 at year end |
| **V1 + basket stop at −50 USD** | 5,187 | 94.5% | +2.35 | −51.08 | **−2,915** | 2,963 | −168.84 (weekend gap) |
| **V2 = V1 + 4H EMA200 trend filter** | 3,952 | 94.7% | +2.26 | −51.50 | **−2,417** | 2,772 | −168.84 (weekend gap) |
| Random BUY/SELL + V1 stop (500 runs) | | | | | median −3,072 (5th–95th: −4,271 to −1,780) | median 3,413 | |

## What this shows

1. **With the stop loss off, one trend traps the bot.**
   - A SELL basket opened on **2026-01-22** filled all 3 orders (0.06 lots) as oil rose.
   - It **never** reached its take profit for the rest of the year.
   - Its floating loss reached **−3,204 USD**, while all the small wins before it added up to only +280 USD.
   - This is exactly the "keeps selling while price goes up" problem.
2. **Closing big losses at −50 (V1) stops the account blowing up, but the maths doesn't work.**
   - An average win of +2.35 against an average loss of −51 needs a **95.6% win rate** just to break even.
   - The bot achieved **94.5%**.
   - The user's real record, about 3,200 USD profit against 3,150 USD losses, fits this break-even-or-worse profile.
3. **The trend filter (V2) helps, but doesn't fix it.**
   - It meets the pre-registered "better" test: net −2,417 vs −2,915, with a smaller drawdown.
   - It is still a clear loser.
4. **The entry signal adds almost nothing.** V1 sits at the 59th percentile of random-direction runs. The result comes from the averaging-and-tiny-target structure, not from the indicators.
5. **Some months are good:** V1 was positive in Feb, Jun, Jul and Aug, which explains strong-looking runs like the user's recent weeks. The big losing months, Mar–Apr (−1,856) and Sep–Oct (−1,060), were oil trend periods.

## Model fidelity and limits

- **Matches the real bot:**
  - order sizes 0.01, 0.02 and 0.03;
  - steps of 0.63, then 0.819, exactly as in the user's trades;
  - TP and trailing size, consistent with the real wins of +0.105 to +0.185;
  - 1 lot = 1,000 barrels (0.02 lot × 1.152 = 23.04 USD, as on the real trade).
- **Approximated:** the TradingView "Indicators Summary" entry. It is rebuilt from TradingView's published 26-indicator rating rules, simplified in places, on 15-minute candles; the real bot's timeframe is unknown. The model opens about 20 baskets a day, against roughly 7 a day for the real bot. Because random entries do about as well, this approximation is unlikely to change the conclusion.
- **Not modelled:** Smart Protection (news pauses) and the 30-minute no-trade window, for lack of a historical news calendar. Swap is taken as 0, as on the real trades; it may not always be 0 overnight.
- **Data:** 37.5M Exness USOILm ticks (2025-09 to 2026-10; the first two months are used only for indicator warm-up). 0 ticks with ask < bid. Median spread is 0.018–0.02; SHA-256 values are in `results/results.json`.
- **Weekend gaps:** a −50 stop can fill much worse after a weekend gap. The worst was −168.84 on 2026-04-19, and 5 stops were worse than −60.

## Files

- `bot.py`: the rebuild and backtest.
- `results/results.json`: all statistics, monthly P&L and data checks.
- `results/*_baskets.csv`: every simulated basket per variant.

```
TICK_DIR=<dir with Exness_USOILm zips> CACHE_DIR=<scratch> python3 -I bot.py
```
