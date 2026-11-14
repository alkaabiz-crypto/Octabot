"""Indicator scan engine (PROTOCOL.md). Builds on research/oil_rsi_vwap (bid/ask data, sessions) read-only."""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "oil_rsi_vwap", "src"))
import oil
import study as S

INDICATORS = ("RSI14_REVERSION", "RSI2_EXTREME", "BOLLINGER_REENTRY", "STOCHASTIC", "MACD", "EMA_9_21",
              "DONCHIAN_20", "VWAP_MOMENTUM", "SUPERTREND", "CCI_20")
EXITS = {  # stop ATR, target ATR (None = trailing), time limit hours (None = none)
    "HW": (2.0, 1.0, 24),
    "SYM": (2.0, 2.0, 48),
    "TRAIL": (2.0, None, None),
}
TRAIL_ATR = 3.0


# ------------------------------------------------------------------------------------------- indicators
def sma(x, n):
    out, s = [None] * len(x), 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def ema(x, n):
    out = [None] * len(x)
    if len(x) < n:
        return out
    k, prev = 2 / (n + 1), sum(x[:n]) / n
    out[n - 1] = prev
    for i in range(n, len(x)):
        prev += k * (x[i] - prev)
        out[i] = prev
    return out


def bollinger(c, n=20, k=2.0):
    up, lo = [None] * len(c), [None] * len(c)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1:i + 1]
        m = sum(w) / n
        sd = math.sqrt(sum((v - m) ** 2 for v in w) / n)
        up[i], lo[i] = m + k * sd, m - k * sd
    return up, lo


def stochastic(h, l, c, n=14, smooth_k=3, smooth_d=3):
    raw = [None] * len(c)
    for i in range(n - 1, len(c)):
        hh, ll = max(h[i - n + 1:i + 1]), min(l[i - n + 1:i + 1])
        raw[i] = 50.0 if hh == ll else (c[i] - ll) / (hh - ll) * 100
    def smooth(x, m):
        out = [None] * len(x)
        for i in range(len(x)):
            w = x[i - m + 1:i + 1] if i >= m - 1 else []
            if len(w) == m and None not in w:
                out[i] = sum(w) / m
        return out
    k = smooth(raw, smooth_k)
    return k, smooth(k, smooth_d)


def macd(c, f=12, s=26, sig=9):
    ef, es = ema(c, f), ema(c, s)
    line = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    first = next(i for i, v in enumerate(line) if v is not None)
    sg = [None] * len(c)
    sg[first:] = ema(line[first:], sig)
    return line, sg


