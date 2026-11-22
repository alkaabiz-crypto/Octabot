# DCA mix study: results

The rules were fixed in `PREREGISTRATION.md` (commit `bfdec811`) before running.
- **Plan:** 10 USD bought on every trading day from Jan 2025 to Oct 2026, with a 0.1% fee and no selling.
- **Prices:** Exness daily closes for the S&P 500, Nasdaq, gold and silver, and Binance for BTC.

## Results

| Plan | Put in | Final | Profit | Worst point vs money put in | Max drop (unit value) | Worst half-year (fresh start) |
|---|---|---|---|---|---|---|
| S&P 500 | 4,730 | 5,400 | **+14.2%** | −14.8% | −18.9% | −0.9% |
| Nasdaq 100 | 4,720 | 5,689 | **+20.5%** | −17.2% | −22.9% | −0.1% |
| Gold | 4,730 | 4,817 | +1.8% | −0.4% | −28.5% | −14.2% |
| Bitcoin (7 days a week, so more days) | 6,690 | 6,050 | −9.6% | −36.5% | −53.0% | −19.8% |
| **50% S&P / 50% gold** | 4,720 | 5,099 | **+8.0%** | **−5.6%** | **−14.1%** | **−4.6%** |
| 40% S&P / 40% gold / 20% BTC | 4,720 | 4,929 | +4.4% | −7.8% | −15.5% | −7.2% |
| Equal 5 (S&P, Nasdaq, gold, silver, BTC) | 4,710 | 5,098 | +8.2% | −10.3% | −26.1% | −7.6% |

## Pre-registered hypotheses

- **H1, PASS:** every mix had a smaller max drop than the average single market. The mixes ranged from −14.1% to −26.1%, against −30.8% for the average single market.
- **H2, PASS:** every mix had a better worst half-year than the average single market. The mixes ranged from −4.6% to −7.6%, against −8.8%.

## What this means

- **Diversifying is the one thing that reliably helped in every test.** Unlike the timing rules, it does not depend on predicting anything.
  - **50/50 S&P 500 and gold** had the **smallest drops** of every plan, and its worst point was only −5.6% below the money put in.
  - It made less than pure Nasdaq or S&P. That is the trade-off, not a flaw.
- **Which single market "won" is hindsight:**
  - Nasdaq won in this window.
  - Gold DCA made only +1.8%, because buying continued through gold's 2026 fall (its worst half-year was −14%).
  - BTC lost.
  - The next 22 months can rank them differently. Mixing protects against picking the wrong one.
- **How to hold it:** use **spot** products, such as an S&P 500 ETF, a gold ETF or physical gold, and spot BTC, with no leverage.
  - **CFDs are a poor fit for long-term holding.** Exness CFDs on indices charge overnight swap every night, which this study did not deduct. Over months, that cost adds up.

Files: `study.py`, `results/results.json`.
