# Multi-market study: which indicators fit which markets

This study ran the same set of about 2,950 indicator variants on 33 Exness markets: 10 forex pairs, 10 indices, 8 cryptocurrencies, and 5 commodities (gold, silver, two oils and natural gas). The variants cover the TradingView built-ins, the community indicators and their strategies, each one with and without the trend filters and with every exit rule. Rules were fixed in [PROTOCOL.md](PROTOCOL.md) before any results were seen.

- **Fit:** for each market, the 5 best variants were chosen on 2023-07 to 2024-12. The 5 best for each market class were also chosen on that period.
- **Test:** those picks were then judged only on 2025-01 to the latest candle, against random entries that use the same exits and the same costs.

The full tables are in [reports/RESULTS.md](reports/RESULTS.md). Per-market raw numbers are in `reports/raw/`.

## Result in one line

None of the 108 fitted picks held up on 2025 to now: 0 of 88 per-market picks and 0 of 20 per-class picks. Raw p ≤ 0.05 came up 8 times, where about 4 are expected by luck. None of those 8 survived the multiple-testing correction, and only some were profitable after costs.

## What the study does show

**Costs decide more than the indicator does.** The table below shows the typical loss per trade of a *random* entry in the 2025–26 period, using the same exits. It is a fair measure of how much each market charges you just to take part.

| Cheapest to trade (median random loss per trade) | Most expensive |
|---|---|
| Gold ≈ 0.00R, BTC −0.02R, ETH −0.02R, US oil −0.03R | BCH −1.69R, LTC −1.54R, natural gas −0.62R |
| JP225 −0.04R, US30 −0.05R, USTEC −0.05R, DE30 −0.06R | SOL −0.38R, XRP −0.31R, EURGBP −0.30R, BNB −0.27R |
| US500 −0.07R, silver −0.07R | most forex pairs −0.13R to −0.18R |

On the 15-minute timeframe, the Exness spread on the small altcoins and on natural gas is often bigger than the move the indicator is trying to catch. In 2026 it was sometimes bigger than the whole ATR. No 15-minute signal can work there.

**The whole-sample check is misleading at first sight.** When the two periods are combined, 548 market-variant pairs pass the false-discovery correction. But 456 of them are LTC, 33 are BCH and 30 are natural gas. Those pairs "beat random" only because they lost less than a random entry in a market where everything loses heavily. Only **2 of the 548** were actually profitable in both periods after costs:

| Market | Variant | 2023–24 | 2025–now | Older history |
|---|---|---|---|---|
| Gold | BBTrend(20,50) + session VWAP filter, BUY, trailing stop | 93 trades, +0.65R | 113 trades, +0.46R (stress +0.37R), win 49% | Lost in 2020 and 2021. It rides gold's 2023–26 bull run, so it is not a stable edge. |
| ETH | Price Momentum Oscillator + ADX>20, SELL, ±1R | 211 trades, +0.09R | 274 trades, +0.09R (stress +0.06R), win 55% | No Exness ETH data before 2023. On gold the same rule lost money every year. |

Both were found by looking at the whole sample. They are leads for a new pre-registered forward test, not confirmed signals.

## Which indicator families fit which class (discovery period only)

These are the families that topped the 2023–24 rankings. They all failed to carry into 2025–now, so read them as "what looked good", not "what works".

- **Forex:** Bollinger %B, HMA, Chaikin Money Flow, all on the SELL side with the ADX>20 filter. In 2025–now, 0 of 10 pairs were positive.
- **Indices:** QQE MOD, True Strength Index and Waddah Attar on the BUY side. They mostly track the index uptrend, and in 2025–now only 1–2 of the 10 indices stayed positive.
- **Crypto:** Range Filter BUY. It beat random in 2025–now (z +3.3) but still lost money in 6 of 7 coins because of the spread.
- **Commodities:** Klinger, TEMA and HMA SELL with ADX>20. In 2025–now, 0 of 5 commodities were positive.

## About 70% win rates

Several picks show win rates of 60–74% (for example JP225 Price Momentum BUY at 71%, and US oil Bull/Bear Power SELL at 64–71%). All of them use the "target ½ stop" exit. Random entries with that same exit win about the same share of trades. The high win rate comes from where the stop and target are placed, not from the indicator.

## Caveats

- ADA data on the Exness archive stops in August 2024, so ADA has no confirmation period.
- Gold, US oil and BTC were already searched in earlier rounds. Their discovery picks are marked as "seen in earlier rounds".
- One run of 15-month confirmation can detect only fairly strong edges. "Not confirmed" means no evidence of an edge. It does not prove that none exists.

## Audit correction (2026-11-12)

The audit in [../audit](../audit) found two problems in this study.
- **The benchmark for held legs was too strict.** This covers the strategies' own exits, hold-to-opposite-signal and the 4-bar hold.
- **The fixed 0.02% slippage was too high** for forex, indices and gold.

The results above are left as they were. The corrected results come from this study's unchanged report script run on patched data, and are in `research/audit/reports/corrected_*`. With the corrections, **Pivot Reversal BUY** passes on BTC (long history) and is confirmed on ETH (multi-market). Everything else stays not confirmed.
