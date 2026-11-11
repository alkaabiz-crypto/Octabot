# Pivot Reversal BUY: forward paper test on BTC

A frozen, append-only paper test of the best signal found in `research/long_history`. The rules and the decision rule
are in [`PROTOCOL.md`](PROTOCOL.md). The current state is in [`ledger/STATUS.md`](ledger/STATUS.md), and every
recorded leg is in `ledger/trades.csv`.

Run `python src/paper.py` to update it. A daily scheduled run updates and commits the ledger.
