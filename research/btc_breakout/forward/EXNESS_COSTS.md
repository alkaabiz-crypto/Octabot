# Exness BTCUSD trading costs: evidence status (2026-11-09)

**Status: NOT VERIFIED.** No Exness cost value has been confirmed from a primary source. Every forward-test result uses hypothetical round-trip cost scenarios of 0.02%, 0.05% and 0.10% of price. They are labelled BINANCE PROXY.

## Primary sources: could not be read

| Source | Result |
|---|---|
| www.exness.com (contract specs, crypto and account pages) | Direct HTTP requests from this environment return a Cloudflare "Just a moment..." bot challenge (HTTP 403). The challenge was not bypassed. |
| get.exness.help (help centre) | The same Cloudflare challenge. A separate page-fetch tool could not resolve the host. |

## Secondary evidence (search-result summaries, 2026-11-09). UNVERIFIED: not usable for backtest costs

These statements come from search-engine summaries of the pages listed below. The pages themselves could not be opened, so wording, dates and accuracy are unconfirmed.

| Topic | What the summaries state | Source(s) |
|---|---|---|
| Contract | BTCUSD: 1 lot = 1 BTC, minimum 0.01 lot | rebt-one.com (third party) |
| Commission | Standard account: no commission. Raw Spread: "2 USD per lot". Zero: "4.375 USD". Per side or round trip is not stated. | exness.com/standard-accounts, get.exness.help Cryptocurrencies article |
| Spread | Standard "from 0.2 pips" is a minimum across all instruments, not BTC-specific. Third-party BTC figures conflict: about 6.4 "points" mean, and 200–400 "points" with unclear units. | exness.com, fxfan.club, tradersunion.com |
| Swap | Charged once a day at 21:00 GMT+0 (summer) or 22:00 (winter). **Triple swap on BTCUSD for positions held over Friday night.** Rates "can change daily". No BTCUSD rate was found. | get.exness.help "About swap", "Does Exness charge fees on orders held overnight" |
| Swap-free | Marketing pages describe BTCUSD as swap-free, but swap-free status is conditional and can be withdrawn for accounts that regularly hold large positions overnight. | exness.com/crypto, get.exness.help "Swap-free status" |
| **Admin fee** | **Overnight BTCUSD positions on swap-free terms "may incur an admin fee of 50 USD/lot"**, separate from swap. | get.exness.help "About admin fees on overnight orders" |

### Why this matters for this strategy (illustrative, not a cost assumption)

The average hold in research was about 20 hours, so most trades stay open past the daily cut-off. Paper position sizes are about 0.015–0.03 BTC, at 0.5% risk of about 2,723 USD with stops of 2 × ATR.

If the 50 USD/lot admin fee applied, it would cost about **0.75–1.5 USD per night**, against about 13.6 USD of risk per trade. That is roughly **0.05–0.1 R per night held**, or about 3× that over a Friday night. This is comparable to the edge seen in research, which was about +0.2 R per trade at 0.05% cost. **Overnight costs could decide whether the edge survives, and they are not modelled at all.**

## What is needed (from your own MT5 terminal, BTCUSDm symbol)

Right-click BTCUSDm in Market Watch, choose Specification, and record:

1. Contract size, minimum volume and volume step
2. Spread: take a sample of the live spread at several times of day; the Specification only shows "floating"
3. Commission, if any, for your account type
4. Swap long, swap short, swap type (points, % or money) and the triple-swap day
5. Whether your account is swap-free, and any admin fee shown in your Personal Area or on the trading calculator

With those values, the cost model can be re-run on the unchanged ledgers as a separate, clearly labelled "Exness-cost" analysis. Neither the strategy nor the recorded results would change.

## Sources consulted

- https://www.exness.com/standard-accounts/
- https://www.exness.com/crypto/ and https://www.exness.com/crypto/btcusd/
- https://get.exness.help/hc/en-us/articles/17854191888540-Cryptocurrencies
- https://get.exness.help/hc/en-us/articles/360014709151-About-swap
- https://get.exness.help/hc/en-us/articles/360011745839-Does-Exness-charge-fees-on-orders-held-overnight
- https://get.exness.help/hc/en-us/articles/11415853845404-About-admin-fees-on-overnight-orders
- https://get.exness.help/hc/en-us/articles/4402341895570-Swap-free-status
- https://fxfan.club/en/rebates/exness/spread/, https://tradersunion.com/brokers/forex/view/exness/btcusd-spread/, https://rebt-one.com/broker/exness/account-type/ (third party)
