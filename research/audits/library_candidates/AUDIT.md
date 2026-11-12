# Read-only statistical audit: ETH Fibonacci, Gold FVG, Oil Fibonacci (12 November 2026)

**Scope and method.** This audit reads the frozen theory library (branch `claude/download-skill-27d08k`, freeze commit `9c158d62`; `verify_freeze.py` reported 90 of 90 files intact at the start and again at 19:23 UTC). It changes nothing there, nor in `library_forward`, any ledger or any strategy parameter. Its historical conclusions are not edited; this document records findings beside them. No parameter search was run.

**Code in this folder.**
- `audit_eth_fib.py` imports the frozen `verify_minute.py` **unchanged** from an extract of the branch.
- `replay_forward_eth.py` replays the frozen `forward.py` **unchanged** (only its network fetch is replaced by historical data), in a scratch copy.
- Results: `eth_fib_audit.json` and `replay_forward_eth.json`.

**Data.**
- **ETH.** Binance ETHUSDT spot 1-minute klines, from the public monthly and daily files at `data.binance.vision`. These are the same klines the library fetched from `data-api.binance.vision`; the 2025+ files use microsecond timestamps, which were converted.
  - 977,760 minutes from 2025-01-01 00:00 to 2026-11-10 23:59, with no gaps. They were truncated to the frozen cutoff, **2026-11-10 11:19 UTC** (977,000 minutes).
  - Not committed (Binance terms; public repository).
- **Gold and oil.** The library's Exness 1-minute bars are not available in this session. Exness 15-minute bid/ask candles (2025-01 to 2026-10-30 20:57 UTC) were used as an **approximation** (section 4). They are not committed either.

## 1. Reproduction (pass 1)

| ETH at 2× cost | Frozen (`candidate_stats.json`) | Re-run here with the frozen code |
|---|---|---|
| 2025 | 326 trades, +32.28 bp | **326, +32.28 bp** |
| 2026 | 288, +19.62 bp | **288, +19.62 bp** |
| 2026, common cutoff (hourly data through 2026-11-09 23:00) | 287, +19.09 bp | **287, +19.09 bp** |

The preserved cutoffs (1-hour through 2026-11-09 23:00, 1-minute through 2026-11-10 11:19) reproduce exactly.

On the 15-minute approximation, gold FVG gives 388 / 311 trades at +4.60 / +10.65 bp, against the frozen +4.78 / +10.97. Oil Fibonacci gives 211 / 178 at +12.92 / +17.40, against +12.87 / +17.30.

## 2. CONFIRMED ERROR: the backtests' limit-order selection uses future information

**Where.** This is the same structure in `verify_minute.py` (`b9`, `d4`, used for the V1 minute-level verification and `candidate_stats.py`) and in the screen engine `theories.py` (`b9` lines 222–235 and `d4_fvg` from line 387).

**What the code does.**
- A signal at candle *i* places a limit order valid for candles *i+1 … i+10*.
- The code scans that **whole** window.
- If the order never fills, it moves to *i+1* and places that candle's order from *i+2*.

**Why that is look-ahead.**
- In real time, at any minute inside the window, nobody knows whether the older order will fill later.
- The backtest takes the newer order's trade **only when the older order never fills during its whole window**, so it conditions on future prices.
- For a long Fibonacci order, "the older, deeper limit was never reached in the next 10 hours" means price did **not** fall that far. The newer trade is therefore selected in exactly the cases where the subsequent path was favourable.

**The forward test does not do this.** `library_forward/forward.py`:
- keeps every pending order;
- takes the first one to fill in time, checking the oldest first;
- cancels the rest.

That is causal. So the backtest and the forward test **implement different strategies**.

**Measured effect.** Everything else is identical: signals, 10-candle order life, fills with one-spread penetration, stop before target, 20-candle time exit, costs.

| 2× costs, mean bp per trade (trades) | Frozen backtest rule (non-causal) | Forward test's rule (causal) | One order at a time (causal) |
|---|---|---|---|
| **ETH Fibonacci 2025** | +32.28 (326) | **−19.95 (354)** | −15.18 (300) |
| **ETH Fibonacci 2026** | +19.62 (288) | **−9.73 (301)** | −26.73 (254) |
| ETH 2026, common cutoff | +19.09 (287) | −10.34 (300) | −27.52 (253) |
| Gold FVG 2025 (15m approx.) | +4.60 (388) | −0.04 (400) | +0.36 (272) |
| Gold FVG 2026 (15m approx.) | +10.65 (311) | +4.71 (314) | +2.05 (226) |
| Oil Fibonacci 2025 (15m approx.) | +12.92 (211) | +2.75 (224) | −11.23 (188) |
| Oil Fibonacci 2026 (15m approx.) | +17.40 (178) | +0.06 (187) | −31.95 (160) |

