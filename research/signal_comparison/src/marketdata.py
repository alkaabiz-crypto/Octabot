"""Hourly bid/ask candles, UTC aggregation to 4H and daily bars, and causal index alignment."""
import bisect
import csv
import dataclasses
import gzip
import typing

H1, H4, D1 = 3600, 14400, 86400


@dataclasses.dataclass(frozen=True)
class Bars:
    """Bid OHLC bars. ``t`` is the bar's nominal open time (UTC seconds); ``end`` is when the bar is final."""
    step: int
    t: typing.List[int]
    o: typing.List[float]
    h: typing.List[float]
    l: typing.List[float]
    c: typing.List[float]

    def __len__(self):
        return len(self.t)

    def end(self, i):
        return self.t[i] + self.step


@dataclasses.dataclass(frozen=True)
class Market:
    """One asset: hourly bid bars plus the matching ask quotes needed for realistic fills."""
    symbol: str
    h1: Bars
    ao: typing.List[float]      # ask at the first quote of the hour
    ah: typing.List[float]
    al: typing.List[float]
    ac: typing.List[float]
    spread_mean: typing.List[float]
    ticks: typing.List[int]


def load_market(symbol, path, end_before=None, start_at=None):
    """Load hourly candles. Rows with open time >= ``end_before`` are never read into memory."""
    cols = {k: [] for k in ("t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "n", "spread_mean")}
    with gzip.open(path, "rt", newline="") as f:
        for r in csv.DictReader(f):
            t = int(r["t"])
            if end_before is not None and t >= end_before:
                break
            if start_at is not None and t < start_at:
                continue
            cols["t"].append(t)
            for k in ("bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "spread_mean"):
                cols[k].append(float(r[k]))
            cols["n"].append(int(r["n"]))
    if any(b <= a for a, b in zip(cols["t"], cols["t"][1:])):
        raise ValueError(f"{symbol}: hourly rows are not strictly increasing in time")
    h1 = Bars(H1, cols["t"], cols["bo"], cols["bh"], cols["bl"], cols["bc"])
    return Market(symbol, h1, cols["ao"], cols["ah"], cols["al"], cols["ac"], cols["spread_mean"], cols["n"])


def aggregate(bars, step):
    """Aggregate bars into UTC-aligned bins of ``step`` seconds. A bin exists only if it contains bars."""
    t, o, h, l, c = [], [], [], [], []
    for i in range(len(bars)):
        b = bars.t[i] // step * step
        if not t or t[-1] != b:
            t.append(b)
            o.append(bars.o[i])
            h.append(bars.h[i])
            l.append(bars.l[i])
            c.append(bars.c[i])
        else:
            if bars.h[i] > h[-1]:
                h[-1] = bars.h[i]
            if bars.l[i] < l[-1]:
                l[-1] = bars.l[i]
            c[-1] = bars.c[i]
    return Bars(step, t, o, h, l, c)


def last_closed_index(higher, at_time):
    """Index of the last ``higher`` bar whose end is <= ``at_time`` (so it is final by then), or -1."""
    # bars are final at t + step; find rightmost t with t + step <= at_time
    return bisect.bisect_right(higher.t, at_time - higher.step) - 1


def align(lower, higher):
    """For every lower bar i, the index of the last higher bar that is final when bar i closes."""
    return [last_closed_index(higher, lower.end(i)) for i in range(len(lower))]
