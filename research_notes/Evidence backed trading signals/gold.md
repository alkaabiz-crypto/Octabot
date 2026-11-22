# Evidence-Backed Trading Signals for Gold (XAUUSD, GC futures, GLD)

> Research method note: this session's network blocked direct page fetches (quantpedia.com, arxiv.org and university eprint hosts failed to resolve). All findings below come from search-engine summaries of the source pages and abstracts, not from reading full papers. Exact figures should be checked against the primary papers before being used as backtest targets. Research date: 2026-11-10.

## 1. Trend-following, time-series momentum, moving-average and breakout rules on gold

### Takeaway
The strongest evidence for gold timing is long-horizon trend filters (12-month time-series momentum, a 10/12-month or 200-day moving average). They mostly add value by getting out of gold during long down-trends, not by beating buy-and-hold in bull markets. After data-snooping controls only a few technical rules survive, standard intraday MA parameters fail, and commodity time-series momentum has weakened since 2009. I found no gold-only, net-of-cost, post-publication test.

### Cited Findings
- **Baur, Dichtl, Drobetz & Wendt, "Investing in gold: Market timing or buy-and-hold?"** (*International Review of Financial Analysis*, vol. 71, 2020). The paper tests more than 4,000 timing strategies: 4,095 monthly seasonal strategies, 18 technical and 15 fundamental strategies. It uses Hansen's (2005) SPA test to control for data snooping. The abstract concludes the results "are not robust to data-snooping biases and limited to specific evaluation periods, supporting the efficiency of the gold market" — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1057521918306227); [RePEc](https://ideas.repec.org/a/eee/finana/v71y2020ics1057521918306227.html)
  - Quantpedia's summary of the same paper says that only "selected technical trading strategies" survive data snooping. It says these winners beat buy-and-hold because they "shift out of gold following a prolonged trend of negative returns" — [Quantpedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/). This is more favourable than the published abstract. The exact parameters of the surviving rules could not be retrieved because the full text and Quantpedia page were blocked.
