# Exness MT5 DEMO forward test: connection status and requirements

**Status (2026-11-10): NOT CONNECTED.** The forward-demo module has not been built, and no Exness results have been simulated in its place.

## Why it cannot connect from here

| Check | Result |
|---|---|
| MetaTrader5 Python package | Not available on this platform (`pip`: "No matching distribution found for MetaTrader5"). The official package is Windows-only and requires a running MT5 terminal. |
| Execution environment | Linux cloud container (x86_64). No MT5 terminal and no Wine. |
| Exness credentials | None present. None should be stored in this cloud environment. |
| User computers connected via Remote Control | None |
| Exness public trading API | None known. Exness trading goes through MT4/MT5 terminals. |

## What is needed to proceed

1. **A Windows computer that you control,** with the Exness MT5 terminal installed and logged in to a **DEMO** account, server name ending in "Trial". It must stay on during market hours.
2. **That computer connected to a Claude Code session,** either:
   - as a folder shared through the Claude desktop app (Settings → Claude Code → Remote Control), or
   - by running Claude Code locally on that computer.
3. **Python 3 on that computer** with `pip install MetaTrader5`.
4. **Credentials kept only on that computer,** inside the terminal. They are never pasted into chat or stored in the repository.
5. **The BTCUSDm Specification and account details,** read from the terminal or through `mt5.symbol_info("BTCUSDm")` and `mt5.account_info()`:
   - contract size, tick size, tick value, volume min/step/max;
   - margin rates, swap long and swap type, triple-swap day, commission;
   - account currency, leverage, balance and free margin.

## Safeguards the module must enforce (design, not yet implemented)

- **Demo check before any order:** refuse to start unless `account_info().trade_mode == ACCOUNT_TRADE_MODE_DEMO` and the server name contains "Trial". Re-check before every order.
- **Fixed strategy:** the frozen Donchian 20 rules from `research/btc_breakout/src/engine.py`, unchanged, run on closed Exness BTCUSDm bid candles. Volume uses the real volume_min, volume_step and contract size, rounded down so risk never exceeds 0.5%. If the required volume is below the minimum, log the signal as `REJECTED_BELOW_MIN_VOLUME`.
- **Full logging:**
  - every signal, accepted or rejected, with its reason;
  - order send time, fill time and latency;
  - requested vs filled price, bid/ask at send time, spread and slippage;
  - commission, swaps per rollover and stop modifications;
  - exit fill;
  - a separate trade and equity ledger in `research/exness_validation/forward_demo/`.
- **No live account and no automatic promotion to live,** regardless of trade count. Binance fills are never used as Exness executions.
- **Interim report at 40 trades** covering:
  - net expectancy, profit factor, drawdown and win rate;
  - concentration in large winners;
  - execution quality;
  - confidence intervals;
  - comparison with the frozen benchmark (the one-year Exness study).
