"""Part 1-2 of PROTOCOL.md: every exit x news combination, fit 2020-07..2024-12, test 2025-01..now.
usage: GOLD_DATA=<dir with XAUUSDm_15m.csv.gz> python src/optimize.py [workers]"""
import itertools
import json
import multiprocessing
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as G  # noqa: E402

S = G.S
DATA = os.environ.get("GOLD_DATA", "")
FIT = (S.ts(2020, 7), S.ts(2025, 1))
STOPS = (0, 1.5, 2, 3)
TRAILS = (0, 2, 3, 4)
BE = (0, 1)
TIME_H = (0, 48, 120)
LOSE_H = (0, 6, 12)
GRID = list(itertools.product(STOPS, TRAILS, BE, TIME_H, LOSE_H, G.NEWS_RULES))
BASE = (0, 0, 0, 0, 0, "NONE")
_R = None


def key(p):
    return "stop={}|trail={}|be={}|time={}|lose={}|news={}".format(*p)


def summarise(R, p, w0, w1, runs=200):
    L = R.legs(p, w0, w1)
    rp, rs = R.r(L, "primary"), R.r(L, "stress")
    n = len(rp)
    out = {"trades": n}
    if n < 5:
        return out
    mu, sd = R.bench(p, L, w0, w1, runs=runs)
    years = {}
    for t, r in zip(L["entry_t"], rp):
        y = time.gmtime(int(t)).tm_year
        years.setdefault(y, []).append(r)
    out.update({"win_rate_pct": float((rp > 0).mean() * 100), "expectancy_r": float(rp.mean()),
                "expectancy_stress_r": float(rs.mean()), "total_r": float(rp.sum()), "total_stress_r": float(rs.sum()),
                "max_drawdown_r": G.max_drawdown(rp), "avg_hold_hours": float(((L["exit_t"] - L["entry_t"]) / 3600).mean()),
                "random_mean_r": mu, "z": (float(rp.mean()) - mu) / sd if sd > 0 else 0.0,
                "years": {str(y): [len(v), float(np.mean(v)), float(np.sum(v))] for y, v in sorted(years.items())}})
    return out


def _init(path):
    global _R
    g = G.Gold(path)
    ev = G.all_events()
    _R = G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])


def _work(p):
    end = int(_R.g.th[-1]) + 3600
    return key(p), {"fit": summarise(_R, p, *FIT), "test": summarise(_R, p, FIT[1], end)}


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    path = os.path.join(DATA, "XAUUSDm_15m.csv.gz")
    t0 = time.time()
    res = {}
    with multiprocessing.Pool(workers, initializer=_init, initargs=(path,)) as pool:
        for i, (k, r) in enumerate(pool.imap_unordered(_work, GRID, chunksize=8)):
            res[k] = r
            if i % 100 == 0:
                print(f"{i}/{len(GRID)} {time.time() - t0:.0f}s", flush=True)
    os.makedirs(os.path.join(G.ROOT, "reports"), exist_ok=True)
    with open(os.path.join(G.ROOT, "reports", "grid.json"), "w") as f:
        json.dump({"meta": {"generated_utc": S.fmt(time.time()), "combinations": len(GRID), "runs": 200,
                            "fit": [S.fmt(FIT[0]), S.fmt(FIT[1])]}, "results": res}, f)
    print("done", time.time() - t0)


if __name__ == "__main__":
    main()
