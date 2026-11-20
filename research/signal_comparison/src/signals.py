"""The three signal approaches. All inputs are closed bid candles; higher-timeframe values are causal."""
import dataclasses

import indicators as ind
import marketdata as md
import protocol as P


@dataclasses.dataclass(frozen=True)
class Features:
    """Per-bar indicator states for one timeframe and one parameter scale. ``None`` where undefined."""
    close: list
    ema_slow: list
    rsi: list
    dc_up: list
    dc_lo: list
    bull: dict[str, list]     # vote name -> list of bool/None
    bear: dict[str, list]

    def votes(self, d, names, i):
        """Number of votes in direction d (+1/-1) among ``names`` at bar i, or None if any is undefined."""
        side = self.bull if d > 0 else self.bear
        total = 0
        for nm in names:
            v = side[nm][i]
            if v is None:
                return None
            total += v
        return total


VOTES_5 = ("ema", "rsi", "macd", "adx", "mid")
CONFIRMERS_4 = ("ema", "rsi", "macd", "adx")


def features(bars, p):
    c, h, l = bars.c, bars.h, bars.l
    n = len(c)
    ef, es = ind.ema(c, p["ema_fast"]), ind.ema(c, p["ema_slow"])
    rs = ind.rsi(c, p["rsi"])
    line, sig = ind.macd(c, p["macd_fast"], p["macd_slow"], p["macd_signal"])
    ax, pdi, mdi = ind.adx(h, l, c, p["adx"])
    up, lo = ind.donchian(h, l, p["donchian"])
    bull = {k: [None] * n for k in VOTES_5}
    bear = {k: [None] * n for k in VOTES_5}
    for i in range(n):
        if es[i] is not None:
            bull["ema"][i] = c[i] > es[i] and ef[i] > es[i]
            bear["ema"][i] = c[i] < es[i] and ef[i] < es[i]
        if rs[i] is not None:
            bull["rsi"][i] = rs[i] > P.RSI_MID
            bear["rsi"][i] = rs[i] < P.RSI_MID
        if sig[i] is not None:
            bull["macd"][i] = line[i] > sig[i]
            bear["macd"][i] = line[i] < sig[i]
        if ax[i] is not None:
            trending = ax[i] >= P.ADX_MIN
            bull["adx"][i] = trending and pdi[i] > mdi[i]
            bear["adx"][i] = trending and mdi[i] > pdi[i]
        if up[i] is not None:
            mid = (up[i] + lo[i]) / 2.0
            bull["mid"][i] = c[i] > mid
            bear["mid"][i] = c[i] < mid
    return Features(c, es, rs, up, lo, bull, bear)


class SignalLab:
    """Computes and caches features per scale, and produces signal masks for every approach."""

    def __init__(self, market):
        self.market = market
        self.h1 = market.h1
        self.h4 = md.aggregate(market.h1, md.H4)
        self.k4 = md.align(self.h1, self.h4)       # last closed 4H bar for each 1H bar
        self._feat = {}

    def feats(self, scale):
        if scale not in self._feat:
            p = P.scaled(scale)
            self._feat[scale] = (features(self.h1, p), features(self.h4, p))
        return self._feat[scale]

    def _cross(self, f, d, i):
        """Fresh Donchian break in direction d at bar i (close crosses the previous-n-bar extreme)."""
        lvl = f.dc_up if d > 0 else f.dc_lo
        if i < 1 or lvl[i] is None or lvl[i - 1] is None:
            return False
        return (f.close[i] - lvl[i]) * d > 0 and (f.close[i - 1] - lvl[i - 1]) * d <= 0

    @staticmethod
    def _rsi_ok(f, d, i):
        return f.rsi[i] is not None and (f.rsi[i] <= P.RSI_HIGH if d > 0 else f.rsi[i] >= P.RSI_LOW)

    def a1(self, d, cand):
        f1, f4 = self.feats(cand["scale"])
        out = [False] * len(self.h1)
        for i in range(1, len(out)):
            k = self.k4[i]
            if k < 0 or f4.ema_slow[k] is None:
                continue
            out[i] = self._cross(f1, d, i) and (f4.close[k] - f4.ema_slow[k]) * d > 0
        return out

    def a2(self, d, cand):
        f1, f4 = self.feats(cand["scale"])
        out = [False] * len(self.h1)
        for i in range(1, len(out)):
            k = self.k4[i]
            if k < 0:
                continue
            gate = (f4.bull if d > 0 else f4.bear)["ema"][k]
            if not gate or not self._cross(f1, d, i):
                continue
            agree, against = f1.votes(d, CONFIRMERS_4, i), f1.votes(-d, CONFIRMERS_4, i)
            if agree is None or against is None:
                continue
            out[i] = agree >= P.MIN_CONFIRMERS and against == 0 and self._rsi_ok(f1, d, i)
        return out

    def _a3_condition(self, f1, f4, d, k_votes, i):
        k = self.k4[i]
        if k < 0:
            return None
        v1, v4 = f1.votes(d, VOTES_5, i), f4.votes(d, VOTES_5, k)
        if v1 is None or v4 is None:
            return None
        return v1 >= k_votes and v4 >= P.HTF_MIN_VOTES

    def a3(self, d, cand):
        f1, f4 = self.feats(cand["scale"])
        out = [False] * len(self.h1)
        prev = None
        for i in range(len(out)):
            cur = self._a3_condition(f1, f4, d, cand["k"], i)
            # a fresh alignment needs a defined, false condition on the previous bar
            out[i] = bool(cur) and prev is False and self._rsi_ok(f1, d, i)
            prev = cur
        return out

    def signals(self, approach, d, cand):
        return {"A1_DONCHIAN_TREND": self.a1, "A2_COMBINED": self.a2, "A3_VOTING": self.a3}[approach](d, cand)
