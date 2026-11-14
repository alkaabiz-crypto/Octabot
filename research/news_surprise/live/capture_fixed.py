"""Forward PAPER test of trading the news surprise (no orders are ever placed).
CAPTURE_FIX_NOTE.md: a copy of the hash-locked capture.py with ONLY two parsing fixes (CRLF in text mode; proxy CONNECT headers).

At a scheduled release this script polls the official BLS data API about once a second, from 15 s before 08:30:00
New York time until the new figure appears (or 5 minutes pass), and records the moment our machine first sees it.
That 'receive time' is what a free setup can actually achieve. evaluate.py later scores the paper trade from the
receive time with Exness tick data.
usage: BLS_API_KEY=<free key, optional> python capture.py NFP|CPI YYYY-MM-DD"""
import calendar
import csv
import datetime
import email.utils
import json
import os
import subprocess
import sys
import time
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "live_captures.csv")
NY = zoneinfo.ZoneInfo("America/New_York")
SERIES = {"NFP": ["CES0000000001", "LNS14000000"], "CPI": ["CUSR0000SA0L1E"]}
FIELDS = ["kind", "release_utc", "first_seen_utc", "seconds_after_release", "clock_offset_s", "polls", "period",
          "values", "forecast", "surprise_score", "status"]


def bls(series, key):
    body = {"seriesid": series, "latest": True}
    if key:
        body["registrationkey"] = key
    r = subprocess.run(["curl", "--suppress-connect-headers", "-sS", "-m", "5", "-D", "-", "-H", "Content-Type: application/json", "-X", "POST",
                        "-d", json.dumps(body), "https://api.bls.gov/publicAPI/v2/timeseries/data/"],
                       capture_output=True, text=True)
    head, _, payload = r.stdout.replace("\r\n", "\n").partition("\n\n")     # FIX: text mode turns CRLF into LF
    server_date = None
    for line in head.splitlines():
        if line.lower().startswith("date:"):
            server_date = email.utils.parsedate_to_datetime(line[5:].strip()).timestamp()
    try:
        return json.loads(payload), server_date
    except ValueError:
        return None, server_date


def latest(js, sid):
    for s in (js or {}).get("Results", {}).get("series", []):
        if s.get("seriesID") == sid and s.get("data"):
            d = s["data"][0]
            return f"{d['year']}-{d['period']}", float(d["value"])
    return None, None


def forecast_for(kind, release_utc):
    path = os.path.join(ROOT, "data", "consensus_log.csv")
    if not os.path.exists(path):
        return {}
    want = {"NFP": ("Non-Farm Employment Change", "Unemployment Rate"), "CPI": ("Core CPI m/m",)}[kind]
    t = time.strftime("%Y-%m-%d %H:%M", time.gmtime(release_utc))
    out = {}
    for r in csv.DictReader(open(path)):
        if r["event_utc"] == t and r["title"] in want and r["forecast"]:
            out[r["title"]] = r["forecast"]                     # the last logged forecast before the release wins
    return out


def num(x):
    x = x.replace("%", "").replace("K", "").replace(",", "").strip()
    return float(x)


def main():
    kind, day = sys.argv[1], sys.argv[2]
    key = os.environ.get("BLS_API_KEY", "")
    t_rel = calendar.timegm(datetime.datetime.fromisoformat(day + "T08:30").replace(tzinfo=NY).utctimetuple())
    sids = SERIES[kind]
    js, sd = bls(sids, key)
    if js and js.get("status") != "REQUEST_SUCCEEDED":
        print("BLS API refused:", js.get("message"))
    before = latest(js, sids[0])[0]
    prev = {sid: latest(js, sid)[1] for sid in sids}          # cached before the release, as a live bot would
    print("period before release:", before, prev)
    while time.time() < t_rel - 15:
        time.sleep(min(30, t_rel - 15 - time.time()))
    polls, seen, status, offsets = 0, None, "timeout", []
    while time.time() < t_rel + 300:
        t_send = time.time()
        js, sd = bls(sids, key)
        t_recv = time.time()
        polls += 1
        if sd:
            offsets.append(sd - (t_send + t_recv) / 2)
        if js and js.get("status") != "REQUEST_SUCCEEDED":
            status = "refused: " + " ".join(js.get("message", []))[:120]
            break
        per, val = latest(js, sids[0])
        if per and per != before:
            seen = (t_recv, per, {s: latest(js, s)[1] for s in sids})
            status = "ok"
            break
        time.sleep(max(0.0, 1.0 - (time.time() - t_send)))
    fc = forecast_for(kind, t_rel)
    score = ""
    if seen and fc:
        v = seen[2]
        try:
            if kind == "CPI" and "Core CPI m/m" in fc and prev.get(sids[0]):
                mom = round(100 * (v[sids[0]] / prev[sids[0]] - 1), 1)        # BLS publishes MoM rounded to 0.1
                score = f"{mom - num(fc['Core CPI m/m']):+.1f}"
            elif kind == "NFP" and "Non-Farm Employment Change" in fc and prev.get(sids[0]):
                ch = v[sids[0]] - prev[sids[0]]                               # thousands (prior month as cached)
                du = v[sids[1]] - num(fc["Unemployment Rate"]) if "Unemployment Rate" in fc else 0.0
                score = f"{ch - num(fc['Non-Farm Employment Change']) - 100 * du:+.1f}"
        except (ValueError, KeyError, TypeError):
            score = ""
    row = {"kind": kind, "release_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(t_rel)),
           "first_seen_utc": f"{datetime.datetime.fromtimestamp(seen[0], datetime.timezone.utc):%Y-%m-%d %H:%M:%S.%f}"[:-3] if seen else "",
           "seconds_after_release": f"{seen[0] - t_rel:.3f}" if seen else "",
           "clock_offset_s": f"{sorted(offsets)[len(offsets) // 2]:+.2f}" if offsets else "", "polls": polls,
           "period": seen[1] if seen else "", "values": json.dumps(seen[2]) if seen else "", "forecast": json.dumps(fc),
           "surprise_score": score, "status": status}
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)
    print(row)


if __name__ == "__main__":
    main()
