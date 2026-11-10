# Donchian 20 BUY: independent validation

A stricter, independent validation of the frozen Donchian 20 BTC breakout strategy (1H entries, 4H EMA200 filter,
long only, ATR trailing stop). Paper research only.

- **[REPORT.md](REPORT.md)**: findings and recommendation. In short: reject as a trading edge. The breakout does not
  beat matched random entry, and the profit comes from market exposure.
- **[PROTOCOL.md](PROTOCOL.md)**: pre-registered prospective protocol for the forward paper test, with sample sizes and stopping rules.

## Independence and what is left untouched

This project only READS the frozen strategy, its data and its forward ledger, from a checkout of branch
`claude/download-skill-27d08k` pinned at commit `f1798b71`. Before use, `src/frozen.py` checks the SHA-256 of
`engine.py`, `protocol.py`, `paper_trader.py` and every data file against the frozen values. The forward test, its
scheduled task, the earlier research modules and all locked parameters are unchanged.

## Reproducing

Python 3.13, standard library only.

```bash
# 1. a read-only checkout of the frozen research
git worktree add --detach /tmp/frozen f1798b71
(cd /tmp/frozen/research/btc_breakout/data && gunzip -k *.gz)
export FROZEN_BTC_BREAKOUT=/tmp/frozen/research/btc_breakout

# 2. from research/donchian_validation
python src/verify_replica.py          # replica == frozen engine, trade for trade (reports/replica_check.json)
python src/run_validation.py          # audit, costs, concentration, regimes, random benchmark (about 3 min)
python src/design_protocol.py         # sample sizes and stopping boundaries (about 30 s)
python src/tick_latency.py <entries.csv> reports/tick_latency.json <workdir>   # tick-level delay (downloads ticks)
python -m unittest discover -s tests -p "test_*.py"

# 3. at each look of the forward test (needs a CURRENT checkout of the forward branch)
python src/evaluate_forward.py
```

All random procedures use seed 20261110, so reruns give identical results.

## Files

| Path | Purpose |
|---|---|
| `src/config.py` | Fixed settings, written before any result |
| `src/frozen.py` | Read-only loader of the frozen engine with integrity checks |
| `src/replica.py` | Replica of the frozen trade simulation, with execution-delay and stop-slippage options |
| `src/exness_lab.py` | The frozen signal logic on Exness BTCUSDm bid/ask quotes |
| `src/run_validation.py` | Every validation analysis; writes `reports/validation.json` and per-trade ledgers |
| `src/design_protocol.py` | Simulation of the sequential design; writes `reports/protocol_design.json` |
| `src/tick_latency.py` | Exness ask movement in the seconds after each signal; writes `reports/tick_latency.json` |
| `src/evaluate_forward.py` | Applies PROTOCOL.md to the forward ledger, read-only |
| `tests/test_validation.py` | Tests, including the random-sampler bias check and replica equality |
