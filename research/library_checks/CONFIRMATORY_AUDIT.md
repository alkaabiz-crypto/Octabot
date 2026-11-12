# Look-ahead audit of the remaining confirmatory tests (2026-11-12)

**Scope:** after the order-handling look-ahead was found in the library candidates (`README.md`), the two other non-Batch-2 confirmatory tests were checked for the same class of error. Each check covered both the historical backtest that selected the test and its forward code.

## Oil Stochastic (`oil_stoch_forward/forward.py`; backtest in `oil_dca_bot/app_conditions/study.py` with `smart_entry/study.py` and `optimize/optimize.py`)

**Signals:** the 4H Stochastic is mapped to each 1H close through the last **closed** 4H candle, using `searchsorted(..., side="right") - 1` in the backtest and `close_ms <= t` in the forward test.

**Entry:**
- In the backtest, at the first Exness tick within 5 minutes after the 1H close.
- In the forward test, at the 1m open after the boundary.

**Exits:**
- The backtest walks real bid/ask ticks. The stop is checked before the target, and the trailing level uses the running best price **up to** each tick.
- The forward test checks the stop first on each 1m candle, and updates the trailing level only after it has been checked.

**Units:** the backtest's `stop=10.0` is in USD. 10 USD ÷ (10 bbl) = 1.00, which equals the forward rule's 100 pips.

**Re-entry** after an exit, at the next hour while the last 4H signal persists, is the same in both and matches `FORWARD_RULES.md`.

**Result: no look-ahead found.**

## Donchian BTC (`btc_breakout/src/engine.py`, forward `btc_breakout/forward/paper_trader.py`)

**Entry:** at the open of the 15m candle that starts at the signal close. It was already flagged as idealised; executable fills are measured by `execution_shadow.py`.

**Stop and trailing:**
- Each 15m bar's low is checked against the current stop **before** the stop is changed.
- The trailing stop is raised only at a 1H close, from the best close and the ATR of the last **closed** 1H candle, so it applies from the next bar.

**Earlier audits:** `btc_breakout/audit/` has a separate, earlier audit history.

**Result: no look-ahead found.**

## Other studies

The look-ahead can only inflate results. The ORB, zone-reversal and session studies all failed, so their verdicts are unaffected.

## Batch 2 H1–H4 (`batch2/common.py`; H3 is confirmatory)

- **H3:** the taker imbalance of the hour **ending** at D is z-scored against the **previous** 720 hours (`shift(1)`). Entry is at the open of the first 1m candle at or after D + 1 min.
- **H1:** only funding stamped in (D − 24h, D] is used.
- **H2 and H4:** they use the futures and DVOL hourly bar that starts at D − 1h, i.e. closes at D, and spot keyed by close time.
- **One position at a time:** the next decision must be at or after the previous exit.
- **Forward runner:** it simulates only decisions at or after E.

**Result: no look-ahead found.**
