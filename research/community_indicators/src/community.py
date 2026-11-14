"""Community-made TradingView indicators, re-implemented from their published open-source logic at default settings.

Every value at 1H candle i uses candles 0..i only (none of these indicators repaints). Built on the indicator-scan
engine (research/indicator_scan, read-only), which supplies bid/ask data, exits and costs.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "indicator_scan", "src"))  # scan.py, run_scan.py
import scan
import study as S

INDICATORS = ("UT_BOT", "SSL_CHANNEL", "SQUEEZE_MOMENTUM", "WAVETREND", "CHANDELIER_EXIT", "HULL_SUITE", "RANGE_FILTER", "QQE")


def ema_sparse(x, n):
    """EMA (SMA seed) over a series that may begin with None values."""
    first = next((i for i, v in enumerate(x) if v is not None), None)
    out = [None] * len(x)
    if first is not None:
        out[first:] = scan.ema(x[first:], n)
    return out


def sma_sparse(x, n):
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if None not in w:
            out[i] = sum(w) / n
    return out


def wma(x, n):
    out, den = [None] * len(x), n * (n + 1) / 2
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if None not in w:
            out[i] = sum(v * (k + 1) for k, v in enumerate(w)) / den
    return out


def linreg_last(y):
    """Value at the last point of the least-squares line through y (Pine ta.linreg(src, len, 0))."""
    n = len(y)
    xm, ym = (n - 1) / 2, sum(y) / n
    sxy = sum((k - xm) * (v - ym) for k, v in enumerate(y))
    sxx = sum((k - xm) ** 2 for k in range(n))
    return ym + sxy / sxx * (n - 1 - xm)


def ut_bot(c, atr10, key=1.0):
    stop = [None] * len(c)
    prev = 0.0
    for i in range(len(c)):
        if atr10[i] is None:
            continue
        loss = key * atr10[i]
        p1 = c[i - 1] if i else c[i]
        if c[i] > prev and p1 > prev:
            s = max(prev, c[i] - loss)
        elif c[i] < prev and p1 < prev:
            s = min(prev, c[i] + loss)
        elif c[i] > prev:
            s = c[i] - loss
        else:
            s = c[i] + loss
        stop[i] = prev = s
    return stop


def ssl_channel(h, l, c, n=10):
    sh, sl = scan.sma(h, n), scan.sma(l, n)
    hlv, out = 0, [None] * len(c)
    for i in range(len(c)):
        if sh[i] is None:
            continue
        hlv = 1 if c[i] > sh[i] else -1 if c[i] < sl[i] else hlv
        out[i] = hlv if hlv != 0 else None
    return out


def squeeze_momentum(h, l, c, n=20, mult_kc=1.5):
    """LazyBear Squeeze Momentum. As published, the Bollinger width uses multKC (1.5), not mult (2.0)."""
    m = len(c)
    basis = scan.sma(c, n)
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, m)]
    rng = scan.sma(tr, n)
    on, off, val = [None] * m, [None] * m, [None] * m
    diff = [None] * m
    for i in range(n - 1, m):
        w = c[i - n + 1:i + 1]
        sd = math.sqrt(sum((v - basis[i]) ** 2 for v in w) / n)
        ub, lb = basis[i] + mult_kc * sd, basis[i] - mult_kc * sd
        uk, lk = basis[i] + rng[i] * mult_kc, basis[i] - rng[i] * mult_kc
        on[i] = lb > lk and ub < uk
        off[i] = lb < lk and ub > uk
        mid = (max(h[i - n + 1:i + 1]) + min(l[i - n + 1:i + 1])) / 2
        diff[i] = c[i] - (mid + basis[i]) / 2
    for i in range(2 * n - 2, m):
        val[i] = linreg_last(diff[i - n + 1:i + 1])
    return on, off, val


def wavetrend(h, l, c, n1=10, n2=21):
    ap = [(h[i] + l[i] + c[i]) / 3 for i in range(len(c))]
    esa = scan.ema(ap, n1)
    dev = [None if e is None else abs(a - e) for a, e in zip(ap, esa)]
    d = ema_sparse(dev, n1)
    ci = [None if e is None or dd is None or dd == 0 else (a - e) / (0.015 * dd) for a, e, dd in zip(ap, esa, d)]
    wt1 = ema_sparse(ci, n2)
    return wt1, sma_sparse(wt1, 4)


def chandelier(h, l, c, atr22, n=22, mult=3.0):
    m = len(c)
    direction = [None] * m
    ls_prev = ss_prev = None
    dr = 1
    for i in range(m):
        if atr22[i] is None or i < n - 1:
            continue
        a = mult * atr22[i]
        ls = max(c[i - n + 1:i + 1]) - a
        ss = min(c[i - n + 1:i + 1]) + a
        lsp = ls if ls_prev is None else ls_prev
        ssp = ss if ss_prev is None else ss_prev
        ls = max(ls, lsp) if c[i - 1] > lsp else ls
        ss = min(ss, ssp) if c[i - 1] < ssp else ss
        dr = 1 if c[i] > ssp else -1 if c[i] < lsp else dr
        direction[i] = dr
        ls_prev, ss_prev = ls, ss
    return direction


def hull(c, n=55):
    half, full = wma(c, n // 2), wma(c, n)
    raw = [None if a is None or b is None else 2 * a - b for a, b in zip(half, full)]
    return wma(raw, round(math.sqrt(n)))


def range_filter(c, per=100, mult=3.0):
    m = len(c)
    absd = [0.0] + [abs(c[i] - c[i - 1]) for i in range(1, m)]
    avrng = scan.ema(absd, per)
    smrng = ema_sparse(avrng, per * 2 - 1)
    filt = [None] * m
    up = dn = 0
    cond = 0
    sig = [0] * m
    prev_f = None
    for i in range(m):
        if smrng[i] is None:
            continue
        r = smrng[i] * mult
        pf = prev_f if prev_f is not None else c[i]
        if c[i] > pf:
            f = max(c[i] - r, pf)
        else:
            f = min(c[i] + r, pf)
        if prev_f is not None:
            up = up + 1 if f > prev_f else 0 if f < prev_f else up
            dn = dn + 1 if f < prev_f else 0 if f > prev_f else dn
        long_c = c[i] > f and up > 0 and i > 0
        short_c = c[i] < f and dn > 0 and i > 0
        new_cond = 1 if long_c else -1 if short_c else cond
        if long_c and cond == -1:
            sig[i] = 1
        elif short_c and cond == 1:
            sig[i] = -1
        cond = new_cond
        filt[i] = prev_f = f
    return sig


def qqe(c, rsi_n=14, sf=5, factor=4.238):
    m = len(c)
    rsima = ema_sparse(S.rsi(c, rsi_n), sf)
    wp = rsi_n * 2 - 1
    atr_rsi = [None] + [None if rsima[i] is None or rsima[i - 1] is None else abs(rsima[i - 1] - rsima[i]) for i in range(1, m)]
    dar = [None if v is None else v * factor for v in ema_sparse(ema_sparse(atr_rsi, wp), wp)]
    longband = shortband = None
    trend = 1
    tl = [None] * m
    for i in range(1, m):
        if dar[i] is None or rsima[i - 1] is None:
            continue
        r, r1 = rsima[i], rsima[i - 1]
        nl, ns = r - dar[i], r + dar[i]
        lb_prev, sb_prev = longband, shortband
        longband = max(lb_prev, nl) if lb_prev is not None and r1 > lb_prev and r > lb_prev else nl
        shortband = min(sb_prev, ns) if sb_prev is not None and r1 < sb_prev and r < sb_prev else ns
        if sb_prev is not None and ((r1 <= sb_prev < r) or (r1 >= sb_prev > r)) and r > sb_prev:
            trend = 1
        elif lb_prev is not None and ((r1 >= lb_prev > r) or (r1 <= lb_prev < r)) and r < lb_prev:
            trend = -1
        tl[i] = longband if trend == 1 else shortband
    sig = [0] * m
    xl = xs = 0
    for i in range(m):
        if tl[i] is None or rsima[i] is None:
            continue
        xl = xl + 1 if tl[i] < rsima[i] else 0
        xs = xs + 1 if tl[i] > rsima[i] else 0
        sig[i] = 1 if xl == 1 else -1 if xs == 1 else 0
    return sig


class CommunityAsset(scan.ScanAsset):
    def __init__(self, path):
        super().__init__(path)
        E = self.e
        h, l, c = E.h, E.l, E.c
        self.ut_stop = ut_bot(c, S.atr(h, l, c, 10))
        self.ssl = ssl_channel(h, l, c)
        self.sq_on, self.sq_off, self.sq_val = squeeze_momentum(h, l, c)
        self.wt1, self.wt2 = wavetrend(h, l, c)
        self.ce_dir = chandelier(h, l, c, S.atr(h, l, c, 22))
        self.hma = hull(c)
        self.rf_sig = range_filter(c)
        self.qqe_sig = qqe(c)

    def community_signals(self, name, d):
        c, n = self.e.c, len(self.e.c)
        out = [False] * n
        for i in range(2, n):
            if name == "UT_BOT":
                s0, s1 = self.ut_stop[i], self.ut_stop[i - 1]
                v = s0 is not None and s1 is not None and ((c[i] > s0 and c[i - 1] <= s1) if d > 0 else (c[i] < s0 and c[i - 1] >= s1))
            elif name == "SSL_CHANNEL":
                v = self.ssl[i] == d and self.ssl[i - 1] == -d
            elif name == "SQUEEZE_MOMENTUM":
                v = bool(self.sq_off[i]) and bool(self.sq_on[i - 1]) and self.sq_val[i] is not None and self.sq_val[i] * d > 0
            elif name == "WAVETREND":
                a, b, a1, b1 = self.wt1[i], self.wt2[i], self.wt1[i - 1], self.wt2[i - 1]
                if None in (a, b, a1, b1):
                    v = False
                elif d > 0:
                    v = a1 <= b1 and a > b and a < -53
                else:
                    v = a1 >= b1 and a < b and a > 53
            elif name == "CHANDELIER_EXIT":
                v = self.ce_dir[i] == d and self.ce_dir[i - 1] == -d
            elif name == "HULL_SUITE":
                h0, h1, h2, h3 = self.hma[i], self.hma[i - 1], self.hma[i - 2], self.hma[i - 3] if i >= 3 else None
                v = None not in (h0, h1, h2, h3) and ((h0 > h2) == (d > 0)) and ((h1 > h3) != (d > 0))
            elif name == "RANGE_FILTER":
                v = self.rf_sig[i] == d
            elif name == "QQE":
                v = self.qqe_sig[i] == d
            else:
                raise ValueError(name)
            out[i] = bool(v)
        return out
