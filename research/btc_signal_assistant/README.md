# BTCUSDT indicator signal assistant

A stand-alone, rule-based assistant that reads Binance BTCUSDT closed candles and answers one question:
**BUY, SELL, WAIT or AVOID right now, and why?**

It is research tooling for paper use. It places no orders, holds no keys and has no connection to the
OctoBot runtime. It is also completely separate from the validated Donchian 20 forward paper test under
`research/btc_breakout/` (on its own branch): nothing in that directory is imported, read or written here.

## What it looks at

| Indicator | 4H (trend confirmation) | 1H (entry) |
|---|---|---|
| Donchian Channel 20 | position of the close inside the previous 20-bar range | **trigger**: a fresh close above the previous 20-bar high (BUY) or below the low (SELL) |
| EMA 50 / 200 | **trend gate**: close above EMA200 and EMA50 above EMA200 is bullish; mirror is bearish; otherwise mixed | structure confirmation |
| RSI 14 | above or below 50; 70 / 30 flagged | momentum confirmation; above 80 (below 20) downgrades a signal to WAIT |
| MACD 12 / 26 / 9 | line vs signal line, histogram direction | momentum confirmation |
| ADX 14 | trend strength (25 strong, 20 weak, below 20 none) and +DI / -DI | confirmation; below 20 counts as neutral |

Each indicator produces an individual reading: BULLISH, BEARISH or NEUTRAL, with a one-line explanation and
the numbers behind it. The report prints all ten readings (five per timeframe) and their agreement count.

## How the recommendation is formed

The rules are fixed and visible in `signal_assistant/analysis.py`. Nothing was fitted to BTC data; every
threshold is the conventional textbook value.

- **BUY** requires all three: the 4H trend gate is bullish, the 1H candle just closed above the previous
  20-bar high (a fresh breakout, not a continuation), and at least 3 of the 4 remaining 1H indicators are
  bullish with none bearish. 1H RSI above 80 turns the BUY into WAIT.
- **SELL** is the mirror image. It should be read as "exit or do not hold longs": short BTC breakouts
  failed every test in the separate breakout study, so SELL is not a validated short entry and the report
  says so.
- **AVOID** means conditions where acting is more likely to hurt than waiting: the data is stale, gapped
  or insufficient; a 1H breakout goes against the 4H trend; or there is no trend on either timeframe (mixed
  4H EMA structure and ADX below 20 on both).
- **WAIT** is everything else. The report lists exactly which BUY conditions are still missing, so the
  distance to a signal is always visible.

**Confidence** is HIGH when at least 9 of the 10 readings agree with the recommendation's direction,
MEDIUM at 7 or 8, LOW below that, and NONE for AVOID. It measures agreement between rules. It is **not** a
probability of profit, and the report says so every time it prints.

## What has evidence and what does not

Only one part of this rule set has been tested out of sample: the Donchian 20 long breakout on 1H with a
4H close above EMA200, in the separate breakout study (walk-forward 2020 to 2025 and a holdout to late
2026; moderate evidence, 33 to 35% win rate, expectancy around +0.2R with an ATR trailing stop, before
swaps). The EMA50-above-EMA200 requirement and the RSI, MACD and ADX confirmations are conventional filters
added on request. They have **no track record**. Filters can remove winning trades as easily as losing
ones, so this assistant may well underperform the plain validated rule.

`replay.py` runs the exact live decision function over history, causally, and reports how often each
recommendation occurred and what the close did afterwards over 4, 12, 24 and 48 hours, next to the
unconditional distribution. It simulates no entries, stops, sizing or costs, so it cannot show
profitability, and it never claims to. Consecutive signals overlap, so its t-statistics are optimistic and
are printed only as a rough scale.

Replay results are in the section at the end of this file. Read them as a description of the past, not a
forecast.

## Running it

Python 3.13 and the standard library only. No OctoBot packages, no third-party dependencies
(pandas and numpy are used by one optional test as an independent reference, and skipped if absent).

