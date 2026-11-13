# STR-023 forward PAPER test: VWAP momentum BUY with the trailing exit (pre-registered 2026-11-13, before its first forward hour)

**What.** Candidate STR-023 (`../../CANDIDATES.md`). It passed on BTC and replicated on ETH in `research/rsi_vwap_study` (frozen), and was never tested on new data. Fake money, no orders.

## Rules: the study's frozen code (`rsi_vwap_study/src/study.py`), unchanged

- **Signal**, on a closed 1-hour candle: the close crosses above the session VWAP (anchored at 00:00 UTC; the previous candle, in the same session, closed at or below it), **and** RSI14 > 50.
- **Entry:** the open of the first 15-minute candle after the signal close.
- **Risk:** 1R = 2 × ATR14 of the signal candle.
- **Exit:** the stop starts at entry − 2 × ATR. After each 1-hour close it trails to the best close since entry − 3 × ATR14, never backwards. Stops are checked on 15-minute lows.
- One position at a time. After an exit, the next signal is the first 1-hour candle that closes after the exit.
- **Markets:** BTCUSDT and ETHUSDT on Binance spot (the study's data source), using public klines.

## Costs (per round trip, as a share of price)

- **Primary** (decides): **0.05%**. This is the study's primary cost, close to the measured Exness BTCUSDm spread (about 0.02%) plus slippage.
- **Also reported:**
  - 0.10% (the study's stress cost);
  - **0.20%** (Binance retail taker, 0.10% per side): at about 1R = 1.2% of price this costs about 0.17R per trade, roughly the whole backtest edge.

**Not modelled:** Exness crypto swap (holds are often overnight). The earlier Donchian work found swap could matter; it will be checked separately before any real-money question.

## Forward period

From the first hourly signal close at or after **2026-11-14 00:00 UTC**. Earlier candles are used only for indicator warm-up.

## Evaluation: rule V2 adapted to R units, decided now

- **Looks:** at 100, 300, 600 and 1,000 closed trades **per market**.
- **Family:** 2 markets × 4 looks, so the critical Newey–West t (5 lags) is z(1 − 0.05/8) = **2.50**.

| Outcome | Condition |
|---|---|
| **PASS** | NW t ≥ 2.50 and mean ≥ +0.05R at the primary cost |
| **STOP (futility)** | mean + 1.645·se < +0.05R |
| **UNDECIDED** | otherwise, until 1,000 trades |

**Expected pace.** The backtest had about 175 trades a year per market, so the first look comes after about 7 months.

**What a PASS means.** Evidence for the entry on new data at Exness-like costs. Real money would still need a separate check of swap and venue costs.

## Operation

`forward.py` runs daily. It downloads closed Binance candles and replays the frozen rules from the start of the forward period.
- **Ledger:** `ledger.csv`, rewritten from the replay; **previously recorded trades must reproduce exactly**, otherwise DATA REVISION → STOP and human review.
- **Report:** `REPORT.md`.
- **Open trade:** a trade still open at the end of the data is reported as open, and nothing after it is counted.
