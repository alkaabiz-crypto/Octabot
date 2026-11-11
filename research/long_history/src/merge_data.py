"""Join the Exness 15-minute bid/ask files into one full-history file per market (no overlap, no gaps filled).
usage: python merge_data.py OUT_DIR OLD_DIR   (OLD_DIR holds the files built with oil_rsi_vwap/src/build_bars.py)"""
import gzip
import os
import sys

RESEARCH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CURRENT = {"USOILm": os.path.join(RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"),
           "XAUUSDm": os.path.join(RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz"),
           "BTCUSDm": os.path.join(RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz")}
OLD = {"USOILm": ["USOILm_2019_2024_15m.csv.gz"],
       "XAUUSDm": ["XAUUSDm_2020_2023_15m.csv.gz", "XAUUSDm_2024_01_02_15m.csv.gz"],
       "BTCUSDm": ["BTCUSDm_2020_2024_15m.csv.gz"]}


def main(out_dir, old_dir, *only):
    os.makedirs(out_dir, exist_ok=True)
    for mkt, cur in CURRENT.items():
        if only and mkt not in only:
            continue
        rows, header = {}, None
        for path in [os.path.join(old_dir, f) for f in OLD[mkt]] + [cur]:      # later files win on overlap
            with gzip.open(path, "rt") as f:
                header = next(f)
                for line in f:
                    rows[int(line.split(",", 1)[0])] = line
        with gzip.open(os.path.join(out_dir, f"{mkt}_15m.csv.gz"), "wt") as f:
            f.write(header)
            for t in sorted(rows):
                f.write(rows[t])
        ts = sorted(rows)
        print(mkt, len(ts), "bars", ts[0], ts[-1])


if __name__ == "__main__":
    main(*sys.argv[1:])
