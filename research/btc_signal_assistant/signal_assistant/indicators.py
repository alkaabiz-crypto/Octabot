"""Pure-Python technical indicators operating on closed candles.

All functions return lists aligned with the input (index i describes candle i) and use ``None``
where the value is not yet defined. Every value at index i depends only on candles 0..i, so a
series truncated at i reproduces the same value at i (no look-ahead). This property is tested.

Definitions follow the textbook versions:
- EMA: seeded with the SMA of the first ``period`` values, then ema = prev + k * (x - prev), k = 2/(period+1).
- RSI: Wilder's RSI. First average gain/loss is a simple mean of ``period`` changes, then Wilder smoothing.
- MACD: EMA(fast) - EMA(slow); signal = EMA(signal) of the MACD line; histogram = MACD - signal.
- ADX: Wilder's DMI/ADX. TR, +DM, -DM smoothed with Wilder's method; DX = 100*|+DI - -DI|/(+DI + -DI);
  ADX seeded with the mean of the first ``period`` DX values, then Wilder-smoothed.
- Donchian: highest high / lowest low of the PREVIOUS ``period`` candles (the current candle excluded),
  so that "close above the upper band" is a genuine breakout of prior range.
"""
from signal_assistant import errors


def _check_period(period):
    if not isinstance(period, int) or period < 1:
        raise errors.IndicatorError(f"period must be a positive integer, got {period!r}")


def sma(values, period):
    _check_period(period)
    out = [None] * len(values)
    running = 0.0
    for i, v in enumerate(values):
        running += v
        if i >= period:
            running -= values[i - period]
        if i >= period - 1:
            out[i] = running / period
    return out


def ema(values, period):
    """EMA seeded with the SMA of the first ``period`` values."""
    _check_period(period)
    out = [None] * len(values)
    if len(values) < period:
        return out
    k = 2.0 / (period + 1)
    prev = sum(values[:period]) / period
    out[period - 1] = prev
    for i in range(period, len(values)):
        prev = prev + k * (values[i] - prev)
        out[i] = prev
    return out


def _ema_from_sparse(values, period):
    """EMA over a list that may start with ``None`` entries (used for the MACD signal line)."""
    first = next((i for i, v in enumerate(values) if v is not None), None)
    out = [None] * len(values)
    if first is None:
        return out
    sub = ema(values[first:], period)
    out[first:] = sub
    return out


def rsi(closes, period):
    """Wilder's RSI."""
    _check_period(period)
    out = [None] * len(closes)
    if len(closes) <= period:
        return out
    gains = losses = 0.0
    for i in range(1, period + 1):
        d = closes[i] - closes[i - 1]
        if d > 0:
            gains += d
        else:
            losses -= d
    avg_gain, avg_loss = gains / period, losses / period
    out[period] = _rsi_value(avg_gain, avg_loss)
    for i in range(period + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        gain = d if d > 0 else 0.0
        loss = -d if d < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        out[i] = _rsi_value(avg_gain, avg_loss)
    return out


def _rsi_value(avg_gain, avg_loss):
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def macd(closes, fast, slow, signal):
    """Returns (macd_line, signal_line, histogram)."""
    if fast >= slow:
        raise errors.IndicatorError("MACD fast period must be smaller than slow period")
    ef, es = ema(closes, fast), ema(closes, slow)
    line = [None if (a is None or b is None) else a - b for a, b in zip(ef, es)]
    sig = _ema_from_sparse(line, signal)
    hist = [None if (a is None or b is None) else a - b for a, b in zip(line, sig)]
    return line, sig, hist


def true_range(highs, lows, closes):
    out = [None] * len(closes)
    for i in range(len(closes)):
        if i == 0:
            out[i] = highs[i] - lows[i]
        else:
            pc = closes[i - 1]
            out[i] = max(highs[i] - lows[i], abs(highs[i] - pc), abs(lows[i] - pc))
    return out


def atr(highs, lows, closes, period):
    """Wilder's ATR (seeded with the mean of the first ``period`` true ranges)."""
    _check_period(period)
    tr = true_range(highs, lows, closes)
    return _wilder_smooth(tr, period)


def _wilder_smooth(values, period):
    """Wilder smoothing: seed = mean of first ``period`` values, then s = (s*(period-1) + x)/period."""
    out = [None] * len(values)
    if len(values) < period:
        return out
    s = sum(values[:period]) / period
    out[period - 1] = s
    for i in range(period, len(values)):
        s = (s * (period - 1) + values[i]) / period
        out[i] = s
    return out


def adx(highs, lows, closes, period):
    """Wilder's DMI. Returns (adx, plus_di, minus_di)."""
    _check_period(period)
    n = len(closes)
    empty = [None] * n
    if n < 2 * period + 1:
        return empty, empty[:], empty[:]
    tr, pdm, mdm = [], [], []
    for i in range(1, n):
        up = highs[i] - highs[i - 1]
        down = lows[i - 1] - lows[i]
        pdm.append(up if (up > down and up > 0) else 0.0)
        mdm.append(down if (down > up and down > 0) else 0.0)
        pc = closes[i - 1]
        tr.append(max(highs[i] - lows[i], abs(highs[i] - pc), abs(lows[i] - pc)))
    # Wilder's original smoothing of TR/DM uses running sums: S = S - S/period + x; seeded with a sum.
    # This equals period * (Wilder-smoothed average). DI ratios are unaffected, so the average form is used.
    s_tr, s_pdm, s_mdm = _wilder_smooth(tr, period), _wilder_smooth(pdm, period), _wilder_smooth(mdm, period)
    plus_di, minus_di, dx = [None] * n, [None] * n, []
    for j in range(len(tr)):
        i = j + 1
        if s_tr[j] is None:
            continue
        if s_tr[j] == 0:
            pdi = mdi = 0.0
        else:
            pdi, mdi = 100.0 * s_pdm[j] / s_tr[j], 100.0 * s_mdm[j] / s_tr[j]
        plus_di[i], minus_di[i] = pdi, mdi
        dx.append(0.0 if pdi + mdi == 0 else 100.0 * abs(pdi - mdi) / (pdi + mdi))
    first_dx_index = period  # candle index of the first DX value (= j of period-1, +1)
    s_dx = _wilder_smooth(dx, period)
    out = [None] * n
    for j, v in enumerate(s_dx):
        if v is not None:
            out[first_dx_index + j] = v
    return out, plus_di, minus_di


def donchian(highs, lows, period):
    """Upper/lower band = highest high / lowest low of the PREVIOUS ``period`` candles.

    Returns (upper, lower, middle). Index i is defined when i >= period.
    """
    _check_period(period)
    n = len(highs)
    upper, lower, middle = [None] * n, [None] * n, [None] * n
    for i in range(period, n):
        hh = max(highs[i - period:i])
        ll = min(lows[i - period:i])
        upper[i], lower[i], middle[i] = hh, ll, (hh + ll) / 2.0
    return upper, lower, middle
