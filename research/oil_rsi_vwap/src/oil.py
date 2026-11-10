"""US oil (USOILm) RSI + VWAP study engine (PROTOCOL.md). Real bid/ask fills; session VWAP weighted by tick volume.

Reuses the tested indicator, statistics and random-benchmark functions of research/rsi_vwap_study (read-only).
"""
import bisect
import csv
import dataclasses
import gzip
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "rsi_vwap_study", "src"))
import study as S

SLIP = {"primary": 0.0002, "stress": 0.0005}
SWAP_PER_DAY = {"primary": 0.0, "stress": 0.0002}
MIN_DAILY_BARS = 200
SESSION_GAP = 7200      # a missing 1H candle (>= 1 hour without quotes) starts a new session


@dataclasses.dataclass(frozen=True)
class Trade:
    signal_index: int
    entry_time: int
    exit_time: int
    direction: int
    entry: float
    risk: float
    r_gross: float          # includes the measured spread (entry and exit at the executable side)
    reason: str
    regime: str

    def r(self, cost):
        days = (self.exit_time - self.entry_time) / 86400
        return self.r_gross - (SLIP[cost] + SWAP_PER_DAY[cost] * days) * self.entry / self.risk

    @property
    def hold_hours(self):
        return (self.exit_time - self.entry_time) / 3600


