"""RSI + VWAP entry study (see PROTOCOL.md). Pure Python. Every value at 1H bar i uses only candles closed by then."""
import bisect
import calendar
import collections
import dataclasses
import json
import math
import os
import random
import statistics
import time

RSI_N, ATR_N = 14, 14
STOP_ATR, TRAIL_ATR, SYM_TARGET_ATR, SYM_MAX_HOURS = 2.0, 3.0, 2.0, 48
COSTS = {"primary": 0.0005, "stress": 0.0010}
RULES = ("V1_VWAP_MOMENTUM", "V2_RSI_REVERSION")
DIRECTIONS = {"BUY": 1, "SELL": -1}
EXITS = ("TRAIL", "SYM")
SEED = 20261110
RANDOM_RUNS = 2000
BOOT = 5000


def ts(y, m, d=1):
    return calendar.timegm((y, m, d, 0, 0, 0))


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


# ------------------------------------------------------------------------------------------- indicators
def rsi(c, n=RSI_N):
    out = [None] * len(c)
    if len(c) <= n:
        return out
    g = sum(max(c[i] - c[i - 1], 0) for i in range(1, n + 1)) / n
    lo = sum(max(c[i - 1] - c[i], 0) for i in range(1, n + 1)) / n
    out[n] = 100.0 if lo == 0 else 100 - 100 / (1 + g / lo)
    for i in range(n + 1, len(c)):
        d = c[i] - c[i - 1]
        g = (g * (n - 1) + max(d, 0)) / n
        lo = (lo * (n - 1) + max(-d, 0)) / n
        out[i] = 100.0 if lo == 0 else 100 - 100 / (1 + g / lo)
    return out


def atr(h, l, c, n=ATR_N):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    out = [None] * len(c)
    if len(c) < n:
        return out
    s = sum(tr[:n]) / n
    out[n - 1] = s
    for i in range(n, len(c)):
        s = (s * (n - 1) + tr[i]) / n
        out[i] = s
    return out


def ema_from_first(x, n):
    """EMA seeded with the first value (same convention as the frozen research engine, used for regime labels)."""
    a, out = 2 / (n + 1), []
    for i, v in enumerate(x):
        out.append(v if i == 0 else a * v + (1 - a) * out[-1])
    return out


def session_vwap(t, h, l, c, v):
    """VWAP anchored at 00:00 UTC, over the session's candles up to and including candle i."""
    out = [None] * len(c)
    day, pv, vol = None, 0.0, 0.0
    for i in range(len(c)):
        dd = t[i] // 86400
        if dd != day:
            day, pv, vol = dd, 0.0, 0.0
        pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        vol += v[i]
        out[i] = pv / vol if vol > 0 else None
    return out


# ------------------------------------------------------------------------------------------- data
@dataclasses.dataclass
class Bars:
    t: list
    o: list
    h: list
    l: list
    c: list
    v: list


def load(path):
    with open(path) as f:
        rows = json.load(f)
    rows.sort(key=lambda r: r[0])
    return Bars(*([r[k] for r in rows] for k in range(6)))


