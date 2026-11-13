# Candidate register (by category), 13 November 2026

Every idea has a **permanent number** in one of the four categories. Each category is tested by its own method ([`PLAN.md`](PLAN.md); protocols in [`categories/`](categories/)). A result from one category's test is **not** a verdict in another: for example, a strategy that loses does not prove its indicator carries no information.

**Status codes**
- **REJECTED / NOT SUPPORTED / NONE:** tested and failed.
- **DECAYED:** true in older data, not now.
- **WATCH:** positive but not yet proven.
- **RUNNING:** a forward paper test is in progress.
- **PENDING:** not yet tested with this category's method.

## Indicators (IND): a measurement. Does it carry information about future moves?

IND batch 001 (`new_discovery/ind_batch_001/`, 2026-11-13) tested IND-001, IND-003 to IND-018 and IND-020. Still PENDING: IND-002 (covered by THE-009), IND-019 and IND-021.

| ID | Candidate | Evidence so far (as part of strategies) | Indicator verdict |
|---|---|---|---|
| IND-001 | Coinbase premium z-score (BTC; Coinbase USD vs Binance USDT) | STR-008 positive in every period since 2017; failed vs Bitstamp and on ETH | WEAK (IND batch 001: 5-day IC positive in every period, not significant) |
| IND-002 | Futures-curve slope ln(F1/F2) (WTI, natural gas) | THE-009: strong pre-2010, faded since | PENDING |
| IND-003 | KST (Know Sure Thing) | Gold KST studies; library G7: failed as rules | NONE (IND batch 001) |
| IND-004 | Distance from session/daily VWAP | RSI+VWAP studies; STR-023 promising on BTC/ETH | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-005 | RSI (14, 2) | Library B1/B2, RSI+VWAP studies: failed as rules | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-006 | MACD | Library A3, F6: failed | NONE (IND batch 001) |
| IND-007 | Moving-average trend (EMA 9/21, SMA 50/200) | Library A1/A2, MOM50: failed or mixed | NONE (IND batch 001) |
| IND-008 | Supertrend | Library A4: failed | NONE (IND batch 001) |
| IND-009 | Parabolic SAR | Library A5: failed | NONE (IND batch 001) |
| IND-010 | ADX / DMI | Library A6: failed | NONE (IND batch 001) |
| IND-011 | Donchian channel position | Library A7/A8: failed; Donchian 20 BTC paper (STR-009) | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-012 | Ichimoku cloud | Library A9: failed | NONE (IND batch 001) |
| IND-013 | Bollinger %B and squeeze | Library B3, A12, F1: failed | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-014 | Stochastic | Library B4; oil stochastic paper (STR-012) | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-015 | CCI | Library B5: failed | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-016 | Williams %R | Library B6: failed | NONE (IND batch 001) — contrarian at 1h, see THE-017 |
| IND-017 | Williams Vix Fix | Community round 2: passed 2025–26 on BTC, then failed on new data | NONE (IND batch 001) |
| IND-018 | HAR realised-volatility forecast | Batch 002 E006: better than EWMA on 6 markets (WATCH as a forecast) | **INFORMATIVE** (IND batch 001: predicts next-day volatility, 5/5 markets) |
| IND-019 | Two-state HMM regime probability | Batch 002 E007: WATCH on USD/JPY only | PENDING |
| IND-020 | 20-day momentum (time-series) | Library A11, batch 001 D002: failed | NONE (IND batch 001) |
| IND-021 | Other TradingView built-ins and community scripts (about 2,950 variants: Aroon, Vortex, TRIX, KAMA, Alligator, Hull, Keltner, Chandelier, Waddah Attar, …) | `multi_market`, `long_history`, `tradingview_*`, `community_indicators*`: 0 survivors as rules | PENDING (group) |

## Strategies (STR): a complete trading rule. Does it make money after costs on new data?

