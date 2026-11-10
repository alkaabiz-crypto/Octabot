# Evidence-Backed Buy/Sell Signals for Crude Oil (WTI/Brent/USOIL) and Liquid Commodities (Silver, Natural Gas)

Research note scope: published evidence for entry/exit rules, prioritizing after-cost, out-of-sample (OOS) and post-publication results; backtestable on daily/hourly data from 2025-01-01.

Method caveat: this was a brief pass (about 15 tool calls). Full-text fetches failed because several hosts are outside the session's network allowlist (fairmodel.econ.yale.edu, www.trendfollowing.com, 4nations.albertjmenkveld.com, www.eia.gov). Most findings therefore come from abstracts, repository records and secondary summaries surfaced by search, not from reading the papers in full. Numbers quoted from secondary summaries are labeled as such. Exact rule parameters that come from my prior knowledge, not from a source retrieved in this session, appear only under "Inferences" and are marked UNVERIFIED.

## 1. Trend-following / time-series momentum / breakout on oil (TSMOM, Hurst et al., Donchian/turtle)

### Takeaway
Trend-following is the best-documented commodity signal over long samples, net of estimated costs (Hurst et al. 1880+; Szakmary et al. 48 years / 28 markets). But the evidence is multi-asset, not crude-specific. Statistical robustness is contested (Huang et al. 2020 JFE). Performance decayed materially after about 2009–2010, especially for fast signals. Simple single-market Donchian/channel rules on energy futures show edges that are thin relative to costs in practitioner tests.

