"""Indicator functions with TradingView's built-in definitions (pure Python, causal; None during warm-up)."""
import math

import ports as P  # noqa: F401  (sets up shared paths)
import scan
import study as S
import community as C1


def sub(a, b):
    return [None if x is None or y is None else x - y for x, y in zip(a, b)]


def shift(x, k):
    return [None] * k + x[:-k] if k else x


def rma(x, n):
    first = next((i for i, v in enumerate(x) if v is not None), None)
    out = [None] * len(x)
    if first is None or len(x) - first < n:
        return out
    s = sum(x[first:first + n]) / n
    out[first + n - 1] = s
    for i in range(first + n, len(x)):
        s = (s * (n - 1) + x[i]) / n
        out[i] = s
    return out


def sma(x, n):
    return C1.sma_sparse(x, n)


def ema(x, n):
    return C1.ema_sparse(x, n)


def wma(x, n):
    out, den = [None] * len(x), n * (n + 1) / 2
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if None not in w:
            out[i] = sum(v * (k + 1) for k, v in enumerate(w)) / den
    return out


def hma(x, n):
    half, full = wma(x, n // 2), wma(x, n)
    return wma([None if a is None or b is None else 2 * a - b for a, b in zip(half, full)], int(math.floor(math.sqrt(n))))


def vwma(c, v, n):
    pv = sma([a * b for a, b in zip(c, v)], n)
    vv = sma(v, n)
    return [None if a is None or b in (None, 0) else a / b for a, b in zip(pv, vv)]


def stdev(x, n):
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if None in w:
            continue
        m = sum(w) / n
        out[i] = math.sqrt(sum((v - m) ** 2 for v in w) / n)
    return out


def highest(x, n):
    return [max(x[i - n + 1:i + 1]) if i >= n - 1 else None for i in range(len(x))]


def lowest(x, n):
    return [min(x[i - n + 1:i + 1]) if i >= n - 1 else None for i in range(len(x))]


def stoch(c, h, l, n):
    hh, ll = highest(h, n), lowest(l, n)
    return [None if a is None else (50.0 if a == b else 100 * (x - b) / (a - b)) for x, a, b in zip(c, hh, ll)]


def stoch_full(h, l, c, n=14, sk=3, sd=3):
    k = sma(stoch(c, h, l, n), sk)
    return k, sma(k, sd)


def stoch_rsi(c, rsi_len=14, st_len=14, sk=3, sd=3):
    r = S.rsi(c, rsi_len)
    hh = [None if i < st_len - 1 or None in r[i - st_len + 1:i + 1] else max(r[i - st_len + 1:i + 1]) for i in range(len(r))]
    ll = [None if i < st_len - 1 or None in r[i - st_len + 1:i + 1] else min(r[i - st_len + 1:i + 1]) for i in range(len(r))]
    raw = [None if a is None or x is None else (50.0 if a == b else 100 * (x - b) / (a - b)) for x, a, b in zip(r, hh, ll)]
    k = sma(raw, sk)
    return k, sma(k, sd)


def dmi(h, l, c, di_len=14, adx_len=14):
    n = len(c)
    up = [None] + [h[i] - h[i - 1] for i in range(1, n)]
    dn = [None] + [l[i - 1] - l[i] for i in range(1, n)]
    pdm = [None if u is None else (u if u > d and u > 0 else 0.0) for u, d in zip(up, dn)]
    mdm = [None if u is None else (d if d > u and d > 0 else 0.0) for u, d in zip(up, dn)]
    tr = [None] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    t, p, m = rma(tr, di_len), rma(pdm, di_len), rma(mdm, di_len)
    plus = [None if a in (None, 0) else 100 * b / a for a, b in zip(t, p)]
    minus = [None if a in (None, 0) else 100 * b / a for a, b in zip(t, m)]
    dx = [None if a is None or b is None else abs(a - b) / ((a + b) if a + b != 0 else 1) for a, b in zip(plus, minus)]
    adx = [None if v is None else 100 * v for v in rma(dx, adx_len)]
    return plus, minus, adx


def cci(src, n):
    out = [None] * len(src)
    for i in range(n - 1, len(src)):
        w = src[i - n + 1:i + 1]
        m = sum(w) / n
        md = sum(abs(v - m) for v in w) / n
        out[i] = 0.0 if md == 0 else (src[i] - m) / (0.015 * md)
    return out


def uo(h, l, c, a=7, b=14, d=28):
    n = len(c)
    bp = [None] + [c[i] - min(l[i], c[i - 1]) for i in range(1, n)]
    tr = [None] + [max(h[i], c[i - 1]) - min(l[i], c[i - 1]) for i in range(1, n)]

    def avg(k):
        sb, st = sma(bp, k), sma(tr, k)
        return [None if x is None or y in (None, 0) else x / y for x, y in zip(sb, st)]
    a1, a2, a3 = avg(a), avg(b), avg(d)
    return [None if None in (x, y, z) else 100 * (4 * x + 2 * y + z) / 7 for x, y, z in zip(a1, a2, a3)]


def wpr(h, l, c, n=14):
    hh, ll = highest(h, n), lowest(l, n)
    return [None if a is None or a == b else 100 * (x - a) / (a - b) for x, a, b in zip(c, hh, ll)]


def ao(h, l):
    hl2 = [(a + b) / 2 for a, b in zip(h, l)]
    return sub(sma(hl2, 5), sma(hl2, 34))


def ichimoku(h, l, conv=9, base=26, span_b=52):
    def mid(n):
        return [None if x is None else (x + y) / 2 for x, y in zip(highest(h, n), lowest(l, n))]
    con, bas = mid(conv), mid(base)
    lead1 = [None if a is None or b is None else (a + b) / 2 for a, b in zip(con, bas)]
    return con, bas, lead1, mid(span_b)


def technical_rating(o, h, l, c, v):
    """TradingView TechnicalRating.calcRatingAll(): returns the total rating per bar."""
    n = len(c)
    con, base, lead1, lead2 = ichimoku(h, l)
    k_st, d_st = stoch_full(h, l, c, 14, 3, 3)
    k_sr, d_sr = stoch_rsi(c, 14, 14, 3, 3)
    dip, din, adx = dmi(h, l, c, 14, 14)
    e12, e26 = ema(c, 12), ema(c, 26)
    macd = sub(e12, e26)
    sig = ema(macd, 9)
    e13 = ema(c, 13)
    bull = [None if e is None else x - e for x, e in zip(h, e13)]
    bear = [None if e is None else x - e for x, e in zip(l, e13)]
    rsi = S.rsi(c, 14)
    cc = cci(c, 20)
    mom = [None] * 10 + [c[i] - c[i - 10] for i in range(10, n)]
    pavg = ema(c, 50)
    u = uo(h, l, c)
    wr = wpr(h, l, c, 14)
    a = ao(h, l)
    mas = [sma(c, k) for k in (10, 20, 30, 50, 100, 200)] + [ema(c, k) for k in (10, 20, 30, 50, 100, 200)] + [hma(c, 9), vwma(c, v, 20)]
    l1_26, l2_26 = shift(lead1, 26), shift(lead2, 26)
    total = [None] * n
    for i in range(2, n):
        r_ma = [math.copysign(1, c[i] - m[i]) if (m[i] is not None and c[i] != m[i]) else (0.0 if m[i] is not None else None) for m in mas]
        if None not in (lead2[i], l1_26[i], l2_26[i], base[i], con[i]):
            b_ = l1_26[i] > l2_26[i] and base[i] > l1_26[i] and con[i] > base[i] and c[i] > con[i]
            s_ = l1_26[i] < l2_26[i] and base[i] < l1_26[i] and con[i] < base[i] and c[i] < con[i]
            r_ma.append(1 if b_ else -1 if s_ else 0)
        else:
            r_ma.append(None)
        ok = [x for x in r_ma if x is not None]
        rating_ma = sum(ok) / len(ok) if ok else None

        def rate(src_ok, bull_c, bear_c):
            return None if not src_ok else (1 if bull_c else -1 if bear_c else 0)
        g = lambda s, k=0: s[i - k] is not None  # noqa: E731
        osc = [
            rate(g(rsi, 1) and g(rsi), g(rsi) and g(rsi, 1) and rsi[i] < 30 and rsi[i - 1] < rsi[i], g(rsi) and g(rsi, 1) and rsi[i] > 70 and rsi[i - 1] > rsi[i]),
            rate(g(d_st, 1) and g(k_st) and g(d_st), g(k_st) and g(d_st) and k_st[i] < 20 and d_st[i] < 20 and k_st[i] > d_st[i],
                 g(k_st) and g(d_st) and k_st[i] > 80 and d_st[i] > 80 and k_st[i] < d_st[i]),
            rate(g(cc, 1) and g(cc), g(cc) and g(cc, 1) and cc[i] < -100 and cc[i] > cc[i - 1], g(cc) and g(cc, 1) and cc[i] > 100 and cc[i] < cc[i - 1]),
            rate(g(adx) and g(adx, 1) and g(dip) and g(din), adx[i] is not None and adx[i - 1] is not None and adx[i] > 20 and adx[i] > adx[i - 1] and dip[i] > din[i],
                 adx[i] is not None and adx[i - 1] is not None and adx[i] > 20 and adx[i] > adx[i - 1] and dip[i] < din[i]),
            rate(g(a, 1) and g(a, 2) and g(a),
                 g(a) and g(a, 1) and g(a, 2) and ((a[i] > 0 >= a[i - 1]) or (a[i] > 0 and a[i - 1] > 0 and a[i] > a[i - 1] and a[i - 2] > a[i - 1])),
                 g(a) and g(a, 1) and g(a, 2) and ((a[i] < 0 <= a[i - 1]) or (a[i] < 0 and a[i - 1] < 0 and a[i] < a[i - 1] and a[i - 2] < a[i - 1]))),
            rate(g(mom, 1) and g(mom), g(mom) and g(mom, 1) and mom[i] > mom[i - 1], g(mom) and g(mom, 1) and mom[i] < mom[i - 1]),
            rate(g(sig) and g(macd), g(sig) and macd[i] > sig[i], g(sig) and macd[i] < sig[i]),
            rate(g(pavg) and g(k_sr) and g(d_sr), g(pavg) and g(k_sr) and g(d_sr) and c[i] < pavg[i] and k_sr[i] < 20 and d_sr[i] < 20 and k_sr[i] > d_sr[i],
                 g(pavg) and g(k_sr) and g(d_sr) and c[i] > pavg[i] and k_sr[i] > 80 and d_sr[i] > 80 and k_sr[i] < d_sr[i]),
            rate(g(wr, 1) and g(wr), g(wr) and g(wr, 1) and wr[i] < -80 and wr[i] > wr[i - 1], g(wr) and g(wr, 1) and wr[i] > -20 and wr[i] < wr[i - 1]),
            rate(g(pavg) and g(bear, 1) and g(bull, 1), g(pavg) and g(bear, 1) and g(bear) and c[i] > pavg[i] and bear[i] < 0 and bear[i] > bear[i - 1],
                 g(pavg) and g(bull, 1) and g(bull) and c[i] < pavg[i] and bull[i] > 0 and bull[i] < bull[i - 1]),
            rate(g(u), g(u) and u[i] > 70, g(u) and u[i] < 30),
        ]
        ok = [x for x in osc if x is not None]
        rating_osc = sum(ok) / len(ok) if ok else None
        if rating_ma is not None and rating_osc is not None:
            total[i] = (rating_ma + rating_osc) / 2
        elif rating_ma is not None or rating_osc is not None:
            total[i] = rating_ma if rating_ma is not None else rating_osc
    return total
