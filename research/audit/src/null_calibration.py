"""Audit 2: calibration of the random-entry benchmark under the null. Random signal masks (no information) are run
through the same evaluation as every real variant. z should have mean ~0, sd ~1 and exceed 1.645 about 5% of the time.
usage: python src/null_calibration.py <15m csv.gz> [crypto]"""
import json
import math
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "tradingview_builtins", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
import builtin_strategies as B  # noqa: E402
import fast_bench as FB  # noqa: E402
import run_everything as RE  # noqa: E402
import study as S  # noqa: E402


def main():
    path = sys.argv[1]
    a = B.BuiltinAsset(path, crypto=len(sys.argv) > 2)
    w0, w1 = S.ts(2023, 7), S.ts(2025, 1)
    rnd = random.Random(3)
    n = len(a.e.t)
    res = {}
    for ex in ("HW", "SYM", "TRAIL", "FLIP"):
        zs = []
        for k in range(100):
            d = rnd.choice((1, -1))
            dens = rnd.choice((0.005, 0.01, 0.03))
            if ex == "FLIP":
                mine = [rnd.random() < dens for _ in range(n)]
                other = [rnd.random() < dens for _ in range(n)]
                tr = RE.flip_legs(a, mine, other, d, w0, w1)
                if len(tr) < 30:
                    continue
                mu, sd = FB.held(a, tr, w0, w1, runs=200, seed=1000 + k)
            else:
                sig = [rnd.random() < dens for _ in range(n)]
                tr = a.run_signals(sig, d, ex, w0, w1)
                if len(tr) < 30:
                    continue
                mu, sd, _ = FB.standard(a, tr, d, ex, w0, w1, runs=200, seed=1000 + k)
            e = statistics.mean(t.r("primary") for t in tr)
            zs.append((e - mu) / sd if sd > 0 else 0.0)
        res[ex] = {"samples": len(zs), "mean_z": statistics.mean(zs), "sd_z": statistics.pstdev(zs),
                   "share_z_over_1.645_pct": 100 * sum(z > 1.645 for z in zs) / len(zs),
                   "share_abs_z_over_1.96_pct": 100 * sum(abs(z) > 1.96 for z in zs) / len(zs)}
        print(ex, {k: round(v, 3) for k, v in res[ex].items()}, flush=True)
    out = {"market": os.path.basename(path), "period": "2023-07..2024-12", "results": res, "generated_utc": S.fmt(time.time())}
    json.dump(out, open(os.path.join(os.path.dirname(HERE), "reports", f"null_calibration_{os.path.basename(path).split('_')[0]}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
