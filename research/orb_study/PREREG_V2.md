# ORB, second interpretation set: pre-registration

Committed **2026-11-12, after the user questioned the first test and before running this one.** Same data, costs, development/holdout split, random control and PASS bar as `PREREGISTRATION.md`. Any PASS must also be confirmed at tick level, as in `VERIFY_PREREG.md`.

## What changes

**1. Close-confirmation entry (CLOSE).** This replaces entering the moment the range is touched.
- **Signal:** wait for a range-sized candle (1, 5 or 15 minutes, aligned to the end of the range; SCHOOL uses 5) to **close** above the range high to buy, or below the range low to sell.
- **Fill:** at the **open of the next 1-minute bar**, plus or minus the half spread.
- **Stop:** the other side of the range.
- **Take profit:** a true 1:1 from the actual entry, so the target equals the entry ± (entry − stop).
- **No close filter**, since entry already needs a close outside the range.

**2. Extra market opens,** tested with **both** touch entry (TOUCH, with X0 and XC exits as before) and CLOSE entry:

| Key | Market | Open | Forced exit |
|---|---|---|---|
| XAU_NY0930 | gold | 09:30 New York (stock open) | 16:00 New York |
| OIL_NY0930 | US oil | 09:30 New York | 16:00 New York |
| XAU_LDN0800 | gold | 08:00 Europe/London (London open) | 16:30 London |

**3. CLOSE entry also on the five original opens** (DAX 09:00 Berlin, S&P and Nasdaq 09:30 New York, gold 08:20 New York, oil 09:00 New York).

## Size of the test

- **Ranges:** R1, R5, R15 and SCHOOL, as before.
- **Combinations:** 8 opens × 4 ranges × CLOSE = 32, plus 3 new opens × 4 ranges × TOUCH × (X0, XC) = 24, for a total of **56**.
- **Multiple testing:** a pass must clear the bar in **both** periods, so about 0.15 false passes are expected.
- **Random control:** the same as before, with the stop and target distance set to the actual risk distance of each trade.
