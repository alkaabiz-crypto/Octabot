"""Audit 3: how big the cost assumptions are per market, in R (= 2 x ATR14 of 1-hour candles).
Spread is measured from the data (ask - bid at each 15-minute open); slippage is the fixed 0.02% (primary) /
0.05% (stress) of price used in every study. Also flags months whose median spread jumps (data or broker changes)."""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

S = "/tmp/claude-0/-home-user-Octabot/673585c7-1020-5c5e-b0a9-ec953e6fb327/scratchpad"


def main():
    files = {os.path.basename(f).split("_")[0]: f for f in glob.glob(f"{S}/multi/bars/*_15m.csv.gz")}
    for m in ("USOILm", "XAUUSDm", "BTCUSDm"):
        files[m] = f"{S}/long/{m}_15m.csv.gz"
    out = {}
    for m, f in sorted(files.items()):
        d = pd.read_csv(f)
        d = d[d.t >= 1735689600]                     # 2025-01 to now
        d["dt"] = pd.to_datetime(d.t, unit="s")
        h = d.set_index("dt").resample("1h").agg({"bh": "max", "bl": "min", "bc": "last"}).dropna()
        tr = np.maximum(h.bh - h.bl, np.maximum((h.bh - h.bc.shift()).abs(), (h.bl - h.bc.shift()).abs()))
        atr = tr.ewm(alpha=1 / 14, adjust=False).mean().median()
        R = 2 * atr
        spread = (d.ao - d.bo).median()
        price = d.bc.median()
        monthly = d.assign(sp=(d.ao - d.bo) / d.bc).groupby(d.dt.dt.to_period("M")).sp.median()
        jumps = {str(k): round(float(v / monthly.median()), 1) for k, v in monthly.items() if v > 3 * monthly.median()}
        out[m] = {"median_spread_R": float(spread / R), "slip_primary_R": float(0.0002 * price / R),
                  "slip_stress_R": float(0.0005 * price / R), "months_with_spread_over_3x_median": jumps}
        print(f"{m:9} spread {spread / R:.3f}R  slip(0.02%) {0.0002 * price / R:.3f}R  stress slip {0.0005 * price / R:.3f}R  "
              f"spread jumps: {jumps}", flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "costs.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
