"""Textbook indicators (pure Python). Value at index i uses bars 0..i only; ``None`` until defined.

Same definitions as the signal assistant (EMA seeded with an SMA, Wilder RSI/ATR/ADX, Donchian over the
PREVIOUS n bars), re-implemented here so this project stands alone. A test checks they agree.
"""


def ema(x, n):
    out = [None] * len(x)
    if len(x) < n:
        return out
    k = 2.0 / (n + 1)
    prev = sum(x[:n]) / n
    out[n - 1] = prev
    for i in range(n, len(x)):
        prev += k * (x[i] - prev)
        out[i] = prev
    return out


def _ema_sparse(x, n):
    first = next((i for i, v in enumerate(x) if v is not None), None)
    out = [None] * len(x)
    if first is not None:
        out[first:] = ema(x[first:], n)
    return out


def wilder(x, n):
    out = [None] * len(x)
    if len(x) < n:
        return out
    s = sum(x[:n]) / n
    out[n - 1] = s
    for i in range(n, len(x)):
        s = (s * (n - 1) + x[i]) / n
        out[i] = s
    return out


def rsi(c, n):
    out = [None] * len(c)
    if len(c) <= n:
        return out
    g = l = 0.0
    for i in range(1, n + 1):
        d = c[i] - c[i - 1]
        if d > 0:
            g += d
        else:
            l -= d
    g, l = g / n, l / n
    out[n] = _rsi(g, l)
    for i in range(n + 1, len(c)):
        d = c[i] - c[i - 1]
        g = (g * (n - 1) + (d if d > 0 else 0.0)) / n
        l = (l * (n - 1) + (-d if d < 0 else 0.0)) / n
        out[i] = _rsi(g, l)
    return out


def _rsi(g, l):
    if l == 0:
        return 100.0 if g > 0 else 50.0
    return 100.0 - 100.0 / (1.0 + g / l)


def macd(c, fast, slow, signal):
    ef, es = ema(c, fast), ema(c, slow)
    line = [None if a is None or b is None else a - b for a, b in zip(ef, es)]
    return line, _ema_sparse(line, signal)


def true_range(h, l, c):
    return [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]


def atr(h, l, c, n):
    return wilder(true_range(h, l, c), n)


def adx(h, l, c, n):
    """Returns (adx, plus_di, minus_di)."""
    m = len(c)
    out, pdi, mdi = [None] * m, [None] * m, [None] * m
    if m < 2 * n + 1:
        return out, pdi, mdi
    tr, pdm, mdm = [], [], []
    for i in range(1, m):
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm.append(up if up > dn and up > 0 else 0.0)
        mdm.append(dn if dn > up and dn > 0 else 0.0)
        tr.append(max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])))
    s_tr, s_p, s_m = wilder(tr, n), wilder(pdm, n), wilder(mdm, n)
    dx = []
    for j in range(n - 1, len(tr)):
        p, q = (0.0, 0.0) if s_tr[j] == 0 else (100.0 * s_p[j] / s_tr[j], 100.0 * s_m[j] / s_tr[j])
        pdi[j + 1], mdi[j + 1] = p, q
        dx.append(0.0 if p + q == 0 else 100.0 * abs(p - q) / (p + q))
    for j, v in enumerate(wilder(dx, n)):
        if v is not None:
            out[n + j] = v
    return out, pdi, mdi


def donchian(h, l, n):
    """Highest high / lowest low of the previous n bars (current bar excluded)."""
    m = len(h)
    up, lo = [None] * m, [None] * m
    for i in range(n, m):
        up[i] = max(h[i - n:i])
        lo[i] = min(l[i - n:i])
    return up, lo
