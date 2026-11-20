"""Download, for each CPI and NFP release date, the series exactly as published that day (ALFRED vintages).
Writes data/vintage_<SERIES>.json: {release_date: [[obs_date, value], ... last 8 obs]}."""
import csv
import io
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GK = os.path.join(os.path.dirname(ROOT), "gold_kst_news", "data")
URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={s}&vintage_date={d}&cosd={c}"


def dates(fn):
    return [l.strip() for l in open(os.path.join(GK, fn)) if l[:2] == "20"]


def get(series, d):
    y = int(d[:4]) - 2
    out = subprocess.run(["curl", "-sSf", "-m", "40", URL.format(s=series, d=d, c=f"{y}-01-01")], capture_output=True, text=True, check=True).stdout
    rows = [r for r in csv.reader(io.StringIO(out))][1:]
    return [[r[0], float(r[1])] for r in rows if len(r) == 2 and r[1] not in ("", ".")][-8:]


def main():
    plan = {"CPILFESL": dates("cpi_releases.csv"), "PAYEMS": dates("nfp_releases.csv"), "UNRATE": dates("nfp_releases.csv")}
    for s, ds in plan.items():
        path = os.path.join(ROOT, "data", f"vintage_{s}.json")
        have = json.load(open(path)) if os.path.exists(path) else {}
        for d in ds:
            if d in have or d < "2019-06-01":
                continue
            for attempt in range(4):
                try:
                    have[d] = get(s, d)
                    break
                except subprocess.CalledProcessError:
                    time.sleep(2 ** attempt)
            time.sleep(0.3)
        json.dump(have, open(path, "w"), indent=0)
        print(s, len(have), file=sys.stderr)


if __name__ == "__main__":
    main()
