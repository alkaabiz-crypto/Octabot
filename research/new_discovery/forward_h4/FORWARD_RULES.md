# Forward PAPER observation: Coinbase premium (batch 003 H4), pre-registered 2026-11-13 before its first live hour

**Status.** H4 is a **WATCH** in batch 003: positive in all four historical periods, but not significant after correcting for 16 tests. This paper test collects **new data** to confirm or kill it.
- It is **not** a promotion and not a trading signal.
- Fake money; no orders; no exchange account.

## Rule (identical to `../batch_003/PREREG.md` H4)

**Premium.** At each hourly close, *prem* = ln(Coinbase BTC-USD close / Binance BTCUSDT close). Both are 1-hour candles of the same start time, from the public APIs.

***z*** = (*prem* − its mean over the previous 720 hours) / their standard deviation; the current hour is excluded.

**Trades.**
- If *z* ≥ +2: **long** BTC. If *z* ≤ −2: **short** BTC.
- **Entry:** the open of the first Binance BTCUSDT 1-minute candle at or after the hourly close.
- **Exit:** the open of the first 1-minute candle at or after entry + 24 hours.
- One position at a time. A signal is taken only if its hourly close is at or after the previous exit.

## What differs from the backtest (fixed now)

- **Execution prices:** Binance BTCUSDT spot 1-minute opens, instead of Exness BTCUSDm bid/ask.
- **Costs:** Binance spot taker fee **0.10% per side** (20 bp round trip) is the **primary** cost; 2× (40 bp) is reported alongside.
  - The backtest's Exness costs were lower: about 2–20 bp, depending on the year.
  - On the backtest's TEST mean, that leaves roughly +17 bp per trade at the primary cost, so the edge has much less room here.
- **Clock:** the forward period begins with the first hourly close at or after **2026-11-13 13:00 UTC**. Earlier hours are used only for the 720-hour z-score window.

## Evaluation (decided now)

This is rule V2 (`../promotion_rule_v2/PROMOTION_RULE_V2.md`), applied to net bp per trade at the **primary** cost. The family is this one test, so the critical value is z(1 − 0.05/4) = **2.24** across the 4 looks.

| Outcome | Condition |
|---|---|
| **Looks** | at 100, 300, 600 and 1,000 closed trades |
| **PASS** | Newey–West t ≥ 2.24 and mean ≥ +2 bp |
| **STOP (futility)** | mean + 1.645·se < +2 bp |
| **UNDECIDED** | no decision after 1,000 trades |

**Expected pace.** The backtest's TEST period had 135 trades in 16 months, so the first look should come about 12 months from now.

**What a PASS means.** It is evidence for the premium effect at Binance retail costs. It would still need a separate decision before any real-money use.

## Operation

- `forward.py` processes every closed hour since its cursor, so a daily run catches up without look-ahead. Each decision uses only candles that closed before it.
- **Files:**
  - `state.json`: cursor and open position.
  - `ledger.csv`: append-only.
  - `signals.csv`: every signal hour, with *prem* and *z* as computed at the time.
  - `REPORT.md`.
- **Data revisions.** On each run, the stored *prem* of past signal hours is re-checked against fresh data. Any change larger than 1e-9 is reported as **DATA REVISION**, and no further trades are processed until a human reviews it.
- A **STOPPED** message is raised if either API fails or returns a gap.
