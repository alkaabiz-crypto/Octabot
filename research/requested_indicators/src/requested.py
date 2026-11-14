"""The requested indicators, each on its own (PROTOCOL.md). Built on research/indicator_scan (read-only)."""
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "community_indicators", "src"))
import itertools

import community as C1
import oil
import scan
import study as S


# ------------------------------------------------------------------------------------------- shared pieces
def dmi(h, l, c, n=14):
    """Wilder DMI: (adx, plus_di, minus_di)."""
    m = len(c)
    adx, pdi, mdi = [None] * m, [None] * m, [None] * m
    tr, pdm, mdm = [], [], []
    for i in range(1, m):
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm.append(up if up > dn and up > 0 else 0.0)
        mdm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))

    def wilder(x):
        out = [None] * len(x)
        if len(x) < n:
            return out
        s = sum(x[:n]) / n
        out[n - 1] = s
        for k in range(n, len(x)):
            s = (s * (n - 1) + x[k]) / n
            out[k] = s
        return out
    st, sp, sm = wilder(tr), wilder(pdm), wilder(mdm)
    dx = []
    for j in range(n - 1, len(tr)):
        p, q = (0.0, 0.0) if st[j] == 0 else (100 * sp[j] / st[j], 100 * sm[j] / st[j])
        pdi[j + 1], mdi[j + 1] = p, q
        dx.append(0.0 if p + q == 0 else 100 * abs(p - q) / (p + q))
    for j, v in enumerate(wilder(dx)):
        if v is not None:
            adx[n + j] = v
    return adx, pdi, mdi


def session_vwap_bands(t, h, l, c, v, session_ids):
    """Volume-weighted VWAP and standard deviation per session, using candles up to and including the current one."""
    m = len(c)
    vwap, sd = [None] * m, [None] * m
    pv = pv2 = vol = 0.0
    for i in range(m):
        if i == 0 or session_ids[i] != session_ids[i - 1]:
            pv = pv2 = vol = 0.0
        tp = (h[i] + l[i] + c[i]) / 3
        pv += tp * v[i]
        pv2 += tp * tp * v[i]
        vol += v[i]
        if vol > 0:
            vwap[i] = pv / vol
            sd[i] = math.sqrt(max(pv2 / vol - vwap[i] ** 2, 0.0))
    return vwap, sd


def pivots(x, left=5, right=5, kind="low"):
    """Confirmed pivots: returns list of (pivot_index, confirm_index)."""
    out = []
    for p in range(left, len(x) - right):
        w = x[p - left:p + right + 1]
        if (kind == "low" and x[p] == min(w) and w.count(x[p]) == 1) or (kind == "high" and x[p] == max(w) and w.count(x[p]) == 1):
            out.append((p, p + right))
    return out


# ------------------------------------------------------------------------------------------- Lorentzian (jdehorty)
def running_normalize(x):
    """Pine `normalize`: rescale with the running historical min and max (no look-ahead)."""
    out, lo, hi = [None] * len(x), None, None
    for i, v in enumerate(x):
        if v is None:
            continue
        lo = v if lo is None else min(lo, v)
        hi = v if hi is None else max(hi, v)
        out[i] = (v - lo) / max(hi - lo, 10e-10)
    return out


def cci_close(c, n):
    out = [None] * len(c)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1:i + 1]
        m = sum(w) / n
        md = sum(abs(v - m) for v in w) / n
        out[i] = 0.0 if md == 0 else (c[i] - m) / (0.015 * md)
    return out


def jdehorty_adx(h, l, c, n):
    m = len(c)
    trs = dmp = dmm = 0.0
    dx = [None] * m
    for i in range(1, m):
        tr = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        p = max(up, 0) if up > dn else 0.0
        q = max(dn, 0) if dn > up else 0.0
        trs = trs - trs / n + tr
        dmp = dmp - dmp / n + p
        dmm = dmm - dmm / n + q
        if trs > 0:
            di_p, di_m = dmp / trs * 100, dmm / trs * 100
            dx[i] = 0.0 if di_p + di_m == 0 else abs(di_p - di_m) / (di_p + di_m) * 100
    out, s = [None] * m, None
    first = next(i for i, v in enumerate(dx) if v is not None)
    vals = dx[first:]
    if len(vals) >= n:
        s = sum(vals[:n]) / n
        out[first + n - 1] = s
        for k in range(n, len(vals)):
            s = (s * (n - 1) + vals[k]) / n
            out[first + k] = s
    return [None if v is None else v / 100 for v in out]


