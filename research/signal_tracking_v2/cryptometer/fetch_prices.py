"""SIG-005: fetch Binance spot 1h klines (public data-api) for every coin in the CryptoMeter call list, over
[first call - 61 days, last call + 68 days]. Cached per coin in <out_dir>; raw data stays in scratch.
usage: python3 -I fetch_prices.py <all_calls.json> <out_dir>"""
import json, os, ssl, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
H = 3600 * 1000


def get(url):
    for k in range(5):
        try: return json.loads(urllib.request.urlopen(url, timeout=30, context=CTX).read())
        except urllib.error.HTTPError as e:
            if e.code == 400: return None                       # unknown symbol
            time.sleep(2 ** k)
        except Exception: time.sleep(2 ** k)
    return None


def fetch(base, lo, hi, out):
    f = os.path.join(out, f"{base}.json")
    if os.path.exists(f): return base, "cached"
    rows, t = [], lo
    while t < hi:
        r = get(f"https://data-api.binance.vision/api/v3/klines?symbol={base}USDT&interval=1h&startTime={t}&endTime={hi}&limit=1000")
        if r is None: break
        if not r: break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in r]; t = r[-1][0] + H
        if len(r) < 1000: break
    json.dump(rows, open(f, "w")); return base, len(rows)


def main():
    calls = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True); span = {}
    for c in calls:
        b = c["pair"].split("-")[0].upper(); t = c["timestamp"]; lo, hi = span.get(b, (t, t)); span[b] = (min(lo, t), max(hi, t))
    jobs = [(b, lo - 61 * 24 * H, min(hi + 68 * 24 * H, int(time.time() * 1000))) for b, (lo, hi) in span.items()]
    with ThreadPoolExecutor(4) as ex:
        for i, r in enumerate(ex.map(lambda a: fetch(*a, out), jobs)):
            if i % 50 == 0: print(i, len(jobs), r, flush=True)
    print("done", len(jobs))


if __name__ == "__main__":
    main()
