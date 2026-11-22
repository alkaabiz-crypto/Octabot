"""Breakout research engine. Implements protocol.py exactly. Causal: every value at bar i uses bars <= i only."""
import json, math, statistics
from protocol import STEP, HIGHER, RISK

def ema(x, n):
    a, out = 2 / (n + 1), []
    for i, v in enumerate(x): out.append(v if i == 0 else a * v + (1 - a) * out[-1])
    return out

def rma(x, n):
    out, prev = [], None
    for i, v in enumerate(x):
        if i < n - 1: out.append(None); continue
        prev = sum(x[:n]) / n if prev is None else (prev * (n - 1) + v) / n
        out.append(prev)
    return out

def rolling(x, n, fn, include_current=True):
    """fn over window ending at i (inclusive) or i-1 (exclusive of current)."""
    out = [None] * len(x)
    for i in range(len(x)):
        lo, hi = (i - n + 1, i + 1) if include_current else (i - n, i)
        if lo >= 0: out[i] = fn(x[lo:hi])
    return out

def pstdev(w): m = sum(w) / len(w); return math.sqrt(sum((v - m) ** 2 for v in w) / len(w))

def build(cs):
    t, o, h, l, c, v = ([x[k] for x in cs] for k in range(6))
    n = len(c)
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    atr14, atr100 = rma(tr, 14), rma(tr, 100)
    sma20 = rolling(c, 20, lambda w: sum(w) / 20); sd20 = rolling(c, 20, pstdev)
    up = [None if m is None else m + 2 * s for m, s in zip(sma20, sd20)]; lo = [None if m is None else m - 2 * s for m, s in zip(sma20, sd20)]
    bw = [None if m is None or m == 0 else 4 * s / m for m, s in zip(sma20, sd20)]
    bw_pct = [None] * n
    for i in range(n):
        if i >= 119 and all(b is not None for b in (bw[i - 119], bw[i])):
            w = bw[i - 119:i + 1]; bw_pct[i] = sum(1 for b in w if b <= bw[i]) / 120
    hh = {k: rolling(h, k, max, include_current=False) for k in (10, 20, 55)}
    ll = {k: rolling(l, k, min, include_current=False) for k in (10, 20, 55)}
    vavg = rolling(v, 20, lambda w: sum(w) / 20, include_current=False)
    return dict(t=t, o=o, h=h, l=l, c=c, v=v, tr=tr, atr=atr14, atr100=atr100, up=up, lo=lo, bw_pct=bw_pct, hh=hh, ll=ll, vavg=vavg,
                e200=ema(c, 200))

def last_closed(times, step, t_close):
    lo, hi, ans = 0, len(times) - 1, -1
    while lo <= hi:
        m = (lo + hi) // 2
        if times[m] + step <= t_close: ans, lo = m, m + 1
        else: hi = m - 1
    return ans

