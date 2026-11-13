# Batch 3: indicators, strategies, theories and mixes

**Results (2026-11-13, rules in `PREREGISTRATION.md`, committed before running at 65ecd833)**

## What was tested

**238,728 combinations** in total: 7 markets × 3 timeframes × 3 exit rules × the following entries.
- **Part A, indicators:** 26 entry indicators, each alone, with 1 filter or with 2 filters (14 filters), so up to 3 indicators at once.
- **Part B, strategies:** 25 published rule sets (Golden cross, MACD + EMA200, Connors RSI-2, Turtle, TTM squeeze, Ichimoku, Supertrend + EMA200 …).
- **Part C, theories and mixes:** 9 theories (the user's Theory #2, FVG, liquidity sweep, break of structure, opening-range and Asian-range breaks, Fibonacci reclaim, previous-week break, VWAP 2σ). Each was tested alone, with the wick-rejection ("John Wick") candle, with 1–2 indicator filters, and with wick + filter.

**Execution:** every entry is at the next bar's open, so no limit-order look-ahead is possible.

**Engine checks** (`run.py --sanity`):
- random signals lose about the spread;
- a look-ahead "cheat" signal shows +55 bp (t = 68), so the engine can see an edge;
- a hand-computed trade matches the engine to 0.001 bp.

## Search (2025, lenient)

**66,463 combinations made money in 2025** at normal cost with ≥ 30 trades: 46,737 indicator mixes, 557 strategies and 19,169 theory mixes.

## Confirmation (2026, unseen for selection; top 30 per part, 90 in total)

| Part | 2025 average of the 30 | 2026 positive at 2× cost | 2026 median | p < 0.05 vs random timing |
|---|---|---|---|---|
| A, indicators | +36.8 bp | 12 / 30 | −2.0 bp | 2 |
| B, strategies | +28.1 bp | 15 / 30 | +1.1 bp | 2 |
| C, theories + mixes | +42.0 bp | 9 / 30 | −6.3 bp | 0 |

**PASS: 0 of 90.**
- **Expected by chance:** 4 of the 90 reached p < 0.05, against 4.5 expected from luck.
- **Corrections:** none survives Holm (needs p ≤ 0.00056) or a lenient false-discovery rule (Benjamini–Hochberg at q = 0.10).

**Closest** (all failed the pre-registered bar):

| Market, timeframe, exit | Entry | 2026 result at 2× cost | p |
|---|---|---|---|
| Gold 4h, X1 | Turtle 20-bar breakout | +57 bp over 54 trades | 0.010 |
| BTC 4h, X3 | Stochastic + EMA200 trend | +124 bp over 28 trades | 0.016 |
| Nasdaq 1h | PSAR flip + ADX < 20 + RSI | +13.6 bp over 95 trades | 0.027 |

Gold rose strongly in 2026, which favours trend-following breakouts.

**The user's Theory #2 mixes:** 10 made the shortlist (+7 to +66 bp in 2025). In 2026, 8 of the 10 lost money. The best was gold 4h with HTF trend + EMA20 slope: +28.8 bp over 25 trades, p = 0.21.

## Reading

Winning in 2025 did not predict winning in 2026: the shortlisted combinations fell back to about zero. That is the signature of selection luck, not a lasting edge. With hundreds of thousands of combinations, tens of thousands look good on one year by chance alone, so "thousands of indicators pass" in a backtest is expected, not evidence.

The test was **not** hard:
- the search was lenient;
- the correction counted only 90 items;
- one market-year of unseen data was enough to show the fall-back.

**Files:** `results/search_2025.json` (shortlist and counts) and `results/confirm_2026.json` (every shortlisted item's 2026 result).
