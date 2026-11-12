"""Append-only archive of Hyperliquid 1-minute candles (xyz:GOLD, xyz:CL) for the forward-evaluation random-timing benchmark.
Hyperliquid's candleSnapshot only serves the most recent ~5,000 one-minute candles, so the forward-period history must be kept
as it happens. Binance 1m history is re-fetchable at any time and is not archived (licence: no redistribution).

Run hourly: python3 -I archive_prices.py
Files: prices/<coin>_1m_<YYYY-MM>.csv.gz (t_ms,o,h,l,c,v; closed candles only; deterministic gzip). An already archived candle is
never overwritten: if the feed later reports a different value, the change is logged in prices/revisions.csv instead.
Gaps (minutes with no candle while the archive was not running long enough) are logged in prices/gaps.csv.
"""
import csv, gzip, io, json, os, ssl, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.join(HERE, "prices"); os.makedirs(P, exist_ok=True)
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
COINS = ("xyz:GOLD", "xyz:CL"); M = 60_000
ARCHIVE_START_MS = 1794355200000   # 2026-11-11 00:00 UTC (before the earliest Hyperliquid forward test start, 08:26 that day)
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def snapshot(coin, start_ms, end_ms):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1m", "startTime": int(start_ms), "endTime": int(end_ms)}}).encode()
    for k in range(5):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}),
                                                     timeout=60, context=CTX).read())
        except Exception:
            if k == 4: raise
            time.sleep(2 ** (k + 1))


def path(coin, ms): return os.path.join(P, f"{coin.replace(':', '_')}_1m_{time.strftime('%Y-%m', time.gmtime(ms / 1000))}.csv.gz")


def load(fp):
    if not os.path.exists(fp): return {}
    with gzip.open(fp, "rt") as f: return {int(r["t_ms"]): r for r in csv.DictReader(f)}


def save(fp, rows):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=["t_ms", "o", "h", "l", "c", "v"], lineterminator="\n"); w.writeheader()
    for t in sorted(rows): w.writerow(rows[t])
    with open(fp, "wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as g: g.write(buf.getvalue().encode())


def log(name, fields, row):
    fp = os.path.join(P, name); first = not os.path.exists(fp)
    with open(fp, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if first: w.writeheader()
        w.writerow(row)


def last_archived(coin):
    fs = sorted(f for f in os.listdir(P) if f.startswith(coin.replace(":", "_") + "_1m_"))
    return max(load(os.path.join(P, fs[-1]))) if fs else None


def main():
    now = int(time.time() * 1000) // M * M
    for coin in COINS:
        last = last_archived(coin); start = (last + M) if last else ARCHIVE_START_MS; got = {}; t = start
        while t < now:
            r = snapshot(coin, t, now - 1)
            r = [x for x in r if x["T"] < now]              # closed candles only
            if not r: break
            for x in r: got[int(x["t"])] = dict(t_ms=int(x["t"]), o=x["o"], h=x["h"], l=x["l"], c=x["c"], v=x["v"])
            nt = max(got) + M
            if nt <= t: break
            t = nt
        if not got: print(f"{coin}: no new closed candles"); continue
        first = min(got)
        if last is not None and first > last + M:
            log("gaps.csv", ["coin", "from_utc", "to_utc", "minutes", "logged_utc"], dict(coin=coin, from_utc=fmt(last + M), to_utc=fmt(first - M),
                minutes=(first - last) // M - 1, logged_utc=fmt(now)))
        if last is None and first > ARCHIVE_START_MS:
            log("gaps.csv", ["coin", "from_utc", "to_utc", "minutes", "logged_utc"], dict(coin=coin, from_utc=fmt(ARCHIVE_START_MS), to_utc=fmt(first - M),
                minutes=(first - ARCHIVE_START_MS) // M, logged_utc=fmt(now)))
        by = {}
        for ts, row in got.items(): by.setdefault(path(coin, ts), {})[ts] = row
        added = 0
        for fp, rows in by.items():
            old = load(fp)
            for ts, row in rows.items():
                if ts in old:
                    if any(abs(float(old[ts][k]) - float(row[k])) > 1e-9 for k in ("o", "h", "l", "c")):
                        log("revisions.csv", ["coin", "t_utc", "archived", "feed_now", "logged_utc"], dict(coin=coin, t_utc=fmt(ts),
                            archived=json.dumps({k: old[ts][k] for k in "ohlc"}), feed_now=json.dumps({k: row[k] for k in "ohlc"}), logged_utc=fmt(now)))
                else: old[ts] = row; added += 1
            save(fp, old)
        print(f"{coin}: {added} candle(s) archived, last {fmt(max(got))} UTC")


if __name__ == "__main__":
    main()
