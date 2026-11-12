"""Score the paper trades for every captured release (run a day after the release, when the Exness tick archive has
it). Entry: the first Exness quote at least EXEC_DELAY seconds after our machine first saw the number (capture.py).
Exit: first quote 15 minutes after the release. Textbook direction (hot -> SELL gold, EUR/USD, GBP/USD; BUY USD/JPY).
R = 2 x the mid-price range of the hour before. Also records the 1-second 'theoretical best' for comparison.
Writes data/live_ledger.csv (append-only). No orders are ever placed.
usage: TICK_WORK=<dir> python evaluate.py"""
import calendar
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import replicate_2016 as RP  # noqa: E402
import ticks as TK  # noqa: E402

EXEC_DELAY = 0.5
CAPT = os.path.join(ROOT, "data", "live_captures.csv")
LEDGER = os.path.join(ROOT, "data", "live_ledger.csv")
FIELDS = ["release_utc", "kind", "market", "surprise_score", "seconds_after_release", "entry_delay_s", "direction",
          "r_achieved", "r_theoretical_1s"]


def ts(s):
    base, _, frac = s.partition(".")
    return calendar.timegm(__import__("time").strptime(base, "%Y-%m-%d %H:%M:%S")) + (float("0." + frac) if frac else 0.0)


def trade(win, t, entry_t, d):
    tt, b, a = win
    mid = (b + a) / 2
    pre = mid[(tt >= t - 3600) & (tt < t)]
    i, j = TK.first_at(tt, entry_t), TK.first_at(tt, t + 900)
    if len(pre) < 10 or i is None or j is None or pre.max() <= pre.min():
        return None
    R = 2 * (pre.max() - pre.min())
    return (b[j] - a[i]) / R if d > 0 else (b[i] - a[j]) / R


def main():
    if not os.path.exists(CAPT):
        print("no captures yet")
        return
    done = {(r["release_utc"], r["market"]) for r in csv.DictReader(open(LEDGER))} if os.path.exists(LEDGER) else set()
    rows = [r for r in csv.DictReader(open(CAPT)) if r["status"] == "ok" and r["surprise_score"] not in ("", "+0.0", "-0.0")]
    new = []
    for r in rows:
        t = int(ts(r["release_utc"]))
        seen = ts(r["first_seen_utc"]) - float(r["clock_offset_s"] or 0)      # correct our clock to the server's
        for mkt, hot_dir in TK.MARKETS.items():
            if (r["release_utc"], mkt) in done:
                continue
            win = RP.windows(mkt, [t], os.environ["TICK_WORK"]).get(t)
            if win is None or len(win[0]) < 20:
                continue
            d = int(np.sign(float(r["surprise_score"]))) * hot_dir
            ra = trade(win, t, seen + EXEC_DELAY, d)
            r1 = trade(win, t, t + 1, d)
            new.append({"release_utc": r["release_utc"], "kind": r["kind"], "market": mkt, "surprise_score": r["surprise_score"],
                        "seconds_after_release": r["seconds_after_release"], "entry_delay_s": f"{seen + EXEC_DELAY - t:.2f}",
                        "direction": "BUY" if d > 0 else "SELL", "r_achieved": "" if ra is None else f"{ra:+.3f}",
                        "r_theoretical_1s": "" if r1 is None else f"{r1:+.3f}"})
    if new:
        exists = os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, FIELDS)
            if not exists:
                w.writeheader()
            w.writerows(new)
    for x in new:
        print(x)
    print(len(new), "new paper trades scored")


if __name__ == "__main__":
    main()
