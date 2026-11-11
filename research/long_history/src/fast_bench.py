"""Compiled (numba) versions of the two random-entry benchmarks used in every round. Same algorithms as
study.random_benchmark (sequential sampler, quarter-matched trade counts, 6 calibration passes of 60 runs) and
tradingview_originals ports.duration_benchmark (same quarter, direction and holding time); only faster."""
import collections

import numba
import numpy as np
import oil
import study as S


@numba.njit(cache=True)
def _seq(et, xt, qi, p, seed, runs):
    np.random.seed(seed)
    nq = p.shape[0]
    counts = np.zeros((runs, nq))
    sums = np.zeros(runs)
    ns = np.zeros(runs)
    for r in range(runs):
        busy = -1
        for k in range(et.shape[0]):
            if et[k] < busy:
                continue
            if np.random.random() < p[qi[k]]:
                counts[r, qi[k]] += 1
                ns[r] += 1
                busy = xt[k]
                sums[r] += 0.0     # filled by caller via mask-free second pass is costly; see _seq_r
    return counts, ns


@numba.njit(cache=True)
def _seq_r(et, xt, qi, rv, p, seed, runs):
    np.random.seed(seed)
    means = np.full(runs, np.nan)
    for r in range(runs):
        busy, s, n = -1, 0.0, 0
        for k in range(et.shape[0]):
            if et[k] < busy:
                continue
            if np.random.random() < p[qi[k]]:
                s += rv[k]
                n += 1
                busy = xt[k]
        if n > 0:
            means[r] = s / n
    return means


def standard(asset, trades, d, exit_rule, w0, w1, runs=200, seed=20261111, cost="primary"):
    outcomes = [tr for tr in asset.table(d, exit_rule) if tr is not None and w0 <= tr.entry_time < w1]
    quarters = sorted({S.quarter(t.entry_time) for t in outcomes})
    qmap = {q: i for i, q in enumerate(quarters)}
    et = np.array([t.entry_time for t in outcomes], np.int64)
    xt = np.array([t.exit_time for t in outcomes], np.int64)
    qi = np.array([qmap[S.quarter(t.entry_time)] for t in outcomes], np.int64)
    rv = np.array([t.r(cost) for t in outcomes])
    target = collections.Counter(S.quarter(t.entry_time) for t in trades)
    per_q = collections.Counter(S.quarter(t.entry_time) for t in outcomes)
    p = np.array([min(1.0, target.get(q, 0) / per_q[q] * 4) for q in quarters])
    want = np.array([target.get(q, 0) for q in quarters], float)
    for it in range(6):
        counts, _ = _seq(et, xt, qi, p, seed + it, 60)
        got = counts.mean(axis=0)
        p = np.where(want == 0, 0.0, np.minimum(1.0, p * np.where(got > 0, want / np.maximum(got, 1e-12), 4.0)))
    means = _seq_r(et, xt, qi, rv, p, seed + 99, runs)
    means = means[~np.isnan(means)]
    win = float((rv > 0).mean() * 100)
    return float(means.mean()), float(means.std()), win


def held(asset, trades, w0, w1, runs=200, seed=20261111, cost="primary"):
    """Random entry bars in the same quarter, same direction and holding time; up to 20 redraws if no quote."""
    E, q = asset.e, asset.q
    n = len(E.t)
    tq = np.array(q["t"], np.int64)
    ao, bo = np.array(q["ao"]), np.array(q["bo"])
    atr = np.array([np.nan if x is None else x for x in asset.atr])
    tclose = np.array(E.t, np.int64) + 3600
    jent = np.searchsorted(tq, tclose)
    jent_ok = (jent < len(tq)) & (tq[np.minimum(jent, len(tq) - 1)] == tclose) & (atr > 0)
    pools = {}
    for i in range(n):
        if w0 <= tclose[i] < w1:
            pools.setdefault(S.quarter(int(tclose[i])), []).append(i)
    pools = {k: np.array(v) for k, v in pools.items()}
    rng = np.random.default_rng(seed)
    slip = oil.SLIP[cost]
    vals = np.full((runs, len(trades)), np.nan)
    for c, tr in enumerate(trades):
        pool = pools[S.quarter(tr.entry_time)]
        dur = tr.exit_time - tr.entry_time
        cand = pool[rng.integers(0, len(pool), size=(runs, 20))]
        tex = tclose[cand] + dur
        kx = np.searchsorted(tq, tex)
        kx_c = np.minimum(kx, len(tq) - 1)
        ok = jent_ok[cand] & (kx < len(tq)) & (tq[kx_c] == tex)
        first = np.argmax(ok, axis=1)
        has = ok[np.arange(runs), first]
        i = cand[np.arange(runs), first]
        j, k = jent[i], kx_c[np.arange(runs), first]
        d = tr.direction
        entry = np.where(d > 0, ao[np.minimum(j, len(tq) - 1)], bo[np.minimum(j, len(tq) - 1)])
        exit_ = np.where(d > 0, bo[k], ao[k])
        risk = 2 * atr[i]
        r = (exit_ - entry) * d / risk - slip * entry / risk
        vals[:, c] = np.where(has, r, np.nan)
    means = np.nanmean(vals, axis=1)
    return float(np.nanmean(means)), float(np.nanstd(means))
