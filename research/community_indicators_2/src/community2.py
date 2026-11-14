"""Round-2 community indicators, re-implemented from their published open-source logic at default settings.

Every value at 1H candle i uses candles 0..i only; swing points are confirmed only after their right-hand candles
close. Built on the indicator-scan engine (research/indicator_scan, read-only) for data, exits and costs.
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "community_indicators", "src"))
import community as C1
import scan
import study as S

SIGNALS = (("HALFTREND", (1, -1)), ("CORAL_TREND", (1, -1)), ("WADDAH_ATTAR", (1, -1)), ("VIX_FIX", (1,)),
           ("ICHIMOKU_TK", (1, -1)), ("PARABOLIC_SAR", (1, -1)), ("SCHAFF_TREND_CYCLE", (1, -1)),
           ("HEIKIN_ASHI_FLIP", (1, -1)), ("SMC_STRUCTURE_BREAK", (1, -1)))


def highest(x, n, i):
    return max(x[i - n + 1:i + 1])


def lowest(x, n, i):
    return min(x[i - n + 1:i + 1])


def halftrend(h, l, c, amplitude=2):
    """everget HalfTrend. Returns trend per bar: +1 up, -1 down (None during warm-up)."""
    m = len(c)
    out = [None] * m
    hma, lma = scan.sma(h, amplitude), scan.sma(l, amplitude)
    trend, next_trend = 0, 0               # 0 = up (as in the original), 1 = down
    max_low, min_high = l[0], h[0]
    for i in range(1, m):
        if hma[i] is None:
            continue
        high_price, low_price = highest(h, amplitude, i), lowest(l, amplitude, i)
        if next_trend == 1:
            max_low = max(low_price, max_low)
            if hma[i] < max_low and c[i] < l[i - 1]:
                trend, next_trend, min_high = 1, 0, high_price
        else:
            min_high = min(high_price, min_high)
            if lma[i] > min_high and c[i] > h[i - 1]:
                trend, next_trend, max_low = 0, 1, low_price
        out[i] = 1 if trend == 0 else -1
    return out


def coral(c, sm=21, cd=0.4):
    di = (sm - 1) / 2 + 1
    c1 = 2 / (di + 1)
    c2 = 1 - c1
    c3 = 3 * (cd * cd + cd ** 3)
    c4 = -3 * (2 * cd * cd + cd + cd ** 3)
    c5 = 3 * cd + 1 + cd ** 3 + 3 * cd * cd
    i1 = i2 = i3 = i4 = i5 = i6 = 0.0
    out = []
    for x in c:
        i1 = c1 * x + c2 * i1
        i2 = c1 * i1 + c2 * i2
        i3 = c1 * i2 + c2 * i3
        i4 = c1 * i3 + c2 * i4
        i5 = c1 * i4 + c2 * i5
        i6 = c1 * i5 + c2 * i6
        out.append(-cd ** 3 * i6 + c3 * i5 + c4 * i4 + c5 * i3)
    return out


def waddah(h, l, c, sens=150, fast=20, slow=40, bb=20, mult=2.0):
    m = len(c)
    ef, es = scan.ema(c, fast), scan.ema(c, slow)
    macd = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    dead = [None if v is None else v * 3.7 for v in S.atr(h, l, c, 100)]   # RMA of true range = Wilder ATR
    up, dn, e1 = [None] * m, [None] * m, [None] * m
    for i in range(bb - 1, m):
        w = c[i - bb + 1:i + 1]
        mu = sum(w) / bb
        sd = math.sqrt(sum((v - mu) ** 2 for v in w) / bb)
        e1[i] = 2 * mult * sd
        if macd[i] is not None and macd[i - 1] is not None:
            t1 = (macd[i] - macd[i - 1]) * sens
            up[i], dn[i] = (t1, 0.0) if t1 >= 0 else (0.0, -t1)
    return up, dn, e1, dead


def vix_fix(l, c, pd=22, bbl=20, mult=2.0, lb=50, ph=0.85):
    m = len(c)
    wvf = [None] * m
    for i in range(pd - 1, m):
        hc = highest(c, pd, i)
        wvf[i] = (hc - l[i]) / hc * 100
    mid = C1.sma_sparse(wvf, bbl)
    out = [False] * m
    for i in range(m):
        if mid[i] is None or i < lb + pd:
            continue
        w = wvf[i - bbl + 1:i + 1]
        sd = math.sqrt(sum((v - mid[i]) ** 2 for v in w) / bbl)
        rng_high = max(wvf[i - lb + 1:i + 1]) * ph
        out[i] = wvf[i] >= mid[i] + mult * sd or wvf[i] >= rng_high
    return out


def ichimoku(h, l, c, t=9, k=26, b=52, shift=26):
    m = len(c)
    tenkan, kijun, top, bot = [None] * m, [None] * m, [None] * m, [None] * m
    for i in range(m):
        if i >= t - 1:
            tenkan[i] = (highest(h, t, i) + lowest(l, t, i)) / 2
        if i >= k - 1:
            kijun[i] = (highest(h, k, i) + lowest(l, k, i)) / 2
        j = i - shift                       # the cloud shown at bar i was computed 26 bars earlier
        if j >= b - 1 and tenkan[j] is not None and kijun[j] is not None:
            sa = (tenkan[j] + kijun[j]) / 2
            sb = (highest(h, b, j) + lowest(l, b, j)) / 2
            top[i], bot[i] = max(sa, sb), min(sa, sb)
    return tenkan, kijun, top, bot


def psar(h, l, start=0.02, inc=0.02, mx=0.2):
    """Wilder's Parabolic SAR. Returns +1 when SAR is below price (uptrend), -1 when above."""
    m = len(h)
    out = [None] * m
    if m < 2:
        return out
    up = h[1] >= h[0]
    sar = l[0] if up else h[0]
    ep = h[1] if up else l[1]
    af = start
    for i in range(1, m):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, l[i - 1], l[i - 2] if i >= 2 else l[i - 1])
            if l[i] < sar:
                up, sar, ep, af = False, ep, l[i], start
            elif h[i] > ep:
                ep, af = h[i], min(af + inc, mx)
        else:
            sar = max(sar, h[i - 1], h[i - 2] if i >= 2 else h[i - 1])
            if h[i] > sar:
                up, sar, ep, af = True, ep, h[i], start
            elif l[i] < ep:
                ep, af = l[i], min(af + inc, mx)
        out[i] = 1 if up else -1
    return out


