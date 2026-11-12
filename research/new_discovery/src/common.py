"""Shared helpers for the discovery program: data loading, periods, costs, statistics."""
import math
import os

import numpy as np
import pandas as pd

SCR = os.environ.get("DISCOVERY_DATA", "/tmp/claude-0/-home-user-Octabot/673585c7-1020-5c5e-b0a9-ec953e6fb327/scratchpad")
LONG = {"XAUUSDm", "USOILm", "BTCUSDm"}
MARKETS = ["XAUUSDm", "USOILm", "UKOILm", "BTCUSDm", "ETHUSDm", "EURUSDm", "GBPUSDm", "USDJPYm", "US500m", "USTECm", "DE30m"]
START = pd.Timestamp("2023-01-01", tz="UTC")
PERIODS = {"TRAIN": (pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-07-01", tz="UTC")),
           "VALIDATION": (pd.Timestamp("2024-07-01", tz="UTC"), pd.Timestamp("2025-07-01", tz="UTC")),
           "TEST": (pd.Timestamp("2025-07-01", tz="UTC"), pd.Timestamp("2030-01-01", tz="UTC"))}
SLICE_2025 = pd.Timestamp("2025-01-01", tz="UTC")
STRESS_PER_DAY = 0.0002


def load(m):
    p = os.path.join(SCR, "long" if m in LONG else "multi/bars", f"{m}_15m.csv.gz")
    d = pd.read_csv(p)
    d["dt"] = pd.to_datetime(d.t, unit="s", utc=True)
    d = d[d.dt >= START - pd.Timedelta(days=120)].set_index("dt").sort_index()
    d["mo"] = (d.bo + d.ao) / 2
    d["mc"] = (d.bc + d.ac) / 2
    return d


def median_spread_frac(d):
    x = d[d.index >= START]
    return float(((x.ao - x.bo) / x.mo).median())


def period_of(ts):
    for k, (a, b) in PERIODS.items():
        if a <= ts < b:
            return k
    return None


def slip(spread_frac, kind):
    return (0.5 if kind == "primary" else 1.5) * spread_frac


def stats(r_bp, extra=None):
    r = np.asarray(r_bp, float)
    n = len(r)
    out = {"trades": n}
    if n < 2:
        return out
    m, sd = float(r.mean()), float(r.std(ddof=1))
    eq = np.cumsum(r)
    dd = float((np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq).max())
    gains, losses = r[r > 0].sum(), -r[r < 0].sum()
    out.update(mean_bp=m, ci95_bp=[m - 1.96 * sd / math.sqrt(n), m + 1.96 * sd / math.sqrt(n)], win_pct=float((r > 0).mean() * 100),
               profit_factor=float(gains / losses) if losses > 0 else None, max_drawdown_bp=dd, total_bp=float(r.sum()))
    if extra:
        out.update(extra)
    return out


def bh(pvals, q=0.05):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m, k = len(pvals), 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            k = rank
    return set(order[:k])
