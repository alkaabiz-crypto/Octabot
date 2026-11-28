"""Audit 4: is the ~1-2 s delay before Exness quotes move after a release a real quote lag, or an offset in the archive
timestamps? Compares Exness BTCUSDm ticks with Binance BTCUSDT trades (millisecond exchange timestamps) around CPI and
NFP releases: the time at which each feed first moves 0.1% away from its pre-release price, and the best-fitting lag."""
import io
import json
import os
import subprocess
import sys
import time
import zipfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "news_surprise", "src"))
import ticks as TK  # noqa: E402

G = TK.R.G
WORK = sys.argv[1]
RELEASES = [("CPI", "2025-06-11"), ("CPI", "2025-07-15"), ("NFP", "2025-07-03"), ("NFP", "2025-09-05"), ("CPI", "2025-09-11")]


def binance(t):
    out = []
    s = (t - 20) * 1000
    while s < (t + 20) * 1000:
        r = json.loads(subprocess.run(["curl", "-sSf", "-m", "30", f"https://data-api.binance.vision/api/v3/aggTrades?symbol=BTCUSDT&startTime={s}&endTime={(t + 20) * 1000}&limit=1000"],
                                      capture_output=True, text=True, check=True).stdout)
        if not r:
            break
        out += [(x["T"] / 1000, float(x["p"])) for x in r]
        s = r[-1]["T"] + 1
        if len(r) < 1000:
            break
    return np.array(out)


def exness(ts):
    by = {}
    for t in ts:
        g = time.gmtime(t)
        by.setdefault((g.tm_year, g.tm_mon), []).append(t)
    out = {}
    for (y, m), tl in by.items():
        zp = os.path.join(WORK, f"BTC_{y}_{m:02d}.zip")
        if not os.path.exists(zp):
            subprocess.run(["curl", "-sS", "-m", "900", "-o", zp, TK.URL.format(s="BTCUSDm", y=y, m=m)], check=True)
        days = {time.strftime("%Y-%m-%d", time.gmtime(t)) for t in tl}
        acc = {t: [] for t in tl}
        with zipfile.ZipFile(zp) as z, z.open(z.namelist()[0]) as f:
            text = io.TextIOWrapper(f, encoding="utf-8")
            next(text)
            for line in text:
                p = line.rstrip().split(",")
                if len(p) != 5 or p[2][1:11] not in days:
                    continue
                x = TK.stamp(p[2])
                for t in tl:
                    if t - 20 <= x <= t + 20:
                        acc[t].append((x, (float(p[3]) + float(p[4])) / 2))
        os.remove(zp)
        out.update({t: np.array(v) for t, v in acc.items()})
    return out


def first_move(arr, t, thr=0.001):
    pre = arr[arr[:, 0] < t]
    if not len(pre):
        return None
    p0 = pre[-1, 1]
    post = arr[(arr[:, 0] >= t) & (np.abs(arr[:, 1] / p0 - 1) >= thr)]
    return float(post[0, 0] - t) if len(post) else None


def best_lag(b, e, t):
    grid = np.arange(t - 5, t + 15, 0.05)
    def at(a, g):
        k = np.searchsorted(a[:, 0], g, side="right") - 1
        return a[np.maximum(k, 0), 1]
    bb = np.diff(np.log(at(b, grid)))
    best = None
    for lag in np.arange(-1, 4.01, 0.05):
        ee = np.diff(np.log(at(e, grid + lag)))
        c = np.corrcoef(bb, ee)[0, 1]
        if best is None or c > best[1]:
            best = (float(lag), float(c))
    return best


def main():
    os.makedirs(WORK, exist_ok=True)
    ts = [(k, G.ny_to_utc(G.datetime.date.fromisoformat(d), "08:30")) for k, d in RELEASES]
    ex = exness([t for _, t in ts])
    res = []
    for k, t in ts:
        b, e = binance(t), ex[t]
        row = {"release": k, "utc": G.S.fmt(t), "binance_first_0.1pct_move_s": first_move(b, t), "exness_first_0.1pct_move_s": first_move(e, t),
               "best_lag_exness_behind_binance_s": None, "corr": None}
        if len(b) > 20 and len(e) > 20:
            row["best_lag_exness_behind_binance_s"], row["corr"] = best_lag(b, e, t)
        res.append(row)
        print(row, flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "feed_lag.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
