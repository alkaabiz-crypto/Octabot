"""News-trading strategies across markets (PROTOCOL.md). Writes reports/raw/<market>.json.
usage: LONG_DATA=<dir> MULTI_BARS=<dir> python src/run.py [workers]"""
import calendar
import datetime
import json
import multiprocessing
import os
import sys
import time
import zoneinfo

import holidays
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "gold_kst_news", "src"))
import engine as G  # noqa: E402

S = G.S
NY = zoneinfo.ZoneInfo("America/New_York")
FROM_LONG = {"USOILm", "BTCUSDm", "XAUUSDm"}
MARKETS = ("USOILm", "BTCUSDm", "XAUUSDm", "UKOILm", "ETHUSDm", "US500m", "USTECm", "US30m", "DE30m",
           "EURUSDm", "USDJPYm", "GBPUSDm", "USDCADm", "XAGUSDm")
EIA_MARKETS = {"USOILm", "UKOILm", "USDCADm"}
STRATS = ("FOLLOW15", "FADE15", "FOLLOW30", "BREAKOUT", "PRE24")
HOLD = 4 * 3600
TEST0 = S.ts(2025, 1)
RUNS = 300
# EIA's published exceptions (www.eia.gov/petroleum/supply/weekly/schedule.php, fetched 2026-11-12):
# data week ending -> (release date, New York time)
EIA_EXCEPTIONS = {
    "2024-12-27": ("2025-01-02", "11:00"), "2025-01-17": ("2025-01-23", "12:00"), "2025-02-14": ("2025-02-20", "12:00"),
    "2025-05-23": ("2025-05-29", "12:00"), "2025-08-29": ("2025-09-04", "12:00"), "2025-10-10": ("2025-10-16", "12:00"),
    "2025-11-07": ("2025-11-13", "12:00"), "2025-12-19": ("2025-12-29", "17:00"), "2026-01-16": ("2026-01-22", "12:00"),
    "2026-02-13": ("2026-02-19", "12:00"), "2026-05-22": ("2026-05-28", "12:00"), "2026-09-04": ("2026-09-10", "12:00"),
    "2026-10-09": ("2026-10-15", "12:00"), "2026-11-06": ("2026-11-12", "12:00")}


def eia_candidates(y0=2020, y1=2026):
    """(utc, from_rule) for every weekly petroleum report."""
    hol = holidays.US(years=range(y0, y1 + 1))
    out = []
    d = datetime.date(y0, 1, 3)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    while d.year <= y1:
        key = d.isoformat()
        wed = d + datetime.timedelta(days=5)
        if key in EIA_EXCEPTIONS:
            a, b = EIA_EXCEPTIONS[key]
            out.append((G.ny_to_utc(datetime.date.fromisoformat(a), b), False))
        elif wed >= datetime.date(2024, 12, 30):
            out.append((G.ny_to_utc(wed, "10:30"), False))
        else:
            week = [wed - datetime.timedelta(days=2), wed - datetime.timedelta(days=1), wed]
            if any(x in hol for x in week):
                out.append((G.ny_to_utc(wed + datetime.timedelta(days=1), "11:00"), True))
            else:
                out.append((G.ny_to_utc(wed, "10:30"), True))
        d += datetime.timedelta(days=7)
    return out


def spike_ok(q, idx, t):
    j = idx.get(t)
    if j is None:
        return False
    r = q["bh"][j] - q["bl"][j]
    others = [q["bh"][idx[t + k * 86400]] - q["bl"][idx[t + k * 86400]] for k in (-14, -13, -8, -7, -6, 6, 7, 8, 13, 14)
              if t + k * 86400 in idx]
    return bool(others) and r > float(np.median(others))


def eia_events(oil_path):
    q = G.oil.load_15m(oil_path)
    idx = {t: j for j, t in enumerate(q["t"])}
    kept, dropped = [], 0
    for t, rule in eia_candidates():
        if t > q["t"][-1]:
            continue
        if rule and t >= q["t"][0] and not spike_ok(q, idx, t):
            dropped += 1
            continue
        kept.append(t)
    return kept, dropped


