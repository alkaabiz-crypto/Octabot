"""Part 3 of PROTOCOL.md: does gold's first 15 minutes after a news release tell the direction of the next hours?
Follow the first-15-minute direction, enter at the next 15m open, exit 4 h after the release, 2 x ATR14 stop.
Benchmark: the same clock time on non-event weekdays of the same quarter. Also measures move size (for the briefing).
usage: GOLD_DATA=<dir> python src/news_direction.py"""
import json
import os
import random
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as G  # noqa: E402

S = G.S
FIT = (S.ts(2020, 7), S.ts(2025, 1))
HOLD = 4 * 3600


def trade_at(g, idx, t, mode="follow", cost="primary"):
    """Release (or control) time t: returns (r, abs 4h move in ATR, abs 15m move in ATR) or None."""
    q = g.q
    j = idx.get(t)
    k = int(np.searchsorted(g.th, t, side="right")) - 2          # last hourly candle closed before t
    if j is None or k < 0 or j + 1 >= len(q["t"]) or g.atr_np[k] != g.atr_np[k]:
        return None
    a = g.atr_np[k]
    first = q["bc"][j] - q["bo"][j]
    if first == 0:
        return None
    d = 1 if first > 0 else -1
    if mode == "fade":
        d = -d
    j1 = j + 1
    if q["t"][j1] != t + 900:
        return None
    entry = q["ao"][j1] if d > 0 else q["bo"][j1]
    risk = 2.0 * a
    sl = entry - d * risk
    jj = j1
    px = None
    while jj < len(q["t"]) and q["t"][jj] < t + HOLD:
        adverse = q["bl"][jj] if d > 0 else q["ah"][jj]
        if (adverse - sl) * d <= 0:
            o = q["bo"][jj] if d > 0 else q["ao"][jj]
            px = o if (o - sl) * d < 0 else sl
            break
        jj += 1
    if px is None:
        if jj >= len(q["t"]):
            return None
        px = q["bo"][jj] if d > 0 else q["ao"][jj]
    exit_t = q["t"][min(jj, len(q["t"]) - 1)]
    days = (exit_t - (t + 900)) / 86400
    r = (px - entry) * d / risk - (G.SLIP[cost] + G.SWAP_PER_DAY[cost] * days) * entry / risk
    j4 = idx.get(t + HOLD)
    move4 = abs(q["bc"][j4 - 1] - q["bo"][j]) / a if j4 is not None else None
    return r, move4, abs(first) / a


def run(g, idx, times, controls_by_q, w0, w1, mode, runs=500, seed=20261112):
    sel = [t for t in times if w0 <= t < w1]
    out = [(t, trade_at(g, idx, t, mode)) for t in sel]
    out = [(t, x) for t, x in out if x is not None]
    if len(out) < 5:
        return {"events": len(out)}
    rs = np.array([x[0] for _, x in out])
    rnd = random.Random(seed)
    means = []
    for _ in range(runs):
        v = []
        for t, _x in out:
            pool = controls_by_q.get((S.quarter(t), time.gmtime(t).tm_hour, time.gmtime(t).tm_min), [])
            for _a in range(20):
                if not pool:
                    break
                y = trade_at(g, idx, rnd.choice(pool), mode)
                if y is not None:
                    v.append(y[0])
                    break
        if v:
            means.append(statistics.mean(v))
    mu, sd = statistics.mean(means), statistics.pstdev(means)
    ctrl_moves = []
    for t, _x in out:
        pool = controls_by_q.get((S.quarter(t), time.gmtime(t).tm_hour, time.gmtime(t).tm_min), [])
        for c in pool[:40]:
            y = trade_at(g, idx, c, mode)
            if y is not None and y[1] is not None:
                ctrl_moves.append(y[1])
    ev_moves = [x[1] for _, x in out if x[1] is not None]
    return {"events": len(out), "win_rate_pct": float((rs > 0).mean() * 100), "expectancy_r": float(rs.mean()),
            "random_mean_r": mu, "z": (float(rs.mean()) - mu) / sd if sd > 0 else 0.0,
            "median_4h_move_atr": float(np.median(ev_moves)) if ev_moves else None,
            "control_median_4h_move_atr": float(np.median(ctrl_moves)) if ctrl_moves else None,
            "median_first15_move_atr": float(np.median([x[2] for _, x in out]))}


def main():
    g = G.Gold(os.path.join(os.environ.get("GOLD_DATA", ""), "XAUUSDm_15m.csv.gz"))
    q = g.q
    idx = {t: j for j, t in enumerate(q["t"])}
    ev = G.all_events()
    all_ev = sorted(set(ev["FOMC"] + ev["CPI"] + ev["NFP"]))
    ev_days = {t // 86400 for t in all_ev}
    end = int(q["t"][-1])
    # control times: same clock (UTC) on weekdays with no event that day or the day before/after
    clock = {(time.gmtime(t).tm_hour, time.gmtime(t).tm_min) for t in all_ev}
    controls = {}
    for t in q["t"]:
        tm = time.gmtime(t)
        if (tm.tm_hour, tm.tm_min) not in clock or tm.tm_wday >= 5:
            continue
        dday = t // 86400
        if dday in ev_days or dday - 1 in ev_days or dday + 1 in ev_days:
            continue
        controls.setdefault((S.quarter(t), tm.tm_hour, tm.tm_min), []).append(t)
    res = {}
    for kind in ("FOMC", "CPI", "NFP"):
        for mode in ("follow", "fade"):
            res[f"{kind}|{mode}"] = {"fit": run(g, idx, ev[kind], controls, *FIT, mode),
                                     "test": run(g, idx, ev[kind], controls, FIT[1], end, mode)}
            print(kind, mode, json.dumps({p: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}
                                          for p, r in res[f"{kind}|{mode}"].items()}), flush=True)
    with open(os.path.join(G.ROOT, "reports", "news_direction.json"), "w") as f:
        json.dump({"meta": {"generated_utc": S.fmt(time.time()), "hold_hours": 4, "runs": 500}, "results": res}, f, indent=1)


if __name__ == "__main__":
    main()
