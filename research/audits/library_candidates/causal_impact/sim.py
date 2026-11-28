"""Independent causal limit-order simulator for the library candidates (B9 Fibonacci, D4 FVG).

Written from FORWARD_RULES.md and a reading of forward.py's state machine, NOT copied from forward.py, verify_minute.py or
the earlier audit script. Two clock modes:
  wall   : the forward test exactly - orders expire 10 wall-clock hours after creation, time exit at the last minute before
           fill-hour + 21 h, next signal check at exit-hour + 2 h, signals only at a minute that starts an hour and only when
           the 1h candle that just closed is present.
  candle : the frozen backtest's candle counting (verify_minute.py) - orders live for the next 10 hourly candles that exist in
           the data, time exit at the close of the 20th candle after the fill candle, next signal at the close of the candle
           after the exit candle. ONLY the order selection differs from the frozen backtest.
Order selection (both modes): every signal adds a pending order; several may be pending; at each minute the pending orders are
checked oldest first and the first one whose fill condition holds is taken; all others are cancelled; no signal while a
position is open. Every decision at minute q uses data of minutes <= q and hourly candles closed by q only.
"""
import numpy as np

H = 60  # minutes per hour


def hourly(m, o, h, l, c):
    hr = m // H; st = np.flatnonzero(np.r_[True, hr[1:] != hr[:-1]]); en = np.r_[st[1:], len(m)]
    return dict(hr=hr[st], s=st, e=en, o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1])


def sig_fib(Hc, k, fib=0.618, look=20, need=50):
    """B9 on closed hourly candles 0..k (k = the candle that just closed)."""
    if k + 1 < need: return None
    c = Hc["c"]; s50 = c[k - 49:k + 1].mean(); hh = Hc["h"][k - look + 1:k + 1]; ll = Hc["l"][k - look + 1:k + 1]
    ih, il = int(np.argmax(hh)), int(np.argmin(ll)); Hh, Ll = hh[ih], ll[il]
    if Hh <= Ll: return None
    if c[k] > s50 and ih > il: return 1, Hh - fib * (Hh - Ll), Ll, Hh
    if c[k] < s50 and il > ih: return -1, Ll + fib * (Hh - Ll), Hh, Ll
    return None


def sig_fvg(Hc, k):
    if k < 2: return None
    h2, l2, hi, li = Hc["h"][k - 2], Hc["l"][k - 2], Hc["h"][k], Hc["l"][k]
    if li > h2 and h2 > l2: return 1, h2, l2, h2 + 2 * (h2 - l2)
    if hi < l2 and h2 > l2: return -1, l2, h2, l2 - 2 * (h2 - l2)
    return None