- **Moskowitz, Ooi & Pedersen, "Time Series Momentum"** (*Journal of Financial Economics*, 2012). The study covers 58 liquid futures, including commodities, from 1985 to 2009. The standard signal goes long when the trailing 12-month excess return is positive and short when it is negative, and is held for 1 month. The paper reports significant TSMOM in all 58 instruments. The diversified strategy earns about 1.26% per month gross alpha. The figures are gross of costs and the paper reports no gold-only stand-alone statistics — [SSRN](https://papers.ssrn.com/abstract=2089463); [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:104:y:2012:i:2:p:228-250)
- **Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing"** (AQR). Over a long history that includes hand-collected CBOT commodity data, TSMOM was profitable on average for "nearly all" commodity futures — [Yale-hosted PDF](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)
- **Decay:** A 2025 NOVA (Lisbon) thesis replicating commodity TSMOM finds strong results before 2009 and weaker results afterwards — [run.unl.pt](https://run.unl.pt/bitstreams/3a74d44e-542e-440d-83b5-b5f44247f18f/download). Another source in the same search says the risk-adjusted performance of TSMOM has been "diminishing in the post 2009 period, particularly in commodities" — [CXO Advisory](https://www.cxoadvisory.com/momentum-investing/intrinsic-momentum-investing/). This is secondary, and neither source gives gold-specific numbers.
- **Urquhart, Batten, Lucey, McGroarty & Peat**: the working paper is "Does technical analysis beat the market? Evidence from high frequency trading in gold and silver" (2015). The peer-reviewed version is in the *Journal of International Financial Markets, Institutions and Money*, vol. 52, 2018.
  - Data and method: 5-minute spot gold and silver from Jan 2008 to Sep 2014, testing 66,297 SMA/EMA/WMA crossover combinations with an in-sample/out-of-sample split.
  - Results: 20.2% of SMA rules were significant for gold, and only SMA rules were significant in both in-sample and out-of-sample gold subperiods. Nothing worked for silver.
  - The standard (1,50), (1,100), (1,150) and (1,200) 5-minute rules produced **negative** returns for gold.
  - The search summaries do not show net-of-cost results.
  - CXO's summary: profitable intraday gold trading is "possible but not easy" — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/high-frequency-technical-trading-of-gold-and-silver/); [paper PDF (mql5 mirror)](https://c.mql5.com/forextsd/forum/174/does_technical_analysis_beat_the_market__evidence_from_high_frequency_trading_in_gold_and_silver.pdf); [RePEc 2018](https://econpapers.repec.org/RePEc:eee:intfin:v:52:y:2018:i:c:p:102-113)
- **Marshall, Cahan & Cahan** tested 7,846 technical rules on 15 commodity futures including gold, using a data-snooping (White reality check) adjustment. The best MA rule beat costs only for oats, and that disappeared in 1995–2005. Their conclusion is that technical timing is "not reliably profitable for commodity futures". Gold-specific numbers were not retrieved — [CXO Advisory summary](https://www.cxoadvisory.com/technical-trading/does-technical-trading-work-with-commodity-futures/)
- **200-day MA filter (vendor data):** SentimenTrader reports that gold earned about +12.3% annualised when above its 200-day MA and +1.9% when below, using data since 1975. This is vendor analysis with no costs or out-of-sample testing — [SentimenTrader](https://sentimentrader.com/blog/gold-suffers-its-1st-real-test-of-its-long-term-trend/). The same vendor calls 50/200 death crosses after long up-trends a "debatable" signal — [SentimenTrader](https://sentimentrader.com/blog/gold-has-lost-its-trend)
- **12-month MA on monthly gold futures:** A CXO-linked study found that a 12-month MA beat buy-and-hold "by a wide margin". The period and costs were not retrieved — [CXO Advisory](https://www.cxoadvisory.com/?p=34759)
- **Intraday technical trading in China's gold market** (*J. Int. Fin. Markets*, 2021) is a separate study of intraday technical rules on Shanghai gold. Its results were not retrieved — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1042443121001876)
- **"Forecast-to-Fill: Benchmark-Neutral Alpha and Billion-Dollar Capacity in Gold Futures (2015–2025)"** (arXiv 2511.08571, Nov 2025) is a recent gold-futures strategy paper covering 2015–2025. Fetching was blocked, so its rules, costs and results are **unknown** — [arXiv](https://arxiv.org/html/2511.08571v1)
- **Practitioner and vendor items, flagged as marketing:** Unger Academy's Supertrend/High-Low breakout on GC claims "$80,000 gained in 2023 and 2024" — [Unger Academy](https://ungeracademy.com/?p=6984). Its "trend following vs intraday bias" piece is here — [Unger Academy](https://ungeracademy.com/?p=7916). Neither is independently verified or tested out of sample.

### Inferences
- The most defensible rules to backtest on daily OHLC are listed below. All can be built from daily closes alone.
  - **(a) 12-month TSMOM:** long if the 252-day return is above 0, otherwise flat or short. Rebalance monthly.
  - **(b) Long-only MA filter:** long if close is above SMA(200 days), or above the 10/12-month SMA on month-end closes; otherwise cash.
  - **(c)** As robustness variants, try shorter lookbacks (1, 3 and 6 months) and a blend of the three.
- The papers say the value comes from avoiding long down-trends. So in a strong bull regime like 2023–early 2026 expect the filters to lag buy-and-hold, and in a sharp reversal expect them to protect. An example of a reversal is the reported ~30% fall in GLD after January 2026 — [SentimenTrader](https://sentimentrader.com/blog/its-time-for-aggressive-traders-to-revisit-gld)
- Do not use standard 5-minute MA crossovers on gold. The only peer-reviewed high-frequency test found they lose money, and the significant parameter sets were found by searching 66k combinations.
- For hourly data, any MA rule should be chosen by walk-forward selection, not with fixed "popular" parameters.

### Gaps
- Exact parameters of the technical rules that survived the SPA test in Baur et al. (2020) were not retrieved.
- No gold-only TSMOM net-of-cost Sharpe ratio or post-2009 decay figure was found.
- No published 2024–2026 out-of-sample performance was found for any gold trend rule.
- No donchian/channel-breakout study specific to gold with costs was found.

## 2. Mean reversion on gold (RSI, Bollinger, short-term reversal)

### Takeaway
There is no robust, peer-reviewed, net-of-cost evidence for RSI or Bollinger mean reversion on gold. Blog-level evidence suggests GLD oversold readings precede modest positive 20-day returns, but that is consistent with gold's general upward drift. Treat all of it as in-sample.

### Cited Findings
- A blog running 856 indicator tests on SPY, QQQ, GLD, TLT and EEM reports:
  - GLD RSI(14)<30: about +101 bps average 20-day forward return over 550 signals.
  - GLD lower-Bollinger-band touch: about +131 bps over 20 days over 236 signals.
  - No costs or out-of-sample testing are described, and the author is not identified — [reigraph blog](https://reigraph-blog.pages.dev/do-technical-indicators-actually-work)
- A "reversal day" strategy on GLD with a 20-day exit claims about +1.5% per trade, but from only 70 signals — [Pulse.bot](https://www.pulse.bot/stock-trading/blogs/reversal-day-strategy-for-the-markets-1fbb2118-59a3-415b-8f16-28b75dbc8c47)
- QuantifiedStrategies tested a True Strength Index (momentum-type) rule on GLD. It made 232 trades with a 0.77% average gain and a 40% win rate. This is a practitioner backtest and not mean reversion — [QuantifiedStrategies](https://quantifiedstrategies.substack.com/p/3-technical-indicator-strategies)
- TradingView and cTrader "high win-rate gold mean reversion" scripts and bots are marketing with unverified backtests — [TradingView](https://in.tradingview.com/script/BhwmTgik-High-Win-Rate-Mean-Reversion-Strategy-for-Gold); [cTrader](https://ctrader.com/products/3199)
- The negative 5-minute MA crossover returns in Urquhart et al. hint at short-horizon noise or reversal at very high frequency, but the authors did not test reversal rules — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/high-frequency-technical-trading-of-gold-and-silver/)

### Inferences
- A daily-OHLC rule worth testing, as hypothesis only: buy GLD/XAU when RSI(2 or 14)<30 or close is below the lower Bollinger band (20, 2), exit after N days or when close crosses back above SMA(5/20).
  - Benchmark it against a random-entry long with the same holding period, because the 20-day forward returns above are close to gold's unconditional drift.
- Adding a trend filter (only take oversold longs when price is above SMA(200)) is the usual practitioner fix, but I found no gold-specific evidence for it.

### Gaps
- No academic study of short-term (1–5 day) reversal in gold futures or GLD after costs was found.
- No out-of-sample test of RSI or Bollinger rules on gold was found.

## 3. Seasonality and calendar effects (month, turn-of-month, day-of-week, intraday/overnight, holidays, FOMC/CPI/NFP)

### Takeaway
The best-documented calendar effect is **overnight-positive / intraday-negative** gold returns, published in peer-reviewed papers covering 1985–2012 and later. The authors report it has weakened, and one practitioner test finds it too small to trade alone after costs. The "autumn effect" (September/November) was not confirmed in later out-of-sample studies and is reported to have reversed. Turn-of-month, day-of-week and holiday effects are weak, descriptive or vendor-only. I found no rigorous gold-specific FOMC, CPI or NFP drift study.

### Cited Findings
**Overnight vs intraday**
- **Blose & Gondhalekar, "Overnight gold returns"** (*Applied Economics Letters*, 21(18), 2014). From 1985 to 2012, overnight returns on the COMEX front-month gold contract were significantly positive and day-session returns significantly negative. GLD showed a similar pattern. The asymmetry "has weakened substantially over the years, but it is still present" — [RePEc](https://ideas.repec.org/a/taf/apeclt/v21y2014i18p1269-1272.html); [GVSU ScholarWorks](https://scholarworks.gvsu.edu/fsdg/975)
- **Blose, Gondhalekar & Kort, "Overnight versus day returns in gold and gold related assets"** (*Journal of Economics and Finance*, 42(3), 526–549, 2018). The same pattern holds across COMEX futures, the London fix, gold miners, and gold closed-end funds and ETFs — [Springer](https://link.springer.com/10.1007/s12197-017-9403-0); [RePEc](https://ideas.repec.org/a/spr/jecfin/v42y2018i3d10.1007_s12197-017-9403-0.html)
- **QuantifiedStrategies (practitioner):** buying GLD at the close and selling at the next open shows the effect, but it is "probably too small to trade by itself", though filters may improve it — [QuantifiedStrategies](https://quantifiedstrategies.substack.com/p/a-quantitative-look-at-the-gold-overnight); [QuantifiedStrategies 2](https://quantifiedstrategies.substack.com/p/gold-overnight-trading-strategy-make-f87)
- **Peter Bell (MPRA working paper, 2015):** a long position held between the London fixes made reliable profits from 2000 to 2010. This is not peer reviewed — [RePEc/MPRA](https://ideas.repec.org/p/pra/mprapa/96124.html)
- **Intraday periodicity:** Batten, Lucey, McGroarty, Peat & Urquhart (*PLOS ONE*, 2017) found strong intraday periodicity in returns and volatility of gold, silver, platinum and palladium using 5-minute data — [paper PDF](https://reading-clone.eprints-hosting.org/79175/1/BattenLuceyMcGroartyPeatUrquhart2017.pdf). The specific hour-by-hour signs were not retrieved.
- **Caminschi & Heaney, "Fixing a Leaky Fixing"** (*Journal of Futures Markets*, 2014) studies short-term market reactions around the London PM fix. Its findings were not retrieved — [search result reference](https://link.springer.com/10.1007/s12197-017-9403-0)
- **CBS master's thesis (Donati & Jung, not peer reviewed):** gold intraday seasonality is "hat-shaped". Gold rises during Asian/Eastern hours, and prices fall around the London fixing times in years of alleged manipulation — [CBS](https://research.cbs.dk/en/studentProjects/gold-price-dynamics-around-the-clock/)
- **Monetary policy shocks and intraday gold** (*International Review of Financial Analysis*, vol. 95, 2024) is a study of how gold intraday returns and volatility react to monetary-policy shocks. Details were not retrieved — [RePEc](https://ideas.repec.org/a/eee/finana/v95y2024ipbs1057521924004186.html)

**Autumn / monthly seasonality**
- **Baur, "The autumn effect of gold"** (*Research in International Business and Finance*, 27(1), 2013). From 1980 to 2010, September and November were the only months with positive and statistically significant gold returns, and the effect comes with higher volatility — [RePEc](https://ideas.repec.org/a/eee/riibaf/v27y2013i1p1-11.html); [UTS](https://opus.lib.uts.edu.au/handle/10453/23416). A secondary source reports average returns of about 2.2% for September and 1.8% for November — [CXO Advisory](https://cxoadvisory.com/calendar-effects/gold-seasonality-drivers)
- **Out-of-sample checks:**
  - Borowski & Łukasik (2019) could not confirm the monthly calendar effects for gold, silver or platinum — [search summary via reference-global](https://reference-global.com/download/article/10.2478/ijme-2024-0011.pdf)
  - A 2024 *International Journal of Management and Economics* paper reports the gold autumn effect "has been reversed and replaced by the winter effect" — [RePEc](https://ideas.repec.org/a/vrs/ijomae/v60y2024i3p157-172n1001.html); [DOAJ](https://doaj.org/article/020bbdef98bc4868b2323d2b260fd09a); [Gdańsk Tech](https://pub.pg.edu.pl/en/download/162800-the-autumn-effect-in-the-gold-market-does-it-contradict-the-adaptive-market-hypothesis)
- In Baur et al. (2020), the 4,095 monthly seasonal strategies did not survive the SPA data-snooping test — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1057521918306227)
- The Perth Mint cautions that monthly seasonal averages carry no guarantee of repeating — [Perth Mint](https://www.perthmint.com/news/investor/investor-knowledge/does-gold-perform-stronger-at-certain-times-of-the-year/)

**Turn-of-month, day-of-week, holidays**
- **Turn-of-month:** Incrementum's *In Gold We Trust* (2004–2023) found higher average returns on the first trading days of the month for GLD, GDX and GDXJ. It notes results are highly sensitive to how the window is defined. This is in-sample and from an industry report — [In Gold We Trust](https://ingoldwetrust.report/nuggets/calendar-anomalies-and-the-gold-market/)
- **Day-of-week:**
  - Kohli (2012): there is a weak day-of-week effect in cash gold from 1980 to 2012 — [Business Perspectives PDF](https://businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/4996/IMC_2012_02_Kohli.pdf)
  - Seasonax (vendor, 2000–2017): Friday is the strongest day — [Seasonax](https://www.seasonax.com/?p=11797)
- **Holidays:** Quantpedia's 2025 "Global Holiday Drift" strategy goes long GLD from D-1 (or D-2) to D+2 around major festivals in several regions (for example Diwali and Chinese New Year). The full rules and statistics are behind a paywall — [Quantpedia](https://quantpedia.com/cultural-calendars-and-the-gold-drift-are-holidays-moving-gld-etf/)

**FOMC / macro announcement days**
- The pre-FOMC drift (Lucca & Moench) is documented for US equities, with no drift in Treasuries. Gold was not tested — [NY Fed SR512](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf)
- Gold-specific evidence is only a trade-newsletter anecdote: gold averaged +0.64% 10 days after the FOMC statement over 35 releases, with weakness before the meeting and no significance test. It is promotional — [FXEmpire](https://www.fxempire.com/forecasts/article/daily-gold-news-thursday-dec-17-gold-going-higher-after-fomc-689150)

### Inferences
- **Most implementable calendar rule (daily OHLC):** long GC/GLD from close to the next open, flat during the day session. Equivalently, long from the US close to the 09:30–08:20 ET open.
  - Costs matter a great deal: it is 2 trades per day, about 500 round trips per year. Test on GC with realistic 1-tick slippage plus commission, and expect the edge to be eaten unless it is filtered.
  - On hourly data, also test "long Asian session (about 23:00–07:00 UTC), flat US session", given the hat-shaped evidence.
- Since the London Gold Fix was replaced by the LBMA Gold Price auction in 2015, fix-time manipulation patterns found in earlier data may not persist. This is my inference and not tested here.
- September/November seasonal longs should be treated as debunked out of sample. A 2025+ backtest is fine as a curiosity but should not be expected to hold.
- Turn-of-month is cheap to test on daily data (for example, long from the last trading day of the month to trading day +3), but the evidence is in-sample only.

### Gaps
- No net-of-cost, post-2015 test of the overnight effect in GC or XAUUSD was found.
- No rigorous gold study of CPI- or NFP-day returns was found.
- The hour-by-hour return signs from Batten et al. (2017) and the Caminschi & Heaney fix findings were not retrieved.
- Quantpedia holiday-drift performance numbers are paywalled and the page was unreachable.

## 4. Cross-asset and macro signals (real yields, DXY, central banks, COT, gold/silver ratio, GVZ)

### Takeaway
None of these has peer-reviewed evidence as a short-term timing trigger after costs. The real-yield relationship, historically the strongest macro driver, broke down from 2022 because of central-bank buying. COT, the gold/silver ratio and GVZ evidence is vendor or blog-grade, and some of it contradicts itself. Baur et al. (2020) also report that fundamental timing rules do not survive data-snooping tests.

### Cited Findings
- **Real yields (10y TIPS):**
  - Historically there was a strong inverse correlation. One source puts R² at about 0.82 before 2022 and about 0.15 after 2022 (blog-grade) — [Wise with Gold](https://wisewithgold-com.pages.dev/the-gold-lens/real-yields-rising-gold/)
  - Goldmoney says the relationship broke down from autumn 2022 — [Goldmoney](https://www.goldmoney.com/research/have-central-banks-lost-control-over-the-gold-price)
  - RBC Wealth Management attributes the break to central-bank purchases above 1,000 t per year in 2022, 2023 and 2024 — [RBC WM](https://www.rbcwealthmanagement.com/en-us/insights/golds-regime-change)
  - A sub-period analysis from 1997 to 2026 is here — [eco3min](https://eco3min.fr/en/gold-vs-real-yields-tips-inverse-correlation-history/)
- **Fundamental timing rules:** Baur et al. (2020) tested 15 fundamental strategies, which per Quantpedia include macro variables. None was robust to data snooping — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1057521918306227); [Quantpedia](https://quantpedia.com/an-extensive-test-of-market-timing-strategies-in-the-gold-market/)
- **Inflation regime switching:** a Quantpedia strategy switches between GLD and a short-USD position based on the inflation trend. Details are paywalled — [Quantpedia](https://quantpedia.com/using-inflation-data-for-systematic-gold-and-treasury-investment-strategies/)
- **Cross-asset regimes:** Quantpedia's 2026 piece combines gold momentum with Treasury momentum — [Quantpedia](https://quantpedia.com/?p=43451). A gold/Bitcoin dual-momentum strategy reportedly had drawdowns near 50% — [Quantpedia](https://quantpedia.com/?p=45559). Details were not retrieved.
- **COT positioning:**
  - There is no peer-reviewed study in my results.
  - A vendor analysis (Bullion Trading LLC) of COMEX managed money from 2006 to 2026 found that after the most bearish 10% of months, gold was higher 12 months later in 22 of 24 cases. The most bullish extremes gave no reliable warning. The sample is small and the method unverified — [Bullion Trading](https://bulliontradingllc.com/blog/gold-cot-report-hedge-fund-positioning/)
  - Sources contradict each other on fading crowded longs, since managed money can stay long through trends — [metalcharts](https://eu1.metalcharts.org/cot/gold); [thetrading.tools](https://www.thetrading.tools/gc-cot)
- **Gold/silver ratio:**
  - A Silver Institute report (sponsored) finds Johansen cointegration and a long-run equilibrium just under 60:1 from 1970 to May 2026. It suggests central-bank buying has pushed the ratio above equilibrium — [Silver Institute](https://silverinstitute.org/wp-content/uploads/2026/07/Is-the-Gold-Silver-Ratio-Relevant-Today.pdf)
  - A blog backtest of the 80/50 rule (Aug 2000–Oct 2025) shows a −50.25% max drawdown and assumes perfect execution — [Substack](https://goldstandardorg.substack.com/p/the-gold-silver-ratio-your-hidden)
  - SentimenTrader found that after six-month surges in the ratio, gold kept outperforming silver for several months. This argues against immediate reversion — [SentimenTrader](https://sentimentrader.com/blog/golds-historic-rise-relative-to-silver)
- **GVZ (gold implied volatility):** the only timing analysis found is a paywalled January 2026 QuantSeeker post on GVZ and GLD returns — [QuantSeeker](https://www.quantseeker.com/p/gvz-and-gold-returns). Academic GVZ work found is volatility forecasting (GARCH-MIDAS), not return timing — [AIMS QFE 2026](https://www.aimspress.com/aimspress-data/qfe/2026/2/PDF/QFE-10-02-009.pdf)

### Inferences
- If macro filters are used, they belong as slow regime overlays (weekly or monthly), not entry triggers. Examples: only hold trend-long when the 3-month change in 10y real yield is ≤0, or when DXY is below its 200-day MA. The post-2022 break means a filter fitted on pre-2022 data would have kept you out of most of the 2023–2025 rally (inference).
- Implementability:
  - The gold/silver ratio can be computed from daily OHLC of GC and SI (or GLD and SLV).
  - Real yields need FRED DFII10 (daily) and DXY needs daily index data.
  - COT is weekly, released Friday for Tuesday positions, so it must be lagged.
  - GVZ is a daily close from Cboe.
- None of these is OHLC-only for gold itself, except the gold/silver ratio if silver prices are available.

### Gaps
- The Erb & Harvey "Golden Dilemma" (real-yield valuation) evidence was not retrieved.
- No peer-reviewed COT-gold timing study was found. Academic literature on hedging pressure and commodity returns exists, but I did not reach gold-specific results.
- No DXY-based gold timing rule with out-of-sample, net-of-cost results was found.
- No GVZ-based timing results are publicly available.

## 5. 2024–2026 performance updates

### Takeaway
I found no peer-reviewed or well-documented out-of-sample update covering 2024–2026 for any of the rules above. Only regime descriptions and vendor claims exist. The period combines a very strong trend (GLD +235% from Nov 2022 to Jan 2026, per a vendor) and then a reported ~30% drawdown. That makes it a stringent live test for trend filters.

### Cited Findings
- GLD gained about 235% from November 2022 to January 2026, then fell about 30% over the following five months and moved back below its 200-day MA (vendor commentary) — [SentimenTrader](https://sentimentrader.com/blog/its-time-for-aggressive-traders-to-revisit-gld)
- An FXStreet commentary from July 2026 notes gold was up year-to-date in Asian trading hours but down in Western hours. This is anecdotal and relevant to the session-split hypothesis — [FXStreet](https://www.fxstreet.com/analysis/a-strange-dichotomy-gold-up-on-the-year-in-asian-markets-down-big-in-the-west-202607131959)
- An arXiv paper (Nov 2025) on gold-futures alpha covering 2015–2025 exists, but its content was not retrieved — [arXiv 2511.08571](https://arxiv.org/html/2511.08571v1)
- Vendor claims for 2023–2024 GC breakout systems are marketing — [Unger Academy](https://ungeracademy.com/?p=6984); [Unger Academy 2024](https://ungeracademy.com/blog/gold-trading-usd14-000-in-2024-using-two-opposite-strategies)
- A paid GLD SMA handbook (28 SMAs, data through Sep 2026) is a sales listing and was not relied on — [Payhip](https://payhip.com/b/2O1Mz)

### Inferences
- A 2025-01-01+ backtest should report results separately for the bull leg (2025 to Jan 2026) and the drawdown leg (Feb–mid 2026), because a trend filter's value shows up almost entirely in the second leg.
- Recommended backtest set from 2025-01-01, ordered by strength of evidence:
  1. 12-month TSMOM / SMA(200) or 10-month SMA long-or-cash filter on daily closes, with a 1-day signal lag.
  2. Overnight-only long (close to next open) on GC or GLD, versus day-session-only, and net of about 1 tick plus commission per side.
  3. The Asian-session versus US-session split on hourly XAUUSD.
  4. Turn-of-month long (T-1 to T+3).
  5. RSI(2/14) or Bollinger oversold long with a 5- to 20-day exit, benchmarked against random entry.
  6. September/November seasonal long, as a control expected to fail.
- Costs to assume:
  - GC is about 1 tick ($10 per contract) slippage plus about $2–5 commission per side.
  - GLD costs 0.40% per year in expenses plus about 1 bp spread.
  - XAUUSD CFD spreads vary by broker. Assume 15–30 cents per oz (inference; not sourced).

### Gaps
- There are no published 2024–2026 out-of-sample results for TSMOM, MA filters, the overnight effect or seasonals in gold.
- The arXiv 2511.08571 methodology and results are unknown because the page could not be reached. Allow arxiv.org and quantpedia.com in the session network settings to retrieve it and the Quantpedia gold pages.
