"""Empirical look-ahead scan of EVERY frozen theory function (theories.py, theories_f.py, theories_g.py, unchanged).
Each theory runs on a synthetic market twice: the original path, and the same path with everything after a cut replaced by an
unrelated path. A causal strategy cannot change any entry (or exit) that happened before the candle containing the cut.
Detects cross-candle look-ahead (e.g. pending-order selection); it cannot detect same-candle ordering assumptions.
usage: python3 -I causality_scan.py <extract_dir> <out_json>
"""
import json, os, sys
import numpy as np, pandas as pd

EXT, OUT = sys.argv[1:3]
os.environ["BARS_DIR"] = "/nonexistent"
sys.path.insert(0, os.path.join(EXT, "research", "theory_library"))
import engine as E, theories as T, theories_f as TF, theories_g as TG  # noqa: E401,E402

START = 1735948800 // 60          # 2025-01-04 00:00 UTC (minutes); synthetic data runs ~120 days, both sides of nothing special
DAYS = 120


def path(seed, minutes):
    r = np.random.default_rng(seed); n = minutes
    ret = r.normal(0, 4e-4, n) + np.repeat(r.normal(0, 3e-5, n // 720 + 1), 720)[:n]
    c = 100 * np.exp(np.cumsum(ret)); o = np.r_[100.0, c[:-1]]; w = np.abs(r.normal(0, 3e-4, (2, n)))
    return o, np.maximum(o, c) * np.exp(w[0]), np.minimum(o, c) * np.exp(-w[1]), c


def frame(mkt, seed, cut_min=None, seed2=None):
    hourly = mkt in E.CRYPTO; n = DAYS * 1440; m = START + np.arange(n)
    o, h, l, c = path(seed, n)
    if cut_min is not None:
        o2, h2, l2, c2 = path(seed2, n); q = int(cut_min - START); s = o[q] / o2[q]
        o, h, l, c = (np.r_[a[:q], b[q:] * s] for a, b in ((o, o2), (h, h2), (l, l2), (c, c2)))
    if hourly:                                   # crypto source data is 1h in the library
        k = (m - START) // 60; st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(m)]
        return pd.DataFrame(dict(m=m[st], o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1], hs=o[st] * E.CRYPTO_FEE))
    return pd.DataFrame(dict(m=m, o=o, h=h, l=l, c=c, hs=np.full(n, 0.01)))


def run_all(mkts, data):
    E.base = lambda mkt: data[mkt]; E.candles.cache_clear(); out = {}
    for tid, fam, tfs, ms, fn in T.REGISTRY + TF.REGISTRY_F + TG.REGISTRY_G:
        for mkt in mkts:
            if mkt not in ms: continue
            for tf in tfs:
                if E.candles(mkt, tf) is None: continue
                res = fn(mkt, tf)
                if res is None: continue
                c, bk = res; out[f"{tid}|{mkt}|{tf}"] = (c.m.values.copy(), list(bk.rows))
    return out


def main():
    mkts = ("XAUUSDm", "US500m", "BTCUSDT"); report = {}
    for seed in (11, 12, 13):
        base = {k: frame(k, seed) for k in mkts}; A = run_all(mkts, base)
        for frac in (0.35, 0.65):
            cut = START + int(DAYS * 1440 * frac) + 7 * 60 + 23          # a mid-candle minute for every timeframe
            alt = {k: frame(k, seed, cut, seed + 500) for k in mkts}; B = run_all(mkts, alt)
            for key in A:
                cm, ra = A[key]; _, rb = B[key]
                # first candle that contains or follows the cut: everything strictly before it must be identical
                kc = int(np.searchsorted(cm, cut, side="right")) - 1
                pre = lambda rows: sorted([(i, s, round(pe, 9)) for i, j, s, pe, px in rows if i < kc] + [(j, round(px, 9), "x") for i, j, s, pe, px in rows if j < kc])
                d = pre(ra) != pre(rb)
                r = report.setdefault(key, dict(cuts=0, changed=0, trades=0)); r["cuts"] += 1; r["changed"] += int(d); r["trades"] += len(ra)
    flagged = {k: v for k, v in report.items() if v["changed"]}
    by_theory = {}
    for k, v in report.items():
        t = k.split("|")[0]; b = by_theory.setdefault(t, dict(combos=0, cuts=0, changed=0)); b["combos"] += 1; b["cuts"] += v["cuts"]; b["changed"] += v["changed"]
    json.dump(dict(n_keys=len(report), flagged=flagged, by_theory=by_theory, all=report), open(OUT, "w"), indent=1)
    print("theory combos scanned:", len(report), "| theories:", len(by_theory))
    for t, b in sorted(by_theory.items(), key=lambda x: -x[1]["changed"]):
        if b["changed"]: print("LOOK-AHEAD", t, b)
    print("clean theories:", sorted(t for t, b in by_theory.items() if not b["changed"]))


if __name__ == "__main__":
    main()
