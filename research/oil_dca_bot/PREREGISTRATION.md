# User's USOIL DCA bot (#16): rebuild and one-year backtest: pre-registration

Written and committed **2026-11-10, before any result was computed.** Research only. The real bot and account are never touched, and no orders are placed.

## Bot settings (from the user's "Bot details" screenshot) and how they are modelled

| Setting | Value | Model (checked against the user's real trades where possible) |
|---|---|---|
| Initial order | 0.01 lot | 0.01 lot at market (SELL at bid, BUY at ask) |
| Extra orders | 2, first 0.02 lot, multiplier 1.5 | 0.02 lot, then 0.03 lot. Matches the real trades (0.01, 0.02, 0.03). |
| Extra order step | 63 pips, step multiplier 1.3 | 1 pip = 0.01 USD. Extra order 1 is 0.63 against the first fill; extra order 2 is a further 0.819. Matches the real trades: 83.072 → 83.702 → 84.522. |
| Take profit | 15 pips + trailing 4 pips | Measured from the **volume-weighted average** price of the basket. Trailing starts once price is 0.15 in profit; the whole basket closes when price pulls back 0.04 from its best level. Matches the real single-order wins (+0.105 to +0.185). |
| Stop loss | Off | None (variant V0) |
| Contract | | 1 lot = 1,000 barrels: 0.01 lot = 10 USD per 1.00 move. Matches the real P&L: 0.02 lot × 1.152 = 23.04 USD. |
| Entry condition | TradingView "Indicators Summary" (26 indicators) | **Approximated** (TradingView's exact code is not public): the TradingView Technical Rating, with 15 moving-average and 11 oscillator votes and TradingView's documented rules, simplified where noted in `bot.py`. A new basket opens at the close of a 15-minute candle when the rating is Buy (> +0.1) or Sell (< −0.1) and no basket is open. |
| Smart Protection (news) | On | **Not modelled:** there is no historical news calendar here. Noted as a limitation. |

**Costs:** real Exness bid/ask ticks (spread included). Commission is 0 and swap is 0, as shown on the user's real trades. Swap may not always be 0 overnight; this is noted.

**Data:** Exness **USOILm** ticks 2025-11 to 2026-10 from `ticks.ex2archive.com`, with SHA-256 values recorded.

## Variants (fixed now, not tuned)

- **V0 as configured:** no stop loss. A basket stays open until it hits TP. Reported: realised P&L, **largest floating loss**, longest time stuck, and any basket still open at the end (marked to market).
- **V1 = V0 + basket stop at −50 USD.** That is about the size of the real loss on 2026-11-10 (−50.76), which is what manual closing effectively did.
- **V2 = V1 + trend filter:** only open a basket in the direction of the closed 4-hour EMA200 (BUY above it, SELL below). This targets the user's stated problem: "keeps selling when it goes up".
- **Benchmark:** V1 with a **random** entry direction, 500 seeded runs. This shows how much the entry signal matters at all.

## What would count as an improvement

- Any variant is judged on net USD over the year, max drawdown in USD (closed plus floating), and the worst single basket.
- V2 is "better" only if net USD is higher **and** max drawdown is no worse than V1.
- None of this justifies more leverage or live changes. It only informs settings to try on a **demo** account first.
