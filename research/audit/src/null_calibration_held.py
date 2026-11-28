"""Audit 2b: null calibration of the corrected held-leg benchmark (shift) vs the old one, on random flip signals
and on random-direction strategy-like legs. usage: python src/null_calibration_held.py <15m csv.gz> [crypto]"""
import json
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "tradingview_builtins", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
sys.path.insert(0, HERE)
import builtin_strategies as B  # noqa: E402
import fast_bench as FB  # noqa: E402
import run_everything as RE  # noqa: E402
import shift_bench as SB  # noqa: E402
import seq_held as SH  # noqa: E402
import study as S  # noqa: E402


def main():
    path = sys.argv[1]
    a = B.BuiltinAsset(path, crypto=len(sys.argv) > 2)
    w0, w1 = S.ts(2023, 7), S.ts(2025, 1)
    rnd = random.Random(5)
    n = len(a.e.t)
    zs_old, zs_new, zs_seq = [], [], []
    for k in range(150):
        d = rnd.choice((1, -1))
        dens = rnd.choice((0.005, 0.01, 0.03))
        mine = [rnd.random() < dens for _ in range(n)]
        other = [rnd.random() < dens for _ in range(n)]
        tr = RE.flip_legs(a, mine, other, d, w0, w1)
        if len(tr) < 30:
            continue
        e = statistics.mean(t.r("primary") for t in tr)
        mu, sd = FB.held(a, tr, w0, w1, runs=200, seed=1000 + k)
        zs_old.append((e - mu) / sd)
        mu, sd = SB.held_shift(a, tr, w0, w1, runs=1000, seed=1000 + k)
        zs_new.append((e - mu) / sd)
        mu, sd = SH.seq_held(a, tr, w0, w1, runs=500, seed=1000 + k)
        zs_seq.append((e - mu) / sd)
    res = {}
    for nm, zs in (("old_independent", zs_old), ("shift", zs_new), ("sequential", zs_seq)):
        res[nm] = {"samples": len(zs), "mean_z": statistics.mean(zs), "sd_z": statistics.pstdev(zs),
                   "share_z_over_1.645_pct": 100 * sum(z > 1.645 for z in zs) / len(zs)}
        print(nm, {k: round(v, 3) for k, v in res[nm].items()}, flush=True)
    json.dump({"market": os.path.basename(path), "period": "2023-07..2024-12", "results": res, "generated_utc": S.fmt(time.time())},
              open(os.path.join(os.path.dirname(HERE), "reports", f"null_calibration_held_{os.path.basename(path).split('_')[0]}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
