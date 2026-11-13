# Opening-range breakout (ORB) and "school run": pre-registration

Committed **2026-11-12, before any data was built or looked at.** The user asked to test a strategy from a short video: "minute chart, wait for the market open, mark the first range, break below → sell, break above → buy, stop on the other side of the range, take profit at 1:1". It includes Tom Hougaard's "school run" variation, plus a filter: if the entry candle does not close outside the range, exit for a small loss.

## Data, 2025-01 to 2026-10 only

- **Source:** Exness ticks. The ticks are built into 1-minute mid bars, each with its median spread.
- **Markets and opens:**

| Market | Exness symbol | Market open used | Forced exit if neither stop nor target is hit |
|---|---|---|---|
| DAX (Hougaard's market) | DE30m | 09:00 Europe/Berlin | 17:30 Berlin |
| S&P 500 | US500m | 09:30 America/New_York | 16:00 New York |
| Nasdaq 100 | USTECm | 09:30 New York | 16:00 New York |
| Gold | XAUUSDm | 08:20 New York (COMEX open) | 13:30 New York |
| US oil | USOILm | 09:00 New York (NYMEX open) | 14:30 New York |

- **Trading days:** weekdays where the market has bars covering the open and the range.

## Range definitions (4)

| Name | Range |
|---|---|
| R1 | the first 1-minute candle after the open |
| R5 | the first 5-minute candle after the open |
| R15 | the first 15-minute candle after the open |
| SCHOOL | the **second** 5-minute candle (open+5 to open+10 minutes), as in Hougaard's school run |

## Entry and exits

- **Entry:** after the range ends, the first 1-minute bar whose high goes above the range high is a **buy-stop fill at range high + half spread**. The first bar whose low goes below the range low is a **sell-stop fill at range low − half spread**.
  - One trade per day, on the first break.
  - If both sides break in the same bar, the day is skipped.
- **Stop:** the other side of the range.
- **Take profit:** 1:1, entry ± the range height.
- **Same bar:** if a bar touches both the stop and the target, the **stop counts first**.
- **Costs:** a half spread is added to the exit too. Results are shown at **1× and 2× the median spread** of the bar. Swap is 0, because every trade is intraday.
- **Time limit:** unresolved trades close at the forced-exit time, at that bar's mid.

**Two exit variants:**
- **X0:** the plain rule above.
- **XC (close filter):** if the range-sized candle in which the entry happened closes back **inside** the range, exit at that close. The candle is 1, 5 or 15 minutes, matching the range; SCHOOL uses 5.

## Evaluation

- **Periods:** development **2025**, holdout **Jan–Oct 2026**.
- **Combinations:** 5 markets × 4 ranges × 2 exits = **40**.
- **Unit:** R per trade (profit divided by range height), plus net R per year.
- **Random control:**
  - **Same days, same range height and same stop and target distances**, but entered at a **random minute** in the same session (between range end and forced exit − 30 min), in a **random direction**.
  - 500 draws, seed 20261112.
- **PASS needs all of:**
  - mean R per trade > 0 at **2× spread in both** development and holdout;
  - at least 100 holdout trades;
  - mean R **above the random 95th percentile in both** periods.
- **Multiple testing:** with 40 combinations, about 0.1 false passes are expected under this two-period bar.

## Consequences

- **PASS:** a frozen forward paper test may be set up separately.
- **FAIL:** the user is told the strategy did not survive costs and controls on 2025–26 data.
