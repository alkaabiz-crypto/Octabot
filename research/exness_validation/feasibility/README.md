# Position-sizing feasibility: frozen Donchian 20 on Exness BTCUSDm

The calculations are arithmetic on the committed one-year tick-replay ledger: 64 trades from 2025-11 to 2026-10, risking 0.5% of equity. No new backtest was run, and the frozen research is unchanged. Inputs: `feasibility.py` and `feasibility_results.json`.

## Specification status: NOT AVAILABLE

The actual MT5 symbol specification and demo account settings could not be read. No MT5 connection exists; see `../forward_demo/CONNECTION_REQUIREMENTS.md`. **Missing values:**

| Needed value | Status |
|---|---|
| Contract size (BTC per lot) | UNKNOWN. Unverified secondary sources say 1 BTC. |
| Tick size | Price data shows 0.01 USD increments, but the symbol's official tick size is unconfirmed. |
| Tick value per lot | UNKNOWN. It would be 0.01 USD if 1 lot = 1 BTC. |
| Minimum volume / volume step | UNKNOWN. Secondary sources say 0.01 / 0.01. |
| Maximum volume | UNKNOWN. Secondary sources say 200 lots in daytime and 60 lots overnight, a general limit for all instruments. |
| Leverage / margin requirement for BTCUSDm | UNKNOWN |
| Account currency and demo balance | UNKNOWN. Paper equity used here: 10,000 AED = 2,722.94 USD. |
| Free margin | UNKNOWN, because it depends on the actual demo account. |
| Commission, swap long, swap type, triple-swap day | UNKNOWN |

## Results (assumption-free unless labelled as a scenario)

- **Required volume:** 0.0074 to 0.0628 BTC, median 0.0197 BTC.
- **Notional value as a multiple of equity:** 0.20× to **1.50×**, median 0.50×.
  - Most trades fit without leverage.
  - The largest ones need roughly 1.5:1. That is far below typical broker leverage, but BTCUSDm leverage is unverified.
- **Scenario A (unverified): 1 BTC per lot, minimum 0.01, step 0.01, rounded down so risk never exceeds 0.5%.**
  - 62 of 64 trades can be opened.
  - **2 trades are below the minimum volume**: they need less than 0.01 BTC.
  - Actual risk is **0.1% to 49.7% below target, median 26.4% below**.
  - With about 2,700 USD of equity, the volume step makes per-trade risk uneven. Results would differ from the R-based study.
- **Scenario B (stress test): minimum 0.1 lot.** No trade can be opened at 0.5% risk on this balance.

### The 2026-08-19 trade (+26.4 R)

| Item | Value |
|---|---|
| Equity before the trade | 2,712.25 USD |
| Target risk (0.5%) | 13.56 USD |
| Entry (ask) | 64,967.98 |
| Risk per BTC (2 × ATR14) | 432.27 |
| Required volume | 0.03137 BTC |
| Notional | 2,038 USD (0.75× equity) |
| Scenario A volume | **0.03 lots** (actual risk 12.97 USD) |
| Scenario A P&L | **about +343 USD** (theoretical +359 USD), before unknown swap. The trade was held over two rollovers. |
| Scenario B | **Not openable** (0.03 BTC is below a 0.1 minimum) |

**Conclusion:** sizing is **feasible only if the minimum volume is 0.01 BTC or smaller**, and even then risk is uneven and usually below target. Under a 0.1-lot minimum the strategy cannot be traded at 0.5% risk on this balance. This cannot be settled without the real MT5 specification.
