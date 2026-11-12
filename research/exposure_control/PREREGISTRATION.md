# Exposure-matched random-timing control: pre-registration

Committed **2026-11-12, before running.**

## Why

The session study showed that a long-only rule can look good just from the market's direction. This test asks a different question: **does the rule's timing add anything beyond how much of the time it is invested?**

## Method

- **Data and costs:** the same as the original backtests. All data is from 2025 onward.
  - **Trend bot:** Binance daily candles cached in `../daily_signal_dca/from_2025/data/`, with the 0.1% fee.
  - **Gold MOM50:** Exness XAUUSDm ticks, built into daily candles with `../shortlist_2025/screen.py`, at **2× spread**.
- **The same engines, unchanged:**
  - `daily_signal_dca/study.py lump` for the trend bot;
  - `shortlist_2025/screen.py run_daily` for gold.
- **Control:** **1,000 circular shifts** of each rule's daily position series. The shift is a whole number of days, drawn uniformly from [20, n − 20] with seed 20261112.
  - A shift keeps the exact exposure and holding-period pattern, but puts the trades at random dates.
  - The return is measured over the same period as the original result.

## Primary tests

| Rule | Measure | Pass |
|---|---|---|
| TREND_ENS on BTCUSDT (the forward trend bot) | full-period lump-sum return | > 95th percentile of the shifts |
| TREND_ENS on ETHUSDT (the forward trend bot) | full-period lump-sum return | > 95th percentile of the shifts |
| G_MOM50_ATR on gold (the gold MOM50 forward test) | full-period net at 2× spread | > 95th percentile of the shifts |

**Information only:** SMA50 on BTC and ETH, and TREND_ENS_VOL.

## Consequences, fixed in advance

- **The forward tests keep running unchanged,** whatever happens here, because their rules are frozen.
- **A FAIL is reported to the user** as "this rule's timing is not distinguishable from chance on 2025–26 data". Any recommendation that relied on it is withdrawn.
- **Low power:** with roughly 22 months of data, a FAIL can come from too little data as well as from no edge. The report will say this.