def simulate(m, o, h, l, c, kind, pen, clock="wall", life=10, tmax=20, fib_need=50, log=None, sigfun=None, policy="multi"):
    """policy: multi (forward.py) | single (ignore signals while an order is pending) | replace (a new signal cancels pending orders)"""
    """pen(lim_or_tp, q) -> penetration required at minute q. Returns trades as dicts with minute indices (f, x)."""
    Hc = hourly(m, o, h, l, c); nH = len(Hc["s"]); sig = (lambda k: sig_fvg(Hc, k)) if kind == "fvg" else (lambda k: sig_fib(Hc, k, need=fib_need))
    if sigfun is not None: sig = lambda k: sigfun(Hc, k)
    hour_of = np.repeat(np.arange(nH), Hc["e"] - Hc["s"])          # candle index of each minute
    pending, pos, trades = [], None, []
    next_ok = -10 ** 18                                            # wall: minute; candle: candle index
    for q in range(len(m)):
        t = int(m[q]); kq = int(hour_of[q])
        # 1) signal at an hour boundary (wall) / at the first minute of a candle (candle), using the candle that just closed
        if pos is None:
            if clock == "wall":
                if t % H == 0 and t >= next_ok and kq >= 1 and Hc["hr"][kq - 1] * H + H == t:
                    k = kq - 1; s = sig(k)
                    if s and policy == "single" and [p for p in pending if t < p["exp"]]: s = None
                    if s and policy == "replace": pending = []
                    if s: pending.append(dict(side=s[0], lim=s[1], stop=s[2], tp=s[3], made=t, exp=t + life * H, sig_k=k))
                    if log is not None and s: log.append(("create", t, k, s[0], s[1]))
            else:
                if q == Hc["s"][kq] and kq >= 1 and kq - 1 >= next_ok:
                    k = kq - 1; s = sig(k)
                    if s and policy == "single" and [p for p in pending if kq < p["exp"]]: s = None
                    if s and policy == "replace": pending = []
                    if s: pending.append(dict(side=s[0], lim=s[1], stop=s[2], tp=s[3], made=t, exp=k + 1 + life, sig_k=k))
                    if log is not None and s: log.append(("create", t, k, s[0], s[1]))
        # 2) fills: purge expired, then oldest first
        if pos is None and pending:
            alive = [p for p in pending if (t < p["exp"] if clock == "wall" else kq < p["exp"])]
            if log is not None:
                for p in pending:
                    if p not in alive: log.append(("expire", t, p["sig_k"]))
            pending = alive
            for p in pending:
                if (p["side"] > 0 and l[q] <= p["lim"] - pen(p["lim"], q)) or (p["side"] < 0 and h[q] >= p["lim"] + pen(p["lim"], q)):
                    e = min(o[q], p["lim"]) if p["side"] > 0 else max(o[q], p["lim"])
                    dl = (t // H * H + (tmax + 1) * H) if clock == "wall" else min(kq + tmax, nH - 1)
                    pos = dict(p, entry=float(e), f=q, ft=t, deadline=dl)
                    if log is not None: log.append(("fill", t, p["sig_k"], len(pending) - 1))
                    pending = []
                    break
        # 3) position management (stop first, then target from the minute after the fill, then time)
        if pos is not None:
            sd = pos["side"]; ex = None
            if q > pos["f"] and ((sd > 0 and o[q] <= pos["stop"]) or (sd < 0 and o[q] >= pos["stop"])): ex = (o[q], "stop_gap")
            elif (sd > 0 and l[q] <= pos["stop"]) or (sd < 0 and h[q] >= pos["stop"]): ex = (pos["stop"], "stop")
            elif q > pos["f"] and ((sd > 0 and h[q] >= pos["tp"] + pen(pos["tp"], q)) or (sd < 0 and l[q] <= pos["tp"] - pen(pos["tp"], q))): ex = (pos["tp"], "target")
            elif clock == "wall" and t + 1 >= pos["deadline"]: ex = (c[q], "time")
            elif clock == "candle" and (kq > pos["deadline"] or (kq == pos["deadline"] and q == Hc["e"][kq] - 1)): ex = (c[q], "time")
            if ex:
                trades.append(dict(side=sd, sig_k=pos["sig_k"], made=pos["made"], f=pos["f"], x=q, ft=pos["ft"], xt=t, lim=pos["lim"], stop=pos["stop"], tp=pos["tp"],
                                   entry=pos["entry"], exit=float(ex[0]), reason=ex[1]))
                if log is not None: log.append(("exit", t, pos["sig_k"], ex[1]))
                next_ok = (t // H * H + 2 * H) if clock == "wall" else kq + 1
                pos = None
    return trades, Hc


def manage_from(m, o, h, l, c, Hc, hour_of, f, side, entry, stop, tp, pen, tmax=20):
    """Candle-clock management from fill minute f (same rules as simulate's step 3). Returns (x, exit_px, reason)."""
    kf = int(hour_of[f]); last = min(kf + tmax, len(Hc["s"]) - 1); end = Hc["e"][last]
    for q in range(f, end):
        if q > f and ((side > 0 and o[q] <= stop) or (side < 0 and o[q] >= stop)): return q, o[q], "stop_gap"
        if (side > 0 and l[q] <= stop) or (side < 0 and h[q] >= stop): return q, stop, "stop"
        if q > f and ((side > 0 and h[q] >= tp + pen(tp, q)) or (side < 0 and l[q] <= tp - pen(tp, q))): return q, tp, "target"
    return end - 1, c[end - 1], "time"


def simulate_lookahead(m, o, h, l, c, kind, pen, life=10, tmax=20, fib_need=51):
    """The FROZEN backtest's selection, re-expressed: at each signal, scan its whole 10-candle window; if it never fills,
    move to the next candle's signal. Uses future data by construction. Used only to show that this selection rule is
    the sole difference between the frozen backtest and the causal simulator."""
    Hc = hourly(m, o, h, l, c); nH = len(Hc["s"]); hour_of = np.repeat(np.arange(nH), Hc["e"] - Hc["s"])
    sig = (lambda k: sig_fvg(Hc, k)) if kind == "fvg" else (lambda k: sig_fib(Hc, k, need=fib_need))
    out = []; k = 2 if kind == "fvg" else fib_need - 1
    while k < nH - (1 if kind == "fvg" else 2):
        s = sig(k)
        if not s: k += 1; continue
        side, lim, stop, tp = s; a = Hc["s"][k + 1] if k + 1 < nH else len(m); b = Hc["e"][min(k + life, nH - 1)]; f = None
        for q in range(a, b):
            if (side > 0 and l[q] <= lim - pen(lim, q)) or (side < 0 and h[q] >= lim + pen(lim, q)): f = q; break
        if f is None: k += 1; continue
        e = min(o[f], lim) if side > 0 else max(o[f], lim); x, px, why = manage_from(m, o, h, l, c, Hc, hour_of, f, side, e, stop, tp, pen, tmax)
        out.append(dict(side=side, sig_k=k, f=f, x=x, entry=float(e), exit=float(px), reason=why)); k = int(hour_of[x]) + 1
    return out, Hc
