"""Download Binance spot klines (closed candles only) from data-api.binance.vision.

Usage: python src/fetch_binance.py SYMBOL START_YYYY-MM-DD OUT_DIR
Writes OUT_DIR/<symbol>_<tf>.json as [[open_time_s, open, high, low, close, volume], ...] for 15m, 1h, 4h and 1d,
in the same layout as the frozen BTC research data, and prints counts and gaps. Nothing is filled or synthesised.
"""
import calendar
import json
import os
import ssl
import sys
import time
import urllib.request

STEP = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


def main():
    symbol, start, out = sys.argv[1], sys.argv[2], sys.argv[3]
    y, m, d = map(int, start.split("-"))
    start_ms = calendar.timegm((y, m, d, 0, 0, 0)) * 1000
    ca = "/root/.ccr/ca-bundle.crt"
    ctx = ssl.create_default_context(cafile=ca) if os.path.exists(ca) else ssl.create_default_context()
    os.makedirs(out, exist_ok=True)
    now_ms = int(time.time() * 1000)
    for tf in ("1d", "4h", "1h", "15m"):
        rows, t = [], start_ms
        while True:
            url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={tf}&limit=1000&startTime={t}"
            for attempt in range(6):
                try:
                    with urllib.request.urlopen(url, timeout=30, context=ctx) as r:
                        page = json.loads(r.read())
                    break
                except OSError as e:
                    err = e
                    time.sleep(2 ** attempt)
            else:
                raise SystemExit(f"download failed {tf} at {t}: {err}")
            closed = [r for r in page if r[6] < now_ms]
            rows += closed
            if len(page) < 1000 or len(closed) < len(page):
                break
            t = page[-1][0] + STEP[tf] * 1000
        data = [[r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in rows]
        with open(os.path.join(out, f"{symbol.lower()}_{tf}.json"), "w") as f:
            json.dump(data, f)
        gaps = sum(1 for a, b in zip(data, data[1:]) if b[0] - a[0] != STEP[tf])
        print(symbol, tf, len(data), time.strftime("%Y-%m-%d", time.gmtime(data[0][0])), "->",
              time.strftime("%Y-%m-%d %H:%M", time.gmtime(data[-1][0])), "gaps", gaps, flush=True)


if __name__ == "__main__":
    main()
