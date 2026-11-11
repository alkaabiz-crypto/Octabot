# Gold MOM50 + ATR exits: forward PAPER test rules (frozen)

Written and committed **2026-11-11 before the first decision.** Fake money only. No orders, no accounts. The rule comes unchanged from `../shortlist_2025/PREREGISTRATION.md` (G_MOM50_ATR), which was the strongest "consistent with published evidence" result in the 2025+ screen and was independently re-verified (`../shortlist_2025/VERIFICATION.md`).

## Data

- **Feed:** Hyperliquid **xyz:GOLD** daily candles (UTC days), public API `api.hyperliquid.xyz`, from 2025-12-22, the first candle available. That is after 2025-01-01, as the user requires.
- **Trading days only:** only fully closed **Monday–Friday** candles are used, so the rule counts trading days as in the Exness backtest. Weekend candles are ignored.
- **Not the user's broker price:** this is not the Exness price, and it can differ by a few USD.

## Rule (unchanged)

- **Entry**, when flat: on a closed day where the close is above the close 50 trading days earlier **and** SMA20 is above SMA20 five trading days earlier.
- **Exit**, when long: on a closed day where any of these is true:
  - close < entry close − 2×ATR14;
  - close < the highest close since entry − 1.5×ATR14;
  - 30 trading days have been held.
- **ATR14:** the Wilder average of the true range, from daily highs and lows.
- **Long or flat only. No leverage.**

## Execution and costs

- **When:** each decision is filled at the **open of the next Monday–Friday candle.**
- **Cost:** a fixed **0.20 USD per oz each side**, 0.40 round trip. That is about 1.5–2.5× the median Exness XAUUSDm spread measured in 2025–26 (0.16–0.36).
- **Swap:** unknown, so not deducted. It is noted in the report.
- **Account:** 2,722.94 USD (10,000 AED). Position = all equity / fill price, in oz.

## Operation

- **First decision:** the close of **2026-11-11** (Wednesday). Earlier days are used only to compute indicators. The test always starts flat.
- **Exactly once:** `state.json` holds the last processed close.
- **Append-only:** `ledger.csv` is never rewritten.
- **Stop:** the test stops with "STOPPED" if a gap in weekday candles or a revised past candle is detected.
- **Evaluation:** after **20 completed trades** or **2027-11-11**, whichever comes first, against buy and hold on the same feed. No result before then is called a conclusion.
