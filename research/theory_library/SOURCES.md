# Sources for the theory catalogue

These sources were checked on 2026-11-12 to confirm that each theory is widely taught and to take its canonical rules. Where sources disagree, the textbook default parameter was used. Broker and vendor pages are marketing material and were used for rules only, never for performance claims.

- **General day-trading styles** (trend, range, breakout, scalping, momentum, indicator use): [XTB](https://www.xtb.com/en/education/top-day-trading-strategies-for-forex-traders), [ActivTrades](https://www.activtrades.com/en/news/best-forex-day-trading-strategy-day-trading-forex-with-confidence), [Forex.com](https://forex.com/en/news-and-analysis/trading-strategies-guide/?amp=true), [CMC Markets](https://www.cmcmarkets.com/en-gb/forex/forex-day-trading-strategies), [DayTrading.com](https://www.daytrading.com/strategies).
- **Gold trading sessions** (London and New York): [Sarwa](https://www.sarwa.co/blog/gold-day-trading-strategy), [BingX](https://bingx.com/es-ar/learn/article/top-gold-trading-strategies-day-trading-swing-trading-smart-hedging).
- **ICT Silver Bullet, killzones and fair value gaps:**
  - [LuxAlgo](https://www.luxalgo.com/blog/ict-silver-bullet-setup-trading-methods/)
  - [Backtrex](https://backtrex.com/en/blog/ict-silver-bullet-strategy-trading-guide)
  - [Quantum Algo](https://www.quantum-algo.com/blog/ict-trading-strategy-complete-guide/)
  - [ChartingLens](https://chartinglens.com/blog/ict-silver-bullet-strategy)

  None publishes a reliable win rate, and the rules differ between sources. The simplified objective version used here is stated in `PREREGISTRATION.md`.
- **Connors RSI(2):** [StockCharts ChartSchool](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2), [LuxAlgo](https://www.luxalgo.com/library/concept/rsi-2/), [MQL5 article 17636](https://www.mql5.com/en/articles/17636). The original source is Connors & Alvarez, *Short Term Trading Strategies That Work* (2008).
- **Turtle rules and Turtle Soup:** Turtle system 1 (20/10) and system 2 (55/20) follow Curtis Faith, *Way of the Turtle* (2007). Turtle Soup follows Connors & Raschke, *Street Smarts* (1995). [TradingView Turtle Soup script](https://www.tradingview.com/script/32Y7ZsaN-Grok-Claude-Turtle-Soup-Strategy).
- **NR7:** Toby Crabel; Connors & Raschke. [Oxford Strat](https://oxfordstrat.com/?p=16086) reports that it is not tradeable after costs without extra rules.
- **Quantpedia strategy database** (650+ strategies, including calendar and crypto anomalies): [Quantpedia](https://quantpedia.com/cryptocurrency-trading-research), [Quantpedia: Best strategies 2021](https://quantpedia.com/the-best-systematic-trading-strategies-in-2021-part-2/).
- **Larry Williams volatility breakout:** Larry Williams, *Long-Term Secrets to Short-Term Trading* (1999). The rule is a stop order at the open ± k × the previous range, with k = 0.6 as a common default.
- **Indicators:**
  - Ichimoku: Hosoda (9,26,52);
  - Supertrend (10,3) and Parabolic SAR (0.02, 0.2): Wilder;
  - ADX (14): Wilder;
  - Bollinger (20,2);
  - Keltner (20,1.5);
  - Stochastic (14,3,3);
  - CCI (20);
  - Williams %R (14).

  These are the platform defaults on MetaTrader and TradingView.

## Addendum 1 sources (batch F)

- **UT Bot, Squeeze Momentum, SSL channel:** [TradingView UT Bot scripts](https://in.tradingview.com/scripts/utbotalert/), [LuxAlgo UT Bot](https://www.luxalgo.com/library/indicator/RIKFamAD-ut-bot-alerts/), [PickMyTrade: top free TradingView indicators](https://blog.pickmytrade.io/top-free-indicators-and-strategies-on-tradingview/). The PickMyTrade page says Squeeze Momentum is the most-liked TradingView indicator.
- **Smart money concepts (order blocks, BOS):**
  - [MQL5: order blocks in an EA](https://www.mql5.com/en/blogs/post/779413)
  - [Backtrex ICT order block](https://backtrex.com/en/blog/ict-order-block-backtest-strategy)
  - [PickMyTrade SMC Structure script](https://id.tradingview.com/script/p81vkiBb-SMC-Structure-PickMyTrade)
  - [MQL5 article 22078](https://www.mql5.com/en/articles/22078)

  These sources note that the definitions are loose. The objective version used here is in the pre-registration.
- **YouTube strategies (200 EMA + MACD, RSI):**
  - [Quant Factory: backtesting YouTube strategies #1](https://medium.com/quant-factory/backtesting-popular-strategies-from-youtube-1-e802670369c6)
  - [TradingView: Testing a YouTube MACD strategy](https://my.tradingview.com/chart/SPX/j8ZIXCFi-Testing-a-Youtube-MACD-Strategy), with an advertised 86% win rate against 32% in a 27-year test
  - [TradingView: RSI is it any good](https://www.tradingview.com/chart/OIS/nbEKyTK3-RSI-Is-it-any-good/)
  - [MQL5 forum: viral MACD video](https://www.mql5.com/en/forum/492013)
- **Chart patterns:**
  - [Quantpedia: double bottom](https://quantpedia.com/technical-analysis-report-methodology-double-bottom-country-trading-strategy/) (its breakouts did better than its bounces)
  - [QuantifiedStrategies: double top](https://quantifiedstrategies.substack.com/p/double-top-chart-pattern-trading)
  - [MQL5: testing head and shoulders](https://www.mql5.com/en/articles/5358)
  - [TheRightTrader: 1-2-3 reversal](https://therighttrader.com/learn/trading-strategies/one-two-three-reversal)
  - [TitanFX: H&S rules](https://research.titanfx.com/technical-analysis/candlestick-chart/head-and-shoulders-top-bottom)

## Addendum 2 sources (batch G)

- **Intraday momentum:**
  - Gao, Han, Li & Zhou, "Market intraday momentum", *JFE* 129(2), 2018 ([RePEc](https://econpapers.repec.org/RePEc:eee:jfinec:v:129:y:2018:i:2:p:394-414), [Alpha Architect](https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/))
  - [16-market extension (Reading)](https://reading-9.eprints-hosting.org/95566/1/Accepted-Version.pdf)
  - [QuantConnect replication](https://www.quantconnect.com/learning/articles/investment-strategy-library/intraday-etf-momentum)
- **Dual Thrust:** [QuantConnect tutorial](https://www.quantconnect.com/tutorials/strategy-library/dual-thrust-trading-algorithm) (negative Sharpe on SPY 2004–2017), [ProRealCode](https://www.prorealcode.com/prorealtime-indicators/dual-thrust-strategy-indicator/), [TradingView BTC Dual Thrust](https://www.tradingview.com/script/7Q7nTaV3-BTCUSD-Dual-Thrust-1H).
- **Pre-FOMC drift:** [Lucca & Moench (Boston Fed presentation)](https://www.bostonfed.org/economic/conf/Macro-Finance-2012/presentations/lucca.pdf), [NY Fed staff report 1052](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1052.pdf).
- **Gold/silver ratio:** [QuantifiedStrategies](https://quantifiedstrategies.substack.com/p/gold-silver-chart-ratio-strategy), [DEV community backtest](https://dev.to/retail_vest_1fd4e7c362443/gold-silver-ratio-strategy-how-1058-returns-tell-the-real-story-484c), [FXStreet](https://www.fxstreet.com/analysis/gold-to-silver-ratio-analysis-mean-reversion-trade-202510291207).
- **Bitcoin seasonality and calendar effects:**
  - [Quantpedia: intraday/overnight anomalies in Bitcoin](https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/)
  - [Quantpedia: calendar effects in Bitcoin](https://quantpedia.com/are-there-any-simple-calendar-effects-in-bitcoin-market/)
  - [Concretum: Bitcoin intraday trend](https://concretumgroup.com/seasonality-in-bitcoin-intraday-trend-trading/)
- **KAMA:** Kaufman, *Smarter Trading* (1995); [ForexTester](https://forextester.com/blog/adaptive-moving-average/); [MQL5](https://www.mql5.com/en/blogs/post/12393).
- **Alligator and fractals:** Bill Williams, *Trading Chaos* (1995).
- **Aroon:** Chande (1995).
- **Vortex:** Botes & Siepman (2010).
- **TRIX:** Hutson (1983).
- **KST:** Pring.
- **Keltner:** Chester Keltner, ATR version by Raschke.

Defaults are those of TradingView and MetaTrader.