def lorentzian_features(o, h, l, c):
    hlc3 = [(h[i] + l[i] + c[i]) / 3 for i in range(len(c))]

    def n_rsi(n1, n2):
        return [None if v is None else v / 100 for v in C1.ema_sparse(S.rsi(c, n1), n2)]
    e1 = scan.ema(hlc3, 10)
    e2 = C1.ema_sparse([None if e is None else abs(x - e) for x, e in zip(hlc3, e1)], 10)
    ci = [None if a is None or b is None or b == 0 else (x - a) / (0.015 * b) for x, a, b in zip(hlc3, e1, e2)]
    wt1 = C1.ema_sparse(ci, 11)
    wt2 = C1.sma_sparse(wt1, 4)
    n_wt = running_normalize([None if a is None or b is None else a - b for a, b in zip(wt1, wt2)])
    n_cci = running_normalize(C1.ema_sparse(cci_close(c, 20), 2))
    return [n_rsi(14, 2), n_wt, n_cci, jdehorty_adx(h, l, c, 20), n_rsi(9, 2)]


def rational_quadratic(c, h=8, r=8.0, x0=25):
    w = [(1 + (i * i) / (h * h * 2 * r)) ** -r for i in range(x0 + 2)]
    out = [None] * len(c)
    for t in range(x0 + 1, len(c)):
        out[t] = sum(c[t - i] * w[i] for i in range(x0 + 2)) / sum(w)
    return out


def klmf_regime(o, h, l, c, threshold=-0.1):
    src = [(o[i] + h[i] + l[i] + c[i]) / 4 for i in range(len(c))]
    v1 = v2 = k = 0.0
    prev_k, slopes = 0.0, []
    for i in range(len(src)):
        if h[i] - l[i] != 0:
            v1 = 0.2 * (src[i] - src[i - 1 if i else 0]) + 0.8 * v1
            v2 = 0.1 * (h[i] - l[i]) + 0.8 * v2
        omega = abs(v1 / v2) if v2 else 0.0
        alpha = (-(omega ** 2) + math.sqrt(omega ** 4 + 16 * omega ** 2)) / 8
        k = alpha * src[i] + (1 - alpha) * k
        slopes.append(abs(k - prev_k))
        prev_k = k
    ema200 = scan.ema(slopes, 200)
    return [e is not None and e > 0 and (s - e) / e >= threshold for s, e in zip(slopes, ema200)]


def lorentzian_entries(o, h, l, c, neighbors=8, max_back=2000):
    """Start-long / start-short conditions of the Lorentzian Classification (defaults; see PROTOCOL.md)."""
    m = len(c)
    feats = lorentzian_features(o, h, l, c)
    start = max(next(i for i in range(m) if all(f[i] is not None for f in feats)), 4)
    F = np.array([[f[i] if f[i] is not None else 0.0 for f in feats] for i in range(m)])
    y = np.zeros(m)
    for j in range(4, m):
        y[j] = -1 if c[j - 4] < c[j] else 1 if c[j - 4] > c[j] else 0
    preds, dists = [], []
    prediction = [0] * m
    for i in range(start + max_back, m):
        lo = i - max_back
        d = np.log1p(np.abs(F[lo:i] - F[i])).sum(axis=1)
        last = -1.0
        labels = y[lo:i]
        for k in range(max_back):
            if k % 4 and d[k] >= last:
                last = d[k]
                dists.append(d[k])
                preds.append(labels[k])
                if len(preds) > neighbors:
                    last = dists[round(neighbors * 3 / 4)]
                    dists.pop(0)
                    preds.pop(0)
        prediction[i] = sum(preds)
    atr1, atr10 = S.atr(h, l, c, 1), S.atr(h, l, c, 10)
    vol_ok = [a is not None and b is not None and a > b for a, b in zip(atr1, atr10)]
    regime_ok = klmf_regime(o, h, l, c)
    yhat = rational_quadratic(c)
    signal, long_start, short_start = 0, [False] * m, [False] * m
    for i in range(1, m):
        prev = signal
        if prediction[i] > 0 and vol_ok[i] and regime_ok[i]:
            signal = 1
        elif prediction[i] < 0 and vol_ok[i] and regime_ok[i]:
            signal = -1
        if yhat[i] is None or yhat[i - 1] is None or i < start + max_back:
            continue
        if signal != prev:
            if signal == 1 and yhat[i] > yhat[i - 1]:
                long_start[i] = True
            elif signal == -1 and yhat[i] < yhat[i - 1]:
                short_start[i] = True
    return long_start, short_start


