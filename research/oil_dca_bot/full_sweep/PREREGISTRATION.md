# Oil bot full sweep (indicators × timeframes × app exits): pre-registration

Committed **2026-11-11, before running.** Research only. Exness USOILm ticks 2025-01 to 2026-10. Real spread plus a 2× stress run, swap 0.

## Grid (only settings the user's app allows)

- **Entry conditions (12):** Indicators Summary, EMA200, SMA200, Bollinger(20,2), Ultimate Oscillator, ADX(14), RSI(14), CCI(20), Stochastic(14,3,3), MACD, Parabolic SAR, MFI(14). Rules as in `../app_conditions/PREREGISTRATION.md`.
- **Timeframes (5):** 15m, 30m, 1H, 4H, 1D.
  - Signals are read on closed candles of that timeframe.
  - A new trade can open at each close of that timeframe, when flat.
- **Exits (6):** no extra orders, 0.01 lot, 4-pip trailing after TP.
  - Take profit: 100, 200 or 300 pips.
  - Stop loss: **300 or 500 pips**; the app's minimum is 300.

That gives **360 combinations**, each at 1× and 2× spread.

## Selection protocol (prevents picking a lucky combination)

1. **Rank by development period only (2025):** net at 2× spread, requiring at least 30 trades and a development max drawdown under 408 USD. **Select the top 5.**
2. **Confirm on the holdout (Jan–Oct 2026)**, which played no part in the selection. A selected combination **passes** only if:
   - holdout net > 0 at 1× **and** 2×;
   - holdout max drawdown < 408 USD;
   - at least 30 holdout trades;
   - holdout net above the 90th percentile of 100 random-direction runs with the **same timeframe and exit**.
3. **Recommendation:** the passing combination with the best holdout net at 2× spread. If none passes, the recommendation is "no reliable setting found".

**Also reported:** the holdout results of all 360 combinations, and the share positive, so the effect of trying so many is visible.
