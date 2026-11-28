"""PROTOCOL.md addendum 4: replication of the tick-delay finding on 2016-2019 (Exness ticks, Investing.com consensus).
usage: TICK_WORK=<dir> python src/replicate_2016.py"""
import csv
import datetime
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
import ticks as TK  # noqa: E402

R = TK.R
G = R.G
MARKETS = TK.MARKETS
DELAYS = (1, 5, 30, 180)
EXIT = 900
PERMS = 2000


def events():
    by = {}
    for r in csv.DictReader(l for l in open(os.path.join(R.ROOT, "data", "consensus_investing_2015_2024.csv")) if not l.startswith("#")):
        if not ("2016-01-01" <= r["date"] <= "2019-12-31"):
            continue
        a, f = R._num(r["actual"]), R._num(r["forecast"])
        if a is None or f is None:
            continue
        k = "CPI" if r["event"].startswith("Core CPI") else "NFP" if r["event"].startswith("Nonfarm") else "UNRATE"
        by.setdefault(r["date"], {})[k] = a - f
    out = []
    for d, v in by.items():
        t = G.ny_to_utc(datetime.date.fromisoformat(d), "08:30")
        if "CPI" in v and v["CPI"] != 0:
            out.append(("CPI", t, v["CPI"]))
        if "NFP" in v:
            s = v["NFP"] - 100 * v.get("UNRATE", 0.0)
            if s != 0:
                out.append(("NFP", t, s))
    return sorted(out, key=lambda x: x[1])


def windows(sym, ts, work):
    by_month = {}
    for t in ts:
        g = time.gmtime(t)
        by_month.setdefault((g.tm_year, g.tm_mon), []).append(t)
    out = {}
    for (y, m), tl in sorted(by_month.items()):
        cache = os.path.join(work, f"{sym}_{y}_{m:02d}_win2.json")
        if not os.path.exists(cache):
            zp = os.path.join(work, f"{sym}_{y}_{m:02d}.zip")
            r = subprocess.run(["curl", "-sS", "-m", "900", "-o", zp, "-w", "%{http_code}", TK.URL.format(s=sym, y=y, m=m)],
                               capture_output=True, text=True)
            if r.stdout.strip() != "200":
                print(sym, y, m, "download failed", r.stdout, flush=True)
                continue
            days = {time.strftime("%Y-%m-%d", time.gmtime(t)) for t in tl}
            acc = {t: ([], [], []) for t in tl}
            with zipfile.ZipFile(zp) as z, z.open(z.namelist()[0]) as f:
                text = io.TextIOWrapper(f, encoding="utf-8")
                next(text)
                for line in text:
                    p = line.rstrip().split(",")
                    if len(p) != 5 or p[2][1:11] not in days:
                        continue
                    x = TK.stamp(p[2])
                    for t in tl:
                        if t - 3700 <= x <= t + 1000:
                            acc[t][0].append(x)
                            acc[t][1].append(float(p[3]))
                            acc[t][2].append(float(p[4]))
            os.remove(zp)
            json.dump({str(k): v for k, v in acc.items()}, open(cache, "w"))
        out.update({int(k): tuple(map(np.array, v)) for k, v in json.load(open(cache)).items()})
    return out


def run_market(sym):
    work = os.environ["TICK_WORK"]
    ev = events()
    win = windows(sym, sorted({t for _, t, _ in ev}), work)
    rng = np.random.default_rng(20261112)
    res, share = {}, {}
    for kind in ("CPI", "NFP"):
        evs = [(t, s) for k, t, s in ev if k == kind and t in win and len(win[t][0]) > 20]
        sh_rows = []
        for dl in DELAYS:
            lo, shrt, sg = [], [], []
            for t, s in evs:
                tt, b, a = win[t]
                mid = (b + a) / 2
                pre = mid[(tt >= t - 3600) & (tt < t)]
                if len(pre) < 10:
                    continue
                rng_h = pre.max() - pre.min()
                i, j = TK.first_at(tt, t + dl), TK.first_at(tt, t + EXIT)
                if i is None or j is None or rng_h <= 0 or tt[i] - (t + dl) > 120:
                    continue
                lo.append((b[j] - a[i]) / (2 * rng_h))
                shrt.append((b[i] - a[j]) / (2 * rng_h))
                sg.append(np.sign(s) * MARKETS[sym])
                if dl == DELAYS[0]:
                    i0 = int(np.searchsorted(tt, t)) - 1
                    tot = mid[j] - mid[i0]
                    if i0 >= 0 and tot != 0:
                        sh_rows.append([(mid[TK.first_at(tt, t + x) or j] - mid[i0]) / tot for x in (1, 2, 5, 30)])
            if len(sg) < 5:
                continue
            lo, shrt, sg = map(np.array, (lo, shrt, sg))
            r = np.where(sg > 0, lo, shrt)
            perm = np.array([np.where(rng.permutation(sg) > 0, lo, shrt).mean() for _ in range(PERMS)])
            res[f"{kind}|{dl}s|15m"] = {"trades": len(r), "win_rate_pct": float((r > 0).mean() * 100),
                                        "expectancy_r": float(r.mean()), "p": float((np.sum(perm >= r.mean()) + 1) / (PERMS + 1))}
        if sh_rows:
            share[kind] = dict(zip(("1s", "2s", "5s", "30s"), map(float, np.median(np.array(sh_rows), axis=0))))
    return sym, {"results": res, "median_share_of_15m_move": share}


def main():
    with multiprocessing.Pool(4) as p:
        out = dict(p.map(run_market, list(MARKETS)))
    h1 = sum(1 for s in MARKETS if out[s]["results"].get("NFP|1s|15m", {}).get("p", 1) <= 0.05
             and out[s]["results"]["NFP|1s|15m"]["expectancy_r"] > 0)
    h2 = {s: [out[s]["results"].get(f"NFP|{d}s|15m", {}).get("expectancy_r") for d in (5, 30, 180)] for s in ("EURUSDm", "GBPUSDm", "USDJPYm")}
    h2_ok = all(np.mean([x for x in v if x is not None]) <= 0.1 for v in h2.values())
    verdict = {"H1_markets_passing": h1, "H1": h1 >= 3, "H2_avg_late_entries": {k: float(np.mean([x for x in v if x is not None])) for k, v in h2.items()}, "H2": bool(h2_ok)}
    json.dump({"meta": {"generated_utc": R.S.fmt(time.time()), "period": "2016-01 to 2019-12", "R": "2 x mid range of the hour before"},
               "verdict": verdict, "results": out}, open(os.path.join(R.ROOT, "reports", "replication_2016_2019.json"), "w"), indent=1)
    for s, o in out.items():
        print(s, o["median_share_of_15m_move"])
        for k, v in o["results"].items():
            print(" ", k, v["trades"], f"win {v['win_rate_pct']:.0f}%", f"E {v['expectancy_r']:+.3f}R", f"p {v['p']:.3f}")
    print(verdict)


if __name__ == "__main__":
    main()
