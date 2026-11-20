"""Hourly time-of-day signals (PROTOCOL.md) on Exness 15-minute bid/ask candles."""
import calendar
import math
import os
import random
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "oil_rsi_vwap", "src"))
import oil
import study as S

SLIP_BPS = {"primary": 2.0, "stress": 5.0}
SWAP_BPS_STRESS = 2.0
SEED = 20261110
RUNS = 1000
H = 3600


def us_dst(t):
    """True if US daylight saving time is in force at UTC time t (2nd Sunday of March to 1st Sunday of November)."""
    y = time.gmtime(t).tm_year

    def nth_sunday(month, n):
        d = 1 + (6 - time.gmtime(calendar.timegm((y, month, 1, 0, 0, 0))).tm_wday) % 7
        return d + 7 * (n - 1)
    start = calendar.timegm((y, 3, nth_sunday(3, 2), 7, 0, 0))     # 02:00 EST = 07:00 UTC
    end = calendar.timegm((y, 11, nth_sunday(11, 1), 6, 0, 0))     # 02:00 EDT = 06:00 UTC
    return start <= t < end


def ny_to_utc(day_utc0, hh, mm):
    """UTC timestamp of New York local time hh:mm on the calendar day starting at day_utc0 (00:00 UTC)."""
    guess = day_utc0 + hh * H + mm * 60 + 5 * H
    return guess - H if us_dst(guess) else guess


def rollover(day_utc0):
    """Daily rollover: 17:00 New York (21:00 UTC in summer, 22:00 UTC in winter)."""
    return ny_to_utc(day_utc0, 17, 0)


class Quotes:
    def __init__(self, path):
        self.q = oil.load_15m(path)
        self.idx = {t: j for j, t in enumerate(self.q["t"])}

    def bid(self, t):
        j = self.idx.get(t)
        return None if j is None else self.q["bo"][j]

    def trade(self, t_in, t_out, d, cost="primary"):
        """Net result in basis points of a trade entered at t_in and closed at t_out, or None if a quote is missing."""
        a, b = self.idx.get(t_in), self.idx.get(t_out)
        if a is None or b is None or t_out <= t_in:
            return None
        q = self.q
        entry = q["ao"][a] if d > 0 else q["bo"][a]
        exit_ = q["bo"][b] if d > 0 else q["ao"][b]
        r = (exit_ - entry) / entry * d * 1e4 - SLIP_BPS[cost]
        if cost == "stress":
            day = t_in // 86400 * 86400
            if any(t_in < rollover(day + k * 86400) <= t_out for k in (-1, 0, 1)):
                r -= SWAP_BPS_STRESS
        return r


def days(w0, w1):
    return range(w0 // 86400 * 86400, w1, 86400)


def weekday(t):
    return time.gmtime(t).tm_wday


# ------------------------------------------------------------------------------------------- signals
def s1_oil_momentum(qt, w0, w1):
    """Returns list of (day, direction, entry_t, exit_t)."""
    out, prev_close = [], None
    for day in days(w0 - 10 * 86400, w1):
        if weekday(day) >= 5:
            continue
        c1430 = ny_to_utc(day, 14, 30)
        p930, p1400 = ny_to_utc(day, 9, 30), ny_to_utc(day, 14, 0)
        if prev_close is not None and day >= w0:
            b930 = qt.bid(p930)
            if b930 is not None and b930 != prev_close:
                d = 1 if b930 > prev_close else -1
                out.append((day, d, p1400, c1430))
        b = qt.bid(c1430)
        if b is not None:
            prev_close = b
    return out


def fixed_window(w0, w1, start_h, length_h, d, weekdays_only=True):
    return [(day, d, day + start_h * H, day + (start_h + length_h) * H)
            for day in days(w0, w1) if not (weekdays_only and weekday(day) >= 5)]


SIGNALS = {
    "S1_OIL_INTRADAY_MOMENTUM": ("USOILm", lambda qt, w0, w1: s1_oil_momentum(qt, w0, w1)),
    "S2a_GOLD_ASIAN_LONG": ("XAUUSDm", lambda qt, w0, w1: fixed_window(w0, w1, 0, 7, 1)),
    "S2b_GOLD_US_SHORT": ("XAUUSDm", lambda qt, w0, w1: fixed_window(w0, w1, 13, 7, -1)),
    "S3_BTC_LATE_EVENING_LONG": ("BTCUSDm", lambda qt, w0, w1: fixed_window(w0, w1, 21, 2, 1, weekdays_only=False)),
}


# ------------------------------------------------------------------------------------------- statistics
def summary(rs):
    n = len(rs)
    if n < 2:
        return {"trades": n}
    m, sd = statistics.mean(rs), statistics.stdev(rs)
    t = m / (sd / math.sqrt(n)) if sd > 0 else None
    wins, losses = [x for x in rs if x > 0], [x for x in rs if x <= 0]
    cum = peak = dd = 0.0
    for x in rs:
        cum += x
        peak = max(peak, cum)
        dd = max(dd, peak - cum)
    return {"trades": n, "win_rate_pct": len(wins) / n * 100, "mean_bps": m, "median_bps": statistics.median(rs), "t_stat": t,
            "p_one_sided": S.t_sf(t, n - 1) if t is not None else None, "total_bps": sum(rs), "max_drawdown_bps": dd,
            "profit_factor": sum(wins) / -sum(losses) if losses and sum(losses) < 0 else None}


def evaluate(name, qt, plan, cost="primary"):
    """Trades from a plan, plus the pre-registered random benchmark."""
    trades = [(day, d, a, b, qt.trade(a, b, d, cost)) for day, d, a, b in plan]
    trades = [x for x in trades if x[4] is not None]
    rs = [x[4] for x in trades]
    res = summary(rs)
    if res["trades"] < 2:
        return res
    res["stress_mean_bps"] = statistics.mean(r for r in (qt.trade(a, b, d, "stress") for _, d, a, b, _ in trades) if r is not None)
    rnd = random.Random(SEED)
    means = []
    if name.startswith("S1"):
        alt = [qt.trade(a, b, -d, cost) for _, d, a, b, _ in trades]
        for _ in range(RUNS):
            means.append(statistics.mean(r if rnd.random() < 0.5 else ar for r, ar in zip(rs, alt)))
        res["always_long_mean_bps"] = statistics.mean(r if d > 0 else ar for (_, d, _, _, r), ar in zip(trades, alt))
    else:
        options = []
        for day, d, a, b, _ in trades:
            length = b - a
            opts = [qt.trade(day + h * H, day + h * H + length, d, cost) for h in range(24)]
            options.append([o for o in opts if o is not None])
        for _ in range(RUNS):
            means.append(statistics.mean(rnd.choice(o) for o in options if o))
        res["all_hours_mean_bps"] = statistics.mean(x for o in options for x in o)
    res["random_mean_bps"] = statistics.mean(means)
    res["p_random"] = (sum(x >= res["mean_bps"] for x in means) + 1) / (len(means) + 1)
    return res