| ID | Candidate | Verdict | Where |
|---|---|---|---|
| STR-001 | ETH Fibonacci 61.8% pullback, 1h (ETH_FIB) | **REJECTED**: its backtest edge came from look-ahead; causal −20 / −10 bp. Paper test RUNNING (other session). | `audits/library_candidates/` |
| STR-002 | Oil Fibonacci pullback, 1h (OIL_FIB) | **REJECTED**: causal −2.5 / −9.6 bp; −13.6 bp with Hyperliquid fees. Paper RUNNING. | same |
| STR-003 | Gold FVG fill, 1h (GOLD_FVG) | **REJECTED**: causal about 0; −5.3 bp with Hyperliquid fees. Paper RUNNING. | same |
| STR-004 | BTC Pivot Reversal BUY, 1h | **RUNNING** (0 / 400 legs) | `pivot_reversal_paper/` |
| STR-005 | ETH Pivot Reversal BUY, 1h | **RUNNING** (0 / 400) | `eth_pivot_paper/` |
| STR-006 | Gold KST + VWAP BUY, 48 h time stop | **RUNNING** (0 / 200) | `gold_kst_paper/` |
| STR-007 | Gold KST + VWAP, 2×ATR stop, flat before news | **RUNNING** (0 / 200) | `gold_kst_risk_paper/` |
| STR-008 | Coinbase premium, 24 h hold (BTC) | **WATCH**, forward **RUNNING** since 2026-11-13 (first look at 100 trades) | `new_discovery/batch_003/`, `forward_h4/` |
| STR-009 | Donchian 20 BUY, BTC | Other session; paper paused with its commits | other branch |
| STR-010 | Gold Asia session | Other session; RUNNING | other branch |
| STR-011 | Gold MOM50 | Other session; RUNNING | other branch |
| STR-012 | Oil Stochastic | Other session; RUNNING | other branch |
| STR-013 | Trend ensemble (BTC) | Other session; RUNNING | other branch |
| STR-014 | Theory-library screen: 63 rules, 535 combinations | **REJECTED**: no causal survivor | other branch, audited here |
| STR-015 | Batch 001: pairs, relative strength, regime switch, machine-learning direction | **REJECTED** | `new_discovery/batch_001/` |
| STR-016 | Batch 002: volatility-managed exposure; HMM regime filter | **REJECTED**, except the HMM filter on USD/JPY (WATCH) | `new_discovery/batch_002/` |
| STR-017 | News-surprise and release-reaction trades (CPI, NFP, FOMC, EIA; 14 markets) | **REJECTED** (0 / 56 and 0 / 225) | `news_surprise/`, `news_markets/` |
| STR-018 | ADP pre-positioning / contrarian | Exploratory forward observation **RUNNING** (daily run) | `news_surprise/` |
| STR-019 | RSI + VWAP entries (oil, gold) | **REJECTED** | `oil_rsi_vwap/`, `gold_rsi_vwap/` |
| STR-020 | Indicator scans: community, TradingView built-ins and originals, requested indicators, multi-market, long history | **REJECTED** (0 survivors after correction) | respective folders |
| STR-021 | Hourly time-of-day effects | **REJECTED** | `hourly_time_signals/` |
| STR-022 | Signal comparison: 3 approaches on BTC and UK oil | **REJECTED** (none survives correction; ranking reversed in the final test) | `signal_comparison/` |
| STR-023 | **VWAP momentum BUY with 2×ATR stop and 3×ATR trail (BTC, replicated on ETH)** | **WATCH**, forward paper test **RUNNING** from 2026-11-14 (BTC and ETH, Binance prices, rule V2; first look at 100 trades per market) | `rsi_vwap_study/`, `new_discovery/forward_str023/` |
| STR-024 | ORB, zone reversal and other session studies | **REJECTED** | other branch |
| STR-025 | Volatility-scaled sizing overlay using IND-018 (HAR forecast), applied to STR-023 | **MIXED** (2/4: slightly higher mean R everywhere, lower drawdown in only 2 of 4 samples); read-only shadow on STR-023's forward ledger | `new_discovery/str_025/` |

## Theories (THE): a claim about how markets behave. Is it true, and is it still true?

