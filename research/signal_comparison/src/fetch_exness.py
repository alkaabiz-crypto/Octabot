"""Build hourly bid/ask candles from the Exness public tick archive (ticks.ex2archive.com).

Usage:  python src/fetch_exness.py SYMBOL FIRST_YYYY-MM LAST_YYYY-MM OUT_DIR [workers]

Each monthly zip holds every quote as ``"exness","SYMBOL","YYYY-MM-DD HH:MM:SS.mmmZ",bid,ask`` (UTC). Ticks are
aggregated per UTC hour into one row:

    t (hour open, UTC seconds), bid open/high/low/close, ask open/high/low/close, tick count, mean spread

Nothing is interpolated or invented: hours without ticks (weekends, session breaks, outages) produce no row.
Months missing from the archive are listed in the output and left as gaps. Monthly results are cached in
OUT_DIR/parts so an interrupted run resumes.
"""
import calendar
import csv
import gzip
import io
import multiprocessing
import os
import subprocess
import sys
import time
import zipfile

URL = "https://ticks.ex2archive.com/ticks/{s}/{y}/{m:02d}/Exness_{s}_{y}_{m:02d}.zip"
HEADER = ["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "n", "spread_mean"]


def months(first, last):
    y, m = map(int, first.split("-"))
    ly, lm = map(int, last.split("-"))
    while (y, m) <= (ly, lm):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def aggregate(lines):
    """Yield hourly rows from an iterator of CSV text lines (header already skipped)."""
    key = None
    row = None
    for line in lines:
        parts = line.rstrip().split(",")
        if len(parts) != 5:
            continue
        stamp = parts[2]
        k = stamp[1:14]                      # 'YYYY-MM-DD HH'
        try:
            bid, ask = float(parts[3]), float(parts[4])
        except ValueError:
            continue
        if bid <= 0 or ask <= 0 or ask < bid:
            continue                         # corrupt quote: skipped, counted by absence
        if k != key:
            if row is not None:
                yield finish(key, row)
            key = k
            row = [bid, bid, bid, bid, ask, ask, ask, ask, 0, 0.0]
        row[1] = max(row[1], bid)
        row[2] = min(row[2], bid)
        row[3] = bid
        row[5] = max(row[5], ask)
        row[6] = min(row[6], ask)
        row[7] = ask
        row[8] += 1
        row[9] += ask - bid
    if row is not None:
        yield finish(key, row)


def finish(key, row):
    t = calendar.timegm((int(key[0:4]), int(key[5:7]), int(key[8:10]), int(key[11:13]), 0, 0))
    return [t, *row[:8], row[8], round(row[9] / row[8], 6)]


def do_month(args):
    symbol, y, m, out_dir = args
    part = os.path.join(out_dir, "parts", f"{symbol}_{y}_{m:02d}.csv")
    if os.path.exists(part):
        return y, m, "cached"
    tmp = os.path.join(out_dir, "parts", f"{symbol}_{y}_{m:02d}.zip")
    url = URL.format(s=symbol, y=y, m=m)
    for attempt in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "600", "-o", tmp, "-w", "%{http_code}", url], capture_output=True, text=True, check=False)
        code = r.stdout.strip()
        if code == "200":
            break
        if code == "404":
            if os.path.exists(tmp):
                os.remove(tmp)
            return y, m, "missing"
        time.sleep(2 ** attempt)
    else:
        return y, m, f"failed ({code} {r.stderr.strip()[:80]})"
    rows = []
    with zipfile.ZipFile(tmp) as z, z.open(z.namelist()[0]) as f:
        text = io.TextIOWrapper(f, encoding="utf-8", newline="")
        next(text)
        rows = list(aggregate(text))
    os.remove(tmp)
    with open(part + ".tmp", "w", newline="") as f:
        csv.writer(f).writerows(rows)
    os.replace(part + ".tmp", part)
    return y, m, f"{len(rows)} hours"


def main():
    symbol, first, last, out_dir = sys.argv[1:5]
    workers = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    os.makedirs(os.path.join(out_dir, "parts"), exist_ok=True)
    jobs = [(symbol, y, m, out_dir) for y, m in months(first, last)]
    status = {}
    with multiprocessing.Pool(workers) as pool:
        for y, m, s in pool.imap_unordered(do_month, jobs):
            status[(y, m)] = s
            print(f"{symbol} {y}-{m:02d}: {s}", flush=True)
    bad = [k for k, s in status.items() if s.startswith("failed")]
    if bad:
        raise SystemExit(f"FAILED months: {sorted(bad)} - rerun to resume")
    all_rows = []
    for y, m in months(first, last):
        part = os.path.join(out_dir, "parts", f"{symbol}_{y}_{m:02d}.csv")
        if os.path.exists(part):
            with open(part) as f:
                all_rows += [r for r in csv.reader(f)]
    all_rows.sort(key=lambda r: int(r[0]))
    out = os.path.join(out_dir, f"{symbol}_1h.csv.gz")
    with gzip.open(out, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(all_rows)
    missing = sorted(k for k, s in status.items() if s == "missing")
    print(f"{symbol}: {len(all_rows)} hourly rows -> {out}; missing months: {missing}")


if __name__ == "__main__":
    main()
