"""Prospective PAPER test of the exploratory gold ADP-contrarian rule, locked in ../FORWARD_TEST_PLAN.md (section C).
No orders are placed. Run daily; it scores each eligible NFP release once, after the Exness archive has the day.

Locked rule (audit variant 'XAUUSDm | candles 2020-26 | entry T-30m | exit T+60m | reversed direction'):
  signal  = sign(ADP actual change - ADP consensus) for the ADP report of the NFP's reference month
            actual: ALFRED ADPMNUSNERSA, latest vintage dated before the NFP day, last obs month == reference month,
                    change = last - previous obs (thousands); consensus: research/news_surprise/data/consensus_log.csv,
                    title 'ADP Non-Farm Employment Change', last row first seen before the ADP release
  direction: ADP above consensus -> BUY gold; below -> SELL gold; equal or missing input -> no trade (logged)
  entry   : open of the Exness XAUUSDm 15-minute candle starting at T-30 min (T = NFP 08:30 New York), ask for BUY / bid for SELL
  exit    : open of the 15-minute candle starting at T+60 min, bid for BUY / ask for SELL; no stop
  R       : 2 x (highest bid high - lowest bid low) of the three 15-minute candles before entry
  costs   : quoted bid/ask only (primary); secondary: minus 1 x the entry candle's spread (stress)
Writes ../data/forward_adp_contrarian.csv (append-only)."""
import calendar
import csv
import datetime
import io
import os
import subprocess
import sys
import time
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
NY = zoneinfo.ZoneInfo("America/New_York")
LOG = os.path.join(ROOT, "data", "consensus_log.csv")
LEDGER = os.path.join(ROOT, "data", "forward_adp_contrarian.csv")
CACHE = os.path.join(ROOT, "live", "cache")
FIELDS = ["nfp_release_utc", "reference_month", "adp_release_utc", "adp_actual_k", "adp_consensus_k", "signal", "direction",
          "entry_utc", "entry_price", "exit_utc", "exit_price", "risk_R_price", "r_primary", "r_stress", "status"]
FIRST_ELIGIBLE = "2026-12-01"
MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}


def num(x):
    x = x.replace("K", "").replace(",", "").replace("%", "").strip()
    return float(x)


def alfred_adp(nfp_day, ref):
    vint = (nfp_day - datetime.timedelta(days=1)).isoformat()
    out = subprocess.run(["curl", "-sSf", "-m", "40", f"https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=ADPMNUSNERSA&vintage_date={vint}"],
                         capture_output=True, text=True)
    rows = [l.split(",") for l in out.stdout.strip().splitlines()[1:] if "," in l]
    rows = [(r[0], float(r[1])) for r in rows if r[1] not in ("", ".")]
    if len(rows) < 2 or rows[-1][0][:7] != f"{ref[0]}-{ref[1]:02d}":
        return None
    return (rows[-1][1] - rows[-2][1]) / 1000.0


def bars_for(day):
    os.makedirs(CACHE, exist_ok=True)
    ym = day.strftime("%Y-%m")
    out = os.path.join(CACHE, f"XAUUSDm_{ym}.csv.gz")
    if not os.path.exists(out):
        subprocess.run([sys.executable, os.path.join(RESEARCH, "oil_rsi_vwap", "src", "build_bars.py"), "XAUUSDm", ym, ym, out,
                        os.path.join(CACHE, "parts"), "1"], check=True, capture_output=True)
    import gzip
    rows = {}
    with gzip.open(out, "rt") as f:
        for r in csv.DictReader(f):
            rows[int(r["t"])] = {k: float(r[k]) for k in ("bo", "bh", "bl", "ao")}
    return rows


def main():
    if not os.path.exists(LOG):
        print("no consensus log yet")
        return
    log = list(csv.DictReader(open(LOG)))
    done = {r["nfp_release_utc"] for r in csv.DictReader(open(LEDGER))} if os.path.exists(LEDGER) else set()
    nfps = sorted({r["event_utc"] for r in log if r["title"] == "Non-Farm Employment Change" and r["event_utc"] >= FIRST_ELIGIBLE})
    now = time.time()
    new = []
    for ev in nfps:
        T = calendar.timegm(time.strptime(ev, "%Y-%m-%d %H:%M"))
        if ev in done or now < T + 36 * 3600:                     # wait until the archive has the day
            continue
        day = datetime.datetime.fromtimestamp(T, NY).date()
        ref = (day.year, day.month - 1) if day.month > 1 else (day.year - 1, 12)
        row = {k: "" for k in FIELDS}
        row.update(nfp_release_utc=ev, reference_month=f"{ref[0]}-{ref[1]:02d}")
        adp_rows = [r for r in log if r["title"] == "ADP Non-Farm Employment Change" and ev[:10] > r["event_utc"][:10] >= (day - datetime.timedelta(days=10)).isoformat()]
        if not adp_rows:
            row["status"] = "missing: ADP release not in the consensus log"
            new.append(row)
            continue
        adp_ev = max(r["event_utc"] for r in adp_rows)
        before = [r for r in adp_rows if r["event_utc"] == adp_ev and r["first_seen_utc"] < adp_ev and r["forecast"]]
        actual = alfred_adp(day, ref)
        row.update(adp_release_utc=adp_ev)
        if not before or actual is None:
            row["status"] = "missing: " + ("ADP consensus not logged before release" if not before else "ADP actual not on ALFRED for the reference month")
            new.append(row)
            continue
        cons = num(before[-1]["forecast"])
        sig = (actual > cons) - (actual < cons)
        row.update(adp_actual_k=f"{actual:.1f}", adp_consensus_k=f"{cons:.1f}", signal=str(sig))
        if sig == 0:
            row["status"] = "no trade: ADP equal to consensus"
            new.append(row)
            continue
        d = sig                                            # reversed textbook: ADP beat -> BUY gold
        bars = bars_for(day)
        te, tx = T - 1800, T + 3600
        prev = [bars.get(te - 900 * k) for k in (1, 2, 3)]
        if te not in bars or tx not in bars or None in prev:
            row["status"] = "missing: Exness candle absent at entry, exit or risk window"
            new.append(row)
            continue
        hi, lo = max(p["bh"] for p in prev), min(p["bl"] for p in prev)
        Rp = 2 * (hi - lo)
        entry = bars[te]["ao"] if d > 0 else bars[te]["bo"]
        ex = bars[tx]["bo"] if d > 0 else bars[tx]["ao"]
        r = (ex - entry) * d / Rp
        spread = bars[te]["ao"] - bars[te]["bo"]
        row.update(direction="BUY" if d > 0 else "SELL", entry_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(te)),
                   entry_price=f"{entry:.3f}", exit_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(tx)), exit_price=f"{ex:.3f}",
                   risk_R_price=f"{Rp:.3f}", r_primary=f"{r:+.4f}", r_stress=f"{r - spread / Rp:+.4f}", status="ok")
        new.append(row)
    if new:
        exists = os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, FIELDS)
            if not exists:
                w.writeheader()
            w.writerows(new)
    for r in new:
        print(r)
    print(len(new), "new rows")


if __name__ == "__main__":
    main()
