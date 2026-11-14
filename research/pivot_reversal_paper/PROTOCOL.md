# Frozen protocol: Pivot Reversal BUY forward paper test on BTC

Frozen on 2026-11-11, before any leg was recorded. Paper trading only. Nothing in earlier studies, the signal
assistant or the existing Donchian forward test is changed, and this test runs alongside them.

## Why this signal

It was the best of 8,637 variants on the full 2020 to 2026 history (`research/long_history`):

- 1,405 BUY legs;
- +0.165R per trade, against +0.020R for random entries held as long;
- positive in 6 of 7 years, and positive after stress costs;
- z = 3.2.

It did **not** pass the multiple-testing correction, so it may be the luckiest of many. Only new data can tell.

## Rules (frozen)

- **Strategy.** TradingView's built-in "Pivot Reversal Strategy" at its defaults (left bars 4, right bars 2), on 1H
  Exness BTCUSDm bid candles, replayed by `research/tradingview_builtins/src/builtin_strategies.py`.
  - After a pivot high is confirmed, a buy-stop sits at that high until the price trades through it or a new pivot
    replaces it.
  - The position stays open until the sell-stop at the latest pivot low fills, which reverses the strategy.
- **What is counted.** Only the BUY legs: from the buy fill to the sell-stop fill.
- **Fills and costs.**
  - Real bid/ask at 15-minute resolution: buy at the ask, sell at the bid.
  - Primary cost: plus 0.02% slippage.
  - Stress cost: plus 0.05% slippage and 0.02% per day held.
- **R.** R = 2 × ATR14 at the signal bar, as in the backtest.
- **Counting window.** Legs entered at or after 2026-11-12 00:00 UTC. Candles from 2026-10 onward are used only to
  warm up pivots and ATR.
- **Frozen code.** The engine files are pinned by SHA-256 in `src/config.py`, and `src/paper.py` refuses to run if any
  of them changes.
- **Append-only ledger.** `ledger/trades.csv` is append-only. If a re-run changes a recorded leg (for example because
  the archive revised its quotes), the script stops and the change must be investigated and documented.

## Decision rule (fixed now)

- **Checkpoints** at 50, 100, 200 and 300 legs are descriptive only. Nothing is changed at them.
- **Futility.** If the first 200 legs have expectancy ≤ 0R, the test has failed and stops.
- **Final decision at 400 legs** (about 1.8 years at the backtest's 221 legs a year). **PASS** only if all three hold:
  - expectancy > 0 at primary cost;
  - expectancy > 0 at stress cost;
  - it beats random entries in the same period with the same holding times (1,000 runs, one-sided p ≤ 0.05).

## Power (written before any leg)

The backtest's margin over random entry was about +0.145R per leg, with a spread of 2.3R per leg. Even if that margin
is real, 400 legs give an expected z of about 1.26, so the pass rule would be met only **about 35% of the time.** A
fail at 400 therefore does not prove the signal is useless. But only a pass would count as evidence. Nothing about the
rules may be changed to improve those odds.

## What a pass would and would not mean

A pass would justify a small, separately reviewed live trial with fixed risk. It would not justify full live trading,
and it would not validate any other indicator.

## Running it

```bash
python src/paper.py      # rebuilds the data from the Exness archive, updates ledger/ and ledger/STATUS.md
```

The archive lags by about a day, so this is a delayed paper record, not a live alert service.
