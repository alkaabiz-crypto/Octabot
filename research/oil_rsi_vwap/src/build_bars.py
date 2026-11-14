"""Build 15-minute bid/ask candles from the Exness public tick archive.

Usage: python src/build_bars.py SYMBOL FIRST_YYYY-MM LAST_YYYY-MM OUT_CSV_GZ WORK_DIR [workers]
Output columns: t (15m open, UTC seconds), bid o/h/l/c, ask o/h/l/c, ticks. Only periods with quotes produce a row.
Months missing from the archive are listed and left as gaps. Monthly parts are cached in WORK_DIR (resumable).
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


def months(a, b):
    y, m = map(int, a.split("-"))
    y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def bucket(stamp):
    # "YYYY-MM-DD HH:MM:SS.mmmZ" -> 15-minute bucket start (UTC seconds)
    base = calendar.timegm((int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10]), int(stamp[11:13]), 0, 0))
    return base + (int(stamp[14:16]) // 15) * 900


def do_month(args):
    sym, y, m, work = args
    part = os.path.join(work, f"{sym}_{y}_{m:02d}.csv")
    if os.path.exists(part):
        return y, m, "cached"
    zpath = part[:-4] + ".zip"
    for attempt in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "900", "-o", zpath, "-w", "%{http_code}", URL.format(s=sym, y=y, m=m)],
                           capture_output=True, text=True, check=False)
        code = r.stdout.strip()
        if code == "200":
            break
        if code == "404":
            return y, m, "missing"
        time.sleep(2 ** attempt)
    else:
        return y, m, f"failed {code}"
    rows, cur, key = [], None, None
    bad = 0
    with zipfile.ZipFile(zpath) as z, z.open(z.namelist()[0]) as f:
        text = io.TextIOWrapper(f, encoding="utf-8")
        next(text)
        for line in text:
            p = line.rstrip().split(",")
            if len(p) != 5:
                bad += 1
                continue
            try:
                bid, ask = float(p[3]), float(p[4])
            except ValueError:
                bad += 1
                continue
            if bid <= 0 or ask < bid:
                bad += 1
                continue
            k = bucket(p[2].strip('"'))
            if k != key:
                if cur:
                    rows.append(cur)
                key = k
                cur = [k, bid, bid, bid, bid, ask, ask, ask, ask, 0]
            cur[2] = max(cur[2], bid)
            cur[3] = min(cur[3], bid)
            cur[4] = bid
            cur[6] = max(cur[6], ask)
            cur[7] = min(cur[7], ask)
            cur[8] = ask
            cur[9] += 1
    if cur:
        rows.append(cur)
    os.remove(zpath)
    with open(part + ".tmp", "w", newline="") as f:
        csv.writer(f).writerows(rows)
    os.replace(part + ".tmp", part)
    return y, m, f"{len(rows)} bars, {bad} bad quotes skipped"


def main():
    sym, a, b, out, work = sys.argv[1:6]
    workers = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    os.makedirs(work, exist_ok=True)
    status = {}
    with multiprocessing.Pool(workers) as pool:
        for y, m, s in pool.imap_unordered(do_month, [(sym, y, m, work) for y, m in months(a, b)]):
            status[(y, m)] = s
            print(f"{sym} {y}-{m:02d}: {s}", flush=True)
    failed = [k for k, s in status.items() if s.startswith("failed")]
    if failed:
        raise SystemExit(f"failed months {sorted(failed)}: rerun to resume")
    rows = []
    for y, m in months(a, b):
        p = os.path.join(work, f"{sym}_{y}_{m:02d}.csv")
        if os.path.exists(p):
            with open(p) as f:
                rows += list(csv.reader(f))
    rows.sort(key=lambda r: int(r[0]))
    with gzip.open(out, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        w.writerows(rows)
    print(f"{sym}: {len(rows)} bars -> {out}; missing months: {sorted(k for k, s in status.items() if s == 'missing')}")


if __name__ == "__main__":
    main()
