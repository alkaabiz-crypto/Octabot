"""The frozen engine's signal logic applied to Exness BTCUSDm quotes (read-only use of the frozen engine).

Bars come from research/exness_validation/data/bars15m (15m bid and ask candles built from the Exness public tick
archive by another session, on the pinned frozen commit). 1H, 4H and 1D BID candles are aggregated on UTC
boundaries and passed through the frozen engine's own ``build`` so every indicator is computed by frozen code.
Signals use the BID (what a chart shows). A long entry pays the ASK open; stops trigger and fill on the BID.
"""
import csv
import glob
import gzip
import os

import config
import frozen


def load_15m(bars_dir=None):
    bars_dir = bars_dir or config.EXNESS_BARS_DIR
    rows = []
    for path in sorted(glob.glob(os.path.join(bars_dir, "BTCUSDm_*.csv.gz"))):
        with gzip.open(path, "rt") as f:
            for r in csv.DictReader(f):
                rows.append((int(r["open_time_utc"]), float(r["bid_o"]), float(r["bid_h"]), float(r["bid_l"]), float(r["bid_c"]),
                             float(r["ask_o"]), float(r["ask_h"]), float(r["ask_l"]), float(r["ask_c"]), int(r["ticks"])))
    rows.sort()
    dedup = []
    for r in rows:
        if not dedup or r[0] != dedup[-1][0]:
            dedup.append(r)
    return dedup


def aggregate(rows, step):
    out = []
    for t, o, h, l, c, *_rest in rows:
        b = t // step * step
        if out and out[-1][0] == b:
            last = out[-1]
            last[2] = max(last[2], h)
            last[3] = min(last[3], l)
            last[4] = c
            last[5] += 1
        else:
            out.append([b, o, h, l, c, 1])
    return out


def complete_only(agg, expected_parts, last_t):
    """Keep aggregated bars that are complete in time. The final bar is dropped if the data ends inside it."""
    return [b for b in agg if b[0] + expected_parts * 900 <= last_t + 900]


def build_lab(bars_dir=None):
    eng = frozen.engine_module()
    rows = load_15m(bars_dir)
    last_t = rows[-1][0]
    raw = {"15m": [[r[0], r[1], r[2], r[3], r[4], r[9]] for r in rows]}
    for tf, step, parts in (("1h", 3600, 4), ("4h", 14400, 16), ("1d", 86400, 96)):
        raw[tf] = [b[:6] for b in complete_only(aggregate(rows, step), parts, last_t)]
    lab = object.__new__(eng.Lab)
    lab.raw = raw
    lab.B = {tf: eng.build(cs) for tf, cs in raw.items()}
    lab.p_idx = {tt: i for i, tt in enumerate(lab.B["15m"]["t"])}
    lab.audit = {"htf_closed": [0, 0], "daily_closed": [0, 0], "entry_after_signal": [0, 0]}
    lab.sig_cache = {}
    ask = {"o": [r[5] for r in rows], "h": [r[6] for r in rows], "l": [r[7] for r in rows], "c": [r[8] for r in rows]}
    return lab, ask
