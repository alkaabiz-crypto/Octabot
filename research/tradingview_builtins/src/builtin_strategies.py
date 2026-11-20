"""TradingView's built-in strategies, replayed from their Pine source (default settings), on Exness bid/ask data.

Order handling mirrors TradingView's broker emulator closely enough for this purpose:
  * orders are decided at a 1H bar's close and are active during the next 1H bar;
  * market orders fill at that bar's first 15m open (buy at the ask, sell at the bid);
  * stop orders fill on the first 15m candle whose bid range reaches the stop, at max(open, stop) for buys (plus the
    spread) and min(open, stop) for sells; if two stops trigger in the same 15m candle, the one nearer its open first;
  * strategy.entry in the opposite direction reverses the position; in the same direction it is ignored (pyramiding 1);
  * pending orders persist across bars or are cancelled exactly as each script does;
  * at most one fill per 1H bar (a simplification; reversals within one hour are rare at these settings).
Not replayed: "Greedy strategy" (pyramiding of gap orders and intraday order limits) and "Technical ratings strategy"
(depends on TradingView's TechnicalRating library and request.security). "Bollinger Bands strategy directed" is the
plain Bollinger strategy with a direction switch, which the BUY/SELL split already covers.
"""
import dataclasses
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(RESEARCH, "tradingview_originals", "src"))
import ports as P  # noqa: E402  (sets up the shared paths)
import oil  # noqa: E402
import scan  # noqa: E402
import study as S  # noqa: E402


@dataclasses.dataclass
class Order:
    d: int            # +1 buy, -1 sell
    kind: str         # "market", "stop", or "exit" (close any open position at market; d is ignored)
    price: float = 0.0


def highest(x, n, i):
    return max(x[i - n + 1:i + 1]) if i >= n - 1 else None


def lowest(x, n, i):
    return min(x[i - n + 1:i + 1]) if i >= n - 1 else None


def crossover(a, b, i):
    return i >= 1 and None not in (a[i], a[i - 1], b[i], b[i - 1]) and a[i] > b[i] and a[i - 1] <= b[i - 1]


def crossunder(a, b, i):
    return i >= 1 and None not in (a[i], a[i - 1], b[i], b[i - 1]) and a[i] < b[i] and a[i - 1] >= b[i - 1]


def pivots_confirmed(x, left, right, kind):
    """Pine ta.pivothigh/low(left, right): True at the bar where the pivot (right bars back) is confirmed."""
    n = len(x)
    out = [None] * n
    for i in range(left + right, n):
        p = i - right
        w = x[p - left:p + right + 1]
        v = x[p]
        if kind == "high" and v == max(w) and all(v > y for k, y in enumerate(w) if k != left):
            out[i] = v
        if kind == "low" and v == min(w) and all(v < y for k, y in enumerate(w) if k != left):
            out[i] = v
    return out