# ------------------------------------------------------------------------------------------- volume profile (oil)
def session_value_areas(q, session_of_15m, rows=50, va=0.70):
    """For each session id: (POC, VAH, VAL) from that session's 15m candles, tick volume spread over each range."""
    by = {}
    for j, s in enumerate(session_of_15m):
        by.setdefault(s, []).append(j)
    out = {}
    for s, js in by.items():
        lo, hi = min(q["bl"][j] for j in js), max(q["bh"][j] for j in js)
        if hi <= lo:
            continue
        step = (hi - lo) / rows
        vol = [0.0] * rows
        for j in js:
            a = min(rows - 1, int((q["bl"][j] - lo) / step))
            b = min(rows - 1, int((q["bh"][j] - lo) / step))
            share = q["n"][j] / (b - a + 1)
            for r in range(a, b + 1):
                vol[r] += share
        poc = max(range(rows), key=lambda r: vol[r])
        lo_r = hi_r = poc
        tot, inside = sum(vol), vol[poc]
        while inside < va * tot and (lo_r > 0 or hi_r < rows - 1):
            down = vol[lo_r - 1] if lo_r > 0 else -1
            up = vol[hi_r + 1] if hi_r < rows - 1 else -1
            if up >= down:
                hi_r += 1
                inside += vol[hi_r]
            else:
                lo_r -= 1
                inside += vol[lo_r]
        out[s] = (lo + (poc + 0.5) * step, lo + (hi_r + 1) * step, lo + lo_r * step)
    return out


