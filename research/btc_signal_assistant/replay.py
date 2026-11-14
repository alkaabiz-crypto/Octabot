"""Historical replay of the assistant's rules - DESCRIPTIVE evidence, not a backtest and not a forecast.

For every closed 1H candle in the data the same ``assess`` function used live is run (causally: only candles
up to that close, and only the last 4H candle closed by then). The script then reports, for each
recommendation class, how often it occurred and what BTC did afterwards over fixed horizons
(close-to-close, no entry slippage, no stops, no costs). The unconditional distribution of the same
horizon returns is printed next to it so the reader can see whether the signal distinguished anything.

What this is NOT: it does not simulate trades, exits, position sizing or costs, so it cannot show
profitability. Overlapping horizons make consecutive samples dependent, so the t-statistics printed are
optimistic and are shown only as a rough scale. With fewer than MIN_SAMPLES signals no comparison is shown.

  python replay.py --offline cache            use cached candles
  python replay.py --days 700                 download 700 days and replay
  python replay.py --offline cache --csv out.csv   also write every BUY/SELL signal to a CSV
"""
import argparse
import csv
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from signal_assistant import analysis, constants, data, enums

HORIZONS_H = (4, 12, 24, 48)
MIN_SAMPLES = 30


def forward_returns(closes, i, horizons):
    out = {}
    for h in horizons:
        out[h] = (closes[i + h] / closes[i] - 1) * 100 if i + h < len(closes) else None
    return out


def describe(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    m = statistics.mean(xs)
    sd = statistics.stdev(xs) if len(xs) > 1 else 0.0
    return {"n": len(xs), "mean": m, "median": statistics.median(xs), "positive_pct": sum(x > 0 for x in xs) / len(xs) * 100,
                "t_vs_zero": (m / (sd / math.sqrt(len(xs))) if sd else None)}


def replay(c1h, c4h, start_index=None):
    quality = data.DataQualityReport(quality=enums.DataQuality.OK.value, issues=[], last_closed_1h_utc="", last_closed_4h_utc="",
                                     age_seconds_1h=0, bars_1h=len(c1h), bars_4h=len(c4h))
    s1h, s4h = analysis.compute_series(c1h), analysis.compute_series(c4h)
    first = constants.MIN_BARS_1H if start_index is None else start_index
    results = []
    for i in range(first, len(c1h)):
        a = analysis.assess(s1h, s4h, i, quality)
        results.append((i, a))
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--offline", metavar="DIR")
    p.add_argument("--days", type=int, default=constants.DEFAULT_HISTORY_DAYS)
    p.add_argument("--csv", metavar="PATH", help="write BUY and SELL signals to this CSV")
    args = p.parse_args(argv)
    if args.offline:
        c1h = data.load_candles_file("1h", os.path.join(args.offline, "btc_1h.json"))
        c4h = data.load_candles_file("4h", os.path.join(args.offline, "btc_4h.json"))
    else:
        c1h, c4h = data.fetch_market(days=args.days)
    results = replay(c1h, c4h)
    closes = c1h.c
    by_rec = {r: [] for r in enums.Recommendation}
    for i, a in results:
        by_rec[a.recommendation].append((i, a))
    total = len(results)
    print(f"Replay of {total} closed 1H candles, {data.fmt_utc(c1h.close_time(results[0][0]))} to "
          f"{data.fmt_utc(c1h.close_time(results[-1][0]))} UTC. Descriptive only: no trades, stops or costs simulated.\n")
    print("Recommendation frequency")
    for r, items in by_rec.items():
        print(f"  {r.value:<6} {len(items):>6}  ({len(items) / total * 100:5.1f}% of candles)")
    print()
    all_fwd = {h: [forward_returns(closes, i, HORIZONS_H)[h] for i, _ in results] for h in HORIZONS_H}
    header = f"{'horizon':>8} {'n':>6} {'mean%':>8} {'median%':>8} {'pos%':>6} {'t':>6}"
    for r in (enums.Recommendation.BUY, enums.Recommendation.SELL):
        items = by_rec[r]
        print(f"{r.value} signals: {len(items)}" + (f" (fewer than {MIN_SAMPLES}: too few to compare, nothing can be concluded)" if len(items) < MIN_SAMPLES else ""))
        if len(items) < MIN_SAMPLES:
            print()
            continue
        print("  after a", r.value, "signal                    |  all candles (unconditional)")
        print("  " + header + "  |  " + header)
        for h in HORIZONS_H:
            d = describe([forward_returns(closes, i, HORIZONS_H)[h] for i, _ in items])
            u = describe(all_fwd[h])
            def fmt(x):
                return f"{x['n']:>6} {x['mean']:>8.3f} {x['median']:>8.3f} {x['positive_pct']:>6.1f} " + (f"{x['t_vs_zero']:>6.2f}" if x['t_vs_zero'] is not None else "   n/a")
            print(f"  {h:>6}h " + fmt(d) + "  |  " + f"{h:>6}h " + fmt(u))
        print("  Overlapping horizons make these samples dependent; t is optimistic. Mean forward return is not expectancy per trade.")
        print()
    buys = by_rec[enums.Recommendation.BUY]
    if buys:
        conf = {}
        for _, a in buys:
            conf[a.confidence.value] = conf.get(a.confidence.value, 0) + 1
        print("BUY signals by confidence label:", ", ".join(f"{k} {v}" for k, v in sorted(conf.items())))
        print()
    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["signal_close_utc", "recommendation", "confidence", "close", "bullish", "bearish", "neutral"] + [f"fwd_{h}h_pct" for h in HORIZONS_H])
            for r in (enums.Recommendation.BUY, enums.Recommendation.SELL):
                for i, a in by_rec[r]:
                    fw = forward_returns(closes, i, HORIZONS_H)
                    w.writerow([a.as_of_utc, r.value, a.confidence.value, a.price, a.agreement["bullish"], a.agreement["bearish"], a.agreement["neutral"]]
                               + [None if fw[h] is None else round(fw[h], 4) for h in HORIZONS_H])
        print("signals written to", args.csv)
    print("Verdict on profitability: NONE. This replay cannot establish an edge. Use the forward paper test procedure for that.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
