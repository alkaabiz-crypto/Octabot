---
title: STR-045 crypto ETF flow signal pre-registration
description: Do daily US spot Bitcoin / Ethereum ETF net flows predict the next days' BTC / ETH returns? IC test and a simple follow/fade rule
sidebar_position: 1
---

# STR-045: spot-ETF flows → BTC / ETH returns (pre-registration, 2026-11-20, before any computation)

**Source.** The user asked to test the "CryptoETF Flows" plugin. The plugin is not installed, and its free API key gives 8 days of history. The same data (daily net flow of all US spot ETFs per asset, BTC since 2024-01-11, ETH since its launch in 2024-07) is embedded in the public pages cryptoetf.today/en/bitcoin-etf-flows and /ethereum-etf-flows. It is read from there; raw data stays in scratch.

## Timing (no look-ahead)

ETF flows for US trading day D are reported after the US close, often only the next morning. The signal from day D is therefore used **at 00:00 UTC of D+2**, about 32 hours after the close.

## Signal

z(D) = (flow(D) − mean of the previous 60 trading days' flows) / their standard deviation.

## Tests (BTC and ETH separately)

1. **IC:** Spearman rank correlation of z(D) with the return from 00:00 UTC D+2 to 00:00 UTC D+3 (h = 1 day) and to D+7 (h = 5 days). Non-overlapping samples for h = 5.
2. **Rule:**
   - **FOLLOW:** z ≥ +1 → LONG; z ≤ −1 → SHORT; hold 1 day (primary) or 5 days (variant); no overlapping trades.
   - **FADE** (the opposite) is reported for completeness. Since FADE is simply the mirror image, its mean is the negative of FOLLOW's minus twice the costs.
- **Prices:** Binance spot daily opens (BTCUSDT, ETHUSDT). **Costs:** 0.05% per side (stress 0.20%).
- **Periods:** VALIDATION = flow days to 2025-06-30; TEST = 2025-07-01 → latest.
- **Benchmark (rule):** random days with the same count, sides and hold, 1,000 sets.
- **Decision (per asset × hold, FOLLOW):**
  - **SCREEN-PASS:** mean net > 0 in both periods, TEST stress > 0, TEST p ≤ 0.05 after BH over the 4 (asset × hold) tests, and ≥ 30 TEST trades.
  - **WATCH:** positive in both periods without the rest. Otherwise **REJECTED**.
  - If FOLLOW is negative in both periods, the result is reported as "flows lag price" rather than turned into a FADE strategy after the fact.

The other two suggested plugins are not strategies:
- **TradingCalc** is a calculator (position size, pip value, liquidation price);
- **Crypto Spot Futures Analyzer** gives AI opinions on setups. It could only be judged by prospectively scoring its calls once installed (the SIG method).
