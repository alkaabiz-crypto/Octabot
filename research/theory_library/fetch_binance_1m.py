"""Download Binance spot 1-minute klines from 2025-01-01 (user rule) for verification V1. Output: OUT_DIR/<SYM>_1m.npz

Usage: OUT_DIR=<dir> python3 -I fetch_binance_1m.py BTCUSDT ETHUSDT
"""
import json, os, ssl, sys, time, urllib.request
import numpy as np

OUT = os.environ["OUT_DIR"]; os.makedirs(OUT, exist_ok=True)
START = 1735689600000; END = 1762732800000 + 365 * 86400000  # 2025-01-01 .. far enough; stops at the last closed minute
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def get(url):
    for k in range(5):
        try: return json.loads(urllib.request.urlopen(url, timeout=30, context=CTX).read())
        except Exception:
            if k == 4: raise
            time.sleep(2 ** (k + 1))


for sym in sys.argv[1:]:
    rows, t = [], START; now = int(time.time() * 1000) // 60000 * 60000
    while t < min(END, now):
        r = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1m&startTime={t}&limit=1000")
        if not r: break
        rows += [(x[0] // 60000, float(x[1]), float(x[2]), float(x[3]), float(x[4])) for x in r if x[6] < now]; t = r[-1][0] + 60000
    a = np.array(rows); assert a[0, 0] * 60000 >= START
    np.savez_compressed(os.path.join(OUT, f"{sym}_1m.npz"), m=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4])
    print(sym, len(a), "minutes", flush=True)
