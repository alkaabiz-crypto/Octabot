"""PROTOCOL.md addendum: entry delay after the release, with Exness tick data (textbook direction, no fitting).
usage: LONG_DATA=<dir> MULTI_BARS=<dir> TICK_WORK=<scratch dir> python src/ticks.py"""
import calendar
import io
import json
import multiprocessing
import os
import subprocess
import sys
import time
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402

NM, S = R.NM, R.S
URL = "https://ticks.ex2archive.com/ticks/{s}/{y}/{m:02d}/Exness_{s}_{y}_{m:02d}.zip"
MARKETS = {"XAUUSDm": -1, "EURUSDm": -1, "GBPUSDm": -1, "USDJPYm": 1}     # textbook: hot -> this direction
DELAYS = (1, 5, 15, 30, 60, 180, 900)
EXITS = (900, 3600)
PERMS = 2000


def stamp(s):
    s = s.strip('"')
    return calendar.timegm((int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16]), 0)) + float(s[17:23].rstrip("Z") or 0)


def windows(sym, events, work):
    """{event_t: (times, bids, asks)} for ticks within [t - 60, t + 3700]."""
    by_month = {}
    for t in events:
        g = time.gmtime(t)
        by_month.setdefault((g.tm_year, g.tm_mon), []).append(t)
    out = {}
    for (y, m), ts in sorted(by_month.items()):
        cache = os.path.join(work, f"{sym}_{y}_{m:02d}_win.json")
        if os.path.exists(cache):
            out.update({int(k): tuple(map(np.array, v)) for k, v in json.load(open(cache)).items()})
            continue
        zp = os.path.join(work, f"{sym}_{y}_{m:02d}.zip")
        r = subprocess.run(["curl", "-sS", "-m", "900", "-o", zp, "-w", "%{http_code}", URL.format(s=sym, y=y, m=m)],
                           capture_output=True, text=True)
        if r.stdout.strip() != "200":
            print(sym, y, m, "download failed", r.stdout, flush=True)
            continue
        days = {time.strftime("%Y-%m-%d", time.gmtime(t)) for t in ts}
        acc = {t: ([], [], []) for t in ts}
        with zipfile.ZipFile(zp) as z, z.open(z.namelist()[0]) as f:
            text = io.TextIOWrapper(f, encoding="utf-8")
            next(text)
            for line in text:
                p = line.rstrip().split(",")
                if len(p) != 5 or p[2][1:11] not in days:
                    continue
                x = stamp(p[2])
                for t in ts:
                    if t - 60 <= x <= t + 3700:
                        a = acc[t]
                        a[0].append(x)
                        a[1].append(float(p[3]))
                        a[2].append(float(p[4]))
        os.remove(zp)
        json.dump({str(k): v for k, v in acc.items()}, open(cache, "w"))
        out.update({k: tuple(map(np.array, v)) for k, v in acc.items()})
    return out


def first_at(tt, t):
    k = int(np.searchsorted(tt, t))
    return k if k < len(tt) else None


def run_market(sym):
    work = os.environ["TICK_WORK"]
    os.makedirs(work, exist_ok=True)
    base = os.environ["LONG_DATA"] if sym in NM.FROM_LONG else os.environ["MULTI_BARS"]
    m = NM.Mkt(os.path.join(base, f"{sym}_15m.csv.gz"))
    sc = {(k, t): s for (k, t), s in R.scores().items() if t >= NM.TEST0 and t <= int(m.tq[-1])}
    win = windows(sym, sorted({t for _, t in sc}), work)
    res = {}
    rng = np.random.default_rng(20261112)
    for kind in ("CPI", "NFP"):
        evs = [(t, s) for (k, t), s in sc.items() if k == kind and s != 0 and t in win and len(win[t][0]) > 10]
        for dl in DELAYS:
            for ex in EXITS:
                if dl >= ex:
                    continue
                lo, sh, sg = [], [], []
                for t, s in evs:
                    tt, b, a = win[t]
                    i, j = first_at(tt, t + dl), first_at(tt, t + ex)
                    atr = m.atr_before(t)
                    if i is None or j is None or atr is None or tt[i] - (t + dl) > 120:
                        continue
                    lo.append((b[j] - a[i]) / (2 * atr))
                    sh.append((b[i] - a[j]) / (2 * atr))
                    sg.append(np.sign(s) * MARKETS[sym])
                if len(sg) < 5:
                    continue
                lo, sh, sg = map(np.array, (lo, sh, sg))
                r = np.where(sg > 0, lo, sh)
                perm = np.array([np.where(rng.permutation(sg) > 0, lo, sh).mean() for _ in range(PERMS)])
                res[f"{kind}|{dl}s|{ex // 60}m"] = {"trades": len(r), "win_rate_pct": float((r > 0).mean() * 100),
                                                     "expectancy_r": float(r.mean()), "perm_mean_r": float(perm.mean()),
                                                     "p": float((np.sum(perm >= r.mean()) + 1) / (PERMS + 1))}
    return sym, res


def main():
    with multiprocessing.Pool(4) as p:
        out = dict(p.map(run_market, list(MARKETS)))
    json.dump({"meta": {"generated_utc": S.fmt(time.time()), "period": "2025-01 to latest", "direction": "textbook"},
               "results": out}, open(os.path.join(R.ROOT, "reports", f"ticks{R.SUFFIX}.json"), "w"), indent=1)
    for sym, r in out.items():
        for k, v in r.items():
            print(sym, k, v["trades"], f"win {v['win_rate_pct']:.0f}%", f"E {v['expectancy_r']:+.3f}R", f"p {v['p']:.3f}")


if __name__ == "__main__":
    main()
