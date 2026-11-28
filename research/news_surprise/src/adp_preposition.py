"""PROTOCOL.md addendum 5: does the ADP surprise predict the NFP surprise, and does positioning 15 minutes before
NFP in that direction pay? usage: SURPRISE=consensus LONG_DATA=.. MULTI_BARS=.. TICK_WORK=.. KAGGLE_US=<csv> HF_CAL=<csv>
python src/adp_preposition.py"""
import csv
import datetime
import json
import math
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replicate_2016 as RP  # noqa: E402

R, TK = RP.R, RP.TK
NM, G, S = R.NM, R.G, R.S
MARKETS = TK.MARKETS


def adp_series():
    out = {}
    for r in csv.DictReader(open(os.environ["KAGGLE_US"], encoding="utf-8", errors="replace")):
        if r["zone"] == "united states" and re.sub(r"\s+", " ", r["event"]).startswith("ADP Nonfarm Employment Change ("):
            a, f = R._num(r["actual"]), R._num(r["forecast"])
            if a is not None and f is not None:
                out[datetime.datetime.strptime(r["date"], "%d/%m/%Y").date()] = a - f
    cur = None
    for line in open(os.environ["HF_CAL"]):
        p = line.rstrip("\n").split(";")
        if re.match(r"^[A-Z][a-z]+day, ", p[0]):
            cur = datetime.datetime.strptime(p[0], "%A, %B %d, %Y").date()
        elif len(p) == 6 and cur and p[1] == "US" and p[2].startswith("ADP Nonfarm Employment Change ("):
            a, f = R._num(p[3]), R._num(p[4])
            if a is not None and f is not None:
                out.setdefault(cur, a - f)
    return out


def nfp_surprises():
    out = {}
    for fn in ("consensus_investing_2015_2024.csv", "consensus_investing.csv"):
        by = {}
        for r in csv.DictReader(l for l in open(os.path.join(R.ROOT, "data", fn)) if not l.startswith("#")):
            a, f = R._num(r["actual"]), R._num(r["forecast"])
            if a is None or f is None:
                continue
            k = "NFP" if r["event"].startswith("Nonfarm") else "UNRATE" if r["event"].startswith("Unemployment") else None
            if k:
                by.setdefault(r["date"], {})[k] = a - f
        for d, v in by.items():
            if "NFP" in v:
                out.setdefault(datetime.date.fromisoformat(d), v["NFP"] - 100 * v.get("UNRATE", 0.0))
    return out


def main():
    adp, nfp = adp_series(), nfp_surprises()
    pairs = []
    for d, s in sorted(nfp.items()):
        if not (datetime.date(2016, 1, 1) <= d <= datetime.date(2026, 6, 30)) or s == 0:
            continue
        prior = [x for x in adp if 0 <= (d - x).days <= 7]
        if not prior:
            continue
        a = adp[max(prior)]
        if a != 0:
            pairs.append((d, a, s))
    hits = sum(np.sign(a) == np.sign(s) for _, a, s in pairs)
    n = len(pairs)
    p_binom = sum(math.comb(n, k) for k in range(hits, n + 1)) / 2 ** n
    print(f"Test 1: ADP surprise sign = NFP surprise sign in {hits}/{n} releases ({100 * hits / n:.0f}%), one-sided binomial p {p_binom:.3f}")
    rng = np.random.default_rng(20261112)
    res = {"test1": {"releases": n, "same_sign": int(hits), "pct": 100 * hits / n, "p": p_binom}, "test2": {}}
    for mkt, hot in MARKETS.items():
        rows = []
        early = [(d, a) for d, a, _ in pairs if d.year <= 2019]
        if early:
            ts = {G.ny_to_utc(d, "08:30"): a for d, a in early}
            win = RP.windows(mkt, sorted(ts), os.environ["TICK_WORK"])
            for t, a in ts.items():
                if t not in win:
                    continue
                tt, b, ak = win[t]
                mid = (b + ak) / 2
                pre = mid[(tt >= t - 900 - 3600) & (tt < t - 900)]
                i, j = TK.first_at(tt, t - 900), TK.first_at(tt, t + 900)
                if len(pre) < 10 or i is None or j is None or pre.max() <= pre.min() or tt[i] - (t - 900) > 120:
                    continue
                Rr = 2 * (pre.max() - pre.min())
                rows.append((t, np.sign(a) * hot, (b[j] - ak[i]) / Rr, (b[i] - ak[j]) / Rr))
        base = os.environ["LONG_DATA"] if mkt in NM.FROM_LONG else os.environ["MULTI_BARS"]
        m = NM.Mkt(os.path.join(base, f"{mkt}_15m.csv.gz"))
        q = m.q
        for d, a, _ in pairs:
            if d.year <= 2019:
                continue
            t = G.ny_to_utc(d, "08:30")
            ji, jx = m.idx.get(t - 900), m.idx.get(t + 900)
            if ji is None or jx is None:
                continue
            k0 = int(np.searchsorted(m.tq, t - 900 - 3600))
            hi, lo = max(q["bh"][k0:ji]), min(q["bl"][k0:ji]) if ji > k0 else (None, None)
            if ji <= k0 or hi <= lo:
                continue
            Rr = 2 * (hi - lo)
            rows.append((t, np.sign(a) * hot, (q["bo"][jx] - q["ao"][ji]) / Rr, (q["bo"][ji] - q["ao"][jx]) / Rr))
        if len(rows) < 10:
            continue
        sg = np.array([r[1] for r in rows])
        lo_, sh_ = np.array([r[2] for r in rows]), np.array([r[3] for r in rows])
        rr = np.where(sg > 0, lo_, sh_)
        perm = np.array([np.where(rng.permutation(sg) > 0, lo_, sh_).mean() for _ in range(2000)])
        p = float((np.sum(perm >= rr.mean()) + 1) / 2001)
        res["test2"][mkt] = {"trades": len(rr), "win_rate_pct": float((rr > 0).mean() * 100), "expectancy_r": float(rr.mean()),
                             "total_r": float(rr.sum()), "p": p,
                             "by_period": {"2016-2019": float(np.mean([x for x, r in zip(rr, rows) if time.gmtime(r[0]).tm_year <= 2019] or [np.nan])),
                                           "2020-2026": float(np.mean([x for x, r in zip(rr, rows) if time.gmtime(r[0]).tm_year >= 2020] or [np.nan]))}}
        print(mkt, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res["test2"][mkt].items()}, flush=True)
    keys = list(res["test2"])
    rej = R.LR.benjamini_hochberg([res["test2"][k]["p"] for k in keys])
    res["confirmed"] = [keys[i] for i in sorted(rej) if res["test2"][keys[i]]["expectancy_r"] > 0]
    print("confirmed:", res["confirmed"])
    json.dump(res, open(os.path.join(R.ROOT, "reports", "adp_preposition.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
