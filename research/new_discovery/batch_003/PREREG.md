# Batch 003 pre-registration: structural and order-flow hypotheses (13 November 2026, written before any code or result)

Protocol, costs and decisions follow `../PROTOCOL.md`, with the amendments below.

## Duplication check (done before writing)

Not tested anywhere in either branch:
- round-number support and resistance;
- precious-metal fixes;
- the CME weekend gap;
- the Coinbase premium.

Searched in this branch (batches 001 and 002, `news_markets`, `news_surprise`, the gold KST work, the user theories) and in the other branch (the frozen theory library's 63 IDs, ORB, zone, session and shortlist studies, Batch 2 H1–H4).
- The pre-FOMC drift and the EIA oil reaction were **excluded**, because `research/news_markets` already tested them (0 of 225 confirmed).
- Funding, basis, aggressor flow, implied-volatility premium and FX carry are left to the other session's Batch 2.

## Data

- **Exness 15-minute bid/ask candles**, built from the public tick archive (`ticks.ex2archive.com`); private research copies, not committed.
  - Gold (XAUUSDm) 2020-01→, oil (USOILm) 2019-02→, BTC (BTCUSDm) 2020-01→: the `long/` files.
  - EUR/USD, USD/JPY, S&P 500 (US500m) and silver (XAGUSDm) 2023-01→: the `multi/bars/` files.
  - All end 2026-11-09/10.
- **H4 only:** hourly BTC-USD candles from Coinbase Exchange's public API and BTCUSDT from Binance's public API, both 2019-11→. Not committed. They are used only to build the signal; trades execute on Exness BTCUSDm.

## Periods

- TRAIN 2023-01 → 2024-06; VALIDATION 2024-07 → 2025-06; TEST 2025-07 → latest (**reused evaluation data**, so the best label possible is SCREEN-PASS).
- **New, EARLY: 2019/2020-01 → 2022-12**, where data exist (gold, oil, BTC; H4 from 2020). This programme has never evaluated these years. They serve as an additional out-of-sample sign check, reported separately.

## Costs

The protocol's costs apply. A long buys at the ask and sells at the bid; a short does the reverse.
- **Primary:** an extra slippage of 0.5 × the market's median spread per trade.
- **Stress:** 1.5 × the median spread, plus 0.02% per day held.

## H1. Round numbers (Osler 2003, *Journal of Finance*; Osler 2000, FRBNY Economic Policy Review)

**Why it might work.** Take-profit orders cluster at round numbers, so trends tend to stop there. Stop-loss orders cluster just beyond them, so a crossing tends to accelerate.

**Grid**, one per market, fixed in advance: gold 10 USD; oil 1 USD; EUR/USD 0.0100; USD/JPY 1.00; S&P 500 50 points; BTC 1,000 USD.

The rules work on 15-minute mid candles. *L* is any grid level.

**R1: rejection at a fresh level (fade).** Long trades mirror the short ones.
- **Short** when all of these hold:
  - the previous 8 candles' highs are all below *L*;
  - candle *k*'s high reaches at least *L*;
  - candle *k* closes below *L*.

**R2: crossing (follow).** Short trades mirror the long ones.
- **Long** when all of these hold:
  - the previous 8 closes are all below *L*;
  - candle *k* closes at or above *L*.

**Execution and benchmark.**
- **Entry:** the next candle's open. **Exit:** the open 4 candles later (1 hour). One position at a time per rule and market. If several levels qualify, the nearest to the close is used.
- **Benchmark:** 1,000 sets of the same number of trades, with the same sides and the same 1-hour hold, at random candle opens in the same period. One-sided p for the mean.

**Count:** 2 rules × 6 markets = **12 tests**.

## H2. London precious-metal fixes (Caminschi & Heaney 2014, *Journal of Futures Markets*; Abrantes-Metz & Metz 2014)

**Why it might work.** Benchmark-related flows and hedging around the LBMA auctions pushed prices down systematically around the fix, at least before the 2015 move to electronic auctions. **The effect may have disappeared since.**

**Rule.**
- **Gold:** short at the open of the 15-minute candle starting **14:45 London time**, and cover at the open of the **15:15** candle. The LBMA Gold PM auction is at 15:00.
- **Silver:** short 11:45 → 12:15 London. The LBMA Silver auction is at 12:00.
- Every London weekday that has both candles.

**Benchmark.** 1,000 sets of 30-minute windows on the same days, at random candle opens between 08:00 and 16:30 London. One-sided p.

**Count:** **2 tests** (XAUUSDm, XAGUSDm).

## H3. BTC "CME gap fill" (popular trader theory; no peer-reviewed support known)

**Claim.** When BTC's price at the CME futures reopen (Sunday 17:00 Chicago time) differs from the CME Friday close (Friday 16:00 Chicago time), price returns to the Friday close.

**Rule** (Exness BTCUSDm, 15-minute data):
- **The levels:**
  - *P_F* is the mid close of the candle ending at Friday 16:00 Chicago time.
  - *P_S* is the mid open of the candle starting at Sunday 17:00 Chicago time.
  - The gap is *g* = *P_S* / *P_F* − 1.
- **Trade** only if |*g*| ≥ 1.0%.
  - Enter at the Sunday 17:00 candle open, in the direction of *P_F*.
  - **Target:** *P_F*.
  - **Stop:** the same distance on the other side of the entry (1:1).
  - **Time exit:** the open of the candle starting at Friday 16:00 Chicago time.
  - Inside a candle the stop is checked first. Target and stop fill at their levels, adjusted for the bid/ask.

**Statistic.** The one-sided t-test of the mean net bp > 0. There is one trade a week at most, so overlap is not an issue.

**Benchmark (reported).** The win rate a 1:1 bracket would have under a driftless random walk is 50%.

**Count:** **1 test**.

## H4. Coinbase premium (BTC)

**Why it might work.** US-based buying shows up first on Coinbase (USD) versus offshore Binance (USDT), and the premium is widely watched as a flow signal.

**Rule.**
- At each hourly close, *prem* = ln(Coinbase BTC-USD close / Binance BTCUSDT close).
- *z* = (*prem* − its mean over the previous 720 hours) / its standard deviation over the previous 720 hours. Both exclude the current hour, so the slow USDT/USD basis is removed.
- If *z* ≥ +2, **long** BTC for 24 hours. If *z* ≤ −2, **short** for 24 hours.
- Entry at the first Exness 15-minute open at or after the hourly close; exit at the first open at or after entry + 24 hours. One position at a time.

**Benchmark.** 1,000 sets of random entries with the same count, sides and 24-hour hold. One-sided p.

**Count:** **1 test**.

## Decisions

- **16 TEST-period tests in total.** Benjamini–Hochberg at 5% across them.
- **SCREEN-PASS** requires all of:
  - mean net > 0 at primary cost in TRAIN, VALIDATION and TEST, **and in EARLY where it exists**;
  - mean > 0 at stress cost in TEST;
  - TEST p ≤ 0.05 against the benchmark, surviving BH;
  - at least 30 TEST trades.
- **WATCH:** positive in every available period but not significant.
- **REJECT:** otherwise.
- A SCREEN-PASS needs a forward period before anything else. All look-ahead rules from `../tests/test_causal_orders.py` apply: decisions use closed candles only, and entries happen at the next candle's open.
