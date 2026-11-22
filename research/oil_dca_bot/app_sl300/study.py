"""Oil bot with the app's minimum 300-pip stop. Implements PREREGISTRATION.md (this folder)."""
import json, os, sys, time
from multiprocessing import Pool
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("TICK_DIR", "/nonexistent")
for p in (ROOT, os.path.join(ROOT, "optimize"), os.path.join(ROOT, "smart_entry"), os.path.join(ROOT, "app_conditions")): sys.path.insert(0, p)
import bot  # noqa
import importlib.util
spec0 = importlib.util.spec_from_file_location("SE", os.path.join(ROOT, "smart_entry", "study.py")); SE = importlib.util.module_from_spec(spec0); sys.modules["study"] = SE; spec0.loader.exec_module(SE)
spec = importlib.util.spec_from_file_location("AC", os.path.join(ROOT, "app_conditions", "study.py")); AC = importlib.util.module_from_spec(spec); spec.loader.exec_module(AC)
EX = {"S1_tp100_sl300": dict(lots=[0.01], steps=[], tp=1.00, trail=0.04, stop=30.0),
      "S2_tp200_sl300": dict(lots=[0.01], steps=[], tp=2.00, trail=0.04, stop=30.0),
      "S3_tp300_sl300": dict(lots=[0.01], steps=[], tp=3.00, trail=0.04, stop=30.0)}
SE.EXITS.update(EX)
def job(a):
    n, x, m = a; rows = SE.run(SE.G["E"][n], SE.EXITS[x], m); return n, x, m, SE.summarize(rows, *SE.DEV), SE.summarize(rows, *SE.HOLD)
def rjob(a):
    x, seed = a; rng = np.random.default_rng(seed); d = rng.choice([-1, 1], size=len(SE.G["closes"])); return x, SE.summarize(SE.run(d, SE.EXITS[x], 1), *SE.HOLD)["net"]
def main():
    t0 = time.time(); t, b, a = SE.load(); mid = (b + a) / 2; s = a - b
    h1, _ = SE.features(t, b); h4 = bot.candles(t, b, SE.H4); c4 = AC.conditions(h4)
    i4 = np.searchsorted(h4.close_ms.values, h1.close_ms.values, side="right") - 1
    E = {f"{k}|4H": np.where(i4 >= 0, c4[k][np.clip(i4, 0, None)], 0) for k in ("Stochastic", "MFI", "Bollinger")}
    SE.G.update(t=t, b=b, a=a, b2=mid - s, a2=mid + s, closes=h1.close_ms.values, trend=h1.trend.values, rangepos=h1.rangepos.values, E=E)
    with Pool(4) as p:
        res = p.map(job, [(n, x, m) for n in E for x in EX for m in (1, 2)])
        rnd = p.map(rjob, [(x, 20261111 + i) for x in EX for i in range(200)])
    out = dict(results={}, random_p90={}, verdicts={})
    for x in EX: out["random_p90"][x] = round(float(np.percentile([r for e, r in rnd if e == x], 90)), 2)
    for n, x, m, dv, ho in res: out["results"][f"{n}|{x}|x{m}"] = dict(dev=dv, holdout=ho)
    for n in E:
        for x in EX:
            r1, r2 = out["results"][f"{n}|{x}|x1"], out["results"][f"{n}|{x}|x2"]
            ok = all(v > 0 for v in (r1["dev"]["net"], r2["dev"]["net"], r1["holdout"]["net"], r2["holdout"]["net"])) and r1["holdout"]["max_dd"] < 408 and r1["holdout"]["baskets"] >= 30
            out["verdicts"][f"{n}|{x}"] = ("PASS" if ok and r1["holdout"]["net"] > out["random_p90"][x] else ("POSITIVE_BUT_BELOW_RANDOM_P90" if ok else "FAIL"))
            print(f"{n:16s} {x:16s} DEV {r1['dev']['net']:>8}/{r2['dev']['net']:>8} HOLD {r1['holdout']['net']:>8}/{r2['holdout']['net']:>8} dd {r1['holdout']['max_dd']:>7} n {r1['holdout']['baskets']:>4} win {r1['holdout'].get('win_rate')} -> {out['verdicts'][f'{n}|{x}']}")
    print("random p90:", out["random_p90"], f"{time.time() - t0:.0f}s")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
if __name__ == "__main__": main()