def load_15m(path):
    cols = {k: [] for k in ("t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "n")}
    with gzip.open(path, "rt") as f:
        for r in csv.DictReader(f):
            cols["t"].append(int(r["t"]))
            for k in ("bo", "bh", "bl", "bc", "ao", "ah", "al", "ac"):
                cols[k].append(float(r[k]))
            cols["n"].append(int(r["ticks"]))
    return cols


def aggregate(t, o, h, l, c, v, step):
    out = S.Bars([], [], [], [], [], [])
    for i in range(len(t)):
        b = t[i] // step * step
        if out.t and out.t[-1] == b:
            out.h[-1] = max(out.h[-1], h[i])
            out.l[-1] = min(out.l[-1], l[i])
            out.c[-1] = c[i]
            out.v[-1] += v[i]
        else:
            for arr, val in ((out.t, b), (out.o, o[i]), (out.h, h[i]), (out.l, l[i]), (out.c, c[i]), (out.v, v[i])):
                arr.append(val)
    return out


def session_vwap(t, h, l, c, v):
    out, sess = [None] * len(t), [0] * len(t)
    pv = vol = 0.0
    s = 0
    for i in range(len(t)):
        if i == 0 or t[i] - t[i - 1] >= SESSION_GAP:
            pv = vol = 0.0
            s += 1
        sess[i] = s
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vol += v[i]
        out[i] = pv / vol if vol > 0 else None
    return out, sess


class OilAsset:
    def __init__(self, path_15m, last_complete_15m=None):
        q = load_15m(path_15m)
        self.q = q
        self.p_idx = {t: j for j, t in enumerate(q["t"])}
        self.e = aggregate(q["t"], q["bo"], q["bh"], q["bl"], q["bc"], q["n"], 3600)
        # the last hour is dropped if the data ends inside it
        if self.e.t and self.e.t[-1] + 3600 > q["t"][-1] + 900:
            for arr in (self.e.t, self.e.o, self.e.h, self.e.l, self.e.c, self.e.v):
                arr.pop()
        self.e_idx = {t: i for i, t in enumerate(self.e.t)}
        self.d = aggregate(self.e.t, self.e.o, self.e.h, self.e.l, self.e.c, self.e.v, 86400)
        self.rsi = S.rsi(self.e.c)
        self.atr = S.atr(self.e.h, self.e.l, self.e.c)
        self.vwap, self.session = session_vwap(self.e.t, self.e.h, self.e.l, self.e.c, self.e.v)
        self.d_e200 = S.ema_from_first(self.d.c, 200)
        self._tables = {}

    def signals(self, rule, d):
        E, r, w = self.e, self.rsi, self.vwap
        out = [False] * len(E.t)
        for i in range(1, len(E.t)):
            if None in (r[i], r[i - 1], w[i], w[i - 1]):
                continue
            if rule == "V1_VWAP_MOMENTUM":
                cross = (E.c[i] - w[i]) * d > 0 and (E.c[i - 1] - w[i - 1]) * d <= 0
                out[i] = self.session[i] == self.session[i - 1] and cross and (r[i] - 50) * d > 0
            elif rule == "V2_RSI_REVERSION":
                level = 30 if d > 0 else 70
                out[i] = (r[i - 1] - level) * d < 0 <= (r[i] - level) * d and (E.c[i] - w[i]) * d < 0
            else:
                raise ValueError(rule)
        return out

    def regime(self, t):
        k = bisect.bisect_right(self.d.t, t - 86400) - 1     # last complete UTC day
        if k < MIN_DAILY_BARS:
            return "undefined"
        e, c = self.d_e200, self.d.c[k]
        slope = e[k] - e[k - 20]
        return "bull" if c > e[k] and slope > 0 else "bear" if c < e[k] and slope < 0 else "sideways"

    def simulate(self, i, d, exit_rule, delay=0):
        q, E = self.q, self.e
        t_close = E.t[i] + 3600
        j = self.p_idx.get(t_close)
        a = self.atr[i]
        if j is None or a is None or a <= 0:
            return None      # no quote right at the signal close (session break): no trade
        j += delay
        if j >= len(q["t"]):
            return None
        long = d > 0
        entry = q["ao"][j] if long else q["bo"][j]
        risk = S.STOP_ATR * a
        sl, tp, best = entry - d * risk, entry + d * S.SYM_TARGET_ATR * a, entry
        # the side that closes the position: bid for a long, ask for a short
        xo, xh, xl, xc = (q["bo"], q["bh"], q["bl"], q["bc"]) if long else (q["ao"], q["ah"], q["al"], q["ac"])
        reg = self.regime(t_close)
        while j < len(q["t"]):
            adverse, favor = (xl[j], xh[j]) if long else (xh[j], xl[j])
            if (adverse - sl) * d <= 0:
                px = xo[j] if (xo[j] - sl) * d < 0 else sl
                return Trade(i, t_close, q["t"][j] + 900, d, entry, risk, (px - entry) * d / risk, "stop", reg)
            bar_close = q["t"][j] + 900
            if exit_rule == "SYM":
                if (favor - tp) * d >= 0:
                    return Trade(i, t_close, bar_close, d, entry, risk, (tp - entry) * d / risk, "target", reg)
                if bar_close - t_close >= S.SYM_MAX_HOURS * 3600:
                    return Trade(i, t_close, bar_close, d, entry, risk, (xc[j] - entry) * d / risk, "time", reg)
            elif bar_close % 3600 == 0:
                k = self.e_idx.get(bar_close - 3600)
                if k is not None and self.atr[k] is not None:
                    best = max(best, xc[j]) if long else min(best, xc[j])
                    trail = best - d * S.TRAIL_ATR * self.atr[k]
                    if (trail - sl) * d > 0:
                        sl = trail
            j += 1
        return None

    def table(self, d, exit_rule):
        key = (d, exit_rule)
        if key not in self._tables:
            self._tables[key] = [self.simulate(i, d, exit_rule) for i in range(len(self.e.t))]
        return self._tables[key]

    def run(self, rule, d, exit_rule, w0, w1):
        sig, tab, E = self.signals(rule, d), self.table(d, exit_rule), self.e
        out, i = [], bisect.bisect_left(E.t, w0 - 3600)
        while i < len(E.t) and E.t[i] + 3600 < w1:
            tr = tab[i] if sig[i] and E.t[i] + 3600 >= w0 else None
            if tr is None:
                i += 1
                continue
            out.append(tr)
            i = bisect.bisect_left(E.t, tr.exit_time - 3600 + 1)
        return out
