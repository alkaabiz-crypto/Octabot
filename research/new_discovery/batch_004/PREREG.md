# Batch 004 pre-registration: commodity term structure (13 November 2026, written before the futures data were parsed or examined)

## Duplication check

Never tested in either branch. The other session's `shortlist_2025` lists the backwardation rule as "not testable: no futures curve".
- A standalone gold-against-real-yields rule was **dropped**, because real yields were already tested as a filter in `gold_kst_news`.
- BTC ETF flows were **dropped**, because the data source is blocked from this session.

## Hypothesis

**The effect.** When a commodity's futures curve is in **backwardation** (front contract above the second), holding the front contract earns a positive premium; in **contango** it earns a negative one.

**Why** (theory of storage, hedging pressure):
- Backwardation signals scarce inventories and producer hedging demand.
- The long side is paid through the roll yield and a risk premium.

**Evidence.**
- Erb & Harvey (2006), *Financial Analysts Journal*.
- Gorton, Hayashi & Rouwenhorst (2013), *Review of Finance*.
- Szymanowska, de Roon, Nijman & van den Goorbergh (2014), *Journal of Finance*.

## Data

- EIA daily settlement prices for futures contracts 1 and 2:
  - WTI crude: `RCLC1`, `RCLC2` (`eia.gov/dnav/pet/hist_xls`), from 1986.
  - Henry Hub natural gas: `RNGC1`, `RNGC2` (`eia.gov/dnav/ng/hist_xls`), from 1994.
- Public US government data; kept in scratch and in the private archive.

## Returns of holding the front contract

- On a non-roll day: *r*ₜ = F1ₜ / F1ₜ₋₁ − 1.
- On a **roll day**, when contract 1 switches to the next expiry: *r*ₜ = F1ₜ / F2ₜ₋₁ − 1. The contract held is the old second contract.

**Detecting roll days.** The heuristic is fixed now.
- Within each calendar month, the roll day is the trading day in the window that maximises |ln(F1ₜ/F1ₜ₋₁)| − |ln(F1ₜ/F2ₜ₋₁)|, provided that is > 0.
- The window is days 15–28 for WTI and days 20–31 plus days 1–3 of the next month for natural gas.
- The number of detected rolls per year is reported as a check; it should be about 12.

**Negative prices.** WTI's contract 1 settled negative on 2020-04-20.
- The **decision** uses data **excluding April 2020** (negative prices; the CFDs this programme trades did not go negative).
- Results including it are also reported.

## Rule (monthly)

- At the **last trading day of each month**, compute *s* = ln(F1 / F2).
- If *s* > 0, hold the front contract **long** for the next month; if *s* < 0, **short**; if *s* = 0, flat.
- The position is the front contract, rolled as above. The monthly return is the compounded daily returns, times the side.

**Costs.** 0.10% per month, deducted every month to cover the roll and a possible side change. This is conservative for futures. **Reported but not deciding:** a cost of 0.25% per month.

## Periods

| Period | WTI | Natural gas |
|---|---|---|
| **DEV** | 1986-02 → 2009-12 | 1994-02 → 2009-12 |
| **HOLDOUT** | 2010-01 → 2026-10 | 2010-01 → 2026-10 |

Also reported: 2023-01 → (this programme's era).

## Statistics and decision

- The mean monthly net return, with a Newey–West t (3 lags) and a one-sided p.
- Also reported: a 10,000-draw random-sign benchmark p, and the always-long front-contract mean.
- **Two tests** (WTI, natural gas), Benjamini–Hochberg at 5% on the HOLDOUT p.

| Label | Conditions |
|---|---|
| **CONFIRMED** | mean > 0 in DEV and HOLDOUT, and HOLDOUT p ≤ 0.05 surviving BH |
| **WATCH** | positive in both, but not significant |
| **REJECT** | otherwise |

**Caveat, fixed now.** These are futures returns. Exness oil CFDs pass carry through their swap and roll adjustments, which this test does not model. A CONFIRMED result would need its own CFD-cost check before anything else.