### Cited Findings
- Hurst et al. ("A Century of Evidence on Trend-Following") report TSMOM profitable across commodity futures since 1880, net of simulated transaction costs. Costs are based on recent estimates per asset class, scaled up for higher historical costs. The authors flag uncertainty in cost estimates and possible omission of roll costs — [Hurst et al. PDF](https://fairmodel.econ.yale.edu/ec439/hurst.pdf) (via search snippet; full text not fetched).
- Szakmary, Shen & Sharma (2010, JBF 34(2):409–426) test dual moving-average crossover and channel (breakout) rules on monthly data for 28 commodity markets over 48 years. They find positive mean excess returns **net of transaction costs in at least 22 of 28 markets**. Pooled, all rules earn significant positive returns over most subperiods, robust to data-mining adjustments and costs. Results were not broken out for crude oil in the retrieved abstract — [RePEc record](https://econpapers.repec.org/RePEc:eee:jbfina:v:34:y:2010:i:2:p:409-426); [EconBiz](https://www.econbiz.de/Record/trend-following-trading-strategies-in-commodity-futures-a-re-examination/10008484707).
- A third-party summary claims Szakmary et al. report Sharpe ratios of 0.4–0.6 with energy and metals outperforming agriculture. This is UNVERIFIED and the page contains unrelated content; do not rely on it — [qgtm-docs summary](https://qgtm-docs.pages.dev/research/gold_silver/paper_szakmary_trend_following).
- Baltas & Kosowski: more efficient volatility estimators and trend-detection methods significantly reduce turnover and therefore rebalancing costs — [Imperial/SSRN 2140091](https://spiral.imperial.ac.uk/bitstream/10044/1/41472/4/SSRN-id2140091.pdf).
- Huang, Li, Wang & Zhou (2020, JFE 135(3):774–794), using 55 futures/forwards over Jan 1985–Dec 2015, find little asset-by-asset evidence of TSMOM, in-sample or OOS. Only 8 of 55 assets show predictability at 10% in-sample. The pooled t-stat falls below bootstrap critical values. A strategy based on the historical sample mean performs about as well as TSMOM, which implies the profits may come from the average drift and volatility scaling rather than from predictability — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:135:y:2020:i:3:p:774-794); [CXO summary](https://www.cxoadvisory.com/momentum-investing/intrinsic-time-series-momentum-does-not-really-exist/); [Alpha Architect](https://alphaarchitect.com/an-empirical-challenge-for-trend-following/).
- Decay: a 2026 arXiv paper reports the 5-year rolling Sharpe of a fast trend portfolio fell from a historical 1–2.5 to statistically indistinguishable from zero after 2010. It attributes the decay mainly to small-tick markets; large-tick markets remain healthier — [arXiv 2607.01550](https://arxiv.org/pdf/2607.01550) (recent; peer review status unknown).
- A 2025 thesis replicating Moskowitz-Ooi-Pedersen finds strong pre-2009 and weaker post-2009 results. It cites Georgopoulou & Wang (2016) for diminishing post-2009 TSMOM performance "particularly in commodities" — [run.unl.pt thesis](https://run.unl.pt/bitstreams/3a74d44e-542e-440d-83b5-b5f44247f18f/download).
- Babbedge & Kerson (CME, 2019) find no clear evidence that markets trend less after the GFC. Decay with execution lag was similar before and after the GFC — [CME PDF](https://www.cmegroup.com/education/files/trends-not-dead-babbedge-kerson-2019.pdf).
- Hutchinson & O'Brien (2014): trend-following is weak for about 4 years after a financial crisis — [ETF.com / Swedroe](https://www.etf.com/sections/index-investor-corner/swedroe-trend-following-works-weakest-after-crises).
- Goulding, Harvey & Mazzoleni (2023) link more frequent turning points to lower trend returns and propose blending slow and fast signals — [Alpha Architect / IBKR summary](https://www.interactivebrokers.com/campus/ibkr-quant-news/breaking-bad-momentum-trends/).
- Live performance 2025–2026: trend-following had a poor start to 2025 (the rolling 12-month trend index return was −18.6% as of 30 Apr 2025). AQR's alternative-trend fund (Helix) said "alternative commodities" were a drag in H1 2025 and that commodity trend reversals caused losses in Sept 2025. AQR Trend Total Return Fund showed +23.26% for 2025 (to 31 Dec 2025) and +15.87% YTD as of 29 May 2026 (multi-asset; not oil-specific) — [Hedgeweek](https://www.hedgeweek.com/aqr-outpaces-trend-following-peers-with-double-digit-h1-gains/); [Institutional Investor](https://www.institutionalinvestor.com/article/aqrs-big-year-funds-climb-stock-picks-and-macro-moves); [AQR fund page](https://funds.aqr.com/funds/aqr-trend-total-return-fund). (Fund marketing/press; not a controlled backtest.)
- Single-market energy channel rules (practitioner): a Benzinga price-channel backtest on CL, HO, NG and RB found the raw edge "clearly insufficient to cover the commission costs and slippage". An ADX filter improved stability. A 20-period Donchian on heating oil had an average trade of about $65, flagged as possibly not covering costs — [Benzinga energy channel](https://www.benzinga.com/general/education/25/07/46280812/price-channel-strategy-for-trend-following-energy-futures-backtest-and-optimization); [Benzinga heating oil Donchian](https://benzinga.com/z/33326083). Ungerer Academy's "$35,000 in 2 years on crude" Donchian post is **vendor marketing** with no cost-adjusted stats — [Unger Academy](https://ungeracademy.com/blog/trading-systems-usd35-000-gained-in-2-years-on-crude-oil).

### Inferences
- Canonical rule specs to backtest (UNVERIFIED in this session, from prior knowledge of the papers):
  - (a) MOP TSMOM: sign of the past 12-month excess return, held for 1 month, position scaled to 40% annualized vol using ex-ante EWMA volatility (about 60-day center of mass).
  - (b) Hurst et al.: equal-weighted average of 1-, 3- and 12-month TSMOM signals, each vol-scaled. Assumes 2-and-20 fees plus asset-class cost estimates.
  - (c) Turtle System 1: 20-day breakout entry, 10-day opposite-breakout exit. System 2: 55-day entry, 20-day exit. 2N ATR stop with N = 20-day ATR.
  - (d) MA crossovers in Szakmary et al. are monthly dual-MA and channel rules with grid lookbacks.
- All of these need only daily close/OHLC, so they are implementable on CFD USOIL. A single-instrument trend rule on oil carries far more noise than the diversified portfolios in which the evidence was found. Expect a low Sharpe (plausibly 0–0.5) and long flat stretches.
- Given the post-2010 decay of fast signals, slower signals (3–12 month) and slow/fast blends are more defensible than 20-day breakouts. CFD overnight swap/financing on USOIL approximates roll cost and must be included, because Hurst et al. flag roll costs as a possible omission.

### Gaps
- No crude-specific, net-of-cost OOS TSMOM result was retrieved. Full texts (Hurst; MOP; Szakmary energy breakdowns) were not accessible.
- No peer-reviewed post-2015 Donchian/turtle backtest on CL with explicit costs was found.

## 2. Carry / term structure (backwardation vs contango, roll yield) and basis-momentum

### Takeaway
Cross-sectional carry/term-structure (long backwardated, short contango) and basis-momentum (Boons & Prado 2019 JF) are well-established multi-commodity premia. For a single oil instrument, the term structure works as a conditioning/timing filter (long only in backwardation). Implementing it requires at least two contract maturities, which CFD-only OHLC data does not provide.

### Cited Findings
- Quantpedia "Term Structure Effect in Commodities": long backwardated, short contango futures across 28 commodities. Reported high Sharpe, uncorrelated with standard factors, lower maximum drawdowns than the benchmark. Original sample 1979–2004 — [Quantpedia](https://quantpedia.com/strategies/term-structure-effect-in-commodities).
- Post-publication check: a QuantConnect replication reports the strategy was "not as profitable as announced" over its test period. The signal is the annualized roll return from near vs. deferred contract prices — [QuantConnect forum](https://www.quantconnect.com/forum/discussion/1884).
- Energy-futures study on Quantpedia: a conditional rollover strategy (long in backwardation, short in contango) delivers the highest Sharpe for all commodities studied. For unconditional strategies, Sharpe rises with maturity (further-dated contracts are better to hold) — [Quantpedia maturity structure of roll yields](https://quantpedia.com/effect-of-maturity-structure-of-roll-yields-in-commodity-futures-strategies/).
- Fuertes, Miffre & Rallis (2010, JBF) combine momentum and term-structure signals for tactical commodity allocation — [City Univ. open access PDF](https://openaccess.city.ac.uk/id/eprint/6416/1/Fuertes_Miffre_Rallis_JBF2010(CRO).pdf); [IDEAS](https://ideas.repec.org/a/eee/jbfina/v34y2010i10p2530-2548.html) (performance figures not retrieved).
- Boons & Prado, "Basis-Momentum", Journal of Finance 74(1):239–279 (2019): basis-momentum = the difference in past momentum between the first-nearby and second-nearby futures strategies. It decomposes into average curvature and slope changes. It "strongly outperforms" basis (carry) and plain momentum in predicting spot and term premiums, both in the time series and in the cross-section. It is not explained by storage theory (similar effects across commodities with different storage characteristics) — [IDEAS/RePEc](https://ideas.repec.org/a/bla/jfinan/v74y2019i1p239-279.html); [NBER conf. paper](https://conference.nber.org/conf_papers/f89296/f89296.pdf); [Tilburg](https://research.tilburguniversity.edu/en/publications/basis-momentum/).
- Follow-up: a Finance Research Letters (2021) paper examines basis-momentum sensitivity to ranking periods — [KNU record](https://research.knu.ac.kr/en/publications/basis-momentum-strategies-and-ranking-periods/).
- Cushing: over 2004–2011, Cushing inventories were a significant positive function of the lagged 2-month minus 1-month WTI spread (contango invites storage). This is a spread→inventory relation, not a return-prediction rule — [EIA working paper](https://www.eia.gov/workingpapers/pdf/cc_arbitrage_full.pdf). In Mar–Apr 2020, Cushing builds in response to the futures-spot spread were 4.3x historical norms — [MPRA 112352](https://mpra.ub.uni-muenchen.de/112352/1/MPRA_paper_112352.pdf).

### Inferences
- Single-instrument oil rule (backtestable only with CL1/CL2 or Brent M1/M2 settlement data): go long when annualized roll yield = (F1/F2 − 1)·(365/days between expiries) > 0 (backwardation); flat or short when < 0.
- Basis-momentum for oil (UNVERIFIED spec from prior knowledge): 12-month return of a rolled first-nearby series minus 12-month return of a rolled second-nearby series; long if positive.
- On a CFD broker, the daily swap/financing rate partly reflects the curve slope. In principle the sign of the long-side swap could proxy contango/backwardation. This proxy is untested; verify with broker data.

### Gaps
- No oil-only, after-cost OOS carry or basis-momentum result was retrieved. Sharpe and returns for Boons & Prado were not accessible (full text blocked).
- No 2023–2026 replication of carry/basis-momentum was found in this pass.

## 3. Inventory signals (EIA weekly surprises, API, Wednesday release, Cushing, COT/hedging pressure)

### Takeaway
EIA inventory surprises move WTI in the expected inverse direction (build → down, draw → up). The effect is concentrated on announcement day, and prices drift in anticipation of the report. There is no reliable persistence beyond the day, so this is mainly an intraday/event signal that needs consensus-forecast data. COT hedging-pressure evidence is mixed and largely gross of costs.

### Cited Findings
- A Journal of Futures Markets (2017) study finds strong announcement-day effects. Futures returns fall with positive (build) surprises and rise with negative (draw) surprises. Prices move in anticipation of the surprise (pre-announcement drift) — [Mountain Scholar PDF](https://api.mountainscholar.org/server/api/core/bitstreams/9938aa1b-96a3-466b-ac76-7710737b5b72/content).
- EIA presentation (Yang, 2017): no asymmetry between builds and draws, and **no persistence of the inventory-news impact beyond announcement day** — [EIA slides](https://www.eia.gov/finance/markets/reports_presentations/2017/yang.pdf) (via snippet).
- Ye & Karali (2016, Energy Economics 59:349–364), intraday: unexpected changes in both API and EIA reports have an immediate inverse effect on returns and raise volatility. EIA shocks have larger and longer effects; EIA is "the main market mover" — [RePEc](https://econpapers.repec.org/RePEc:eee:eneeco:v:59:y:2016:i:c:p:349-364); [AAEA 2015 paper](https://ageconsearch.umn.edu/record/205595/files/AAEA_Ye_Karali-2015.pdf).
- On EIA release days, the half-hour containing the release (the third half-hour) predicts the last half-hour return. On other days only the first half-hour predicts it — [Energy Journal exec summary (Xu)](https://www.iaee.org/ej/ejexec/ej44-5-Xu-exsum.pdf).
- Natural gas: there is a strong negative relation between NG futures returns and the EIA storage surprise — [Reading NG paper](https://centaur.reading.ac.uk/90003/1/NG_paper_final_round.pdf). Another study finds over 50% of NG futures' annual return accrues on weekly EIA storage-announcement days. The authors note investors are now arbitraging this away, a decay warning — [Energy Journal exec summary (Wichmann)](https://iaee.org/ej/ejexec/ej42-2-Wichmann-exsum.pdf).
- COT / hedging pressure: de Roon, Nijman & Veld find hedging pressure affects futures returns — [AgEcon](https://ageconsearch.umn.edu/record/18929/files/cp00sa01.pdf). Gorton, Hayashi & Rouwenhorst find no evidence that hedging pressure predicts risk premiums after controlling for inventories. Rouwenhorst & Tang (2012) find hedging-pressure variation does not predict gross returns, and trading frictions would impede exploitation — [MPRA 36426](https://mpra.ub.uni-muenchen.de/36426/1/MPRA_paper_36426.pdf); [CXO](https://www.cxoadvisory.com/momentum-investing/classic-paper-physical-inventories-and-commodity-futures-returns). A CXO summary cites COT-based active strategy returns of 9.6% (hedger-based) and 11.1% (speculator-based). These are secondary figures, unverified and probably gross — [CXO](https://www.cxoadvisory.com/commodity-futures/page/13).

### Inferences
- Backtestable rule candidates:
  - (a) EIA-day intraday momentum: on Wednesdays (EIA release 10:30 ET), take the sign of the 10:30–11:00 ET return and hold into the final 30 minutes before settlement. Needs 30-min or hourly bars. Hourly bars are coarse but approximate it.
  - (b) A surprise-sign trade needs consensus forecasts (e.g., a Reuters/Bloomberg poll) plus the API Tuesday print. Not implementable with OHLC alone.
  - (c) NG Thursday storage-day long exposure (pre-positioning before the Thursday 10:30 ET report), with decay already flagged by the authors.
- Because there is no persistence beyond the day, swing traders should not hold "inventory-surprise" positions for multiple days on this evidence.
- COT is weekly with a 3-day publication lag (Tue positions, Fri release). Evidence is weak after controlling for inventories, so it is low priority.

### Gaps
- No after-cost OOS P&L for an EIA-surprise trading rule was found. Effect sizes (cents per million barrels of surprise) were not retrievable.
- No study testing Cushing stocks as a direct return predictor OOS was found.

## 4. Seasonality (driving season, month-of-year, day-of-week, OPEC days, intraday)

### Takeaway
Day-of-week effects in oil (a negative Monday) appear in-sample but are not statistically robust and vary across periods. OPEC production-cut announcements show significant short-lived reactions. Intraday momentum (first half-hour predicts last half-hour) is the most tradable documented intraday pattern. Natural gas has the strongest documented calendar seasonality. Little of this has been shown OOS after costs.

### Cited Findings
- Auer (2014, Energy Economics 43:82–88): oil returns tend to be lower on Mondays, "suggesting profitable investment strategies", but not to a statistically significant extent — [RePEc](https://econpapers.repec.org/RePEc:eee:eneeco:v:43:y:2014:i:c:p:82-88).
- Meek & Hoelscher (2023, Cogent Econ & Finance) test day-of-week effects in WTI, Brent, RBOB, heating oil and NG futures, Jan 2002–Dec 2021 (no holdout confirmed) — [IDEAS](https://ideas.repec.org/a/taf/oaefxx/v11y2023i1p2213876.html).
- Chinese crude futures (2025, Int. Rev. Fin. Anal.): a significant positive Monday effect pre-COVID, insignificant over the full sample. This is evidence of instability — [IDEAS](https://ideas.repec.org/a/eee/finana/v106y2025ics1057521925005253.html).
- A weekend effect is reported as statistically and economically significant in energy futures — [vLex](https://law-journals-books.vlex.com/vid/risky-short-positions-and-855670779).
- An older crack-spread study (heating oil/gasoline) used seasonal rolling averages to pick buy/sell points in OOS simulations. It covers spreads, not outright crude — [AgEcon confp14-99](https://ageconsearch.umn.edu/record/285759/files/confp14-99.pdf).
- OPEC (Demirer & Kutan 2010, Energy Economics 32(6)): over 1983–2008, only **production-cut** announcements had a significant impact, smaller at longer maturities. Post-cut persistence offered excess returns for going **long the day after the conference ends** (in-sample) — [IDEAS](https://ideas.repec.org/a/eee/eneeco/v32y2010i6p1467-1476.html). IMF WP 2022/183: OPEC meeting impact about 3% but not long-lasting, consistent with overreaction — [IMF](https://www.imf.org/-/media/files/publications/wp/2022/english/wpiea2022183-print-pdf.pdf.md). Implied volatility drops about 3% after day 1 of a meeting and about 5% over 5 days (Horan, Peterson & Mahar 2004) — same IMF/Energy Journal references.
- Intraday momentum, crude (Wen et al. 2021, Economic Modelling 95:374–384): USO 2006–2018. Only the **first half-hour return predicts the last half-hour return**; a market-timing strategy earns "substantial" profits. Predictive information comes mostly from the overnight component — [RePEc](https://econpapers.repec.org/RePEc:eee:ecmode:v:95:y:2021:i:c:p:374-384); [Hull repository](https://hull-repository.worktribe.com/OutputFile/3303156). A practitioner (Quantified Strategies) reports only about 1.85% annualized for an open-half-hour rule (secondary, unverified), which suggests a small economic edge after costs.
- Natural gas: futures prices of all maturities peak when traded in June. A "buy low, sell high" seasonal strategy earns excess profits with low risk (OOS status unclear) — [Glasgow eprint](https://eprints.gla.ac.uk/281581/1/281581.pdf). CME notes the seasonality turn around December — [CME Group](https://www.cmegroup.com/newsletters/excell-with-options-report-from-rich-excell/excell-with-options-report-from-rich-excell-2025-10-21.html).

### Inferences
- Intraday momentum (sign of the first 30 min → hold the last 30 min) is implementable on hourly/30-min CFD data. Session-time alignment matters: the CL pit-equivalent is 9:00–14:30 ET, while CFDs trade nearly 24h. Small per-trade edge vs. spread is the main risk.
- The OPEC rule (long the day after an announced cut, short holding period) is event-driven. Needs an event calendar; OHLC is enough for prices.
- Monday/day-of-week rules should be treated as **in-sample only / not robust**; low priority.
- Driving-season (gasoline/crude spring strength) rules: no rigorous OOS evidence was retrieved.

### Gaps
- No peer-reviewed OOS test of month-of-year seasonality for WTI/Brent outright was found. No silver seasonality evidence was retrieved.

## 5. Mean reversion in oil — robust short-term rules?

### Takeaway
No robust, published after-cost short-term mean-reversion rule for crude oil was found. The intraday evidence points to momentum, not reversal. Practitioner work on large one-day oil drops suggests short-horizon continuation rather than reversal.

### Cited Findings
- Intraday: the documented pattern is first-to-last half-hour momentum, not reversal; no study testing last-half-hour reversal in crude was found — [Wen et al. 2021](https://econpapers.repec.org/RePEc:eee:ecmode:v:95:y:2021:i:c:p:374-384); [Xu, Energy Journal](https://www.iaee.org/ej/ejexec/ej44-5-Xu-exsum.pdf).
- After large one-day oil declines/reversals, crude tended to keep declining over a few weeks or less (practitioner analysis, 2025; vendor research, small sample) — [SentimenTrader](https://sentimentrader.com/blog/oils-loss-nasdaqs-gain).
- Fading breakouts on crude (2010–2024) was tested by a practitioner; results not retrievable from the excerpt — [Benzinga false breakout](https://www.benzinga.com/trading-ideas/technicals/25/05/45202553/is-the-false-breakout-strategy-worth-using-on-crude-oil-futures).
- The EIA effect does not persist beyond the announcement day, so there is no documented multi-day reversal or continuation from inventory shocks — [EIA slides](https://www.eia.gov/finance/markets/reports_presentations/2017/yang.pdf).

### Inferences
- Mean-reversion rules on oil (RSI(2), Bollinger fade) should be treated as hypotheses requiring the user's own walk-forward test. They lack published support and conflict with the documented intraday momentum. Oil's fat tails and gap risk (OPEC, geopolitics) make fade strategies vulnerable.

### Gaps
- No academic short-term reversal study specific to WTI/Brent with costs was found in this pass. Cross-sectional commodity short-term reversal literature was not searched.

## 6. 2023–2026 updates

### Takeaway
Recent work highlights decay in fast trend signals after 2010, possibly from microstructure. It recommends slow/fast blending. Live trend funds had a large drawdown in early 2025 and a recovery in late 2025–2026, with commodity trends a drag at times. No new oil-specific OOS signal evidence was found.

### Cited Findings
- arXiv 2607.01550 (2026): fast-trend Sharpe has been about zero since 2010, concentrated in small-tick markets — [arXiv](https://arxiv.org/pdf/2607.01550).
- Goulding, Harvey & Mazzoleni (2023): turning points erode trend returns; blend speeds — [IBKR/Alpha Architect](https://www.interactivebrokers.com/campus/ibkr-quant-news/breaking-bad-momentum-trends/).
- Trend index rolling 12-month return was −18.6% at 30 Apr 2025. AQR noted commodity trend reversals as a loss source in 2025 — [Hedgeweek](https://www.hedgeweek.com/aqrs-quant-funds-deliver-strong-returns-amid-volatility-in-2025/); [Institutional Investor](https://www.institutionalinvestor.com/article/aqrs-big-year-funds-climb-stock-picks-and-macro-moves).
- Meek & Hoelscher (2023) day-of-week in energy futures; Chinese crude Monday-effect instability (2025) — [IDEAS](https://ideas.repec.org/a/taf/oaefxx/v11y2023i1p2213876.html); [IDEAS](https://ideas.repec.org/a/eee/finana/v106y2025ics1057521925005253.html).
- Cushing at its lowest seasonal level in more than 5 years (July 2025), tied to a narrowing WTI-Brent spread (Kpler vendor commentary, not evidence) — [Kpler](https://www.kpler.com/fr/blog/record-midwest-runs-and-inventory-draws-squeeze-wti-brent-spread).

### Inferences
- Priority for backtesting on 2025-01-01+ daily/hourly USOIL CFD data, by evidence strength and OHLC feasibility:
  1. Slow vol-scaled TSMOM (1/3/12-month blend). OHLC OK.
  2. Intraday first→last half-hour momentum, with an EIA-Wednesday variant. Needs 30m/1h bars.
  3. Donchian 55/20 with ATR stop. OHLC OK; weak single-market evidence.
  4. OPEC-cut next-day long. Needs an event calendar.
  5. Term-structure/basis-momentum filter. Needs futures curve data, so not OHLC-only.
  6. NG storage-day / June-peak seasonality. Decay flagged.
- The 2025-01-01 window is short (under 2 years). Any slow-trend backtest will contain only a handful of independent trades, so results will be statistically meaningless on their own. Combine with longer CL history for validation.

### Gaps
- No silver-specific evidence was gathered (silver is covered only implicitly by multi-commodity trend/carry studies).
- No crude-specific post-publication decay study was found. Full-text verification of key parameters and Sharpe figures (MOP 2012, Hurst et al., Boons & Prado) remains outstanding because those hosts are blocked in this session.
