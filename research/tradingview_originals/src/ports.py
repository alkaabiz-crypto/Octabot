"""Faithful ports of the original TradingView scripts (PROTOCOL.md). Each function cites the original's logic.

Built on research/indicator_scan (bid/ask data, exits, costs) and reuses the earlier rebuilds that the audit found
identical to the originals (UT Bot, SSL, Chandelier, HalfTrend, Coral; see PROTOCOL.md).
"""
import math
import os
import random
import statistics
import sys

import numpy as np
from numba import njit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "community_indicators", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "community_indicators_2", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "requested_indicators", "src"))
import community as C1
import community2 as C2
import oil
import requested as RQ
import scan
import study as S

WEEK = 7 * 86400
CFD_WEEK_ANCHOR = 3 * 86400 + 21 * 3600    # Sunday 21:00 UTC (FX/CFD weekly session start)
CRYPTO_WEEK_ANCHOR = 4 * 86400             # Monday 00:00 UTC


# ------------------------------------------------------------------------------------------- Lorentzian v6
@njit(cache=True)
def _lorentzian_realtime(F, y, k):
    n = F.shape[0]
    pred_arr = np.zeros(k + 2)
    dist_arr = np.zeros(k + 2)
    cnt = 0
    prediction = np.zeros(n)
    for t in range(n):
        start = t - 2000 if t >= 2000 else 0          # maxBarsBackIndex with last_bar_index = t (real time)
        stop = min(t, 1999)                # sizeLoop = min(maxBarsBack - 1, size - 1)
        step = 1 if stop >= start else -1
        last = -1.0
        i = start
        while True:
            if i % 4 != 0:
                d = 0.0
                ok = True
                for j in range(F.shape[1]):
                    a, b = F[t, j], F[i, j]
                    if np.isnan(a) or np.isnan(b):
                        ok = False
                        break
                    d += math.log(1.0 + abs(a - b))
                if ok and d >= last:
                    last = d
                    dist_arr[cnt] = d
                    pred_arr[cnt] = y[i]
                    cnt += 1
                    if cnt > k:
                        last = dist_arr[round(k * 3 / 4)]
                        for m in range(cnt - 1):
                            dist_arr[m] = dist_arr[m + 1]
                            pred_arr[m] = pred_arr[m + 1]
                        cnt -= 1
            if i == stop:
                break
            i += step
        s = 0.0
        for m in range(cnt):
            s += pred_arr[m]
        prediction[t] = s
    return prediction


def lorentzian_v6(o, h, l, c, neighbors=8):
    """Start-long / start-short of jdehorty's Lorentzian Classification v6 at its defaults, replayed in real time."""
    m = len(c)
    hlc3 = [(h[i] + l[i] + c[i]) / 3 for i in range(m)]
    f_rsi14 = [None if v is None else v / 100 for v in S.rsi(c, 14)]            # n_rsi(close, 14, 1): ema(,1) = itself
    e1 = scan.ema(hlc3, 10)
    e2 = C1.ema_sparse([None if e is None else abs(x - e) for x, e in zip(hlc3, e1)], 10)
    ci = [None if a is None or b is None or b == 0 else (x - a) / (0.015 * b) for x, a, b in zip(hlc3, e1, e2)]
    wt1 = C1.ema_sparse(ci, 11)
    wt2 = C1.sma_sparse(wt1, 4)
    f_wt = RQ.running_normalize([None if a is None or b is None else a - b for a, b in zip(wt1, wt2)])
    f_cci = RQ.running_normalize(RQ.cci_close(c, 20))                           # n_cci(close, 20, 1)
    f_adx = RQ.jdehorty_adx(h, l, c, 20)
    f_rsi9 = [None if v is None else v / 100 for v in S.rsi(c, 9)]
    F = np.array([[np.nan if f[i] is None else f[i] for f in (f_rsi14, f_wt, f_cci, f_adx, f_rsi9)] for i in range(m)])
    y = np.zeros(m)
    for i in range(4, m):
        y[i] = -1 if c[i - 4] < c[i] else 1 if c[i - 4] > c[i] else 0           # y_train_series, as in the original
    pred = _lorentzian_realtime(F, y, neighbors)
    tr1, atr10 = S.atr(h, l, c, 1), S.atr(h, l, c, 10)
    vol_ok = [a is not None and b is not None and a > b for a, b in zip(tr1, atr10)]
    # regime filter (MLExtensions.regime_filter on ohlc4, threshold -0.1)
    src = [(o[i] + h[i] + l[i] + c[i]) / 4 for i in range(m)]
    v1 = v2 = k = 0.0
    slopes, prev_k = [], 0.0
    for i in range(m):
        v1 = 0.2 * (src[i] - (src[i - 1] if i else src[i])) + 0.8 * v1
        v2 = 0.1 * (h[i] - l[i]) + 0.8 * v2
        omega = abs(v1 / v2) if v2 else 0.0
        alpha = (-(omega ** 2) + math.sqrt(omega ** 4 + 16 * omega ** 2)) / 8
        k = alpha * src[i] + (1 - alpha) * k
        slopes.append(abs(k - prev_k))
        prev_k = k
    ema200 = scan.ema(slopes, 200)
    regime_ok = [e is not None and e > 0 and (s - e) / e >= -0.1 for s, e in zip(slopes, ema200)]
    yhat = RQ.rational_quadratic(c, 8, 8.0, 25)
    signal, longs, shorts = 0, [False] * m, [False] * m
    for i in range(1, m):
        prev = signal
        if pred[i] > 0 and vol_ok[i] and regime_ok[i]:
            signal = 1
        elif pred[i] < 0 and vol_ok[i] and regime_ok[i]:
            signal = -1
        if signal != prev and yhat[i] is not None and yhat[i - 1] is not None:
            longs[i] = signal == 1 and yhat[i - 1] < yhat[i]
            shorts[i] = signal == -1 and yhat[i - 1] > yhat[i]
    return longs, shorts