class Lab:
    def __init__(self, data_dir):
        self.raw = {tf: json.load(open(f"{data_dir}/btc_{tf}.json")) for tf in STEP}
        self.B = {tf: build(cs) for tf, cs in self.raw.items()}
        self.p_idx = {tt: i for i, tt in enumerate(self.B["15m"]["t"])}
        self.audit = {"htf_closed": [0, 0], "daily_closed": [0, 0], "entry_after_signal": [0, 0]}
        self.sig_cache = {}

    def _chk(self, key, ok): self.audit[key][0] += bool(ok); self.audit[key][1] += 1

    def signals(self, tf, model, d, dc_len=None):
        key = (tf, model, d, dc_len)
        if key in self.sig_cache: return self.sig_cache[key]
        b = self.B[tf]; c, n = b["c"], len(b["c"]); out = [False] * n
        for i in range(260, n):
            if b["atr"][i - 1] is None or b["atr100"][i - 1] is None: continue
            vol_ok = b["vavg"][i] is not None and b["v"][i] > 1.5 * b["vavg"][i]
            if model in ("M1_BB_SQUEEZE", "M6_SQUEEZE_VOL"):
                sq = any(p is not None and p <= 0.2 for p in b["bw_pct"][i - 5:i])
                band, pband = (b["up"], b["up"]) if d > 0 else (b["lo"], b["lo"])
                cross = (c[i] - band[i]) * d > 0 and (c[i - 1] - pband[i - 1]) * d <= 0
                out[i] = sq and cross and (model == "M1_BB_SQUEEZE" or vol_ok)
            elif model in ("M2_DONCHIAN20", "M4_DONCHIAN_VOL", "M5_TREND_DC55"):
                k = 55 if model == "M5_TREND_DC55" else (dc_len or 20)
                if k not in b["hh"]:
                    b["hh"][k] = rolling(b["h"], k, max, include_current=False); b["ll"][k] = rolling(b["l"], k, min, include_current=False)
                lvl = b["hh"][k] if d > 0 else b["ll"][k]
                if lvl[i] is None or lvl[i - 1] is None: continue
                cross = (c[i] - lvl[i]) * d > 0 and (c[i - 1] - lvl[i - 1]) * d <= 0
                out[i] = cross and (model != "M4_DONCHIAN_VOL" or vol_ok)
            elif model == "M3_ATR_CONTRACT":
                contr = any(b["atr"][j] is not None and b["atr100"][j] and b["atr"][j] / b["atr100"][j] < 0.75 for j in range(i - 5, i))
                lvl = b["hh"][10] if d > 0 else b["ll"][10]
                out[i] = contr and b["tr"][i] > 1.5 * b["atr"][i - 1] and lvl[i] is not None and (c[i] - lvl[i]) * d > 0
        self.sig_cache[key] = out
        return out

    def htf_ok(self, tf, model, d, t_close):
        H = self.B[HIGHER[tf]]; hs = STEP[HIGHER[tf]]; k = last_closed(H["t"], hs, t_close)
        self._chk("htf_closed", H["t"][k] + hs <= t_close)
        ok = (H["c"][k] - H["e200"][k]) * d > 0
        if model == "M5_TREND_DC55": ok = ok and (H["e200"][k] - H["e200"][k - 10]) * d > 0
        return ok

    def regime(self, t_close):
        D = self.B["1d"]; k = last_closed(D["t"], 86400, t_close); self._chk("daily_closed", D["t"][k] + 86400 <= t_close)
        slope = D["e200"][k] - D["e200"][k - 20]
        return "bull" if D["c"][k] > D["e200"][k] and slope > 0 else "bear" if D["c"][k] < D["e200"][k] and slope < 0 else "sideways"

    def simulate(self, tf, model, d, stop, w0, w1, stop_mult=2.0, trail_mult=3.0, dc_len=None):
        """Defaults = locked protocol. Optional arguments exist only for the post-hoc neighbourhood diagnostic."""
        E, P = self.B[tf], self.B["15m"]; step = STEP[tf]; sig = self.signals(tf, model, d, dc_len)
        pt, po, ph, pl, pc = P["t"], P["o"], P["h"], P["l"], P["c"]
        trades, n = [], len(E["t"])
        i = last_closed(E["t"], step, w0 + step)  # first candle with open >= w0 (approx), then guard below
        i = max(i, 260)
        while i < n and E["t"][i] < w1:
            if E["t"][i] < w0 or not sig[i]: i += 1; continue
            t_sig_close = E["t"][i] + step
            if not self.htf_ok(tf, model, d, t_sig_close): i += 1; continue
            j = self.p_idx.get(t_sig_close)
            if j is None or pt[j] >= w1: i += 1; continue
            self._chk("entry_after_signal", pt[j] >= t_sig_close)
            entry = po[j]; atr = E["atr"][i]; sl = entry - d * stop_mult * atr; risk = abs(entry - sl); tp = entry + d * 2 * risk
            best_close = entry; R, reason, t_exit = None, None, None
            while j < len(pt):
                h, l, c = ph[j], pl[j], pc[j]; adverse, favor = (l, h) if d > 0 else (h, l)
                if (adverse - sl) * d <= 0:
                    px = po[j] if (po[j] - sl) * d < 0 else sl  # gap through stop -> fill at open
                    R, reason = (px - entry) * d / risk, "stop"; break
                if stop == "FIXED" and (favor - tp) * d >= 0: R, reason = 2.0, "target"; break
                bar_close = pt[j] + 900
                if bar_close % step == 0:
                    k = last_closed(E["t"], step, bar_close)
                    if stop == "TRAIL":
                        best_close = max(best_close, c) if d > 0 else min(best_close, c)
                        trail = best_close - d * trail_mult * E["atr"][k]
                        if (trail - sl) * d > 0: sl = trail
                if bar_close >= w1: R, reason = (c - entry) * d / risk, "window_end"; break
                j += 1
            if R is None: j = len(pt) - 1; R, reason = (pc[j] - entry) * d / risk, "data_end"
            t_exit = pt[j] + 900
            trades.append(dict(entry_time=t_sig_close, exit_time=t_exit, side=d, entry=round(entry, 2), risk=round(risk, 4),
                               R_gross=round(R, 6), k=entry / risk, exit=reason, regime=self.regime(t_sig_close),
                               hold_h=round((t_exit - t_sig_close) / 3600, 2)))
            i = last_closed(E["t"], step, t_exit) + 1
        return trades

def metrics(trades, cost):
    r = [x["R_gross"] - cost * x["k"] for x in trades]
    if not r: return dict(trades=0, net_pct=0.0, pf=None, expectancy=None, t_stat=None, max_dd_pct=0.0, win_rate=None, avg_hold_h=None)
    eq = peak = 1.0; mdd = 0.0
    for v in r: eq *= 1 + RISK * v; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
    pos, neg = sum(v for v in r if v > 0), -sum(v for v in r if v < 0)
    m = statistics.mean(r); sd = statistics.stdev(r) if len(r) > 1 else 0
    return dict(trades=len(r), net_pct=round((eq - 1) * 100, 2), pf=round(pos / neg, 3) if neg else None, expectancy=round(m, 4),
                t_stat=round(m / (sd / math.sqrt(len(r))), 2) if sd else None, max_dd_pct=round(mdd * 100, 2),
                win_rate=round(sum(v > 0 for v in r) / len(r) * 100, 1), avg_hold_h=round(statistics.mean(x["hold_h"] for x in trades), 1))
