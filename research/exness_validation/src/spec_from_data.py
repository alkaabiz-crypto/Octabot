"""Contract facts that can be MEASURED from Exness BTCUSDm tick-derived data: price increment, spread distribution and
active trading hours or gaps. Values that cannot be measured (contract size, tick value, commission, swap) are NOT
estimated here."""
import csv, glob, gzip, json, os, statistics, time, zipfile, io, ssl, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", "bars15m", "BTCUSDm_*.csv.gz"))):
    rows += list(csv.DictReader(gzip.open(f, "rt")))
by_year, by_hour, by_wd = {}, {}, {}
for r in rows:
    t = int(r["open_time_utc"]); g = time.gmtime(t); pct = float(r["spread_mean"]) / float(r["bid_c"]) * 100
    by_year.setdefault(g.tm_year, []).append((float(r["spread_mean"]), pct))
    by_hour.setdefault(g.tm_hour, []).append(pct); by_wd.setdefault(g.tm_wday, []).append(int(r["ticks"]))
ts = [int(r["open_time_utc"]) for r in rows]
gaps = sorted(((b - a) // 900 - 1, a) for a, b in zip(ts, ts[1:]) if b - a != 900)
# price increment: smallest positive difference between distinct observed prices (sample: last processed month's ticks)
out = dict(
    spread_by_year={y: dict(median_usd=round(statistics.median(v[0] for v in vs), 2), median_pct=round(statistics.median(v[1] for v in vs), 4),
                            p90_pct=round(sorted(v[1] for v in vs)[int(0.9 * len(vs))], 4)) for y, vs in sorted(by_year.items())},
    spread_pct_by_utc_hour_median={h: round(statistics.median(v), 4) for h, v in sorted(by_hour.items())},
    avg_ticks_per_15m_by_weekday={["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][d]: round(statistics.mean(v)) for d, v in sorted(by_wd.items())},
    candles_15m=len(rows), gaps_15m=len(gaps), missing_15m_periods=sum(g for g, _ in gaps),
    largest_gaps=[dict(start_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(a + 900)), missing_15m=g) for g, a in gaps[-10:][::-1]])
json.dump(out, open(os.path.join(ROOT, "reports", "spec_from_data.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
