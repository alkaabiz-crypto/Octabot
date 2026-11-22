# Opening-range breakout (ORB) and Hougaard "school run": results

The rules were fixed in `PREREGISTRATION.md` (commit `7033ffe6`) before any data was built.
- **Data:** Exness ticks from Jan 2025 to Oct 2026, built into 1-minute bars.
- **Markets:** DAX, S&P 500, Nasdaq, gold and US oil.
- **Ranges:** the first 1-, 5- or 15-minute candle, or the 2nd 5-minute candle (school run).
- **Exits:** stop on the other side of the range, take profit at 1:1, optional exit if the candle closes back inside the range.
- **Comparison:** 2025 against Jan–Oct 2026, with a random-entry control.

## Verdict: no version survives

| Step | Result |
|---|---|
| Main study, 40 combinations | **38 FAIL.** Only **gold, school run** (range 08:25–08:30 New York) passed, with both exits. |
| Independent **tick-level** re-test of that pass (`VERIFY_PREREG.md`, real gap fills and real spreads) | **NOT CONFIRMED.** At 2× cost: **+0.002 R per trade in 2025, −0.030 R in 2026** (258 and 215 trades). |
| Agreement between the two models on trade direction | 99.6% of 446 shared days, so the rule itself was coded the same way. |
| Why the 1-minute model was too optimistic | Real entries filled **0.21 USD worse** on average, about 0.04 R. Stops that **gapped** through the level also filled worse. The 1-minute model filled at the level plus the median spread. |
| Neighbouring windows (08:20 and 08:30 starts) | Negative in both years at 1× and 2× cost. The pass sat on one exact 5-minute window, which is a sign of luck, not edge. |
| The close filter (exit if the candle closes back inside the range) | It did **not** help. Win rate fell from about 57% to about 47%, and mean R was lower in every gold test. |

## Main study, mean R per trade at 2× spread (development 2025 / holdout 2026)

| Market | First 1m | First 5m | First 15m | School run (2nd 5m) |
|---|---|---|---|---|
| DAX | −0.21 / +0.14 | −0.17 / −0.05 | −0.09 / −0.10 | −0.32 / −0.01 |
| S&P 500 | −0.10 / −0.12 | −0.08 / −0.23 | −0.04 / −0.09 | −0.11 / −0.26 |
| Nasdaq | −0.02 / −0.11 | −0.01 / −0.09 | +0.08 / −0.10 | +0.01 / −0.05 |
| Gold | +0.03 / −0.03 | −0.01 / −0.11 | −0.10 / −0.13 | +0.10 / +0.11, then **≈0 / −0.03 at tick level** |
| US oil | −0.06 / −0.20 | −0.12 / −0.08 | −0.15 / −0.13 | −0.30 / −0.09 |

(X0 exits shown. The XC close filter was similar or worse.)

## What this means

- **On 2025–26 Exness data, the opening-range breakout with a 1:1 target does not make money after real costs** in any of the five markets.
  - Win rates sit around 45–60%.
  - With a 1:1 target you need well over 50% wins plus enough margin to pay the spread.
  - On a small 5-minute range, the spread is a large share of the risk.
- **The one apparent winner disappeared** once the tick data showed real fills. Most of its trades happen right at the 08:30 New York data release, when price jumps past the entry.
- **The "80% win rate" claim from the video is not supported.** The best version here won about 58–61%, and only before realistic fills.

Files: `build_bars.py`, `study.py`, `verify_tick.py`, `results/results.json`, `results/verify_tick.json`, `data/*_sha256.json`.

## Second interpretation set (after the user questioned the test): `PREREG_V2.md`

The user thought the first test might have used the wrong rules, so 56 more versions were tested:
- **close-confirmation entry**, where a candle must close outside the range before entering, with a true 1:1 target from the entry;
- the **09:30 New York stock open** for gold and oil;
- the **08:00 London open** for gold.

| Step | Result |
|---|---|
| 56 combinations (`results/results_v2.json`) | **55 FAIL.** Close-confirmation entries failed on every market and open. |
| The one pass: gold, first 1-minute candle after 09:30 New York, touch entry | 1-minute model at 2× cost: +0.057 R in 2025 and +0.018 R in 2026, which is very thin. |
| Tick-level re-test of that pass (`verify_tick_v2.py`, `results/verify_tick_v2.json`) | **NOT CONFIRMED: −0.081 R in 2025 and −0.067 R in 2026** at 2× cost. It is negative even at 1× cost (−0.009 and −0.013). On a 1-minute range the spread is about 6% of the risk, and real fills are worse than the bar model. |
| Neighbouring windows (09:29, 09:31, first 2 minutes) | Negative in 2026 at every window. |

**Conclusion across both sets (96 versions):** no opening-range or school-run variant makes money on 2025–26 Exness data after realistic fills and spreads.
