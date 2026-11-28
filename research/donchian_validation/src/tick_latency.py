"""Execution delay at tick level: how much the Exness BTCUSDm ASK moves in the seconds after a signal candle closes.

Usage: python src/tick_latency.py ENTRY_TIMES_CSV OUT_JSON WORK_DIR
ENTRY_TIMES_CSV has columns entry_time (UTC seconds, = signal 1H close) and risk (price distance of 1R).
For each month containing entries, the monthly tick zip is downloaded from ticks.ex2archive.com, streamed, and
only ticks within 10 minutes after each entry time are kept. The zip is deleted afterwards.
Reported per entry: first-tick delay, and the ask at +1, +5, +30, +60 and +300 seconds minus the first ask, in R.
"""
import bisect
import calendar
import csv
import io
import json
import os
import subprocess
import sys
import time
import zipfile

URL = "https://ticks.ex2archive.com/ticks/BTCUSDm/{y}/{m:02d}/Exness_BTCUSDm_{y}_{m:02d}.zip"
OFFSETS = (0, 1, 5, 30, 60, 300)
WINDOW = 600


def parse_ts(s):
    # "YYYY-MM-DD HH:MM:SS.mmmZ"
    base = calendar.timegm((int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]), int(s[14:16]), int(s[17:19])))
    frac = float("0" + s[19:].rstrip("Z")) if len(s) > 20 else 0.0
    return base + frac


def month_ticks(y, m, starts, work):
    zpath = os.path.join(work, f"BTCUSDm_{y}_{m:02d}.zip")
    for attempt in range(5):
        r = subprocess.run(["curl", "-sS", "-m", "1200", "-o", zpath, "-w", "%{http_code}", URL.format(y=y, m=m)],
                           capture_output=True, text=True, check=False)
        if r.stdout.strip() == "200":
            break
        time.sleep(2 ** attempt)
    else:
        raise SystemExit(f"download failed {y}-{m:02d}: {r.stdout} {r.stderr}")
    keep = {s: [] for s in starts}
    ss = sorted(starts)
    with zipfile.ZipFile(zpath) as z, z.open(z.namelist()[0]) as f:
        text = io.TextIOWrapper(f, encoding="utf-8")
        next(text)
        for line in text:
            p = line.split(",")
            stamp = p[2].strip('"')
            # cheap prefilter on minute: only parse lines whose hour matches an entry hour window
            t = parse_ts(stamp)
            k = bisect.bisect_right(ss, t) - 1
            if k >= 0 and t - ss[k] <= WINDOW:
                keep[ss[k]].append((t, float(p[3]), float(p[4])))
    os.remove(zpath)
    return keep


def main():
    entries_csv, out_json, work = sys.argv[1:4]
    os.makedirs(work, exist_ok=True)
    with open(entries_csv) as f:
        entries = [(int(r["entry_time"]), float(r["risk"])) for r in csv.DictReader(f)]
    by_month = {}
    for t, risk in entries:
        g = time.gmtime(t)
        by_month.setdefault((g.tm_year, g.tm_mon), []).append((t, risk))
    done = {}
    if os.path.exists(out_json):
        with open(out_json) as f:
            done = json.load(f)
    for (y, m), items in sorted(by_month.items()):
        key = f"{y}-{m:02d}"
        if key in done:
            continue
        ticks = month_ticks(y, m, [t for t, _ in items], work)
        rows = []
        for t, risk in items:
            tk = ticks[t]
            if not tk:
                rows.append({"entry_time": t, "risk": risk, "ticks": 0})
                continue
            first_t, _, first_ask = tk[0]
            row = {"entry_time": t, "risk": risk, "ticks": len(tk), "first_tick_delay_s": first_t - t, "first_ask": first_ask,
                       "first_spread": tk[0][2] - tk[0][1]}
            for off in OFFSETS[1:]:
                later = [a for (tt, _, a) in tk if tt >= t + off]
                row[f"ask_move_R_{off}s"] = (later[0] - first_ask) / risk if later else None
            rows.append(row)
        done[key] = rows
        with open(out_json, "w") as f:
            json.dump(done, f, indent=1)
        print(key, len(items), "entries", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
