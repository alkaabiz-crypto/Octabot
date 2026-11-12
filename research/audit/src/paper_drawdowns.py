"""Historical worst drawdown (in R, cumulative, primary cost) and leg rate of each paper-test rule, measured on data
before the paper tests began (to 2026-11-11). Used only to pre-register drawdown limits in FORWARD_TEST_PLAN.md."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "tradingview_builtins", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "gold_kst_news", "src"))
import builtin_strategies as B  # noqa: E402
import engine as G  # noqa: E402

S = B.S
END = S.ts(2026, 11, 12)


def dd(r):
    eq = np.cumsum(r)
    return float((np.maximum.accumulate(np.concatenate([[0.0], eq]))[1:] - eq).max())


def main():
    base = sys.argv[1]
    out = {}
    for name, path, w0 in (("BTC Pivot Reversal BUY", f"{base}/long/BTCUSDm_15m.csv.gz", S.ts(2020, 7)),
                           ("ETH Pivot Reversal BUY", f"{base}/multi/bars/ETHUSDm_15m.csv.gz", S.ts(2023, 7))):
        a = B.BuiltinAsset(path, crypto=True)
        tr = [t for t in a.simulate_strategy("PIVOT_REVERSAL") if t.direction == 1 and w0 <= t.entry_time < END]
        r = np.array([t.r("primary") for t in tr])
        yrs = (tr[-1].entry_time - tr[0].entry_time) / (365.25 * 86400)
        out[name] = {"period": [S.fmt(w0), "2026-11-11"], "legs": len(r), "legs_per_year": len(r) / yrs,
                     "mean_r": float(r.mean()), "sd_r": float(r.std(ddof=1)), "max_drawdown_r": dd(r)}
    g = G.Gold(f"{base}/long/XAUUSDm_15m.csv.gz")
    ev = G.all_events()
    R = G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])
    for name, p in (("Gold KST 48h time stop", (0, 0, 0, 48, 0, "NONE")), ("Gold KST original", (0, 0, 0, 0, 0, "NONE")),
                    ("Gold KST 2xATR stop + close before news", (2, 0, 0, 0, 0, "BLOCK_FLAT"))):
        L = R.legs(p, S.ts(2020, 7), END)
        r = R.r(L, "primary")
        yrs = (L["entry_t"][-1] - L["entry_t"][0]) / (365.25 * 86400)
        out[name] = {"period": ["2020-07-01", "2026-11-11"], "legs": int(len(r)), "legs_per_year": float(len(r) / yrs),
                     "mean_r": float(r.mean()), "sd_r": float(r.std(ddof=1)), "max_drawdown_r": dd(r)}
    for k, v in out.items():
        print(k, {x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()})
    json.dump(out, open(os.path.join(os.path.dirname(HERE), "reports", "paper_drawdowns.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
