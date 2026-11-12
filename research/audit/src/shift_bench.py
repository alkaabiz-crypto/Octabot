"""Corrected benchmark for held legs (hold-to-opposite-signal and strategies' own exits).

The old benchmark (long_history fast_bench.held) drew each leg's random entry independently. Real held legs are
back-to-back and cover most of the period, so their mean varies far less than independent draws: under the null
its z had sd 0.68 (audit 2), i.e. it was too strict. Here every run shifts the WHOLE leg sequence by one random
offset in time (wrapping inside the period), keeping each leg's direction, length and spacing. Same fills and
costs as fast_bench.held."""
import numpy as np

import study as S  # noqa: F401
import oil


def held_shift(asset, trades, w0, w1, runs=1000, seed=20261112, cost="primary"):
    E, q = asset.e, asset.q
    tq = np.array(q["t"], np.int64)
    ao, bo = np.array(q["ao"]), np.array(q["bo"])
    atr = np.array([np.nan if x is None else x for x in asset.atr])
    tclose = np.array(E.t, np.int64) + 3600
    win = np.where((tclose >= w0) & (tclose < w1))[0]
    N = len(win)
    if N < 10 or not trades:
        return float("nan"), float("nan")
    jent = np.searchsorted(tq, tclose)
    jent_c = np.minimum(jent, len(tq) - 1)
    jent_ok = (jent < len(tq)) & (tq[jent_c] == tclose) & (atr > 0)
    loc = {int(i): k for k, i in enumerate(win)}
    p = np.array([loc.get(int(t.signal_index), -1) for t in trades])
    keep = p >= 0
    p = p[keep]
    tr = [t for t, k in zip(trades, keep) if k]
    dur = np.array([t.exit_time - t.entry_time for t in tr], np.int64)
    d = np.array([t.direction for t in tr])
    rng = np.random.default_rng(seed)
    off = rng.integers(1, N, size=runs)
    newp = (p[None, :] + off[:, None]) % N                     # runs x legs
    i = win[newp]
    tex = tclose[i] + dur[None, :]
    kx = np.searchsorted(tq, tex)
    kx_c = np.minimum(kx, len(tq) - 1)
    ok = jent_ok[i] & (kx < len(tq)) & (tq[kx_c] == tex)
    j = jent_c[i]
    entry = np.where(d[None, :] > 0, ao[j], bo[j])
    exit_ = np.where(d[None, :] > 0, bo[kx_c], ao[kx_c])
    risk = 2 * atr[i]
    days = dur[None, :] / 86400
    r = (exit_ - entry) * d[None, :] / risk - (oil.SLIP[cost] + oil.SWAP_PER_DAY[cost] * days) * entry / risk
    r = np.where(ok, r, np.nan)
    means = np.nanmean(r, axis=1)
    return float(np.nanmean(means)), float(np.nanstd(means))