# ------------------------------------------------------------------------------------------- asset
class ReqAsset(scan.ScanAsset):
    def __init__(self, path, utc_day_sessions=False):
        super().__init__(path)
        E = self.e
        _o, h, l, c, v = E.o, E.h, E.l, E.c, E.v
        sess = [t // 86400 for t in E.t] if utc_day_sessions else self.session
        self.sess = sess
        self.vw, self.vw_sd = session_vwap_bands(E.t, h, l, c, v, sess)
        self.e20, self.e50, self.e200 = scan.ema(c, 20), scan.ema(c, 50), scan.ema(c, 200)
        self.adx14, self.pdi14, self.mdi14 = dmi(h, l, c, 14)
        self.piv_low, self.piv_high = pivots(l, kind="low"), pivots(h, kind="high")
        self._lor = None
        self._va = None

    def lorentzian(self):
        if self._lor is None:
            E = self.e
            self._lor = lorentzian_entries(E.o, E.h, E.l, E.c)
        return self._lor

    def value_areas(self):
        if self._va is None:
            q = self.q
            idx = [S_bisect(self.e.t, t) for t in q["t"]]
            sess15 = [self.sess[k] if k >= 0 else -1 for k in idx]
            self._va = session_value_areas(q, sess15)
        return self._va

    def req_signals(self, name, d):
        E, n = self.e, len(self.e.c)
        c = E.c
        out = [False] * n
        if name == "LORENTZIAN":
            ls, ss = self.lorentzian()
            return ls if d > 0 else ss
        if name in ("SUPERTREND", "MACD"):
            return self.scan_signals(name, d)
        if name == "RSI14":
            return self.scan_signals("RSI14_REVERSION", d)
        if name == "RSI_DIVERGENCE":
            piv = self.piv_low if d > 0 else self.piv_high
            src = E.l if d > 0 else E.h
            prev = None
            for p, conf in piv:
                if self.rsi[p] is None:
                    continue
                if prev is not None and conf < n:
                    pp = prev
                    if (src[p] - src[pp]) * d < 0 and (self.rsi[p] - self.rsi[pp]) * d > 0:
                        out[conf] = True
                prev = p
            return out
        if name == "VP_80_RULE" or name == "VP_BREAKOUT":
            va = self.value_areas()
            sids = sorted(set(self.sess))
            prior = {s: va.get(p) for p, s in itertools.pairwise(sids)}
            first_open = {}
            for i in range(n):
                first_open.setdefault(self.sess[i], E.o[i])
            for i in range(1, n):
                s = self.sess[i]
                if s != self.sess[i - 1] or prior.get(s) is None:
                    continue
                _poc, vah, val = prior[s]
                if name == "VP_80_RULE":
                    if d > 0:
                        out[i] = first_open[s] < val and c[i - 1] <= val < c[i]
                    else:
                        out[i] = first_open[s] > vah and c[i - 1] >= vah > c[i]
                else:
                    out[i] = (c[i - 1] <= vah < c[i]) if d > 0 else (c[i - 1] >= val > c[i])
            return out
        for i in range(1, n):
            same = self.sess[i] == self.sess[i - 1]
            if name in ("VWAP_BAND_REVERSION", "VWAP_BAND_BREAKOUT", "SESSION_VWAP_CROSS"):
                w0, w1, s0, s1 = self.vw[i], self.vw[i - 1], self.vw_sd[i], self.vw_sd[i - 1]
                if not same or None in (w0, w1, s0, s1):
                    continue
                if name == "VWAP_BAND_REVERSION":
                    b0, b1 = (w0 - 2 * s0, w1 - 2 * s1) if d > 0 else (w0 + 2 * s0, w1 + 2 * s1)
                    v = (c[i - 1] <= b1 and c[i] > b0) if d > 0 else (c[i - 1] >= b1 and c[i] < b0)
                elif name == "VWAP_BAND_BREAKOUT":
                    b0, b1 = (w0 + s0, w1 + s1) if d > 0 else (w0 - s0, w1 - s1)
                    v = (c[i - 1] <= b1 and c[i] > b0) if d > 0 else (c[i - 1] >= b1 and c[i] < b0)
                else:
                    v = (c[i - 1] <= w1 and c[i] > w0) if d > 0 else (c[i - 1] >= w1 and c[i] < w0)
            elif name == "EMA_20_50_200_PULLBACK":
                e20, e20p, e50, e200 = self.e20[i], self.e20[i - 1], self.e50[i], self.e200[i]
                if None in (e20, e20p, e50, e200):
                    continue
                trend = (e50 > e200 and c[i] > e200) if d > 0 else (e50 < e200 and c[i] < e200)
                v = trend and ((c[i - 1] < e20p and c[i] > e20) if d > 0 else (c[i - 1] > e20p and c[i] < e20))
            elif name in ("ADX14_20", "ADX14_25"):
                th = 20 if name.endswith("20") else 25
                a0, a1, p, m_ = self.adx14[i], self.adx14[i - 1], self.pdi14[i], self.mdi14[i]
                if None in (a0, a1, p, m_):
                    continue
                v = a1 < th <= a0 and ((p > m_) if d > 0 else (m_ > p))
            else:
                raise ValueError(name)
            out[i] = bool(v)
        return out

    def simulate(self, i, d, exit_rule, delay=0):
        if exit_rule != "NATIVE":
            return super().simulate(i, d, exit_rule, delay)
        q, E = self.q, self.e
        t_close = E.t[i] + 3600
        j, k = self.p_idx.get(t_close), self.p_idx.get(t_close + 4 * 3600)
        a = self.atr[i]
        if j is None or k is None or a is None or a <= 0:
            return None
        entry = q["ao"][j] if d > 0 else q["bo"][j]
        exit_ = q["bo"][k] if d > 0 else q["ao"][k]
        risk = 2.0 * a
        return oil.Trade(i, t_close, q["t"][k], d, entry, risk, (exit_ - entry) * d / risk, "time", self.regime(t_close))


def S_bisect(ts, t):
    import bisect
    return bisect.bisect_right(ts, t) - 1
