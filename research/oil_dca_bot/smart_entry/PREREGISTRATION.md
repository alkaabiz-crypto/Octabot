# Oil bot "smart entry" study: pre-registration

Written and committed **2026-11-11, before any result was computed.** Research only. The user's real bot is stopped, and nothing is connected to any account. The user's complaint: *"it keeps selling at the bottom when it's clearly a buy."*

## Data

- **Prices:** Exness **USOILm** bid/ask ticks, **2025-01-01 to 2026-10-31** (the user's rule: no data before 2025).
- **Indicators:** built on closed **1H** and **4H** bid candles, plus daily candles for the range filter. They become active as warm-up allows; EMA200 on 4H is ready around Feb 2025.
- **Periods:**
  - development: 2025-01 to 2025-12;
  - **holdout: 2026-01 to 2026-10.** It is used only once, with the same rules.

## Entry rules (fixed; all use indicators the user's bot app offers)

Evaluated at each closed 1H candle when no basket is open. The basket opens at the first tick after the close: BUY at ask, SELL at bid.

| ID | Entry |
|---|---|
| E0 | The user's current entry: the TradingView-style rating from `../bot.py` on 1H candles (BUY > +0.1, SELL < −0.1) |
| E1 TREND | BUY if the 4H close > EMA200(4H), otherwise SELL |
| E2 TREND+MTF | BUY if close > EMA200(4H) **and** 1H close > EMA50(1H) **and** EMA50(1H) higher than 3 bars ago. SELL is the mirror. Otherwise no trade |
| E3 PULLBACK | In a 4H uptrend (close > EMA200 4H): BUY when RSI(2) on 1H < 10. In a 4H downtrend: SELL when RSI(2) on 1H > 90 |
| E4 E0 + GUARDS | E0, but: no SELL if the price is in the lowest 20% of the last 20 daily candles' range; no BUY if it is in the top 20%; and only in the 4H EMA200 trend direction |
| E5 BREAKOUT | BUY on a 1H close above the highest close of the previous 20 hours while the 4H trend is up. SELL is the mirror |
| E6 MACD | BUY when MACD(12,26,9) on 1H crosses above its signal while the 4H trend is up. SELL is the mirror |
| CONTROL | Random direction at every closed 1H candle, 200 seeded runs per exit set |

## Exit sets (fixed, the same for every entry)

| Set | Settings |
|---|---|
| X1, user's grid | 0.01 lot, then 2 extra orders (0.02, then 0.03) 63 pips apart with ×1.3 step; TP 15 pips from the average price with 4-pip trailing; **basket stop at −50 USD** |
| X2, simple | 0.01 lot, **no extra orders**, TP 100 pips with 4-pip trailing, **stop 100 pips** (1.00 USD of price, −10 USD) |

- **Units:** 1 pip = 0.01 USD; 1 lot = 1,000 barrels.
- **Costs:** real bid/ask. Swap is 0 (Exness lists USOIL as swap-free by default; unverified for this account). A **2× spread** stress run is included.

## Measures

For each entry and exit set, in each period:
- net USD, max drawdown, basket count and win rate;
- **"bad entries":**
  - the share of SELLs opened in the lowest 20% of the 20-day range, and of BUYs in the top 20%;
  - the share of entries against the 4H EMA200 trend.

## Pass (all required, judged on the HOLDOUT for each entry and exit pair)

1. net > 0 in the development period **and** in the holdout, at 1× and 2× spread;
2. holdout net above the 90th percentile of the random control with the same exit set;
3. holdout max drawdown below 15% of the 10,000 AED paper account, i.e. below 408 USD;
4. at least 30 baskets in the holdout.

- **A pass** means "worth a forward paper/demo test", **never** live money.
- **If nothing passes**, the answer is that no entry rule tested here fixes the bot. The report will then explain what the data shows about why.
