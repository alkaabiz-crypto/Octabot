# H4 (Coinbase premium) check C: a second USDT venue (pre-registered 2026-11-13, before any OKX data was downloaded)

**Purpose.** H4 worked against Binance (USDT) but not against Bitstamp (USD). If the effect is about **USD demand against offshore USDT demand** (THE-014), it should also appear against **another USDT venue**. Bybit is geo-blocked from this session, so the venue is **OKX** (BTC-USDT spot, public API).

**Rule.** Identical to H4 and check B:
- *prem* = ln(Coinbase BTC-USD hourly close / OKX BTC-USDT hourly close);
- *z* over the previous 720 hours, excluding the current one;
- |*z*| ≥ 2 → follow for 24 h, one position at a time;
- Exness BTCUSDm execution and costs;
- periods EARLY 2020–22, TRAIN, VALIDATION, TEST;
- random-entry benchmark.

| Label | Conditions |
|---|---|
| **REPLICATED** | mean > 0 in all 4 periods; TEST stress > 0; TEST p ≤ 0.05; ≥ 30 TEST trades |
| **PARTIAL** | positive in all 4 periods, but TEST p > 0.05 |
| **NOT REPLICATED** | otherwise |

H4's decision and forward test are unaffected.
