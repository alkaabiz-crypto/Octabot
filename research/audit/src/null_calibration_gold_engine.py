"""Audit 2c: null calibration of the gold KST study's benchmark (gold_kst_news engine Runner.bench: independent random
entries with the same exit rules). Random entry masks replace the KST signal; the exit stays 'next bearish KST cross'
plus the option under test. z should have sd ~1."""
import json
import os
import statistics
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "gold_kst_news", "src"))
import engine as G  # noqa: E402


def main():
    g = G.Gold(sys.argv[1])
    ev = G.all_events()
    R = G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])
    w0, w1 = G.S.ts(2020, 7), G.S.ts(2025, 1)
    rng = np.random.default_rng(4)
    n = len(g.th)
    out = {}
    for name, p in (("original (hold to bearish cross)", (0, 0, 0, 0, 0, "NONE")), ("2xATR stop", (2, 0, 0, 0, 0, "NONE")),
                    ("48h time stop", (0, 0, 0, 48, 0, "NONE")), ("trail 3xATR", (0, 3, 0, 0, 0, "NONE"))):
        zs = []
        for k in range(120):
            sig = rng.random(n) < rng.choice([0.005, 0.01, 0.02])
            L = R.legs(p, w0, w1, sig=sig)
            if len(L["r_gross"]) < 50:
                continue
            e = float(R.r(L, "primary").mean())
            mu, sd = R.bench(p, L, w0, w1, runs=200, seed=int(k))
            zs.append((e - mu) / sd)
        out[name] = {"samples": len(zs), "mean_z": statistics.mean(zs), "sd_z": statistics.pstdev(zs),
                     "share_z_over_1.645_pct": 100 * sum(z > 1.645 for z in zs) / len(zs)}
        print(name, {k: round(v, 3) for k, v in out[name].items()}, flush=True)
    json.dump({"period": "2020-07..2024-12", "results": out, "generated_utc": G.S.fmt(time.time())},
              open(os.path.join(os.path.dirname(HERE), "reports", "null_calibration_gold_engine.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