**Independent confirmation.** The **frozen `forward.py` itself**, replayed unchanged over the ETH history, gives **2025: 354 trades, −19.95 bp; 2026: 300 trades, −10.35 bp** (`replay_forward_eth.json`). That matches this audit's own causal implementation to within one trade.

**Consequence.** The historical edge of all three candidates comes almost entirely from the order-selection look-ahead.
- Under the causal rule the live paper tests use, the backtests show:
  - ETH negative in both years;
  - gold about zero to +5 bp;
  - oil about zero.
- None would meet the frozen candidate rule (> 0 and ≥ 2 bp at 2× costs) in both years, except possibly gold's 2026 on the approximation.
- The forward paper tests themselves are **valid**, because they are causal. But their **prior expectation should now be about zero or negative, not the backtest figures**.

**Also affected, by code inspection only, not measured.** The same "if not filled within the window, retry from the next candle" structure appears in `theories.py` `stop_break` (used by the stop-entry theories, for example C3) and in `theories_f.py` `f11`. Their screen results may be biased in either direction.

**Proposed correction (not implemented; needs the user's authorisation).**
- Re-evaluate the pending-order theories with the forward test's causal order selection, as a **separately documented** re-analysis outside the frozen library.
- Report the candidates' causal backtests next to the frozen ones.
- Keep the forward tests unchanged.
- The frozen library's conclusions are not edited here.

## 3. Statistical assumptions (ETH, 2× costs, frozen rule)

| Check | 2025 | 2026 (all / common cutoff) | Finding |
|---|---|---|---|
| Overlapping trades within the strategy | 0 | 0 / 0 | One position at a time is confirmed. The compounded "whole account per trade" figure is feasible for one strategy alone. |
| Time in market | 40.5% | 38.9% | Running the three candidates together would need capital split three ways or leverage; this is not modelled anywhere. |
| Serial correlation, lags 1–5 | 0.005, 0.061, −0.032, −0.098, 0.060 | −0.030, 0.048, **0.182**, 0.090, 0.058 | Lag 3 in 2026 is notable. |
| Ljung–Box Q(5) (5% critical 11.07) | 5.96 | **14.05 / 14.52** | Independence is rejected in 2026. |
| t-statistic, iid / Newey–West (5 lags) | 2.68 / 2.67 | 2.05 / **1.82**; 1.99 / **1.76** | Dependence-aware, the 2026 mean is **not** significant at 5%. |
| 95% CI of the mean, iid t (frozen) / stationary block bootstrap | +8.6…+56.0 / +7.9…+56.5 | +0.8…+38.5 / **−3.2…+44.8**; cutoff −3.9…+44.8 | The bootstrap interval includes zero in 2026. |
| Max drawdown, compounded: at trade closes (frozen) / marked to market by the minute | −23.7% / **−24.4%** | −20.4% / −20.7% | The trade-close figure slightly understates. |

**Fees.**
- The library's "1×" ETH cost is 0.05% per side, which is half of Binance's standard spot fee for a regular account (0.10% maker and taker; 0.075% with the BNB discount).
- So the **"2×" scenario, not "1×", is the realistic one**, and every 1× ETH figure (+42.3 / +29.6 bp, +137.8% / +85.3%) is optimistic.

## 4. The 500-run random benchmark (`engine.random_control`, `sensitivity_hole.rand_means`)

**How it works.**
- Each draw places the strategy's trades, with the same sides and the same durations in candles, at **independent uniform random start candles** within the period.
- Entry is at the candle open, the hold lasts the same number of candles, and there is no stop or target. Costs are 2×.
- The minute-level mean is ranked against the 500 draw means.

**Limitations confirmed by inspection.**
- **Resolution.** With 500 draws, "percentile 100" only means p < 0.002 for that single combination. It is not corrected for the 535 combinations or for the selection of the best ones.
- **Not matched to the strategy's exits.** The control holds to a fixed time, while the strategy's exits depend on the path (stop or target). The two return distributions differ in shape, and the comparison mixes timing skill with exit structure.
- **Not matched to the entry mechanism.** The control enters at the open, while the strategy enters with a limit order after a pullback. The control does not ask whether *these* limit levels beat random limit levels.
- **Built from screen-level trades, but compared with minute-level means.** The candidate documents label this approximate.
- **Independent, overlapping draws.** With about 40% time in market, random trades overlap each other, unlike the strategy's sequential trades. In this branch's own audit (`research/audit/`), this kind of control mis-states the null variance when exposure is high, so the percentile's calibration is unknown.
- **Most decisively:** the benchmark cannot detect the look-ahead in section 2. The look-ahead lives in which trades are taken, not in their timing relative to random entries.

## 5. Multiple testing

- **The frozen library already reports that no candidate reaches the Bonferroni bar** for 535 combinations (|t| ≥ about 3.9). This audit agrees, and adds:
  - with dependence-aware t (Newey–West), ETH's 2026 is 1.76–1.82;
  - under the causal rule, ETH's t is negative.
- **The family is larger than 535.** The candidates also passed sequential gates (screen, 9-neighbour check, minute re-test V1/V3, hole sensitivity). On the same branch there were further searches: ORB 40, zone reversal 60, session 3, the shortlist (about 20), batch 2 (8 hypotheses) and earlier studies. This branch adds more than 100,000 tests. No correction accounts for that whole family.
- **The forward pass rule is weak.** After 100 trades it requires mean net > 0 and ≥ 2 bp at 2× costs, with no significance test. With ETH's per-trade sd of 162 bp, the standard error at 100 trades is 16.2 bp. A strategy with **zero** true edge passes with probability **about 45%** (normal approximation; gold's is about 40%, from its sd of 80 bp). This is a limitation of the frozen rule, recorded here and not changed.

