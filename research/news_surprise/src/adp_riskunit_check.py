"""ADP closing amendment, item 3: effect of correcting the 2016-2019 risk unit of addendum 5.

Addendum 5 defined R as 2 x the mid-price range of the hour before entry (entry = T-15 min). For 2016-2019 its tick
cache started at T-3700 s, so the 'hour' was really T-3700..T-900 = 46.7 minutes. This script re-extracts the ticks
with a cache from T-4600 s, recomputes the identical addendum-5 trades (same pairing, direction, entry, exit, seed)
with (a) the original truncated window and (b) the full 60-minute window, and reports both. The addendum-5 result
file is not touched. usage: same environment as adp_preposition.py, plus TICK_WORK3=<dir>"""
import io
import json
import math
import os
import subprocess
import sys
import time
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adp_preposition as AP  # noqa: E402

RP, R, TK = AP.RP, AP.R, AP.TK
NM, G, S = AP.NM, AP.G, AP.S


def windows_wide(sym, ts, work):
    by = {}
    for t in ts:
        g = time.gmtime(t)
        by.setdefault((g.tm_year, g.tm_mon), []).append(t)
    out = {}
    for (y, m), tl in sorted(by.items()):
        cache = os.path.join(work, f"{sym}_{y}_{m:02d}_win3.json")
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
                        if t - 4600 <= x <= t + 1000:
                            acc[t][0].append(x)
                            acc[t][1].append(float(p[3]))
                            acc[t][2].append(float(p[4]))
            os.remove(zp)
            json.dump({str(k): v for k, v in acc.items()}, open(cache, "w"))
        out.update({int(k): tuple(map(np.array, v)) for k, v in json.load(open(cache)).items()})
    return out


def legs_for(win, t, a, hot, start):
    tt, b, ak = win
    mid = (b + ak) / 2
    pre = mid[(tt >= start) & (tt < t - 900)]
    i, j = TK.first_at(tt, t - 900), TK.first_at(tt, t + 900)
    if len(pre) < 10 or i is None or j is None or pre.max() <= pre.min() or tt[i] - (t - 900) > 120:
        return None
    Rr = 2 * (pre.max() - pre.min())
    return (np.sign(a) * hot, (b[j] - ak[i]) / Rr, (b[i] - ak[j]) / Rr)


def stats(rows, seed_rng):
    sg = np.array([r[0] for r in rows])
    lo, sh = np.array([r[1] for r in rows]), np.array([r[2] for r in rows])
    rr = np.where(sg > 0, lo, sh)
    perm = np.array([np.where(seed_rng.permutation(sg) > 0, lo, sh).mean() for _ in range(2000)])
    sd = rr.std(ddof=1)
    half = 1.96 * sd / math.sqrt(len(rr))
    return {"trades": len(rr), "mean_r": float(rr.mean()), "total_r": float(rr.sum()),
            "ci95_mean_r": [float(rr.mean() - half), float(rr.mean() + half)],
            "p_signflip": float((np.sum(perm >= rr.mean()) + 1) / 2001)}


def main():
    adp, nfp = AP.adp_series(), AP.nfp_surprises()
    pairs = []
    for d, s in sorted(nfp.items()):
        if not (AP.datetime.date(2016, 1, 1) <= d <= AP.datetime.date(2026, 6, 30)) or s == 0:
            continue
        prior = [x for x in adp if 0 <= (d - x).days <= 7]
        if prior and adp[max(prior)] != 0:
            pairs.append((d, adp[max(prior)], s))
    early = {G.ny_to_utc(d, "08:30"): a for d, a, _ in pairs if d.year <= 2019}
    orig = json.load(open(os.path.join(R.ROOT, "reports", "adp_preposition.json")))["test2"]
    out = {}
    for mkt, hot in TK.MARKETS.items():
        w_old = RP.windows(mkt, sorted(early), os.environ["TICK_WORK"])          # the cache addendum 5 used
        w_new = windows_wide(mkt, sorted(early), os.environ["TICK_WORK3"])
        res = {}
        for label, win, start in (("original (window T-3700..T-900 s, 46.7 min)", w_old, lambda t: t - 900 - 3600),
                                  ("corrected (full 60 min, T-4500..T-900 s)", w_new, lambda t: t - 900 - 3600)):
            rows = [x for t, a in early.items() if t in win for x in [legs_for(win[t], t, a, hot, start(t))] if x]
            res[label] = stats(rows, np.random.default_rng(20261112))
        out[mkt] = {"2016-2019 only": res, "addendum5_reported_2016_2019_mean_r": orig[mkt]["by_period"]["2016-2019"],
                    "addendum5_reported_all_periods": {k: orig[mkt][k] for k in ("trades", "expectancy_r", "total_r", "p")}}
        print(mkt, json.dumps(out[mkt], default=float), flush=True)
    json.dump({"meta": {"generated_utc": S.fmt(time.time()), "note": "sensitivity only; addendum-5 results unchanged"},
               "results": out}, open(os.path.join(R.ROOT, "reports", "adp_riskunit_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
