# RSI + VWAP entries on gold (XAUUSDm), 2025-01 to now

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any gold quote was downloaded.
The code, rules, costs and pass rule are those of the US oil study (`research/oil_rsi_vwap`). Nothing in earlier
studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict: RSI + VWAP entries have no edge on gold

**VWAP momentum BUY made money on gold, but only because gold rose 58%.** Random long entries with the same exit,
costs and trade count made more: +0.179R against the rule's +0.146R. Random entry did at least as well in 68% of
runs, and t is only 1.25, so the rule fails the pre-registered test. The SELL and RSI-reversion variants all lost
money, and none beat random entry.

## Data and costs

- **Data.** Exness XAUUSDm, every bid and ask quote, aggregated to 15-minute bid/ask candles. Statistics cover
  2025-01-01 to 2026-11-09. 2024-03 to 2024-12 was used only for indicator warm-up.
- **Market context.** Gold rose 58% over the period. 2025 was entirely a bull regime.
- **Fills and costs.** The median spread was 0.005% of price, much tighter than oil. Primary cost adds 0.02%
  slippage. Stress cost adds 0.05% slippage and 0.02% per day held for swaps.

## Results, 2025-01 to now (primary cost)

| Variant | Trades | Win rate | Profit factor | Expectancy | 95% CI | t | Random entry | p vs random | Max drawdown | Stress cost |
|---|---|---|---|---|---|---|---|---|---|---|
| **VWAP momentum BUY, trail (primary)** | 236 | 31.8% | 1.26 | +0.146R | −0.08 to +0.38 | 1.25 | **+0.179R** | 0.68 | 28.6R (13.5%) | +0.062R |
| VWAP momentum BUY, ±1R | 354 | 50.8% | 0.99 | −0.003R | −0.11 to +0.10 | −0.05 | +0.028R | 0.76 | 27.9R (13.1%) | −0.065R |
| VWAP momentum SELL, trail | 204 | 32.8% | 0.90 | −0.061R | −0.25 to +0.14 | −0.60 | −0.124R | 0.18 | 40.5R (18.5%) | −0.138R |
| VWAP momentum SELL, ±1R | 296 | 47.3% | 0.84 | −0.084R | −0.20 to +0.03 | −1.49 | −0.082R | 0.51 | 32.7R (15.3%) | −0.142R |
| RSI reversion BUY, trail | 96 | 35.4% | 0.78 | −0.116R | −0.35 to +0.14 | −0.93 | +0.115R | 0.94 | 16.8R (8.2%) | −0.183R |
| RSI reversion BUY, ±1R | 96 | 47.9% | 0.90 | −0.046R | −0.24 to +0.15 | −0.48 | −0.012R | 0.65 | 13.8R (6.7%) | −0.097R |
| RSI reversion SELL, trail | 115 | 27.8% | 0.59 | −0.250R | −0.46 to −0.04 | −2.29 | −0.180R | 0.75 | 31.8R (14.8%) | −0.326R |
| RSI reversion SELL, ±1R | 115 | 40.0% | 0.67 | −0.184R | −0.36 to −0.02 | −2.10 | −0.116R | 0.79 | 24.6R (11.7%) | −0.245R |

1R is 2 × ATR14 at entry. Drawdown percentages assume 0.5% risk per trade. "p vs random" is the share of 2,000
matched random-entry runs that did at least as well. All Holm-adjusted p-values are 1.0.

### The primary rule by year and regime

| Slice | Trades | Expectancy |
|---|---|---|
| 2025 (all bull regime) | 127 | +0.40R |
| 2026 | 110 | −0.15R |
| Bull regime | 190 | +0.17R |
| Bear regime | 36 | +0.03R |
| Without its 5 best trades | 231 | +0.01R |

The profit came from riding gold's 2025 rally, and random long entries captured it just as well. When the rally
paused in 2026, the rule lost money. With the ±1R exit the same entry is flat, so it does not predict direction.

## What this means

- **Don't use RSI + VWAP entries on gold.** A positive backtest here is the market's rise, not the signal.
- **The pattern now holds across three markets.** On BTC/ETH the rule beat random entry narrowly; on US oil and on
  gold it did not. That makes the BTC/ETH result more likely luck or crypto-specific.

## Reproducing

```bash
cd research/gold_rsi_vwap
python ../oil_rsi_vwap/src/build_bars.py XAUUSDm 2024-03 2026-11 data/XAUUSDm_15m.csv.gz /tmp/gold_parts
python src/run_gold.py      # about 1 minute; writes reports/results.json
```

The engine and its tests live in `research/oil_rsi_vwap`. All random procedures use seed 20261110.
