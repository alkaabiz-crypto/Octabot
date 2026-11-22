"""ORB / school-run study. Implements PREREGISTRATION.md (this folder).

Usage: BARS_DIR=<dir with <sym>_1m.npz from build_bars.py> python3 -I study.py
"""
import datetime as dt, json, os, time, zlib
from multiprocessing import Pool
from zoneinfo import ZoneInfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); BARS = os.environ["BARS_DIR"]
MARKETS = {"DE30m": ("Europe/Berlin", (9, 0), (17, 30)), "US500m": ("America/New_York", (9, 30), (16, 0)),
           "USTECm": ("America/New_York", (9, 30), (16, 0)), "XAUUSDm": ("America/New_York", (8, 20), (13, 30)),
           "USOILm": ("America/New_York", (9, 0), (14, 30))}
RANGES = {"R1": (0, 1, 1), "R5": (0, 5, 5), "R15": (0, 15, 15), "SCHOOL": (5, 10, 5)}   # (start offset, end offset, close-filter candle) minutes
EXITS = ("X0", "XC"); N_RANDOM = 500; SEED = 20261112
DAYS = [dt.date(2025, 1, 1) + dt.timedelta(days=i) for i in range((dt.date(2026, 10, 31) - dt.date(2025, 1, 1)).days + 1)]
DAYS = [d for d in DAYS if d.weekday() < 5]
D = {}