# ------------------------------------------------------------------------------------------- BigBeluga Session VWAP
def bigbeluga_signals(t, h, l, c, v, week_anchor, mult=2.0, gap=10):
    """Lower/upper reversal signals of Session VWAP Profile & Candle Delta [BigBeluga] on a 1H chart (weekly session)."""
    m = len(c)
    buy, sell = [False] * m, [False] * m
    sv = spv = sp2v = 0.0
    last_sig = -9999
    for i in range(m):
        new_week = i > 0 and (t[i] - week_anchor) // WEEK != (t[i - 1] - week_anchor) // WEEK
        if new_week:
            sv, spv, sp2v = v[i], c[i] * v[i], c[i] * c[i] * v[i]
        else:
            sv += v[i]
            spv += c[i] * v[i]
            sp2v += c[i] * c[i] * v[i]
        if sv <= 0:
            continue
        vw = spv / sv
        sd = math.sqrt(max(0.0, sp2v / sv - vw * vw))
        up, lo = vw + sd * mult, vw - sd * mult
        if i - last_sig >= gap:
            if h[i] > up and c[i] < up:
                sell[i], last_sig = True, i
            elif l[i] < lo and c[i] > lo:
                buy[i], last_sig = True, i
    return buy, sell


# ------------------------------------------------------------------------------------------- Supertrend (Kivanc)
def supertrend_kivanc(h, l, c, periods=10, mult=3.0):
    a = S.atr(h, l, c, periods)
    m = len(c)
    trend = [None] * m
    up_prev = dn_prev = None
    tr = 1
    for i in range(m):
        if a[i] is None:
            continue
        hl2 = (h[i] + l[i]) / 2
        up, dn = hl2 - mult * a[i], hl2 + mult * a[i]
        up1 = up if up_prev is None else up_prev
        dn1 = dn if dn_prev is None else dn_prev
        if i and c[i - 1] > up1:
            up = max(up, up1)
        if i and c[i - 1] < dn1:
            dn = min(dn, dn1)
        tr = 1 if (tr == -1 and c[i] > dn1) else -1 if (tr == 1 and c[i] < up1) else tr
        trend[i] = tr
        up_prev, dn_prev = up, dn
    return trend


# ------------------------------------------------------------------------------------------- Range Filter (guikroth)
def range_filter_guikroth(c, per=100, mult=3.0):
    m = len(c)
    absd = [0.0] + [abs(c[i] - c[i - 1]) for i in range(1, m)]
    smrng = C1.ema_sparse(scan.ema(absd, per), per * 2 - 1)
    sig = [0] * m
    prev_f, up, dn, cond = 0.0, 0, 0, 0
    for i in range(m):
        if smrng[i] is None:
            continue
        r = smrng[i] * mult
        x = c[i]
        if x > prev_f:
            f = max(x - r, prev_f)
        else:
            f = min(x + r, prev_f)
        up = up + 1 if f > prev_f else 0 if f < prev_f else up
        dn = dn + 1 if f < prev_f else 0 if f > prev_f else dn
        moved = i > 0 and x != c[i - 1]
        long_c = x > f and moved and up > 0
        short_c = x < f and moved and dn > 0
        if long_c and cond == -1:
            sig[i] = 1
        elif short_c and cond == 1:
            sig[i] = -1
        cond = 1 if long_c else -1 if short_c else cond
        prev_f = f
    return sig


