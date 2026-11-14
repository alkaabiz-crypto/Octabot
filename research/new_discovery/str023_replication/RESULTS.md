# STR-023 replication on five other cryptocurrencies: results. **NOT REPLICATED**

Pre-registered in `PREREG.md` (commit `0d1ad30d`). Script `run_rep.py`, output `results.json`. Data: Exness 15-minute bid/ask, 2023-02 → 2026-11, tick-count VWAP. Frozen study code.

| Market | Trades | Median Exness spread | Mean R at the decision cost (1.5× spread) | t | Mean R at the study's 0.05% | Random entry at 0.05% | p_random |
|---|---|---|---|---|---|---|---|
| SOL | 431 | 0.67% | −0.321 | −3.17 | +0.147 | +0.083 | 0.14 |
| BNB | 448 | 0.36% | −0.345 | −3.81 | +0.077 | +0.069 | 0.47 |
| XRP | 640 | 0.27% | −0.132 | −1.13 | +0.080 | +0.045 | 0.32 |
| LTC | 653 | 1.41% | −1.212 | −17.7 | −0.024 | −0.044 | 0.31 |
| BCH | 638 | 0.36% | −0.277 | −3.68 | −0.025 | −0.005 | 0.65 |

**Reading.**
- **At Exness's real costs** the strategy loses on all five: altcoin CFD spreads of 0.27–1.41% exceed its whole gross edge.
- **At the study's cheap 0.05% cost** three markets are slightly positive, but **none beats matched random entry** (p_random 0.14–0.65). Even before costs, the entry adds nothing measurable on these markets.
- **STR-023 does not generalise beyond BTC and ETH.** Its forward test on BTC and ETH continues unchanged, but this lowers the prior that its BTC/ETH backtest edge is a general effect.