def minute(day, hm, tz):
    return int(dt.datetime(day.year, day.month, day.day, hm[0], hm[1], tzinfo=ZoneInfo(tz)).timestamp() // 60)


def setup(sym):
    z = np.load(os.path.join(BARS, f"{sym}_1m.npz")); tz, op, fx = MARKETS[sym]
    D[sym] = dict(m=z["m"], o=z["o"], h=z["h"], l=z["l"], c=z["c"], hs=z["sp"] / 2)
    days = []
    for d in DAYS:
        o_m, f_m = minute(d, op, tz), minute(d, fx, tz)
        days.append((d, o_m, f_m))
    D[sym]["days"] = days


def idx(sym, a, b):
    m = D[sym]["m"]; return int(np.searchsorted(m, a)), int(np.searchsorted(m, b))   # bars with a <= minute < b


def manage(sym, side, i0, j_end, lvl_entry, stop, tp, H, mult, xc=None):
    """From bar i0 (entry bar) to bar j_end-1: stop first, then target; xc=(candle_end_minute, rh, rl) close filter. Returns R."""
    g = D[sym]; hs = g["hs"] * mult
    entry = lvl_entry + side * hs[i0]
    lo, hi = g["l"][i0:j_end], g["h"][i0:j_end]
    hit_stop = (lo <= stop) if side > 0 else (hi >= stop)
    hit_tp = (hi >= tp) if side > 0 else (lo <= tp)
    s = int(np.argmax(hit_stop)) if hit_stop.any() else 10**9; t = int(np.argmax(hit_tp)) if hit_tp.any() else 10**9
    k_exit, px = None, None
    if s <= t and s < 10**9: k_exit, px = s, stop
    elif t < 10**9: k_exit, px = t, tp
    if xc is not None:
        ce, rh, rl = xc; jc = int(np.searchsorted(g["m"], ce)) - 1 - i0   # last bar of the entry candle
        if 0 <= jc < j_end - i0 and (k_exit is None or jc < k_exit):
            cl = g["c"][i0 + jc]
            if rl <= cl <= rh: k_exit, px = jc, cl
    if k_exit is None: k_exit, px = j_end - 1 - i0, g["c"][j_end - 1]
    fill = px - side * hs[i0 + k_exit]
    return side * (fill - entry) / H


def rule_trades(sym, rng, ex, mult):
    g = D[sym]; a0, a1, cm = RANGES[rng]; out = []
    for d, o_m, f_m in g["days"]:
        i, j = idx(sym, o_m + a0, o_m + a1)
        if j - i < max(1, int(0.8 * (a1 - a0))) or g["m"][i] != o_m + a0: continue
        rh, rl = g["h"][i:j].max(), g["l"][i:j].min(); H = rh - rl
        if H <= 0: continue
        k, e = idx(sym, o_m + a1, f_m)
        if e - k < 2: continue
        up, dn = g["h"][k:e] > rh, g["l"][k:e] < rl
        fu = int(np.argmax(up)) if up.any() else 10**9; fd = int(np.argmax(dn)) if dn.any() else 10**9
        if fu == fd == 10**9 or fu == fd: continue
        side = 1 if fu < fd else -1; i0 = k + min(fu, fd)
        lvl, stop, tp = (rh, rl, rh + H) if side > 0 else (rl, rh, rl - H)
        xc = None
        if ex == "XC":
            em = g["m"][i0]; ce = o_m + a1 + ((em - (o_m + a1)) // cm + 1) * cm; xc = (ce, rh, rl)
        out.append((d.year, manage(sym, side, i0, e, lvl, stop, tp, H, mult, xc), d, H, o_m + a1, f_m))
    return out


def summ(rs):
    r = np.array(rs); return dict(trades=int(len(r)), mean_R=round(float(r.mean()), 4) if len(r) else None, net_R=round(float(r.sum()), 2),
                                  win_rate=round(float((r > 0).mean()), 3) if len(r) else None)


def job(args):
    sym, rng, ex = args; setup(sym); res = {}
    for mult in (1, 2):
        tr = rule_trades(sym, rng, ex, mult)
        res[f"x{mult}"] = {p: summ([r for y, r, *_ in tr if (y == 2025) == (p == "dev")]) for p in ("dev", "holdout")}
    if ex == "X0":                                                           # random control depends only on market and range
        tr = rule_trades(sym, rng, "X0", 2); rs = np.random.default_rng(SEED + zlib.crc32(f"{sym}|{rng}".encode()) % 1000)
        draws = {"dev": [], "holdout": []}; g = D[sym]
        for _ in range(N_RANDOM):
            acc = {"dev": [], "holdout": []}
            for y, _, d, H, start_m, f_m in tr:
                k, e = idx(sym, start_m, f_m - 30)
                if e - k < 1: continue
                i0 = k + int(rs.integers(0, e - k)); side = 1 if rs.random() < 0.5 else -1; _, e2 = idx(sym, start_m, f_m)
                lvl = g["o"][i0]; acc["dev" if y == 2025 else "holdout"].append(manage(sym, side, i0, e2, lvl, lvl - side * H, lvl + side * H, H, 2))
            for p in acc: draws[p].append(np.mean(acc[p]) if acc[p] else 0.0)
        res["random_x2_p95"] = {p: round(float(np.percentile(v, 95)), 4) for p, v in draws.items()}
        res["random_x2_p50"] = {p: round(float(np.percentile(v, 50)), 4) for p, v in draws.items()}
    return sym, rng, ex, res


def main():
    t0 = time.time(); jobs = [(s, r, e) for s in MARKETS for r in RANGES for e in EXITS]
    with Pool(4) as p: res = p.map(job, jobs)
    R = {f"{s}|{r}|{e}": v for s, r, e, v in res}
    for s in MARKETS:
        for r in RANGES: R[f"{s}|{r}|XC"]["random_x2_p95"] = R[f"{s}|{r}|X0"]["random_x2_p95"]; R[f"{s}|{r}|XC"]["random_x2_p50"] = R[f"{s}|{r}|X0"]["random_x2_p50"]
    for k, v in R.items():
        d2, h2, p95 = v["x2"]["dev"], v["x2"]["holdout"], v["random_x2_p95"]
        ok = (d2["mean_R"] or -1) > 0 and (h2["mean_R"] or -1) > 0 and h2["trades"] >= 100 and d2["mean_R"] > p95["dev"] and h2["mean_R"] > p95["holdout"]
        v["verdict"] = "PASS" if ok else "FAIL"
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results=R, n_pass=sum(v["verdict"] == "PASS" for v in R.values()))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print("combo | dev x1 | dev x2 | hold x1 | hold x2 (mean R, trades, win) | random p95 dev/hold | verdict")
    for k, v in R.items():
        f = lambda s: f"{s['mean_R']:+.3f} n{s['trades']} w{s['win_rate']}" if s["mean_R"] is not None else "n0"
        print(k, "|", f(v["x1"]["dev"]), "|", f(v["x2"]["dev"]), "|", f(v["x1"]["holdout"]), "|", f(v["x2"]["holdout"]), "|", v["random_x2_p95"], "|", v["verdict"])
    print("PASS count:", out["n_pass"], f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
