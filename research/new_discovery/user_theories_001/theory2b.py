"""Theory #2b: zones from the SAME day's opening range (22:00-07:00 UTC) + 15-minute signal candle. Implements PREREG.md test A.
Copied from the frozen research/zone_reversal_study/study.py; ONLY the range (opening range instead of previous day) and the
signal window (from 07:00 UTC) differ.

Usage: BARS_DIR=<dir with <sym>_1m.npz from ../orb_study/build_bars.py> python3 -I study.py
"""
import json, os, time, zlib
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); BARS = os.environ["BARS_DIR"]
MARKETS = ("XAUUSDm", "USOILm", "DE30m", "US500m", "USTECm"); ZONES = ("Z50", "Z25"); SIGNALS = ("S1", "S2"); TARGETS = ("T1", "T2", "TM")
N_RANDOM = 500; SEED = 20261112; NO_ENTRY_AFTER = 20 * 60; OR_END = 7 * 60; G = {}


def load(sym):
    z = np.load(os.path.join(BARS, f"{sym}_1m.npz")); m = z["m"]
    g = dict(m=m, o=z["o"], h=z["h"], l=z["l"], c=z["c"], hs=z["sp"] / 2, day=(m + 120) // 1440)
    b = m // 15; st = np.flatnonzero(np.r_[True, b[1:] != b[:-1]]); en = np.r_[st[1:], len(m)]
    g["c15"] = dict(start=b[st] * 15, i0=st, i1=en, o=g["o"][st], h=np.maximum.reduceat(g["h"], st), l=np.minimum.reduceat(g["l"], st), c=g["c"][en - 1], day=g["day"][st])
    # opening range: bars of trading day d (starts 22:00 UTC of the previous date) with UTC time < 07:00 on date d
    in_or = ((m % 1440) < OR_END) | ((m % 1440) >= 22 * 60)
    rng = {}
    for d in np.unique(g["day"]):
        sel = np.flatnonzero((g["day"] == d) & in_or)
        if len(sel) >= 120: rng[int(d)] = (float(g["h"][sel].max()), float(g["l"][sel].min()))
    g["prev"] = rng; G[sym] = g


def manage(g, side, i0, j_end, entry_lvl, stop, tp, R, mult):
    hs = g["hs"] * mult; entry = entry_lvl + side * hs[i0]
    lo, hi = g["l"][i0:j_end], g["h"][i0:j_end]
    hs_ = (lo <= stop) if side > 0 else (hi >= stop); ht = (hi >= tp) if side > 0 else (lo <= tp)
    s = int(np.argmax(hs_)) if hs_.any() else 10**9; t = int(np.argmax(ht)) if ht.any() else 10**9
    if s <= t and s < 10**9: k, px = s, stop
    elif t < 10**9: k, px = t, tp
    else: k, px = j_end - 1 - i0, g["c"][j_end - 1]
    return side * ((px - side * hs[i0 + k]) - entry) / R, i0 + k


def day_end_idx(g, day):
    return int(np.searchsorted(g["m"], (day + 1) * 1440 - 120 - 5))


def trades(sym, zone, sig, tgt, mult):
    g = G[sym]; c = g["c15"]; n = len(c["start"]); out = []; free_from = -1
    for q in range(n - 1):
        if c["i0"][q] < free_from: continue
        d = int(c["day"][q]); pr = g["prev"].get(d)
        if pr is None or c["day"][q + 1] != d or ((c["start"][q + 1] + 120) % 1440) > NO_ENTRY_AFTER + 120: continue
        if not (OR_END <= c["start"][q] % 1440 < 22 * 60): continue           # signal candle opens at/after 07:00 UTC (range complete)
        ph, pl = pr; w = ph - pl
        if w <= 0: continue
        o, h, l, cl = c["o"][q], c["h"][q], c["l"][q], c["c"][q]
        long_area = cl < pl + (0.5 if zone == "Z50" else 0.25) * w; short_area = cl > (pl + 0.5 * w if zone == "Z50" else ph - 0.25 * w)
        body = abs(cl - o)
        if sig == "S1": lg, sh = long_area and cl > o, short_area and cl < o
        else: lg, sh = long_area and cl > o and (min(o, cl) - l) >= 2 * body, short_area and cl < o and (h - max(o, cl)) >= 2 * body
        if not (lg or sh): continue
        side = 1 if lg else -1; i0 = int(c["i0"][q + 1]); lvl = g["o"][i0]; stop = l if side > 0 else h; R = side * (lvl - stop)
        if R <= 2 * 2 * g["hs"][i0]: continue
        if tgt == "TM":
            tp = pl + 0.5 * w
            if side * (tp - lvl) <= 0: continue
        else: tp = lvl + side * R * (1 if tgt == "T1" else 2)
        e = day_end_idx(g, d)
        if e - i0 < 2: continue
        r, k = manage(g, side, i0, e, lvl, stop, tp, R, mult); free_from = k + 1
        out.append((d, r, R, abs(tp - lvl), i0, e))
    return out


def summ(rs):
    r = np.array(rs); return dict(trades=int(len(r)), mean_R=round(float(r.mean()), 4) if len(r) else None, net_R=round(float(r.sum()), 2), win_rate=round(float((r > 0).mean()), 3) if len(r) else None)


def period(d):  # trading-day number -> "dev" (2025) / "holdout" (2026)
    return "dev" if d * 1440 * 60 < 1767225600 else "holdout"


def job(args):
    sym, zone, sig, tgt = args; load(sym); g = G[sym]; res = {}
    for mult in (1, 2):
        tr = trades(sym, zone, sig, tgt, mult); res[f"x{mult}"] = {p: summ([r for d, r, *_ in tr if period(d) == p]) for p in ("dev", "holdout")}
    rs = np.random.default_rng(SEED + zlib.crc32(f"{sym}|{zone}|{sig}|{tgt}".encode()) % 1000); draws = {"dev": [], "holdout": []}; c = g["c15"]
    ok = (((c["start"] + 120) % 1440) <= NO_ENTRY_AFTER + 120) & ((c["start"] % 1440) >= OR_END + 15) & ((c["start"] % 1440) < 22 * 60); cands = {}
    for d in {t[0] for t in tr}: cands[d] = np.flatnonzero((c["day"] == d) & ok)      # computed once per day (same set as before)
    for _ in range(N_RANDOM):
        acc = {"dev": [], "holdout": []}
        for d, _, R, tdist, _, e in tr:
            cand = cands[d]
            if not len(cand): continue
            i0 = int(c["i0"][cand[int(rs.integers(0, len(cand)))]])
            if e - i0 < 2: continue
            side = 1 if rs.random() < 0.5 else -1; lvl = g["o"][i0]
            r, _ = manage(g, side, i0, e, lvl, lvl - side * R, lvl + side * tdist, R, 2); acc[period(d)].append(r)
        for p in acc: draws[p].append(np.mean(acc[p]) if acc[p] else 0.0)
    res["random_x2_p95"] = {p: round(float(np.percentile(v, 95)), 4) for p, v in draws.items()}
    d2, h2, p95 = res["x2"]["dev"], res["x2"]["holdout"], res["random_x2_p95"]
    res["verdict"] = "PASS" if ((d2["mean_R"] or -1) > 0 and (h2["mean_R"] or -1) > 0 and h2["trades"] >= 100 and d2["mean_R"] > p95["dev"] and h2["mean_R"] > p95["holdout"]) else "FAIL"
    return "|".join(args), res


def main():
    t0 = time.time(); jobs = [(s, z, q, t) for s in MARKETS for z in ZONES for q in SIGNALS for t in TARGETS]
    with Pool(4) as p: R = dict(p.map(job, jobs))
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results=R, n_pass=sum(v["verdict"] == "PASS" for v in R.values()))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    f = lambda s: f"{s['mean_R']:+.3f} n{s['trades']} w{s['win_rate']}" if s["mean_R"] is not None else "n0"
    for k, v in R.items(): print(k, "|", f(v["x1"]["dev"]), "|", f(v["x2"]["dev"]), "|", f(v["x1"]["holdout"]), "|", f(v["x2"]["holdout"]), "|", v["random_x2_p95"], "|", v["verdict"])
    print("PASS count:", out["n_pass"], f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
