# Research status, 2026-11-23 (weekly, Monday)

**Bottom line:** every scheduled run succeeded. The forward tests now have 0–5 closed trades each, mostly losing, but all are far from any decision point and far from their drawdown limits. This week's new research (about 20 strategies, including the reels you sent, CryptoMeter, market making, ETF flows and negative correlation) found **no** validated edge after costs.

## Scheduled runs (last 7 days)

- Daily paper runs: **8 SUCCESS, 0 FAILED** (2026-11-16 → 2026-11-23, all scheduled).
- Watchdog: **ALL OK** (daily paper run 11-23 03:24; Coinbase premium 11-23 04:48; STR-023 11-22 05:22).

## Running tests

| Test | Closed trades | Mean (primary cost) | Cumulative / drawdown limit | Decision state |
|---|---|---|---|---|
| BTC Pivot Reversal BUY | 4 (25% win) | −0.46R | −1.86R / −49R | futility check at 200 legs |
| ETH Pivot Reversal BUY | 5 (20% win) | −0.54R | −2.69R / −37R | futility check at 200 legs |
| Gold KST, 48 h time stop (primary) | 4 (0% win) | −1.02R | −4.09R / −37R | futility check at 100 legs |
| Gold KST, 2×ATR stop + news close | 4 (0% win) | −1.02R | −4.08R / −58R | futility check at 100 legs |
| STR-008 Coinbase premium (BTC) | 4 | −146 bp | – | first look at 100 trades; no open position |
| STR-023 VWAP momentum BTC / ETH | 2 / 4 | −0.98R / −0.85R | – | first look at 100 per market; ETH BUY open at 1686.44 |
| STR-025 volatility-sizing shadow | 2 / 4 | −0.98R / −0.85R (sizing changes nothing so far) | – | follows STR-023 |
| STR-046 ETF flows (BTC, ETH) | 0 | – | – | futility at 20, first look at 40; BTC SHORT open from 11-22 at 60,215.78, exit due 12-12 |
| Batch 2 (run here since 11-16, your authorisation) | H1 ETH 1 (+319 bp); H3 BTC 5 (−54 bp); H3 ETH 5 (+9 bp); others 0 | – | – | monitoring only until each test's evaluation date; H1 BTC/ETH and H4 BTC LONG open |
| Library paper tests (other branch: GOLD_FVG, OIL_FIB, ETH_FIB) | 0 / 0 / 0 | – | – | evaluator: no closed trades. The other branch's commits are **still paused** (last commit 2026-11-13 01:10) |
| SignalPro (SIG-001–004) | 1 prospective | −1.0R | – | needs 50 prospective screenshots; none new since 11-13 |

- Theory-library freeze (other branch): **intact, 90 files match.**

## This week's research results (all paper, all pre-registered)

- **Your reels and indicators:** GainzAlgo-style (STR-032), QuantLab NY-open candle (STR-033), soualium value area (STR-043), keepssy liquidity sweep (STR-044), scuta_net NY-open + trailing stop (STR-049; the claim reproduces only with zero costs), ICT sweep/CHoCH/OTE (STR-041): all REJECTED.
- **CryptoMeter AI screener (SIG-005):** 2,019 calls, UNPROFITABLE with real stops and targets; the site's 92% "win rate" counts the best price within 30 days.
- **Market making (STR-042):** loses even before fees.
- **Academic batch, pairs, negative correlation (STR-034..040, STR-050):** nothing passes. WATCH only: gold turn-of-month, crypto weekly momentum (fading), GBP/USD–USD/CHF reversion (tiny samples).
- **ETF flows (STR-045):** REJECTED at 1–5 days; a longer-hold version is now a frozen forward test (STR-046).
- **Funding carry (STR-047):** SOMETIMES worth it (2020–22), currently below the T-bill rate. **Yields → gold (STR-048):** REJECTED.
- **Test count (G7):** 20,868.

## Due in the next 7 days

- Daily: paper tests 03:23, Coinbase premium 04:47, STR-023 05:21, Batch 2 05:37, watchdog 06:07, ETF flows 06:53 (UTC).
- Batch 2: H1 BTC/ETH LONGs exit 2026-11-25 00:01; H4 BTC LONG exits 2026-11-29 00:01.
- **2026-12-01 06:41:** first monthly honesty check (G7).
- Next weekly status: 2026-11-30 05:13 UTC.
- Later: NFP capture 2026-12-04; STR-046 BTC exit 2026-12-12; CPI capture 2026-12-10. No decision look is due this week.

## Failures

None.
