# Oil Stochastic 4H bot: forward PAPER test rules (frozen)

Written and committed **2026-11-11 before the first decision.** Fake money only. No orders, no accounts. These are the settings recommended to the user (`../oil_dca_bot/app_conditions/README.md`, best candidate), unchanged.

## Data

- **Feed:** Hyperliquid **xyz:CL** (WTI), public API, using **4H** candles for the signal and **1m** candles for managing the trade. All data is from 2026, satisfying the user's rule of nothing before 2025.
- **Not the user's broker price:** this is not the Exness USOILm price, and the two can differ slightly.

## Entry

- **Stochastic(14, 3, 3)** on fully closed 4H candles:
  - %K = SMA3 of the raw %K(14);
  - %D = SMA3 of %K;
  - **BUY** when %K < 20 and %K > %D;
  - **SELL** when %K > 80 and %K < %D.
- **Timing:** the signal is checked at each fully closed **1H** boundary, using the latest closed 4H candle, but only when **no position is open**.
- **Fill:** at the open of the first 1m candle after that boundary.

## Position and exits

- **Size:** 0.01 lot = 10 barrels. No extra orders, no leverage beyond the broker's own.
- **Stop:** 1.00 USD (100 pips) against the entry, filled at the stop price. A gap through the stop fills at the 1m open.
- **Take profit:** once price has moved 1.00 in favour (100 pips), trailing starts. The trade closes when price pulls back 0.04 (4 pips) from the best price since then, at that level.
- **Same-candle rule:** if a 1m candle reaches both the stop and the target, the **stop counts first**. Trailing exits are checked from the candle after the trigger.
- **Costs:** a spread of **0.02 USD per round trip**, 0.01 on each side, which is the median Exness USOILm spread in 2025–26. Swap is 0, since USOIL is listed as swap-free by default; this is unverified.

## Operation

- **Start:** the test starts flat. The **first check is at the 1H boundary after the first run**.
- **Exactly once:** `state.json` holds the last processed 1m candle time and any open position.
- **Append-only:** `ledger.csv` holds one row per closed trade and is never rewritten.
- **Stop condition:** the test stops with "STOPPED" if the 1m feed has a gap of more than 90 minutes on a weekday while a trade is open.
- **Evaluation:** after **100 closed trades**. The backtest equivalent was about +90 to +200 USD per 10 months at 0.01 lot. Nothing before 100 trades is called a result.
