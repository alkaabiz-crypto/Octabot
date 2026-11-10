# Oil DCA bot: settings search with an out-of-sample test: pre-registration

Written and committed **2026-11-10, before any tuning result was computed.** Research only.

## Split

- **Train (search):** 2025-11-01 to 2026-05-01.
- **Test (untouched until the choice is fixed):** 2026-05-01 to 2026-11-01.
- Same data and execution model as `../bot.py`: Exness USOILm bid/ask ticks; limit fills at the level; stops and trailing exits at the triggering tick; 1 lot = 1,000 barrels; commission and swap 0.

## Grid (only settings the user's bot app offers)

| Setting | Values |
|---|---|
| Take profit (pips; 1 pip = 0.01) | 15, 30, 60, 100 (trailing 4 pips kept) |
| Extra orders | 0, 1, 2 (sizes 0.02, 0.03 as now) |
| Extra order step (pips; step multiplier 1.3 kept) | 63, 100, 150 (not applicable with 0 extra orders) |
| Basket stop (USD) | 25, 50, 100 |
| Direction | rating only; rating + 4H EMA200 trend filter |
| Rating timeframe | 15m, 1h |

This gives 4 × (1 + 2 × 3) × 3 × 2 × 2 = **336 combinations**. "Stop loss off" is excluded: the one-year test already showed one basket stuck for 281 days at −3,204 USD.

## Selection rule (fixed now)

1. On **train** only, pick the combination with the highest net USD. A tie is broken by the lower max drawdown.
2. Run it **unchanged** on **test**.
3. As a robustness check, also report the test results of the **top 10** train combinations and the share of **all 336** that are profitable in test.

## Pass/fail, decided now

The chosen settings pass only if, on **test**, all three hold:
1. net USD > 0;
2. max drawdown is below 50% of the gross profit;
3. net USD is above the 95th percentile of 200 random-direction runs with the same settings on test.

- **A pass** would justify a **demo-account** trial of those settings only. It never justifies live money or larger size.
- **A fail** means no setting of this bot was shown to work. The recommendation is then to stop the bot.
