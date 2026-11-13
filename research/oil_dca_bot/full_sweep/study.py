"""Oil bot full sweep: 12 app entry conditions x 5 timeframes x 6 app-allowed exits. Implements PREREGISTRATION.md.

Usage: CACHE_DIR=<scratch screen_cache with USOILm npz> python3 -I study.py
"""
import importlib.util, json, os, sys, time
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("TICK_DIR", "/nonexistent")
for p in (ROOT, os.path.join(ROOT, "optimize")): sys.path.insert(0, p)
import bot  # noqa: E402


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


SE = load_mod("study", os.path.join(ROOT, "smart_entry", "study.py"))           # load, run, summarize, DEV/HOLD, G
AC = load_mod("ac_study", os.path.join(ROOT, "app_conditions", "study.py"))     # conditions()
TFS = {"15m": 900_000, "30m": 1_800_000, "1H": 3_600_000, "4H": 14_400_000, "1D": 86_400_000}
EXITS = {f"TP{tp}_SL{sl}": dict(lots=[0.01], steps=[], tp=tp / 100, trail=0.04, stop=sl / 10) for tp in (100, 200, 300) for sl in (300, 500)}
ACCOUNT_DD = 408.0; N_RANDOM = 100; SEED = 20261111
TF = {}


def use_tf(tf):
    d = TF[tf]; SE.G.update(closes=d["closes"], trend=d["zeros"], rangepos=d["nan"])


def job(args):
    tf, cond, ex, m = args; use_tf(tf)
    rows = SE.run(TF[tf]["E"][cond], EXITS[ex], m)
    return tf, cond, ex, m, SE.summarize(rows, *SE.DEV), SE.summarize(rows, *SE.HOLD)


def rjob(args):
    tf, ex, seed = args; use_tf(tf); rng = np.random.default_rng(seed)
    d = rng.choice([-1, 1], size=len(TF[tf]["closes"]))
    return tf, ex, SE.summarize(SE.run(d, EXITS[ex], 1), *SE.HOLD)["net"]


def main():
    t0 = time.time(); t, b, a = SE.load(); mid = (b + a) / 2; s = a - b
    SE.G.update(t=t, b=b, a=a, b2=mid - s, a2=mid + s)
    for tf, ms in TFS.items():
        c = bot.candles(t, b, ms); E = AC.conditions(c)
        TF[tf] = dict(closes=c.close_ms.values, E=E, zeros=np.zeros(len(c), dtype=int), nan=np.full(len(c), np.nan))
        print(f"{tf}: {len(c)} candles, {time.time() - t0:.0f}s", flush=True)
    jobs = [(tf, cond, ex, m) for tf in TFS for cond in TF[tf]["E"] for ex in EXITS for m in (1, 2)]
    with Pool(4) as p: res = p.map(job, jobs, chunksize=4)
    print(f"sweep done {len(jobs)} runs, {time.time() - t0:.0f}s", flush=True)
    R = {}
    for tf, cond, ex, m, dv, ho in res: R.setdefault((tf, cond, ex), {})[m] = dict(dev=dv, holdout=ho)
    eligible = [k for k, v in R.items() if v[2]["dev"]["baskets"] >= 30 and v[2]["dev"]["max_dd"] < ACCOUNT_DD]
    top5 = sorted(eligible, key=lambda k: -R[k][2]["dev"]["net"])[:5]
    pairs = sorted({(k[0], k[2]) for k in top5})
    with Pool(4) as p: rnd = p.map(rjob, [(tf, ex, SEED + i) for tf, ex in pairs for i in range(N_RANDOM)])
    p90 = {pr: float(np.percentile([r for tf, ex, r in rnd if (tf, ex) == pr], 90)) for pr in pairs}
    sel = []
    for k in top5:
        v = R[k]; h1, h2 = v[1]["holdout"], v[2]["holdout"]
        ok = h1["net"] > 0 and h2["net"] > 0 and h1["max_dd"] < ACCOUNT_DD and h1["baskets"] >= 30 and h1["net"] > p90[(k[0], k[2])]
        sel.append(dict(combo="|".join(k), dev_net_1x=v[1]["dev"]["net"], dev_net_2x=v[2]["dev"]["net"], dev_trades=v[1]["dev"]["baskets"], dev_dd=v[1]["dev"]["max_dd"],
                        hold_net_1x=h1["net"], hold_net_2x=h2["net"], hold_trades=h1["baskets"], hold_dd=h1["max_dd"], hold_win=h1.get("win_rate"),
                        random_p90=round(p90[(k[0], k[2])], 2), verdict="PASS" if ok else "FAIL"))
    allh = [(k, v[1]["holdout"]["net"], v[2]["holdout"]["net"], v[1]["dev"]["net"], v[2]["dev"]["net"], v[1]["holdout"]["baskets"]) for k, v in R.items()]
    both = [x for x in allh if x[3] > 0 and x[4] > 0 and x[1] > 0 and x[2] > 0 and x[5] >= 30]
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), n_combinations=len(R), selected_top5_by_2025=sel,
               share_holdout_positive_2x=round(float(np.mean([x[2] > 0 for x in allh])), 3),
               n_positive_all_four=len(both), positive_all_four=[dict(combo="|".join(x[0]), hold_1x=x[1], hold_2x=x[2], dev_1x=x[3], dev_2x=x[4], hold_trades=x[5]) for x in sorted(both, key=lambda z: -z[2])],
               by_timeframe_median_holdout_2x={tf: round(float(np.median([x[2] for x in allh if x[0][0] == tf])), 2) for tf in TFS},
               by_condition_median_holdout_2x={c: round(float(np.median([x[2] for x in allh if x[0][1] == c])), 2) for c in TF["1H"]["E"]},
               all_results={"|".join(k): v for k, v in R.items()})
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("selected_top5_by_2025", "share_holdout_positive_2x", "n_positive_all_four", "by_timeframe_median_holdout_2x", "by_condition_median_holdout_2x")}, indent=1, default=str))
    print("positive in all four (top 15):"); [print(x) for x in out["positive_all_four"][:15]]
    print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
