"""Audit 2d: null calibration of the news-markets benchmark: fake 'events' at real release clock times on ordinary
weekdays (no event that day or adjacent), run through the same evaluate(); z should have sd ~1."""
import json
import os
import statistics
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "news_markets", "src"))
import run as NM  # noqa: E402

S, G = NM.S, NM.G


def main():
    out = {}
    for mkt, base in (("XAUUSDm", "LONG_DATA"), ("EURUSDm", "MULTI_BARS")):
        m = NM.Mkt(os.path.join(os.environ[base], f"{mkt}_15m.csv.gz"))
        ev = G.all_events()
        macro = ev["FOMC"] + ev["CPI"] + ev["NFP"]
        pool = NM.controls(m, sorted(macro), macro)
        # fake event sets: 50 random control times at each release's clock time, drawn per quarter
        rng = np.random.default_rng(1)
        for strat in ("FOLLOW15", "FADE15", "BREAKOUT", "PRE24"):
            zs = []
            for k in range(80):
                fake = []
                for t in ev["CPI"]:
                    tm = time.gmtime(t)
                    cands = pool.get((S.quarter(t), tm.tm_hour, tm.tm_min), [])
                    if cands:
                        fake.append(int(cands[rng.integers(len(cands))]))
                pool2 = {kk: [c for c in v if c not in set(fake)] for kk, v in pool.items()}
                r = NM.evaluate(m, sorted(fake), pool2, strat, S.ts(2023, 7), S.ts(2026, 11), rng, {})
                if "z" in r:
                    zs.append(r["z"])
            out[f"{mkt}|{strat}"] = {"samples": len(zs), "mean_z": statistics.mean(zs), "sd_z": statistics.pstdev(zs),
                                     "share_z_over_1.645_pct": 100 * sum(z > 1.645 for z in zs) / len(zs)}
            print(mkt, strat, {k: round(v, 3) for k, v in out[f"{mkt}|{strat}"].items()}, flush=True)
    json.dump({"results": out, "generated_utc": S.fmt(time.time())},
              open(os.path.join(os.path.dirname(HERE), "reports", "null_calibration_news.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
