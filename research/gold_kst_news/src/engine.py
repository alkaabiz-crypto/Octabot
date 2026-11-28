"""Gold KST + session VWAP BUY engine with configurable exits and news rules (PROTOCOL.md). Compiled with numba.

Reuses the tested data loader, candle aggregation, ATR and session VWAP of the earlier rounds (read-only)."""
import bisect
import calendar
import collections
import csv
import datetime
import os
import sys
import zoneinfo

import numba
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "oil_rsi_vwap", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "rsi_vwap_study", "src"))
import oil  # noqa: E402
import study as S  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
SLIP = {"primary": 0.0002, "stress": 0.0005}
SWAP_PER_DAY = {"primary": 0.0, "stress": 0.0002}
NEWS_RULES = ("NONE", "BLOCK", "BLOCK_FLAT", "BLOCK_24H")
# entry blocked from `before` seconds before to `after` seconds after an event; FLAT: close 30 min before
_NEWS_WINDOWS = {"NONE": (0, 0, False), "BLOCK": (7200, 3600, False), "BLOCK_FLAT": (7200, 3600, True),
                 "BLOCK_24H": (86400, 0, False)}


# ------------------------------------------------------------------------------------------------- events
def ny_to_utc(date, hhmm):
    h, m = map(int, hhmm.split(":"))
    dt = datetime.datetime(date.year, date.month, date.day, h, m, tzinfo=NY)
    return calendar.timegm(dt.utctimetuple())


def fomc_events():
    out = []
    with open(os.path.join(ROOT, "data", "fomc_decisions.csv")) as f:
        for r in csv.DictReader(line for line in f if not line.startswith("#")):
            out.append(ny_to_utc(datetime.date.fromisoformat(r["date"]), r["time_ny"]))
    return out


def _release_csv(name):
    with open(os.path.join(ROOT, "data", name)) as f:
        return [ny_to_utc(datetime.date.fromisoformat(r["date"]), "08:30")
                for r in csv.DictReader(line for line in f if not line.startswith("#"))]


def all_events():
    """{kind: sorted UTC release times} for FOMC, CPI and NFP (official dates, see data/)."""
    return {"FOMC": sorted(fomc_events()), "CPI": _release_csv("cpi_releases.csv"), "NFP": _release_csv("nfp_releases.csv")}


def nfp_rule_dates(y0, y1):
    """BLS rule: the third Friday after the end (Saturday) of the week (Sun-Sat) that contains the 12th."""
    out = []
    for y in range(y0, y1 + 1):
        for m in range(1, 13):
            d12 = datetime.date(y, m, 12)
            sat = d12 + datetime.timedelta(days=(5 - d12.weekday()) % 7)
            out.append(sat + datetime.timedelta(days=6 + 14))
    return out


# ------------------------------------------------------------------------------------------------- data
class Gold:
    def __init__(self, path):
        q = oil.load_15m(path)
        self.q = q
        E = oil.aggregate(q["t"], q["bo"], q["bh"], q["bl"], q["bc"], q["n"], 3600)
        if E.t and E.t[-1] + 3600 > q["t"][-1] + 900:
            for arr in (E.t, E.o, E.h, E.l, E.c, E.v):
                arr.pop()
        self.e = E
        self.atr = S.atr(E.h, E.l, E.c)
        self.vwap, _ = oil.session_vwap(E.t, E.h, E.l, E.c, E.v)
        c, n = E.c, len(E.c)
        roc = lambda k: [None] * k + [100 * (c[i] - c[i - k]) / c[i - k] for i in range(k, n)]  # noqa: E731

        def sma(x, k):
            out = [None] * len(x)
            for i in range(k - 1, len(x)):
                w = x[i - k + 1:i + 1]
                if None not in w:
                    out[i] = sum(w) / k
            return out
        kst = [None if None in (a, b, d, e) else a + 2 * b + 3 * d + 4 * e
               for a, b, d, e in zip(sma(roc(10), 10), sma(roc(15), 10), sma(roc(20), 10), sma(roc(30), 15))]
        sig = sma(kst, 9)
        up = [False] * n
        dn = [False] * n
        for i in range(1, n):
            if None in (kst[i], kst[i - 1], sig[i], sig[i - 1]):
                continue
            up[i] = kst[i - 1] <= sig[i - 1] and kst[i] > sig[i]
            dn[i] = kst[i - 1] >= sig[i - 1] and kst[i] < sig[i]
        self.kst_up, self.kst_dn = up, dn
        self.buy = [u and w is not None and cc > w for u, cc, w in zip(up, c, self.vwap)]
        # arrays for the compiled simulator
        self.tq = np.array(q["t"], np.int64)
        self.A = {k: np.array(q[k]) for k in ("ao", "bo", "bh", "bl", "bc")}
        self.th = np.array(E.t, np.int64)
        self.atr_np = np.array([np.nan if x is None else x for x in self.atr])
        self.j_entry = np.searchsorted(self.tq, self.th + 3600)          # 15m index of the hour close
        self.j_entry_ok = (self.j_entry < len(self.tq)) & (self.tq[np.minimum(self.j_entry, len(self.tq) - 1)] == self.th + 3600)
        # for each hourly bar, the index of the next bearish KST cross (strictly later), -1 if none
        nxt = np.full(n, -1, np.int64)
        k = -1
        for i in range(n - 1, -1, -1):
            nxt[i] = k
            if dn[i]:
                k = i
        self.next_dn = nxt
        self.hour_of_15m = np.searchsorted(self.th, self.tq, side="right") - 1   # hourly bar containing each 15m bar

    def news_arrays(self, events):
        ev = np.array(sorted(events), np.int64)
        return ev


