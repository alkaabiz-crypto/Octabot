# Oil bot: which single app entry condition is best? Pre-registration

Written and committed **2026-11-11, before any result was computed.** Research only.

The user's bot app (screenshot 11:38 UAE) allows **one** entry condition: Indicators Summary, EMA, SMA, Bollinger Bands, Ultimate Oscillator, ADX, RSI, CCI, Stochastic, MACD, Parabolic SAR or MFI. TradingView Signal is locked. The app's exact parameters per condition are unknown, so each is modelled with its **standard default settings and TradingView's buy/sell rules**.

## Data and periods

Same as `../smart_entry`: Exness USOILm ticks, development **2025**, holdout **Jan–Oct 2026**, real spread plus a 2× stress run, swap 0.

## Conditions (each on closed **1H** and on closed **4H** candles)

| Condition | BUY | SELL |
|---|---|---|
| Indicators Summary | rating > +0.1 (`../bot.py` approximation) | rating < −0.1 |
| EMA(200) | close > EMA200 | close < EMA200 |
| SMA(200) | close > SMA200 | close < SMA200 |
| Bollinger Bands(20, 2) | close < lower band | close > upper band |
| Ultimate Oscillator(7, 14, 28) | UO < 30 | UO > 70 |
| ADX(14) | ADX > 20 and +DI > −DI | ADX > 20 and −DI > +DI |
| RSI(14) | RSI < 30 | RSI > 70 |
| CCI(20) | CCI < −100 | CCI > 100 |
| Stochastic(14, 3, 3) | %K < 20 and %K > %D | %K > 80 and %K < %D |
| MACD(12, 26, 9) | MACD > signal | MACD < signal |
| Parabolic SAR(0.02, 0.2) | close > SAR | close < SAR |
| MFI(14) | MFI < 20 | MFI > 80 |

- **Basket opening:** a new basket opens at the next closed 1H candle when the condition, read at its latest closed value on the chosen timeframe, gives a direction and no basket is open.
- **Volume:** tick count is used as volume for MFI.

## Exit sets

- **X1:** the user's current grid. Extra orders 0.02 then 0.03, step 63 pips ×1.3, TP 15 pips + 4 trailing, **basket stop at −50 USD**. With the stop off, the earlier study showed one basket stuck for 281 days.
- **X2:** simple. No extra orders, TP 100 pips + 4 trailing, stop 100 pips.

## Pass (same as `../smart_entry`)

All required for a condition and exit pair:
1. net > 0 in the development period and in the holdout, at 1× and 2× spread;
2. holdout net above the 90th percentile of random direction with the same exit set (reused from `../smart_entry/results/results.json`: X1 −808.61, X2 +208.72);
3. holdout max drawdown < 408 USD;
4. at least 30 holdout baskets.

## Ranking and caveats

- **Ranking among the rest:** holdout net at 2× spread, then the lowest share of "sells at the bottom".
- **Luck warning:** with 48 combinations, about 2–5 could pass by luck. A pass leads only to a **demo** test.
