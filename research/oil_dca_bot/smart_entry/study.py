"""Oil bot smart-entry study. Implements PREREGISTRATION.md (this folder). Research only.

Usage: CACHE_DIR=<scratch screen_cache with USOILm_YYYY_MM.npz> python3 -I study.py
"""
import json, os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("TICK_DIR", "/nonexistent"); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "optimize"))
import bot  # noqa: E402  (candles, rating)
import optimize as OPT  # noqa: E402  (basket simulator with lots/steps/stop/tp/trail)

CACHE = os.environ["CACHE_DIR"]
MONTHS = [f"{y}_{m:02d}" for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
MS = lambda s: int(pd.Timestamp(s, tz="UTC").value // 10**6)
DEV, HOLD = (MS("2025-01-01"), MS("2026-01-01")), (MS("2026-01-01"), MS("2026-11-01"))
H1, H4, D1 = 3_600_000, 4 * 3_600_000, 86_400_000
EXITS = {"X1_user_grid": dict(lots=[0.01, 0.02, 0.03], steps=[0.63, 0.63 * 1.3], tp=0.15, trail=0.04, stop=50.0),
         "X2_simple": dict(lots=[0.01], steps=[], tp=1.00, trail=0.04, stop=10.0)}
ACCOUNT_USD = 2722.94; N_RANDOM = 200; SEED = 20261111
G = {}


def load():
    p = [np.load(os.path.join(CACHE, f"USOILm_{m}.npz")) for m in MONTHS]
    t = np.concatenate([x["t"] for x in p]); b = np.concatenate([x["bid"] for x in p]); a = np.concatenate([x["ask"] for x in p])
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    assert t[0] >= MS("2025-01-01")
    return t, b, a


def ema(x, n): return x.ewm(span=n, adjust=False).mean()


def rsi(c, n):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def features(t, bid):
    h1 = bot.candles(t, bid, H1); h4 = bot.candles(t, bid, H4); d1 = bot.candles(t, bid, D1)
    h4["ema200"] = ema(h4.c, 200).where(h4.index >= 199)
    i4 = np.searchsorted(h4.close_ms.values, h1.close_ms.values, side="right") - 1      # last CLOSED 4H candle
    h1["c4"] = np.where(i4 >= 0, h4.c.values[np.clip(i4, 0, None)], np.nan)
    h1["ema200_4h"] = np.where(i4 >= 0, h4.ema200.values[np.clip(i4, 0, None)], np.nan)
    up = h1.c4 > h1.ema200_4h; dn = h1.c4 < h1.ema200_4h; ok = h1.ema200_4h.notna()
    h1["trend"] = np.where(ok & up, 1, np.where(ok & dn, -1, 0))
    d1["hi20"] = d1.h.rolling(20).max(); d1["lo20"] = d1.l.rolling(20).min()
    idd = np.searchsorted(d1.close_ms.values, h1.close_ms.values, side="right") - 1     # last CLOSED daily candle
    hi = np.where(idd >= 0, d1.hi20.values[np.clip(idd, 0, None)], np.nan); lo = np.where(idd >= 0, d1.lo20.values[np.clip(idd, 0, None)], np.nan)
    h1["rangepos"] = (h1.c - lo) / (hi - lo)
    r = bot.rating(h1); e0 = np.where(r > 0.1, 1, np.where(r < -0.1, -1, 0)); e0[np.isnan(r)] = 0
    e50 = ema(h1.c, 50); r2 = rsi(h1.c, 2); hi20 = h1.c.shift(1).rolling(20).max(); lo20 = h1.c.shift(1).rolling(20).min()
    macd = ema(h1.c, 12) - ema(h1.c, 26); sig = ema(macd, 9); xup = (macd > sig) & (macd.shift() <= sig.shift()); xdn = (macd < sig) & (macd.shift() >= sig.shift())
    tr = h1.trend.values; rp = h1.rangepos.values
    E = {}
    E["E0_user_rating"] = e0
    E["E1_trend"] = tr.copy()
    E["E2_trend_mtf"] = np.where((tr == 1) & (h1.c > e50) & (e50 > e50.shift(3)), 1, np.where((tr == -1) & (h1.c < e50) & (e50 < e50.shift(3)), -1, 0))
    E["E3_pullback"] = np.where((tr == 1) & (r2 < 10), 1, np.where((tr == -1) & (r2 > 90), -1, 0))
    g = e0.copy(); g[(g == -1) & (rp < 0.2)] = 0; g[(g == 1) & (rp > 0.8)] = 0; g[g != tr] = 0; E["E4_rating_guarded"] = g
    E["E5_breakout"] = np.where((tr == 1) & (h1.c > hi20), 1, np.where((tr == -1) & (h1.c < lo20), -1, 0))
    E["E6_macd"] = np.where((tr == 1) & xup, 1, np.where((tr == -1) & xdn, -1, 0))
    for k in E: E[k] = np.asarray(E[k], dtype=int)
    return h1, E


def run(dirs, ex, spread_mult):
    t, closes, tr, rp = G["t"], G["closes"], G["trend"], G["rangepos"]
    b, a = (G["b"], G["a"]) if spread_mult == 1 else (G["b2"], G["a2"])
    pos = np.searchsorted(t, closes, side="left"); k = 0; out = []
    while k < len(closes):
        if dirs[k] == 0: k += 1; continue
        i0 = pos[k]
        if i0 >= len(t) or t[i0] - closes[k] > 300_000: k += 1; continue
        pnl, x, worst = OPT.basket(t, b, a, i0, int(dirs[k]), ex["stop"], ex["lots"], ex["steps"], ex["tp"], ex["trail"])
        out.append((int(t[i0]), int(t[x]), int(dirs[k]), pnl, worst, int(tr[k]), float(rp[k]) if not np.isnan(rp[k]) else np.nan))
        k = int(np.searchsorted(closes, t[x], side="right"))
    return out


def summarize(rows, lo, hi):
    r = [x for x in rows if lo <= x[0] < hi]
    if not r: return dict(baskets=0, net=0.0, max_dd=0.0)
    pn = np.array([x[3] for x in r]); wo = np.array([x[4] for x in r]); side = np.array([x[2] for x in r]); trd = np.array([x[5] for x in r]); rp = np.array([x[6] for x in r])
    eq = peak = dd = 0.0
    for p, w in zip(pn, wo): dd = max(dd, peak - (eq + w)); eq += p; peak = max(peak, eq); dd = max(dd, peak - eq)
    sells, buys = side == -1, side == 1
    return dict(baskets=len(r), net=round(float(pn.sum()), 2), max_dd=round(dd, 2), win_rate=round(float((pn > 0).mean()), 3),
                avg_win=round(float(pn[pn > 0].mean()), 2) if (pn > 0).any() else None, avg_loss=round(float(pn[pn <= 0].mean()), 2) if (pn <= 0).any() else None,
                sells=int(sells.sum()), buys=int(buys.sum()),
                pct_sells_at_bottom=round(float((rp[sells] < 0.2).mean()), 3) if sells.any() else None,
                pct_buys_at_top=round(float((rp[buys] > 0.8).mean()), 3) if buys.any() else None,
                pct_against_4h_trend=round(float(((trd != 0) & (side != trd)).mean()), 3))


def job(args):
    name, ex_name, m = args
    rows = run(G["E"][name], EXITS[ex_name], m)
    return name, ex_name, m, summarize(rows, *DEV), summarize(rows, *HOLD)


def rjob(args):
    ex_name, seed = args
    rng = np.random.default_rng(seed); dirs = rng.choice([-1, 1], size=len(G["closes"]))
    return ex_name, summarize(run(dirs, EXITS[ex_name], 1), *HOLD)["net"]


def main():
    t0 = time.time(); t, b, a = load(); mid = (b + a) / 2; s = a - b
    h1, E = features(t, b)
    G.update(t=t, b=b, a=a, b2=mid - s, a2=mid + s, closes=h1.close_ms.values, trend=h1.trend.values, rangepos=h1.rangepos.values, E=E)
    print(f"ticks {len(t):,}, 1H candles {len(h1)}, {time.time() - t0:.0f}s", flush=True)
    jobs = [(n, x, m) for n in E for x in EXITS for m in (1, 2)]
    with Pool(4) as p:
        res = p.map(job, jobs)
        rnd = p.map(rjob, [(x, SEED + i) for x in EXITS for i in range(N_RANDOM)])
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results={}, random_holdout={}, verdicts={})
    for n, x, m, dv, ho in res: out["results"][f"{n}|{x}|x{m}"] = dict(dev=dv, holdout=ho)
    for x in EXITS:
        v = np.array([r for e, r in rnd if e == x]); out["random_holdout"][x] = dict(median=round(float(np.median(v)), 2), p90=round(float(np.percentile(v, 90)), 2), p10=round(float(np.percentile(v, 10)), 2))
    for n in E:
        for x in EXITS:
            r1, r2 = out["results"][f"{n}|{x}|x1"], out["results"][f"{n}|{x}|x2"]
            ok = (r1["dev"]["net"] > 0 and r2["dev"]["net"] > 0 and r1["holdout"]["net"] > 0 and r2["holdout"]["net"] > 0
                  and r1["holdout"]["net"] > out["random_holdout"][x]["p90"] and r1["holdout"]["max_dd"] < 0.15 * ACCOUNT_USD and r1["holdout"]["baskets"] >= 30)
            out["verdicts"][f"{n}|{x}"] = "PASS" if ok else "FAIL"
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print(json.dumps(out["verdicts"], indent=1), json.dumps(out["random_holdout"]), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