# ------------------------------------------------------------------------------------------------- simulation
class Mkt:
    def __init__(self, path):
        self.g = G.Gold(path)
        self.q = self.g.q
        self.tq = self.g.tq
        self.idx = {int(t): j for j, t in enumerate(self.tq)}

    def atr_before(self, t):
        k = int(np.searchsorted(self.g.th, t, side="right")) - 2
        a = self.g.atr_np[k] if k >= 0 else np.nan
        return a if a == a and a > 0 else None

    def walk(self, d, j, t_exit, a, cost):
        q, tq = self.q, self.tq
        entry = q["ao"][j] if d > 0 else q["bo"][j]
        risk = 2 * a
        sl = entry - d * risk
        t0 = tq[j]
        n = len(tq)
        while j < n and tq[j] < t_exit:
            adverse = q["bl"][j] if d > 0 else q["ah"][j]
            if (adverse - sl) * d <= 0:
                o = q["bo"][j] if d > 0 else q["ao"][j]
                px = o if (o - sl) * d < 0 else sl
                break
            j += 1
        else:
            if j >= n or tq[j] - t_exit > 3 * 3600:
                return None
            px = q["bo"][j] if d > 0 else q["ao"][j]
        days = (tq[min(j, n - 1)] - t0) / 86400
        return (px - entry) * d / risk - (G.SLIP[cost] + G.SWAP_PER_DAY[cost] * days) * entry / risk

    def trade(self, t, strat, cost="primary"):
        q, idx = self.q, self.idx
        a = self.atr_before(t if strat != "PRE24" else t - 86400)
        if a is None:
            return None
        if strat == "PRE24":
            j = idx.get(t - 86400)
            return None if j is None else self.walk(1, j, t - 900, a, cost)
        j = idx.get(t)
        if j is None:
            return None
        if strat in ("FOLLOW15", "FADE15"):
            mv = q["bc"][j] - q["bo"][j]
            if mv == 0 or idx.get(t + 900) is None:
                return None
            d = (1 if mv > 0 else -1) * (1 if strat == "FOLLOW15" else -1)
            return self.walk(d, idx[t + 900], t + HOLD, a, cost)
        if strat == "FOLLOW30":
            j2, j3 = idx.get(t + 900), idx.get(t + 1800)
            if j2 is None or j3 is None:
                return None
            mv = q["bc"][j2] - q["bo"][j]
            if mv == 0:
                return None
            return self.walk(1 if mv > 0 else -1, j3, t + HOLD, a, cost)
        if strat == "BREAKOUT":
            hi, lo = q["bh"][j], q["bl"][j]
            for k in (1, 2, 3):
                jj = idx.get(t + 900 * k)
                if jj is None or jj + 1 >= len(self.tq) or self.tq[jj + 1] != t + 900 * (k + 1):
                    continue
                if q["bc"][jj] > hi:
                    return self.walk(1, jj + 1, t + HOLD, a, cost)
                if q["bc"][jj] < lo:
                    return self.walk(-1, jj + 1, t + HOLD, a, cost)
            return None
        raise ValueError(strat)

    def move(self, t):
        a = self.atr_before(t)
        j, k = self.idx.get(t), self.idx.get(t + HOLD)
        if a is None or j is None or k is None:
            return None
        return abs(self.q["bc"][k - 1] - self.q["bo"][j]) / a


