---
title: STR-049 NY-open candle + EMA 12 + trailing stop pre-registration
description: Instagram scuta_net (Arabic) claim of +982% on the Nasdaq 2019-2026 from the first 5-minute candle after the New York open, EMA 12 direction and a trailing stop
sidebar_position: 1
---

# STR-049: first 5-minute candle + EMA 12 + trailing stop (pre-registration, 2026-11-22, before any computation)

## Source

An Instagram post by **scuta_net**, from a screenshot the user sent on 2026-11-22. The Arabic caption, in translation:
- "A strategy that starts from one 5-minute candle, and made **982%** in the historical backtest."
- Rules:
  - the first 5-minute candle after the New York session opens;
  - **closed above the 12 EMA = buy, below it = sell**;
  - a **trailing stop** follows the price as long as the momentum continues.
- "Nasdaq, 5-minute frame, 2019–2026: **1,448 trades · profit factor 1.29 · win rate 57% · max drawdown under 20%**."
- The full study and source code are offered on a Telegram channel (not available here).
- The chart shows a stepped dashed stop under the candles, rising after each new candle, with the trade "staying open".

This is close to STR-033 (QuantLab). The differences: direction comes from the EMA only (as STR-033's variant B), and the exit is a trailing stop instead of a fixed 6 hours.

## Rules (fixed now; trailing-stop details are not given, so three variants)

- **Data:** Exness USTECm 1-minute mid prices and spreads, 2019-08 → 2026-10 (the STR-033 build), aggregated into 5-minute candles.
- **Signal:** the 09:30–09:35 New York candle. Its close vs EMA 12 of continuous 5-minute closes, read at 09:35. Above → LONG; below → SHORT.
- **Entry:** the 09:35 1-minute open.
- **Initial stop:** the opposite end of the first 5-minute candle.
- **Trailing stop** (updated at each 5-minute close; it only moves in the trade's favour):
  - **T1 (primary, as drawn):** the stop is raised to the low of the last completed 5-minute candle (the high for shorts).
  - **T2:** the stop trails 2 × ATR14 (5-minute) behind the highest close since entry (the lowest for shorts).
  - **T3:** exit at the first 5-minute close on the wrong side of EMA 12 (initial stop still active).
- **Exit:** the stop is hit (checked on 1-minute bars; a gap through it fills at the open), or the 16:00 New York close. Day trading only, nothing held overnight.
- **Costs:** the actual spread at entry and exit (stress 2 ×).
- **Reported:**
  - R per trade (risk = entry to initial stop);
  - win rate and profit factor;
  - compounded return at 1% risk per trade, and maximum drawdown, to compare with the claim (+982%, PF 1.29, 57% wins, max DD < 20%).
- **Benchmark:** a random direction on the same days with the same trailing rule, 1,000 sets.
- **Decision:**
  - **SCREEN-PASS:** mean R > 0 in every period (2019-08→2022, TRAIN, VALIDATION, TEST), TEST stress > 0, TEST p ≤ 0.05 after BH over the 3 variants, and ≥ 30 TEST trades.
  - **WATCH:** positive in every period. Otherwise **REJECTED**.