def supertrend(h, l, c, n=10, mult=3.0):
    """Standard Supertrend on Wilder ATR. Returns +1 (up) / -1 (down) / None per bar."""
    a = S.atr(h, l, c, n)
    trend = [None] * len(c)
    fu = fl = None
    t = 1
    for i in range(len(c)):
        if a[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2
        bu, bl = hl2 + mult * a[i], hl2 - mult * a[i]
        if fu is None:
            fu, fl = bu, bl
        else:
            fu = bu if (bu < fu or c[i - 1] > fu) else fu
            fl = bl if (bl > fl or c[i - 1] < fl) else fl
        if t == 1 and c[i] < fl:
            t = -1
        elif t == -1 and c[i] > fu:
            t = 1
        trend[i] = t
    return trend


def cci(h, l, c, n=20):
    tp = [(h[i] + l[i] + c[i]) / 3 for i in range(len(c))]
    out = [None] * len(c)
    for i in range(n - 1, len(c)):
        w = tp[i - n + 1:i + 1]
        m = sum(w) / n
        md = sum(abs(v - m) for v in w) / n
        out[i] = 0.0 if md == 0 else (tp[i] - m) / (0.015 * md)
    return out


def crosses_up(x, y, i):
    return None not in (x[i], x[i - 1], y[i], y[i - 1]) and x[i - 1] <= y[i - 1] and x[i] > y[i]


# ------------------------------------------------------------------------------------------- asset
class ScanAsset(oil.OilAsset):
    def __init__(self, path):
        super().__init__(path)
        E = self.e
        self.rsi2 = S.rsi(E.c, 2)
        self.bb_up, self.bb_lo = bollinger(E.c)
        self.st_k, self.st_d = stochastic(E.h, E.l, E.c)
        self.macd, self.macd_sig = macd(E.c)
        self.e9, self.e21 = ema(E.c, 9), ema(E.c, 21)
        self.st = supertrend(E.h, E.l, E.c)
        self.cci = cci(E.h, E.l, E.c)
        hh, ll = [None] * len(E.c), [None] * len(E.c)
        for i in range(20, len(E.c)):
            hh[i], ll[i] = max(E.h[i - 20:i]), min(E.l[i - 20:i])
        self.dc_hi, self.dc_lo = hh, ll

    def scan_signals(self, name, d):
        """Signal on each closed 1H candle for indicator ``name`` in direction d (+1 BUY, -1 SELL)."""
        if name == "VWAP_MOMENTUM":
            return self.signals("V1_VWAP_MOMENTUM", d)
        c, n = self.e.c, len(self.e.c)
        out = [False] * n

        def up_through(x, level, i):        # x crosses up through a constant level
            return x[i] is not None and x[i - 1] is not None and x[i - 1] < level <= x[i]

        def down_through(x, level, i):
            return x[i] is not None and x[i - 1] is not None and x[i - 1] > level >= x[i]

        for i in range(1, n):
            if name == "RSI14_REVERSION":
                v = up_through(self.rsi, 30, i) if d > 0 else down_through(self.rsi, 70, i)
            elif name == "RSI2_EXTREME":
                v = down_through(self.rsi2, 10, i) if d > 0 else up_through(self.rsi2, 90, i)
            elif name == "BOLLINGER_REENTRY":
                v = crosses_up(c, self.bb_lo, i) if d > 0 else crosses_up(self.bb_up, c, i)
            elif name == "STOCHASTIC":
                k, dd = self.st_k, self.st_d
                if d > 0:
                    v = crosses_up(k, dd, i) and k[i - 1] < 20 and dd[i - 1] < 20
                else:
                    v = crosses_up(dd, k, i) and k[i - 1] > 80 and dd[i - 1] > 80
            elif name == "MACD":
                v = crosses_up(self.macd, self.macd_sig, i) if d > 0 else crosses_up(self.macd_sig, self.macd, i)
            elif name == "EMA_9_21":
                v = crosses_up(self.e9, self.e21, i) if d > 0 else crosses_up(self.e21, self.e9, i)
            elif name == "DONCHIAN_20":
                v = crosses_up(c, self.dc_hi, i) if d > 0 else crosses_up(self.dc_lo, c, i)
            elif name == "SUPERTREND":
                v = self.st[i] is not None and self.st[i - 1] is not None and self.st[i - 1] == -d and self.st[i] == d
            elif name == "CCI_20":
                v = up_through(self.cci, -100, i) if d > 0 else down_through(self.cci, 100, i)
            else:
                raise ValueError(name)
            out[i] = bool(v)
        return out

    def simulate(self, i, d, exit_rule, delay=0):
        if exit_rule == "TRAIL":
            return super().simulate(i, d, "TRAIL", delay)
        stop_atr, tgt_atr, max_h = EXITS[exit_rule]
        q, E = self.q, self.e
        t_close = E.t[i] + 3600
        j = self.p_idx.get(t_close)
        a = self.atr[i]
        if j is None or a is None or a <= 0:
            return None
        long = d > 0
        entry = q["ao"][j] if long else q["bo"][j]
        risk = stop_atr * a
        sl, tp = entry - d * risk, entry + d * tgt_atr * a
        xo, xh, xl, xc = (q["bo"], q["bh"], q["bl"], q["bc"]) if long else (q["ao"], q["ah"], q["al"], q["ac"])
        reg = self.regime(t_close)
        while j < len(q["t"]):
            adverse, favor = (xl[j], xh[j]) if long else (xh[j], xl[j])
            if (adverse - sl) * d <= 0:
                px = xo[j] if (xo[j] - sl) * d < 0 else sl
                return oil.Trade(i, t_close, q["t"][j] + 900, d, entry, risk, (px - entry) * d / risk, "stop", reg)
            if (favor - tp) * d >= 0:
                px = xo[j] if (xo[j] - tp) * d > 0 else tp     # a gap beyond the target fills at the open
                return oil.Trade(i, t_close, q["t"][j] + 900, d, entry, risk, (px - entry) * d / risk, "target", reg)
            if q["t"][j] + 900 - t_close >= max_h * 3600:
                return oil.Trade(i, t_close, q["t"][j] + 900, d, entry, risk, (xc[j] - entry) * d / risk, "time", reg)
            j += 1
        return None

    def run_signals(self, sig, d, exit_rule, w0, w1):
        import bisect
        tab, E = self.table(d, exit_rule), self.e
        out, i = [], bisect.bisect_left(E.t, w0 - 3600)
        while i < len(E.t) and E.t[i] + 3600 < w1:
            tr = tab[i] if sig[i] and E.t[i] + 3600 >= w0 else None
            if tr is None:
                i += 1
                continue
            out.append(tr)
            i = bisect.bisect_left(E.t, tr.exit_time - 3600 + 1)
        return out