## 6. Compounding, sizing and capital

- The compounded figures put the whole account in every trade, with no leverage. That is feasible per strategy, because trades don't overlap, but **not for the three candidates combined**, whose combined time in market would exceed 100% at times.
- ETH risks 1.1–1.7% of the account per trade (the median stop distance) at full notional.
- The drawdowns (−20% to −24%) are measured at trade closes. Minute marking adds about 0.3–0.7 points.
- "Simple sum" is the honest additive figure, and "compounded" is path-dependent. Neither includes a funding or margin model.

## 7. Feed differences

- **ETH:** the backtest and the forward test use the same feed and costs (Binance spot, 0.05% per side, 1 bp penetration).
- **Gold and oil:** backtests on Exness CFD bars, forward tests on Hyperliquid xyz perpetuals.
  - The forward cost is a fixed spread taken from Exness (gold 0.22 USD/oz, oil 0.02 USD/bbl).
  - Hyperliquid's own taker and maker fees and its hourly **funding** are **not modelled** in the forward tests.
  - Level differences and correlations are documented in `FREEZE.md` §1: hourly return correlation 0.996 for oil, about 0.1–0.2% level gap for gold.
- **Unresolved:** whether Hyperliquid fees and funding are material at these holding times (7–15 hours).

## Summary

| Category | Item |
|---|---|
| **Confirmed error** | Non-causal limit-order selection in the backtests of B9 and D4 (screen and minute verification). Under the forward test's causal rule, the three candidates' historical edges disappear: ETH −20 / −10 bp; gold about 0 / +5; oil about 0 / 0. This was confirmed by replaying the frozen `forward.py`. |
| Confirmed limitation | ETH 2026 returns are serially dependent (Ljung–Box 14.1). Its Newey–West t is 1.76–1.82, and its bootstrap CI includes zero. |
| Confirmed limitation | ETH's "1×" cost is half of Binance's standard fee; "2×" is the realistic case. |
| Confirmed limitation | The random control is not matched to exits, entries or selection, and cannot detect the order-selection bias. |
| Confirmed limitation | The forward pass rule passes a zero-edge strategy with probability about 40–45%. |
| Confirmed limitation | The compounded returns cannot be combined across the candidates without a capital model. |
| Unresolved | Whether other pending-order theories (`stop_break` users, F11) are biased, and in which direction. Gold and oil were checked only on the 15m approximation, not on the exact 1-minute bars. Hyperliquid fees and funding are not modelled in the forward tests. |
| Not changed | Every frozen file, historical result, conclusion, forward configuration and ledger. |
