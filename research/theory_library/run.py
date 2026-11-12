"""Run every pre-registered theory on every applicable market/timeframe (PREREGISTRATION.md).

Usage: BARS_DIR=<orb 1m bars> python3 -I run.py
"""
import json, os, sys, time, zlib
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E  # noqa: E402
import theories as T  # noqa: E402

DRAWS = 500; SEED = 20261112


def summ(r):
    return dict(trades=int(len(r)), mean_bp=round(float(r.mean() * 1e4), 2) if len(r) else None, sum_pct=round(float(r.sum() * 100), 2),
                win=round(float((r > 0).mean()), 3) if len(r) else None)


def run_market(mkt):
    out = {}
    for tid, fam, tfs, mkts, fn in T.REGISTRY:
        if mkt not in mkts: continue
        for tf in tfs:
            if E.candles(mkt, tf) is None: continue
            key = f"{tid}|{mkt}|{tf}"; t0 = time.time()
            try:
                res = fn(mkt, tf)
            except Exception as ex:  # report, never hide
                out[key] = dict(error=repr(ex)); continue
            if res is None: continue
            c, bk = res; r1, _ = E.evaluate(c, bk, 1); r2, meta = E.evaluate(c, bk, 2)
            rng = np.random.default_rng(SEED + zlib.crc32(key.encode()) % 100000)
            rc = E.random_control(c, meta, 2, DRAWS, rng) if len(meta) else {"dev": None, "holdout": None}
            d, h = summ(r2["dev"]), summ(r2["holdout"])
            p95 = {p: (round(float(v[1] * 1e4), 2) if v is not None else None) for p, v in rc.items()}
            p50 = {p: (round(float(v[0] * 1e4), 2) if v is not None else None) for p, v in rc.items()}
            ok = (d["mean_bp"] is not None and h["mean_bp"] is not None and d["mean_bp"] > 0 and h["mean_bp"] > 0 and h["trades"] >= 30
                  and p95["dev"] is not None and p95["holdout"] is not None and d["mean_bp"] > p95["dev"] and h["mean_bp"] > p95["holdout"])
            out[key] = dict(theory=tid, family=fam, market=mkt, tf=tf, x1=dict(dev=summ(r1["dev"]), holdout=summ(r1["holdout"])), x2=dict(dev=d, holdout=h),
                            random_x2_p50_bp=p50, random_x2_p95_bp=p95, verdict="PASS" if ok else "FAIL", secs=round(time.time() - t0, 1))
            print(key, out[key]["x2"], out[key]["verdict"], flush=True)
    return out


def main():
    t0 = time.time(); R = {}
    with Pool(4) as p:
        for part in p.imap_unordered(run_market, E.EXNESS + E.CRYPTO): R.update(part)
    ok = {k: v for k, v in R.items() if "error" not in v}
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), n_combinations=len(ok), n_errors=len(R) - len(ok),
               errors={k: v for k, v in R.items() if "error" in v}, n_pass=sum(v["verdict"] == "PASS" for v in ok.values()), results=R)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print("combinations", out["n_combinations"], "errors", out["n_errors"], "PASS", out["n_pass"], f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