class Asset:
    def __init__(self, name, path_15m, path_1h, path_1d):
        self.name = name
        self.p, self.e, self.d = load(path_15m), load(path_1h), load(path_1d)
        E = self.e
        self.rsi = rsi(E.c)
        self.atr = atr(E.h, E.l, E.c)
        self.vwap = session_vwap(E.t, E.h, E.l, E.c, E.v)
        self.p_idx = {t: j for j, t in enumerate(self.p.t)}
        self.e_idx = {t: i for i, t in enumerate(E.t)}
        self.d_e200 = ema_from_first(self.d.c, 200)
        self._tables = {}

    # -- signals
    def signals(self, rule, d):
        E, r, w = self.e, self.rsi, self.vwap
        out = [False] * len(E.t)
        for i in range(1, len(E.t)):
            if r[i] is None or r[i - 1] is None or w[i] is None or w[i - 1] is None:
                continue
            if rule == "V1_VWAP_MOMENTUM":
                same_session = E.t[i] // 86400 == E.t[i - 1] // 86400
                cross = (E.c[i] - w[i]) * d > 0 and (E.c[i - 1] - w[i - 1]) * d <= 0
                out[i] = same_session and cross and (r[i] - 50) * d > 0
            elif rule == "V2_RSI_REVERSION":
                level = 30 if d > 0 else 70
                cross = (r[i - 1] - level) * d < 0 <= (r[i] - level) * d
                out[i] = cross and (E.c[i] - w[i]) * d < 0
            else:
                raise ValueError(rule)
        return out

    def regime(self, t):
        """Label from the last COMPLETE UTC day before time t (daily EMA200 and its 20-day slope)."""
        k = bisect.bisect_right(self.d.t, t - 86400) - 1
        if k < 220:
            return "undefined"
        e, c = self.d_e200, self.d.c[k]
        slope = e[k] - e[k - 20]
        if c > e[k] and slope > 0:
            return "bull"
        if c < e[k] and slope < 0:
            return "bear"
        return "sideways"

    # -- trade outcome from a signal on 1H candle i
    def simulate(self, i, d, exit_rule, delay=0):
        """Trade from a signal on 1H candle i. ``delay`` (15m candles) is a diagnostic only; 0 is the protocol."""
        E, P = self.e, self.p
        t_close = E.t[i] + 3600
        j = self.p_idx.get(t_close)
        a = self.atr[i]
        if j is None or a is None or a <= 0:
            return None
        j += delay
        if j >= len(P.t):
            return None
        entry = P.o[j]
        risk = STOP_ATR * a
        sl = entry - d * risk
        tp = entry + d * SYM_TARGET_ATR * a
        best = entry
        n = len(P.t)
        while j < n:
            adverse, favor = (P.l[j], P.h[j]) if d > 0 else (P.h[j], P.l[j])
            if (adverse - sl) * d <= 0:
                px = P.o[j] if (P.o[j] - sl) * d < 0 else sl
                return Trade(i, t_close, P.t[j] + 900, d, entry, risk, (px - entry) * d / risk, "stop", self.regime(t_close))
            bar_close = P.t[j] + 900
            if exit_rule == "SYM":
                if (favor - tp) * d >= 0:
                    return Trade(i, t_close, bar_close, d, entry, risk, (tp - entry) * d / risk, "target", self.regime(t_close))
                if bar_close - t_close >= SYM_MAX_HOURS * 3600:
                    return Trade(i, t_close, bar_close, d, entry, risk, (P.c[j] - entry) * d / risk, "time", self.regime(t_close))
            elif bar_close % 3600 == 0:
                k = self.e_idx.get(bar_close - 3600)
                if k is not None and self.atr[k] is not None:
                    best = max(best, P.c[j]) if d > 0 else min(best, P.c[j])
                    trail = best - d * TRAIL_ATR * self.atr[k]
                    if (trail - sl) * d > 0:
                        sl = trail
            j += 1
        return None   # still open at the end of the data: not a completed trade

    def table(self, d, exit_rule):
        """Outcome of an entry after every 1H close (shared by the strategy and the random benchmark)."""
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
            i = bisect.bisect_left(E.t, tr.exit_time - 3600 + 1)   # next candle closing after the exit
        return out


@dataclasses.dataclass(frozen=True)
class Trade:
    signal_index: int
    entry_time: int
    exit_time: int
    direction: int
    entry: float
    risk: float
    r_gross: float
    reason: str
    regime: str

    def r(self, cost):
        return self.r_gross - COSTS[cost] * self.entry / self.risk

    @property
    def hold_hours(self):
        return (self.exit_time - self.entry_time) / 3600


# ------------------------------------------------------------------------------------------- statistics
def t_sf(t, df):
    """One-sided P(T > t), Student t (regularised incomplete beta, continued fraction)."""
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5

    def cf(a, b, x):
        tiny, qab, qap, qam = 1e-300, a + b, a + 1, a - 1
        c, dd = 1.0, 1 - qab * x / qap
        dd = 1 / (dd if abs(dd) > tiny else tiny)
        h = dd
        for m in range(1, 300):
            m2 = 2 * m
            for aa in (m * (b - m) * x / ((qam + m2) * (a + m2)), -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))):
                dd = 1 + aa * dd
                dd = 1 / (dd if abs(dd) > tiny else tiny)
                c = 1 + aa / c
                c = c if abs(c) > tiny else tiny
                h *= dd * c
            if abs(dd * c - 1) < 1e-12:
                break
        return h
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x))
    ib = bt * cf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - bt * cf(b, a, 1 - x) / b
    return ib / 2 if t > 0 else 1 - ib / 2


