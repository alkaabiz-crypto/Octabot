# Retail Trading Signals and the Reliability of Trading-Rule Research

Research date: 2026-11-10. About 16 search calls. Most findings come from search-result abstracts and summaries, not full texts. Where a figure rests on a secondary or vendor source, the note says so.

## Q1. What share of retail CFD accounts lose money, and what does the evidence say about copy/social trading (e.g. eToro)?

### Takeaway
Regulators found that 74–89% of retail CFD accounts lose money. Average losses per client were EUR 1,600–29,000. This finding was the basis for ESMA's 2018 product intervention: leverage caps, negative balance protection, and a mandatory loss-percentage warning. Independent evidence on copy trading is thin and mixed. The one positive eToro-linked result comes from a 2012 study promoted by eToro itself. Later academic and experimental work points to more risk-taking and no consistent outperformance.

### Cited Findings
- ESMA's 2018 product intervention cited national regulators' analysis: 74–89% of retail CFD accounts typically lose money, with average losses per client of EUR 1,600 to EUR 29,000. ESMA banned binary options for retail clients and restricted CFDs instead of banning them. — [ESMA press release, "ESMA agrees to prohibit binary options and restrict CFDs"](https://www.esma.europa.eu/node/84933); [ESMA notice of PI decisions](https://www.esma.europa.eu/sites/default/files/library/esma35-43-1135_notice_of_pi_decisions_on_cfds_and_binary_options.pdf)
- The CFD restrictions were:
  - leverage caps of 30:1 on major FX pairs and 20:1 on non-major pairs, gold and major indices (lower caps applied to other underlyings);
  - margin close-out rules;
  - negative balance protection, so a retail client cannot lose more than they deposit;
  - limits on incentives;
  - a standardised risk warning that states the provider's own percentage of losing retail accounts.
  — [ESMA](https://www.esma.europa.eu/node/84933); [FinanceFeeds](https://financefeeds.com/esma-bans-offering-binary-options-retail-investors-introduces-restrictions-cfds/); [CMS law summary](https://cms.law/en/gbr/regulatory-news/esma-fca-measures-on-the-provision-of-contracts-for-differences-and-binary-options-to-retail-investors-in-the-eu)
- Under MiFIR, ESMA's intervention measures are temporary and renewable every three months. — [ESMA](https://www.esma.europa.eu/node/84933)
- Copy trading, eToro and MIT (2012). Copying a suggested investor reportedly did 6–10% better than manual trading and 4% better than unguided copying. The design was a field experiment with about 6,000 traders, each given a $20 coupon to copy a guru. The source is an eToro press release, so it is not independent. — [PRNewswire / eToro](https://prnewswire.com/news-releases/tuning-social-networks-improves-financial-performance-on-etoro-social-investment-network-150723145.html); [MIT thesis](https://dspace.mit.edu/bitstream/handle/1721.1/112852/1015683926-MIT.pdf)
- Copy trading, Bond University. An analysis of more than 25 million trades found that copy traders give in to emotions (FOMO) and take riskier trades that hurt their profits. — [Bond University](https://bond.edu.au/news/fomo-wrecking-your-portfolio)
- Copy trading, experimental research (Barcelona School of Economics / Pompeu Fabra, with Heidelberg and Essex co-authors). Copy trading led to excessive risk-taking. — [BSE "Copy Trading"](https://bse.eu/research/publications/copy-trading)
- Copy trading, University of Vienna master's thesis ("Can Copy Trading Beat the Market?"). Social trading cannot consistently be said to produce better financial outcomes. — [univie thesis](https://utheses-gateway.univie.ac.at/api/document/get/file/73534)
- Copy trading, TalTech thesis. It studied 28 hand-collected eToro copy portfolios and noted that no prior study of social-trading portfolio performance existed. — [TalTech](https://digikogu.taltech.ee/en/Download/9c402020-d23e-447e-bcba-e41823baa02d)
- Copy trading, Traders Union survey (non-academic, proprietary). 41% of respondents stopped copy trading because of losses, drawdowns or poor performance. — [Traders Union](https://tradersunion.com/interesting-articles/copy-trading-smart-investing-or-hidden-risk-tu-research/)

### Inferences
- The broker-disclosed loss percentage is the best independent base rate for the strategies in scope. Grid bots, signals and copy trading all mostly run on CFD/FX broker accounts. Any signal vendor's claimed results should be read against this 70–80%+ loss base rate.
- Copy trading adds a second layer of selection bias. Leaderboards rank traders on past returns, which rewards lucky high-variance traders. The experimental "excessive risk-taking" finding fits that mechanism.

### Gaps
- I did not retrieve current (2025–2026) broker-level loss percentages. Typical recent disclosures by large EU/UK brokers are about 60–80%, but I did not verify any specific numbers this session.
- I did not confirm whether the ESMA measures were later made permanent through national competent authorities, or the status of the FCA's 2019 permanent rules. My background knowledge says both happened, but this session found no source.
- I found no large, peer-reviewed, eToro-wide outcome study of copiers' net returns after fees and spreads.

## Q2. Audits or academic studies of Telegram/Discord/paid signal groups; survivorship/selection bias; pump-and-dump links

### Takeaway
I found no rigorous, independent, peer-reviewed audit of the average performance of paid signal groups. Published "verified ROI" figures come from vendors or ranking sites with no stated method. The strongest academic evidence links Telegram crypto groups to organised pump-and-dump schemes. Regulators, the FCA in particular, have moved from warnings to criminal charges against "finfluencers" who promote unauthorised FX/CFD trading and signals.

### Cited Findings
- Xu & Livshits, "The Anatomy of a Cryptocurrency Pump-and-Dump Scheme" (USENIX Security 2019):
  - studied 220 pump-and-dumps organised in Telegram channels from 21 Jul to 18 Nov 2018, and 412 events from Jun 2018 to Feb 2019 in the extended version;
  - about 100 organised channels coordinate about 2 pumps a day, producing about USD 6M a month of artificial volume;
  - smaller market-cap coins are targeted more often;
  - a random-forest model predicts target coins with AUC > 0.90.
  — [USENIX](https://www.usenix.org/conference/usenixsecurity19/presentation/xu-jiahua); [arXiv 1811.10109](https://arxiv.org/abs/1811.10109)
- Hacken (2018, security firm, not academic). A review of 12 Telegram groups looked at member statistics rather than trade outcomes and found fake accounts in some groups. — [Hacken](https://hacken.io/insights/why-we-hate-telegram-group-pump-and-you-should-too)
- NCI MSc thesis (Mohib Ur Rehman, 2024). It proposes extracting signals (coin, entry, targets) from social-media posts and backtesting them to score provider accuracy and transparency. It is a student thesis, and I could not extract its findings. — [NCIRL](https://norma.ncirl.ie/8791/1/mohiburrehman.pdf)
- Vendor and ranking sites (Flexe.io, CoinCub) report figures such as "verified ROI 4.43x to 418%" with no published method, and they sell rankings. These should not be treated as evidence. — [Flexe.io](https://flexe.io/blog/telegram-free-crypto-signals-performance-data/); [CoinCub](https://coincub.com/blog/best-crypto-signals-telegram-channels-2026/)
- Practitioner commentary describes a common selection-bias practice: posting many vague calls, then claiming only the winners after the fact. — [templo.panamabahai.net (low-quality source; illustrative only)](https://templo.panamabahai.net/2026/06/25/telegram-crypto-signals-how-to-check-accuracy-and-avoid-scams/)
- FCA actions:
  - Warning-list cases include Instagram "traders" who show lavish lifestyles and tell followers they can earn the same by following their signals. An FCA official noted that promoters get paid whether or not followers make money. — [Finance Magnates](https://www.financemagnates.com/forex/britons-warned-to-watch-out-for-instagram-fx-scams/)
  - In May 2024 the FCA charged 9 individuals, including reality-TV influencers, over an unauthorised FX trading scheme promoted on social media. Trials are reportedly listed for 1 Feb 2027 and 15 Mar 2027 at Southwark Crown Court. — [AJ Bell](https://www.ajbell.co.uk/group/news/tv-stars-among-nine-finfluencers-charged-fca); [Investment Week](https://www.investmentweek.co.uk/news/4208916/finfluencers-fca-legal-action-trading-scheme)
  - The FCA interviewed 20 finfluencers under caution, focusing on FX/CFD promotion. It led an international crackdown with more than 650 social-media takedown requests and action against more than 50 websites. — [FCA press release](https://www.fca.org.uk/news/press-releases/fca-leads-international-crackdown-illegal-finfluencers); [inkl](https://inkl.com/news/uk-watchdog-interviews-20-social-media-finfluencers-under-caution)
  - FCA red flags include urgency ("only available for a few hours") and claims of exclusivity. — [Finance Magnates](https://www.financemagnates.com/forex/britons-warned-to-watch-out-for-instagram-fx-scams/)

### Inferences
- Signal sellers often earn from subscriptions or broker affiliate/IB rebates on volume, so their revenue does not depend on followers making money. The FCA quote supports this. The incentive favours high trade frequency and aggressive marketing over real edge.
- Survivorship bias is structural. Failed channels are deleted or renamed. Only surviving channels advertise track records, and they report those records themselves.

### Gaps
- I found no peer-reviewed study measuring net returns of following paid FX/crypto signal groups, and no audit of "AI signal" apps (SignalPro-style). Any claim that these groups have an edge has no independent support that I could find.
- I did not retrieve SEC, CFTC or ASIC warnings on signal or copy-trading scams this session. ASIC and CFTC have published such warnings, but I did not verify them.
- I did not find Hamrick et al. (pump-and-dump on Telegram/Discord) directly. Xu & Livshits cite it as consistent prior work.

## Q3. Popular TradingView indicators (Supertrend, UT Bot, LuxAlgo, "Pro Trend Signals"): any independent evidence?

### Takeaway
I found no peer-reviewed study showing that Supertrend, UT Bot, LuxAlgo or similar retail scripts are profitable out of sample after costs. Results are very sensitive to parameter choice, which invites overfitting. Self-published trader backtests show low win rates and weak or negative intraday results.

### Cited Findings
- An IJIRT paper (low-tier journal) on an ML-filtered Supertrend used 4 years of training and 3 years of unseen test data. Changing the confidence threshold altered selectivity and risk, but there was no monotonic relationship with profitability. — [IJIRT](https://ijirt.org/publishedpaper/IJIRT209123_PAPER.pdf)
- An arXiv thesis on Bayesian-optimising Supertrend found that performance is heavily driven by the chosen ATR multiplier and period, which is a sign of parameter sensitivity. — [arXiv 2405.14262](https://arxiv.org/html/2405.14262v1)
- A broader study (Springer, Financial Markets and Portfolio Management) found technical rules beat buy-and-hold in 13 of 23 developed-market indices, but the results are very sensitive to moderate transaction costs. — [Springer s11408-023-00433-2](https://link.springer.com/content/pdf/10.1007/s11408-023-00433-2.pdf)
- A self-published backtest (Liberated Stocktrader) reports a Supertrend win rate of about 42%. Results were negative on 5-minute charts and weak on daily charts. — [Liberated Stocktrader](https://www.liberatedstocktrader.com/supertrend-indicator/)
- LuxAlgo publishes educational content on the "Probability of Backtest Overfitting". This vendor content acknowledges the overfitting problem but is not evidence for its own indicators. — [LuxAlgo library](https://www.luxalgo.com/library/concept/probability-of-backtest-overfitting.md)

### Inferences
- Most popular scripts are trend-following variants built on ATR or moving averages: Supertrend is ATR-band trailing, and UT Bot is an ATR trailing stop. They are therefore covered by the general technical-rule literature (Q5), which finds that simple rules lost significance after data-snooping correction and costs in developed markets since the 1980s.
- TradingView "strategy" backtests with repainting, intrabar fills or zero commission can badly overstate results. This comes from background knowledge and was not verified this session.

### Gaps
- No independent studies found on UT Bot, LuxAlgo signals or "Pro Trend Signals" specifically.

## Q4. Martingale/averaging/grid/DCA bots on FX/CFD: risk of ruin and why high win rates mislead

### Takeaway
I found no peer-reviewed study of retail martingale or grid EAs. The mathematics is standard gambler's ruin, and practitioner analyses agree on it. Martingale sizing turns many small wins into a rare, total loss. High win rates and smooth equity curves come from that mechanism, not from edge. Fixed-lot grids have bounded but trend-exposed losses. Martingale accounts face near-certain ruin over enough sequences.

### Cited Findings
- Phoenix Technologies analysis (via ThorTradeCopier, a vendor) modelled a 5-rung martingale ladder on a $2,000 buffer.
  - At a 55% win rate, the ladder is more likely than not to breach within 38 sequences.
  - Fixed $100 risk has about 1.81% lifetime ruin.
  - An edge makes the ladder profitable per sequence while it survives, but sizing still multiplies the risk of ruin.
  — [ThorTradeCopier](https://thortradecopier.com/blog/does-martingale-work)
- Autochartist / Shaun Overton (simulation claim). The probability of ruin rises with the number of trades, to about 95% by 1,000 trades. — [Autochartist](https://trader.autochartist.com/?p=68349)
- MQL5 community commentary:
  - Martingale EAs "don't fail slowly; they fail all at once".
  - Gold trends break recovery-based systems that showed high win rates and smooth curves in backtests.
  — [MQL5 blog](https://www.mql5.com/en/blogs/post/767654); [MQL5 forum thread](https://www.mql5.com/en/forum/502291)
- A grid vs. martingale comparison found fixed-lot grids have bounded, predictable losses in trends, while martingale accounts face "certain destruction given enough time". The source is broker or affiliate content. — [steadypips](https://steadypips.pages.dev/posts/grid-trading-vs-martingale/); [Titan FX research](https://research.titanfx.com/column/what-is-martingale-strategy)

### Inferences
- Win rate alone says nothing about edge. Expectancy = p·avgWin − (1−p)·avgLoss. A 95% win rate with a tail loss 20 times the average win has negative expectancy. Backtests shorter than the typical time between blow-ups will hide the tail.
- Margin calls and stop-outs at retail CFD brokers make ruin "absorbing" before the theoretical recovery trade, especially under ESMA leverage caps (30:1 on majors, 20:1 on gold). Negative balance protection limits the loss to the deposit, but a total loss of the deposit is still ruin.
- Bots that average down on CFDs also pay overnight financing on growing positions, which adds negative carry. This is background knowledge, not verified this session.

### Gaps
- No academic or regulator study of real-account outcomes for martingale or grid EAs was found. Such a study could, for example, use myfxbook or MQL5 signal survival rates. MQL5 Signals or myfxbook survival data would be the next place to look.

## Q5. Meta-research: data snooping, multiple testing, publication decay, replication, backtest overfitting

### Takeaway
After correcting for data snooping, technical trading rules show little economic value in developed markets after about the mid-1980s. Any remaining in-sample profits disappear with modest transaction costs. Across the wider anomaly literature:
- returns fall 26% out of sample and 58% after publication;
- about 65% of 452 anomalies fail replication at t > 1.96, and 82% fail at multiple-testing thresholds;
- new factors should clear t > 3.0;
- testing more than about 45 configurations on 5 years of data almost guarantees a spurious in-sample Sharpe ratio of 1.

### Cited Findings
- Sullivan, Timmermann & White (1999), *Journal of Finance* 54(5):1647–1691.
  - They applied White's Reality Check bootstrap to a universe of about 7,846 technical rules. The universe extends the 26 rules of Brock, Lakonishok & LeBaron (1992), tested on about 100 years of daily DJIA data.
  - The best rule looks significant in sample, but rules lose predictive power for major US indices after the mid-1980s.
  — [Paper PDF](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf); [RePEc](https://econpapers.repec.org/RePEc:bla:jfinan:v:54:y:1999:i:5:p:1647-1691); rule count per secondary summary in [ThorTradeCopier](https://thortradecopier.com/blog/does-technical-analysis-work)
- Hsu & Kuan (2005), *Journal of Financial Econometrics* 3(4):606–628.
  - They used the Reality Check and Hansen's SPA test on a universe of 39,832 rules, including complex strategies, across DJIA, S&P 500, Nasdaq Composite and Russell 2000 for 1990–2003.
  - Significant profits appeared only in the "young" markets (Nasdaq, Russell), not in DJIA or S&P 500.
  - Complex strategies can improve on simple ones.
  — [RePEc](https://econpapers.repec.org/RePEc:oup:jfinec:v:3:y:2005:i:4:p:606-628); [CXO summary](https://www.cxoadvisory.com/technical-trading/technical-trading-thoroughly-tested)
- Hansen's SPA test was developed because the Reality Check can be low-powered and conservative when the universe includes poor rules. — [Park & Irwin / AgEcon](https://ageconsearch.umn.edu/record/19039/files/cp05pa01.pdf)
- Bajgrowicz & Scaillet (2012), *Journal of Financial Economics* 106(3):473–491.
  - They used the False Discovery Rate on DJIA daily data from 1897.
  - Even with FDR, an investor could never have chosen the future best rules in advance, because rule performance does not persist.
  - Even in sample, performance is completely offset by low transaction costs.
  - This "seriously calls into question" the economic value of technical rules reported for early periods.
  — [Paper PDF](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Bajgrowicz_Scaillet.pdf); [RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:106:y:2012:i:3:p:473-491)
- McLean & Pontiff (2016), *Journal of Finance*, "Does Academic Research Destroy Stock Return Predictability?"
  - Across 97 predictors, portfolio returns are 26% lower out of sample (pre-publication) and 58% lower post-publication.
  - The authors read the 26% as an upper bound on data mining and the about 32% difference as the effect of publication-informed trading.
  - Returns are gross of trading costs and shorting frictions.
  — [Paper PDF (gwern mirror)](https://Www.Gwern.net/doc/economics/2016-mclean.pdf); [Counterpoint mirror](https://counterpointfunds.com/wp-content/uploads/2017/07/PredictabilityMcleanPontiff.pdf); [CXO](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation)
- Harvey, Liu & Zhu (2016), *Review of Financial Studies* 29(1):5–68.
  - Given extensive data mining, a t > 2.0 hurdle makes no sense for new factors. New factors should clear t > 3.0.
  - "Most claimed research findings in financial economics are likely false."
  - The paper catalogues about 316 factors. Secondary sources state the counts inconsistently, so check the paper.
  — [NBER w20592](https://nber.org/papers/w20592); [RePEc](https://econpapers.repec.org/RePEc:oup:rfinst:v:29:y:2016:i:1:p:5-68.)
- Hou, Xue & Zhang (2020), *Review of Financial Studies* 33(5):2019–2133, "Replicating Anomalies".
  - Using NYSE breakpoints and value weights, 65% of 452 anomalies fail |t| > 1.96, and 82% fail at a multiple-testing threshold of t = 2.78.
  - Without microcap controls, the failure rates are lower (about 43% and 56%).
  - Value, momentum, investment and profitability anomalies hold up best.
  — [IDEAS/RePEc](https://ideas.repec.org/a/oup/rfinst/v33y2020i5p2019-2133..html); [CXO](https://www.cxoadvisory.com/big-ideas/most-stock-anomalies-fake-news/); [Alpha Architect](https://alphaarchitect.com/replicating-anomalies/)
- A counterpoint: Jensen, Kelly & Pedersen ("Is There a Replication Crisis in Finance?", JF 2023) report that about 82% of factors replicate under their Bayesian/CAPM-alpha approach. This finding comes from a secondary blog summary. — [Systematically Biased substack](https://systematicallybiased.substack.com/p/pockets-of-replicability-post5)
- Bailey & López de Prado (2014), *Journal of Portfolio Management*, "The Deflated Sharpe Ratio". It corrects the Sharpe ratio for selection bias under multiple testing and for non-normal returns, and it introduces minimum track-record length. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting" (*Journal of Computational Finance*, 2015/2017).
  - PBO is estimated with combinatorially symmetric cross-validation (CSCV). It is the probability that the configuration that is best in sample performs below median out of sample.
  - It needs the full record of all trials.
  — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253); [paper PDF](https://carmamaths.org/jon/backtest2.pdf)
- Bailey et al., "Pseudo-Mathematics and Financial Charlatanism" / "Backtest Overfitting and Out-of-Sample Performance".
  - With 5 years of daily data, testing more than about 45 independent configurations almost guarantees one with an in-sample annualised Sharpe ratio of 1 and an expected out-of-sample Sharpe ratio of 0.
  - The likelihood of overfitting cannot be estimated if the number of trials is not reported.
  — [CXO summary](https://www.cxoadvisory.com/big-ideas/insidiousness-of-overfitting-investment-strategies-via-iterative-backtests); [carmamaths](https://carmamaths.org/jon/backtest.pdf)

### Inferences
- There is a consistent pattern across 1999–2020. In-sample significance of trading rules is mostly a product of search, and the true number of trials is almost never disclosed. What survives tends to be small, concentrated in less efficient markets or periods, and fragile to costs.
- Retail indicator and signal vendors effectively run very large, undisclosed searches over parameters, assets and timeframes. They then show the best result, which is exactly the setting where DSR and PBO say the reported Sharpe ratio is inflated.

### Gaps
- I did not retrieve the exact formulas for minimum backtest length or minimum track-record length. Their published forms are in the SSRN papers above.
- I did not get exact counts from Harvey-Liu-Zhu; secondary sources are inconsistent (296, 313 or 316).

## Q6. Practical guidance: validating a rule (walk-forward, OOS, cost stress) and minimum sample sizes

### Takeaway
The literature suggests a clear validation protocol:
1. Record every trial.
2. Correct for multiple testing with the Reality Check/SPA, the FDR, or t > 3.
3. Report the Deflated Sharpe Ratio and the PBO.
4. Use true out-of-sample or walk-forward periods that the search never touched.
5. Stress-test costs, since modest costs erase most technical-rule profits.
6. Require enough history relative to the number of configurations tried.

### Cited Findings
- Multiple-testing corrections:
  - White's Reality Check (used in STW 1999);
  - Hansen's SPA, which is more powerful (Hsu-Kuan 2005);
  - the FDR, which keeps more true discoveries (Bajgrowicz-Scaillet 2012);
  - a t > 3.0 hurdle (Harvey-Liu-Zhu 2016).
  — sources as in Q5: [STW](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Sullivan_Timmermann_White.pdf), [Hsu-Kuan](https://econpapers.repec.org/RePEc:oup:jfinec:v:3:y:2005:i:4:p:606-628), [B&S](https://econpapers.repec.org/RePEc:eee:jfinec:v:106:y:2012:i:3:p:473-491), [HLZ](https://nber.org/papers/w20592)
- Overfitting diagnostics: the DSR deflates the observed Sharpe ratio for the number of trials and for skew/kurtosis, and the PBO via CSCV estimates the chance that the in-sample winner fails out of sample. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551); [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- Sample size versus trials: more than about 45 configurations on 5 years of data implies that a spurious Sharpe ratio of about 1 is expected, so required history grows with the number of trials. — [CXO / Bailey et al.](https://www.cxoadvisory.com/big-ideas/insidiousness-of-overfitting-investment-strategies-via-iterative-backtests)
- Transaction costs: low costs fully offset in-sample technical-rule profits on the DJIA (B&S 2012), and results across 23 markets are very sensitive to moderate costs. — [B&S](https://bashtage.github.io/kevinsheppard.com/files/teaching/mfe/advanced-econometrics/Bajgrowicz_Scaillet.pdf); [Springer](https://link.springer.com/content/pdf/10.1007/s11408-023-00433-2.pdf)
- Persistence: the best past rules cannot be identified in advance, so rolling or walk-forward re-selection needs to be tested itself. — [B&S 2012](https://econpapers.repec.org/RePEc:eee:jfinec:v:106:y:2012:i:3:p:473-491)
- Expect decay: budget for a 26–58% haircut on backtested or published edge after it goes live or is published. — [McLean & Pontiff](https://Www.Gwern.net/doc/economics/2016-mclean.pdf)

### Inferences
- Practical checklist (synthesis, not a single source):
  1. Freeze a holdout period, ideally the most recent one, and touch it once.
  2. Use walk-forward or CSCV rather than a single split.
  3. Count and log all parameter, asset and timeframe combinations tried.
  4. Report the DSR and PBO.
  5. Use a t-stat of at least 3 on mean returns, which takes roughly 9 years of daily data for an annualised Sharpe ratio of 1, since t ≈ SR·√years.
  6. Model spread, commission, slippage and swap at 1.5–2 times observed levels.
  7. Test across regimes (trends versus ranges) and instruments.
  8. For martingale or grid systems, judge on worst-case drawdown and time-to-ruin simulations, not win rate.
- The rule of thumb t ≈ SR·√T is my own derivation for i.i.d. returns. Under it, t = 3 requires T ≈ 9 years at a Sharpe ratio of 1 and about 36 years at a Sharpe ratio of 0.5. This shows why short retail track records (weeks or months) carry almost no statistical information.

### Gaps
- No single authoritative source on minimum numbers of trades (e.g. "at least 100–200 trades") was found. Such figures circulate in practitioner literature but were not verified this session.
