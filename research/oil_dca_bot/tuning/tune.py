"""Settings search for the user's oil DCA bot with an out-of-sample test. Implements PREREGISTRATION.md (this folder).

Usage: TICK_DIR=... CACHE_DIR=... python3 -I tune.py
"""
import itertools, json, os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402  (data loading, candles, rating, helpers; bot.py itself is unchanged)

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = ("2025-11-01", "2026-05-01"); TEST = ("2026-05-01", "2026-11-01")
TPS = [0.15, 0.30, 0.60, 1.00]; EXTRAS = [0, 1, 2]; STEPS0 = [0.63, 1.00, 1.50]; STOPS = [25.0, 50.0, 100.0]
DIRS = ["rating", "rating+trend"]; TFS = ["15m", "1h"]
TRAIL, BARRELS, N_RANDOM, SEED = 0.04, 1000, 200, 20261111
G = {}


def ms(x): return int(pd.Timestamp(x, tz="UTC").as_unit("ns").value // 1_000_000)


def basket(t, bid, ask, i0, side, stop_usd, lots, steps, tp):
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
            k = j; bp = None
            while True:
                b2 = min(n, k + 4096); seg = ext[k:b2]
                best = np.maximum.accumulate(seg) if side > 0 else np.minimum.accumulate(seg)
                if bp is not None: best = np.maximum(best, bp) if side > 0 else np.minimum(best, bp)
                hit = (best - seg) * side >= TRAIL
                if hit.any():
                    x = k + int(np.argmax(hit)); return (ext[x] - avg) * side * BARRELS * L, x, worst
                if b2 >= n: return (ext[n - 1] - avg) * side * BARRELS * L, n - 1, worst
                bp = best[-1]; k = b2
        fills.append((lots[len(fills)], nxt)); i = j + 1


def run(period, tf, dirs, cfg):
    t, b, a = G["ticks"][period]; closes = G["closes"][(period, tf)]
    lots = [0.01, 0.02, 0.03][:1 + cfg["extra"]]; steps = [cfg["step"], cfg["step"] * 1.3][:cfg["extra"]] if cfg["extra"] else []
    pos = np.searchsorted(t, closes, side="left")
    eq = peak = dd = gp = 0.0; nb = wins = 0; k = 0
    while k < len(closes):
        if dirs[k] == 0: k += 1; continue
        i0 = pos[k]
        if i0 >= len(t) or t[i0] - closes[k] > 60_000: k += 1; continue
        pnl, x, worst = basket(t, b, a, i0, int(dirs[k]), cfg["stop"], lots, steps, cfg["tp"])
        dd = max(dd, peak - (eq + worst)); eq += pnl; peak = max(peak, eq); dd = max(dd, peak - eq)
        nb += 1; wins += pnl > 0; gp += max(pnl, 0)
        k = int(np.searchsorted(closes, t[x], side="right"))
    return dict(net=round(eq, 2), maxdd=round(dd, 2), gross_profit=round(gp, 2), baskets=nb, win_rate=round(wins / nb, 4) if nb else None)


def job(args):
    period, cfg = args
    return cfg, run(period, cfg["tf"], G["dirs"][(period, cfg["tf"], cfg["dir"])], cfg)


def rand_job(args):
    cfg, seed = args
    rng = np.random.default_rng(seed); n = len(G["closes"][("test", cfg["tf"])])
    return run("test", cfg["tf"], rng.choice([-1, 1], size=n), cfg)["net"]


def prepare():
    t, bid, ask, q = bot.load()
    c4 = bot.candles(t, bid, bot.H4_MS); c4["ema"] = c4.c.ewm(span=200, adjust=False).mean(); c4.loc[c4.index < 200, "ema"] = np.nan
    for tf, tfms in (("15m", bot.TF_MS), ("1h", 3_600_000)):
        c = bot.candles(t, bid, tfms); r = bot.rating(c)
        idx = np.searchsorted(c4.close_ms.values, c.close_ms.values, side="right") - 1
        ema = np.where(idx >= 0, c4.ema.values[np.clip(idx, 0, None)], np.nan)
        for period, (s, e) in (("train", TRAIN), ("test", TEST)):
            sel = (c.close_ms.values > ms(s)) & (c.close_ms.values <= ms(e)) & ~np.isnan(r)
            G["closes"][(period, tf)] = c.close_ms.values[sel]
            d = np.where(r[sel] > 0.1, 1, np.where(r[sel] < -0.1, -1, 0)); cl = c.c.values[sel]; em = ema[sel]
            G["dirs"][(period, tf, "rating")] = d
            G["dirs"][(period, tf, "rating+trend")] = np.where(np.isnan(em), 0, np.where((d > 0) & (cl > em), 1, np.where((d < 0) & (cl < em), -1, 0)))
    for period, (s, e) in (("train", TRAIN), ("test", TEST)):
        i0, i1 = np.searchsorted(t, ms(s)), np.searchsorted(t, ms(e))
        G["ticks"][period] = (t[i0:i1], bid[i0:i1], ask[i0:i1])


def main():
    t0 = time.time()
    G.update(closes={}, dirs={}, ticks={}); prepare()
    grid = []
    for tp, extra, stop, d, tf in itertools.product(TPS, EXTRAS, STOPS, DIRS, TFS):
        for step in ([None] if extra == 0 else STEPS0):
            grid.append(dict(tp=tp, extra=extra, step=step, stop=stop, dir=d, tf=tf))
    assert len(grid) == 336, len(grid)
    print(f"prepared {time.time() - t0:.0f}s; grid {len(grid)}", flush=True)
    with Pool(4) as p:
        train = p.map(job, [("train", c) for c in grid]); print(f"train done {time.time() - t0:.0f}s", flush=True)
        test = p.map(job, [("test", c) for c in grid]); print(f"test done {time.time() - t0:.0f}s", flush=True)
        rows = [dict(**c, **{f"train_{k}": v for k, v in tr.items()}, **{f"test_{k}": v for k, v in te.items()}) for (c, tr), (_, te) in zip(train, test)]
        df = pd.DataFrame(rows).sort_values(["train_net", "train_maxdd"], ascending=[False, True]).reset_index(drop=True)
        chosen = df.iloc[0].to_dict(); cfg = {k: chosen[k] for k in ("tp", "extra", "step", "stop", "dir", "tf")}
        if pd.isna(cfg["step"]): cfg["step"] = None
        cfg["extra"] = int(cfg["extra"])
        rnd = np.array(p.map(rand_job, [(cfg, SEED + i) for i in range(N_RANDOM)]))
    checks = dict(test_net_positive=bool(chosen["test_net"] > 0), test_dd_below_half_gross=bool(chosen["test_maxdd"] < 0.5 * chosen["test_gross_profit"]),
                  test_beats_random_p95=bool(chosen["test_net"] > np.percentile(rnd, 95)))
    res = dict(generated_utc=bot.fmt(int(time.time() * 1000)), train=TRAIN, test=TEST, grid_size=len(grid), chosen=chosen,
               random_test=dict(runs=N_RANDOM, median=round(float(np.median(rnd)), 2), p5=round(float(np.percentile(rnd, 5)), 2), p95=round(float(np.percentile(rnd, 95)), 2)),
               checks=checks, PASS=bool(all(checks.values())),
               top10_train=df.head(10).to_dict("records"),
               share_profitable=dict(train=round(float((df.train_net > 0).mean()), 4), test=round(float((df.test_net > 0).mean()), 4),
                                     both=round(float(((df.train_net > 0) & (df.test_net > 0)).mean()), 4)),
               original_settings=df[(df.tp == 0.15) & (df.extra == 2) & (df.step == 0.63) & (df.stop == 50.0) & (df.tf == "15m")].to_dict("records"),
               best_test_in_hindsight=df.sort_values("test_net", ascending=False).head(3).to_dict("records"))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    df.to_csv(os.path.join(HERE, "results", "grid.csv"), index=False)
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print(json.dumps(dict(chosen=chosen, checks=checks, PASS=res["PASS"], random=res["random_test"], share=res["share_profitable"]), default=str), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
