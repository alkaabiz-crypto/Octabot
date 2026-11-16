# Research status, 2026-11-16 (weekly, Monday)

**Bottom line:** every scheduled run succeeded. All forward tests are still at 0–1 closed trades, far from any decision point. The week's new research (STR-027 order blocks, and TradingView batches 003–005 testing every TradingView indicator and up to 5 at once) found **no** new edge after costs.

## Scheduled runs (last 7 days)

- Daily paper runs: **5 SUCCESS, 0 FAILED** (4 scheduled, plus 1 accidental manual run on 2026-11-14 10:12, logged as manual).
- Watchdog: **ALL OK** (daily paper run 11-16 03:24; Coinbase premium 11-16 04:48; STR-023 11-15 05:21).

## Running tests

| Test | Closed trades | Mean (primary cost) | Drawdown / limit | Decision state |
|---|---|---|---|---|
| BTC Pivot Reversal BUY | 0 | – | 0 / −49R | futility check at 200 legs |
| ETH Pivot Reversal BUY | 0 | – | 0 / −37R | futility check at 200 legs |
| Gold KST, 48 h time stop (primary) | 1 | −1.09R | −1.09 / −37R | futility check at 100 legs |
| Gold KST, 2×ATR stop + news close | 1 | −1.02R | −1.02 / −58R | futility check at 100 legs |
| STR-008 Coinbase premium (BTC) | 1 | −224 bp | – | first look at 100 trades; LONG open from 11-15 18:00 |
| STR-023 VWAP momentum (BTC, ETH) | 0 / 0 | – | – | first look at 100 per market |
| STR-025 volatility-sizing shadow | 0 | – | – | waits for STR-023 trades |
| Library paper tests (other branch: GOLD_FVG, OIL_FIB, ETH_FIB) | 0 / 0 / 0 | – | – | evaluator: no closed trades. The other branch's commits are **still paused** (last commit 2026-11-13 01:10), so these are stale |
| Batch 2 H1–H4 (other branch) | not running | – | – | not authorised by you |
| SignalPro (SIG-001–004) | 1 prospective | −1.0R | – | needs 50 prospective screenshots; none new since 11-13 |

- Theory-library freeze (other branch): **intact, 90 files match.**

## This week's research results

- **STR-027** (your volumetric order blocks + EMA 21/50 + TP1–TP5): REJECTED on BTC, ETH, gold and oil.
- **TradingView batch 003:** 13 community indicators, all NONE; 10 popular double/triple combinations × 5 markets, 0/50 pass.
- **TradingView batch 004:** the remaining 40 built-ins, all NONE. The best-market study across 33 markets found the "best" market is almost always a small coin used backwards at 1 hour, which loses after costs.
- **TradingView batch 005:** the non-direction built-ins as traders use them, plus 3-to-5+ indicators at once: 0/120 pass. Every indicator is reviewed in `new_discovery/tv_batch_005/INDICATOR_REVIEW.md`.
- **Test count (G7):** about 20,700.

## Due in the next 7 days

- Daily: paper tests 03:23, Coinbase premium 04:47, STR-023 05:21, watchdog 06:07 (UTC).
- Next weekly status: 2026-11-23 05:13 UTC.
- **2026-12-01 06:41:** first monthly honesty check (G7).
- Later: NFP capture 2026-12-04; CPI capture 2026-12-10. No decision look is due this week.

## Failures

None.
