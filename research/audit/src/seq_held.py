"""Corrected benchmark for held legs (hold-to-opposite-signal and strategies' own exits): sequential, non-overlapping
random entries (like fast_bench.standard, which audit 2 found well calibrated), each held for a duration drawn from
the strategy's own leg durations, entry counts matched per calendar quarter. Same fills and costs as fast_bench.held."""
import collections

import numba
import numpy as np

import oil
import study as S


@numba.njit(cache=True)
def _runs(tc, qi, jent, jok, tq, ao, bo, atr, durs, d, p, slip, swap, seed, runs, count_only):
    np.random.seed(seed)
    nq = p.shape[0]
    counts = np.zeros((runs, nq))
    means = np.full(runs, np.nan)
    n = tc.shape[0]
    m = tq.shape[0]
    for r in range(runs):
        busy = -1
        s = 0.0
        c = 0
        for k in range(n):
            if tc[k] < busy or not jok[k]:
                continue
            if np.random.random() >= p[qi[k]]:
                continue
            dur = durs[np.random.randint(durs.shape[0])]
            tex = tc[k] + dur
            kx = np.searchsorted(tq, tex)
            if kx >= m or tq[kx] != tex:
                continue
            counts[r, qi[k]] += 1
            busy = tex
            if count_only:
                continue
            j = jent[k]
            entry = ao[j] if d > 0 else bo[j]
            ex = bo[kx] if d > 0 else ao[kx]
            risk = 2.0 * atr[k]
            s += (ex - entry) * d / risk - (slip + swap * dur / 86400.0) * entry / risk
            c += 1
        if c > 0:
            means[r] = s / c
    return counts, means


def seq_held(asset, trades, w0, w1, runs=500, seed=20261112, cost="primary"):
    """trades: one direction. Returns (mean, sd) of random-run mean R."""
    if not trades:
        return float("nan"), float("nan")
    E, q = asset.e, asset.q
    tq = np.array(q["t"], np.int64)
    ao, bo = np.array(q["ao"]), np.array(q["bo"])
    atr_all = np.array([np.nan if x is None else x for x in asset.atr])
    tclose = np.array(E.t, np.int64) + 3600
    sel = np.where((tclose >= w0) & (tclose < w1))[0]
    tc = tclose[sel]
    jent = np.searchsorted(tq, tc)
    jc = np.minimum(jent, len(tq) - 1)
    atr = atr_all[sel]
    jok = (jent < len(tq)) & (tq[jc] == tc) & (atr > 0)
    quarters = sorted({S.quarter(int(t)) for t in tc})
    qmap = {qq: i for i, qq in enumerate(quarters)}
    qi = np.array([qmap[S.quarter(int(t))] for t in tc], np.int64)
    want = collections.Counter(S.quarter(t.entry_time) for t in trades)
    want = np.array([want.get(qq, 0) for qq in quarters], float)
    per_q = np.bincount(qi, minlength=len(quarters)).astype(float)
    durs = np.array([t.exit_time - t.entry_time for t in trades], np.int64)
    d = trades[0].direction
    p = np.minimum(1.0, want / np.maximum(per_q, 1) * 4)
    for it in range(8):
        counts, _ = _runs(tc, qi, jc, jok, tq, ao, bo, atr, durs, d, p, 0.0, 0.0, seed + it, 40, True)
        got = counts.mean(axis=0)
        p = np.where(want == 0, 0.0, np.minimum(1.0, p * np.where(got > 0, want / np.maximum(got, 1e-12), 4.0)))
    _, means = _runs(tc, qi, jc, jok, tq, ao, bo, atr, durs, d, p, oil.SLIP[cost], oil.SWAP_PER_DAY[cost], seed + 99, runs, False)
    means = means[~np.isnan(means)]
    return float(means.mean()), float(means.std())
