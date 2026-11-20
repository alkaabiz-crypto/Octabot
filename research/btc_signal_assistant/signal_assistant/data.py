"""Market data: Binance BTCUSDT spot klines, closed candles only.

Source: ``data-api.binance.vision`` (Binance's official public market-data mirror), the same source the
Donchian forward test uses. A candle is used only when its Binance close time is in the past, so an
unfinished candle never influences a signal. Candles can also be loaded from a local JSON file in the
``[[open_time_s, open, high, low, close, volume], ...]`` layout for offline runs and tests.
"""
import dataclasses
import itertools
import json
import os
import ssl
import time
import typing
import urllib.error
import urllib.request

from signal_assistant import constants, enums, errors


@dataclasses.dataclass(frozen=True)
class Candles:
    """Column-oriented closed candles for one timeframe. ``t`` is the candle OPEN time in UTC seconds."""
    timeframe: str
    t: list[int]
    o: list[float]
    h: list[float]
    l: list[float]
    c: list[float]
    v: list[float]

    def __len__(self):
        return len(self.t)

    @property
    def step(self):
        return constants.STEP_SECONDS[self.timeframe]

    def close_time(self, i):
        """Close time (UTC seconds) of candle i."""
        return self.t[i] + self.step

    def truncated(self, n):
        """First ``n`` candles only (used for no-look-ahead checks and replays)."""
        return Candles(self.timeframe, self.t[:n], self.o[:n], self.h[:n], self.l[:n], self.c[:n], self.v[:n])

    @staticmethod
    def from_rows(timeframe, rows):
        rows = sorted(rows, key=lambda r: r[0])
        for r in rows:
            _, o, h, l, c, v = r[:6]
            if not (l <= min(o, c) and max(o, c) <= h and l > 0 and v >= 0):
                raise errors.CorruptCandleError(f"{timeframe} candle at {r[0]} fails OHLC sanity check: {r[:6]}")
        return Candles(timeframe, [int(r[0]) for r in rows], [float(r[1]) for r in rows], [float(r[2]) for r in rows],
                       [float(r[3]) for r in rows], [float(r[4]) for r in rows], [float(r[5]) for r in rows])

    def to_rows(self):
        return [[self.t[i], self.o[i], self.h[i], self.l[i], self.c[i], self.v[i]] for i in range(len(self))]


class DataQualityReport(typing.TypedDict):
    quality: str
    issues: list[str]
    last_closed_1h_utc: str
    last_closed_4h_utc: str
    age_seconds_1h: int
    bars_1h: int
    bars_4h: int


def _ssl_context():
    if os.path.exists(constants.CA_BUNDLE_PATH):
        return ssl.create_default_context(cafile=constants.CA_BUNDLE_PATH)
    return ssl.create_default_context()


def fetch_closed_candles(timeframe, start_s, now_s=None, symbol=constants.SYMBOL, retries=5, sleep=time.sleep):
    """Download closed candles from ``start_s`` (UTC seconds) up to now. Pages by startTime."""
    now_ms = int((now_s if now_s is not None else time.time()) * 1000)
    step_ms = constants.STEP_SECONDS[timeframe] * 1000
    ctx = _ssl_context()
    out, t = [], int(start_s) * 1000
    while True:
        url = f"{constants.BINANCE_KLINES_URL}?symbol={symbol}&interval={timeframe}&limit=1000&startTime={t}"
        err = None
        for attempt in range(retries):
            try:
                with urllib.request.urlopen(url, timeout=30, context=ctx) as resp:
                    rows = json.loads(resp.read())
                break
            except (urllib.error.URLError, OSError, ValueError) as e:
                err = e
                sleep(2 ** attempt)
        else:
            raise errors.DataUnavailableError(f"{timeframe} download failed at {t}: {err}")
        closed = [r for r in rows if r[6] < now_ms]
        out.extend(closed)
        if len(rows) < 1000 or len(closed) < len(rows):
            break
        t = rows[-1][0] + step_ms
    return Candles.from_rows(timeframe, [[r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in out])


def load_candles_file(timeframe, path):
    try:
        with open(path) as f:
            rows = json.load(f)
    except (OSError, ValueError) as e:
        raise errors.DataUnavailableError(f"cannot read {timeframe} candles from {path}: {e}") from e
    return Candles.from_rows(timeframe, rows)


def save_candles_file(candles, path):
    with open(path, "w") as f:
        json.dump(candles.to_rows(), f)


def fetch_market(days=constants.DEFAULT_HISTORY_DAYS, now_s=None):
    """Fetch 1H and 4H closed candles covering the last ``days`` days."""
    now_s = now_s if now_s is not None else time.time()
    start = int(now_s) - days * 86400
    return fetch_closed_candles("1h", start, now_s), fetch_closed_candles("4h", start, now_s)


def fmt_utc(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


def gaps(candles, last_n=None):
    """Return (open_time_before_gap, open_time_after_gap) pairs. Checks the last ``last_n`` candles if given."""
    ts = candles.t if last_n is None else candles.t[-last_n:]
    return [(a, b) for a, b in itertools.pairwise(ts) if b - a != candles.step]


def assess_quality(c1h, c4h, now_s=None):
    """Decide whether the data can support a recommendation."""
    now_s = now_s if now_s is not None else time.time()
    issues = []
    quality = enums.DataQuality.OK
    if len(c1h) < constants.MIN_BARS_1H or len(c4h) < constants.MIN_BARS_4H:
        issues.append(f"insufficient history: {len(c1h)} 1H bars (need {constants.MIN_BARS_1H}), "
                      f"{len(c4h)} 4H bars (need {constants.MIN_BARS_4H})")
        quality = enums.DataQuality.UNUSABLE
    age = int(now_s - c1h.close_time(len(c1h) - 1)) if len(c1h) else 10 ** 9
    if age > constants.MAX_STALE_SECONDS:
        issues.append(f"stale data: last closed 1H candle is {age // 60} minutes old")
        quality = enums.DataQuality.UNUSABLE
    # the last closed 4H candle must be the one that contains, or precedes, the last closed 1H candle
    if len(c1h) and len(c4h) and c4h.close_time(len(c4h) - 1) > c1h.close_time(len(c1h) - 1):
        issues.append("4H data runs ahead of 1H data")
        quality = enums.DataQuality.UNUSABLE
    for c in (c1h, c4h):
        recent = gaps(c, constants.GAP_CHECK_BARS)
        if recent:
            a, b = recent[0]
            issues.append(f"gap in recent {c.timeframe} candles between {fmt_utc(a)} and {fmt_utc(b)} UTC")
            quality = enums.DataQuality.UNUSABLE
        elif gaps(c):
            issues.append(f"{len(gaps(c))} historical gap(s) in {c.timeframe} data (exchange halts); indicators span them")
            if quality == enums.DataQuality.OK:
                quality = enums.DataQuality.DEGRADED
    return DataQualityReport(quality=quality.value, issues=issues,
                             last_closed_1h_utc=fmt_utc(c1h.close_time(len(c1h) - 1)) if len(c1h) else "",
                             last_closed_4h_utc=fmt_utc(c4h.close_time(len(c4h) - 1)) if len(c4h) else "",
                             age_seconds_1h=age, bars_1h=len(c1h), bars_4h=len(c4h))
