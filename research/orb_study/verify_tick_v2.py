"""Tick-level re-test of the v2 pass XAU_NY0930|R1|TOUCH_X0 (gold, first 1-minute candle after 09:30 New York, touch entry,
stop at the other side, 1:1 target, forced exit 16:00 New York). Same fill rules as verify_tick.py / VERIFY_PREREG.md.

Usage: CACHE_DIR=<screen_cache with XAUUSDm_YYYY_MM npz ticks> python3 -I verify_tick_v2.py
"""
import datetime as dt, json, os, time
from zoneinfo import ZoneInfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.environ["CACHE_DIR"]; NY = ZoneInfo("America/New_York")
MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
WINDOWS = {"R1_0930": ((9, 30), 1), "R1_0929": ((9, 29), 1), "R1_0931": ((9, 31), 1), "R2_0930": ((9, 30), 2)}


def ms(d, h, m):
    return int(dt.datetime(d.year, d.month, d.day, h, m, tzinfo=NY).timestamp() * 1000)


def day_trade(t, b, a, d, start, length):
    s0 = ms(d, *start); s1 = s0 + length * 60_000; fx = ms(d, 16, 0)
    i, j = np.searchsorted(t, s0), np.searchsorted(t, s1)
    if j - i < 5 or t[i] - s0 > 60_000: return None
    mid = (b[i:j] + a[i:j]) / 2; rh, rl = mid.max(), mid.min(); H = rh - rl; hs0 = (a[i] - b[i]) / 2
    if H <= 0: return None
    k, e = j, np.searchsorted(t, fx)
    if e - k < 10: return None
    up = np.flatnonzero(a[k:e] >= rh + hs0); dn = np.flatnonzero(b[k:e] <= rl - hs0)
    fu = up[0] if len(up) else None; fd = dn[0] if len(dn) else None
    if fu is None and fd is None: return None
    side = 1 if (fd is None or (fu is not None and fu < fd)) else -1; q = k + (fu if side > 0 else fd)
    entry = a[q] if side > 0 else b[q]; sp_in = a[q] - b[q]
    stop_lvl, tp_lvl = ((rl - hs0, rh + H - hs0) if side > 0 else (rh + hs0, rl - H + hs0))
    bb, aa = b[q + 1:e], a[q + 1:e]
    st = np.flatnonzero(bb <= stop_lvl) if side > 0 else np.flatnonzero(aa >= stop_lvl)
    tp = np.flatnonzero(bb >= tp_lvl) if side > 0 else np.flatnonzero(aa <= tp_lvl)
    s_i = st[0] if len(st) else 10**12; t_i = tp[0] if len(tp) else 10**12
    if s_i < t_i: x, px = s_i, (bb[s_i] if side > 0 else aa[s_i])
    elif t_i < 10**12: x, px = t_i, tp_lvl
    else: x, px = len(bb) - 1, (bb[-1] if side > 0 else aa[-1])
    r1 = side * (px - entry) / H; r2 = r1 - (sp_in / 2 + (aa[x] - bb[x]) / 2) / H
    return dict(day=str(d), r1=r1, r2=r2, H=H, spread_over_H=sp_in / H)


def summ(rows, key):
    r = np.array([x[key] for x in rows]); return dict(trades=int(len(r)), mean_R=round(float(r.mean()), 4), win=round(float((r > 0).mean()), 3))


def main():
    t0 = time.time(); res = {w: [] for w in WINDOWS}
    for y, m in MONTHS:
        z = np.load(os.path.join(CACHE, f"XAUUSDm_{y}_{m:02d}.npz")); t, b, a = z["t"], z["bid"], z["ask"]; o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
        d = dt.date(y, m, 1)
        while d.month == m:
            if d.weekday() < 5:
                for w, (st, ln) in WINDOWS.items():
                    r = day_trade(t, b, a, d, st, ln)
                    if r: res[w].append(r)
            d += dt.timedelta(days=1)
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), windows={})
    for w, rows in res.items():
        out["windows"][w] = {p: {k: summ([r for r in rows if (r["day"] < "2026") == (p == "2025")], k) for k in ("r1", "r2")} for p in ("2025", "2026")}
        out["windows"][w]["median_spread_over_range"] = round(float(np.median([r["spread_over_H"] for r in rows])), 3)
    x = out["windows"]["R1_0930"]
    out["verdict"] = "CONFIRMED" if (x["2025"]["r2"]["mean_R"] > 0 and x["2026"]["r2"]["mean_R"] > 0) else "NOT CONFIRMED"
    json.dump(out, open(os.path.join(HERE, "results", "verify_tick_v2.json"), "w"), indent=1)
    print(json.dumps(out, indent=1), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
