# Oil DCA bot: wide optimisation with walk-forward validation: pre-registration

Written and committed **2026-11-10, before any result was computed.** Research only. Same data and execution model as `../bot.py`: Exness USOILm bid/ask ticks 2025-11 to 2026-10; commission and swap 0; 1 lot = 1,000 barrels.

## Search space (settings the user's bot app offers)

| Setting | Values |
|---|---|
| Take profit (pips) | 15, 30, 60, 100, 150 |
| Trailing TP (pips) | 0 (plain take profit), 4 |
| Extra orders | 0, 1, 2, 3 |
| Extra order size | 0.02 lot; amount multiplier 1.0 or 1.5 (lots rounded down to 0.01) |
| Extra order step (pips) | 63, 100, 150, 250; step multiplier 1.3 |
| Basket stop (USD) | 25, 50, 100, 200 |
| Entry direction | Indicators Summary rating; rating + 4H EMA200 trend filter; trend only (4H EMA200 side); faded rating (opposite); always BUY; always SELL |
| Entry timeframe | 15m, 1h. Always BUY / always SELL use 15m only, because the timeframe makes no difference to them. |

- Extra-order combinations: 1 with 0 extras, 4 steps with 1 extra, and 4 steps × 2 multipliers for each of 2 and 3 extras: 21 in total.
- Total: 5 × 2 × 21 × 4 × (4 direction modes × 2 timeframes + 2 always-modes) = **8,400 settings.**
- Each setting runs once over the whole year. Every basket is assigned to the month it closed in.

## Validation (the only result that counts)

**Walk-forward, monthly:**
- For each test month from Feb to Oct 2026 (9 months), choose the setting with the best train score on the **previous 3 months** only.
- Train score = net USD / max drawdown USD, with at least 30 baskets required. A tie is broken by net USD.
- That setting's P&L in the test month is recorded.
- The 9 out-of-sample months are joined into one result. Switching settings at month boundaries is approximated: each setting's baskets are taken as if it had run all year.

**Pass (all required):**
1. walk-forward out-of-sample net USD > 0;
2. at least 6 of the 9 out-of-sample months are positive;
3. the out-of-sample max drawdown is below the out-of-sample net × 2, so a single bad month cannot erase the gains.

**Also reported, but descriptive only and never a pass:**
- the best full-year setting in hindsight;
- the most robust setting (best worst-quarter result);
- how often each setting value is chosen;
- the share of all settings profitable in all 4 quarters.

These are in-sample and are **not** evidence that a setting works.

A pass would justify a demo trial of the walk-forward procedure only. A fail means no settings of this bot can be recommended.
