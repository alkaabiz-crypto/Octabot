"""Standard BUY/SELL signals for every directional TradingView built-in indicator (PROTOCOL.md, part B).

Defaults come from each built-in's Pine source. Each function returns (buy, sell) boolean lists on 1H bid candles;
every value at bar i uses bars 0..i only.
"""
import math

import ports as P  # noqa: F401  (paths)
import scan
import study as S
import ta_lib as T


def up_cross(a, b, i):
    return i >= 1 and None not in (a[i], a[i - 1], b[i], b[i - 1]) and a[i - 1] <= b[i - 1] and a[i] > b[i]


def dn_cross(a, b, i):
    return i >= 1 and None not in (a[i], a[i - 1], b[i], b[i - 1]) and a[i - 1] >= b[i - 1] and a[i] < b[i]


def const(n, v):
    return [v] * n


def cross_pair(a, b):
    n = len(a)
    return [up_cross(a, b, i) for i in range(n)], [dn_cross(a, b, i) for i in range(n)]


def levels(x, lo, hi):
    """Oversold/overbought: BUY when x crosses up through lo, SELL when it crosses down through hi."""
    n = len(x)
    return [up_cross(x, const(n, lo), i) for i in range(n)], [dn_cross(x, const(n, hi), i) for i in range(n)]


def zero(x):
    return cross_pair(x, const(len(x), 0.0))


def first_true(flags):
    return [bool(flags[i]) and (i == 0 or not flags[i - 1]) for i in range(len(flags))]


def dema(x, n):
    e = T.ema(x, n)
    return [None if a is None or b is None else 2 * a - b for a, b in zip(e, T.ema(e, n))]


def tema(x, n):
    e1 = T.ema(x, n)
    e2 = T.ema(e1, n)
    e3 = T.ema(e2, n)
    return [None if None in (a, b, c) else 3 * a - 3 * b + c for a, b, c in zip(e1, e2, e3)]


def alma(x, n=9, offset=0.85, sigma=6):
    m, s = offset * (n - 1), n / sigma
    w = [math.exp(-((k - m) ** 2) / (2 * s * s)) for k in range(n)]
    out = [None] * len(x)
    for i in range(n - 1, len(x)):
        win = x[i - n + 1:i + 1]
        out[i] = sum(win[k] * w[k] for k in range(n)) / sum(w)
    return out


def kama(x, er_len=10, fast=2, slow=30):
    out = [None] * len(x)
    fs, ss = 2 / (fast + 1), 2 / (slow + 1)
    prev = None
    for i in range(er_len, len(x)):
        change = abs(x[i] - x[i - er_len])
        vol = sum(abs(x[k] - x[k - 1]) for k in range(i - er_len + 1, i + 1))
        er = change / vol if vol else 0.0
        sc = (er * (fs - ss) + ss) ** 2
        prev = x[i] if prev is None else prev + sc * (x[i] - prev)
        out[i] = prev
    return out


def linreg(x, n):
    out = [None] * len(x)
    xm = (n - 1) / 2
    sxx = sum((k - xm) ** 2 for k in range(n))
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        ym = sum(w) / n
        slope = sum((k - xm) * (v - ym) for k, v in enumerate(w)) / sxx
        out[i] = ym + slope * (n - 1 - xm)
    return out


def mcginley(x, n=14):
    out, prev = [None] * len(x), None
    e = T.ema(x, n)
    for i in range(len(x)):
        if prev is None:
            if e[i] is not None:
                prev = e[i]
                out[i] = prev
            continue
        prev = prev + (x[i] - prev) / (n * (x[i] / prev) ** 4)
        out[i] = prev
    return out


def ma_cross(c, ma):
    return cross_pair(c, ma)


