# Batch 004 results: commodity term structure

Pre-registered in `PREREG.md` (commit `db056629`, before the data were parsed). Two tests, Benjamini–Hochberg at 5% on the HOLDOUT p.

**Data limitation, disclosed.** EIA stopped publishing these NYMEX futures settlements on **2024-04-05**, so HOLDOUT is 2010-01 → 2024-03 (not 2026-10 as planned), and the 'since 2023' slice is only 16 months. Roll detection found about 12 rolls a year in every complete year (WTI 10–12, NG 11–12).

| Market | Period | Months | Mean net / month | NW t | p (one-sided) | p random sign | Always-long mean | Share backwardated |
|---|---|---|---|---|---|---|---|---|
| WTI | DEV | 299 | +1.872% | 3.16 | 0.0008 | 0.0007 | +1.561% | 0.555 |
| WTI | HOLDOUT | 171 | +0.238% | 0.34 | 0.3688 | 0.3589 | +0.383% | 0.333 |
| WTI | since_2023 | 16 | -0.806% | -0.47 | 0.6817 | 0.6383 | +1.049% | 0.5 |
| NG | DEV | 191 | +1.359% | 1.08 | 0.1394 | 0.142 | -0.190% | 0.183 |
| NG | HOLDOUT | 171 | +0.240% | 0.22 | 0.4141 | 0.3784 | -1.489% | 0.211 |
| NG | since_2023 | 16 | +0.829% | 0.25 | 0.4008 | 0.4059 | -7.574% | 0.25 |

**Decisions:** WTI **WATCH**, natural gas **WATCH** (positive in DEV and HOLDOUT, not significant in HOLDOUT; 0 of 2 significant after BH).

Including April 2020 (negative WTI prices) changes WTI's HOLDOUT mean from +0.238% to +0.355% per month (p 0.32), and leaves the decision unchanged.

## Reading

- **WTI's term-structure premium was strong in 1986–2009:** +1.87% a month net, NW t 3.2, p 0.0008. That matches the literature, which used mostly pre-2010 data.
- **It has mostly gone since 2010:** +0.24% a month, p 0.37. Natural gas shows the same fade (+1.36% → +0.24%, neither significant).
- This is a textbook example of a published anomaly decaying after publication and the financialisation of commodities around 2005–2010.
- The last 16 months available (2023-01 → 2024-03) were negative for WTI (−0.81% a month).
- **Not pursued further.** Its futures returns also do not translate directly into Exness CFD returns, whose swaps carry the roll economics.
