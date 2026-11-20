"""Audit fix 2: the requested-indicator and indicator-scan studies judged 2025 and 2026 separately (each had to reach
p <= 0.05 on its own), which needs a large edge in two short samples. Re-run every variant on the single window the
user asked for, 2025-01 to the latest candle: calibrated random benchmark (fast_bench.standard / seq_held), costs
with spread-linked slippage (0.5 x median spread, stress 1.5 x + 0.02%/day), Benjamini-Hochberg over everything.
usage: python src/pooled_2025.py"""
import json
import math
import os
import statistics
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "requested_indicators", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
sys.path.insert(0, HERE)
import requested as RQ  # noqa: E402
import run_requested as RR  # noqa: E402
import scan  # noqa: E402
import fast_bench as FB  # noqa: E402
import seq_held as SH  # noqa: E402
import study as S  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("lr", os.path.join(RESEARCH, "long_history", "src", "report.py"))
LR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LR)


def slip_of(a, w0):
    q = a.q
    sp = [aa - bb for t, aa, bb in zip(q["t"], q["ao"], q["bo"]) if t >= w0]
    pr = [bb for t, bb in zip(q["t"], q["bc"]) if t >= w0]
    f = statistics.median(sp) / statistics.median(pr)
    return 0.5 * f, 1.5 * f


def costs(trades, slip, swap=0.0):
    return np.array([t.r_gross - (slip + swap * (t.exit_time - t.entry_time) / 86400) * t.entry / t.risk for t in trades])


def main():
    out = {}
    for mkt, (path, utc, names) in RR.MARKETS.items():
        a = RQ.ReqAsset(path, utc_day_sessions=utc)
        w0, w1 = S.ts(2025, 1), a.e.t[-1] + 3600
        sp, ss = slip_of(a, w0)
        jobs = [("requested", ind, a.req_signals) for ind in names] + [("scan", ind, a.scan_signals) for ind in scan.INDICATORS]
        for src, ind, fn in jobs:
            for d in (1, -1):
                sig = fn(ind, d)
                for ex in RR.EXITS + (("NATIVE",) if ind == "LORENTZIAN" else ()):
                    tr = a.run_signals(sig, d, ex, w0, w1)
                    key = f"{mkt}|{src}|{ind}|{'BUY' if d > 0 else 'SELL'}|{ex}"
                    if len(tr) < 30:
                        out[key] = {"trades": len(tr)}
                        continue
                    r_old = np.array([t.r("primary") for t in tr])
                    r_new, r_st = costs(tr, sp), costs(tr, ss, 0.0002)
                    if ex == "NATIVE":
                        mu, sd = SH.seq_held(a, tr, w0, w1, runs=500)
                    else:
                        mu, sd, _ = FB.standard(a, tr, d, ex, w0, w1, runs=500)
                    z = (r_old.mean() - mu) / sd if sd > 0 else 0.0
                    out[key] = {"trades": len(tr), "win_rate_pct": float((r_new > 0).mean() * 100),
                                "expectancy_r_old_costs": float(r_old.mean()), "expectancy_r": float(r_new.mean()),
                                "expectancy_stress_r": float(r_st.mean()), "z": float(z), "p": 0.5 * math.erfc(z / math.sqrt(2))}
            print(mkt, src, ind, flush=True)
    keys = [k for k in out if "z" in out[k]]
    rej = LR.benjamini_hochberg([out[k]["p"] for k in keys])
    sig = [keys[i] for i in sorted(rej)]
    conf = [k for k in sig if out[k]["expectancy_stress_r"] > 0]
    top = sorted(keys, key=lambda k: -out[k]["z"])[:15]
    json.dump({"meta": {"window": "2025-01 to latest", "generated_utc": S.fmt(time.time()), "variants": len(keys)},
               "bh_significant": sig, "confirmed_profitable": conf, "top15_by_z": top, "results": out},
              open(os.path.join(os.path.dirname(HERE), "reports", "pooled_2025.json"), "w"), indent=1)
    print("variants", len(keys), "BH significant", sig, "profitable at stress", conf)
    for k in top:
        v = out[k]
        print(f"{k:55} n={v['trades']:4} win={v['win_rate_pct']:.0f}% E={v['expectancy_r']:+.3f} (old {v['expectancy_r_old_costs']:+.3f}) stress={v['expectancy_stress_r']:+.3f} z={v['z']:+.2f} p={v['p']:.4f}")


if __name__ == "__main__":
    main()
