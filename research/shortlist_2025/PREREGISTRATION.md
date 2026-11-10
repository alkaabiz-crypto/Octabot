# Research shortlist screen on 2025+ data: pre-registration

Written and committed **2026-11-10, before any result was computed.** Research only: no orders, no accounts.

- **Source:** the rules come from `reports/Evidence backed trading signals.md` and are used with their **published settings, never re-tuned.**
- **Data:** only data from **2025-01-01** onward, per the user's rule.
  - Gold and US oil: Exness **XAUUSDm** and **USOILm** bid/ask ticks, 2025-01 to 2026-10.
  - BTC and ETH: Binance BTCUSDT and ETHUSDT daily and hourly candles from 2025-01-01, `../daily_signal_dca/from_2025/data`.
- **Purpose:** less than two years of data can only **screen** a rule, checking whether it behaves as published. It cannot prove an edge.

## Rules

**Gold (XAUUSDm, long or flat)**
- **G_SMA200:** long while the daily close is above its 200-day SMA. This becomes possible only once 200 days of 2025+ data exist, around late Oct 2025.
- **G_MOM50_ATR** (Forecast-to-Fill template):
  - **entry:** close above the close 50 days ago **and** the 20-day SMA higher than 5 days ago;
  - **exit, whichever comes first:** close below entry − 2×ATR14, close below peak − 1.5×ATR14, or 30 trading days held.
- **G_ASIA / G_US:** long only 22:00–07:00 UTC, or only 13:00–21:00 UTC, every weekday.
- **G_SEPNOV (control, expected to fail):** long only in September and November.
- **Not testable under the 2025+ rule:** the 24-month momentum and 36/48-month moving-average rules (rank 1 in the report) and the 10-month SMA, which need 10–48 months of history. They are reported as not testable.

**US oil (USOILm)**
- **O_MOM_BLEND** (long or short): at each month-end, position = average sign of the 1-, 3- and 12-month returns. It needs 12 months of 2025+ history, so it is active from 2026-01.
- **O_INTRADAY:**
  - take the sign of the 09:30–10:00 New York time return;
  - on Wednesdays (the regular EIA release day), the 10:30–11:00 New York return is used instead;
  - hold that direction from 15:30 to 16:00 New York time, exiting at the 16:00 price;
  - New York time follows US daylight-saving changes;
  - holiday-week EIA moves are **not** modelled.
- **O_TURTLE** (long or short): enter on a close at a 55-day high (long) or low (short); exit on a 20-day opposite extreme.
- **Not testable:** the OPEC-cut rule and the backwardation rule. There is no event calendar or futures curve here.

**BTC and ETH (Binance spot, long or flat, no leverage)**
- **C_DONCH_ENS** (Zarattini ensemble):
  - one sub-signal for each lookback of 5, 10, 20, 30, 60, 90, 150, 250 and 360 days;
  - each enters when the close is above that lookback's highest close (previous days);
  - each exits when the close is below a trailing stop = max(previous stop, midpoint of that lookback's highest and lowest close);
  - position = the equal-weight average of the 9 sub-signals, scaled to 25% volatility (90-day) and **capped at 1.0, because the user forbids leverage**;
  - each lookback becomes active once it has enough 2025+ history.
- **C_SMA50:** long while the close is above SMA50.
- **C_MAX20 / C_MAX10:** if today's close is the highest of the last 20 (or 10) days, hold for the next day.
- **C_MIN10 (control):** if today's close is the lowest of the last 10 days, hold for the next day.

## Costs

- **Gold and oil:** the real Exness spread at each entry and exit tick (buy at ask, sell at bid). Swap is unknown and not deducted; it is noted for rules held overnight. A **2× spread** stress run is also reported.
- **Crypto:** 0.1% per side, with a 0.2% stress run.
- **Timing:** daily signals trade at the first tick, or the next candle open, after the signal close.

## Screen (decided now)

A rule is labelled **CONSISTENT WITH PUBLISHED EVIDENCE** only if **all** of these hold over its active window:
1. its net return is above 0 **at 2× costs**;
2. for long/flat filters, its max drawdown is smaller than buy-and-hold's over the same window; for intraday and long/short rules, its net return is above 0 at 1× **and** 2× costs;
3. it made at least 10 trades.

Otherwise it is labelled **NOT CONFIRMED**.

- A "consistent" label qualifies a rule only for a **forward paper test**, never for live money.
- Control rules that pass are a warning sign about luck in this short window.
