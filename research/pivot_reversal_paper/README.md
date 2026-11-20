# Pivot Reversal BUY: forward paper test on BTC

A frozen, append-only paper test of the best signal found in `research/long_history`. The rules and the decision rule
are in [`PROTOCOL.md`](PROTOCOL.md). The current state is in [`ledger/STATUS.md`](ledger/STATUS.md), and every
recorded leg is in `ledger/trades.csv`.

Run `python src/paper.py` to update it. A daily scheduled run updates and commits the ledger.

## Audit note (2026-11-12)

The audit in [../audit](../audit) found that the random-entry benchmark used here for held legs (`fast_bench.held`) is **conservative**. With no edge at all, its z-score had a standard deviation of only about 0.79 on BTC, against the 1.0 a correct test should give. So the final decision at 400 legs is stricter than intended. It cannot pass by luck more often than stated, but it could miss a real edge.

The frozen rules are left unchanged. At the decision point, also report the calibrated sequential benchmark (`research/audit/src/seq_held.py`) next to the frozen one. On the 2020–2026 backtest, that benchmark raised this strategy's z from 3.21 to 4.35.
