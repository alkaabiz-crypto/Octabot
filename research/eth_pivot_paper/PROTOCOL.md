# Frozen protocol: Pivot Reversal BUY forward paper test on ETH

Frozen on 2026-11-12, before any leg was recorded. This is paper trading only, and nothing in other studies or paper tests is changed.

## Why this test

The 2026-11-12 audit ([../audit](../audit)) corrected the benchmark for held legs. After the correction, Pivot Reversal BUY was the one strategy with support on two crypto markets:
- **BTC, 2020–2026:** 1,405 trades, +0.17R per trade, z about 4.4.
- **ETH:** picked on 2023-07 to 2024-12, then confirmed on 2025-01 to now. That is 404 trades, +0.17R per trade, z about 3.2, p about 0.001. It only just passed the multiple-testing correction.

The BTC version already runs as a frozen paper test (`../pivot_reversal_paper`). This test adds ETH on new data.

## Rules (same as the BTC test)

- **Strategy.** TradingView's built-in "Pivot Reversal Strategy" (leftBars 4, rightBars 2) on 1-hour Exness ETHUSDm candles, BUY legs only.
- **Fills.** Real bid/ask and the strategy's own exits. R = 2 × ATR14.
- **What counts.** Legs entered from 2026-11-12 00:00 UTC.
- **Checkpoints.** 50, 100, 200 and 300 legs. Futility: stop as failed if expectancy is ≤ 0 after 200 legs.
- **Decision at 400 legs.** PASS only if expectancy is > 0 at primary and at stress cost **and** p ≤ 0.05 against the calibrated sequential random-entry benchmark (`research/audit/src/seq_held.py`, frozen by hash).
- The engine files are hash-checked on every run, and the ledger is append-only.

A pass would justify a small, separately reviewed live trial, not full live trading.