# ------------------------------------------------------------------------------------------------- simulator
@numba.njit(cache=True)
def _sim(i, tq, ao, bo, bh, bl, bc, th, atr, j_entry, next_dn, hour_of_15m, ev,
         stop_atr, trail_atr, be_on, time_h, lose_h, flat):
    """One BUY leg from hourly signal bar i. Returns (entry_t, exit_t, entry, risk, r_gross) or entry_t = -1."""
    a = atr[i]
    j = j_entry[i]
    if np.isnan(a) or a <= 0 or j >= tq.shape[0] or tq[j] != th[i] + 3600:
        return -1, 0, 0.0, 0.0, 0.0
    entry = ao[j]
    risk = 2.0 * a
    t0 = tq[j]
    sl = -1e18 if stop_atr == 0 else entry - stop_atr * a
    best = entry
    k_dn = next_dn[i]
    t_flip = th[k_dn] + 3600 if k_dn >= 0 else 1 << 62
    e_ptr = np.searchsorted(ev, t0)
    n = tq.shape[0]
    while j < n:
        t = tq[j]
        # exits decided at this 15m open
        if t >= t_flip:
            return t0, t, entry, risk, (bo[j] - entry) / risk
        if flat:
            while e_ptr < ev.shape[0] and ev[e_ptr] - 1800 < t0:
                e_ptr += 1
            if e_ptr < ev.shape[0] and t >= ev[e_ptr] - 1800:
                return t0, t, entry, risk, (bo[j] - entry) / risk
        if time_h > 0 and t - t0 >= time_h * 3600:
            return t0, t, entry, risk, (bo[j] - entry) / risk
        # intrabar stop
        if bl[j] <= sl:
            px = bo[j] if bo[j] < sl else sl
            return t0, t + 900, entry, risk, (px - entry) / risk
        bar_close = t + 900
        if bar_close % 3600 == 0:
            k = hour_of_15m[j]
            if k >= 0 and not np.isnan(atr[k]):
                c = bc[j]
                if c > best:
                    best = c
                if trail_atr > 0:
                    tr = best - trail_atr * atr[k]
                    if tr > sl:
                        sl = tr
                if be_on and best - entry >= 2.0 * a and entry > sl:
                    sl = entry
                if lose_h > 0 and bar_close - t0 >= lose_h * 3600 and bar_close - t0 < lose_h * 3600 + 3600 and c < entry:
                    if j + 1 < n:
                        return t0, tq[j + 1], entry, risk, (bo[j + 1] - entry) / risk
        j += 1
    return -1, 0, 0.0, 0.0, 0.0


@numba.njit(cache=True)
def _blocked(t, ev, before, after):
    if before == 0 and after == 0:
        return False
    p = np.searchsorted(ev, t - after)
    return p < ev.shape[0] and ev[p] - before <= t


