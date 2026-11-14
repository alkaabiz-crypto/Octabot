# Can scheduled news be traded? Oil, crypto, indices, forex and metals (pre-registered)

Written before any result was computed. This is a separate module, and nothing in earlier studies is changed.

## Markets and data

Exness 15-minute bid/ask candles:
- **From 2020** (earlier long-history downloads): US oil (USOILm), BTC (BTCUSDm) and gold (XAUUSDm).
- **From 2023-01** (multi-market downloads):
  - Brent (UKOILm), ETH (ETHUSDm);
  - S&P 500 (US500m), Nasdaq 100 (USTECm), Dow (US30m), DAX (DE30m);
  - EUR/USD, USD/JPY, GBP/USD, USD/CAD;
  - silver (XAGUSDm).

## Events (all scheduled and public in advance)

- **FOMC, CPI, NFP**: the same official dates as `research/gold_kst_news/data/`. FOMC dates come from the Federal Reserve; CPI and NFP from ALFRED vintage dates.
- **EIA weekly petroleum report** (US oil, Brent and USD/CAD only).
  - 2025–26: EIA's published schedule, Wednesday 10:30 New York time plus its listed exceptions.
  - 2020–24: EIA's standard rule, Wednesday 10:30, moved to Thursday 11:00 in a week with a US federal holiday on Monday to Wednesday. A rule date is dropped if oil's 15-minute range at that time is not above the median for that clock time on nearby days. This catches unlisted exceptions; the number dropped is reported.

## Strategies

Every strategy has a 2 × ATR14 stop, where ATR14 is taken from the last closed hourly candle before the event. R is 2 × ATR. Costs are the real Exness spread plus 0.02% slippage (stress: 0.05% plus 0.02% per day).

| Name | Rule |
|---|---|
| FOLLOW15 | Trade in the direction of the release candle (the first 15 minutes). Enter at the next 15-minute open, exit 4 h after the release. |
| FADE15 | The same, against the direction of the release candle. |
| FOLLOW30 | Trade in the direction of the first 30 minutes. Enter 30 minutes after the release, exit 4 h after it. |
| BREAKOUT | After the release candle, the first 15-minute close above its high (BUY) or below its low (SELL), within 60 minutes. Enter at the next open, exit 4 h after the release. |
| PRE24 | BUY 24 h before the release and sell 15 minutes before it. This is the pre-FOMC drift reported for US stocks. Long only. |

## Benchmark

For each event, the same strategy is run at the same UTC clock time on weekdays in the same quarter with no event that day, the day before or the day after. On those control days the direction comes from that day's own candles. Each event is matched with one random control, 300 runs. z = (event mean − control mean) / standard deviation of control means.

## Fit and test

- Fit: 2020-07 to 2024-12 for markets with data from 2020; 2023-07 to 2024-12 for the others. Test: 2025-01 to the latest candle.
- A market × event × strategy passes fit with at least 15 events, z ≥ 1.645 and positive expectancy at stress cost.
- Benjamini–Hochberg at 5% is applied over the test-period p-values of all fit passers. A combination is **confirmed** only if it survives that and has positive test expectancy at stress cost.
- Expected power is low: about 8 FOMC meetings and 12 CPI and NFP releases a year, so the test period holds about 15 to 22 events per type. Only large effects can be confirmed. EIA has about 95 events in the test period.

## Also reported (descriptive, for risk)

For every market and event type: the median absolute move in the 4 hours after the release, in ATR, against the control days. This shows where closing before news matters most.
