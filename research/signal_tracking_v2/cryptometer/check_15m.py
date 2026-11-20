"""SIG-005 Amendment-1 check: E1 on Binance 15m candles over each unique TEST call's own 7 days.
usage: python3 -I check_15m.py <all_calls.json> <cache_dir>"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import fetch_prices as F  # noqa: E402
SPLIT = 1751328000000; M15 = 15 * 60 * 1000; STOP, TGT, N = 0.05, 0.10, 672


def one(c, cache):
    b = c["pair"].split("-")[0].upper(); ts = c["timestamp"]; f = os.path.join(cache, f"{b}_{ts}.json")
    if not os.path.exists(f):
        start = (ts + M15 - 1) // M15 * M15; r = F.get(f"https://data-api.binance.vision/api/v3/klines?symbol={b}USDT&interval=15m&startTime={start}&limit=1000")
        json.dump(r or [], open(f, "w"))
    a = json.load(open(f))
    if len(a) < N + 1 or a[0][0] - ts > 2 * 3600 * 1000: return None
    side = 1 if c["side"] == "BUY" else -1; o = [float(x[1]) for x in a]; h = [float(x[2]) for x in a]; l = [float(x[3]) for x in a]; cl = [float(x[4]) for x in a]
    e = o[0]; stop = e * (1 - side * STOP); tgt = e * (1 + side * TGT)
    for k in range(N):
        if k > 0 and (o[k] - stop) * side <= 0: return side * (o[k] / e - 1) - 0.002
        if ((l[k] if side > 0 else h[k]) - stop) * side <= 0: return -STOP - 0.002
        if ((h[k] if side > 0 else l[k]) - tgt) * side >= 0: return TGT - 0.002
    return side * (cl[N - 1] / e - 1) - 0.002


def main():
    calls = json.load(open(sys.argv[1])); cache = sys.argv[2]; os.makedirs(cache, exist_ok=True); seen = set(); todo = []
    for c in calls:
        k = (c["pair"].split("-")[0].upper(), c["timestamp"])
        if c["timestamp"] >= SPLIT and k not in seen: seen.add(k); todo.append(c)
    with ThreadPoolExecutor(4) as ex: res = [r for r in ex.map(lambda c: one(c, cache), todo) if r is not None]
    x = np.array(res); out = dict(n=len(x), E1_mean_net_pct=round(float(x.mean() * 100), 3), E1_win_pct=round(float((x > 0).mean() * 100), 1))
    json.dump(out, open(os.path.join(HERE, "check_15m.json"), "w"), indent=1); print(out)


if __name__ == "__main__":
    main()