def signals(E):
    o, h, l, c, v = E.o, E.h, E.l, E.c, E.v
    n = len(c)
    hl2 = [(a + b) / 2 for a, b in zip(h, l)]
    hlc3 = [(a + b + d) / 3 for a, b, d in zip(h, l, c)]
    out = {}
    # moving averages: close crosses the MA
    out["SMA_9"] = ma_cross(c, T.sma(c, 9))
    out["EMA_9"] = ma_cross(c, T.ema(c, 9))
    out["WMA_9"] = ma_cross(c, T.wma(c, 9))
    out["DEMA_9"] = ma_cross(c, dema(c, 9))
    out["TEMA_9"] = ma_cross(c, tema(c, 9))
    out["HMA_9"] = ma_cross(c, T.hma(c, 9))
    out["ALMA_9"] = ma_cross(c, alma(c))
    out["KAMA_10_2_30"] = ma_cross(c, kama(c))
    out["LSMA_25"] = ma_cross(c, linreg(c, 25))
    out["MCGINLEY_14"] = ma_cross(c, mcginley(c))
    out["SMMA_7"] = ma_cross(c, T.rma(c, 7))
    out["VWMA_20"] = ma_cross(c, T.vwma(c, v, 20))
    s20, s50, s100, s200 = T.sma(c, 20), T.sma(c, 50), T.sma(c, 100), T.sma(c, 200)
    bull = [None not in (a, b, d, e) and a > b > d > e for a, b, d, e in zip(s20, s50, s100, s200)]
    bear = [None not in (a, b, d, e) and a < b < d < e for a, b, d, e in zip(s20, s50, s100, s200)]
    out["MA_RIBBON_20_50_100_200"] = (first_true(bull), first_true(bear))
    # zero-line oscillators
    out["AWESOME_OSC"] = zero(T.ao(h, l))
    ss, sl_ = T.sma(c, 20), T.sma(c, 50)
    sds, sdl = T.stdev(c, 20), T.stdev(c, 50)
    bbt = []
    for i in range(n):
        if None in (ss[i], sl_[i], sds[i], sdl[i]) or ss[i] == 0:
            bbt.append(None)
            continue
        lo_s, lo_l, up_s, up_l = ss[i] - 2 * sds[i], sl_[i] - 2 * sdl[i], ss[i] + 2 * sds[i], sl_[i] + 2 * sdl[i]
        bbt.append((abs(lo_s - lo_l) - abs(up_s - up_l)) / ss[i] * 100)
    out["BBTREND_20_50"] = zero(bbt)
    e13 = T.ema(c, 13)
    out["BULL_BEAR_POWER_13"] = zero([None if e is None else (a - e) + (b - e) for a, b, e in zip(h, l, e13)])
    mfm = [0.0 if a == b else ((x - b) - (a - x)) / (a - b) for x, a, b in zip(c, h, l)]
    mfv = [m * vv for m, vv in zip(mfm, v)]
    sv = T.sma(v, 20)
    out["CHAIKIN_MONEY_FLOW_20"] = zero([None if s_ is None or s_ == 0 else a / (s_ * 1.0) / 20 for a, s_ in zip(T.sma(mfv, 20), sv)])
    ad = []
    acc = 0.0
    for m_ in mfv:
        acc += m_
        ad.append(acc)
    out["CHAIKIN_OSC_3_10"] = zero(T.sub(T.ema(ad, 3), T.ema(ad, 10)))
    diff = [0.0] + [c[i] - c[i - 1] for i in range(1, n)]
    cmo = [None] * n
    for i in range(9, n):
        w = diff[i - 8:i + 1]
        su, sd_ = sum(x for x in w if x > 0), -sum(x for x in w if x < 0)
        cmo[i] = 0.0 if su + sd_ == 0 else 100 * (su - sd_) / (su + sd_)
    out["CHANDE_MOMENTUM_9"] = zero(cmo)
    roc = lambda k: [None] * k + [100 * (c[i] - c[i - k]) / c[i - k] for i in range(k, n)]  # noqa: E731
    r14, r11 = roc(14), roc(11)
    out["COPPOCK_10_14_11"] = zero(T.wma([None if a is None or b is None else a + b for a, b in zip(r14, r11)], 10))
    s21 = T.sma(c, 21)
    shift_ = 21 // 2 + 1
    out["DPO_21"] = zero([None if i < shift_ or s21[i - shift_] is None else c[i] - s21[i - shift_] for i in range(n)])
    eom = [None] + [None if h[i] == l[i] or v[i] == 0 else 10000 * ((hl2[i] - hl2[i - 1]) * (h[i] - l[i]) / v[i]) for i in range(1, n)]
    out["EASE_OF_MOVEMENT_14"] = zero(T.sma(eom, 14))
    out["ELDER_FORCE_13"] = zero(T.ema([None] + [(c[i] - c[i - 1]) * v[i] for i in range(1, n)], 13))
    out["PRICE_OSC_12_26"] = zero(T.sub(T.ema(c, 12), T.ema(c, 26)))
    out["ROC_9"] = zero(roc(9))
    out["MOMENTUM_10"] = zero([None] * 10 + [c[i] - c[i - 10] for i in range(10, n)])
    e1 = T.ema([math.log(x) for x in c], 18)
    e2 = T.ema(e1, 18)
    e3 = T.ema(e2, 18)
    out["TRIX_18"] = zero([None] + [None if e3[i] is None or e3[i - 1] is None else 10000 * (e3[i] - e3[i - 1]) for i in range(1, n)])
    pc = [None] + [c[i] - c[i - 1] for i in range(1, n)]
    erg = T.ema(T.ema(pc, 5), 20)
    erg_a = T.ema(T.ema([None if x is None else abs(x) for x in pc], 5), 20)
    smi_e = [None if a is None or b in (None, 0) else 100 * a / b for a, b in zip(erg, erg_a)]
    out["SMI_ERGODIC_OSC_20_5_5"] = zero(T.sub(smi_e, T.ema(smi_e, 5)))
    tsi_tr = [None] * n
    for i in range(13, n):
        w = c[i - 13:i + 1]
        xm, ym = 6.5, sum(w) / 14
        sxy = sum((k - xm) * (y - ym) for k, y in enumerate(w))
        sxx = sum((k - xm) ** 2 for k in range(14))
        syy = sum((y - ym) ** 2 for y in w)
        tsi_tr[i] = 0.0 if syy == 0 else sxy / math.sqrt(sxx * syy)
    out["TREND_STRENGTH_14"] = zero(tsi_tr)
    out["WOODIES_CCI_14"] = zero(T.cci(hlc3, 14))
    # signal-line crossings
    def sroc(k, m_):
        return T.sma(roc(k), m_)
    kst = [None if None in (a, b, d, e) else a + 2 * b + 3 * d + 4 * e for a, b, d, e in zip(sroc(10, 10), sroc(15, 10), sroc(20, 10), sroc(30, 15))]
    out["KST"] = cross_pair(kst, T.sma(kst, 9))
    trend = [0] + [1 if hlc3[i] > hlc3[i - 1] else -1 for i in range(1, n)]
    vf = [t * vv for t, vv in zip(trend, v)]
    kvo = T.sub(T.ema(vf, 34), T.ema(vf, 55))
    out["KLINGER_34_55_13"] = cross_pair(kvo, T.ema(kvo, 13))
    r1 = [None] + [100 * (c[i] / c[i - 1] - 1) for i in range(1, n)]
    pmo = T.ema([None if x is None else 10 * x for x in T.ema(r1, 35)], 20)
    out["PRICE_MOMENTUM_OSC_35_20_10"] = cross_pair(pmo, T.ema(pmo, 10))
    num = T.sum_ = None
    co = [x - y for x, y in zip(c, o)]
    hl = [x - y for x, y in zip(h, l)]
    def swma(x):
        return [None if i < 3 else (x[i] + 2 * x[i - 1] + 2 * x[i - 2] + x[i - 3]) / 6 for i in range(len(x))]
    num = T.sma(swma(co), 10)
    den = T.sma(swma(hl), 10)
    rvi = [None if a is None or b in (None, 0) else a / b for a, b in zip(num, den)]
    out["RELATIVE_VIGOR_10"] = cross_pair(rvi, swma([0.0 if x is None else x for x in rvi]))
    ds = T.ema(T.ema(pc, 25), 13)
    das = T.ema(T.ema([None if x is None else abs(x) for x in pc], 25), 13)
    tsi = [None if a is None or b in (None, 0) else 100 * a / b for a, b in zip(ds, das)]
    out["TRUE_STRENGTH_25_13_13"] = cross_pair(tsi, T.ema(tsi, 13))
    fish = [None] * n
    val = 0.0
    fprev = 0.0
    hh9, ll9 = T.highest(hl2, 9), T.lowest(hl2, 9)
    for i in range(n):
        if hh9[i] is None:
            continue
        rng = hh9[i] - ll9[i]
        val = 0.66 * ((hl2[i] - ll9[i]) / rng - 0.5) + 0.67 * val if rng else 0.67 * val
        val = max(min(val, 0.999), -0.999)
        fprev = 0.5 * math.log((1 + val) / (1 - val)) + 0.5 * fprev
        fish[i] = fprev
    out["FISHER_9"] = cross_pair(fish, [None] + fish[:-1])
    # level crossings
    up20, lo20 = scan.bollinger(c, 20, 2.0)
    pb = [None if a is None or a == b else (x - b) / (a - b) for x, a, b in zip(c, up20, lo20)]
    out["BOLLINGER_PCT_B"] = levels(pb, 0.0, 1.0)
    streak, st = [0] * n, 0
    for i in range(1, n):
        st = (st + 1 if st > 0 else 1) if c[i] > c[i - 1] else ((st - 1 if st < 0 else -1) if c[i] < c[i - 1] else 0)
        streak[i] = st
    rr = [None] * n
    for i in range(100, n):
        rr[i] = 100 * sum(1 for k in range(i - 100, i) if r1[k] is not None and r1[k] < r1[i]) / 100
    crsi = [None if a is None or b is None or d is None else (a + b + d) / 3 for a, b, d in zip(S.rsi(c, 3), S.rsi([float(x) for x in streak], 2), rr)]
    out["CONNORS_RSI_3_2_100"] = levels(crsi, 10, 90)
    tp_ = hlc3
    mf = [tp_[i] * v[i] for i in range(n)]
    mfi = [None] * n
    for i in range(14, n):
        pos = sum(mf[k] for k in range(i - 13, i + 1) if tp_[k] > tp_[k - 1])
        neg = sum(mf[k] for k in range(i - 13, i + 1) if tp_[k] < tp_[k - 1])
        mfi[i] = 100.0 if neg == 0 else 100 - 100 / (1 + pos / neg)
    out["MFI_14"] = levels(mfi, 20, 80)
    k1 = T.stoch(c, h, l, 14)
    d1 = T.sma(k1, 3)
    out["STOCHASTIC_14_1_3"] = ([up_cross(k1, d1, i) and k1[i] < 20 for i in range(n)], [dn_cross(k1, d1, i) and k1[i] > 80 for i in range(n)])
    ksr, dsr = T.stoch_rsi(c)
    out["STOCH_RSI_14_14_3_3"] = ([up_cross(ksr, dsr, i) and ksr[i] < 20 for i in range(n)], [dn_cross(ksr, dsr, i) and ksr[i] > 80 for i in range(n)])
    hh10, ll10 = T.highest(h, 10), T.lowest(l, 10)
    rel = [None if a is None else x - (a + b) / 2 for x, a, b in zip(c, hh10, ll10)]
    rng10 = [None if a is None else a - b for a, b in zip(hh10, ll10)]
    smi = [None if a is None or b in (None, 0) else 200 * a / b for a, b in zip(T.ema(T.ema(rel, 3), 3), T.ema(T.ema(rng10, 3), 3))]
    smi_sig = T.ema(smi, 3)
    out["STOCH_MOMENTUM_INDEX_10_3_3"] = ([up_cross(smi, smi_sig, i) and smi[i] < -40 for i in range(n)], [dn_cross(smi, smi_sig, i) and smi[i] > 40 for i in range(n)])
    out["ULTIMATE_OSC_7_14_28"] = levels(T.uo(h, l, c), 30, 70)
    out["WILLIAMS_PCT_R_14"] = levels(T.wpr(h, l, c, 14), -80, -20)
    rci = [None] * n
    for i in range(9, n):
        w = c[i - 9:i + 1]
        order = sorted(range(10), key=lambda k: w[k])
        prank = [0] * 10
        for r_, k in enumerate(order):
            prank[k] = r_ + 1
        dsum = sum((prank[k] - (k + 1)) ** 2 for k in range(10))
        rci[i] = (1 - 6 * dsum / (10 * (100 - 1))) * 100
    out["RANK_CORRELATION_10"] = levels(rci, -80, 80)
    out["CCI_20"] = levels(T.cci(hlc3, 20), -100, 100)
    sd10 = T.stdev(c, 10)
    upv = [None] + [None if sd10[i] is None else (sd10[i] if c[i] > c[i - 1] else 0.0) for i in range(1, n)]
    dnv = [None] + [None if sd10[i] is None else (sd10[i] if c[i] < c[i - 1] else 0.0) for i in range(1, n)]
    eu, ed = T.ema(upv, 14), T.ema(dnv, 14)
    rvx = [None if a is None or b is None or a + b == 0 else 100 * a / (a + b) for a, b in zip(eu, ed)]
    out["RELATIVE_VOLATILITY_10"] = cross_pair(rvx, const(n, 50.0))
    # line crossings
    aru = [None if i < 14 else 100 * (14 - (i - max(range(i - 14, i + 1), key=lambda k: (h[k], k)))) / 14 for i in range(n)]
    ard = [None if i < 14 else 100 * (14 - (i - max(range(i - 14, i + 1), key=lambda k: (-l[k], k)))) / 14 for i in range(n)]
    out["AROON_14"] = cross_pair(aru, ard)
    dip, din, _ = T.dmi(h, l, c, 14, 14)
    out["DMI_14"] = cross_pair(dip, din)
    trr = [None] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    vmp = [None] + [abs(h[i] - l[i - 1]) for i in range(1, n)]
    vmm = [None] + [abs(l[i] - h[i - 1]) for i in range(1, n)]
    def ssum(x, k):
        return [None if i < k or None in x[i - k + 1:i + 1] else sum(x[i - k + 1:i + 1]) for i in range(len(x))]
    st14 = ssum(trr, 14)
    vip = [None if a is None or b in (None, 0) else a / b for a, b in zip(ssum(vmp, 14), st14)]
    vim = [None if a is None or b in (None, 0) else a / b for a, b in zip(ssum(vmm, 14), st14)]
    out["VORTEX_14"] = cross_pair(vip, vim)
    lips, teeth = T.shift(T.rma(hl2, 5), 3), T.shift(T.rma(hl2, 8), 5)
    out["WILLIAMS_ALLIGATOR"] = cross_pair(lips, teeth)
    # flips and breaks
    atr20 = S.atr(h, l, c, 20)
    vstop, up_, maxv, minv, st_ = [None] * n, True, None, None, None
    state = [None] * n
    for i in range(n):
        if atr20[i] is None:
            continue
        if maxv is None:
            maxv = minv = c[i]
            st_ = c[i] - 2 * atr20[i]
        maxv, minv = max(maxv, c[i]), min(minv, c[i])
        st_ = max(st_, maxv - 2 * atr20[i]) if up_ else min(st_, minv + 2 * atr20[i])
        if up_ and c[i] < st_:
            up_, maxv, minv, st_ = False, c[i], c[i], c[i] + 2 * atr20[i]
        elif not up_ and c[i] > st_:
            up_, maxv, minv, st_ = True, c[i], c[i], c[i] - 2 * atr20[i]
        state[i] = 1 if up_ else -1
    out["VOLATILITY_STOP_20_2"] = ([i > 0 and state[i] == 1 and state[i - 1] == -1 for i in range(n)], [i > 0 and state[i] == -1 and state[i - 1] == 1 for i in range(n)])
    a10 = S.atr(h, l, c, 10)
    fhs = [None if x is None or a is None else x - a for x, a in zip(T.highest(h, 10), a10)]
    fls = [None if x is None or a is None else x + a for x, a in zip(T.lowest(l, 10), a10)]
    stop_s = [None if i < 8 or None in fhs[i - 8:i + 1] else max(fhs[i - 8:i + 1]) for i in range(n)]
    stop_l = [None if i < 8 or None in fls[i - 8:i + 1] else min(fls[i - 8:i + 1]) for i in range(n)]
    top = [None if a is None or b is None else max(a, b) for a, b in zip(stop_s, stop_l)]
    bot = [None if a is None or b is None else min(a, b) for a, b in zip(stop_s, stop_l)]
    out["CHANDE_KROLL_STOP"] = ([up_cross(c, top, i) for i in range(n)], [dn_cross(c, bot, i) for i in range(n)])
    s20b = T.sma(c, 20)
    env_u = [None if x is None else x * 1.10 for x in s20b]
    env_l = [None if x is None else x * 0.90 for x in s20b]
    out["ENVELOPE_20_10PCT"] = ([up_cross(c, env_l, i) for i in range(n)], [dn_cross(c, env_u, i) for i in range(n)])
    lrc_u, lrc_l = [None] * n, [None] * n
    xm = 49.5
    sxx = sum((k - xm) ** 2 for k in range(100))
    for i in range(99, n):
        w = c[i - 99:i + 1]
        ym = sum(w) / 100
        slope = sum((k - xm) * (y - ym) for k, y in enumerate(w)) / sxx
        fit = [ym + slope * (k - xm) for k in range(100)]
        dev = math.sqrt(sum((y - f) ** 2 for y, f in zip(w, fit)) / 100)
        lrc_u[i], lrc_l[i] = fit[-1] + 2 * dev, fit[-1] - 2 * dev
    out["LINREG_CHANNEL_100_2"] = ([up_cross(c, lrc_l, i) for i in range(n)], [dn_cross(c, lrc_u, i) for i in range(n)])
    tw, acc_tw, cnt, day = [None] * n, 0.0, 0, None
    for i in range(n):
        dd = E.t[i] // 86400
        if dd != day:
            day, acc_tw, cnt = dd, 0.0, 0
        acc_tw += (o[i] + h[i] + l[i] + c[i]) / 4
        cnt += 1
        tw[i] = acc_tw / cnt
    out["TWAP_1D"] = ([up_cross(c, tw, i) and E.t[i] // 86400 == E.t[i - 1] // 86400 for i in range(n)],
                      [dn_cross(c, tw, i) and E.t[i] // 86400 == E.t[i - 1] // 86400 for i in range(n)])
    obv, acc = [], 0.0
    for i in range(n):
        acc += 0 if i == 0 else (v[i] if c[i] > c[i - 1] else -v[i] if c[i] < c[i - 1] else 0)
        obv.append(acc)
    out["OBV_VS_SMA20"] = cross_pair(obv, T.sma(obv, 20))
    out["ACCUM_DIST_VS_SMA20"] = cross_pair(ad, T.sma(ad, 20))
    pvt, acc = [0.0], 0.0
    for i in range(1, n):
        acc += (c[i] - c[i - 1]) / c[i - 1] * v[i]
        pvt.append(acc)
    out["PVT_VS_SMA20"] = cross_pair(pvt, T.sma(pvt, 20))
    nvi, pvi = [1000.0], [1000.0]
    for i in range(1, n):
        ch = (c[i] - c[i - 1]) / c[i - 1]
        nvi.append(nvi[-1] * (1 + ch) if v[i] < v[i - 1] else nvi[-1])
        pvi.append(pvi[-1] * (1 + ch) if v[i] > v[i - 1] else pvi[-1])
    out["NVI_VS_EMA255"] = cross_pair(nvi, T.ema(nvi, 255))
    out["PVI_VS_EMA255"] = cross_pair(pvi, T.ema(pvi, 255))
    # RSI divergence indicator (built-in): regular bullish / bearish divergence on RSI pivots (5/5), 5..60 bars apart
    rsi14 = S.rsi(c, 14)
    buy, sell = [False] * n, [False] * n
    last_pl = last_ph = None
    for i in range(10, n):
        p = i - 5
        w = rsi14[p - 5:p + 6]
        if None in w:
            continue
        if rsi14[p] == min(w) and w.count(rsi14[p]) == 1:
            if last_pl is not None and 5 <= p - last_pl <= 60 and rsi14[p] > rsi14[last_pl] and l[p] < l[last_pl]:
                buy[i] = True
            last_pl = p
        if rsi14[p] == max(w) and w.count(rsi14[p]) == 1:
            if last_ph is not None and 5 <= p - last_ph <= 60 and rsi14[p] < rsi14[last_ph] and h[p] > h[last_ph]:
                sell[i] = True
            last_ph = p
    out["RSI_DIVERGENCE_BUILTIN"] = (buy, sell)
    return out


def alternates(buy, sell):
    """True if BUY and SELL signals strictly alternate (then FLIP trading is meaningful)."""
    seq = [1 if b else -1 for b, s in zip(buy, sell) if b or s]
    return len(seq) > 10 and all(x != y for x, y in zip(seq, seq[1:]))