| ID | Candidate | Verdict | Where |
|---|---|---|---|
| THE-001 | Theory #2: previous-day range zones + 15m signal candle (user) | **NOT SUPPORTED** (0 / 60) | other branch, `zone_reversal_study` |
| THE-002 | Theory #2b: same-day opening-range zones (user) | **NOT SUPPORTED** (0 / 60; all negative) | `new_discovery/user_theories_001/` |
| THE-003 | "John Wick": wick rejection predicts reversal (user) | **NOT SUPPORTED** (0 / 19 new timeframes; 1h 0 / 7) | same |
| THE-004 | BTC CME weekend gaps get filled | **NOT SUPPORTED** (−24 to −83 bp per trade in every period) | `new_discovery/batch_003/` |
| THE-005 | Round numbers act as support and resistance (Osler) | **NOT SUPPORTED** (reversal: round levels reverse *less* often on BTC and gold) / **DECAYED** (acceleration after crossing: gold 2020–24 only). Trading rules also lost after costs. | `new_discovery/the_005/RESULTS.md` |
| THE-006 | Gold and silver fall around the London fix | **DECAYED** (gold about 0; literature effect was pre-2015) | same |
| THE-007 | Pre-FOMC drift in stock indices | **NOT SUPPORTED** in Exness CFDs | `news_markets/` |
| THE-008 | Pre-holiday effect (US indices, DAX) | **WATCH** (S&P 500 and Nasdaq positive in all periods, not significant) | `new_discovery/batch_002/` |
| THE-009 | Commodity term-structure (backwardation) premium | **DECAYED** (WTI +1.9%/month 1986–2009; +0.2% since) | `new_discovery/batch_004/` |
| THE-010 | Market reactions to US releases continue after the first minutes | **NOT SUPPORTED** (moves done within seconds); silver after CPI is a lead only | `news_surprise/`, `news_markets/` |
| THE-011 | BTC leads ETH (lead-lag) | **NOT SUPPORTED** | `new_discovery/batch_002/` |
| THE-012 | Scaling exposure by volatility improves risk-adjusted returns | **NOT SUPPORTED** | `new_discovery/batch_002/` |
| THE-013 | Volatility has long memory (HAR beats EWMA) | **WATCH** (6 markets) | `new_discovery/batch_002/` |
| THE-014 | The Coinbase premium measures US demand that leads BTC | **PARTLY SUPPORTED**: BTC positive in every period since 2017 against Binance USDT (2017–19 +80 bp, p < 0.001) **and** against OKX USDT (all 4 periods positive); **not** against Bitstamp USD; not on ETH (last 16 months). So it is a USD-vs-USDT demand signal. | `new_discovery/batch_003/` |
| THE-015 | Calendar effects: turn of month, weekdays, overnight, weekend | **NOT SUPPORTED** | library, `hourly_time_signals/` |
| THE-016 | ICT / SMC concepts: fair value gaps, order blocks, Judas swing, Silver Bullet, liquidity sweeps | **NOT SUPPORTED** (library D1–D4, F9–F12; FVG's apparent edge was look-ahead) | other branch, audited here |
| THE-017 | Short-horizon reversal: overbought/oversold readings (RSI, Williams %R, Donchian, Bollinger…) predict a small opposite move over the next hour (BTC, EUR/USD) | **NOT SUPPORTED** (event study 2026-11-13: TEST effect wrong-signed on BTC, not significant on EUR/USD, 0/6 replications; ≤ 0.3 bp per event vs 1–12 bp costs) | `new_discovery/the_017/RESULTS.md` |

## Signals (SIG): someone else's calls. Profitable, and are the reported results accurate?

| ID | Candidate | Logged | Prospective | Verdict |
|---|---|---|---|---|
| SIG-001 | SignalPro free signals, gold (XAUUSD and XAUUSD 24/7) | 30 | 2 | **NOT YET DECIDABLE** (needs ≥ 50 prospective). Earlier mostly-retrospective analysis: no profit after realistic entries. Claims: **INACCURATE** in places (one trade shown as both "Stop Loss Hit" and "TP1 Reached"; "TP1 then breakeven" reported as success). |
| SIG-002 | SignalPro free signals, oil (USOIL) | 2 | 0 | NOT YET DECIDABLE |
| SIG-003 | SignalPro free signals, other (BTC, silver, DXY) | 3 | 1 | NOT YET DECIDABLE |

**To make SIG decidable:** screenshot each signal **as soon as it is posted** ("Trade Active, 0/3"), with the clock visible.

## How to add a candidate

Send it with a short description. It gets the next number in its category, is pre-registered with that category's protocol, and is tested.