# ------------------------------------------------------------------------------------------- order generators
def strategy_orders(name, E, atr14):
    """Return a list (per 1H bar) of orders active in the NEXT bar, plus extra state for ADX breakout."""
    o, h, l, c = E.o, E.h, E.l, E.c
    n = len(c)
    orders = [[] for _ in range(n)]
    if name == "BAR_UP_DOWN":
        for i in range(1, n):
            if c[i] > o[i] and o[i] > c[i - 1]:
                orders[i].append(Order(1, "market"))
            if c[i] < o[i] and o[i] < c[i - 1]:
                orders[i].append(Order(-1, "market"))
    elif name == "BOLLINGER_BANDS":
        up, lo = scan.bollinger(c, 20, 2.0)
        for i in range(1, n):
            if crossover(c, lo, i):
                orders[i].append(Order(1, "stop", lo[i]))
            if crossunder(c, up, i):
                orders[i].append(Order(-1, "stop", up[i]))
    elif name == "CHANNEL_BREAKOUT":
        for i in range(5, n):
            orders[i].append(Order(1, "stop", highest(h, 5, i)))
            orders[i].append(Order(-1, "stop", lowest(l, 5, i)))
    elif name == "CONSECUTIVE_UP_DOWN":
        ups = dns = 0
        for i in range(1, n):
            ups = ups + 1 if c[i] > c[i - 1] else 0
            dns = dns + 1 if c[i] < c[i - 1] else 0
            if ups >= 3:
                orders[i].append(Order(1, "market"))
            if dns >= 3:
                orders[i].append(Order(-1, "market"))
    elif name in ("INSIDE_BAR", "OUTSIDE_BAR"):
        for i in range(1, n):
            cond = (h[i] < h[i - 1] and l[i] > l[i - 1]) if name == "INSIDE_BAR" else (h[i] > h[i - 1] and l[i] < l[i - 1])
            if cond and c[i] > o[i]:
                orders[i].append(Order(1, "market"))
            if cond and c[i] < o[i]:
                orders[i].append(Order(-1, "market"))
    elif name == "KELTNER_CHANNELS":
        ma = scan.ema(c, 20)
        rng = S.atr(h, l, c, 10)
        up = [None if a is None or b is None else a + b * 2.0 for a, b in zip(ma, rng)]
        lo = [None if a is None or b is None else a - b * 2.0 for a, b in zip(ma, rng)]
        bprice = sprice = None
        bcond = scond = False
        long_live = short_live = False
        for i in range(1, n):
            cu, cl = crossover(c, up, i), crossunder(c, lo, i)
            if cu:
                bprice = h[i]
                bcond = True
            if cl:
                sprice = l[i]
                scond = True
            if bcond and ma[i] is not None and (c[i] < ma[i] or h[i] >= bprice):
                long_live = False
            if cu:
                long_live = True
            if scond and ma[i] is not None and (c[i] > ma[i] or l[i] <= sprice):
                short_live = False
            if cl:
                short_live = True
            if long_live:
                orders[i].append(Order(1, "stop", bprice))
            if short_live:
                orders[i].append(Order(-1, "stop", sprice))
    elif name == "MACD":
        e12, e26 = scan.ema(c, 12), scan.ema(c, 26)
        macd = [None if a is None or b is None else a - b for a, b in zip(e12, e26)]
        sig = P.C1.ema_sparse(macd, 9)
        delta = [None if a is None or b is None else a - b for a, b in zip(macd, sig)]
        zero = [0.0] * n
        for i in range(1, n):
            if crossover(delta, zero, i):
                orders[i].append(Order(1, "market"))
            if crossunder(delta, zero, i):
                orders[i].append(Order(-1, "market"))
    elif name == "MOMENTUM":
        for i in range(13, n):
            m0, m0p = c[i] - c[i - 12], c[i - 1] - c[i - 13]
            m1 = m0 - m0p
            if m0 > 0 and m1 > 0:
                orders[i].append(Order(1, "stop", h[i]))
            if m0 < 0 and m1 < 0:
                orders[i].append(Order(-1, "stop", l[i]))
    elif name == "MA_CROSSOVER":
        ma = scan.sma(c, 9)
        bc = sc = 0
        for i in range(n):
            if ma[i] is None:
                continue
            bc = bc + 1 if c[i] > ma[i] else 0
            sc = sc + 1 if c[i] < ma[i] else 0
            if bc == 1:
                orders[i].append(Order(1, "market"))
            if sc == 1:
                orders[i].append(Order(-1, "market"))
    elif name == "TWO_MA_CROSSOVER":
        f, s = scan.sma(c, 9), scan.sma(c, 18)
        for i in range(1, n):
            if crossover(f, s, i):
                orders[i].append(Order(1, "market"))
            if crossunder(f, s, i):
                orders[i].append(Order(-1, "market"))
    elif name == "PARABOLIC_SAR":
        start, inc, mx = 0.02, 0.02, 0.2
        uptrend, ep, sar, af, next_sar = False, None, None, start, None
        for i in range(1, n):
            first = False
            sar = next_sar
            if i == 1:
                if c[i] > c[i - 1]:
                    uptrend, ep, prev_sar, prev_ep = True, h[i], l[i - 1], h[i]
                else:
                    uptrend, ep, prev_sar, prev_ep = False, l[i], h[i - 1], l[i]
                first = True
                sar = prev_sar + start * (prev_ep - prev_sar)
            if uptrend:
                if sar > l[i]:
                    first, uptrend, sar, ep, af = True, False, max(ep, h[i]), l[i], start
            elif sar < h[i]:
                first, uptrend, sar, ep, af = True, True, min(ep, l[i]), h[i], start
            if not first:
                if uptrend and h[i] > ep:
                    ep, af = h[i], min(af + inc, mx)
                elif not uptrend and l[i] < ep:
                    ep, af = l[i], min(af + inc, mx)
            if uptrend:
                sar = min(sar, l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            else:
                sar = max(sar, h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            next_sar = sar + af * (ep - sar)
            orders[i].append(Order(-1, "stop", next_sar) if uptrend else Order(1, "stop", next_sar))
    elif name == "PIVOT_EXTENSION":
        ph, pl = pivots_confirmed(h, 4, 2, "high"), pivots_confirmed(l, 4, 2, "low")
        for i in range(n):
            if pl[i] is not None:
                orders[i].append(Order(1, "market"))
            if ph[i] is not None:
                orders[i].append(Order(-1, "market"))
    elif name == "PIVOT_REVERSAL":
        ph, pl = pivots_confirmed(h, 4, 2, "high"), pivots_confirmed(l, 4, 2, "low")
        hp = lp = 0.0
        le = se = False
        for i in range(n):
            if ph[i] is not None:
                hp, le = ph[i], True
            elif le and h[i] > hp:
                le = False
            if pl[i] is not None:
                lp, se = pl[i], True
            elif se and l[i] < lp:
                se = False
            if le:
                orders[i].append(Order(1, "stop", hp))
            if se:
                orders[i].append(Order(-1, "stop", lp))
    elif name == "PRICE_CHANNEL":
        for i in range(20, n):
            orders[i].append(Order(1, "stop", highest(h, 20, i)))
            orders[i].append(Order(-1, "stop", lowest(l, 20, i)))
    elif name == "RSI":
        r = S.rsi(c, 14)
        for i in range(1, n):
            if r[i] is None or r[i - 1] is None:
                continue
            if r[i - 1] <= 30 < r[i]:
                orders[i].append(Order(1, "market"))
            if r[i - 1] >= 70 > r[i]:
                orders[i].append(Order(-1, "market"))
    elif name == "STOCHASTIC_SLOW":
        k, d = scan.stochastic(h, l, c, 14, 3, 3)
        for i in range(1, n):
            if crossover(k, d, i) and k[i] < 20:
                orders[i].append(Order(1, "market"))
            if crossunder(k, d, i) and k[i] > 80:
                orders[i].append(Order(-1, "market"))
    elif name == "SUPERTREND":
        tr = P.supertrend_kivanc(h, l, c, 10, 3.0)
        for i in range(1, n):
            if tr[i] == 1 and tr[i - 1] == -1:
                orders[i].append(Order(1, "market"))
            if tr[i] == -1 and tr[i - 1] == 1:
                orders[i].append(Order(-1, "market"))
    elif name == "VOLATILITY_EXPANSION_CLOSE":
        tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
        a = scan.sma(tr, 5)
        for i in range(5, n):
            orders[i].append(Order(1, "stop", c[i] + a[i] * 0.75))
            orders[i].append(Order(-1, "stop", c[i] - a[i] * 0.75))
    elif name == "TECHNICAL_RATINGS":
        import ta_lib
        r = ta_lib.technical_rating(o, h, l, c, E.v)
        for i in range(n):
            if r[i] is not None and r[i] > 0.5:
                orders[i].append(Order(1, "market"))
            if r[i] is not None and r[i] < -0.5:
                orders[i].append(Order(-1, "market"))
    elif name.startswith("CA_"):
        chartart_orders(name, E, orders)
    elif name == "ADX_BREAKOUT_ROB_BOOKER":
        return orders          # needs the position; handled inside the simulator
    else:
        raise ValueError(name)
    return orders


def chartart_orders(name, E, orders):
    """ChartArt's most-liked double strategies (PUB;2187, 2004, 2811, 2304, 1897), replayed from source at defaults."""
    import ta_lib as T
    o, h, l, c = E.o, E.h, E.l, E.c
    n = len(c)
    if name == "CA_BOLLINGER_RSI":
        vrsi = S.rsi(c, 6)
        basis, dev = T.sma(c, 200), T.stdev(c, 200)
        up = [None if a is None or b is None else a + 2 * b for a, b in zip(basis, dev)]
        lo = [None if a is None or b is None else a - 2 * b for a, b in zip(basis, dev)]
        fifty = [50.0] * n
        for i in range(1, n):
            if crossover(vrsi, fifty, i) and crossover(c, lo, i):
                orders[i].append(Order(1, "stop", lo[i]))
            if crossunder(vrsi, fifty, i) and crossunder(c, up, i):
                orders[i].append(Order(-1, "stop", up[i]))
    elif name == "CA_MACD_SMA200":
        fast, slow, vslow = T.sma(c, 12), T.sma(c, 26), T.sma(c, 200)
        macd = T.sub(fast, slow)
        hist = T.sub(macd, T.sma(macd, 9))
        zero = [0.0] * n
        pend_l = pend_s = None
        for i in range(26, n):
            if None in (slow[i], vslow[i], hist[i], hist[i - 1]):
                continue
            if slow[i] < vslow[i]:
                pend_l = None
            if crossover(hist, zero, i) and macd[i] > 0 and fast[i] > slow[i] and vslow[i] is not None and c[i - 26] > vslow[i]:
                pend_l = l[i]
            if slow[i] > vslow[i]:
                pend_s = None
            if crossunder(hist, zero, i) and macd[i] < 0 and fast[i] < slow[i] and c[i - 26] < vslow[i]:
                pend_s = h[i]
            # a buy stop at the low (below price) fills at the next open, then the order is consumed
            if pend_l is not None:
                orders[i].append(Order(1, "stop", pend_l))
                pend_l = None
            if pend_s is not None:
                orders[i].append(Order(-1, "stop", pend_s))
                pend_s = None
    elif name == "CA_GOLDEN_CROSS_SMA200":
        f, sl_ = T.sma(c, 50), T.sma(c, 200)
        for i in range(1, n):
            if crossover(f, sl_, i):
                orders[i].append(Order(1, "market"))
            if crossunder(f, sl_, i):
                orders[i].append(Order(0, "exit"))
    elif name == "CA_MACD_STOCHASTIC":
        macd = T.sub(T.ema(c, 12), T.ema(c, 26))
        delta = T.sub(macd, T.ema(macd, 9))
        k = T.sma(T.stoch(c, h, l, 14), 3)
        d = T.sma(k, 2)
        zero = [0.0] * n
        for i in range(1, n):
            if k[i] is None or d[i] is None:
                continue
            if crossover(k, d, i) and k[i] < 29 and crossover(delta, zero, i):
                orders[i].append(Order(1, "market"))
            if crossunder(k, d, i) and k[i] > 71 and crossunder(delta, zero, i):
                orders[i].append(Order(-1, "market"))
    elif name == "CA_STOCHASTIC_RSI":
        k = T.sma(T.stoch(c, h, l, 14), 3)
        d = T.sma(k, 3)
        vrsi = S.rsi(c, 14)
        lo30, hi70 = [30.0] * n, [70.0] * n
        for i in range(1, n):
            if k[i] is None or d[i] is None:
                continue
            if crossover(k, d, i) and k[i] < 20 and crossover(vrsi, lo30, i):
                orders[i].append(Order(1, "market"))
            if crossunder(k, d, i) and k[i] > 80 and crossunder(vrsi, hi70, i):
                orders[i].append(Order(-1, "market"))
    else:
        raise ValueError(name)


CHARTART = ("CA_BOLLINGER_RSI", "CA_MACD_SMA200", "CA_GOLDEN_CROSS_SMA200", "CA_MACD_STOCHASTIC", "CA_STOCHASTIC_RSI")

NAMES = ("BAR_UP_DOWN", "BOLLINGER_BANDS", "CHANNEL_BREAKOUT", "CONSECUTIVE_UP_DOWN", "INSIDE_BAR", "KELTNER_CHANNELS",
         "MACD", "MOMENTUM", "MA_CROSSOVER", "OUTSIDE_BAR", "PARABOLIC_SAR", "PIVOT_EXTENSION", "PIVOT_REVERSAL",
         "PRICE_CHANNEL", "RSI", "STOCHASTIC_SLOW", "SUPERTREND", "TWO_MA_CROSSOVER", "VOLATILITY_EXPANSION_CLOSE",
         "ADX_BREAKOUT_ROB_BOOKER", "TECHNICAL_RATINGS")


def rob_booker_adx(E):
    """ADX(14,14) via Pine's dirmov/rma formulas; returns adx series."""
    h, l, c = E.h, E.l, E.c
    n = len(c)
    up = [0.0] + [h[i] - h[i - 1] for i in range(1, n)]
    dn = [0.0] + [l[i - 1] - l[i] for i in range(1, n)]
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    pdm = [u if u > d and u > 0 else 0.0 for u, d in zip(up, dn)]
    mdm = [d if d > u and d > 0 else 0.0 for u, d in zip(up, dn)]

    def rma(x, k):
        out = [None] * len(x)
        s = sum(x[:k]) / k
        out[k - 1] = s
        for i in range(k, len(x)):
            s = (s * (k - 1) + x[i]) / k
            out[i] = s
        return out
    t, p, m = rma(tr, 14), rma(pdm, 14), rma(mdm, 14)
    plus = [None if a is None or a == 0 else 100 * b / a for a, b in zip(t, p)]
    minus = [None if a is None or a == 0 else 100 * b / a for a, b in zip(t, m)]
    ratio = [0.0 if a is None or b is None else abs(a - b) / ((a + b) if a + b != 0 else 1) for a, b in zip(plus, minus)]
    return [None if v is None else 100 * v for v in rma(ratio, 14)]


class BuiltinAsset(P.OriginalAsset):
    def simulate_strategy(self, name):
        """Replay the strategy over the whole data set. Returns a list of completed trades (oil.Trade)."""
        E, q = self.e, self.q
        n = len(E.t)
        orders = strategy_orders(name, E, self.atr)
        adx = rob_booker_adx(E) if name == "ADX_BREAKOUT_ROB_BOOKER" else None
        pos, entry, entry_t, entry_i = 0, None, None, None
        tp = sl = None
        tr_mode = name == "TECHNICAL_RATINGS"
        trail_on, best, atr_e = False, None, None
        box_u = box_l = None
        trades = []

        def close_trade(px, t_exit, reason="reverse"):
            a = self.atr[entry_i]
            if a is not None and a > 0:
                trades.append(oil.Trade(entry_i, entry_t, t_exit, pos, entry, 2 * a, (px - entry) * pos / (2 * a), reason, self.regime(entry_t)))

        for i in range(n - 1):
            act = list(orders[i])
            if adx is not None:
                if pos == 0 and i >= 21:
                    box_u, box_l = highest(E.h, 20, i - 1), lowest(E.l, 20, i - 1)
                if pos == 0 and box_u is not None and adx[i] is not None and adx[i] < 18:
                    cross_u = (E.c[i] - box_u) * (E.c[i - 1] - box_u) < 0
                    cross_l = (E.c[i] - box_l) * (E.c[i - 1] - box_l) < 0
                    if cross_u:
                        act.append(Order(1, "market"))
                    elif cross_l:
                        act.append(Order(-1, "market"))
            t_next = E.t[i + 1]
            bars = [self.p_idx.get(t_next + k * 900) for k in range(4)]
            bars = [j for j in bars if j is not None]
            if not bars:
                continue
            filled = False
            for j in bars:
                # Technical ratings: strategy.exit(loss = 3 ATR, trail_points = 5 ATR, trail_offset = 2 ATR)
                if tr_mode and pos != 0 and atr_e:
                    fav = q["bh"][j] if pos > 0 else q["al"][j]
                    adv = q["bl"][j] if pos > 0 else q["ah"][j]
                    stop_px = entry - pos * 3 * atr_e
                    if trail_on:
                        stop_px = best - pos * 2 * atr_e if (best - pos * 2 * atr_e - stop_px) * pos > 0 else stop_px
                    if (adv - stop_px) * pos <= 0:
                        close_trade(stop_px, q["t"][j] + 900, "trail" if trail_on else "stop")
                        pos, trail_on = 0, False
                        continue
                    best = fav if best is None or (fav - best) * pos > 0 else best
                    if (best - entry) * pos >= 5 * atr_e:
                        trail_on = True
                # protective exits (ADX breakout only)
                if pos != 0 and tp is not None:
                    hit_sl = (q["bl"][j] <= sl) if pos > 0 else (q["ah"][j] >= sl)
                    hit_tp = (q["bh"][j] >= tp) if pos > 0 else (q["al"][j] <= tp)
                    if hit_sl or hit_tp:
                        px = sl if hit_sl else tp
                        close_trade(px, q["t"][j] + 900, "stop" if hit_sl else "target")
                        pos, tp, sl = 0, None, None
                        continue
                if filled:
                    continue
                if pos != 0 and j == bars[0] and any(od.kind == "exit" for od in act):
                    close_trade(q["bo"][j] if pos > 0 else q["ao"][j], q["t"][j], "exit")
                    pos, filled = 0, True
                    continue
                cands = []
                for od in act:
                    if od.kind == "exit" or od.d == pos:
                        continue
                    if od.kind == "market" and j == bars[0]:
                        cands.append((0.0, od, q["ao"][j] if od.d > 0 else q["bo"][j]))
                    elif od.kind == "stop":
                        if od.d > 0 and q["bh"][j] >= od.price:
                            fill = max(q["bo"][j], od.price) + (q["ao"][j] - q["bo"][j])
                            cands.append((abs(od.price - q["bo"][j]), od, fill))
                        elif od.d < 0 and q["bl"][j] <= od.price:
                            cands.append((abs(od.price - q["bo"][j]), od, min(q["bo"][j], od.price)))
                if not cands:
                    continue
                _, od, px = min(cands, key=lambda x: x[0])
                t_fill = q["t"][j]
                if pos != 0:
                    close_trade(px, t_fill)                              # the reversing order closes at the same fill
                pos, entry, entry_t, entry_i, filled = od.d, px, t_fill, i, True
                atr_e, best, trail_on = self.atr[i], px, False
                if adx is not None:
                    w = box_u - box_l
                    tp, sl = (entry + w, entry - 0.5 * w) if pos > 0 else (entry - w, entry + 0.5 * w)
        return trades
