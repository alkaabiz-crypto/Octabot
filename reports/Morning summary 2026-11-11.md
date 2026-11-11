# Morning summary, 11 November 2026

Everything below is research and paper testing with fake money. Nothing touched your Exness account, no real or demo trades were placed, and no data from before January 2025 was used.

## 1. What I checked overnight (all passed)

| Check | Result |
|---|---|
| Re-did 3 backtest results with separate, simple code (gold, oil, BTC) | All match: oil and BTC exactly, gold within 0.2 points |
| Trend bot's first real decision (00:00 UTC) against a fresh Binance download | Correct. **BTC 25%** (above only its 200-day average), bought 680.74 $ at 73,796; **ETH 0%** (below all averages) |
| BTC Donchian paper test audit | 0 critical problems, 0 mismatches; still 0 of 40 trades |
| Reran the 2025 trend-bot backtest | Every number came out identical |
| GitHub | Everything saved and matching |

## 2. Backtest of the research shortlist (Jan 2025 to Oct 2026, real Exness costs, also at double costs)

| Rule | Result | Verdict |
|---|---|---|
| **Gold: buy on 50-day momentum, ATR stop, trailing stop, 30-day exit** | **+49% vs +32% for holding gold, worst drop −13% vs −27%** | **Best result. Now a paper test** |
| Gold: hold only 22:00–07:00 UTC (Asian hours) | +20% | Passed. The swap fee most likely never applies, because entry is after the daily fee time |
| BTC above its 50-day average | +29% while BTC fell 21% | Passed (already inside the trend bot) |
| ETH breakout rules | +4% to +38% while ETH fell 37% | Passed, but weak: independent studies doubt single-coin crypto rules |
| **US oil: every rule** | Intraday momentum −15% to −24%; trend rules too few trades | **Failed.** The oil signal is about zero before costs, and the spread eats it |

## 3. Second deep research round (report: `reports/Trading signal evidence gaps.md`)

- **No independent replication on 2025–26 data exists** for any of the top published rules. Our own backtest is the best check available.
- **Gold:** Exness's gold spread is tiny (about 0.6 basis points per round trip), so costs don't kill the gold rules. Slow trend rules (200-day and 10-month averages) reacted late to gold's 2026 fall, about 20% below the peak.
- **US oil:** the best published oil signal was wiped out by market shocks and trading costs in later studies. No oil rule deserves real money.
- **Bitcoin:** studies are split on whether the 50-day average adds anything for bitcoin alone. The strongest results are for baskets of 20 coins.
- **Exness:** gold and US oil look swap-free by default for most clients, but check the swap values in your MT5 symbol specification.

## 4. What's running now

| Paper test (fake money) | Status |
|---|---|
| **NEW: Gold momentum + ATR rule** (10,000 AED, Hyperliquid gold prices) | First decision at tonight's daily close (00:00 UTC Nov 12) |
| Trend bot, BTC and ETH (lump sum and 10 $/day DCA) | Running since 00:00 UTC today; BTC 25%, ETH 0% |
| BTC Donchian breakout | 0 of 40 trades; the trend filter is still down |
| SignalPro tracker | No live signals since SP-001 |
| Daily web research | Every day at 08:43 UAE |

**One thing needs you:** adding the new gold test to the hourly scheduled task needs your approval, and the request timed out while you slept. Until you approve it, I'm running the gold test by hand in each hourly update.

## 5. My recommendation

1. **Real money: plain DCA, no leverage.** Nothing in this research changes that.
2. **Watch the gold momentum paper test.** It's the strongest new rule; judge it after 20 trades.
3. **Stop the Exness oil DCA bot**, or set a hard stop. No oil rule held up in any test.
4. **Ignore signal apps.** There's still no independent evidence they work.
