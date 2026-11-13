# Gold Asian-session long: forward PAPER test rules (frozen)

Written and committed **2026-11-12 00:05 UTC, before the first entry.** Fake money only. No orders, no accounts.

This is the rule that passed the pre-registered robustness test in `../shortlist_2025/ASIA_ROBUSTNESS_PREREG.md`:
- **Variant A, 22:05 entry.** Exness XAUUSDm ticks, 2025-01 to 2026-10.
- **Results:** net **+23.6%** at 1× spread and **+20.3%** at 2× spread, over 472 trades with 54% wins.
- **Swap:** the swap check (`../shortlist_2025/VERIFICATION.md`) showed the position is never open at the Exness rollover, so no swap applies.

## Data

- **Feed:** Hyperliquid **xyz:GOLD** 1m candles, from the public API. All data is from 2026, which satisfies the user's rule of nothing before 2025.
- **Not the user's broker price:** this is not the Exness XAUUSDm price.

## Rule

- **Entry:** every day whose UTC weekday is **Sunday to Thursday**, buy at the **open of the first 1m candle at or after 22:05 UTC**. That is 02:05 UAE time.
- **Exit:** sell at the **open of the first 1m candle at or after 07:00 UTC the next day**. That is 11:00 UAE time.
- **Direction:** long only. No stop, no target, no other filter.
- **Size:** the whole paper account, starting at **2,722.94 USD**. The account compounds, with no leverage and fractional ounces allowed.
- **Fixed 1-ounce line:** each trade's result is also shown for a fixed **1 oz**, which is 0.01 lot on Exness.
- **Costs:** a spread of **0.20 USD per oz per round trip**, the same as the gold MOM50 test. Results at **2× cost (0.40)** are shown alongside. Swap is 0, as explained above.

## Operation

- **Start:** the first entry is **2026-11-12 22:05 UTC**.
- **Exactly once:** `state.json` holds the last processed 1m candle and any open position. Each 1m candle is processed once.
- **Append-only:** `ledger.csv` has one row per closed trade and is never rewritten.
- **STOPPED, with no workaround, if:**
  - the 1m feed has a gap of more than 90 minutes while a position is open; or
  - the feed no longer reaches back to the last processed candle, because runs were missed for more than about 3 days.
- **Evaluation after 100 closed trades,** which takes about 5 months. **Pass:** the average net result per trade at 2× cost is above 0. The backtest's average was +4.3 bp per trade at 2× cost.
  - Before 100 trades, nothing is called a result.
  - Gold buy-and-hold from the first entry is reported alongside for comparison only.
