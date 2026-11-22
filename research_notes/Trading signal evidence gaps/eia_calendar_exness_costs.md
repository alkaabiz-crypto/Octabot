# EIA release calendar (WPSR / Natural Gas Storage) 2025–2026 and Exness trading costs (XAUUSDm, USOILm, BTCUSDm)

Research date: 2026-11-11. **Method limitation:** direct page fetches of www.eia.gov, ir.eia.gov (and therefore exness.com / get.exness.help, which were not attempted after the EIA hosts failed) were blocked by this session's network allowlist ("getaddrinfo ENOTFOUND"). All findings below come from web-search result snippets of the cited URLs, not from full-page reads. Every value should be re-checked against the live page before being hard-coded into a backtest. To fetch directly, www.eia.gov, ir.eia.gov, www.exness.com and get.exness.help must be added to the session's allowed network hosts.

## Q1. EIA Weekly Petroleum Status Report (WPSR) 2025 and 2026 schedule, including holiday shifts

### Takeaway
The WPSR normally comes out Wednesday at 10:30 ET. When a federal holiday falls on a Monday, Tuesday or Wednesday, it moves one day to Thursday, now usually at 12:00 noon ET. A Thursday or Friday holiday does not move it. Only a few 2026 shifts were confirmed from sources (MLK, Labor Day, Columbus Day via a related report, Veterans Day), plus Memorial Day 2025 and an unusual Christmas 2025 case. The full table below applies the rule. It is NOT a copy of EIA's official table.