# ------------------------------------------------------------------------------------------- QQE MOD (Mihkel00)
def _qqe_line(c, rsi_len=6, sf=5, factor=3.0):
    m = len(c)
    sm = C1.ema_sparse(S.rsi(c, rsi_len), sf)
    atr_rsi = [None] + [None if sm[i] is None or sm[i - 1] is None else abs(sm[i - 1] - sm[i]) for i in range(1, m)]
    dar = [None if v is None else v * factor for v in C1.ema_sparse(atr_rsi, rsi_len * 2 - 1)]
    lb = [0.0] * m
    sb = [0.0] * m
    line = [None] * m
    trend = 0
    for i in range(1, m):
        if dar[i] is None or sm[i - 1] is None:
            lb[i], sb[i] = lb[i - 1], sb[i - 1]
            continue
        r, r1 = sm[i], sm[i - 1]
        nl, ns = r - dar[i], r + dar[i]
        lb[i] = max(lb[i - 1], nl) if (r1 > lb[i - 1] and r > lb[i - 1]) else nl
        sb[i] = min(sb[i - 1], ns) if (r1 < sb[i - 1] and r < sb[i - 1]) else ns
        if i >= 2:
            cross_short = (r1 - sb[i - 2]) * (r - sb[i - 1]) < 0     # ta.cross(smoothedRsi, shortBand[1])
            cross_long = (lb[i - 2] - r1) * (lb[i - 1] - r) < 0       # ta.cross(longBand[1], smoothedRsi)
            if cross_short:
                trend = 1
            elif cross_long:
                trend = -1
        line[i] = lb[i] if trend == 1 else sb[i]
    return line, sm


def qqe_mod(c, threshold=3.0, bb_len=50, bb_mult=0.35):
    line, rsi_p = _qqe_line(c, 6, 5, 3.0)
    m = len(c)
    up_sig, dn_sig = [False] * m, [False] * m
    x = [None if v is None else v - 50 for v in line]
    for i in range(bb_len - 1, m):
        w = x[i - bb_len + 1:i + 1]
        if None in w or rsi_p[i] is None:
            continue
        mu = sum(w) / bb_len
        sd = math.sqrt(sum((v - mu) ** 2 for v in w) / bb_len)
        upper, lower = mu + bb_mult * sd, mu - bb_mult * sd
        r = rsi_p[i] - 50                       # the secondary RSI is identical (same length and smoothing)
        up_sig[i] = r > threshold and r > upper
        dn_sig[i] = r < -threshold and r < lower
    return up_sig, dn_sig


# ------------------------------------------------------------------------------------------- asset with all scripts
def first_bars(flags):
    return [bool(flags[i]) and (i == 0 or not flags[i - 1]) for i in range(len(flags))]