@numba.njit(cache=True)
def _run(sig, w0, w1, tq, ao, bo, bh, bl, bc, th, atr, j_entry, next_dn, hour_of_15m, ev,
         stop_atr, trail_atr, be_on, time_h, lose_h, before, after, flat):
    n = th.shape[0]
    out = np.zeros((n, 5))
    m = 0
    busy = -1
    for i in range(n):
        tc = th[i] + 3600
        if not sig[i] or tc < w0 or tc >= w1 or tc < busy:
            continue
        if _blocked(tc, ev, before, after):
            continue
        r = _sim(i, tq, ao, bo, bh, bl, bc, th, atr, j_entry, next_dn, hour_of_15m, ev,
                 stop_atr, trail_atr, be_on, time_h, lose_h, flat)
        if r[0] < 0:
            continue
        out[m, 0], out[m, 1], out[m, 2], out[m, 3], out[m, 4] = r
        out[m, 0] = i
        m += 1
        busy = r[1]
    return out[:m]


@numba.njit(cache=True)
def _bench(pools, pool_off, quarters_of_trades, seed, runs, tq, ao, bo, bh, bl, bc, th, atr, j_entry, next_dn,
           hour_of_15m, ev, stop_atr, trail_atr, be_on, time_h, lose_h, before, after, flat, slip, swap):
    np.random.seed(seed)
    means = np.full(runs, np.nan)
    for r in range(runs):
        s, cnt = 0.0, 0
        for q in quarters_of_trades:
            a, b = pool_off[q], pool_off[q + 1]
            if b <= a:
                continue
            for _ in range(30):
                i = pools[a + np.random.randint(b - a)]
                if _blocked(th[i] + 3600, ev, before, after):
                    continue
                x = _sim(i, tq, ao, bo, bh, bl, bc, th, atr, j_entry, next_dn, hour_of_15m, ev,
                         stop_atr, trail_atr, be_on, time_h, lose_h, flat)
                if x[0] >= 0:
                    days = (x[1] - x[0]) / 86400.0
                    s += x[4] - (slip + swap * days) * x[2] / x[3]
                    cnt += 1
                    break
        if cnt > 0:
            means[r] = s / cnt
    return means


class Runner:
    def __init__(self, g, events):
        self.g = g
        self.ev = np.array(sorted(events), np.int64)
        self.sig = np.array(g.buy)
        self.arr = (g.tq, g.A["ao"], g.A["bo"], g.A["bh"], g.A["bl"], g.A["bc"], g.th, g.atr_np, g.j_entry,
                    g.next_dn, g.hour_of_15m, self.ev)

    def legs(self, p, w0, w1, sig=None):
        stop_atr, trail_atr, be_on, time_h, lose_h, news = p
        before, after, flat = _NEWS_WINDOWS[news]
        raw = _run(self.sig if sig is None else sig, w0, w1, *self.arr, float(stop_atr), float(trail_atr), bool(be_on),
                   int(time_h), int(lose_h), int(before), int(after), bool(flat))
        th = self.g.th
        ent_t = th[raw[:, 0].astype(np.int64)] + 3600 if len(raw) else np.zeros(0)
        return {"signal_index": raw[:, 0].astype(np.int64), "entry_t": ent_t, "exit_t": raw[:, 1],
                "entry": raw[:, 2], "risk": raw[:, 3], "r_gross": raw[:, 4]}

    @staticmethod
    def r(legs, cost):
        days = (legs["exit_t"] - legs["entry_t"]) / 86400.0
        return legs["r_gross"] - (SLIP[cost] + SWAP_PER_DAY[cost] * days) * legs["entry"] / legs["risk"]

    def bench(self, p, legs, w0, w1, runs=200, seed=20261112, cost="primary"):
        stop_atr, trail_atr, be_on, time_h, lose_h, news = p
        before, after, flat = _NEWS_WINDOWS[news]
        th = self.g.th
        tc = th + 3600
        qs = sorted({S.quarter(int(t)) for t in tc if w0 <= t < w1})
        qmap = {q: k for k, q in enumerate(qs)}
        pools, off = [], [0]
        for q in qs:
            idx = [i for i in range(len(th)) if w0 <= tc[i] < w1 and S.quarter(int(tc[i])) == q]
            pools.extend(idx)
            off.append(len(pools))
        qt = np.array([qmap[S.quarter(int(t))] for t in legs["entry_t"]], np.int64)
        means = _bench(np.array(pools, np.int64), np.array(off, np.int64), qt, seed, runs, *self.arr,
                       float(stop_atr), float(trail_atr), bool(be_on), int(time_h), int(lose_h), int(before),
                       int(after), bool(flat), SLIP[cost], SWAP_PER_DAY[cost])
        means = means[~np.isnan(means)]
        return float(means.mean()), float(means.std())


def max_drawdown(rs):
    eq = np.cumsum(rs)
    peak = np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:]
    return float((peak - eq).max()) if len(rs) else 0.0
