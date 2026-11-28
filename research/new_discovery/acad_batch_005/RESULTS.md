---
title: Academic strategy batch 005 results
description: Intraday momentum, Bitcoin intraday momentum, overnight drift, pre-FOMC drift and turn of the month on Exness prices 2019-2026
sidebar_position: 2
---

# Academic batch 005 results (2026-11-18)

Rules: [`PREREG.md`](PREREG.md) (commit 5da5a503, before any computation). Script: `run_acad5.py`; numbers: `results.json`; Fed dates: `fomc_dates.json` (scheduled announcement days, from federalreserve.gov). 16 strategy × market tests; the pre-registration's "15" missed the gold turn-of-month line, which is listed in its table.

**Bottom line: 0 SCREEN-PASS, 15 REJECTED, 1 WATCH (turn of the month on gold).** No forward test follows.

## Net bp per trade after Exness spreads (TEST p in brackets)

| Strategy | Market | 2019-08→2022 | 2023→mid-2024 | mid-2024→mid-2025 | Jul 2025→now | Decision |
|---|---|---|---|---|---|---|
| **034 Intraday momentum** (last 30 min follows first 30 min) | S&P 500 | −7.0 | −2.2 | −1.9 | −0.7 (0.39) | REJECTED |
| | Nasdaq | −4.8 | −4.1 | −3.0 | +0.8 (0.10) | REJECTED |
| | Dow | −4.8 | −1.9 | −2.6 | −1.4 (0.93) | REJECTED |
| | DAX | −3.7 | −2.8 | −3.3 | −0.8 (0.49) | REJECTED |
| **035 BTC intraday momentum** | BTC | −11.8 | −9.2 | −10.0 | −12.5 (0.98) | REJECTED |
| **036 Overnight drift** (long close → next open) | S&P 500 | −0.6 | +0.1 | +2.6 | +5.4 (0.03) | REJECTED |
| | Nasdaq | −0.4 | +3.3 | +4.5 | +8.4 (0.03) | REJECTED |
| | Dow | +1.6 | −1.1 | −0.2 | +5.1 (0.03) | REJECTED |
| **037 Pre-FOMC drift** (24 h before the Fed) | S&P 500 | +31.3 | +10.4 | +40.0 | −14.9 (0.98) | REJECTED |
| | Nasdaq | +51.2 | +10.4 | +60.0 | −3.4 (0.79) | REJECTED |
| | Dow | +18.6 | +8.0 | +30.1 | −18.6 (0.89) | REJECTED |
| **038 Turn of the month** | S&P 500 | +28.4 | +32.6 | −42.7 | +69.0 (0.03) | REJECTED |
| | Nasdaq | +46.8 | +45.6 | −6.1 | +79.4 (0.09) | REJECTED |
| | Dow | +28.6 | +16.4 | −58.5 | +89.7 (0.02) | REJECTED |
| | BTC | +225.9 | −16.8 | −61.6 | +5.2 (0.42) | REJECTED |
| | **Gold** | +22.6 | +24.5 | +68.4 | +85.3 (0.13) | **WATCH** |

## Reading

- **Intraday momentum (Gao et al. 2018) has disappeared, or is smaller than the spread,** on every index and on BTC. The academic sample ended in 2013. The 30-minute moves are too small to pay an Exness spread, and BTC at 0.05% per side loses about 10 bp per trade.
- **Overnight drift** is positive in the last two to three periods for the S&P 500 and Nasdaq (+5 to +8 bp per night recently), but it was flat to negative in 2019–2022.
  - It also ignores swap. The break-even swap is about 3.7 bp per night (S&P 500) and 5.7 bp (Nasdaq) in TEST, and long index swaps are typically about 2 bp per night.
  - So it is not a pass, and its recent strength coincides with a strong 2025–26 rally.
- **The pre-FOMC drift** was strong through mid-2025: +31 to +60 bp per meeting, matching Lucca & Moench. **It reversed in the latest period** (−3 to −19 bp over 11 meetings). It has about 8 events a year, so it could never reach the 30-trade bar anyway.
- **Turn of the month:**
  - On the US indices it is positive in 3 of 4 periods but lost badly in mid-2024 → mid-2025.
  - **On gold it is positive in all four periods (WATCH),** at +23 to +85 bp per turn. But gold's ordinary 4-day returns were just as large in two periods (benchmark +28 and +90 bp). So most of it is gold's rally, not a month-end effect. The excess over normal days is positive in only 2 of 4 periods.
  - With 12 events a year it cannot be significant soon.
- **Checks:**
  - Fed meeting dates come from the official calendar, scheduled meetings only.
  - Prices are the actual Exness mid at each stated minute, and spreads are those quoted at that minute.
  - 2019-08 is the first month in the Exness archive.
