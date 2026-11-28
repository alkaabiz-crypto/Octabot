"""Batch 2 DEVELOPMENT run (exploratory only; previously inspected target series). Implements PREREGISTRATION.md.
Raw data is cached in DATA_DIR (scratch, never committed); only hashes and derived per-test statistics are committed.
Outputs: results/development.json (stats, benchmarks, n_req), results/data_manifest_development.json (SHA-256 of raw files).

Usage: DATA_DIR=<scratch dir> python3 -I dev.py
"""
import json, os, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common as C  # noqa: E402

DATA = os.environ["DATA_DIR"]; os.makedirs(DATA, exist_ok=True)


def cached(name, fn):
    p = os.path.join(DATA, name + ".pkl")
    if os.path.exists(p): return pd.read_pickle(p)
    x = fn(); pd.to_pickle(x, p); return x


def load(coin, end_ms):
    tag = f"{coin}_{C.START_MS}_{end_ms}"
    m1 = cached(f"m1_{tag}", lambda: C.binance_klines(f"{coin}USDT", "1m", C.START_MS, end_ms))
    h1 = cached(f"h1_{tag}", lambda: C.binance_klines(f"{coin}USDT", "1h", C.START_MS, end_ms))
    fund = cached(f"fund_{tag}", lambda: C.hl_funding(coin, C.START_MS, end_ms))
    dvol = cached(f"dvol_{tag}", lambda: C.deribit_dvol(coin, C.START_MS, end_ms))
    qs = cached(f"quarterlies_{coin}", lambda: C.deribit_quarterlies(coin))
    futs = []
    for n, e, cr in qs:
        if cr >= end_ms: continue
        s = cached(f"fut_{n}_{end_ms}", lambda n=n, e=e, cr=cr: C.deribit_chart(n, max(C.START_MS, cr), min(e, end_ms)))
        futs.append((n, e, s))
    return m1, h1, fund, dvol, futs


def raw_signals(hid, h1, fund, dvol, futs):
    return {"H1": lambda: C.h1_signals(fund), "H2": lambda: C.h2_signals(futs, h1), "H3": lambda: C.h3_signals(h1), "H4": lambda: C.h4_signals(dvol, h1)}[hid]()


def quality(coin, m1, h1, fund, dvol, futs):
    gaps = lambda t, step: int((np.diff(t) > step).sum())
    return dict(m1_rows=int(len(m1)), m1_gaps=gaps(m1.t.values, C.M), h1_rows=int(len(h1)), h1_gaps=gaps(h1.t.values, C.H), funding_rows=int(len(fund)),
                funding_gaps_over_1h=gaps(fund.t.values, C.H + 60_000) if len(fund) else None, dvol_rows=int(len(dvol)), dvol_gaps=gaps(dvol.index.values, C.H) if len(dvol) else None,
                futures=[(n, int(len(s)), pd.Timestamp(e, unit="ms").strftime("%Y-%m-%d")) for n, e, s in futs],
                first_last=dict(m1=[str(pd.Timestamp(m1.t.min(), unit="ms")), str(pd.Timestamp(m1.t.max(), unit="ms"))],
                                funding=[str(pd.Timestamp(fund.t.min(), unit="ms")), str(pd.Timestamp(fund.t.max(), unit="ms"))] if len(fund) else None,
                                dvol=[str(pd.Timestamp(dvol.index.min(), unit="ms")), str(pd.Timestamp(dvol.index.max(), unit="ms"))] if len(dvol) else None))


def main():
    from statistics import NormalDist
    z1, z2 = NormalDist().inv_cdf(1 - 0.05 / 8), NormalDist().inv_cdf(0.80)
    out = dict(label="DEVELOPMENT 2025-01-01 -> T0 (2026-11-12 19:10:31 UTC). Previously inspected target series: EXPLORATORY ONLY, cannot PASS.",
               tests={}, quality={})
    for coin in C.COINS:
        m1, h1, fund, dvol, futs = load(coin, C.T0_MS); out["quality"][coin] = quality(coin, m1, h1, fund, dvol, futs)
        for hid in ("H1", "H2", "H3", "H4"):
            tid = f"{hid}_{coin}"; sig = raw_signals(hid, h1, fund, dvol, futs); tr = C.simulate(sig, C.HOLD[hid], m1, C.START_MS, C.T0_MS)
            s1, s2 = C.summarize(tr, coin, "primary"), C.summarize(tr, coin, "stress")
            b1 = C.bench_random(tr, hid, coin, m1, C.START_MS, C.T0_MS, C.test_seed(tid)); b2 = C.bench_placebo(sig, hid, coin, m1, C.START_MS, C.T0_MS, C.test_seed(tid))
            obs = s1.get("mean_bp", 0) / 1e4 if tr else None
            rt = 1.5 * C.SPREAD_BP[coin]; delta = max(10.0, 2 * rt)
            nreq = int(np.ceil(((z1 + z2) * s1["sd_bp"] / delta) ** 2)) if tr and s1.get("sd_bp") else None
            per_year = round(len(tr) / ((C.T0_MS - C.START_MS) / (365 * C.D)), 1)
            out["tests"][tid] = dict(raw_signals=len(sig), primary=s1, stress=s2,
                                     B1_random=dict(p=C.pval(obs, b1), median_bp=round(float(np.median(b1) * 1e4), 2), p95_bp=round(float(np.percentile(b1, 95) * 1e4), 2)) if b1 is not None else None,
                                     B2_placebo=dict(p=C.pval(obs, b2), median_bp=round(float(np.nanmedian(b2) * 1e4), 2), p95_bp=round(float(np.nanpercentile(b2, 95) * 1e4), 2)) if b2 is not None else None,
                                     power=dict(delta_bp=delta, n_req=nreq, dev_trades_per_year=per_year, years_to_n_req=round(nreq / per_year, 1) if nreq and per_year else None))
            print(tid, json.dumps(out["tests"][tid]), flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "development.json"), "w"), indent=1)
    man = {f: C.sha256(os.path.join(DATA, f)) for f in sorted(os.listdir(DATA)) if f.endswith(".pkl")}
    json.dump(dict(note="raw files kept in session scratch only (licences: Binance non-commercial/no hosting; Deribit personal use; Hyperliquid unknown)", files=man),
              open(os.path.join(HERE, "results", "data_manifest_development.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