### Cited Findings
- Standard release: wpsrsummary.pdf, overview.pdf and Tables 1–14 (CSV/XLS) are posted "after 10:30 a.m. [ET] on Wednesday"; all other PDF/HTML files after 1:00 p.m. ET Wednesday. "For some weeks which include holidays, releases are delayed by one day." — [EIA WPSR page](https://eia.gov/petroleum/supply/weekly); [EIA WPSR schedule page](https://www.eia.gov/petroleum/supply/weekly/schedule.php) (snippets seen 2026-11-11)
- The EIA schedule page lists holiday weeks with a Thursday 12:00 p.m. ET release. Its examples include Memorial Day 2025, released **Thursday, May 29, 2025**. — [EIA WPSR schedule](https://www.eia.gov/petroleum/supply/weekly/schedule.php) (search snippet, 2026-11-11)
- Rule as stated in trade press: "EIA delays its Weekly Petroleum Status Report when a federal holiday falls on Monday, Tuesday or Wednesday"; normal Wed 10:30 a.m. ET; holiday weeks "usually Thursday at 12:00 p.m."; "Thursday holiday: released Wednesday 1200 ET" (this refers to the gas storage report). — [BOE Report, 2026-10-09](https://boereport.com/2026/10/09/schedule-for-us-energy-data-in-holiday-week-2/); [EnergyNow, Oct 2026](https://energynow.com/2026/10/schedule-for-us-energy-data-in-holiday-week-2/)
- MLK week 2026: data for week ending Jan 16, 2026 released **Thursday, January 22, 2026 at 12:00 p.m. and 2:00 p.m.** (two file tranches). — [EIA "upcoming reports" notice](https://www.eia.gov/about/new/) (search snippet; the snippet said "week of January 9", which conflicts with the date. Treat the week-ending label as unverified.)
- Labor Day 2026 (Mon Sep 7): WPSR **Thursday, Sep 10, 2026 at noon EDT**. — [BOE Report, 2026-09-04](https://boereport.com/2026/09/04/schedule-for-us-energy-data-in-holiday-week/)
- Columbus Day 2026: EIA's heating-oil/propane schedule shows **Thursday Oct 15, 2026** (2:00 p.m., a different report). A broker preview is titled "EIA Crude Oil Inventories Preview: 15 October 2026 Report", which points to a Thursday Oct 15 WPSR. — [EIA heating oil schedule](https://www.eia.gov/petroleum/heatingoilpropane/schedule.php); [Admiral Markets](https://admiralmarkets.com/analytics/traders-blog/eia-crude-oil-inventories-october-2026)
- Veterans Day 2026 (Wed Nov 11): WPSR for week ending Nov 6 released **Thursday, Nov 12, 2026 at noon ET**. — [BOE Report](https://boereport.com/2026/10/09/schedule-for-us-energy-data-in-holiday-week-2/); [Investinglive](https://investinglive.com/commodities/private-oil-inventory-survey-shows-huge-headline-build-vs-draw-expected/); [EIA heating oil schedule (Thu Nov 12, 2:00 p.m.)](https://www.eia.gov/petroleum/heatingoilpropane/schedule.php)
- Christmas 2025 anomaly: EIA moved the report for the week ending **Dec 19, 2025** from Wednesday to **Monday, Dec 29, 2025**, citing the Christmas holiday. It then pushed that Monday release later in the day. Data for the week ending Dec 26 was to be released "as usual" **Wednesday, Dec 31, 2025**. — [Investing.com](https://www.investing.com/news/commodities-news/us-eia-delays-weekly-petroleum-status-report-to-later-monday-93CH-4424217); [Longbridge](https://longbridge.com/en/news/270738863) (snippets only; the exact time on Dec 29 was not seen)
- Example of a normal week: next report Wednesday, Nov 4, 2026, 10:30 a.m. ET. — [EIA "upcoming reports"](https://www.eia.gov/about/new/) / aggregator snippet

### Inferences
Table built by applying the Mon/Tue/Wed-holiday rule to US federal holidays. "Confirmed" = a cited source states the date. Times for shifted weeks are 12:00 ET (Tables/summary) per the current rule. Older EIA practice was sometimes 11:00 ET, and the MLK 2026 notice shows a 12:00 / 2:00 p.m. split. Every week not listed is Wednesday 10:30 ET.

| Holiday (federal) | Holiday date | WPSR release | Time ET | Status |
|---|---|---|---|---|
| New Year's Day 2025 | Wed Jan 1, 2025 | Thu Jan 2, 2025 | ~12:00 (unverified; could be 11:00) | Inferred |
| MLK Day 2025 | Mon Jan 20, 2025 | Thu Jan 23, 2025 | ~12:00 | Inferred |
| Presidents Day 2025 | Mon Feb 17, 2025 | Thu Feb 20, 2025 | ~12:00 | Inferred |
| Memorial Day 2025 | Mon May 26, 2025 | Thu May 29, 2025 | 12:00 | Confirmed (EIA schedule snippet) |
| Juneteenth 2025 | Thu Jun 19, 2025 | Wed Jun 18, 2025 (no shift) | 10:30 | Inferred |
| Independence Day 2025 | Fri Jul 4, 2025 | Wed Jul 2, 2025 (no shift) | 10:30 | Inferred |
| Labor Day 2025 | Mon Sep 1, 2025 | Thu Sep 4, 2025 | ~12:00 | Inferred |
| Columbus Day 2025 | Mon Oct 13, 2025 | Thu Oct 16, 2025 | ~12:00 | Inferred. The Oct 1–Nov 12, 2025 federal shutdown may have affected releases (not verified). |
| Veterans Day 2025 | Tue Nov 11, 2025 | Thu Nov 13, 2025 | ~12:00 | Inferred |
| Thanksgiving 2025 | Thu Nov 27, 2025 | Wed Nov 26, 2025 (no shift) | 10:30 | Inferred |
| Christmas 2025 | Thu Dec 25, 2025 | Week ending Dec 19 → **Mon Dec 29, 2025**; week ending Dec 26 → Wed Dec 31, 2025 | Dec 29 time unverified; Dec 31 10:30 | Confirmed by news (anomalous; the rule would predict Wed Dec 24) |
| New Year's Day 2026 | Thu Jan 1, 2026 | Wed Dec 31, 2025 (no shift) | 10:30 | Consistent with news above |
| MLK Day 2026 | Mon Jan 19, 2026 | Thu Jan 22, 2026 | 12:00 (and 2:00 p.m. for remaining files) | Confirmed (EIA notice snippet) |
| Presidents Day 2026 | Mon Feb 16, 2026 | Thu Feb 19, 2026 | ~12:00 | Inferred |
| Memorial Day 2026 | Mon May 25, 2026 | Thu May 28, 2026 | ~12:00 | Inferred |
| Juneteenth 2026 | Fri Jun 19, 2026 | Wed Jun 17, 2026 (no shift) | 10:30 | Inferred |
| Independence Day 2026 (observed) | Fri Jul 3, 2026 | Wed Jul 1, 2026 (no shift) | 10:30 | Inferred |
| Labor Day 2026 | Mon Sep 7, 2026 | Thu Sep 10, 2026 | 12:00 | Confirmed (BOE Report) |
| Columbus Day 2026 | Mon Oct 12, 2026 | Thu Oct 15, 2026 | ~12:00 | Strongly implied (heating oil schedule + Admiral preview) |
| Veterans Day 2026 | Wed Nov 11, 2026 | Thu Nov 12, 2026 | 12:00 | Confirmed (multiple) |
| Thanksgiving 2026 | Thu Nov 26, 2026 | Wed Nov 25, 2026 (no shift) | 10:30 | Inferred |
| Christmas 2026 | Fri Dec 25, 2026 | Wed Dec 23, 2026 (no shift) | 10:30 | Inferred. The 2025 precedent shows EIA can deviate. |
| New Year's Day 2027 | Fri Jan 1, 2027 | Wed Dec 30, 2026 (no shift) | 10:30 | Inferred |

- For backtests, the safest approach is to read the actual release timestamps from EIA's historical schedule page, or from a timestamped economic calendar, rather than from this table.

### Gaps
- Could not read EIA's official schedule table (www.eia.gov blocked). All rows marked "Inferred" are unverified.
- Exact time of the delayed releases in early 2025 (11:00 vs 12:00 ET) is not confirmed.
- Whether the Oct–Nov 2025 government shutdown changed any WPSR dates is not confirmed.
- Exact release time on Mon Dec 29, 2025 is not known.

## Q2. EIA Weekly Natural Gas Storage Report (WNGSR) schedule

### Takeaway
The WNGSR is normally released Thursday at 10:30 ET. In Thursday-holiday weeks it moves to Wednesday at 12:00 ET. Three such dates were confirmed: Nov 26, 2025, Dec 24, 2025, and Nov 25, 2026.

### Cited Findings
- Thanksgiving 2025: **11/26/2025, Wednesday, 12:00 p.m.**; Christmas 2025: **12/24/2025, Wednesday, 12:00 p.m.** — [EIA WNGSR schedule (ir.eia.gov/ngs_test)](https://ir.eia.gov/ngs_test/schedule.html) (search snippet)
- Thanksgiving 2026: "Alternate release date: November 25, 2026", Wednesday, 12:00 p.m. — [EIA WNGSR schedule](https://ir.eia.gov/ngs/schedule.html) (snippet; the search tool flagged the page metadata as possibly stale)
- "Thursday holiday: released Wednesday 1200 ET" — [BOE Report](https://boereport.com/2026/10/09/schedule-for-us-energy-data-in-holiday-week-2/)

### Inferences
- Other likely shifts: Juneteenth 2025 (Thu Jun 19) → Wed Jun 18, 2025 at 12:00; New Year's 2026 (Thu Jan 1) → Wed Dec 31, 2025 at 12:00. Monday holidays usually do not move the Thursday WNGSR, though EIA has sometimes moved it to Thursday 12:00 in Mon–Wed holiday weeks. Not verified for 2025–2026.
- Friday holidays (Jul 4, 2025; Jul 3, 2026; Juneteenth 2026; Christmas 2026) would leave the Thursday 10:30 release unchanged. Not verified.

### Gaps
- Full official 2025/2026 WNGSR table not read (ir.eia.gov blocked).
- The base time (Thursday 10:30 ET) comes from general knowledge and was not seen in a 2025–2026 snippet. Verify it.

## Q3. Exness trading costs: XAUUSDm, USOILm, BTCUSDm (Standard / Standard Cent "m" symbols)

### Takeaway
Exness Standard accounts charge no commission. Cost is spread plus swap. Swaps are quoted in points per lot per night, change often, and must be read from the MT5 symbol specification. No reliable current numeric swap values were found for any of the three symbols. Rollover is 21:00 GMT+0 in summer and 22:00 GMT+0 in winter. Gold and oil have a daily break of about an hour around rollover. Crypto trades 24/7 except during maintenance.

### Cited Findings
**Commission and spread**
- "Of all trading account types available, only Zero and Raw Spread trading account types have a trading commission applied. All other trading accounts are commission-free." — [Exness Help: Are trading accounts charged a commission fee?](https://get.exness.help/hc/en-us/articles/360012007919-Are-trading-accounts-charged-a-commission-fee) (snippet, 2026-11-11)
- Standard account spread "From 0.2 pips"; max lot size 200 (7:00–20:59 GMT+0) and 60 (21:00–6:59 GMT+0). — [Exness Standard accounts](https://www.exness.com/standard-accounts/); [Exness Help: Standard account](https://get.exness.help/hc/en-us/articles/17537782738460-Standard-account)
- An older Exness page caps UKOIL and USOIL at 100 lots. — snippet from the search on [Exness Help: Trading account types](https://get.exness.help/hc/en-us/articles/360013782240-Trading-account-types) (attribution uncertain)
- USOIL/UKOIL are available on Standard Cent only on MT5 and Exness platforms. The only stated USOIL commission figures apply to Raw Spread and Zero accounts. — [Exness Help: Commodities](https://get.exness.help/hc/en-us/articles/17854173039388-Commodities)
- BTCUSD spread on Standard "about 200–400 points during active hours", from a third party with an old, inconsistent table. Unreliable. — [TradersUnion](https://tradersunion.com/brokers/forex/view/exness/btcusd-spread/)

**Swap: quoting, timing, triple days**
- Swap is quoted in points, separately for long and short. View it via the Exness website "Specifications" or MT4/MT5 (right-click symbol → Specification). — [Issuu Exness blog copy](https://issuu.com/exness_blog/docs/exness.docx/s/91077899) (unofficial)
- Rollover/swap time: **21:00 GMT+0 (summer), 22:00 GMT+0 (winter)**. The table includes a Wednesday row marked "Triple for crypto crosses only". The page text was partly garbled in the snippet. — [Exness Help: About swap](https://get.exness.help/hc/en-us/articles/360014709151-About-swap)
- Crypto: swap applied once a day Monday–Friday. **Triple swap on Friday night for BTCUSD, ETHUSD, ETHBTC, BTCUSDT** (covers the weekend). Triple on **Wednesday night** for crypto crosses BTCXAU, BTCXAG, BTCTHB, BTCAUD, BTCZAR, BTCCNH. "Public holidays may affect this schedule." — [Exness Crypto](https://www.exness.com/crypto/)
- Conflict: an Exness-branded mirror says "no swap is charged on cryptocurrency positions". — [exnessbank.com/crypto](https://www.exnessbank.com/crypto/) (not a confirmed official Exness domain)
- Gold/oil triple-swap day: not stated in an Exness source seen. A different broker's glossary says Wednesday for FX/metals and Friday for indices/energy. That does NOT apply to Exness. — [Vantotrade glossary](https://vantotrade.com/glossary/what-is-triple-swap-day/)
- An outlier third-party page claims 7:00 a.m. rollover and Wednesday triple. It contradicts the official help page. Disregard. — [exn.fxsignup.com](https://exn.fxsignup.com/en/trade/swap.html)

**Swap values found (all unreliable / non-official)**
- XAUUSD: "approx −$3.50/lot/day long, +$0.50/lot/day short" (third-party guide, Apr 2026) — [tradingzenith](https://tradingzenith-net.pages.dev/artigos/exness-gold-trading-india). Also "−2.10 long / −1.80 short (examples, change daily)" — [exbroker mirror](https://exbroker-co-za.pages.dev/swap-exness). Also an unattributed "−$42.00 long / +$12.00 short per lot per night" — [lowspreadbroker](https://lowspreadbroker-com.pages.dev/artigos/lowest-spread-broker-gold-xauusd). These figures disagree with each other by an order of magnitude.
- BTCUSD long: roughly −$12.62 to −$17.64 per lot per night, Friday triple (third-party pages that disagree with each other) — [ex-platforms](https://ex-platforms.com/en/swap-rates); [brokers-trade.com.pk](https://brokers-trade.com.pk/swap-rates)
- USOIL: no values found.

**Swap-free rules**
- "Extended Swap-free status [is offered] by default to all applicable trading accounts created by clients in non-Islamic countries." Standard tier covers cryptocurrencies and stocks. The extended tier adds **USOIL, UKOIL, XNGUSD, XAUUSD**. Crypto crosses (BTCXAU, BTCXAG, BTCTHB, BTCAUD, BTCCNH, BTCJPY, BTCZAR) joined the extended program in July 2023. — [Exness Help (zendesk mirror): Are swap-free trading accounts available in non-Islamic countries?](https://exnesshelpcenter1650503396.zendesk.com/hc/en-us/articles/10301387770908-Are-swap-free-trading-accounts-available-in-non-Islamic-countries)
- Clients registered in eligible Islamic countries (UAE presumably among them, not confirmed) get swap-free on all instruments. This regime is separate and cannot be converted. Status is shown in Personal Area → Exness benefits → Trading conditions → Swap-Free. Even swap-free accounts can be charged swap on some symbols. — [FX Recap](https://fxrecap.com/top-broker/exness-review/islamic-account); [theforexlens](https://theforexlens.com/islamic-brokers/exness); [scribehow](https://scribehow.com/page/Is_Exness_Standard_Account_Swap-Free_Everything_You_Need_to_Know__5AUcJ0gLSxmDHAHLDDYqJg) (third-party)
- Some third parties say status is kept or revoked by a monitoring algorithm (for example, for holding positions long-term or exploiting swap-free). Not verified in official docs.

**Trading hours, daily break, leverage**
- Server time GMT+0. **XAU daily break 20:58–22:02**; **USOIL daily break 20:59–22:01** (server time). — [Exness commodities page, via exnessbank.com mirror](https://www.exnessbank.com/commodities/) / [Exness commodities](https://www.exness.com/commodities/)
- Rollover/break shifts with US DST (21:00 UTC during US DST, 22:00 UTC otherwise). — [compareforexbrokers.ng](https://compareforexbrokers.ng/exness-gold-xauuusd-trading/) (third-party, consistent with the About swap page)
- USOIL fixed leverage **1:1000** (UKOIL 1:200). During higher-margin-requirement (HMR) periods both go to **5% margin (1:20)**. Energy daily break: 1:20 (5%). — [Exness commodities](https://www.exnessbank.com/commodities/); [Exness Help: HMR](https://get.exness.help/hc/en-us/articles/20618327917596-Higher-Margin-Requirements-HMR)
- Gold: up to **1:Unlimited** for eligible accounts. Capped at **1:200 from 15 min before to 5 min after major news**. New positions opened shortly before the daily break are capped (1:1000 cited). HMR metals range 1:100–1:1000. — same sources
- Crypto: CFD crypto trading 24/7 "except during server maintenance". Crypto margin requirements are "fixed, regardless of the leverage you use". — [Exness Crypto](https://www.exness.com/crypto/); [exnessbank.com/crypto](https://www.exnessbank.com/crypto/)
- Contract size XAUUSD: 1 lot = 100 oz, min 0.01 lot (Exness-branded page). Whether "m" symbols use the same contract size, and how Standard Cent sizes differ (cent accounts are denominated in USC), was not verified. — [Issuu Exness copy](https://issuu.com/exness_blog/docs/exness.docx/s/91077899)

### Inferences
- For a backtest of Standard "m" symbols, use spread only (commission = 0) plus swap per night at the 21:00/22:00 UTC rollover. Apply crypto swap Mon–Fri with ×3 on Friday for BTCUSDm (there is no separate Sat/Sun charge). If the account is extended swap-free (default for non-Islamic-country clients), set swap = 0 for XAUUSDm, USOILm and crypto. Swap-free status can be revoked, so a scenario with swap charged should also be modeled.
- No trades should be simulated inside the gold/oil daily break (about 20:58–22:02 server time, shifting with DST). Spreads usually widen sharply around this window.
- Gold/oil triple-swap day is likely Wednesday for XAU and Friday for USOIL (the common industry convention), but this was NOT confirmed for Exness.

### Gaps
- No verified current numeric swap long/short values for XAUUSDm, USOILm or BTCUSDm. They must be read from MT5 → Symbol → Specification on a live/demo Standard account, or from the Exness contract specifications page (blocked here).
- No verified typical spread for any of the three symbols on Standard. Exness publishes average spreads on its contract-specification pages, which could not be fetched.
- Contract size for USOILm (likely 100 barrels per lot) and BTCUSDm (likely 1 BTC per lot) is not verified.
- BTCUSD leverage cap is not found.
- Whether BTCUSD is in the "standard" or "extended" swap-free tier is not stated explicitly (cryptocurrencies are listed generically under standard).
- Whether UAE clients get full Islamic-country swap-free or the non-Islamic extended regime is not confirmed.
- The triple-swap day for XAU and USOIL on Exness is not confirmed.
