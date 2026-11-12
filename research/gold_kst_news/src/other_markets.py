"""IDEAS.md part C: DOLLAR_FALLING and VOL_LOW on silver and EUR/USD (KST + session VWAP BUY, original exit).
usage: MULTI_BARS=<dir with <SYM>_15m.csv.gz> python src/other_markets.py"""
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as G  # noqa: E402
import ideas as I  # noqa: E402
import optimize as O  # noqa: E402

S = G.S
MARKETS = ("XAGUSDm", "EURUSDm")
FILTERS = ("DOLLAR_FALLING", "VOL_LOW")


def stats(R, p, L, w0, w1):
    rp, rs = R.r(L, "primary"), R.r(L, "stress")
    if len(rp) < 5:
        return {"trades": len(rp)}
    mu, sd = R.bench(p, L, w0, w1)
    return {"trades": len(rp), "win_rate_pct": float((rp > 0).mean() * 100), "expectancy_r": float(rp.mean()),
            "expectancy_stress_r": float(rs.mean()), "total_r": float(rp.sum()), "max_drawdown_r": G.max_drawdown(rp),
            "random_mean_r": mu, "z": (float(rp.mean()) - mu) / sd if sd > 0 else 0.0}


def main():
    ev = G.all_events()
    out = {}
    for m in MARKETS:
        g = G.Gold(os.path.join(os.environ["MULTI_BARS"], f"{m}_15m.csv.gz"))
        R = G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])
        w0, w1 = S.ts(2023, 7), int(g.th[-1]) + 3600
        flt = I.filters(g)
        out[f"{m}|UNFILTERED"] = stats(R, O.BASE, R.legs(O.BASE, w0, w1), w0, w1)
        for f in FILTERS:
            sig = np.array([b and o for b, o in zip(g.buy, flt[f])])
            out[f"{m}|{f}"] = stats(R, O.BASE, R.legs(O.BASE, w0, w1, sig=sig), w0, w1)
        for k in [k for k in out if k.startswith(m)]:
            print(k, {x: (round(v, 3) if isinstance(v, float) else v) for x, v in out[k].items()}, flush=True)
    keys = [f"{m}|{f}" for m in MARKETS for f in FILTERS]
    ps = [0.5 * math.erfc(out[k].get("z", 0) / math.sqrt(2)) for k in keys]
    rej = I.__dict__.get("lr")
    import importlib.util
    spec = importlib.util.spec_from_file_location("lr", os.path.join(G.RESEARCH, "long_history", "src", "report.py"))
    lr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lr)
    rej = lr.benjamini_hochberg(ps)
    carried = [keys[i] for i in sorted(rej) if out[keys[i]].get("expectancy_stress_r", -1) > 0
               and out[keys[i]]["expectancy_r"] > out[keys[i].split("|")[0] + "|UNFILTERED"].get("expectancy_r", 9)]
    json.dump({"meta": {"generated_utc": S.fmt(time.time()), "period": "2023-07 to latest"}, "p": dict(zip(keys, ps)),
               "carried_over": carried, "results": out}, open(os.path.join(G.ROOT, "reports", "other_markets.json"), "w"), indent=1)
    print("p:", dict(zip(keys, [round(p, 3) for p in ps])), "carried over:", carried)


if __name__ == "__main__":
    main()
