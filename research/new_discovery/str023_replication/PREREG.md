# STR-023 replication on five other cryptocurrencies (pre-registered 2026-11-14, before computation)

**Purpose.** STR-023 (VWAP momentum BUY + trailing exit) passed on BTC and replicated on ETH, and its forward test runs from 2026-11-14. This test asks whether it works on **markets it was never tested on**. The rules are unchanged: the frozen `rsi_vwap_study/src/study.py`, called as `Asset.run("V1_VWAP_MOMENTUM", BUY, "TRAIL")`.

## Data

- **Exness 15-minute bid/ask candles** for SOLUSDm, BNBUSDm, XRPUSDm, LTCUSDm and BCHUSDm, 2023-01 → 2026-11 (private archive, `exness_15m_multi/`).
- Mid prices are aggregated to 15m, 1h and 1d candles in the study's JSON format.
- **Volume:** CFDs have no traded volume, so the **Exness tick count** per candle is used as the volume weight in the study's session VWAP. This is a disclosed difference from the study, which used Binance volume.

**Period.** 2023-01-01 → 2026-11-09, all of it new for STR-023. The first 30 days are used only as indicator warm-up.

## Costs, per round trip as a share of price

- **Decision cost:** 1.5 × the market's median Exness spread over the period (spread plus half-spread slippage, the discovery protocol's primary cost).
- **Also reported:** the study's 0.05%.

## Statistics, per market

- Trades and mean R at both costs.
- t of the mean.
- The study's own matched random-entry benchmark (`random_benchmark`, 2,000 runs, same exits and one-position rule), evaluated at the study's 0.05% cost; p_random.
- Benjamini–Hochberg across the 5 p_random values.

## Verdict

| Verdict | Conditions |
|---|---|
| **REPLICATED** | ≥ 3 of 5 markets have mean R > 0 at the decision cost **and** p_random ≤ 0.05 after BH |
| **PARTIAL** | ≥ 3 of 5 have mean R > 0 at the decision cost, but < 3 are significant |
| **NOT REPLICATED** | otherwise |

STR-023's forward test is unaffected by this result.
