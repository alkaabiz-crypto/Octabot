"""ORB second interpretation set. Implements PREREG_V2.md. Reuses the bar engine (idx, manage) from study.py.

Usage: BARS_DIR=<orb bars> python3 -I study_v2.py
"""
import importlib.util, json, os, time, zlib
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("orb_main", os.path.join(HERE, "study.py")); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
OPENS = {"DE30m": ("DE30m", "Europe/Berlin", (9, 0), (17, 30)), "US500m": ("US500m", "America/New_York", (9, 30), (16, 0)),
         "USTECm": ("USTECm", "America/New_York", (9, 30), (16, 0)), "XAUUSDm": ("XAUUSDm", "America/New_York", (8, 20), (13, 30)),
         "USOILm": ("USOILm", "America/New_York", (9, 0), (14, 30)), "XAU_NY0930": ("XAUUSDm", "America/New_York", (9, 30), (16, 0)),
         "OIL_NY0930": ("USOILm", "America/New_York", (9, 30), (16, 0)), "XAU_LDN0800": ("XAUUSDm", "Europe/London", (8, 0), (16, 30))}
NEW = ("XAU_NY0930", "OIL_NY0930", "XAU_LDN0800")


def setup(key):
    sym, tz, op, fx = OPENS[key]; z = np.load(os.path.join(M.BARS, f"{sym}_1m.npz"))
    M.D[key] = dict(m=z["m"], o=z["o"], h=z["h"], l=z["l"], c=z["c"], hs=z["sp"] / 2,
                    days=[(d, M.minute(d, op, tz), M.minute(d, fx, tz)) for d in M.DAYS])


def close_trades(key, rng, mult):
    g = M.D[key]; a0, a1, cm = M.RANGES[rng]; out = []
    for d, o_m, f_m in g["days"]:
        i, j = M.idx(key, o_m + a0, o_m + a1)
        if j - i < max(1, int(0.8 * (a1 - a0))) or g["m"][i] != o_m + a0: continue
        rh, rl = g["h"][i:j].max(), g["l"][i:j].min()
        if rh <= rl: continue
        k, e = M.idx(key, o_m + a1, f_m)
        if e - k < 3: continue
        mm = g["m"][k:e]; cid = (mm - (o_m + a1)) // cm
        last = np.flatnonzero(np.r_[cid[1:] != cid[:-1], True])            # last bar of each candle
        cl = g["c"][k:e][last]; cend = o_m + a1 + (cid[last] + 1) * cm
        sig = np.flatnonzero(((cl > rh) | (cl < rl)) & (cend < f_m - 1))
        if not len(sig): continue
        s = sig[0]; side = 1 if cl[s] > rh else -1
        i0 = int(np.searchsorted(g["m"], cend[s]))
        if i0 >= e: continue
        lvl = g["o"][i0]; stop = rl if side > 0 else rh; risk = side * (lvl - stop)
        if risk <= 0: continue
        out.append((d.year, M.manage(key, side, i0, e, lvl, stop, lvl + side * risk, risk, mult), d, risk, o_m + a1, f_m))
    return out


def random_p(key, rng, tr):
    g = M.D[key]; rs = np.random.default_rng(M.SEED + zlib.crc32(f"{key}|{rng}|v2".encode()) % 1000); draws = {"dev": [], "holdout": []}
    for _ in range(M.N_RANDOM):
        acc = {"dev": [], "holdout": []}
        for y, _, d, H, start_m, f_m in tr:
            k, e = M.idx(key, start_m, f_m - 30)
            if e - k < 1: continue
            i0 = k + int(rs.integers(0, e - k)); side = 1 if rs.random() < 0.5 else -1; _, e2 = M.idx(key, start_m, f_m); lvl = g["o"][i0]
            acc["dev" if y == 2025 else "holdout"].append(M.manage(key, side, i0, e2, lvl, lvl - side * H, lvl + side * H, H, 2))
        for p in acc: draws[p].append(np.mean(acc[p]) if acc[p] else 0.0)
    return {p: round(float(np.percentile(v, 95)), 4) for p, v in draws.items()}


def job(args):
    key, rng, mode = args; setup(key); res = {}
    if mode == "CLOSE":
        for mult in (1, 2):
            tr = close_trades(key, rng, mult); res[f"x{mult}"] = {p: M.summ([r for y, r, *_ in tr if (y == 2025) == (p == "dev")]) for p in ("dev", "holdout")}
        res["random_x2_p95"] = random_p(key, rng, close_trades(key, rng, 2))
    else:
        ex = mode.split("_")[1]
        for mult in (1, 2):
            tr = M.rule_trades(key, rng, ex, mult); res[f"x{mult}"] = {p: M.summ([r for y, r, *_ in tr if (y == 2025) == (p == "dev")]) for p in ("dev", "holdout")}
        res["random_x2_p95"] = random_p(key, rng, M.rule_trades(key, rng, "X0", 2))
    return f"{key}|{rng}|{mode}", res


def main():
    t0 = time.time()
    jobs = [(k, r, "CLOSE") for k in OPENS for r in M.RANGES] + [(k, r, m) for k in NEW for r in M.RANGES for m in ("TOUCH_X0", "TOUCH_XC")]
    with Pool(4) as p: R = dict(p.map(job, jobs))
    for k, v in R.items():
        d2, h2, p95 = v["x2"]["dev"], v["x2"]["holdout"], v["random_x2_p95"]
        v["verdict"] = "PASS" if ((d2["mean_R"] or -1) > 0 and (h2["mean_R"] or -1) > 0 and h2["trades"] >= 100 and d2["mean_R"] > p95["dev"] and h2["mean_R"] > p95["holdout"]) else "FAIL"
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results=R, n_pass=sum(v["verdict"] == "PASS" for v in R.values()))
    json.dump(out, open(os.path.join(HERE, "results", "results_v2.json"), "w"), indent=1)
    f = lambda s: f"{s['mean_R']:+.3f} n{s['trades']} w{s['win_rate']}" if s["mean_R"] is not None else "n0"
    for k, v in R.items(): print(k, "|", f(v["x1"]["dev"]), "|", f(v["x2"]["dev"]), "|", f(v["x1"]["holdout"]), "|", f(v["x2"]["holdout"]), "|", v["random_x2_p95"], "|", v["verdict"])
    print("PASS count:", out["n_pass"], f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
