# Evidence-Backed Buy/Sell Signals for BTC, ETH, SOL

Method note: this was done with web search only. Direct fetches of primary PDFs and pages failed because quantpedia.com, bis.org, arxiv.org, cxoadvisory.com and bryanvine.github.io are outside this session's allowed network domains. So many figures below come from search-result abstracts or secondary summaries, and are flagged as such. No figure was taken from training memory without a source. Before implementing anything, verify the exact parameters against the primary PDFs.

## Trend-following / time-series momentum / moving-average rules

### Takeaway
The best-supported family is simple trend and momentum on BTC: price above an N-day SMA (5 to 100 days), 10-day new-high (MAX) breakouts, and Donchian-channel ensembles. These have out-of-sample support, and in one case (Zarattini/Pagani/Barbon) after-fee support. All of them can be built from daily OHLC alone. Evidence on decay after 2022 is thin. The MIN (buy-the-low) leg has decayed out of sample, while MAX has held up through Aug 2024.

### Cited Findings
- **Detzel, Liu, Strauss, Zhou & Zhu (Financial Management 50(1), 2021, pp.107–137).** Ratios of BTC price to its moving averages forecast daily BTC returns both in and out of sample. The working-paper version used 5-, 10-, 20-, 50- and 100-day SMAs. Another paper reports that the 5–100 day MA rules "both in- and out-of-sample, offer predictive power." — [EconPapers record](https://econpapers.repec.org/RePEc:bla:finmgt:v:50:y:2021:i:1:p:107-137); [WUSTL profile](https://profiles.wustl.edu/en/publications/learning-and-predictability-via-technical-analysis-evidence-from-/). The exact cost assumptions and OOS window were not verified (full text not accessible).
  - Rule to backtest: long when Close_t / SMA_N(t) > 1, otherwise flat, for N ∈ {5,10,20,50,100}, using daily closes. The paper also uses the MA ratios as regression predictors.
- **Simple technical rules with multiple-testing control (International Review of Economics & Finance, 2024).** The study tests 75,360 rules in six classes at daily and intraday frequencies, picks the best after transaction costs with a multiple-hypothesis-testing procedure, and evaluates portfolios of those rules out of sample. It finds that simple rules can beat buy-and-hold OOS, especially on a risk-return basis. Rules that track price more closely trade more and pay more in costs. — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S1059056024003010). The specific winning rules and cost levels were not seen.
- **Grayscale, "The Trend is Your Friend" (Aug 2023).** Rule: go long BTC when price crosses above its 50-day SMA, go to cash when it crosses below (no shorting). Since 2012 this gave higher annualized return and lower volatility than buy-and-hold. A 20/100-day SMA crossover also beat buy-and-hold, but crossover results are more sensitive to the lookback chosen. **Excludes exchange fees. This is vendor research, in-sample, with no OOS split.** — [Grayscale Research](https://research.grayscale.com/reports/the-trend-is-your-friend-managing-bitcoins-volatility-with-momentum-signals); fee caveat from [Estrategias de Inversión summary](https://www.estrategiasdeinversion.com/analisis/bolsa-y-mercados/informes/la-medias-moviles-la-estrategia-de-grayscale-con-n-640585).
- **Zarattini, Pagani & Barbon, "Catching Crypto Trends" (Swiss Finance Institute RP 25-80, 2025).** An ensemble of Donchian-channel trend models with different lookbacks and volatility-based position sizing, applied to a rotational portfolio of the top 20 most liquid coins. Reported **net-of-fees Sharpe > 1.5** and 10.8% annualized alpha vs BTC. A secondary summary gives net Sharpe 1.57, max drawdown 11%, and a gross "Combo" with Sharpe 1.58, CAGR 30% and alpha 14%. Gross turnover was high, so the authors added a turnover-control algorithm to stay viable after fees. Costs of 0.10%, 0.25% and 0.50% were reportedly tested. — [IDEAS/RePEc](https://ideas.repec.org/p/chf/rpseri/rp2580.html); [Concretum summary](https://concretumgroup.com/catching-crypto-trends-a-tactical-approach-for-bitcoin-and-altcoins/); [Barbon paper page](https://abarbon.com/papers/catching-crypto-trends). The 1.57 figure is secondary, and the authors' firm (Concretum) sells research, so there is a mild vendor flag.
- **Liu & Tsyvinski, "Risks and Returns of Cryptocurrency" (NBER w24877, 2018; RFS 2021).** Significant time-series momentum at daily and weekly frequency in BTC, XRP and ETH. In weekly sorts, the top quintile of last-week performers averaged about 11.2% the next week vs about 2.6% for the bottom quintile (secondary-summary figure). Momentum and investor attention were the strongest predictors, while production cost and realized volatility showed little support. — [NBER PDF](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf); [VoxEU column](https://cepr.org/voxeu/columns/risks-and-returns-cryptocurrencies). Sample is roughly 2011–2018. **Gross of costs, and no post-publication test was found.**
- **Liu, Tsyvinski & Wu, "Common Risk Factors in Cryptocurrency" (NBER w25882, 2019).** Cross-sectional 1-week momentum earns about 2.7% excess weekly returns, and the size and momentum factors explain it. — [NBER PDF](https://www.nber.org/papers/w25882.pdf).
- **Quantpedia MAX/MIN (BTC daily, Oct 2015–Aug 2024 in the update).** MAX means buy when BTC closes at its N-day high (trend). MIN means buy at the N-day low (mean reversion). N ranged from 10 to 50, and **10 days works best**. In the out-of-sample update, MAX "remains very effective" while MIN "is not performing as well as it did in the in-sample analysis" and has deeper drawdowns. The original study warned of drawdowns above 80%. No significant day-of-week effect was found. — [Quantpedia revisit](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/); [original](https://quantpedia.com/trend-following-and-mean-reversion-in-bitcoin/). Cost assumptions were not verified. This is a practitioner blog, not peer reviewed.
- **Shelton (JRFM 2024)** found technical-analysis and sentiment measures are generally poor out-of-sample BTC return predictors, while a blended market-timing strategy did well OOS. This conflicts with Detzel et al. — [IDEAS](https://ideas.repec.org/a/gam/jjrfmx/v17y2024i10p443-d1490211.html).
- **Sanhueza doctoral thesis (UDP, 2026).** Of 67 BTC variables significant in-sample, only 29 improved OOS at one or more horizons, and only 4 consistently beat a random walk. The predictive content that survived was concentrated in technical indicators. — [Thesis PDF](https://doctorados.udp.cl/cms/wp-content/uploads/2026/06/Tesis_Doctoral_Aliro_Sanhueza.pdf).
- **Molnar, "Bitcoin Runs on a Clock" (SSRN, summarized by Quantpedia).** Argues that price-based cycle indicators "die" as BTC swings shrink, and that the halving-cycle clock persists. — [Quantpedia summary](https://quantpedia.com/bitcoin-runs-on-a-clock-why-every-price-indicator-dies-and-the-halving-clock-doesnt/).

### Inferences
- The candidates with the most independent support, all implementable from exchange daily OHLC: (a) Close > SMA50 (or SMA20/SMA100) long/flat; (b) 10-day-high breakout long (MAX10) with a trailing exit; (c) a multi-lookback Donchian ensemble with volatility targeting and turnover control. The most recent, but practitioner-only, evidence suggests (b) and (c) have held up best.
- Long/flat versions beat long/short in most of the cited studies, and most of the gain comes from avoiding large drawdowns. A 2025+ backtest window (which includes drawdowns in 2025–26) mainly tests how well a rule sidesteps drawdowns.
- Decay risk: Shelton (2024) and Sanhueza (2026) suggest much technical predictability vanishes OOS. Use pre-specified parameters (for example SMA50 or MAX10 exactly as published) rather than re-optimizing on 2025+ data.

### Gaps
- The exact OOS windows, cost assumptions and Sharpe figures for Detzel et al. were not verified (no full-text access).
- No source was found that reports trend-rule performance for 2022–2026 specifically, other than the MAX/MIN update to Aug 2024.
- No published ETH- or SOL-specific trend results were found. The Zarattini et al. top-20 rotation implicitly includes ETH and SOL.

## Intraday and seasonality effects

### Takeaway
Shen, Urquhart & Wang find intraday time-series momentum in BTC in and out of sample, strongest in high-volume and high-volatility periods. Quantpedia's 21:00–23:00 UTC long window is the best-known hour-of-day rule, but it is single-exchange, practitioner-only, and had a rough 2022–2023. Calendar effects (day-of-week, turn-of-month) are time-varying and not robust. No credible evidence was found on CME gaps or the US-open effect.

### Cited Findings
- **Shen, Urquhart & Wang, "Bitcoin intraday time-series momentum," Financial Review 57(2), 2022, pp.319–344.** Adapts Gao et al. (2018): the first intraday segment's return predicts the last segment's return. They find strong intraday TSMOM in BTC both in and out of sample, with substantial economic gains in market timing, especially during downturns. The effect is driven by liquidity provision, not late-informed trading, and predictability is greatest when volume or volatility is high. — [Birmingham portal](https://research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/); [Reading accepted manuscript](https://reading-9.eprints-hosting.org/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf). Exact segment definitions (which hour is "first" and which is "last" in a 24h market), the sample and costs were not verified. Read the manuscript before coding.
  - Generic rule: compute the return over the first k hours of the UTC day (r_first). At the start of the final segment, go long if r_first > 0 and short or flat if r_first < 0, and close at the day end. Implementable with hourly OHLC.
- **Zarattini/Pagani/Barbon intraday BTC trend paper.** Gross-of-fees Sharpe of about 1.6 over 2018–2025. This is **gross, so after-cost viability is unknown**. — [Concretum "seasonality in bitcoin intraday trend trading"](https://concretumgroup.com/seasonality-in-bitcoin-intraday-trend-trading/) (via search summary).
- **Quantpedia hour-of-day (Gemini hourly, 2015–early 2022).** BTC returns cluster at 22:00 and 23:00 UTC. Rule: buy at 21:00 UTC and sell at 23:00 UTC (the strategy page phrases it as long at 22:00 for 2 hours). Originally reported 33% p.a. with max drawdown -22.45%. A later update reports 40.64% p.a. and Calmar 1.79, but **notes a rough 2022–2023 with a drawdown**. The effect is stronger on high-volatility days, on Fridays, and in uptrends. — [Quantpedia intraday anomalies](https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/); [Quantpedia seasonality of Bitcoin](https://quantpedia.com/the-seasonality-of-bitcoin/); [strategy page](https://quantpedia.com/strategies/intraday-seasonality-in-bitcoin). This is a single exchange with a practitioner backtest, and the cost assumptions were not verified. With about 365 round trips a year, cost per trip matters a lot.
- **Day-of-week.** Caporale & Plastun found that crypto day-of-week results are not conclusive evidence against efficiency. Another BTC study found a reverse Monday effect (higher Monday returns). A dynamic study concludes that crypto calendar effects are time-varying, consistent with the adaptive-market hypothesis. — [CESifo WP 6716](https://cesifo.org/DocDL/cesifo1_wp6716.pdf); [UNED dynamic calendar anomalies](https://portalcientifico.uned.es/documentos/653bfc548e0df037b36df52b?lang=eu); [Quantpedia day-of-week](https://quantpedia.com/the-day-of-the-week-effect-in-the-crypto-currency-market/).
- **Turn-of-month.** Kumar (2022) finds TOM effects in BTC, ETH and LTC for 2015–2021, not explained by day-of-week or January effects. Vasileiou (2023) questions whether TOM is exploitable. — [Emerald, Managerial Finance](https://emerald.com/insight/content/doi/10.1108/MF-02-2022-0084/full/html); [Inderscience](https://www.inderscience.com/filter.php?aid=129336).

### Inferences
- Intraday momentum (Shen et al.) and the 21–23 UTC window can be tested directly on hourly exchange OHLC from 2025 onward. Since both trade daily, include realistic taker fees and spread, for example 2–10 bp per side on BTC perps or spot.
- Calendar effects look like weak, regime-dependent signals. They are better used as filters (for example, only take trend entries on high-volatility days) than as standalone rules.

### Gaps
- No rigorous source was found on **CME futures gaps** or the **US equity open (13:30/14:30 UTC)** as BTC timing signals. Only social-media claims exist, so treat these as untested.
- No source was found measuring post-2022 decay of intraday TSMOM.
- Weekend effect with a decay analysis: none found.
- Full text of the Quantpedia 2024+ updates (year-by-year returns, cost model) could not be fetched.

## Mean reversion / short-term reversal in large caps

### Takeaway
Short-horizon evidence for BTC and large caps leans toward momentum, not reversal (Liu–Tsyvinski at 1 week, Quantpedia MAX > MIN). Buy-the-dip (MIN) has decayed out of sample and carries severe drawdown risk.

### Cited Findings
- Quantpedia's MIN (buy at the 10–50 day low) underperformed its in-sample results in the OOS update to Aug 2024, with more severe drawdowns than MAX. The original study noted drawdowns over 80%. — [Quantpedia revisit](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/).
- Daily and weekly time-series momentum, rather than reversal, is significant in BTC, ETH and XRP. — [Liu & Tsyvinski NBER w24877](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf).
- BitMEX (2018 blog) found that extreme funding can signal a counter-trend trade, but much of the profit came from collecting the funding payment itself. — [BitMEX blog](https://www.bitmex.com/blog/xbtusd-funding-mean-reversion-strategy). This is exchange-vendor content.

### Inferences
- For BTC, ETH and SOL, mean-reversion rules should be treated as unproven after costs. If tested at all, condition them on an uptrend filter (for example, buy a 10-day low only while Close > SMA100). This is an untested hybrid.

### Gaps
- No peer-reviewed, after-cost, OOS study of short-term (1–5 day) reversal specific to BTC, ETH or SOL was found in this search.

## Derivatives signals (funding, basis/carry, OI, liquidations, options skew)

### Takeaway
Basis/carry has the strongest academic support. In BIS work, high crypto carry predicts future crashes, which makes it a risk-off or exit signal, and cash-and-carry harvesting averaged above 10% p.a. Funding-rate direction is a weak or mixed predictor of next-period returns. No rigorous OOS evidence was found for OI, liquidations or skew as timing signals.

### Cited Findings
- **Schmeling, Schrimpf & Todorov, "Crypto carry" (BIS WP 1087, Apr 2023, revised Oct 2025; CEPR DP 20719).** The carry is the return on long spot plus short futures. It averaged above 10% p.a., was sometimes above 40%, and reached up to about 60% p.a. It is barely related to interest-rate differentials and is driven by a convenience yield from trend-chasing small leveraged investors and scarce arbitrage capital. **High carry predicts future price crashes**, and rising carry coincides with rising prices of crash insurance. — [BIS page](https://www.bis.org/publications/working-paper-1087-crypto-carry); [EconPapers](https://econpapers.repec.org/RePEc:bis:biswps:1087); [IDEAS CEPR](https://ideas.repec.org/p/cpr/ceprdp/20719.html). The exact predictive horizons, thresholds and after-cost carry-trade returns could not be extracted (PDF blocked). A Management Science acceptance appears in one listing but was not confirmed.
  - Implementable rule idea, with thresholds to be calibrated pre-2025: annualized basis = (F/S − 1) × 365/days-to-expiry, or the 8h perp funding rate × 3 × 365. When basis or funding is in its top decile, reduce or exit trend longs (a crash-risk filter), or run delta-neutral long spot plus short perp to collect it.
- **Inan, "Predictability of funding rates" (International Review of Financial Analysis vol. 119, 2026, DOI 10.1016/j.irfa.2026.105464).** Binance and Bybit funding rates are statistically predictable, but forecasts only add value if they improve decisions after costs. Stability varies more on Bybit, and predictability weakens in unsettled markets. — [Securities.io summary](https://www.securities.io/bitcoin-funding-rates-forecasting-trading-costs/). Secondary source only.
- The BTC funding rate's link to next-period returns is "loose" and mixed. — [Brave New Coin](https://bravenewcoin.com/insights/testing-theory-is-perpetual-swap-funding-rate-predictive). Practitioner source.
- K33 (2024) framed persistently negative perp funding as a bottoming or bullish signal for BTC. — [The Block](https://www.theblock.co/post/315831/perp-signal-bitcoin-bottom-bullish-year-end-k33). **Vendor commentary, with no OOS test.**
- Nimmagadda & Ammanamanchi (arXiv 2019) used BitMEX data with GARCH funding-rate models and found Granger causality between funding and perp prices. — [arXiv 1912.03270](https://www.arxiv.org/abs/1912.03270). In-sample only.

### Inferences
- Funding and basis are available from exchange APIs, so they meet the OHLC/funding-only constraint. The best-supported use is as a **crash-risk or exit overlay** (high carry means de-risk), not as a directional entry trigger.
- Cash-and-carry is a carry harvest, not a timing signal. Its post-ETF yields may be lower, but no source was found to confirm that.

### Gaps
- No rigorous OOS evidence was found for **open interest**, **liquidation cascades** or **options skew/25-delta risk reversal** (Deribit) as timing signals.
- No source quantified carry levels or crash predictability in 2024–2026 (post-ETF).

## On-chain signals (MVRV, SOPR, NUPL, exchange flows, stablecoin flows, hash ribbons)

### Takeaway
No peer-reviewed out-of-sample test of MVRV, SOPR, NUPL or hash ribbons was found. Peer-reviewed work finds that fundamental or on-chain-style valuation models (stock-to-flow, Metcalfe) explain returns in sample but fail out of sample. MVRV thresholds rest on a few cycles and appear to be degrading.

### Cited Findings
- Shelton (JRFM 2024): stock-to-flow and Metcalfe's Law help explain BTC returns in sample but have limited to no OOS predictive ability. — [IDEAS](https://ideas.repec.org/a/gam/jjrfmx/v17y2024i10p443-d1490211.html).
- Kyriakou et al. (City, University of London WP), covering 12 cryptocurrencies, question the value of both technical and fundamental analysis. — [Glasgow eprints PDF](https://eprints.gla.ac.uk/302711/1/302711.pdf).
- Molnar, "Bitcoin Runs on a Clock": MVRV thresholds of >3.7 for tops and <1.0 for bottoms were identified retrospectively. The positive OOS timing result comes from a single bear-dominated period, and cycle indicators are degrading as swings shrink. — [Quantpedia summary](https://quantpedia.com/bitcoin-runs-on-a-clock-why-every-price-indicator-dies-and-the-halving-clock-doesnt/).
- Glassnode published "Systematic Feature Discovery for Digital Asset Markets." **This is vendor research.** Its contents were not verified. — [Glassnode research](https://research.glassnode.com/systematic-feature-discovery-for-digital-assets/).
- A HKUST student project on trading BTC with on-chain data exists but is not peer reviewed. — [HKUST PDF](https://cse.hkust.edu.hk/~rossiter/independent_studies_projects/trading_bitcoin_onchain_data/trading_bitcoin_onchain_data.pdf).

### Inferences
- On-chain metrics are **not** implementable from exchange OHLC or funding data. They need Glassnode, CryptoQuant or a node. With only about 3–4 cycle observations, they are unsuitable for a 2025+ daily or hourly backtest that would produce statistically meaningful results.

### Gaps
- No rigorous OOS evaluation of SOPR, NUPL, exchange net flows, stablecoin supply or flows, or hash ribbons was found.

## ETF flows and macro links (liquidity, DXY, Nasdaq)

### Takeaway
Spot BTC ETF flows (since Jan 2024) mostly follow price, or move in two-way feedback with it. At most there is weak short-term predictive content, and one 2026 analysis found almost none at a 5-day horizon. No rigorous OOS evidence was found for DXY, Nasdaq or global-liquidity timing rules.

### Cited Findings
- FalconX: ETF flows show short-term predictive power for BTC price moves but do not predict their magnitude, and Granger causality is not true causation. — [FalconX](https://falconx.io/newsroom/what-can-spot-etf-flows-tell-us-about-the-trajectory-of-bitcoin-prices-a-preliminary-statistical-investigation). Vendor (a broker).
- Bitwise: BTC returns Granger-predict ETP flows at short lags, and the reverse is also significant at many lags, which implies feedback. — [Bitwise ETP series part 2](https://bitwiseinvestments.eu/blog/crypto-research/bitcoin-etp-series-part-2). Vendor (an ETF issuer).
- DWF Labs (reported by Cointelegraph, Oct 2026): ETF flows track past price closely but give almost no clue about 5-day-ahead direction. — [Cointelegraph](https://cointelegraph.com/news/bitcoin-etf-flows-follow-price-trends-dwf-labs?rand=50490). Vendor research reported secondhand.
- A Ledger (University of Pittsburgh) paper using Jan 2024–May 2025 data finds cointegration between ETF net assets and BTC price, a long-run levels link that is not predictive. — [Ledger PDF](https://ledger.pitt.edu/ojs/ledger/article/download/393/333?inline=1).
- Quantpedia "Silicon vs. Satoshi" studies tactical rotation between the Nasdaq-100 and BTC. Its details were not verified. — [Quantpedia](https://quantpedia.com/silicon-vs-satoshi-tactical-asset-rotation-between-nasdaq-100-and-bitcoin/).

### Inferences
- ETF flows are published after the US close (T+0 evening or T+1). Any rule built on them must lag the signal by one day to avoid look-ahead bias. Given the evidence, flows are better treated as a confirmation of trend than as an independent trigger.
- ETF flow data is not exchange OHLC or funding data. It needs issuer data or Farside-style aggregators.

### Gaps
- No peer-reviewed OOS test was found of global M2 or liquidity, DXY, or Nasdaq lead-lag as BTC timing signals.

## 2024–2026 performance updates

### Takeaway
Verified post-2023 updates are scarce. The MAX10 trend rule held up OOS to Aug 2024. Donchian ensembles report net Sharpe above 1.5 through 2025 (authors' own backtest). The 21–23 UTC effect weakened in 2022–2023. Crypto carry was revised in Oct 2025 and still reports crash predictability. ETF-flow signals look weak.

### Cited Findings
- MAX10 still effective and MIN degraded, with data to Aug 2024. — [Quantpedia revisit](https://quantpedia.com/revisiting-trend-following-and-mean-reversion-strategies-in-bitcoin/).
- Donchian ensemble net Sharpe > 1.5 (SFI RP 25-80, 2025). — [IDEAS](https://ideas.repec.org/p/chf/rpseri/rp2580.html).
- Intraday BTC trend gross Sharpe about 1.6 over 2018–2025. — [Concretum](https://concretumgroup.com/seasonality-in-bitcoin-intraday-trend-trading/).
- The 21–23 UTC strategy had a rough patch in 2022–2023. — [Quantpedia](https://quantpedia.com/the-seasonality-of-bitcoin/).
- Crypto carry revised Oct 2025. — [BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry).
- Funding predictability (IRFA 2026) matters only if it improves decisions after costs. — [Securities.io](https://www.securities.io/bitcoin-funding-rates-forecasting-trading-costs/).
- Technical predictability mostly vanishes OOS: 4 of 67 variables consistently beat a random walk (2026 thesis). — [UDP thesis](https://doctorados.udp.cl/cms/wp-content/uploads/2026/06/Tesis_Doctoral_Aliro_Sanhueza.pdf).

### Inferences
- A sensible pre-registered 2025-01-01+ test set, implementable from exchange OHLC and funding only:
  1. Daily long/flat Close > SMA50, with SMA20 and SMA100 as robustness checks (Detzel, Grayscale).
  2. Daily MAX10: long on a close at a new 10-day high, exit on a close below the 10-day low or SMA (Quantpedia; the exit rule should be checked against the source).
  3. Donchian ensemble across several lookbacks (for example 10/20/50/100), with inverse-volatility sizing and a turnover band (Zarattini et al.).
  4. Hourly intraday TSMOM (Shen et al.), with first-segment and last-segment definitions taken from the paper.
  5. Hourly 21:00–23:00 UTC long (Quantpedia), optionally restricted to Fridays or high-volatility days.
  6. A funding or basis top-decile overlay as a de-risk filter on rules 1–3 (Schmeling et al.).
- Apply each rule to BTC, ETH and SOL with the same parameters. The cross-asset evidence is mostly BTC or top-20 baskets.

### Gaps
- No independent (non-author, non-vendor) post-publication replication covering 2024–2026 was found for any rule.
- The primary PDFs could not be fetched in this session. Allow quantpedia.com, bis.org, arxiv.org and cxoadvisory.com to verify exact parameters, costs and year-by-year results.
