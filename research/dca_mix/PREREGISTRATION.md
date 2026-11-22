# DCA mix study: pre-registration

Committed **2026-11-12, before running.**

## Why

Every timing rule tested so far failed random-timing controls (`../session_study`, `../exposure_control`, `../trend_breadth`, `../mom50_breadth`). The remaining practical question for real money is **what to buy regularly**, not when. This study compares fixed-mix DCA plans.

## Data, all from 2025 onward

- **Exness daily mid closes:**
  - US500m and USTECm, from `../mom50_breadth/data`;
  - XAGUSDm, from the same folder;
  - XAUUSDm, built from the cached Exness ticks with `../shortlist_2025/screen.py daily`.
- **Binance BTCUSDT daily closes,** from `../daily_signal_dca/from_2025/data`.
- **Dates used:** only dates where every market in the mix has a close, from 2025-01-02 to 2026-10-30.

## Method

- **Contributions:** 10 USD on every common trading date, split by the mix weights and bought at that day's close.
- **Costs:** a 0.1% fee on every purchase. No selling and no rebalancing.
- **Swap or financing is ignored.** For long-term holding the user should use spot ETFs, physical gold or spot BTC, not leveraged CFDs. That advice is in the report.

## Mixes, fixed now

| Name | Weights |
|---|---|
| SP500 | 100% S&P 500 |
| NASDAQ | 100% Nasdaq 100 |
| GOLD | 100% gold |
| BTC | 100% bitcoin |
| SP_GOLD | 50% S&P 500, 50% gold |
| SP_GOLD_BTC | 40% S&P 500, 40% gold, 20% BTC |
| EQUAL5 | 20% each of S&P 500, Nasdaq, gold, silver, BTC |

## Measures

- final profit % on the money put in;
- **worst point**, the lowest value against the money put in so far;
- max drawdown of the account value;
- for each calendar half-year, the profit of a fresh plan started at its first date.

## Hypotheses

- **H1:** the mixes (SP_GOLD, SP_GOLD_BTC, EQUAL5) have a smaller max drawdown than the **average** single-market plan.
- **H2:** the mixes' worst half-year is better than the average single market's worst half-year.

**Not claimed:** which plan made the most money. That is one 22-month window and depends on hindsight. It is reported, but no recommendation is based on the highest return.
