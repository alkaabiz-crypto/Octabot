# Hyperliquid fees and funding for the GOLD_FVG and OIL_FIB paper tests (13 November 2026)

**What this is.** The gold and oil library paper tests (`library_forward/forward.py`, frozen) run on Hyperliquid HIP-3 perpetuals, xyz:GOLD and xyz:CL. They charge only a fixed Exness-derived spread (0.22 USD/oz and 0.02 USD/bbl per round trip, doubled for the main result). Hyperliquid's trading fees and hourly funding are **not modelled**.
- This note measures what they would add.
- **Nothing is changed:** the frozen rules, costs and ledgers stay as they are.
- This is an interpretation aid only.

## Inputs

- **[FACT] Fees.** From Hyperliquid's API (`userFees` for an empty address, 2026-11-13): base-tier perpetuals **taker 0.045%, maker 0.015%**, with no referral or staking discount.
  - xyz:GOLD and xyz:CL report `deployerFeeScale` 1.0.
  - [UNKNOWN] Whether HIP-3 markets charge more than the base rate could not be verified: the documentation host is blocked from this session. Both the base rate and 2× base are shown.
- **[FACT] Funding.** From `fundingHistory`, the last 500 hourly rates (about 21 days):

  | Market | Mean per hour | Mean of absolute rate per hour | Range per hour |
  |---|---|---|---|
  | xyz:GOLD | +0.94 bp (longs pay) | 1.02 bp | −0.44 to +0.39 bp |
  | xyz:CL | +0.007 bp | 0.80 bp | −0.73 to +1.36 bp |

- **[CALC] Trades.** The causal forward-model trades on Exness 1-minute data, 2025-01 to 2026-10, from `src/causal_orders.py`, which reproduces the frozen `forward.py`. This uses their actual exit reasons and holding times.
- **Assumptions.** The entry is a resting limit, so it pays the maker fee. A target exit is a limit (maker); stop, gap-stop and time exits are market orders (taker). Funding is the mean rate × holding hours × side.

## Result (per trade, mean, bp of price)

| | Gold (696 trades; 372 long; 7.2 h mean hold) | Oil (414 trades; 209 long; 12.4 h mean hold) |
|---|---|---|
| Exit mix | 419 stop, 7 gap, 212 target, 58 time | 207 stop, 6 gap, 113 target, 88 time |
| Spread cost modelled by the paper test (2×) | 1.17 | 5.67 |
| **Hyperliquid fees, base tier** | **5.09** | **5.18** |
| Funding, at the 21-day mean rate | +0.04 (longs and shorts nearly cancel) | +0.00 |
| Funding, typical absolute size per trade | 0.74 | 1.00 |
| **Net, forward model as modelled** | **−0.16** | **−8.42** |
| **Net with base fees + funding** | **−5.29** | **−13.60** |
| Net if HIP-3 fees are 2× base | −10.37 | −18.78 |

## Interpretation

- **[CALC]** For gold, Hyperliquid's fees are **more than 4 times** the cost the paper test charges. So the paper test's 2× cost scenario does **not** cover real execution on this venue.
- Even with zero modelling error elsewhere, the gold strategy would need an edge above about 5 bp per trade just to break even after fees. The causal backtest shows about 0 (`CAUSAL_IMPACT_ASSESSMENT.md`).
- Oil was already negative, and fees make it worse.
- **[HYP]** A pass of these paper tests, under the frozen rule or under `research/new_discovery/promotion_rule_v2/PROMOTION_RULE_V2.md`, would therefore **not** imply profitability on Hyperliquid. Any real-money assessment would need venue fees, funding and fill quality.
- Funding is small on average, because the strategies trade both sides. Its sign depends on market positioning, so it could matter in a one-sided period.
