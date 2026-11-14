"""PROTOCOL.md addendum 3: gold after NFP, consensus surprise, 2020-03..2024-12 ticks (never looked at before).
usage: SURPRISE=consensus LONG_DATA=<dir> TICK_WORK=<dir> python src/gold_nfp_check.py"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run as R  # noqa: E402
import ticks as TK  # noqa: E402

NM, S = R.NM, R.S


def main():
    assert R.MODE == "consensus"
    m = NM.Mkt(os.path.join(os.environ["LONG_DATA"], "XAUUSDm_15m.csv.gz"))
    ev = sorted((t, s) for (k, t), s in R.scores().items() if k == "NFP" and S.ts(2020, 3) <= t < S.ts(2025, 1))
    win = TK.windows("XAUUSDm", [t for t, _ in ev], os.environ["TICK_WORK"])
    rng = np.random.default_rng(20261112)
    out = {}
    for dl in (30, 180):
        lo, sh, sg, yrs = [], [], [], []
        for t, s in ev:
            if t not in win or len(win[t][0]) < 10:
                continue
            tt, b, a = win[t]
            i, j = TK.first_at(tt, t + dl), TK.first_at(tt, t + 900)
            atr = m.atr_before(t)
            if i is None or j is None or atr is None or tt[i] - (t + dl) > 120:
                continue
            lo.append((b[j] - a[i]) / (2 * atr))
            sh.append((b[i] - a[j]) / (2 * atr))
            sg.append(-np.sign(s))                       # textbook: strong jobs report -> SELL gold
            yrs.append(time.gmtime(t).tm_year)
        lo, sh, sg = map(np.array, (lo, sh, sg))
        r = np.where(sg > 0, lo, sh)
        perm = np.array([np.where(rng.permutation(sg) > 0, lo, sh).mean() for _ in range(2000)])
        out[f"{dl}s"] = {"trades": len(r), "win_rate_pct": float((r > 0).mean() * 100), "expectancy_r": float(r.mean()),
                         "total_r": float(r.sum()), "perm_mean_r": float(perm.mean()),
                         "p": float((np.sum(perm >= r.mean()) + 1) / 2001),
                         "by_year": {str(y): [int(sum(1 for x in yrs if x == y)), float(np.mean([v for v, x in zip(r, yrs) if x == y]))]
                                     for y in sorted(set(yrs))}}
        print(dl, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[f"{dl}s"].items()})
    p, s2 = out["30s"], out["180s"]
    verdict = p["p"] <= 0.05 and p["expectancy_r"] > 0 and s2["expectancy_r"] > 0
    out["verdict"] = "lead holds" if verdict else "lead dropped"
    print(out["verdict"])
    json.dump({"meta": {"generated_utc": S.fmt(time.time()), "period": "2020-03 to 2024-12"}, "results": out},
              open(os.path.join(R.ROOT, "reports", "gold_nfp_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
