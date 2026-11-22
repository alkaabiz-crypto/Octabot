# Library candidates: order-handling look-ahead (found 2026-11-12)

## What was wrong

The backtest (`theory_library/theories.py`) and the "independent" minute-level verification (`theory_library/verify_minute.py`) share the same loop for limit-order strategies:

> signal i → search candles i+1 … i+10 for a fill → if none, **go back to signal i+1**.

When order i expires unfilled, the code steps back one candle. It then takes signal i+1's fill from candles that had **already passed**, knowing that order i never filled. No trader can do that in real time.

The forward test (`library_forward/forward.py`) handles orders causally, as `FORWARD_RULES.md` describes, so it never had this problem.

## Check

`order_overlap.py` changes **only** the order handling and keeps everything else the same:
- `verify_minute.py`'s own data, signals, fills, exits and Exness per-minute costs, imported unchanged;
- two causal rules: the forward test's rule (all signals while flat place orders, and the first fill in time wins), and "one pending order at a time".

The old loop reproduces the frozen numbers exactly, which confirms the harness.

**Mean net return per trade at 2× cost (bp), 2025 / 2026, Exness minute data:**

| Candidate | Frozen (look-ahead) | Forward-test rule | One order at a time |
|---|---|---|---|
| ETH_FIB | +32.3 / +19.6 | **−20.0 / −9.7** | **−15.2 / −26.7** |
| OIL_FIB | +12.9 / +17.3 | **−2.5 / −9.6** | **−11.2 / −32.1** |
| GOLD_FVG | +4.8 / +11.0 | **−0.3 / +3.8** | **+0.1 / +2.0** |

## Conclusion

All three edges were produced by the look-ahead. Under causal order handling none is positive with meaningful confidence: ETH and oil are negative, and gold is about zero.

- **The theory library now has no valid candidates.**
- Other limit-order theories in the 535-combination screen have the same flaw, so the screen's limit-order results are unreliable too.
- The frozen files are left untouched as the record. This note and `results/order_overlap.json` document the correction.

**Lesson:** the "independent" re-implementation copied the original's loop structure, so it reproduced the bug instead of catching it. Future checks must be written from the trading rules, not from the backtest's code.