def schaff(c, length=10, fast=23, slow=50, factor=0.5):
    m = len(c)
    ef, es = scan.ema(c, fast), scan.ema(c, slow)
    macd = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    f1 = pf = f2 = pff = None
    pf_hist, out = [None] * m, [None] * m
    for i in range(m):
        w = macd[i - length + 1:i + 1] if i >= length - 1 else []
        if len(w) < length or None in w:
            continue
        v1 = min(w)
        v2 = max(w) - v1
        f1 = (macd[i] - v1) / v2 * 100 if v2 > 0 else (f1 or 0.0)
        pf = f1 if pf is None else pf + factor * (f1 - pf)
        pf_hist[i] = pf
        w2 = pf_hist[i - length + 1:i + 1]
        if None in w2:
            continue
        v3 = min(w2)
        v4 = max(w2) - v3
        f2 = (pf - v3) / v4 * 100 if v4 > 0 else (f2 or 0.0)
        pff = f2 if pff is None else pff + factor * (f2 - pff)
        out[i] = pff
    return out


def heikin_ashi(o, h, l, c):
    m = len(c)
    bull = [None] * m
    ha_o = (o[0] + c[0]) / 2
    ha_c = (o[0] + h[0] + l[0] + c[0]) / 4
    bull[0] = ha_c > ha_o
    for i in range(1, m):
        ha_o = (ha_o + ha_c) / 2
        ha_c = (o[i] + h[i] + l[i] + c[i]) / 4
        bull[i] = ha_c > ha_o
    return bull


