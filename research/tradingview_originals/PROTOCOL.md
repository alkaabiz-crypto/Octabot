# Pre-registered protocol: the ORIGINAL TradingView scripts, traded the way they are designed

Written on 2026-11-10, before any result of this round was computed. Paper research only. Nothing in earlier studies,
the signal assistant or the frozen Donchian forward test is changed.

## Why this round

TradingView became reachable from this environment, so the original Pine source of each script was downloaded
(`sources_manifest/manifest.json` lists each URL, its publication id and the SHA-256 of the source). The sources are
third-party code under their authors' licences, so they are not committed. Two things were wrong with earlier rounds.

1. **Some earlier rebuilds differed from the originals.** An audit against the real source found:

   | Script | Earlier rebuild vs original |
   |---|---|
   | Lorentzian Classification (jdehorty, v6) | Feature parameters were 2, not the original 1, for RSI 14, CCI 20 and RSI 9. The neighbour search differed: the original searches a fixed history block, newest first. |
   | Session VWAP Profile & Candle Delta (BigBeluga) | It has its own signals: a wick through the 2σ band with a close back inside, at least 10 bars apart. VWAP is on close × volume with a weekly session on a 1H chart. The rebuild had none of this. |
   | QQE MOD (Mihkel00) | A different script from the QQE tested earlier |
   | Waddah Attar Explosion (LazyBear) | The original dead zone is a fixed 20, not 3.7 × ATR |
   | Range Filter (guikroth) | One condition was missing (close ≠ previous close) |
   | Supertrend (KivancOzbilgic) | The trend flips against the previous bar's band |
   | UT Bot, SSL, Chandelier Exit, HalfTrend, Coral Trend, Squeeze Momentum, WaveTrend, Vix Fix | Match the originals |
   | Hull Suite | Source not public (HTTP 401); not tested |

2. **Most of these scripts are stop-and-reverse tools.** On TradingView they are traded from one signal to the
   opposite signal, and earlier rounds used fixed exits only.

## Scripts and how each is traded

All use their published default settings on 1H bid candles.

| Script | BUY | SELL | Native exit |
|---|---|---|---|
| Lorentzian Classification v6 | start-long | start-short | the script's strict exit: 4 bars later |
| BigBeluga Session VWAP | "lower reversal": low < lower 2σ band, close > band, ≥ 10 bars since the last signal | "upper reversal" | none defined, so standard exits only |
| UT Bot Alerts (QuantNomad) | buy | sell | FLIP: hold to the opposite signal |
| SSL Channel (ErwinBeckers) | flip up | flip down | FLIP |
| Chandelier Exit (everget) | buy | sell | FLIP |
| HalfTrend (everget) | buy | sell | FLIP |
| Supertrend (KivancOzbilgic) | buy | sell | FLIP |
| Range Filter (guikroth version) | long condition | short condition | FLIP |
| Coral Trend (LazyBear) | turns up | turns down | FLIP |
| QQE MOD (Mihkel00) | first "QQE up" column | first "QQE down" column | FLIP (up to down) |
| Waddah Attar Explosion (LazyBear) | first bar where the up column > explosion line and > 20 | the same for the down column | none defined, so standard exits only |

**Exits:**

- **FLIP** (stop-and-reverse scripts): enter at the next 15-minute open after the signal candle closes, and exit at the
  next 15-minute open after the opposite signal. There is no stop, as on the chart. BUY legs and SELL legs are
  evaluated separately.
- **NATIVE** (Lorentzian only): exit after 4 hourly bars.
- **The three standard exits for every script**, for comparison with earlier rounds:
  - HW: 2 × ATR stop, 1 × ATR target, 24 h;
  - SYM: 2 × ATR target and stop, 48 h;
  - TRAIL: 2 × ATR stop, 3 × ATR trail.

## Lorentzian: real-time replay

Live, the script recomputes on each new bar with `last_bar_index` = the current bar. So for every bar t, the
original's loop is replayed exactly:

- `i` runs from `t − 2000` to `min(1999, t)`, counting down when the start is larger, as Pine does;
- bars whose index is a multiple of 4 are skipped;
- the lastDistance rule and the persistent predictions array are kept.

Bar index 0 is the first candle in the data (2024-03-01), standing in for the start of the chart's history. Features
use the original library formulas, with running-min/max normalisation.

## Benchmarks, costs, periods, pass rule

- **Costs.** Real bid/ask (buy at the ask, sell at the bid) plus 0.02% slippage. R = 2 × ATR14 at entry, so results are
  comparable with earlier rounds.
- **Standard exits:** the matched random-entry benchmark as before.
- **FLIP and NATIVE exits:** random entries in the same calendar quarter, holding exactly as long as the strategy's
  trades, in the same direction, 1,000 runs.
- **Selection** is 2025; **confirmation** is 2026 to the latest quote.
- **Reliable** means, in both periods:
  - at least 30 trades in 2025 and 20 in 2026;
  - expectancy > 0;
  - p_random ≤ 0.05.

  **70%-worthy** means reliable, and also a win rate of at least 70% in both periods.
- **Pre-registered untouched-data check** for any reliable variant:
  - BTC 2020–2024 on Binance (0.05% cost);
  - US oil 2019-02 to 2024-12 on Exness ticks;
  - gold 2020–2023 on Exness ticks (downloaded if needed).

  A variant counts as **validated** only if it also has expectancy > 0 and p_random ≤ 0.05 there.

About 250 variants are tested. Even a validated variant justifies only a frozen forward paper test.
