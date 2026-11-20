"""Replica of the frozen engine's trailing-stop long simulation, with execution knobs the engine does not have.

With default arguments it must reproduce engine.Lab.simulate() trade for trade (verified in verify_replica.py and
tests). The knobs (entry delay, stop slippage, separate execution prices) are used only for sensitivity analysis.

Execution model of the frozen engine, reproduced exactly:
  * signal on a CLOSED 1H candle (Donchian 20 cross + last closed 4H close > EMA200);
  * entry at the OPEN of the 15m candle that starts at the signal close;
  * initial stop = entry - 2 x ATR14 of the signal candle; risk R = entry - stop;
  * the stop is checked on every 15m low (gap through the stop fills at the 15m open), BEFORE the trail update;
  * at each 1H close the stop rises to max(stop, highest 1H close since entry - 3 x ATR14 of that 1H candle);
  * after an exit, the next signal must be on a 1H candle that closes after the exit time.
"""
import bisect
import dataclasses


@dataclasses.dataclass(frozen=True)
class Trade:
    signal_index: int
    entry_time: int
    exit_time: int
    entry: float
    risk: float
    r_gross: float
    reason: str
    regime: str

    @property
    def k(self):
        """Price / risk: converts a cost in fraction of price into R."""
        return self.entry / self.risk

    def r_net(self, cost_fraction):
        return self.r_gross - cost_fraction * self.k

    @property
    def hold_hours(self):
        return (self.exit_time - self.entry_time) / 3600.0


class Market:
    """Arrays the simulation needs. Signal prices and execution prices may differ (e.g. Exness bid vs ask)."""

    def __init__(self, lab, exec_open=None, exec_low=None):
        self.lab = lab
        self.E, self.P = lab.B["1h"], lab.B["15m"]
        self.pt, self.po, self.ph, self.pl, self.pc = (self.P[k] for k in ("t", "o", "h", "l", "c"))
        # long entries pay exec_open (e.g. ask); stops are hit on exec_low / filled on the bid series (pl/po)
        self.entry_open = exec_open if exec_open is not None else self.po
        self.exit_low = exec_low if exec_low is not None else self.pl
        self.exit_open = self.po
        self.exit_close = self.pc
        self.p_idx = lab.p_idx
        self.sig = lab.signals("1h", "M2_DONCHIAN20", 1)
        H = lab.B["4h"]
        self.filter_on = [False] * len(self.E["t"])
        for i in range(len(self.E["t"])):
            tc = self.E["t"][i] + 3600
            k = bisect.bisect_right(H["t"], tc - 14400) - 1
            if k >= 0 and H["e200"][k] is not None:
                self.filter_on[i] = H["c"][k] > H["e200"][k]
        self._regime_cache = {}

    def regime(self, t):
        if t not in self._regime_cache:
            self._regime_cache[t] = self.lab.regime(t)
        return self._regime_cache[t]

    def last_closed_1h(self, t_close):
        """Index of the last 1H candle whose close is <= t_close."""
        return bisect.bisect_right(self.E["t"], t_close - 3600) - 1

    def simulate_from(self, i, w1=10 ** 11, delay=0, stop_slip=0.0, stop_mult=2.0, trail_mult=3.0):
        """One long trade from a signal on 1H candle i. Returns a Trade or None if no entry bar exists."""
        E = self.E
        t_sig_close = E["t"][i] + 3600
        j = self.p_idx.get(t_sig_close)
        if j is None:
            return None
        if delay:
            j += delay
            if j >= len(self.pt) or self.pt[j] - t_sig_close > 900 * delay * 4:   # data gap: skip
                return None
        if self.pt[j] >= w1 or E["atr"][i] is None:
            return None
        entry = self.entry_open[j]
        atr = E["atr"][i]
        sl = entry - stop_mult * atr
        risk = entry - sl
        best = entry
        pt, _pl, po, pc, xl = self.pt, self.pl, self.exit_open, self.exit_close, self.exit_low
        n = len(pt)
        R = reason = None
        while j < n:
            if xl[j] <= sl:
                px = po[j] if po[j] < sl else sl * (1 - stop_slip)
                R, reason = (px - entry) / risk, "stop"
                break
            bar_close = pt[j] + 900
            if bar_close % 3600 == 0:
                k = self.last_closed_1h(bar_close)
                best = max(best, pc[j])
                trail = best - trail_mult * E["atr"][k]
                sl = max(sl, trail)
            if bar_close >= w1:
                R, reason = (pc[j] - entry) / risk, "window_end"
                break
            j += 1
        if R is None:
            j = n - 1
            R, reason = (pc[j] - entry) / risk, "data_end"
        return Trade(i, t_sig_close, pt[j] + 900, entry, risk, R, reason, self.regime(t_sig_close))

    def run(self, w0, w1, signals=None, **kw):
        """Sequential one-position simulation over signals (default: the frozen Donchian signals + 4H filter)."""
        E = self.E
        sig = self.sig if signals is None else signals
        use_filter = signals is None
        out = []
        i = max(self.last_closed_1h(w0 + 3600), 260)
        n = len(E["t"])
        while i < n and E["t"][i] < w1:
            if E["t"][i] < w0 or not sig[i] or (use_filter and not self.filter_on[i]):
                i += 1
                continue
            tr = self.simulate_from(i, w1=w1, **kw)
            if tr is None:
                i += 1
                continue
            out.append(tr)
            i = self.last_closed_1h(tr.exit_time) + 1
        return out