```bash
cd research/btc_signal_assistant

python run.py                 # analyse the latest closed candles (downloads from Binance)
python run.py --json          # same, machine readable
python run.py --quiet         # one line: time, recommendation, confidence, price
python run.py --save cache    # download and keep the candles
python run.py --offline cache # analyse saved candles (no network)
python run.py --watch         # loop: re-analyse ~45 s after every 1H close, notify on confirmed BUY
python replay.py --offline cache --csv signals.csv   # historical replay (descriptive)
```

Exit codes: 0 normal, 1 data problem (no recommendation), 10 when the recommendation is BUY.

Data comes from `data-api.binance.vision`, Binance's public market-data mirror, the same source as the
forward test. Only candles whose close time is in the past are used, so an unfinished candle can never
influence a reading. The 4H candle used for trend confirmation is always the last one that had closed when
the 1H candle closed. If the last 1H candle is more than two hours old, if any candle is missing in the
last 60 bars, or if there is too little history for EMA200, the answer is AVOID with the reason.

## Notifications for a confirmed BUY

Whenever the recommendation is BUY, the assistant:

1. prints a framed alert banner on the console;
2. writes `alerts/BUY_<time>.md` with the alert and the full report, and appends a row to `alerts/alerts.csv`;
3. posts the alert to a webhook if `SIGNAL_ASSISTANT_WEBHOOK_URL` is set (JSON body with `content` and
   `text`, so a Discord or Slack-style incoming webhook works);
4. sends a Telegram message if `SIGNAL_ASSISTANT_TELEGRAM_BOT_TOKEN` and `SIGNAL_ASSISTANT_TELEGRAM_CHAT_ID` are set.

Each signal candle is notified once. The last notified candle is stored in `state/last_notified.json`, so
the watch loop and repeated runs do not repeat the alert. A failing webhook or Telegram call is reported
in the output and never stops the analysis. The alert text repeats that rule agreement is not a probability.

`state/`, `alerts/` and `cache/` are git-ignored.

## Tests

```bash
cd research/btc_signal_assistant/tests
python -m unittest discover -s . -p "test_*.py"
```

65 tests cover:

- **indicators**: first defined index of every series, textbook properties (constant and monotonic series,
  hand-computed RSI and Donchian examples, MACD identity), agreement to 7 decimals with independent
  vectorised pandas implementations of EMA, RSI, MACD, ADX/DI and ATR, and a truncation test proving no
  value uses future candles;
- **decision rules**: every branch (BUY, BUY downgraded by RSI, SELL, SELL downgraded, counter-trend
  AVOID, no-trend AVOID, unusable-data AVOID, not-ready AVOID, WAIT with missing conditions), plus an
  invariant check that every recommendation produced on 13 months of real candles satisfies the documented
  rules, that the live path and replay path agree, and that truncating history does not change past answers;
- **data**: OHLC sanity rejection, stale / gapped / insufficient / misaligned data detection, closed-candle
  filtering and paging of the Binance download, typed errors on failure;
- **notifications**: console, files, webhook and Telegram channels with a fake HTTP layer, de-duplication,
  forced re-send, failure reporting, and absence of probability wording in the alert;
- **CLI**: text, JSON and quiet output on the offline fixture, exit codes, replay output and CSV.

The fixture (`tests/fixtures/btc_*.json.gz`) is 400 days of Binance BTCUSDT 1H and 4H candles ending
2026-11-09 19:00 UTC, so the whole suite runs offline in about two seconds.

## Before any live use

1. Do not trade this live. The combined rule set has no out-of-sample track record.
2. Run `python run.py --watch` (or an hourly cron calling `python run.py --quiet`) and paper-trade the
   BUY alerts for at least 40 signals or six months, recording entry, exit rule and result, exactly as the
   Donchian forward test does. The replay below can suggest how long that will take.
3. Compare the paper results with the plain validated Donchian rule over the same period. If the extra
   filters do not help, drop them.
4. Only then consider the broker's real costs (spread, commission, swaps) and re-evaluate.

## Historical replay (descriptive, no trades simulated)

See [`REPLAY.md`](REPLAY.md): full Binance history since December 2018 and the 13-month fixture period, with the
interpretation. Short version: BUY signals had a higher mean but not a higher median forward move than
random candles, SELL signals were followed by rising prices, and the last 13 months were negative. No
evidence of profitability exists for this rule set.
