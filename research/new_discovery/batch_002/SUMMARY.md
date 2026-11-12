# Batch 002 summary

- **Pre-registration:** `PREREG.md` (commit `8c7ceecf`, made before any result), with amendment 1 (pre-holiday execution time) disclosed in commit `5939db81`.
- **Results:** `RESULTS.md` and `results/batch_002.json`. Registry: `../REGISTRY.csv` and `../REGISTRY.md`.
- **Scale:** 38 tests, one pre-set setting each. **TEST is reused evaluation data** (seen in batch 001 for the same price series).

## Outcome: 0 SCREEN-PASS, 9 WATCH, 29 REJECT

| ID | Idea | Result |
|---|---|---|
| E005 | Volatility-managed exposure | Raised the TEST Sharpe only for gold (+0.48, p 0.084) and US oil (+0.05). It **hurt** in 9 of 11 markets: US indices −0.3 to −0.6, USD/JPY −0.28. This matches the out-of-sample criticism of volatility timing (Cederburg et al. 2020): it cut exposure at the wrong times for index CFDs. REJECT ×11. |
| E006 | HAR-RV against EWMA variance forecasts | HAR had lower forecast loss in TEST in **9 of 11** markets, and in all three periods in **6**: BTC, ETH, EUR/USD, GBP/USD, S&P and Nasdaq. Only DAX survives the correction (DM +4.1), and its TRAIN period was negative, so it is REJECT. Gold and US oil were worse with HAR in TEST. |
| E007 | Two-state hidden-Markov regime filter | It worsened the Sharpe ratio in most markets. Its exposure was often near zero (forex 1–4%), so it mostly kept the strategy flat. USD/JPY was positive in all three periods but tiny in TEST (+0.04, p 0.47). The HMM needs 250 days, so TRAIN had little or no exposure for several markets, which makes them untestable there. |
| E008 | BTC → ETH and ETH → BTC 15-minute lead-lag | Negative in every period at primary cost (−3 to −18 bp per trade). The "laggard" does not catch up within 15 minutes beyond the spread. REJECT ×2. |
| E009 | Pre-holiday effect | S&P (+3.5 bp) and Nasdaq (+9.0 bp) were positive in every period, but **no better than ordinary days**: their ordinary-day means were +3.5 and +6.2 bp in TEST (p ≈ 0.5). There were only 12–13 events per period. The DAX had 4–6 events and a negative VALID period. |

## Lessons and limitations

- **Volatility timing does not transfer to these CFDs**: it lowered risk-adjusted returns where it mattered most (the US indices).
- **HAR is the one consistently useful building block**: it gave better variance forecasts in most markets. But the comparison is **not fully fair**, because HAR is fitted directly to the realised-variance target while EWMA forecasts close-to-close variance without rescaling. A scale-calibrated EWMA (EWMA of RV itself) is the fair follow-up, and it is pre-registered next.
- **The pre-holiday tests are underpowered.** About 10 US holidays a year cannot separate a few bp from ordinary days in under 4 years.
- **The HMM's 250-day warm-up** leaves TRAIN partly untestable.

## Next (batch 003, to be pre-registered before running)

1. **A fair volatility-forecast comparison:** HAR against EWMA of RV and a GARCH(1,1)-type baseline. If HAR still wins, use it as the risk unit for sizing, measured by drawdown and Sharpe at equal average risk, not by direction.
2. **The other session's H1–H5** (funding, basis, order flow, volatility risk premium, carry) remain **its** pending proposals, awaiting the user. They are not run here, to avoid duplication.
3. **Forward-only validation** for every WATCH item that is still of interest: E006 HAR on the 6 markets.