def summary(rs):
    n = len(rs)
    if n < 2:
        return {"trades": n}
    m, sd = statistics.mean(rs), statistics.stdev(rs)
    wins, losses = [x for x in rs if x > 0], [x for x in rs if x <= 0]
    cum = peak = dd = 0.0
    eq = epk = 1.0
    ddp = 0.0
    for x in rs:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
        eq *= 1 + 0.005 * x
        epk = max(epk, eq)
        ddp = max(ddp, 1 - eq / epk)
    t = m / (sd / math.sqrt(n)) if sd > 0 else None
    srt = sorted(rs, reverse=True)
    total = sum(rs)
    return {"trades": n, "win_rate_pct": len(wins) / n * 100, "profit_factor": sum(wins) / -sum(losses) if losses and sum(losses) < 0 else None,
                "expectancy_r": m, "t_stat": t, "p_one_sided": t_sf(t, n - 1) if t is not None else None, "total_r": total,
                "max_drawdown_r": dd, "max_drawdown_pct": ddp * 100, "top5_share_of_total_pct": sum(srt[:5]) / total * 100 if total > 0 else None,
                "expectancy_without_top5_r": statistics.mean(srt[5:]) if n > 6 else None}


def boot_ci(rs, seed=SEED):
    rnd = random.Random(seed)
    n = len(rs)
    ms = sorted(sum(rnd.choices(rs, k=n)) / n for _ in range(BOOT))
    return ms[int(0.025 * BOOT)], ms[int(0.975 * BOOT) - 1]


def holm(pvals):
    items = sorted((p, k) for k, p in pvals.items() if p is not None)
    adj, running = {}, 0.0
    for rank, (p, k) in enumerate(items):
        running = max(running, min(1.0, (len(items) - rank) * p))
        adj[k] = running
    return adj


# ------------------------------------------------------------------------------------------- random benchmark
def quarter(t):
    g = time.gmtime(t)
    return (g.tm_year, (g.tm_mon - 1) // 3)


def sequential_random(outcomes, p, rnd):
    chosen, busy = [], -1
    for tr in outcomes:
        if tr.entry_time < busy:
            continue
        if rnd.random() < p[quarter(tr.entry_time)]:
            chosen.append(tr)
            busy = tr.exit_time
    return chosen


def random_benchmark(asset, trades, d, exit_rule, w0, w1, cost="primary", runs=RANDOM_RUNS, seed=SEED):
    outcomes = [tr for tr in asset.table(d, exit_rule) if tr is not None and w0 <= tr.entry_time < w1]
    target = collections.Counter(quarter(tr.entry_time) for tr in trades)
    per_q = collections.Counter(quarter(tr.entry_time) for tr in outcomes)
    p = {q: min(1.0, target.get(q, 0) / per_q[q] * 4) for q in per_q}
    rnd = random.Random(seed)
    for _ in range(6):
        counts = collections.Counter()
        for _ in range(60):
            counts.update(quarter(x.entry_time) for x in sequential_random(outcomes, p, rnd))
        for q in list(p):
            want, got = target.get(q, 0), counts[q] / 60
            p[q] = 0.0 if want == 0 else min(1.0, p[q] * (want / got if got > 0 else 4))
    s_mean = statistics.mean(tr.r(cost) for tr in trades)
    means = []
    for _ in range(runs):
        ch = sequential_random(outcomes, p, rnd)
        if ch:
            means.append(statistics.mean(x.r(cost) for x in ch))
    means.sort()
    return {"random_mean_r": statistics.mean(means), "random_p05_p95": (means[int(0.05 * len(means))], means[int(0.95 * len(means))]),
                "excess_r": s_mean - statistics.mean(means), "p_random": (sum(x >= s_mean for x in means) + 1) / (len(means) + 1),
                "unconditional_mean_r": statistics.mean(x.r(cost) for x in outcomes)}


def env_path(*parts):
    return os.path.join(*parts)
