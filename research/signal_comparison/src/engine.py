"""Trade simulation on hourly bid/ask candles, and causal regime labels.

``Outcomes`` precomputes, for every hour, what a trade ENTERED at that hour's first quote would have done under
one direction and one exit rule. Any signal list is then turned into trades by walking forward in time and
never holding two positions at once. Random-entry benchmarks reuse the same table, so a benchmark trade is
simulated exactly like a strategy trade.
"""
import dataclasses
import random

import indicators as ind
import marketdata as md
import protocol as P


@dataclasses.dataclass(frozen=True)
class Trade:
    signal_index: int      # 1H bar whose close produced the signal
    entry_index: int       # 1H bar at whose first quote the position is opened
    exit_index: int        # 1H bar during (or at the close of) which it is closed
    entry_time: int
    exit_time: int
    direction: int
    entry: float
    risk: float            # price distance of 1R (2 x ATR14)
    r_spread: float        # result in R with the real spread only
    reason: str
    regime: str
    entry_spread: float = 0.0   # ask - bid at the entry quote

    def r_net(self, cost, today_spread_fraction=None):
        if cost == P.TODAY_COST:
            # diagnostic: swap the actual entry spread for a recent typical one (fraction of price)
            swapped = (self.entry_spread - today_spread_fraction * self.entry) / self.risk
            return self.r_spread + swapped - P.COSTS[P.PRIMARY_COST]["slippage"] * self.entry / self.risk
        c = P.COSTS[cost]
        days = (self.exit_time - self.entry_time) / 86400.0
        return self.r_spread - (c["slippage"] + c["swap_per_day"] * days) * self.entry / self.risk

    @property
    def hold_hours(self):
        return (self.exit_time - self.entry_time) / 3600.0


class Regimes:
    """bull / bear / sideways from daily bars built from the hourly bid candles. Causal."""

    def __init__(self, h1):
        self.d1 = md.aggregate(h1, md.D1)
        self.e200 = ind.ema(self.d1.c, 200)

    def at(self, t):
        """Label using the last UTC day that was complete at time t."""
        k = md.last_closed_index(self.d1, t)
        if k < 20 or self.e200[k] is None or self.e200[k - 20] is None:
            return "undefined"
        slope = self.e200[k] - self.e200[k - 20]
        c = self.d1.c[k]
        if c > self.e200[k] and slope > 0:
            return "bull"
        if c < self.e200[k] and slope < 0:
            return "bear"
        return "sideways"


class Outcomes:
    """outcome[e] = (r_spread, exit_index, exit_time, reason, entry, risk) for an entry at bar e, or None."""

    def __init__(self, market, direction, exit_rule):
        if exit_rule not in P.EXITS:
            raise ValueError(exit_rule)
        self.market, self.d, self.exit_rule = market, direction, exit_rule
        b = market.h1
        self.atr = ind.atr(b.h, b.l, b.c, P.ATR_PERIOD)
        self.table = [None] * len(b)
        for e in range(1, len(b)):
            if self.atr[e - 1] is not None and self.atr[e - 1] > 0:
                self.table[e] = self._simulate(e)

    def _simulate(self, e):
        m, b, d, atr = self.market, self.market.h1, self.d, self.atr
        n = len(b)
        long = d > 0
        entry = m.ao[e] if long else b.o[e]
        risk = P.STOP_ATR * atr[e - 1]
        sl = entry - d * risk
        tp = entry + d * P.SYM_TARGET_ATR * atr[e - 1]
        best = entry
        j = e
        while j < n:
            # quotes that can hurt / help: a long is closed at the bid, a short at the ask
            o_x, adverse, favor, c_x = (b.o[j], b.l[j], b.h[j], b.c[j]) if long else (m.ao[j], m.ah[j], m.al[j], m.ac[j])
            if (adverse - sl) * d <= 0:
                px = o_x if (o_x - sl) * d < 0 else sl          # gap through the stop fills at the opening quote
                return ((px - entry) * d / risk, j, b.t[j] + md.H1, "stop", entry, risk)
            if self.exit_rule == "SYM":
                if (favor - tp) * d >= 0:
                    return ((tp - entry) * d / risk, j, b.t[j] + md.H1, "target", entry, risk)
                if j - e + 1 >= P.SYM_MAX_BARS:
                    return ((c_x - entry) * d / risk, j, b.t[j] + md.H1, "time", entry, risk)
            else:
                best = max(best, b.c[j]) if long else min(best, b.c[j])
                trail = best - d * P.TRAIL_ATR * atr[j]
                if (trail - sl) * d > 0:
                    sl = trail
            j += 1
        j = n - 1
        c_x = b.c[j] if long else m.ac[j]
        return ((c_x - entry) * d / risk, j, b.t[j] + md.H1, "data_end", entry, risk)


def trades_from_signals(outcomes, signals, regimes, start_index=0):
    """Sequential, one position at a time. A signal at bar i enters at bar i+1 (the next available hour)."""
    b = outcomes.market.h1
    out, i, n = [], start_index, len(b)
    while i < n - 1:
        if not signals[i] or outcomes.table[i + 1] is None:
            i += 1
            continue
        e = i + 1
        r, x, t_exit, reason, entry, risk = outcomes.table[e]
        out.append(Trade(i, e, x, b.t[e], t_exit, outcomes.d, entry, risk, r, reason, regimes.at(b.t[e]),
                         outcomes.market.ao[e] - b.o[e]))
        i = max(x, e)     # a signal on the exit bar's close is allowed (it comes after the exit)
    return out


def random_expectancies(outcomes, first_index, last_index, n_trades, cost, runs, seed):
    """Mean net R of ``runs`` random-entry strategies with ~n_trades entries in [first_index, last_index)."""
    rnd = random.Random(seed)
    pool = [e for e in range(max(first_index, 1), last_index) if outcomes.table[e] is not None]
    b = outcomes.market.h1
    c = P.COSTS[cost]
    means = []
    if not pool or n_trades < 1:
        return means
    for _ in range(runs):
        picks = sorted(rnd.sample(pool, min(n_trades, len(pool))))
        total, count, busy_until = 0.0, 0, -1
        for e in picks:
            if e <= busy_until:
                continue
            r, x, t_exit, _, entry, risk = outcomes.table[e]
            days = (t_exit - b.t[e]) / 86400.0
            total += r - (c["slippage"] + c["swap_per_day"] * days) * entry / risk
            count += 1
            busy_until = x
        if count:
            means.append(total / count)
    return means


def index_at_or_after(bars, t):
    import bisect
    return bisect.bisect_left(bars.t, t)


def today_spread_fraction(market, before_time):
    """Median opening spread (fraction of price) in the year before ``before_time``."""
    import statistics
    b = market.h1
    lo, hi = index_at_or_after(b, before_time - P.TODAY_SPREAD_WINDOW_DAYS * 86400), index_at_or_after(b, before_time)
    return statistics.median((market.ao[i] - b.o[i]) / b.o[i] for i in range(lo, hi))
