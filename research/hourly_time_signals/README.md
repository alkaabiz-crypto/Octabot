# Hourly time-of-day signals on oil, gold and BTC

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Verdict: none of the published hourly effects works on Exness after costs

Four hourly signals were taken from published research and tested on Exness bid/ask quotes. Each had to beat its
random benchmark in 2025 and again in 2026. **None did.** Two looked good in one year and failed in the other, which
is the pattern luck produces.

## Results (net of the real spread and 0.02% slippage; 1 bp = 0.01% of price)

| Signal | Year | Trades | Win rate | Mean per trade | t | Random benchmark | p vs random | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Oil intraday momentum**: trade the last half-hour (14:00–14:30 New York) in the direction of the first half-hour | 2025 | 249 | 42.6% | −5.5 bp | −2.77 | −4.8 bp | 0.63 | Fails |
| | 2026 | 213 | 43.7% | −8.1 bp | −1.99 | −4.3 bp | 0.82 | |
| **Gold Asian-hours long**: buy 00:00, sell 07:00 UTC | 2025 | 258 | 50.0% | +3.4 bp | 0.97 | +2.3 bp | 0.37 | Fails |
| | 2026 | 221 | 48.0% | −1.5 bp | −0.20 | −2.4 bp | 0.42 | |
| **Gold US-hours short**: sell 13:00, buy back 20:00 UTC | 2025 | 249 | 41.8% | −6.3 bp | −1.36 | −7.4 bp | 0.35 | Fails |
| | 2026 | 215 | 47.9% | +9.1 bp | 1.30 | −2.8 bp | **0.009** | |
| **BTC late-evening long**: buy 21:00, sell 23:00 UTC | 2025 | 362 | 50.3% | +4.1 bp | 1.25 | −4.2 bp | **0.006** | Fails |
| | 2026 | 311 | 44.1% | −4.4 bp | −1.37 | −3.9 bp | 0.57 | |

The two benchmarks work differently:

- **Oil:** the random benchmark uses the same days and window, with a coin-flip direction.
- **Gold and BTC:** it uses the same direction and holding time, starting at a random hour of the same day. This
  separates "these hours are special" from "the market went up anyway".

### What happened to each

- **Oil intraday momentum.** The direction of the first half-hour did not predict the last half-hour at all. A coin flip
  did as well. The half-hour move is also small next to the cost of trading it: the measured spread plus slippage is
  about 5 bp per trade, roughly the whole loss.
- **Gold Asian hours.** These were slightly positive in 2025, but no better than any other 7-hour window that year.
  They lost in 2026.
- **Gold US-hours short.** It lost in 2025, while gold was rallying, and won in 2026. One good year after one bad year
  is not a repeatable effect.
- **BTC 21:00–23:00 UTC.** It beat other hours clearly in 2025, then lost in 2026, like other hours. It also holds through
  the daily swap rollover, and at stress cost even 2025 is about zero (+0.4 bp).

## Why the published effects did not survive

- **Most were measured before costs**, on futures with tiny spreads. On Exness the spread and slippage are about 2 to
  5 bp per trade. That is as large as the effects themselves.
- **Published effects decay** once traders know about them. Several of these studies used data from before 2020.
- **Some evidence was weak to begin with.** The BTC hour-of-day effect came from one exchange, and a 7-exchange study had
  already found no persistent pattern.

## Where this leaves the search for signals

Across every study in this research, the only signal that beat random entry in a pre-registered test and replicated on
a second market is VWAP momentum BUY with a trailing stop on BTC/ETH (`research/rsi_vwap_study`). Even that fails on oil
and gold. Hourly indicators, community indicators and hourly time effects have all failed on oil, gold and BTC.

## Reproducing

```bash
cd research/hourly_time_signals
python src/run_hourly.py                            # under a minute
python -m unittest discover -s tests -p "test_*.py"
```
