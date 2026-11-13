# Evidence-backed buy/sell signals for US stock indices (SPY/US500, QQQ/NAS100, US30) and the US dollar (DXY, EURUSD)

Scope note: about 20 search calls were made, mostly reading search-result summaries and abstracts. Few full PDFs were opened, so figures marked "secondary" should be checked against the original paper before relying on them. Vendor or practitioner sources are flagged **[vendor/practitioner]**. Sources that are only in-sample are flagged **[in-sample]**.

## Trend / moving-average timing (10-month SMA, 200-day SMA, Faber) and time-series momentum: performance, costs, post-publication results, decay

### Takeaway
The monthly 10-month SMA rule (Faber) is the best documented trend rule with real post-publication data: its out-of-sample decade after 2007 was reportedly better on a risk-adjusted basis than its in-sample period. It is cheap to trade because it switches rarely. Slow (monthly, 12-month) time-series momentum has a century of supporting evidence. Fast trend (horizons of days to weeks) seems to have broken down around 2009 on many futures, so a backtest on 2025+ data should favour slow trend rules.

### Cited Findings
- **Exact rule (Faber 10-month SMA):** at the last trading day of each month, hold the index if its month-end close is above its 10-month simple moving average, otherwise hold cash or T-bills. It is implemented as the reference "Faber market timing strategy" in R quantstrat — [quantstrat stratFaber](https://rdrr.io/github/braverock/quantstrat/man/stratFaber.html)
- **Post-publication update:** Faber re-tested the rule about 10 years after publishing it, in a 2018 special issue of the Journal of Portfolio Management. The update compared the in-sample period (1972–2005) with the roughly 11 years after it, and reportedly found a Sharpe ratio improvement "from 0.45 to 0.80". This figure is secondary (a Swedroe summary), and it is unclear whether 0.80 refers to the timing rule versus buy-and-hold or to out-of-sample versus in-sample. Results were similar for foreign stocks, US bonds, REITs and commodities — [Swedroe/ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist)
- **Parameter robustness:** CXO reports that the rule is not brittle across 8-, 10-, 12- and 14-month SMAs. It raises the open question of whether trading only at month-end is itself data mining, since other rebalance days could change the results — [CXO Advisory](https://www.cxoadvisory.com/momentum-investing/are-momentum-strategies-fragile/)
- The original paper's venue is cited inconsistently as the Journal of Wealth Management (2007) or the "Journal of Risk Management" (Spring 2007) — [Swedroe/ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist); [quantstrat](https://rdrr.io/github/braverock/quantstrat/man/stratFaber.html)
- **Time-series momentum, long run:** Hurst, Ooi and Pedersen test 67 markets (29 commodities, 11 equity indices, 15 bonds, 12 currency pairs) from 1880 to 2016. TSMOM had positive average returns in every decade, low correlation to traditional assets, and did well in 8 of the 10 largest 60/40 drawdowns. Drawdowns reached about 25% over extended periods. Two of the three authors are from AQR, so the paper is practitioner-affiliated — [Alpha Architect summary](https://alphaarchitect.com/time-series-momentum-aka-trend-following-the-historical-evidence/); [paper PDF](https://www.TrendFollowing.com/whitepaper/Century_Evidence_Trend_Following.pdf)
- **Caveat on the long sample:** an independent summary notes that investors could not have collected or processed the data needed to trade this way for much of that history — [CXO Advisory](https://www.cxoadvisory.com/momentum-investing/trend-following-with-intrinsic-momentum-over-the-very-long-run)
- **Decay of fast trend (2026 paper):** Kurth, Eisler, Rej and Bouchaud (arXiv 2607.01550, July 2026) study about 100 liquid futures from 1995 to 2025. They find that short-term trend strategies stopped delivering reliable returns around 2009, as an abrupt regime shift rather than gradual decay. The losses were concentrated in small-tick contracts, while large-tick contracts were largely unaffected. Their proposed cause is the post-crisis rise of HFT market making. Fast signals (days to weeks) were hit hardest. Capital Fund Management is the authors' affiliation (practitioner) — [arXiv](https://arxiv.org/abs/2607.01550); [Quantpedia summary](https://quantpedia.com/is-trend-still-your-friend-a-microstructural-account-of-the-demise-of-short-term-trend-following/)

### Inferences
- For daily or monthly OHLC backtests from 2025 onward, monthly rules (10-month SMA, 12-month TSMOM sign) and the daily 200-day SMA are the most defensible trend candidates. Fast crossovers (for example 5/20-day) carry the post-2009 decay risk described above.
- ES/NQ are large-tick contracts, so the Bouchaud et al. finding may hurt US equity index futures less than small-tick markets. This is an inference that needs checking in the paper's per-contract tables.
- Trend rules on indices mostly reduce drawdowns rather than adding return. In a strong bull year a timing rule can lag buy-and-hold, and whipsaws around the SMA are the main cost.

### Gaps
- I found no primary-source figures for 200-day SMA performance after costs after 2010, and no post-2018 out-of-sample extension of Faber.
- I found no 2023–2026 TSMOM performance numbers from AQR or Man Group (CTA indices had a strong 2022 and mixed 2023–2025, but this was not verified here).

## Short-term mean reversion on indices (RSI(2), Connors, IBS, lower Bollinger band, N-day lows): exact rules, out-of-sample/post-publication results, decay after about 2010

### Takeaway
Daily mean reversion on US equity index ETFs (IBS, RSI(2)) has the most practitioner out-of-sample support of any short-term pattern. The evidence is mostly blogs and forum backtests rather than peer-reviewed tests after costs. Reported post-2010 results stay positive but with deep drawdowns (for example about 23.5%) and a weak stretch in 2018–2021. These rules need only daily OHLC data and suit US500/NAS100/US30 CFDs, but overnight financing and spread costs matter because the edge per trade is small.

### Cited Findings
- **Connors RSI(2), common rule:** go long when the close is above its 200-day SMA and RSI(2) is below a threshold (10 or 5). Exit when the close is above the 5-day SMA or RSI(2) is above 70 (exact variants differ by source). QuantConnect's 2010–2022 SPY backtest reports a net profit of 158.3%, CAGR 7.57%, a 62% win rate, a max drawdown of 23.5%, and a downturn in 2018–2021 **[vendor/practitioner]** — [QuantConnect forum](https://quantconnect.com/forum/discussion/15754/an-overview-of-a-simple-rsi-based-trading-strategy)
- **Early out-of-sample test of Connors/TradingMarkets rules (2007–2009):** CXO found the limited out-of-sample evidence "mixed" on whether the rules are reliably profitable, and warned that the published in-sample results may have substantial data-snooping bias — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/out-of-sample-tests-of-bullish-regime-2-day-rsi-signals)
- Claims that RSI(2) has survived "17+ years out of sample" come from a promotional Substack with unverified methods **[vendor/marketing]** — [Alpha Algo Trading Research](https://algotr.substack.com/p/this-simple-mean-reversion-strategy)
- Arthur Hill (StockCharts) published an update of an RSI mean-reversion system that discusses its drawdowns (2018) **[vendor/practitioner]** — [StockCharts](https://articles.stockcharts.com/article/articles-arthurhill-2018-10-systemtrader---update-to-rsi-mean-reversion-strategy-and-dealing-with-the-dreaded-drawdown/)
- **IBS (Internal Bar Strength):** IBS = (Close − Low)/(High − Low). The typical rule buys at the close when IBS is below 0.2 and exits at the close when IBS is above 0.8 (or the next day). Pagonidis (2013), "The IBS Effect: Mean Reversion in Equity ETFs", reports a CAGR of about 13% for SPY and up to 40% for EWS **before transaction costs** — [Jonathan Kinlay summary](https://jonathankinlay.com/?p=2199)
- **IBS out-of-sample:** a QuantShare test fitted parameters only on SPY data through 2000 and reports that the system "still performed well" on the out-of-sample remainder. The same post shows an overfit full-sample version for comparison **[practitioner]** — [R-bloggers / Intelligent Trading Tech](https://www.r-bloggers.com/2013/01/ibs-reversion-edge-with-quantshare/)
- Practitioners warn that shorting systematically on high IBS fights the index's long-term upward drift, so long-only versions are preferred — [R-bloggers](https://www.r-bloggers.com/2013/01/ibs-reversion-edge-with-quantshare/)
- **Academic short-term reversal on index futures:** Della Corte, Kosowski and Wang study daily reversal on stocks, index futures and other futures (1993–2014). The strategies have turnover of about 100% per day, which "would substantially reduce any profitability", and the results are gross — [CXO Advisory](https://www.cxoadvisory.com/?p=28354); [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-with-futures)
- Short-term reversal behaves like a "short volatility" strategy: its returns come mainly in the weeks after large market declines — [Quantpedia](https://quantpedia.com/strategies/short-term-reversal-with-futures)
- Abrams and Walker's daily S&P 500 mean reversion (1999–2010, index data, gross) earned a 0.7% CAGR in bull states and 11.9% in bear states — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/complex-mean-reversion-and-swing-trading-stock-index-strategy/)

### Inferences
- The best candidates to backtest from 2025 onward are long-only IBS below 0.2 with exit at the next close or when IBS is above 0.8, and RSI(2) below 10 with a filter of close above SMA200 and exit when close is above SMA5. Both fit daily OHLC data on CFDs.
- Mean-reversion edges are regime-dependent (stronger in high volatility). The 2018–2021 weakness suggests the decay question is not settled. Treat any post-2010 claim as unproven until it survives your own after-cost test.
- On CFDs, the typical 1–4 day hold incurs overnight financing. Signals are taken at the close, so execution must be at or near the close. Hourly bars make a close-proxy entry possible (for example the last hour).

### Gaps
- I found no peer-reviewed post-2010 after-cost study of RSI(2), IBS, lower Bollinger band or N-day-low rules on SPY/QQQ.
- I found no published evidence specific to the Dow (US30), or about lower Bollinger band or 7-day-low rules beyond practitioner sites (Quantified Strategies pages were not fetched).

## Calendar and intraday anomalies: overnight vs intraday, turn-of-the-month, pre-holiday, pre-FOMC drift, day-of-week, intraday momentum, options expiration — which survived out of sample and after costs?

### Takeaway
Survivors: turn-of-the-month (still positive in long samples, but weaker in some periods) and intraday momentum (the Gao et al. last half-hour rule and the 2024 Zarattini et al. "noise area" breakout with reported net-of-cost results). Weakened or dead: the pre-FOMC drift (largely disappeared after 2015, except possibly in high-uncertainty regimes) and the pre-holiday effect for large caps (not significant for the S&P 500 in 1983–2019). The overnight-return anomaly in SPY is large historically, but reportedly peaked in January 2022 and is hard to capture after costs and spreads.

### Cited Findings
**Overnight vs intraday**
- Bespoke: buying SPY at the close and selling at the next open returned more than 670% since 1993 (excluding dividends), while buying at the open and selling at the close lost more than 11%. Reported figures vary by date (for example +634% vs −13.9%) **[practitioner]** — [Bloomberg/BQ](https://www.bloombergquint.com/markets/for-monster-gains-with-world-s-largest-etf-trade-it-after-hours)
- Alpha Architect, January 1993 to January 2020: 717% overnight, 627% buy-and-hold, 12% intraday — [Alpha Architect](https://alphaarchitect.com/?p=57001)
- One analysis says the overnight outperformance peaked in January 2022 and has deteriorated since — [Two Quants Substack](https://twoquants.substack.com/p/trading-the-night-effect) **[practitioner]**
- A commentary argues the pattern is a SPY ETF effect rather than an S&P 500 index effect — [FXStreet](https://www.fxstreet.com/amp/analysis/who-is-getting-action-at-night-202508190629). Another explanation offered is bid-ask bounce noise in close-to-open versus open-to-close returns — [Falkenblog](https://falkenblog.blogspot.com/2012/11/another-overnight-return-puzzle.html?m=1)
- Lou, Polk and Skouras (JFE 2019): at the stock level, momentum profits accrue overnight and other anomalies accrue intraday, with offsetting reversals across the two sessions. The authors note that trading costs make strategies exploiting these patterns "much less attractive" — [LSE PDF](https://personal.lse.ac.uk/polk/research/TugOfWar.pdf); [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:134:y:2019:i:1:p:192-213)

**Turn-of-the-month (TOM)**
- Rule: long from the close of trading day −1 (or −4/−5) before month-end through the close of trading day +3 of the new month, otherwise flat. Quantpedia calls it profitable and statistically significant over long-run data — [Quantpedia](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes); [QuantConnect](https://www.quantconnect.com/learning/articles/investment-strategy-library/turn-of-the-month-in-equity-indexes)
- A century-long US study finds that nearly the entire equity premium is earned from the last trading day through the first three trading days of the next month, with the rest of the month close to zero or negative — [run.unl.pt thesis/paper](https://run.unl.pt/bitstreams/e4f74902-309f-431d-b4f7-17ea2d328e42/download)
- Maberly and Waggoner (Atlanta Fed, 2000) found TOM effects disappeared after 1990 in S&P 500 futures and spot, and warned against out-of-sample inference from in-sample regularities. Xu and McConnell (2006) reported TOM to be "remarkably stable" — [Atlanta Fed WP 2000-11](https://www.atlantafed.org/research/publications/wp/2000/11.aspx); [Fed in Print](https://fedinprint.org/item/fedawp/13394/original)
- A 2026 Quantpedia sector study (data through June 2026) finds the first trading day of the month has the strongest average SPY return in the D−10 to D+10 window, while D+2 and D+3 show "sharp negative returns", which differs from the classic window. This suggests the recent effect is concentrated on day +1 — [Quantpedia](https://quantpedia.com/sectoral-intramonth-momentum-cycle/)
- CXO tests a TOM window (−5 to +4) from 1993 to early 2024 with switching frictions included. The numbers were not retrieved — [CXO Advisory guide](https://www.cxoadvisory.com/guides/calendar-effects/)

**Pre-holiday**
- Ko and Yang (Critical Finance Review, 2024) extend Ariel (1990) to 1983–2019. The DJIA and S&P 500 had significant pre-holiday premia in 1963–1982 but not in 1983–2019 (S&P 500 t-stat 0.93). The effect now exists only among small firms — [CFR](https://nowpublishers.com/article/Details/CFR-0111); [PDF](https://cfr.ivo-welch.info/published/papers/ko2021pre.pdf)
- CXO finds that holiday-specific effects such as Labor Day and Thanksgiving do not support an exploitable anomaly or may be weakening — [CXO Labor Day](https://www.cxoadvisory.com/calendar-effects/stock-returns-around-labor-day); [CXO Thanksgiving](https://www.cxoadvisory.com/calendar-effects/stock-returns-around-thanksgiving)

**Pre-FOMC drift (Lucca and Moench)**
- The original Lucca and Moench sample is 1994–2011. Kurov, Wolfe and Gilbert (Finance Research Letters, 2021) find that the drift "essentially disappeared" after 2015, both for meetings with and without press conferences, possibly because of reduced uncertainty — [RePEc](https://ideas.repec.org/a/eee/finlet/v40y2021ics1544612320315956.html); [Skidmore PDF](https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf)
- Counter-evidence: Ignatieva and Ohashi (Applied Economics, 2025) still find positive pre-announcement excess equity returns, but short-lived — [RePEc](https://ideas.repec.org/a/taf/applec/v57y2025i17p2021-2037.html). Another view is that the drift appears only when uncertainty or the risk premium is high — [Quantpedia](https://quantpedia.com/fomc-equity-drift-occurs-in-periods-of-high-uncertainty/)

**Intraday momentum**
- Gao, Han, Li and Zhou (JFE 2018; SPY 1993–2013): the first half-hour return (prior close to 10:00 ET) predicts the last half-hour return (15:30–16:00). Out-of-sample R² is 1.2–1.4%, or 2.0% when combined with the 12th half-hour, and the authors say the result survives transaction costs — [paper PDF](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf)
- Rule: if the first half-hour return is positive (negative), go long (short or flat) at 15:30 and exit at 16:00. The long-or-cash version earned 6.3% a year gross versus −0.5% for always holding the last half-hour (sample through 2012) — [CXO Advisory](https://cxoadvisory.com/calendar-effects/first-and-last-half-hours-of-trading-linked)
- QuantConnect's replication matches about 6.67% a year (a recreation, not independent out-of-sample evidence) — [QuantConnect](https://www.quantconnect.com/research/15348/intraday-etf-momentum/)
- Alpha Architect's in-house backtests found no support for a related intraday momentum result — [Alpha Architect](https://alphaarchitect.com/2015/02/overnight-momentum-vs-intraday-momentum/)
- Zarattini, Aziz and Barbon (2024/2025, SFI WP 24-97, SSRN 4824172) define a "noise area" from 14-day average intraday moves relative to the open. They go long or short on a break of the band, trail the stop with the higher (lower) of the band or VWAP, and are always flat at the close. On 1-minute SPY data from May 2007 to April 2024 they report 1,985% total return net of costs, 19.6% a year and a Sharpe ratio of 1.33. The assumed costs are $0.0035 per share commission plus $0.001 per share slippage (secondary). Aziz runs Bear Bull Traders, a trading-education company **[practitioner-affiliated]** — [SFI](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy); [Concretum](https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/); [CXO review](https://www.cxoadvisory.com/momentum-investing/complex-intraday-time-series-momentum-strategy-applied-to-spy/)

### Inferences
- With hourly OHLC only, the Gao et al. rule can be approximated by the open-to-first-hour return predicting the last hour's return. The Zarattini rule needs sub-hourly bars to work as specified, and an hourly version would be a degraded approximation.
- The overnight-hold rule (buy the close, sell the open) generates about 500 round trips a year. On CFD spreads, costs are likely to exceed the edge, and post-2022 weakness has been reported, so it is a low-priority candidate.
- TOM is the cheapest calendar rule to test (about 12 round trips a year, daily data). The 2026 Quantpedia result suggests testing a narrower window (day −1 to day +1) alongside the classic −1 to +3.
- FOMC: a backtest from 2025 onward has only about 8 meetings a year, so it cannot be validated statistically. Treat it as a conditional overlay at best (active only when VIX is elevated).

### Gaps
- I found no reliable recent evidence on day-of-week effects or options-expiration week for SPY, QQQ or Dow (not searched in depth).
- I found no independent post-2013 after-cost replication of the Gao et al. last half-hour rule, and no independent replication of Zarattini et al. beyond the authors.
- The CXO 1993–2024 TOM figures with frictions were not retrieved.

## Volatility regime / VIX signals (VIX term structure, volatility targeting)

### Takeaway
Volatility targeting of a single equity index looks good in sample (Moreira and Muir), but Cederburg et al. (JFE 2020) show that real-time versions generally do not beat buy-and-hold on Sharpe ratio or certainty-equivalent return. Its main benefit is drawdown control, not alpha. A VIX term structure in backwardation is a rare stress flag that tends to coincide with drawdowns but is poorly timed. Contango by itself carries no timing information for the S&P 500.

### Cited Findings
- Cederburg, O'Doherty, Wang and Yan (JFE 2020; 103 equity strategies): in-sample results confirm Moreira and Muir, but "reasonable out-of-sample versions generally earn lower certainty equivalent returns and Sharpe ratios" than the unmanaged portfolios. The authors attribute this to structural instability in the spanning regressions — [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117); [Alpha Architect](https://alphaarchitect.com/does-portfolio-timing-based-on-volatility-signals-outperform-buy-and-hold/); [Lehigh PDF](https://www.lehigh.edu/~xuy219/research/COWY.pdf)
- DeMiguel, Martín-Utrera and Uppal (JF 2024): a conditional multifactor volatility-managed portfolio does beat its unconditional counterpart out of sample and net of costs. This is a multifactor result, not single-index timing — [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:79:y:2024:i:6:p:3859-3891)
- VIX term structure: when it is in contango (the usual state) there is "no meaningful market timing signal for S&P500 returns". A negative slope (backwardation) can act as a contrarian, oversold indicator — [Macrosynergy](https://macrosynergy.com/?p=41000)
- 21 of 22 backwardation episodes from 2004 to 2025 coincided with an S&P 500 drawdown of more than 5% within 30 days, but backwardation can persist for weeks before the bottom, so it is not precise timing (small sample, blog source) **[practitioner]** — [Eco3min](https://eco3min.fr/en/vix-backwardation-contango-volatility-term-structure/)
- CXO: the term structure explained little of short-term VIX futures returns (correlation −0.12, R² 0.01). Long short-term VIX futures are "a losing game". VXX/XIV term-structure timing looked strong over 2006–2014 but used simulated pre-inception data — [CXO short-term VIX futures](https://www.cxoadvisory.com/volatility-effects/short-term-vix-futures-performance); [CXO roll return](https://cxoadvisory.com/volatility-effects/exploiting-vix-futures-roll-return-with-exchange-traded-products)
- Claims of 94.8% accuracy and Sharpe ratios of 2.24–2.6 for VIX term-structure signals come from a self-published ResearchGate paper and are unverified **[flag]** — [Harbourfront Quant](https://harbourfrontquant.substack.com/p/using-vix-futures-term-structure)

### Inferences
- VIX/VIX3M data is not in CFD OHLC feeds and would need a separate daily feed (CBOE publishes it free). A proxy that uses only OHLC data is realized-volatility targeting, for example scaling exposure by target vol divided by 20-day realized vol. Per Cederburg, expect lower drawdowns rather than a higher Sharpe ratio.
- Combining a backwardation flag with mean reversion (buying oversold markets during stress) is consistent with the evidence that reversal works mainly after large declines, but this combination was not tested directly in the sources.

### Gaps
- I found no published after-cost out-of-sample test of a VIX/VIX3M ratio rule for SPY covering 2023–2026.

## US dollar: carry, momentum and trend rules on DXY/EURUSD — evidence and decay

### Takeaway
FX technical and trend rules show clear decay. One study finds their predictive power has "completely disappeared" for G11 currencies (out-of-sample 1999–2020). Carry performed worse after 2008. A walk-forward study (2003–2025) found that only EURUSD and USDJPY time-series momentum cleared a 0.5 Sharpe bar (0.54 for EURUSD). DXY/EURUSD trend rules should be treated as weak candidates.

### Cited Findings
- Menkhoff, Sarno, Schmeling and Schrimpf (JFE 2012): currency momentum is largely unrelated to carry and to technical rules, and limits to arbitrage hinder exploiting it — [BIS WP 366](https://www.bis.org/publ/work366.pdf); [JFE PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- A paper with an out-of-sample period of 1999–2020 finds that technical-rule effectiveness "falls significantly over time" and that predictive power for G11 currencies "has completely disappeared", attributing what remains to time-series momentum — [ADU repository](https://repository.adu.ac.ae/bitstreams/30d15095-739e-4967-a33f-7233bf0644df/download)
- A counter-paper argues that claims of vanishing technical profitability may be premature — [NYU archive](https://archive.nyu.edu/jspui/bitstream/2451/31452/2/PLP1.pdf)
- "Currency carry trade: The decline in performance after the 2008 Global Financial Crisis" (Journal of International Financial Markets, Institutions and Money, vol. 76, 2022). Only the title was seen, not the findings — [RePEc](https://ideas.repec.org/a/eee/intfin/v76y2022ics1042443121001670.html)
- A walk-forward study of 7 major pairs (2003–2025): only USDJPY (Sharpe 0.78) and EURUSD (Sharpe 0.54), both using time-series momentum, cleared the 0.5 Sharpe tradeability bar. MA crossovers were not the best EURUSD rule. This is a student/EPAT project **[practitioner]** — [QuantInsti](https://www.quantinsti.com/articles/trend-following-strategies-major-currency-markets-epat-project/)
- For 1981–2012, currency carry with a trend-following overlay had a higher Sharpe ratio and lower drawdown than standalone carry — [CXO Advisory](https://www.cxoadvisory.com/?p=27433)
- Burnside et al. note that currency momentum made money during the 2008 crisis — [NBER w16942](https://www.nber.org/papers/w16942.pdf)

### Inferences
- Carry is a cross-sectional strategy across many currencies. It cannot be expressed in DXY or EURUSD alone beyond the sign of the USD–EUR rate differential, plus the swap or financing that CFD/FX brokers credit or debit.
- The most defensible single-pair rule is slow TSMOM on EURUSD (for example the sign of the 12-month or 6-month return, rebalanced monthly), with low expectations (Sharpe of about 0.5 at best in 2003–2025).
- DXY is about 58% EUR, so DXY and EURUSD rules are largely redundant. (The weight is general knowledge and was not verified in this session.)

### Gaps
- I found no source that tests a DXY moving-average rule directly, or that splits FX trend results into the 2010s and 2020s.
- I found no 2023–2026 evidence on FX trend or carry (for example the strong USD in 2022 and its reversal in 2025 were not covered by sources found).

## Updates covering 2023–2026

### Takeaway
New evidence from 2023–2026 consists of: (1) the July 2026 Bouchaud et al. paper documenting the post-2009 failure of short-term trend; (2) the 2024/2025 Zarattini et al. intraday momentum paper (net of costs, through April 2024); (3) Ko and Yang (2024) showing the large-cap pre-holiday effect is gone; (4) Ignatieva and Ohashi (2025) finding pre-FOMC drift is weak and short-lived; (5) DeMiguel et al. (2024) partly rescuing volatility management in a multifactor setting; (6) a 2026 Quantpedia result that the turn-of-the-month effect in SPY is now concentrated on day +1 with weakness on days +2/+3; and (7) a practitioner report that the SPY overnight effect has deteriorated since January 2022.

### Cited Findings
- Short-term trend failed around 2009 across about 100 futures (1995–2025) — [arXiv 2607.01550](https://arxiv.org/abs/2607.01550)
- Intraday "noise area" momentum on SPY: 19.6% a year, Sharpe 1.33, net of costs, 2007–April 2024 — [SFI WP 24-97](https://www.sfi.ch/de/publications/n-24-97-beat-the-market-an-effective-intraday-momentum-strategy-for-s-p500-etf-spy)
- The large-cap pre-holiday premium is not significant for 1983–2019 — [Ko and Yang, CFR 2024](https://nowpublishers.com/article/Details/CFR-0111)
- Pre-FOMC drift is short-lived — [Applied Economics 2025](https://ideas.repec.org/a/taf/applec/v57y2025i17p2021-2037.html)
- TOM on SPY: day +1 is strongest, days +2/+3 negative (data through June 2026) — [Quantpedia 2026](https://quantpedia.com/sectoral-intramonth-momentum-cycle/)
- The SPY overnight effect peaked in January 2022 — [Two Quants](https://twoquants.substack.com/p/trading-the-night-effect)
- Conditional multifactor volatility management works out of sample net of costs — [JF 2024](https://econpapers.repec.org/RePEc:bla:jfinan:v:79:y:2024:i:6:p:3859-3891)

### Inferences
- Shortlist for backtesting on daily or hourly OHLC data from 2025-01-01, ordered by strength of evidence after costs:
  1. Faber 10-month SMA (or 200-day SMA): monthly or daily, very low turnover.
  2. TOM long from day −1 to +3 (and a day −1 to +1 variant): daily.
  3. Long-only IBS below 0.2 and RSI(2) below 10 with SMA200 filter: daily, watch financing costs.
  4. First-hour predicts last-hour intraday momentum: hourly approximation.
  5. Realized-vol scaling as a risk overlay.
- Low priority or likely decayed: pre-holiday, pre-FOMC, fast MA crossovers, buy-close/sell-open overnight holding on CFDs, and DXY/EURUSD MA rules.
- A test window starting in 2025 (under 2 years) is too short to confirm any rule statistically. It can only check consistency with the long-run evidence, not establish an edge.

### Gaps
- Day-of-week and options-expiration evidence was not researched in depth.
- I found no 2025–2026 out-of-sample performance figures for the Faber, RSI(2) or IBS rules from a credible independent source.
