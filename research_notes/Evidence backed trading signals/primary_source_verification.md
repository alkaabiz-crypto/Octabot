# Primary-source verification of evidence-backed trading signals (gold, US indices, oil, crypto)

Method note (2026-11-10): primary documents were downloaded directly (arXiv PDFs, Quantpedia article HTML and table images, BIS WP 1087 PDF, EIA schedule page). Some hosts still could not be reached from this session. **papers.ssrn.com** returns a Cloudflare "Just a moment..." challenge to scripted clients, so no SSRN abstract or PDF could be read. **cxoadvisory.com without www** and the mirrors aqr.com, fairmodel.econ.yale.edu, oxfordstrat.com, thechartist.com.au, concretumgroup.com, abarbon.com, etf.com, c.mql5.com and ir.eia.gov were refused by the proxy. www.cxoadvisory.com loaded, but its articles stop at a paywall after the setup paragraph. Anything that depends on those hosts is marked **UNVERIFIED**.

## 1. arXiv 2511.08571 "Forecast-to-Fill" (gold futures 2015–2025): rules and results

### Takeaway
The paper describes a fully specified long-only daily trend/momentum rule on COMEX gold, but its headline numbers do not hold together. The "Sharpe 2.88 / 43% CAGR" headline comes from a strategy with 0.91% realized volatility (2.65% CAGR), and the 43% figure is simply that result scaled up to 15% volatility. The paper's own cost-stress table gives a Sharpe of 0.94 at baseline costs, not 2.88. The fill-timing assumption also contradicts itself between sections. Treat it as a rule template, not as evidence of a 2.9 Sharpe.

### Cited Findings
- **Authors and date:** Singha, Aguilera-Toste and Lahiri, arXiv:2511.08571v1 [q-fin.TR], 11 Nov 2025. 21 pages. Not peer-reviewed. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Data and walk-forward design (Sec. 2.1–2.2):** daily LBMA/COMEX settlement prices through 16 Sep 2025, with OOS extended to 31 Oct 2025. Each fold trains on 10 years and tests on the next 6 months. The first OOS window starts Jan 2015, so 2005–2025 data are used, giving 2,793 OOS trading days. The appendix says the strategy trades CME GC continuous front-month, rolled 2 business days before first notice. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Exact signal (Sec. 3.2–3.5, 6.2–6.3):**
  - Compute the EMA of log price, ỹt = λỹt−1 + (1−λ)log Pt. The paper **never states the value of λ**; it is "estimated on training".
  - Take the slope Δỹt and z-score it with training-window mean and standard deviation. Clip z to ±3 and map it to p_trend = (z̄+3)/6.
  - Momentum flag m = 1{Pt/Pt−50 > 1}, i.e. **K = 50 days**.
  - Combine: p_bull = 0.6·p_trend + 0.4·m.
  - **Enter long if p_bull ≥ 0.52 and Δỹt > 0.** The strategy is long-only.
  — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Exits (Sec. 6.3):** a position exits on any of the following:
  - a hard stop at entry − 2×ATR14;
  - a trailing stop at the running peak − 1.5×ATR14;
  - a 30-trading-day timeout;
  - p_bear > 0.50, which halves or closes the position.
  — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Sizing (Sec. 2.4, 4):**
  - EWMA volatility forecast scaled to a 15% annual target, with leverage capped at Wmax = 2.0.
  - Weight multiplied by (p_bull − 0.5)/0.5.
  - Friction-adjusted Kelly fraction × 0.40, with a floor of 25% of the volatility budget when Kelly is about 0.
  - Mean absolute weight is about 0.033, so the strategy is usually almost flat.
  — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Cost assumptions (Sec. 2.3):** a round trip costs k = 0.7 bp, plus square-root impact with γ = 0.02. Overnight funding is ignored (Limitations section). — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Headline OOS results (Sec. 8.1):**
  - Annual return 2.62%, volatility 0.91%, Sharpe 2.88, CAGR 2.65%, max drawdown 0.52%, Calmar 5.11.
  - 1,282 entries, 1,132 non-zero-exposure days.
  - Bootstrap 95% CI for the Sharpe [2.49, 3.27].
  - On active days: hit rate 65.81%, payoff ratio 1.49×, +2.58 bp per active day.
  - "At 15% volatility, the CAGR is 43%." This is a linear rescale, not a traded result.
  — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Sub-periods (Table 1, Sec. 11.1):** these windows are nested, so they are not independent OOS tests.

  | Period | Sharpe | Max drawdown |
  |---|---|---|
  | 2015–2025 | 2.88 | 0.52% |
  | 2019+ | 2.93 | 0.47% |
  | 2022+ | 2.91 | 0.47% |

  The paper reports **no decay**. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Regime attribution (Table 2):** bull days (p_bull > 0.55) have Sharpe 3.82 over 1,628 days; bear days have Sharpe −0.02 over 1,116 days. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Cost stress (Table 3, Sec. 12.1) contradicts the headline:**

  | Cost multiplier | Sharpe |
  |---|---|
  | 0.5× | 1.907 |
  | 1.0× | 0.937 |
  | 1.5× | −0.033 |
  | 2.0× | −1.004 |

  The text nevertheless says that at 1.0× "the Sharpe ratio remains well above 2.5" and that 2.0× is "close to zero". — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Fill timing contradicts itself:**

  | Fill timing | Sharpe | Max drawdown |
  |---|---|---|
  | T+0 | 2.88 | 0.52% |
  | T+1 | 2.28 | 0.63% |
  | T+2 | 2.24 | 0.56% |

  The appendix says the baseline is "filled at t+1 close (T+1 baseline)", but the 2.88 headline is the T+0 row. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)
