"""Download Binance BTCUSDT klines (official public market-data mirror), paging by startTime. No synthetic data."""
import json, ssl, sys, time, urllib.request
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
D, start_ms = sys.argv[1], int(sys.argv[2])
STEP = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}
for tf in ("1d", "4h", "1h", "15m"):
    out, t = [], start_ms
    while True:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={tf}&limit=1000&startTime={t}"
        for a in range(5):
            try: rows = json.loads(urllib.request.urlopen(url, timeout=30, context=ctx).read()); break
            except Exception as e: time.sleep(2 ** a)
        else: raise SystemExit(f"download failed {tf} at {t}: {e}")
        rows = [r for r in rows if r[6] < time.time() * 1000]  # closed candles only
        if not rows: break
        out += rows; t = rows[-1][0] + STEP[tf] * 1000
        if len(rows) < 900: break
        time.sleep(0.15)
    gaps = sum(1 for a, b in zip(out, out[1:]) if b[0] - a[0] != STEP[tf] * 1000)
    json.dump([[r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in out], open(f"{D}/btc_{tf}.json", "w"))
    print(tf, len(out), "candles", time.strftime("%Y-%m-%d", time.gmtime(out[0][0] / 1000)), "->", time.strftime("%Y-%m-%d %H:%M", time.gmtime(out[-1][0] / 1000)), "gaps:", gaps, flush=True)
