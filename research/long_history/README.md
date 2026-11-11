# Every indicator on the full available history

Paper research only. The rules were committed in [`PROTOCOL.md`](PROTOCOL.md) before any result existed. Nothing in
earlier studies, the signal assistant or the frozen Donchian forward test was changed.

## Why this re-test

The earlier rounds judged signals one year at a time. Before this study, two checks asked whether that was unfair to
the indicators.

- **Are the indicators calculated correctly? Yes.** They were compared value by value with an independent library
  (pandas_ta) on the real oil candles. These matched exactly:
  - RSI, ATR, EMA, WMA, HMA, DEMA, TEMA and LSMA;
  - MACD, Stochastic, Williams %R, ADX and ±DI;
  - Awesome and Ultimate Oscillators, ROC, Momentum and Bollinger.

  CCI matches TradingView's formula.
- **Can the test detect an edge? Yes, but one year is short.** Fake signals with a known edge were planted:
  - signals right 80% of the time about the next day's direction were caught every time;
  - signals right 70% of the time were caught 2 times in 3;
  - signals right 60% of the time were usually missed;
  - pure coin flips were correctly rejected.

So this round uses all the history available:

| Market | Test period |
|---|---|
| US oil | mid-2019 to now |
| Gold | mid-2020 to now |
| BTC | mid-2020 to now |

The data is every Exness bid and ask quote, which gives each signal 3 to 4 times more trades. It also tests every
combination with an entry filter, not just the ones that looked good in 2025. Altogether that is 8,810 variants.

## Verdict

**Still no reliable signal, on any of the three markets.**

| Market | Variants with ≥ 200 trades | Beat random at p ≤ 0.05 | Significant after correcting for the number tested | Passed every rule |
|---|---|---|---|---|
| US oil | 2,640 | 55 | 0 | 0 |
| Gold | 2,632 | 103 | 0 | 0 |
| BTC | 2,774 | 59 | 0 | 0 |

**With 8,637 variants and no edge anywhere, about 430 would beat random at p ≤ 0.05 by luck alone. Only 217 did.** The
indicators as a group did slightly *worse* than chance. With this many tries, a real edge would need a z-score of
about 4.4 to stand out. The best one found was 3.2.

**On costs:** after stress costs, only 29 of 2,640 oil variants made any money at all. Oil is the hardest of the three
for indicator trading.

## The most interesting near-misses

None passed. Each is listed with why it looks good and why it isn't proof.

| Market | Signal | Trades | Result | Why it isn't an edge |
|---|---|---|---|---|
| BTC | Pivot Reversal strategy (TradingView built-in), BUY legs | 1,405 | +0.165R per trade; positive in 6 of 7 years; +0.125R after stress cost; z = 3.2 | It is the single best of 8,637 tries, which is where luck shows up. It is not significant after correction, and it is similar in spirit to the earlier VWAP-momentum BTC candidate (buy strength, let winners run). |
| Gold | Price Momentum Oscillator or Awesome Oscillator BUY, with the 4H EMA 200 filter and a trailing stop | ~380 to 440 | +0.34R per trade; positive in every year 2020 to 2026 | Random BUY entries with the same filter and exit made +0.16 to +0.17R too. Most of the profit is just being long gold during a rally. It beats random by about +0.17R, z = 2.6 to 2.9, which is not significant after correction. |
| Gold | Built-in RSI Divergence BUY, ±1R exit | 203 | 58% win, +0.14R per trade | Few trades, and negative in two years |

## The 70% win rate, one more time

With the target at half the stop distance, the median signal won about as often as random entry:

| Market | Median win rate: signals | Median win rate: random entries |
|---|---|---|
| US oil | 60.5% | 59.7% |
| Gold | 63.4% | 64.5% |
| BTC | 61.4% | 62.3% |

Some variants exceed 70% over hundreds of trades. None passes the rules, because random entries with the same exit
win almost as often.

## What this means

- **The conclusion of the earlier rounds holds with 3 to 4 times more data.** TradingView indicators, built-in and
  community, at their standard settings, do not give a reliable hourly BUY or SELL edge on US oil, gold or BTC after
  real Exness costs.
- **The ideas worth a frozen forward paper test are long-side momentum with a trailing exit on BTC:** VWAP momentum
  BUY (`research/rsi_vwap_study`) and Pivot Reversal BUY. Both fit the same pattern: cut losers, let winners run, buy
  strength. Neither is proven.
- **On gold, "buy and trail with the trend" made money in every year**, but random entries did nearly as well. That
  is a market trend, not an indicator skill, and it would not survive a gold downtrend.
- Nothing here justifies live trading.

## Reproducing

```bash
cd research/oil_rsi_vwap
python src/build_bars.py USOILm 2019-02 2024-12 $DIR/USOILm_2019_2024_15m.csv.gz $DIR/parts
python src/build_bars.py XAUUSDm 2020-01 2023-12 $DIR/XAUUSDm_2020_2023_15m.csv.gz $DIR/parts
python src/build_bars.py XAUUSDm 2024-01 2024-02 $DIR/XAUUSDm_2024_01_02_15m.csv.gz $DIR/parts
python src/build_bars.py BTCUSDm 2020-01 2024-02 $DIR/BTCUSDm_2020_2024_15m.csv.gz $DIR/parts
cd ../long_history
python src/merge_data.py $DIR/long $DIR
LONG_DATA=$DIR/long python src/run_long.py      # about 15 minutes on 4 cores
python src/report.py                            # pass rule, writes reports/RESULTS.md and results.json
python -m unittest discover -s tests -p "test_*.py"
```