- **Data-snooping disclosure:** a grid of 64 configurations (EMA decay, momentum K, activation threshold) was tested. The stationary-bootstrap SPA test gives p < 0.001. Reversing the signal gives a Sharpe of −2.95. — [arXiv PDF](https://arxiv.org/pdf/2511.08571)

### Inferences
- The only parts of the rule that can be copied are K = 50 momentum, the 0.52 threshold, 2/1.5 ATR14 stops and the 30-day timeout. λ is unspecified, so the slope leg cannot be reproduced exactly.
- The 0.7 bp round-trip cost suits institutional GC futures. It is far below retail XAUUSD CFD spreads, which are typically several bp or more (background knowledge, not verified here). Since Sharpe already falls to about 0 at 1.5× the paper's own costs, the edge would very likely disappear at CFD costs.
- **Correction to gold.md:** gold.md lines 26/164/184 say the content is "unknown". It is now known, and should be read as weak evidence because the paper contradicts itself.

### Gaps
- The value of λ and the yearly non-overlapping tables are promised in "companion materials" that were not found.

## 2. Baur et al. gold timing (Quantpedia summary and data-snooping test): which technical rules survived, with lookbacks

### Takeaway
All rules are **monthly** long-gold/cash switches. The best technical rules were 24-month time-series momentum (MOM24) and price above its 36- or 48-month MA (MA1-36, MA1-48). Even these only marginally survive data snooping. The plain SPA p-value for technical rules in the absolute-return test is 0.079 (bullion) and 0.066 (COMEX), so the family test does not reject at 5%. The step-SPA(3) test identifies 3 outperforming technical strategies. Seasonal and fundamental rules fail clearly.

### Cited Findings
- **Source:** the Quantpedia page summarises the SSRN working paper (Bartsch, Baur, Dichtl, Drobetz, "Investing in the Gold Market: Market Timing or Buy-and-Hold?", SSRN 3202658). The evaluation period is **January 1990 to December 2015**. — [Quantpedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)
- **Technical rule set:**
  - **MA rules:** long if the short MA (s = 1, 2, 3 months) is above the long MA (l = 9, 12 months), plus s = 1 with l = 10, 24, 36, 48 months. That gives 10 MA rules.
  - **TSMOM rules:** long if the past k-month return is positive, with k = 1, 3, 6, 9, 12, 24, 36, 48. That gives 8 rules, for **18 technical rules in total**.
  - Fundamental: 15 rules, built from 11 predictors plus the mean and kitchen-sink forecasts.
  - Seasonal: all 2^12 monthly in/out combinations, 4,095 tested.
  — [Quantpedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)
- **Table 3 (traditional backtest, mean monthly return in %):**

  | Strategy | Bullion | COMEX |
  |---|---|---|
  | MOM24 | 0.611 | 0.614 |
  | MA1-36 | 0.607 | 0.604 |
  | MA1-48 | 0.600 | 0.602 |
  | MOM12 | 0.543 | 0.542 |
  | Buy-and-hold | 0.313 | 0.310 |

  Monthly Sharpe ratios on bullion: MOM24 0.099, MA1-36 0.098, MA1-48 0.097, buy-and-hold 0.015. — [Quantpedia, Table 3 image](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)
- **Table 4 (SPA test, absolute returns):**

  | Strategy family | Price series | Best rule | Nominal p | SPA p | Step-SPA(3) survivors |
  |---|---|---|---|---|---|
  | Technical | Bullion | MOM24 | 0.0173 | 0.0789 | 3 |
  | Technical | COMEX | MOM24 | 0.0140 | 0.0656 | 3 |
  | Seasonal | Bullion | SEA3190 | — | 0.7847 | none |
  | Seasonal | COMEX | SEA2302 | — | 0.8213 | none |
  | Fundamental | Bullion | KSF | — | 0.2705 | none |
  | Fundamental | COMEX | KSF | — | 0.2443 | none |

  — [Quantpedia, Table 4 image](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)
- **Mechanism (authors):** the winning rules "shift out of the gold market following a prolonged trend of negative gold market returns". The authors attribute this to behavioural biases. — [Quantpedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)

### Inferences
- The three step-SPA survivors are most likely MOM24, MA1-36 and MA1-48, the top three in Table 3. The table does not name them, so this is **UNVERIFIED**.
- These are very slow, monthly rules: price above a 36- or 48-month MA, or a positive 24-month return. They say nothing about intraday or daily gold rules.
- **Correction to gold.md:** the note says the IRFA 2020 abstract concludes the results "are not…". The working-paper abstract says the results are "robust to data-snooping biases only for selected technical trading strategies". Even that is borderline at 5% in Panel A (SPA p ≈ 0.066–0.079).

### Gaps
- Panel B of Table 4 (Sharpe-based SPA) is cropped in the image.
- The published IRFA vol. 71 (2020) version could not be checked against the working paper (ScienceDirect and SSRN were not reachable). The sample or results may differ.
- Transaction costs are not stated on the Quantpedia page.

## 3. Quantpedia "Trend-following and Mean-reversion in Bitcoin" (MAX/MIN) and the 2024 revisit

### Takeaway
The rule is: be long BTC for the next day when today's price equals its x-day maximum (MAX) or minimum (MIN), with x from 10 to 50. In the true out-of-sample window (4 Feb 2022 to 20 Aug 2024) MAX kept working but MIN did not. In that window **the 20-day MAX beat the 10-day**, which contradicts the "10 days works best" claim if applied to the OOS. No transaction costs are reported.

### Cited Findings
- **Original study (15 Mar 2022, Padyšák and Vojtko):**
  - Data: Gemini daily BTC, 26 Nov 2015 to 3 Feb 2022, including weekends.
  - MAX/MIN computed over the previous 10/20/30/40/50 days.
  - Shorter lookbacks are best.
  - The combined "at MAX or at MIN" strategy (10-day) returned 98.43% a year, with 47.75% volatility, −37.67% max drawdown and Ret/Vol 2.06. BTC itself had 74.35% volatility and −83.65% max drawdown.
  - The page states no costs.
  — [Quantpedia 2022](https://quantpedia.com/trend-following-and-mean-reversion-in-bitcoin/)
- **Holding period:** the original says "the risk lies in the negative return the following day". The revisit defines r_t,x as the BTC return on the day the condition holds. Together these imply a **one-day hold, re-evaluated daily**. — [Quantpedia 2022](https://quantpedia.com/trend-following-and-mean-reversion-in-bitcoin/); [Quantpedia 2024](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/)
- **Revisit (12 Sep 2024, Beluska):**
  - Data: Gemini daily **open prices at 00:00 UTC**, 9 Oct 2015 to 20 Aug 2024.
  - Full-sample results are "slightly less effective" than the original, with 10-day still the best.
  - **OOS = 4 Feb 2022 to 20 Aug 2024.** In the OOS, MAX "remains alive"; "buying the BTC when it reaches a 10-days maximum appears to be less effective than buying at a 20-days maximum". MIN gave "low or even negative returns".
  - No significant day-of-week effect on MAX/MIN was found.
  - The tables are images, and the OOS numbers are not in the text.
  — [Quantpedia 2024](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/)
- **Source paper:** Padyšák and Vojtko, "Seasonality, Trend-following, and Mean reversion in Bitcoin", SSRN 4081000. — [Quantpedia strategy page](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)

### Inferences
- **Correction to crypto.md line 147:** the crypto.md recipe "exit on a close below the 10-day low or SMA" is not the Quantpedia rule. The published rule is a next-day hold, re-checked every day. Any trailing-exit variant is an untested modification.
- **Correction to crypto.md line 18:** "10 days works best" is true in-sample only. In the OOS the 20-day MAX did better.
- The rule holds one day at a time and may flip often, so turnover is high. With fees not modelled, the headline returns are gross.

### Gaps
- The numeric OOS returns, volatility and drawdown per lookback are only in images, which were not extracted.
- The cost-adjusted performance has not been published.

## 4. Quantpedia Bitcoin intraday seasonality (21:00–23:00 UTC) and its 2023 update

### Takeaway
The rule is: buy BTC at 21:00 UTC and sell at 23:00 UTC, every day. Original 2015–Feb 2022 results: 33% a year, 20.93% volatility, −22.45% max drawdown. The Sep 2023 update (to Jun 2023) reports 40.64% a year and −22.7% max drawdown, but admits "a rough period in 2022 and 2023". Filtering to high-volatility days gives 37.26% a year and −18.87% max drawdown. No costs are reported. Quantpedia's own pages disagree on the entry hour and the max drawdown.

### Cited Findings
- **Original (18 Feb 2022):**
  - Data: Gemini hourly, 9 Oct 2015 to 3 Feb 2022, UTC.
  - The returns for the 22:00 and 23:00 hourly bars are the largest and statistically significant at 5%. No hour is significantly negative.
  - Rule: "buy Bitcoin at 21:00 (UTC +0) and sell it at 23:00".
  - Result: annual return 33%, volatility 20.93%, max drawdown −22.45%.
  — [Quantpedia 2022](https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/)
- **Update (13 Sep 2023):**
  - Sample extended to 30 Jun 2023, same rule.
  - Annual return 40.64%, max drawdown −22.7%, Calmar 1.79.
  - Friday was the best day, then Thursday.
  - Restricting to uptrend days (price above its 10/20/50/200-day MA at 00:00 UTC) strengthens the pattern.
  - Restricting to **high-volatility days** (30-day hourly volatility above its 365-day moving median) gives 37.26% a year, −18.87% max drawdown and Calmar 1.97.
  — [Quantpedia 2023](https://quantpedia.com/the-seasonality-of-bitcoin/)
- **Quantpedia's own pages disagree:**
  - The screener page says "open a long position in the BTC at 22:00 (UTC +0) and hold it for two hours".
  - It lists max drawdown −34.04% and Sharpe 1.58 for 2015–2021.
  - It states "Transaction costs: Not Reported".
  — [Quantpedia strategy page](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin)

### Inferences
- The blog's convention is that the "22:00 return" is the 21:00→22:00 bar. Under that convention, a 21:00→23:00 hold captures the 22:00 and 23:00 bars. The screener's "22:00 entry" is probably an error in the screener description, and builders should use 21:00–23:00 UTC entries.
- The rule makes one round trip a day, about 365 a year. At 5 bp a side that costs about 36% a year (my arithmetic), similar in size to the gross return. After-cost viability is doubtful except at maker-fee levels.
- The figures come from a single exchange (Gemini) and are practitioner research, not peer-reviewed.

### Gaps
- No post-June-2023 update was found.
- Results for the uptrend-filter variant are in an image table that was not extracted.

## 5. BIS "Crypto carry" (WP 1087): how the futures basis predicts crashes; usable thresholds

### Takeaway
The paper gives **no trading threshold**. It reports continuous predictive regressions. In price units, a $1 higher basis predicts about a $5 (1-month) to $10 (3-month) lower spot price at expiry. A 10% rise in carry predicts a 44% rise in short-futures liquidations the next month. High carry also predicts more negative skew and higher volatility. A cash-and-carry on CME has Sharpe about 0.6 before costs. Use it as a continuous de-risking overlay. Any cut-off (for example carry above 20–40% a year) would be the builder's own, untested choice.

### Cited Findings
- **Version:** BIS WP 1087, published 4 April 2023, "This version: March 24, 2023", 54 pages. The BIS landing page shows only the April 2023 date. — [BIS PDF](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf); [BIS page](https://www.bis.org/publications/working-paper-1087-crypto-carry)
- **Data and stylised facts:**
  - Basis data from Skew, annualised, constant 1- and 3-month maturities, across Binance, OKEx, FTX, Huobi, BitMEX, Deribit and CME.
  - Main sample **April 2019 to January 2022**.
  - Average carry is about 10% a year (10–11% for OKEx/CME), peaking at up to 60% a year. Spikes above 40% occurred in early 2020 and March 2021 and collapsed quickly.
  - Cross-exchange correlation is above 90%; CME's correlation with the crypto-native exchanges is only 60–70%.
  — [BIS PDF, Sec. 1–2](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf)
- **Predictive regressions (Eq. 3–4, Fig. 3):** S_T − S_t = α + β1(F − S) and F_t,T − F_T,T = α + β2(F − S).
  - Higher carry predicts lower spot **and** lower futures prices at expiry, with |β2| > |β1|.
  - For 1-month BTC: $1 more basis predicts a ~$5 drop in spot and a ~$6 drop in futures.
  - For 3-month contracts the coefficients are above 10, about −$10 spot and −$11 futures.
  - The 1-month estimates are less statistically significant, and CME 1-month is insignificant.
  — [BIS PDF, Sec. 2.4.1](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf)
- **Liquidations (Table 6):** "a rise in carry by 10% predicts 44% increase in total sell liquidations (relative to total open interest) over the next month". Carry predicts only short liquidations, not long ones. — [BIS PDF, Sec. 3.3](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf)
- **Crash risk (Sec. 3.4, Table 7):** "a higher carry predicts lower (more negative) skew of BTC, and ETH returns". It also predicts higher realised and implied volatility. — [BIS PDF](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf)
- **Cash-and-carry returns (Table 5):**
  - Tested on CME 1-month BTC, over 2018–2022 and 2019–2022.
  - The futures leg returns 3–4% a month with about 25% monthly volatility and strong negative skew.
  - At 10× leverage, the short-futures leg would have been liquidated in more than half the months.
  - The cash-and-carry Sharpe is about 0.6 "before transaction costs and financing spreads".
  — [BIS PDF, Sec. 3.3](https://www.bis.org/publications/working-paper-1087-crypto-carry.pdf)

### Inferences
- A usable rule built from this paper would be a continuous, monotone de-risking schedule, for example scaling down long exposure as annualised 1–3-month basis or funding rises above its historical average of about 10%. The paper does not test any such rule, so this is a hypothesis.
- The regressions are on overlapping horizons up to expiry, in levels, within a 2019–2022 boom/bust sample. They are not an out-of-sample trading backtest.
- **Correction to crypto.md line 78:** "revised Oct 2025; CEPR DP 20719" was **not confirmed**. The BIS PDF and landing page show only the March/April 2023 version. The other figures in crypto.md (10% a year average, above 40%, up to 60%) match the source.

### Gaps
- No post-2022 or post-ETF evidence is in this paper.
- If a 2025 revision exists, it was not reachable here.

## 6. Bouchaud et al. 2026 (fast-trend decay) and Hurst–Ooi–Pedersen "Century of Evidence"

### Takeaway
Kurth, Eisler, Rej and Bouchaud (arXiv 2607.01550, 2 Jul 2026) show the Sharpe of an EWMA-crossover trend portfolio across about 100 futures falling from about 0.84 (1995–2009) to 0.12 (2009–2025) at the fastest speed. The slowest speed falls from 0.70 to 0.40. Equity indices and FX are where trend "effectively vanished", because they sit in the **small-tick** tier. This contradicts the earlier inference that ES/NQ would be spared. Hurst–Ooi–Pedersen full text could not be reached.

### Cited Findings
- **Signal and portfolio (Sec. 2, Eq. 1–2):**
  - Signal = EWMA_τ(price) − EWMA_4τ(price), normalised by its 16τ exponentially weighted standard deviation and clipped at ±2.
  - "Equal-risk" position = signal / σ, where σ is the 16τ EWMA of absolute daily price changes.
  - There is also a liquidity-weighted version.
  - Universe: 101 futures in four sectors, daily settlement prices. The contract list is in Appendix A.
  — [arXiv PDF](https://arxiv.org/pdf/2607.01550)
- **Table 1 Sharpe ratios:**

  | Signal | 1995–2009 | 2009–2025 |
  |---|---|---|
  | EWM-5-20 | 0.84 ± 0.27 | 0.12 ± 0.24 |
  | EWM-10-40 | 0.83 ± 0.27 | 0.22 ± 0.24 |
  | EWM-20-80 | 0.79 ± 0.27 | 0.27 ± 0.26 |
  | EWM-50-200 | 0.70 ± 0.27 | 0.40 ± 0.26 |

  The break is "abrupt", with "no recovery". The five-year rolling Sharpe of EWM-5-20 falls from 1–2.5 historically to roughly zero after 2010. — [arXiv PDF, Sec. 3.1–3.2](https://arxiv.org/pdf/2607.01550)
- **By sector (Fig. 4, Sec. 3.3):** "Trend has effectively vanished for IDX and FXR, while YLD and CMD show no appreciable degradation." — [arXiv PDF](https://arxiv.org/pdf/2607.01550)
- **By tick size (Sec. 5.2):**
  - Contracts are split at the median of tick/volatility each month.
  - Small-tick contracts: Sharpe about 0.8 before the break, about 0 after.
  - Large-tick contracts: about 1.4 before, 1.0–1.2 after.
  - The asset-class pattern is "a downstream symptom of the clustering of IDX and FXR in the small-tick tier and of YLD and most CMD in the large-tick tier."
  - Small-tick contracts in low-volatility regimes still earn.
  — [arXiv PDF](https://arxiv.org/pdf/2607.01550)
- **Costs:** zero-lag execution "produces equally flat post-2008 returns, even without costs". Square-root impact at CTA scale explains only about 0.1 of Sharpe drag (Appendix B). The decay is in the signal itself, not in costs. — [arXiv PDF, Sec. 4.1](https://arxiv.org/pdf/2607.01550)
- **Universe:** it includes SPMINI, NSDQMINI, DJMINI, RUSSELLMINI, GOLD0, SILVER0, CRUDE0, WTICRUDE0 and BRENT0. — [arXiv PDF, App. A](https://arxiv.org/pdf/2607.01550)
- **Hurst–Ooi–Pedersen:** the AQR-hosted copy and all mirrors were blocked. The specification in the existing notes (oil_commodities.md, line 29) (equal-weight 1/3/12-month TSMOM, volatility-scaled, 2-and-20 fees plus asset-class costs, 67 markets, 1880–2016) remains **UNVERIFIED** against the primary text. — [AQR (blocked)](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)

### Inferences
- **Correction to us_indices_dollar.md line 21:** the note says "ES/NQ are large-tick contracts, so the Bouchaud et al. finding may hurt US equity index futures less". The paper says equity indices cluster in the **small-tick** tier, and that index trend has "effectively vanished". Fast trend on US indices is the worst case, not the best.
- Gold, crude and most commodities are mostly in the large-tick tier and CMD shows "no appreciable degradation". Fast and medium trend on gold and oil is therefore better supported than on indices. This is inferred from the sector result, because individual contract tiers are not tabulated.
- The table reports pre/post Sharpe ratios with standard errors of about ±0.25, so the post-2009 slow-signal figure of 0.40 is only marginally significant.

### Gaps
- Exact per-contract tick tiers are not tabulated.
- The Hurst et al. construction and net Sharpe could not be retrieved (aqr.com, fairmodel.econ.yale.edu and trendfollowing.com need to be allowed).

## 7. Zarattini, Pagani & Barbon (2025) "Catching Crypto Trends": exact rule and after-fee results

### Takeaway
The rule is a long-only Donchian ensemble over nine lookbacks from 5 to 360 days. Entry is a close above the N-day maximum close. The exit is a ratcheting trailing stop at the midpoint of the N-day max and min closes. Positions are sized to 25% target volatility with leverage capped at 200%. Reported: about 18% net CAGR and about 11% net alpha versus BTC at 0.10% costs (Jan 2015 to mid-Mar 2025), and Sharpe above 1.5. These details come from CXO's paraphrase and search abstracts because SSRN was not reachable. They are secondary but specific.

### Cited Findings
- **Rule (CXO paraphrase of the April 2025 paper):**
  - Lookbacks: 5, 10, 20, 30, 60, 90, 150, 250, 360 days.
  - Entry: open a position when the daily close crosses above that lookback's maximum close.
  - Exit: daily trailing stop = max(prior stop, midpoint of the lookback's max and min closes).
  - Sizing: 25% / annualised 90-day standard deviation, leverage capped at 200%.
  - Each day, form an equal-weight ensemble across the lookbacks.
  - Universe: coins listed for at least 1 year with median daily volume of at least $2M over the prior 30 days, top 20 by liquidity.
  - Costs of 0.10%, 0.25% and 0.50% were tested.
  - Data: 21,616 assets, Jan 2010 to mid-Mar 2025.
  — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/)
- **Results:** 18% net CAGR and 11% annualised net alpha versus BTC buy-and-hold, Jan 2015 to mid-Mar 2025, at 0.10% costs, with monthly rebalancing. — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/)
- **Identifiers:** Swiss Finance Institute RP 25-80, SSRN 5209907, 38 pages, dated 2025-10. The abstract reports "Sharpe ratio above 1.5 and an annualized alpha of 10.8% vs Bitcoin … net of fees". — [RePEc/IDEAS](https://ideas.repec.org/p/chf/rpseri/rp2580.html)

### Inferences
- The "net Sharpe above 1.5" claim in crypto.md is consistent with this source.
- crypto.md line 148 suggests lookbacks of 10/20/50/100. The actual published set is 5–360 with a midpoint trailing stop, so the recipe should be updated to that.
- Results at 0.25% and 0.50% costs, and any decay, are behind the CXO paywall and SSRN.

### Gaps
- Net results at higher costs, a BTC-only Sharpe, and 2022–2025 sub-period results remain **UNVERIFIED**.

## 8. Faber 10-month SMA follow-up; Gao et al. intraday momentum; 2026 turn-of-month update

### Takeaway
The Faber 2018 "Revisited 10 Years Later" figures and the Gao et al. (JFE 2018) figures could not be checked against primary text, because SSRN, JPM and the mql5 mirror were unreachable. Quantpedia's Aug 2026 study is not an index turn-of-month update. It is a **sector-momentum** intramonth cycle, it is gross of costs, and it reports Sharpe ratios of about 0.55. Quantpedia's index TOM screener entry still cites 1926–2005: 7.2% a year, Sharpe 1.04, costs "Not Reported".

### Cited Findings
- **Index TOM (Quantpedia screener):**
  - Rule: "Buy SPY ETF 1 day (some papers say 4 days) before the end of the month and sell the 3rd trading day of the new month at the close."
  - Backtest 1926–2005: 7.2% a year (annualised daily return 0.15%), volatility 6.9%, Sharpe 1.04, max drawdown −20.79%.
  - Transaction costs "Not Reported".
  - Robustness includes the 1987–2005 post-discovery holdout.
  — [Quantpedia TOM](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)
- **Quantpedia "Sectoral Intramonth Momentum Cycle" (17 Aug 2026):**
  - Data: 9 SPDR sector ETFs and SPY, 22 Dec 1998 to 30 Jun 2026.
  - Ranking: 252-day total return at month-end; top 3 versus bottom 3 (Strat2), or top 3 versus SPY (Strat1).
  - The legs and results:

  | Leg | Strat2 return / Sharpe / max drawdown | Strat1 return / Sharpe |
  |---|---|---|
  | Long momentum on day D+1 | 2.83% / 0.42 / −14.85% | 0.23% / 0.15 |
  | Reversed momentum on D+2 and D+3 | 3.26% / 0.46 | — |
  | Momentum from D−10 to D−5 | 1.35% / 0.32 | — |
  | Composite | 5.99%, 10.87% vol, Sharpe 0.55, max drawdown −21.72% | 3.77% / 0.54 |

  - Costs are not modelled. The authors only claim Sharpe 0.55 is "within the range that survives realistic transaction costs".
  — [Quantpedia 2026](https://quantpedia.com/sectoral-intramonth-momentum-cycle/)

### Inferences
- The sector study is in-sample over the full period. Its three legs are motivated by prior literature, but the windows were chosen on the same data.
- It is not directly usable for index CFDs. It does suggest the index TOM window, D−1 to D+3, overlaps sector flows on D+1 to D+3.
- The Faber "0.45 → 0.80 Sharpe" figure in us_indices_dollar.md stays secondary (Swedroe). A search summary of the same Swedroe piece also gives "return from 9.8% to 11.3%" for the multi-asset version. Neither could be confirmed.

### Gaps
- Faber JPM 2018 tables: **UNVERIFIED** (SSRN 962461 / jpm.iijournals.com unreachable).
- Gao, Han, Li and Zhou JFE 2018, including the OOS R² of 1.2–1.4% and the cost claims: **UNVERIFIED** (SSRN 2440866 and the mql5 mirror were blocked, and the www-less CXO host was refused).
- No 2026 Quantpedia update of the plain index TOM effect was found.

## 9. EIA weekly inventory release timing (for oil event rules)

### Takeaway
The Weekly Petroleum Status Report is released at **10:30 a.m. ET on Wednesday**. Holiday weeks shift it, usually to **Thursday, and usually at 12:00 p.m. ET**, not 10:30. An event rule must use EIA's published exception calendar rather than a fixed "Wednesday 10:30" assumption.

### Cited Findings
- "The standard release time and day of the week will be at 10:30 a.m. eastern time on Wednesday with the following exceptions. All times are eastern." — [EIA WPSR schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php)
- **Exceptions, 2025–2026 (week ending → release):**

  | Holiday | Week ending | Release | Time (ET) |
  |---|---|---|---|
  | New Year | 27 Dec 2024 | Thu 2 Jan 2025 | 11:00 a.m. |
  | MLK Day / Inauguration | 17 Jan 2025 | Thu 23 Jan 2025 | 12:00 p.m. |
  | Presidents' Day | 14 Feb 2025 | Thu 20 Feb 2025 | 12:00 p.m. |
  | Memorial Day | 23 May 2025 | Thu 29 May 2025 | 12:00 p.m. |
  | Labor Day | 29 Aug 2025 | Thu 4 Sep 2025 | 12:00 p.m. |
  | Columbus Day | 10 Oct 2025 | Thu 16 Oct 2025 | 12:00 p.m. |
  | Veterans Day | 7 Nov 2025 | Thu 13 Nov 2025 | 12:00 p.m. |
  | Christmas | 19 Dec 2025 | **Mon 29 Dec 2025** | **5:00 p.m.** |
  | MLK Day | 16 Jan 2026 | Thu 22 Jan 2026 | 12:00 p.m. |
  | Presidents' Day | 13 Feb 2026 | Thu 19 Feb 2026 | 12:00 p.m. |
  | Memorial Day | 22 May 2026 | Thu 28 May 2026 | 12:00 p.m. |
  | Labor Day | 4 Sep 2026 | Thu 10 Sep 2026 | 12:00 p.m. |
  | Columbus Day | 9 Oct 2026 | Thu 15 Oct 2026 | 12:00 p.m. |
  | Veterans Day | 6 Nov 2026 | Thu 12 Nov 2026 | 12:00 p.m. |

  — [EIA WPSR schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php)

### Inferences
- In oil_commodities.md line 77, the rule "on Wednesdays (EIA release 10:30 ET), take the sign of the 10:30–11:00 ET return" should be keyed to the actual release timestamp from the EIA calendar. On holiday-shifted weeks, a Wednesday 10:30 bar carries no EIA news, so a fixed-schedule backtest would add noise. The Thursday 12:00 releases fall in a different intraday liquidity window.
- The Christmas 2025 release (Mon 5:00 p.m.) came after the futures settlement window. A daily-bar event study would assign it to the next session.

### Gaps
- The natural-gas storage report schedule (ir.eia.gov) was blocked, so its Thursday 10:30 ET timing and holiday exceptions are **UNVERIFIED** here.
- The API (American Petroleum Institute) Tuesday 4:30 p.m. ET release time is not an EIA source and was not checked.