def controls(m, all_events, macro_events):
    ev_days = {t // 86400 for t in all_events}
    near = {t // 86400 + k for t in macro_events for k in (-1, 1)}
    clocks = {}
    for t in m.tq:
        t = int(t)
        tm = time.gmtime(t)
        if tm.tm_wday >= 5:
            continue
        dd = t // 86400
        if dd in ev_days or dd in near:
            continue
        clocks.setdefault((S.quarter(t), tm.tm_hour, tm.tm_min), []).append(t)
    return clocks


def evaluate(m, events, pool, strat, w0, w1, rng, cache):
    sel = [t for t in events if w0 <= t < w1]
    rs, rst, keys = [], [], []
    for t in sel:
        r = m.trade(t, strat)
        if r is None:
            continue
        rs.append(r)
        rst.append(m.trade(t, strat, "stress"))
        tm = time.gmtime(t)
        keys.append((S.quarter(t), tm.tm_hour, tm.tm_min))
    out = {"events": len(rs)}
    if len(rs) < 5:
        return out
    ctrl = []
    for k in keys:
        if (strat, k) not in cache:
            vals = [m.trade(c, strat) for c in pool.get(k, [])]
            cache[(strat, k)] = np.array([v for v in vals if v is not None])
        ctrl.append(cache[(strat, k)])
    if any(len(c) == 0 for c in ctrl):
        ok = [i for i, c in enumerate(ctrl) if len(c)]
        rs, rst, ctrl = [rs[i] for i in ok], [rst[i] for i in ok], [ctrl[i] for i in ok]
        out["events"] = len(rs)
        if len(rs) < 5:
            return out
    draws = np.array([c[rng.integers(0, len(c), RUNS)] for c in ctrl])      # events x runs
    means = draws.mean(axis=0)
    rs = np.array(rs)
    mu, sd = float(means.mean()), float(means.std())
    out.update({"win_rate_pct": float((rs > 0).mean() * 100), "expectancy_r": float(rs.mean()),
                "expectancy_stress_r": float(np.mean(rst)), "total_r": float(rs.sum()), "control_mean_r": mu,
                "z": (float(rs.mean()) - mu) / sd if sd > 0 else 0.0})
    return out


def run_market(mkt):
    t0 = time.time()
    base = os.environ["LONG_DATA"] if mkt in FROM_LONG else os.environ["MULTI_BARS"]
    m = Mkt(os.path.join(base, f"{mkt}_15m.csv.gz"))
    ev = G.all_events()
    kinds = {"FOMC": ev["FOMC"], "CPI": ev["CPI"], "NFP": ev["NFP"]}
    eia_dropped = None
    if mkt in EIA_MARKETS:
        kinds["EIA"], eia_dropped = eia_events(os.path.join(os.environ["LONG_DATA"], "USOILm_15m.csv.gz"))
    macro = ev["FOMC"] + ev["CPI"] + ev["NFP"]
    allev = sorted(set(macro + kinds.get("EIA", [])))
    pool = controls(m, allev, macro)
    first = int(m.tq[0])
    fit0 = S.ts(2020, 7) if mkt in FROM_LONG else S.ts(2023, 7)
    fit0 = max(fit0, first + 30 * 86400)
    end = int(m.tq[-1])
    rng = np.random.default_rng(20261112)
    cache = {}
    res, moves = {}, {}
    for kind, evs in kinds.items():
        for strat in STRATS:
            res[f"{kind}|{strat}"] = {"fit": evaluate(m, evs, pool, strat, fit0, TEST0, rng, cache),
                                      "test": evaluate(m, evs, pool, strat, TEST0, end, rng, cache)}
        ev_mv = [x for x in (m.move(t) for t in evs if t >= fit0) if x is not None]
        ctl = []
        for t in evs:
            if t < fit0:
                continue
            tm = time.gmtime(t)
            for c in pool.get((S.quarter(t), tm.tm_hour, tm.tm_min), [])[:20]:
                x = m.move(c)
                if x is not None:
                    ctl.append(x)
        moves[kind] = {"event_median_4h_move_atr": float(np.median(ev_mv)) if ev_mv else None,
                       "control_median_4h_move_atr": float(np.median(ctl)) if ctl else None, "events": len(ev_mv)}
    out = {"meta": {"market": mkt, "generated_utc": S.fmt(time.time()), "fit": [S.fmt(fit0), S.fmt(TEST0)],
                    "test_end": S.fmt(end), "runs": RUNS, "eia_rule_dates_dropped": eia_dropped,
                    "seconds": round(time.time() - t0)}, "results": res, "moves": moves}
    os.makedirs(os.path.join(ROOT, "reports", "raw"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "reports", "raw", f"{mkt}.json"), "w"), indent=1)
    return mkt, round(time.time() - t0)


def main():
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    with multiprocessing.Pool(workers) as p:
        for mkt, s in p.imap_unordered(run_market, MARKETS):
            print("finished", mkt, s, "s", flush=True)


if __name__ == "__main__":
    main()
