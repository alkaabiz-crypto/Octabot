"""Wide optimisation of the user's oil DCA bot with monthly walk-forward validation. Implements PREREGISTRATION.md.

Usage: TICK_DIR=... CACHE_DIR=... python3 -I optimize.py
"""
import itertools, json, math, os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
START, END = "2025-11-01", "2026-11-01"
MONTH_STARTS = pd.date_range(START, END, freq="MS", tz="UTC")
MB = np.array([int(x.as_unit("ns").value // 1_000_000) for x in MONTH_STARTS])        # 13 boundaries
TPS = [0.15, 0.30, 0.60, 1.00, 1.50]; TRAILS = [0.0, 0.04]; STOPS = [25.0, 50.0, 100.0, 200.0]; STEPS0 = [0.63, 1.00, 1.50, 2.50]
DIRS = ["rating", "rating+trend", "trend", "fade"]; ALWAYS = ["always_buy", "always_sell"]; TFS = ["15m", "1h"]
BARRELS = 1000
G = {}


def extras_options():
    out = [dict(extra=0, step=None, amult=None)]
    out += [dict(extra=1, step=s, amult=1.0) for s in STEPS0]
    for n in (2, 3):
        out += [dict(extra=n, step=s, amult=a) for s in STEPS0 for a in (1.0, 1.5)]
    return out


def lots_steps(c):
    lots = [0.01]
    for k in range(c["extra"]): lots.append(math.floor(0.02 * c["amult"] ** k * 100 + 1e-9) / 100)
    steps = [c["step"] * 1.3 ** k for k in range(c["extra"])]
    return lots, steps


def basket(t, bid, ask, i0, side, stop_usd, lots, steps, tp, trail):
    n = len(t); ent = ask if side > 0 else bid; ext = bid if side > 0 else ask
    fills = [(lots[0], float(ent[i0]))]; levels = []; lvl = fills[0][1]
    for s in steps: lvl -= side * s; levels.append(lvl)
    i = i0 + 1; worst = 0.0
    while True:
        L = sum(x for x, _ in fills); avg = sum(x * p for x, p in fills) / L
        tp_px = avg + side * tp; stop_px = avg - side * stop_usd / (BARRELS * L)
        nxt = levels[len(fills) - 1] if len(fills) < len(lots) else None
        def m(a, b):
            e = ext[a:b]; mk = ((e - tp_px) * side >= 0) | ((e - stop_px) * side <= 0)
            if nxt is not None: mk |= (ent[a:b] - nxt) * side <= 0
            return mk
        j = bot.first(m, i, n); se = n if j is None else j + 1
        if se > i:
            adv = ext[i:se].min() if side > 0 else ext[i:se].max(); worst = min(worst, (adv - avg) * side * BARRELS * L)
        if j is None: return (ext[n - 1] - avg) * side * BARRELS * L, n - 1, worst
        if (ext[j] - stop_px) * side <= 0: return (ext[j] - avg) * side * BARRELS * L, j, worst
        if (ext[j] - tp_px) * side >= 0:
            if trail == 0: return (tp_px - avg) * side * BARRELS * L, j, worst          # plain TP: limit fill at the level
            k = j; bp = None
            while True:
                b2 = min(n, k + 4096); seg = ext[k:b2]
                best = np.maximum.accumulate(seg) if side > 0 else np.minimum.accumulate(seg)
                if bp is not None: best = np.maximum(best, bp) if side > 0 else np.minimum(best, bp)
                hit = (best - seg) * side >= trail
                if hit.any():
                    x = k + int(np.argmax(hit)); return (ext[x] - avg) * side * BARRELS * L, x, worst
                if b2 >= n: return (ext[n - 1] - avg) * side * BARRELS * L, n - 1, worst
                bp = best[-1]; k = b2
        fills.append((lots[len(fills)], nxt)); i = j + 1


def run(c):
    t, b, a = G["ticks"]; closes = G["closes"][c["tf"]]; dirs = G["dirs"][(c["tf"], c["dir"])]
    lots, steps = lots_steps(c); pos = np.searchsorted(t, closes, side="left")
    cm, pn, wo = [], [], []; k = 0
    while k < len(closes):
        if dirs[k] == 0: k += 1; continue
        i0 = pos[k]
        if i0 >= len(t) or t[i0] - closes[k] > 60_000: k += 1; continue
        pnl, x, worst = basket(t, b, a, i0, int(dirs[k]), c["stop"], lots, steps, c["tp"], c["trail"])
        cm.append(int(t[x])); pn.append(pnl); wo.append(worst)
        k = int(np.searchsorted(closes, t[x], side="right"))
    return np.array(cm, dtype=np.int64), np.array(pn), np.array(wo)


def dd_of(pn, wo):
    eq = peak = dd = 0.0
    for p, w in zip(pn, wo):
        dd = max(dd, peak - (eq + w)); eq += p; peak = max(peak, eq); dd = max(dd, peak - eq)
    return dd


def job(c):
    cm, pn, wo = run(c)
    mi = np.searchsorted(MB, cm, side="right") - 1                                   # month index 0..11
    monthly = [float(pn[mi == m].sum()) for m in range(12)]; counts = [int((mi == m).sum()) for m in range(12)]
    folds = []
    for m in range(3, 12):
        tr = (mi >= m - 3) & (mi < m); n = int(tr.sum()); net = float(pn[tr].sum()); dd = dd_of(pn[tr], wo[tr])
        folds.append(dict(train_n=n, train_net=net, train_dd=dd, test_net=monthly[m], test_n=counts[m],
                          test_dd=dd_of(pn[mi == m], wo[mi == m])))
    return dict(cfg=c, net=float(pn.sum()), dd=dd_of(pn, wo), baskets=len(pn), win_rate=float((pn > 0).mean()) if len(pn) else None,
                monthly=monthly, quarters=[sum(monthly[q * 3:(q + 1) * 3]) for q in range(4)], folds=folds)


def prepare():
    t, bid, ask, q = bot.load()
    c4 = bot.candles(t, bid, bot.H4_MS); c4["ema"] = c4.c.ewm(span=200, adjust=False).mean(); c4.loc[c4.index < 200, "ema"] = np.nan
    s, e = MB[0], MB[-1]
    G["closes"], G["dirs"] = {}, {}
    for tf, tfms in (("15m", bot.TF_MS), ("1h", 3_600_000)):
        c = bot.candles(t, bid, tfms); r = bot.rating(c)
        idx = np.searchsorted(c4.close_ms.values, c.close_ms.values, side="right") - 1
        ema = np.where(idx >= 0, c4.ema.values[np.clip(idx, 0, None)], np.nan)
        sel = (c.close_ms.values > s) & (c.close_ms.values <= e) & ~np.isnan(r) & ~np.isnan(ema)
        G["closes"][tf] = c.close_ms.values[sel]
        d = np.where(r[sel] > 0.1, 1, np.where(r[sel] < -0.1, -1, 0)); tr = np.where(c.c.values[sel] > ema[sel], 1, -1)
        G["dirs"][(tf, "rating")] = d; G["dirs"][(tf, "rating+trend")] = np.where(d == tr, d, 0)
        G["dirs"][(tf, "trend")] = tr; G["dirs"][(tf, "fade")] = -d
        G["dirs"][(tf, "always_buy")] = np.ones_like(d); G["dirs"][(tf, "always_sell")] = -np.ones_like(d)
    i0, i1 = np.searchsorted(t, s), np.searchsorted(t, e)
    G["ticks"] = (t[i0:i1], bid[i0:i1], ask[i0:i1])
    return q


def main():
    t0 = time.time(); q = prepare()
    grid = []
    for tp, tr, ex, st in itertools.product(TPS, TRAILS, extras_options(), STOPS):
        base = dict(tp=tp, trail=tr, stop=st, **ex)
        for d, tf in itertools.product(DIRS, TFS): grid.append(dict(base, dir=d, tf=tf))
        for d in ALWAYS: grid.append(dict(base, dir=d, tf="15m"))
    assert len(grid) == 8400, len(grid)
    print(f"prepared {time.time() - t0:.0f}s grid {len(grid)}", flush=True)
    out = []
    with Pool(4) as p:
        for k, r in enumerate(p.imap_unordered(job, grid, chunksize=8)):
            out.append(r)
            if (k + 1) % 500 == 0: print(f"  {k + 1}/{len(grid)} {time.time() - t0:.0f}s", flush=True)
    # walk-forward
    wf = []
    for f, m in enumerate(range(3, 12)):
        cands = [r for r in out if r["folds"][f]["train_n"] >= 30 and r["folds"][f]["train_dd"] > 0]
        best = max(cands, key=lambda r: (r["folds"][f]["train_net"] / r["folds"][f]["train_dd"], r["folds"][f]["train_net"]))
        fo = best["folds"][f]
        wf.append(dict(test_month=str(MONTH_STARTS[m].date())[:7], chosen=best["cfg"], train_net=round(fo["train_net"], 2), train_dd=round(fo["train_dd"], 2),
                       test_net=round(fo["test_net"], 2), test_baskets=fo["test_n"], test_dd_within_month=round(fo["test_dd"], 2)))
    oos = np.array([w["test_net"] for w in wf]); eq = np.cumsum(oos)
    oos_dd = float(max(0.0, np.max(np.maximum.accumulate(np.r_[0, eq]) - np.r_[0, eq])))
    oos_dd = max(oos_dd, max(w["test_dd_within_month"] for w in wf))
    checks = dict(oos_net_positive=bool(oos.sum() > 0), at_least_6_of_9_months_positive=bool((oos > 0).sum() >= 6),
                  oos_dd_below_2x_net=bool(oos_dd < 2 * oos.sum()) if oos.sum() > 0 else False)
    df = pd.DataFrame([dict(**r["cfg"], net=round(r["net"], 2), dd=round(r["dd"], 2), baskets=r["baskets"], win_rate=r["win_rate"],
                            **{f"q{i + 1}": round(v, 2) for i, v in enumerate(r["quarters"])}) for r in out])
    df["worst_quarter"] = df[["q1", "q2", "q3", "q4"]].min(axis=1)
    res = dict(generated_utc=bot.fmt(int(time.time() * 1000)), grid_size=len(grid), data_months=list(q),
               walk_forward=wf, oos_net=round(float(oos.sum()), 2), oos_positive_months=int((oos > 0).sum()), oos_max_dd=round(oos_dd, 2),
               checks=checks, PASS=bool(all(checks.values())),
               descriptive_in_sample=dict(
                   share_profitable_full_year=round(float((df.net > 0).mean()), 4),
                   share_profitable_all_4_quarters=round(float((df.worst_quarter > 0).mean()), 4),
                   best_full_year=df.sort_values("net", ascending=False).head(5).to_dict("records"),
                   best_worst_quarter=df.sort_values("worst_quarter", ascending=False).head(5).to_dict("records"),
                   median_net_by={g: df.groupby(g).net.median().round(1).to_dict() for g in ("tp", "trail", "extra", "stop", "dir", "tf")},
                   chosen_frequency={g: pd.Series([w["chosen"][g] for w in wf]).astype(str).value_counts().to_dict() for g in ("tp", "trail", "extra", "stop", "dir", "tf")}))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    df.to_csv(os.path.join(HERE, "results", "all_settings.csv"), index=False)
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print(json.dumps(dict(wf=[(w["test_month"], w["test_net"]) for w in wf], oos_net=res["oos_net"], checks=checks, PASS=res["PASS"])), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