class OriginalAsset(scan.ScanAsset):
    def __init__(self, path, crypto=False):
        super().__init__(path)
        E = self.e
        o, h, l, c, v = E.o, E.h, E.l, E.c, E.v
        sig = {}
        ls, ss = lorentzian_v6(o, h, l, c)
        sig["LORENTZIAN_V6"] = (ls, ss)
        sig["BIGBELUGA_SESSION_VWAP"] = bigbeluga_signals(E.t, h, l, c, v, CRYPTO_WEEK_ANCHOR if crypto else CFD_WEEK_ANCHOR)
        ut = C1.ut_bot(c, S.atr(h, l, c, 10))
        sig["UT_BOT"] = ([i > 0 and ut[i] is not None and ut[i - 1] is not None and c[i] > ut[i] and c[i - 1] <= ut[i - 1] for i in range(len(c))],
                         [i > 0 and ut[i] is not None and ut[i - 1] is not None and c[i] < ut[i] and c[i - 1] >= ut[i - 1] for i in range(len(c))])

        def flips(state):
            return ([i > 0 and state[i] == 1 and state[i - 1] == -1 for i in range(len(state))],
                    [i > 0 and state[i] == -1 and state[i - 1] == 1 for i in range(len(state))])
        sig["SSL_CHANNEL"] = flips(C1.ssl_channel(h, l, c))
        sig["CHANDELIER_EXIT"] = flips(C1.chandelier(h, l, c, S.atr(h, l, c, 22)))
        sig["HALFTREND"] = flips(C2.halftrend(h, l, c))
        sig["SUPERTREND_KIVANC"] = flips(supertrend_kivanc(h, l, c))
        rf = range_filter_guikroth(c)
        sig["RANGE_FILTER"] = ([x == 1 for x in rf], [x == -1 for x in rf])
        cr = C2.coral(c)
        cstate = [None] * 300 + [1 if cr[i] > cr[i - 1] else -1 if cr[i] < cr[i - 1] else None for i in range(300, len(c))]
        for i in range(301, len(c)):
            if cstate[i] is None:
                cstate[i] = cstate[i - 1]
        sig["CORAL_TREND"] = flips(cstate)
        qu, qd = qqe_mod(c)
        sig["QQE_MOD"] = (first_bars(qu), first_bars(qd))
        up_c, dn_c, e1, _ = C2.waddah(h, l, c)
        wb = [up_c[i] is not None and e1[i] is not None and up_c[i] > e1[i] and up_c[i] > 20 for i in range(len(c))]
        ws = [dn_c[i] is not None and e1[i] is not None and dn_c[i] > e1[i] and dn_c[i] > 20 for i in range(len(c))]
        sig["WADDAH_ATTAR_ORIGINAL"] = (first_bars(wb), first_bars(ws))
        self.sig = sig

    def simulate(self, i, d, exit_rule, delay=0):
        if exit_rule != "NATIVE":
            return super().simulate(i, d, exit_rule, delay)
        return self.hold(i, d, 4 * 3600)

    def hold(self, i, d, seconds):
        """Enter after candle i closes, exit `seconds` later at the 15m open; R = 2 x ATR14 for comparability."""
        q, E = self.q, self.e
        t_close = E.t[i] + 3600
        j, k = self.p_idx.get(t_close), self.p_idx.get(t_close + seconds)
        a = self.atr[i]
        if j is None or k is None or a is None or a <= 0:
            return None
        entry = q["ao"][j] if d > 0 else q["bo"][j]
        exit_ = q["bo"][k] if d > 0 else q["ao"][k]
        return oil.Trade(i, t_close, q["t"][k], d, entry, 2.0 * a, (exit_ - entry) * d / (2.0 * a), "time", self.regime(t_close))

    def flip_trades(self, name, d, w0, w1):
        """Stop-and-reverse legs in direction d: from a d-signal to the next opposite signal."""
        buy, sell = self.sig[name]
        mine, other = (buy, sell) if d > 0 else (sell, buy)
        E, n = self.e, len(self.e.t)
        out, i = [], 0
        while i < n:
            if not mine[i] or not (w0 <= E.t[i] + 3600 < w1):
                i += 1
                continue
            j = next((k for k in range(i + 1, n) if other[k]), None)
            if j is None:
                break
            tr = self.hold(i, d, E.t[j] - E.t[i])
            if tr is not None:
                out.append(tr)
            i = j
        return out

    def duration_benchmark(self, trades, w0, w1, cost="primary", runs=1000, seed=20261110):
        """Random entries in the same calendar quarter, same direction, same holding time as each strategy trade."""
        E = self.e
        by_q = {}
        for i, t in enumerate(E.t):
            tc = t + 3600
            if w0 <= tc < w1:
                by_q.setdefault(S.quarter(tc), []).append(i)
        rnd = random.Random(seed)
        means = []
        for _ in range(runs):
            vals = []
            for tr in trades:
                pool = by_q.get(S.quarter(tr.entry_time))
                for _attempt in range(20):
                    rt = self.hold(rnd.choice(pool), tr.direction, tr.exit_time - tr.entry_time)
                    if rt is not None:
                        vals.append(rt.r(cost))
                        break
            if vals:
                means.append(statistics.mean(vals))
        s_mean = statistics.mean(t.r(cost) for t in trades)
        return {"random_mean_r": statistics.mean(means), "p_random": (sum(x >= s_mean for x in means) + 1) / (len(means) + 1)}