def smc_breaks(h, l, c, length=5):
    """LuxAlgo-style internal structure: swing found at bar i-length, confirmed at bar i. Returns +1/-1 breaks."""
    m = len(c)
    sig = [0] * m
    os_, top_y, btm_y, top_live, btm_live = 0, None, None, False, False
    for i in range(length, m):
        upper, lower = highest(h, length, i), lowest(l, length, i)
        prev = os_
        os_ = 0 if h[i - length] > upper else 1 if l[i - length] < lower else os_
        if os_ == 0 and prev != 0:
            top_y, top_live = h[i - length], True
        if os_ == 1 and prev != 1:
            btm_y, btm_live = l[i - length], True
        if top_live and top_y is not None and c[i] > top_y and c[i - 1] <= top_y:
            sig[i], top_live = 1, False
        elif btm_live and btm_y is not None and c[i] < btm_y and c[i - 1] >= btm_y:
            sig[i], btm_live = -1, False
    return sig


class Community2Asset(scan.ScanAsset):
    def __init__(self, path):
        super().__init__(path)
        E = self.e
        o, h, l, c = E.o, E.h, E.l, E.c
        self.ht = halftrend(h, l, c)
        self.coral = coral(c)
        self.wae_up, self.wae_dn, self.wae_e1, self.wae_dead = waddah(h, l, c)
        self.vix = vix_fix(l, c)
        self.tk, self.kj, self.cloud_top, self.cloud_bot = ichimoku(h, l, c)
        self.sar = psar(h, l)
        self.stc = schaff(c)
        self.ha = heikin_ashi(o, h, l, c)
        self.smc = smc_breaks(h, l, c)

    def c2_signals(self, name, d):
        c, n = self.e.c, len(self.e.c)
        out = [False] * n
        for i in range(3, n):
            if name == "HALFTREND":
                v = self.ht[i] == d and self.ht[i - 1] == -d
            elif name == "CORAL_TREND":
                v = i > 300 and ((self.coral[i] > self.coral[i - 1]) == (d > 0)) and ((self.coral[i - 1] > self.coral[i - 2]) != (d > 0))
            elif name == "WADDAH_ATTAR":
                col = self.wae_up if d > 0 else self.wae_dn
                def fire(k, col=col):
                    return None not in (col[k], self.wae_e1[k], self.wae_dead[k]) and col[k] > self.wae_e1[k] and col[k] > self.wae_dead[k]
                v = fire(i) and not fire(i - 1)
            elif name == "VIX_FIX":
                v = self.vix[i] and not self.vix[i - 1]
            elif name == "ICHIMOKU_TK":
                tk, kj, top, bot = self.tk, self.kj, self.cloud_top, self.cloud_bot
                if None in (tk[i], kj[i], tk[i - 1], kj[i - 1], top[i]):
                    v = False
                elif d > 0:
                    v = tk[i - 1] <= kj[i - 1] and tk[i] > kj[i] and c[i] > top[i]
                else:
                    v = tk[i - 1] >= kj[i - 1] and tk[i] < kj[i] and c[i] < bot[i]
            elif name == "PARABOLIC_SAR":
                v = self.sar[i] == d and self.sar[i - 1] == -d
            elif name == "SCHAFF_TREND_CYCLE":
                s0, s1 = self.stc[i], self.stc[i - 1]
                v = s0 is not None and s1 is not None and ((s1 < 25 <= s0) if d > 0 else (s1 > 75 >= s0))
            elif name == "HEIKIN_ASHI_FLIP":
                v = self.ha[i] == (d > 0) and self.ha[i - 1] == (d < 0)
            elif name == "SMC_STRUCTURE_BREAK":
                v = self.smc[i] == d
            else:
                raise ValueError(name)
            out[i] = bool(v)
        return out
