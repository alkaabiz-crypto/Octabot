# Robustness audit: positioning before the jobs report using ADP

This audits the study in PROTOCOL.md addendum 5. Its results (`reports/adp_preposition.json`) are kept unchanged. The audit plan was written into PROTOCOL.md before it ran. The code is `src/adp_robustness.py` and the numbers are in `reports/adp_robustness.json`.

## 1. Data and pairing

- **ADP figures.** Three calendar copies (Kaggle US 2015–2024, Kaggle global 2020–2025, Hugging Face 2020–2026) agree on 178 of 180 shared releases.
  - The exception is March 2023, where Kaggle US shows 145K and the other two show −53K. Either way it is a miss against the 200K forecast, so the sign used in the tests does not change.
  - The audit uses the Kaggle US value.
- **Jobs-report figures** agree on all 185 shared releases.
- **Pairing.** Matching each jobs report to the ADP report for the same reference month gives the same pairs as the original 0–7-day window, with no mismatches, plus 3 extra releases (123 against 120).

## 2. Does ADP predict the jobs-report surprise?

| Version | Same sign | 95% range | p (one-sided) | Rank correlation of sizes | Smallest hit rate detectable at 80% power |
|---|---|---|---|---|---|
| All, payrolls + unemployment (original definition) | 58/122 (48%) | 39–56% | 0.74 | −0.10 | 62% |
| All, payrolls only | 56/122 (46%) | 37–55% | 0.84 | −0.09 | 62% |
| Large ADP surprises (above median, more than 37K) | 26/60 (43%) | 32–56% | 0.88 | −0.20 | 66% |
| Largest third of ADP surprises | 18/41 (44%) | 30–59% | 0.83 | −0.25 | 71% |
| 2016–2019 | 27/47 (57%) | 43–70% | 0.19 | +0.18 | 69% |
| 2020–2026 | 31/75 (41%) | 31–53% | 0.95 | −0.18 | 66% |
| Excluding 2020 | 54/110 (49%) | 40–58% | 0.61 | −0.02 | 63% |

**What this supports.** A strong, stable link, with ADP getting the jobs-report surprise direction right about 62% of the time or more, is unlikely in this sample.

**What it does not rule out.** A weak link, below about 60%, cannot be excluded.

**One pattern worth noting.** The relationship looks different before and after 2020: positive in 2016–19 (57%, not significant) and slightly negative in 2020–26 (41%). ADP changed its method in 2022, and the economy after 2020 was unusual. The split is not significant, but it means one pooled number may hide two opposite periods.

## 3. Does trading before the release pay?

There were 192 variants: 4 markets × 12 entry/exit combinations × 4 versions (all, excluding 2020, large ADP surprises, reversed direction).
- Entries from 60 minutes to 1 minute before the release; exits 5, 15 or 60 minutes after.
- Real Exness bid/ask: tick data for 2016–19, 15-minute candles for 2020–26.
- R is twice the price range of the 45 minutes before entry.

**Results.**
- 49 of 192 variants had a positive mean.
- 3 had raw p ≤ 0.05, where luck alone would give about 10. None passed the multiple-testing correction.
- The textbook direction (ADP beat → expect a strong jobs report) did not pay in any version.

**The only consistent pattern is the reverse.** Gold in 2020–26, betting *against* the ADP signal from 15–60 minutes before the release to 60 minutes after, gave +0.38R to +0.45R per trade (72 trades, p 0.013–0.04). That matches the 41% hit rate above, but:
- it is 3 of 192 variants and fails the correction;
- the reversed direction was a sensitivity check, not a hypothesis;
- it covers one market and one period.

It is a **lead**: testable only on releases from December 2026 onward, with the rule written down first.

**Power.** At 80% power the trade tests could only detect average effects of about 0.5–1.0R per trade. Smaller real edges, such as +0.1–0.2R, would mostly not be detected.

## 4. Code review of `adp_preposition.py`

- **Risk unit, 2016–19.** The R window of "the hour before entry" was cut short to about 47 minutes, because the tick cache starts 61.7 minutes before the release. This is not look-ahead, but R is defined slightly differently in 2016–19 than in 2020–26. The audit uses 45 minutes everywhere.
- **Range expression.** The line computing the 2020–26 range is written in a way that only works by luck of operator precedence. The result is correct, because the empty case cannot occur there, but it is fragile. The audit code computes the range explicitly.
- **Forecast timing.** The jobs-report forecast in the calendar data has no timestamp. If it was updated after ADP was released, the test measures whether ADP adds anything *beyond* a forecast that already includes it. That is the right question for trading, but a different question from "is ADP informative at all".
- **Costs.** Only bid/ask is used, with no extra slippage. Spreads at the exit 5–15 minutes after release are as quoted. Real fills in fast markets could be worse, which would make the results less favourable, not more.

## 5. What has been disproven, and what remains untested

**Disproven within the tested scope** (2016–2026, Exness gold, EUR/USD, GBP/USD, USD/JPY):
- A strong link (a hit rate of about 62% or more) between ADP's beat or miss and the jobs-report surprise direction.
- Positioning 1–60 minutes before the jobs report in the textbook ADP direction, held to 5–60 minutes after, with average effects of about 0.5R per trade or more.
- In the earlier studies, for the specific rules tested:
  - entering after the release from 5 seconds onward, in the surprise direction, held 15–60 minutes, for these four markets;
  - following, fading or breaking out on the first 15–30 minutes, held 4 hours;
  - buying 24 hours before FOMC, CPI or NFP.

**Not disproven, because it was not tested, or tested with too little power:**
- **Weak effects.** ADP hit rates around 52–60%, or trade edges of +0.1–0.3R, which these sample sizes cannot detect.
- **Other predictors of the jobs report.** Weekly jobless claims, ISM and PMI employment indices, Challenger layoffs, the Conference Board labour differential, state data, "whisper" numbers and revisions.
- **Predictors for CPI.** For example the Cleveland Fed inflation nowcast against the consensus, PPI, import prices and used-car prices.
- **Other markets.** Bonds and rate futures, stock-index futures, the dollar index and options are not on Exness, and BTC and ETH were not tested with ADP.
- **Other designs.**
  - Sizing by surprise size.
  - Conditioning on market regime or on how the forecast moved before the release.
  - Volatility trades (straddles, which need options).
  - Holding periods longer than 4 hours (the post-release drift of days in the literature).
  - Pre-release positioning flows.
- **The 2020–26 contrarian pattern** on gold. It is a lead for a forward test, not evidence.
- **Whether a realistic setup can capture the first-second move.** This is the forward paper test in `live/`, with its first capture on 2026-12-04.

**Not claimed.** Neither this audit nor the earlier studies show that trading after the release is profitable for a retail trader, or that the first second is the only possible source of an edge. They show only that, among the rules tested, the first second was the only window with a measurable edge.
