# Verification of the gold SCHOOL passes: pre-registration

Committed **2026-11-12, after the main study** (2 of 40 combinations passed, `XAUUSDm|SCHOOL|X0` and `XAUUSDm|SCHOOL|XC`) and **before running this check.**

## Why

The gold SCHOOL range is 08:25–08:30 New York, so entries cluster right at **08:30 ET, when US economic data is released**. At that time price can jump straight through the breakout level and spreads widen. The 1-minute model fills a stop order at the level plus the bar's median half spread, which can understate the real cost.

## Independent tick-level re-test (new code, not reusing `study.py`)

- **Ticks:** Exness XAUUSDm, the same cached files.
- **Range:** the mid high and low of all ticks from 08:25:00 to 08:29:59.999 New York.
- **Entry:** a buy stop fills at the **ask of the first tick whose ask ≥ range high + the range-start half spread**, or a sell stop at the bid of the first tick whose bid ≤ range low − that half spread.
  - In plain terms: at the real tick price, gaps included.
  - The first side triggered wins. One trade per day.
- **Stop:** sell at the **bid of the first tick with bid ≤ stop level**, gaps included. For a short, buy at the ask of the first tick with ask ≥ stop level.
- **Take profit:** a limit order at entry level ± H. It fills at the level when the bid (for a long) or the ask (for a short) reaches it.
- **Forced exit:** at 13:30 New York, at the tick's bid or ask.
- **XC:** checked at the tick that closes the 5-minute candle containing the entry.
- **2× cost:** an extra half spread on each side, using that tick's spread.

## Pass, for the result to be confirmed

- The tick-level mean R at 2× cost is **> 0 in both 2025 and Jan–Oct 2026** for X0; XC is reported too.
- **Agreement:** the 1-minute model and the tick model agree on the trade direction on ≥ 95% of shared days.

## Reported for information, with no verdict

- **Neighbouring windows** shifted by ±5 minutes (08:20–08:25 and 08:30–08:35), and the same rule on days with versus without a major 08:30 release. Release days are taken from the tick data: 1-minute range at 08:30 > 3× its 20-day median.
- Mean slippage of tick fills against the 1-minute model's fill prices.

**If confirmed:** a frozen forward paper test is set up, and the user is told it is a candidate only. Nothing goes live.
