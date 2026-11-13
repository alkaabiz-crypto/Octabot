# Primary texts of four trend/momentum papers (Hurst–Ooi–Pedersen, Faber, Gao et al., Zarattini–Pagani–Barbon)

Method note (2026-11-11): **none of the four primary texts could be read in this session.** The network is more restricted than on 2026-11-10. Both curl and WebFetch were refused (proxy 403 / DNS "ENOTFOUND") for the following hosts:
- Hurst: aqr.com, and the mirror ecapital.ch.
- Faber: mebfaber.com, community.portfolio123.com, trendfollowing.com, pm-research.com.
- Gao: smallake.kr, c.mql5.com, apps.olin.wustl.edu (Guofu Zhou's faculty pages).
- Zarattini: concretumgroup.substack.com, econpapers.repec.org, quantifiedstrategies.com.
- General: web.archive.org, scholar.archive.org, export.arxiv.org, diva-portal.org, wp.lancs.ac.uk, sciencedirect.com, alphaarchitect.com, ideas.repec.org.

GitHub API access to third-party repos is also disabled. The reachable hosts were arxiv.org, quantpedia.com, www.cxoadvisory.com (paywalled after its first paragraph) and bis.org.

Web search found mirror URLs for every paper (listed below). A rerun with those hosts allowed should be able to close most gaps. **Everything below that is not from arXiv is a SECONDARY summary from search-engine snippets and is flagged as such.** Numbers recalled from memory are not stated as findings. They are listed under Gaps as "to verify".

## 1. Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing" (AQR 2014 / JPM 2017)

### Takeaway
The primary text was not read. Secondary sources agree on the scope: 67 markets in four asset classes, 1880–2016, a TSMOM strategy, and no losing decade. They give gross annual returns of about 18.0% and about 11.0% net of fees and costs, with 9.7% volatility. One secondary source gives a net Sharpe of 0.76 (7.3% a year over cash), but that does not reconcile with 11.0%/9.7% unless cash returns are subtracted. The construction details (1/3/12-month equal weight, the vol target, the "2-and-20" fee model) and the decade and commodity tables remain **UNVERIFIED**.

### Cited Findings
- **Scope (SECONDARY):** the 2017 version covers 67 markets across commodities, equities, bonds and currencies, 1880–2016. — [Alpha Architect, "Trend Following is Everywhere"](https://alphaarchitect.com/trend-following-is-everywhere/) (search snippet; page itself blocked)
- **Returns (SECONDARY):** "gross annualized returns were 18.0 percent over the full period, with net returns (after fees) of 11.0 percent, with a volatility of 9.7 percent". — [Alpha Architect](https://alphaarchitect.com/trend-following-is-everywhere/) (search snippet)
- **Decades and Sharpe (SECONDARY, non-institutional source):** "fourteen decades. Not one losing decade". "After costs and fees, the strategy returned 7.3% a year above cash, with a Sharpe ratio of 0.76." — [Investing Canvas Substack](https://investingcanvas.substack.com/p/tales-from-the-underground-137-years) (search snippet)
- **AQR forward-looking view (SECONDARY, date unknown):** an AQR document gives an expected "Sharpe Ratio of 0.4 net of fees and transaction costs", well below the historical figure. — search snippet attributed to [Efficient Capital / AQR](https://www.efficient.com/resources/a-century-of-evidence-on-trend-following-investing)
- **Version history:** CBS lists both a main paper and an "Executive Summary". The earlier version (2012–2014) begins in 1903, not 1880, so numbers quoted from different versions are not comparable. — [CBS Research Portal](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing/); [CBS Exec Summary](https://research.cbs.dk/en/publications/a-century-of-evidence-on-trend-following-investing-executive-summ/)
- **Horizon finding, as characterised by a later arXiv paper (PRIMARY for the citing paper only):** "Hurst et al. (2017) find that twelve-month momentum strategies deliver strong and stable returns over more than a century of global data, while shorter-term implementations tend to be noisier and less persistent." The same paper cites Winton (2013) for 1984–2013 Sharpe ratios: 1.12 for intermediate speed, against 0.87 for short and 0.81 for long. — [Etienne et al., arXiv 2510.23150, Sec. 1](https://arxiv.org/pdf/2510.23150)
- **Mirror URLs found but blocked:** [ecapital.ch PDF](http://www.ecapital.ch/downloads/AQR_A%20Century_of_Evidence_on_Trend-Following.pdf); SSRN abstract_id=2993026.

### Inferences
- If 11.0% is the net total return and 7.3% is the net excess return over cash, the two figures imply an average cash yield of about 3.7%. That is plausible over 1880–2016, so the secondary figures may be consistent. Then 7.3%/9.7% ≈ 0.75 matches the 0.76 Sharpe. This is my arithmetic, not a reported reconciliation.
- Treat the century-long Sharpe ratio as an upper bound for a builder. AQR's own forward-looking net Sharpe was about 0.4, and Bouchaud et al. 2026 (see the earlier notes, Sec. 6) show fast trend decaying after 2009. In those results commodities did not decay.

### Gaps
- **UNVERIFIED against the primary text:**
  - signal construction, i.e. an equal-weighted average of 1-, 3- and 12-month TSMOM;
  - per-market sizing to a constant vol (the ex-ante 40% figure comes from Moskowitz–Ooi–Pedersen 2012; whether HOP use it, or scale the portfolio to 10% vol, needs checking);
  - monthly rebalancing;
  - the fee model (2% management and 20% performance fee) and the asset-class transaction-cost assumptions, including the higher costs assumed for earlier periods;
  - the decade-by-decade net table, the gross/net drawdown, and the 2012–2016 post-original-sample results;
  - any commodity, gold or crude sub-results.
- None of these appeared in any reachable source. Allowing aqr.com or ecapital.ch would close them.

## 2. Faber, "A Quantitative Approach to Tactical Asset Allocation" (2006/2007 JWM; 2013 update; 2018 "Revisited 10 Years Later")

### Takeaway
The rule is confirmed by multiple secondary sources: at each month-end, hold an asset if its monthly close is above its 10-month SMA, otherwise hold cash. The 2013 update added 2008–2012 data. A blog summary of that update reports figures for the 2006–2012 post-publication period: volatility 7.3%, max drawdown 9.4% (about 80% lower than buy-and-hold), Sharpe about 0.6, "almost quadrupled". These figures could not be checked against Faber's tables. The 2018 JWM revisit's numbers were not found.

### Cited Findings
- **Rule (SECONDARY):** "buy when monthly price > 10-month SMA and sell and move to cash when monthly price < 10-month SMA". When the market is below its 10-month SMA, returns are on average 60% lower and volatility 30% higher. — search summary of [the7circles.uk](https://the7circles.uk/tactical-asset-allocation-meb-faber/) and [ResearchGate listing](https://www.researchgate.net/publication/228202718_A_Quantitative_Approach_to_Tactical_Asset_Allocation)
- **2013 update scope (SECONDARY):** it updates the 2006 white paper with 2008–2012 data, and the models "performed well in real-time, achieving equity like returns with bond like volatility and drawdowns". — search snippet ([the7circles.uk](https://the7circles.uk/tactical-asset-allocation-meb-faber/))
- **2006–2012 "out-of-sample" figures (SECONDARY, blog):** "volatility is down to 7.3% pa, the max drawdown is reduced by 80% (to 9.4%) and Sharpe is almost quadrupled (to 0.6)". — search snippet ([the7circles.uk](https://the7circles.uk/tactical-asset-allocation-meb-faber/)). The benchmark, the asset set (probably the 5-asset GTAA) and the CAGR are not given in the snippet.
- **Parameter robustness (SECONDARY):** an independent check finds that "the 10-month SMA is not the optimum parameter for any of the statistics, but … there is very broad parameter stability across the five moving average lengths". — search snippet ([LinkedIn, L. Scott 2022, "Revisited Almost 15 Years Later"](https://www.linkedin.com/pulse/quantitative-approach-tactical-asset-allocation-revisited-louis-scott))
- **2018 revisit:** "A Quantitative Approach to Tactical Asset Allocation Revisited 10 Years Later", Journal of Wealth Management, Multi-Asset Special Issue 2018. Its results were not retrieved. — search snippet
- **Earlier-pass secondary figure (still unverified):** Swedroe reports a "0.45 → 0.80 Sharpe" and a "return from 9.8% to 11.3%" for the multi-asset version. — see the prior notes, Sec. 8
- **Mirror URLs found but blocked:** [mebfaber.com SSRN-id962461.pdf](https://mebfaber.com/wp-content/uploads/2016/05/SSRN-id962461.pdf), [portfolio123 PDF](https://community.portfolio123.com/uploads/short-url/kbsA05k7XScAkgohfEGeGkwoOD3.pdf), [trendfollowing.com CMT-Simple.pdf](https://www.trendfollowing.com/whitepaper/CMT-Simple.pdf), [pm-research full text](https://www.pm-research.com/content/iijpracapp%3A%3A%3A6%3A%3A%3A1%3A%3A%3A1.13.full.pdf).

### Inferences
- The rule is a slow, monthly signal (about 1–3 switches a year per asset), so costs are a minor issue for it, unlike the intraday rules below.
- The "Sharpe 0.6" for 2006–2012 is a small, crisis-dominated window (it includes 2008). It mainly shows drawdown control, not a return edge.

### Gaps
- **UNVERIFIED:**
  - the original sample (1973–2005 or 1972–2012 in the update) and the exact asset list (US stocks, EAFE, 10-year Treasuries, GSCI, REITs);
  - whether returns include dividends or interest and T-bill cash;
  - the cost or slippage assumption (the original reportedly ignores costs; not verified);
  - the exact CAGR, Sharpe and drawdown tables for the 2006/2013/2018 versions;
  - the GSCI/commodity-only timing results.
- No gold- or oil-specific results from Faber were found.

## 3. Gao, Han, Li & Zhou (JFE 2018), "Market intraday momentum", and later replications on oil and gold

### Takeaway
The publication details and core claim are confirmed by abstract-level sources. The sample is the S&P 500 ETF (SPY), 1993–2013. The return from the previous close to the end of the first half-hour predicts the last half-hour return. The effect is stronger on volatile days, high-volume days, recession days and major macro-news days. The exact windows, OOS R², timing-strategy returns and cost results could not be read. Later evidence on oil and gold is mixed:
- **US crude via USO (2006–2018):** momentum holds in- and out-of-sample (Wen et al. 2021).
- **Chinese crude futures:** no momentum; reversal instead.
- **Chinese gold futures:** the effect disappeared after night trading launched.
- **MNQ / micro gold 2021–2025 (arXiv 2026):** no OHLCV intraday signal survived realistic friction.

### Cited Findings
- **Publication details:** Gao, Han, Li, Zhou, *Journal of Financial Economics* 129(2), 2018, pp. 394–414. — [EconPapers](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414) (search snippet)
- **Core claim (abstract):** using high-frequency S&P 500 ETF data from 1993–2013, the first half-hour return, measured from the previous day's close, predicts the last half-hour return. The predictability is stronger on more volatile days, higher-volume days, recession days and major macroeconomic news release days. — [SSRN 2440866](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866) (search snippet; SSRN itself blocked)
- **Working-paper title:** "Intraday Momentum: The First Half-Hour Return Predicts the Last Half-Hour Return". — [ResearchGate](https://www.researchgate.net/publication/272303487_Intraday_Momentum_The_First_Half-Hour_Return_Predicts_the_Last_Half-Hour_Return)
- **Crude oil, USO ETF (SECONDARY):** Wen, Gong, Ma, Xu (2021), *Economic Modelling* 95, 374–384, using one-minute USO data for 2006–2018. The first half-hour return "significantly and positively predicts the last half-hour return, both IS and OS". The authors attribute the predictability to the overnight component. — [ScienceDirect abstract](https://www.sciencedirect.com/science/article/abs/pii/S0264999319310417) (search snippet); bibliographic details confirmed in [arXiv 2605.04004 references](https://arxiv.org/pdf/2605.04004)
- **Chinese crude futures (SECONDARY):** the first half-hour return "cannot forecast the last half-hour return" in either the day or night session, and the authors find intraday reversal. — [Economic Modelling 2021, S0264999321000134](https://www.sciencedirect.com/science/article/abs/pii/S0264999321000134) (search snippet)
- **Chinese gold and silver futures (SECONDARY):** before night trading, the first daytime half-hour was the efficient predictor. After night trading launched, "the predictive ability of the first half-hour return in the day session disappears". — [J. Int. Fin. Markets 2025, S1044028325000110](https://www.sciencedirect.com/science/article/abs/pii/S1044028325000110) (search snippet)
- **Chinese commodity futures (SECONDARY):** copper, steel, soybean and soybean meal show a positive first-half-hour → last-half-hour effect. — [RIBAF, S0275531919311328](https://www.sciencedirect.com/science/article/abs/pii/S0275531919311328) (search snippet)
- **Falsification study on futures (PRIMARY, arXiv 2605.04004, Mesfin, May 2026, independent and not peer-reviewed):**
  - **Design:** 14 OHLCV intraday signal families on MNQ, 947 days of 5-minute bars, 2021–2025, with an expanding-window walk-forward and OOS years 2023/2024/2025.
  - **Pass criteria (all required):** net T ≥ 2.0, at least 30 trades per fold, positive net return, consistent sign across years, and permutation p < 0.05.
  - **Result:** "None passed all five". Eleven families had a gross edge of 0.07–1.50 points per trade, below the 2.0-point MNQ round-trip friction ($4 per micro).
  - **Closest near-miss:** a first-30-minute Kalman-velocity "gap continuation short", explicitly motivated by Wen et al.'s first-half-hour result. It earned net +14.52 points (T = 1.46) on only 35 OOS trades, with 2024 at −11.87 (Table 6).
  - **Micro gold:** MGC (1,091 days, 0.50-point friction) was tested only with OU mean reversion. "All configurations remain negative" (Table 9).
  - **Caveat:** the paper does **not** test the exact Gao sign rule.
  — [arXiv 2605.04004, Abstract, Sec. 2, 4.4, 4.8](https://arxiv.org/pdf/2605.04004)
- **Mirror URLs found but blocked:** [smallake.kr SSRN PDF](https://www.smallake.kr/wp-content/uploads/2015/01/SSRN-id2440866.pdf), [c.mql5.com PDF](https://c.mql5.com/forextsd/forum/173/intraday_momentum_-_the_first_half-hour_return_predicts_the_last_half-hour_return.pdf), and international replications ([Lancaster FoFI 2020](http://wp.lancs.ac.uk/fofi2020/files/2020/04/FoFI-2020-092-Zeming-Li.pdf), [Reading accepted version](https://centaur.reading.ac.uk/95566/1/Accepted-Version.pdf)).

### Inferences
- For oil, the only positive US evidence uses the USO ETF, and it reports both IS and OS predictability. That supports testing a "sign of the first half-hour, including the overnight move" rule on WTI CFDs/futures. Chinese crude evidence is negative.
- For gold, no US (COMEX/GLD) replication was found. The Chinese evidence suggests the effect fades once trading is near-24h, which describes COMEX gold. This is an inference, not a tested result.
- A single last-half-hour round trip per day has a small gross edge. The MNQ study shows that liquid-futures friction (about 1–2 index points) is enough to absorb typical intraday OHLCV edges. Cost modelling is decisive.

### Gaps
- **UNVERIFIED (memory only, to verify):**
  - the predictor is the return from the previous 16:00 close to 10:00 ET, and the target is 15:30–16:00 ET;
  - in-sample R² is about 1.6%, with OOS R² of about 1.2–1.4% (the earlier note's figure);
  - the market-timing strategy (long or short SPY in the last half-hour by the sign of the first) has an annualised return of about 6–7% and a Sharpe of about 1;
  - the cost and break-even analysis;
  - whether the paper includes other ETFs. Some versions add the 12th half-hour as a predictor.
- No US GLD/GC replication was found. The Wen et al. USO coefficients and OOS R² were not read.

## 4. Zarattini, Pagani & Barbon (2025), "Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins"

### Takeaway
The rule, from the earlier CXO paraphrase, is confirmed again here in summary form:
- a long-only Donchian ensemble over 9 lookbacks from 5 to 360 days, entered on a close above the N-day maximum close;
- a ratcheting trailing stop at the midpoint of the N-day max and min closes;
- sizing at 25% target vol over 90-day realised vol, with leverage capped at 200%;
- a universe of the top 20 liquid coins;
- costs tested at 0.10%, 0.25% and 0.50%.

The new finding is a **BTC-only** result, from the authors' firm summary as seen in a snippet: from Jan 2015, net CAGR 30% and Sharpe 1.56. The rotational top-20 portfolio has Sharpe above 1.5 and alpha of 10.8% against BTC, net of fees. Results at each cost level, ETH-only results and drawdowns remain unverified.

### Cited Findings
- **Identifiers:** Swiss Finance Institute RP 25-80, SSRN 5209907, 38 pages. First posted Apr/May 2025, revised Oct 2025. — [IDEAS/RePEc](https://ideas.repec.org/p/chf/rpseri/rp2580.html); [abarbon.com paper page](https://abarbon.com/papers/catching-crypto-trends) (search listing)
- **Abstract:** applied to "a rotational portfolio of the top 20 most liquid coins", the model achieved "a Sharpe ratio above 1.5 and an annualized alpha of 10.8% versus Bitcoin", net of fees. — [IDEAS/RePEc](https://ideas.repec.org/p/chf/rpseri/rp2580.html) (search snippet)
- **BTC-only (SECONDARY, authors' firm):** "Applied to Bitcoin from January 2015, the ensemble model delivers a net-of-fee CAGR of 30% and a Sharpe ratio of 1.56." — [Concretum Group summary](https://concretumgroup.com/catching-crypto-trends-a-tactical-approach-for-bitcoin-and-altcoins/) (search snippet; host blocked)
- **Costs (SECONDARY):** the authors "consider transaction costs of 0.10%, 0.25% and 0.50% and propose a way to mitigate impact of these costs". — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/) (paywalled)
- **Rotational portfolio Sharpe (TERTIARY, GitHub issue):** cited as 1.58 for 2015–2025, "net of fees at 0.10% to 0.50%". It conflicts slightly with ">1.5", and it is unclear which cost level it applies to. — [GitHub issue #137](https://github.com/zebadee2kk/DeFi-TraderStack-Agent/issues/137) (search snippet; not authoritative)
- **Earlier pass (CXO paraphrase):**
  - 18% net CAGR and 11% net alpha against BTC, Jan 2015 to mid-Mar 2025, at 0.10% costs;
  - data on 21,616 assets, 2010–2025;
  - universe filter: listed at least 1 year and 30-day median volume of at least $2M.
  — [CXO Advisory](https://www.cxoadvisory.com/technical-trading/crypto-asset-trend-following-strategies/) via the prior notes, Sec. 7

### Inferences
- Note the inversion: the BTC-only CAGR (30%) is higher than the rotational portfolio's 18% (CXO), while their Sharpe ratios are similar (about 1.56 and above 1.5). The rotational portfolio's main benefit is alpha and diversification against BTC, not a higher Sharpe. Both are vol-targeted, so CAGR depends on leverage use. This reconciles the sources if both numbers are right.
- The 9-lookback ensemble with daily stops trades often on the short lookbacks (5–30 days). That is presumably why the authors test up to 0.50% costs and propose a mitigation, plausibly a rebalance threshold or a monthly rebalance; CXO mentions monthly rebalancing. The mitigation is not verified.

### Gaps
- **UNVERIFIED:**
  - net CAGR, Sharpe and max drawdown at 0.25% and 0.50%;
  - the mitigation method itself;
  - ETH-only results (none found in any source);
  - the BTC-only drawdown and the cost level behind the 30%/1.56 figure;
  - 2022–2025 sub-period results;
  - the correlation and diversification against traditional trend-following (the abstract says this is examined).
- Allowing concretumgroup.com, concretumgroup.substack.com/p/catching-crypto-trends, or abarbon.com would close these.
