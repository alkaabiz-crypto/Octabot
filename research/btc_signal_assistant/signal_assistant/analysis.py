"""Indicator readings and the BUY / SELL / WAIT / AVOID decision.

The decision is a fixed, transparent rule set. It is NOT a fitted model and it carries no probability.
Rules (long side; the short side mirrors them):

  Trend gate (4H, last closed candle):  close > EMA200 and EMA50 > EMA200          -> trend BULLISH
  Trigger   (1H, last closed candle):   close crosses above the previous-20-bar high -> fresh Donchian breakout
  Confirmation (1H): at least 3 of {EMA 50/200, RSI 14, MACD 12/26/9, ADX 14} bullish and none bearish
  Guard: 1H RSI above 80 downgrades BUY to WAIT (stretched move)

  BUY   = gate + trigger + confirmation, data OK
  SELL  = mirror image (close below the previous-20-bar low with a bearish 4H trend). Note that shorting BTC
          failed in the separate breakout study; SELL is best read as "exit / do not hold longs".
  AVOID = data unusable, a breakout against the 4H trend, or no trend on either timeframe (ADX < 20 on both)
  WAIT  = everything else; the report lists exactly which conditions are missing

Only the gate + Donchian trigger part of this rule set has out-of-sample evidence (the separate Donchian 20
study). The extra confirmations are conventional filters with NO track record here; they can remove good
trades as well as bad ones. The replay script reports what they did historically, descriptively.
"""
import dataclasses
import typing

from signal_assistant import constants, enums, indicators
from signal_assistant.data import Candles, DataQualityReport, fmt_utc

EVIDENCE_NOTE = (
    "Confidence is the share of indicator readings that agree with the recommendation. It is a measure of "
    "agreement between rules, not a probability that the trade is profitable. Only the 'Donchian 20 breakout on "
    "1H with 4H close above EMA200' component has been tested out of sample (separate study, moderate evidence, "
    "33-35% win rate, expectancy about +0.2R before swaps). The EMA/RSI/MACD/ADX confirmations added here have "
    "no track record and may filter out winners as well as losers. Nothing in this report is a forecast."
)


@dataclasses.dataclass(frozen=True)
class IndicatorReading:
    name: str
    timeframe: str
    bias: enums.Bias
    summary: str
    values: dict[str, float | None]


@dataclasses.dataclass(frozen=True)
class Series:
    """Indicator series for one timeframe, aligned with the candles."""
    candles: Candles
    ema_fast: list
    ema_slow: list
    rsi: list
    macd: list
    macd_signal: list
    macd_hist: list
    adx: list
    plus_di: list
    minus_di: list
    dc_upper: list
    dc_lower: list
    dc_mid: list
    atr: list

    def ready(self, i):
        """True when every indicator is defined at index i."""
        return i >= 0 and all(s[i] is not None for s in (self.ema_slow, self.rsi, self.macd_signal, self.adx, self.dc_upper))


def compute_series(candles):
    c, h, l = candles.c, candles.h, candles.l
    line, sig, hist = indicators.macd(c, constants.MACD_FAST, constants.MACD_SLOW, constants.MACD_SIGNAL)
    adx_v, pdi, mdi = indicators.adx(h, l, c, constants.ADX_PERIOD)
    up, lo, mid = indicators.donchian(h, l, constants.DONCHIAN_PERIOD)
    return Series(candles, indicators.ema(c, constants.EMA_FAST), indicators.ema(c, constants.EMA_SLOW),
                  indicators.rsi(c, constants.RSI_PERIOD), line, sig, hist, adx_v, pdi, mdi, up, lo, mid,
                  indicators.atr(h, l, c, constants.ADX_PERIOD))


def aligned_4h_index(c4h, close_time_1h):
    """Index of the last CLOSED 4H candle whose close time is at or before the 1H close time, or -1."""
    lo, hi, best = 0, len(c4h) - 1, -1
    while lo <= hi:
        m = (lo + hi) // 2
        if c4h.close_time(m) <= close_time_1h:
            best, lo = m, m + 1
        else:
            hi = m - 1
    return best


def _r(x, nd=2):
    return None if x is None else round(x, nd)


def read_donchian(s, i):
    close, up, lo = s.candles.c[i], s.dc_upper[i], s.dc_lower[i]
    prev_above = i >= 1 and s.dc_upper[i - 1] is not None and s.candles.c[i - 1] > s.dc_upper[i - 1]
    prev_below = i >= 1 and s.dc_lower[i - 1] is not None and s.candles.c[i - 1] < s.dc_lower[i - 1]
    vals = {"close": close, "upper": _r(up), "lower": _r(lo), "middle": _r(s.dc_mid[i])}
    if close > up:
        fresh = not prev_above
        vals["fresh_breakout"] = 1.0 if fresh else 0.0
        txt = ("close broke above the previous 20-bar high (fresh breakout)" if fresh
               else "close is above the previous 20-bar high, but the breakout happened on an earlier bar")
        return IndicatorReading(f"Donchian {constants.DONCHIAN_PERIOD}", s.candles.timeframe, enums.Bias.BULLISH, txt, vals)
    if close < lo:
        fresh = not prev_below
        vals["fresh_breakdown"] = 1.0 if fresh else 0.0
        txt = ("close broke below the previous 20-bar low (fresh breakdown)" if fresh
               else "close is below the previous 20-bar low, but the breakdown happened on an earlier bar")
        return IndicatorReading(f"Donchian {constants.DONCHIAN_PERIOD}", s.candles.timeframe, enums.Bias.BEARISH, txt, vals)
    pos = (close - lo) / (up - lo) * 100 if up > lo else 50.0
    vals["position_pct"] = _r(pos, 1)
    return IndicatorReading(f"Donchian {constants.DONCHIAN_PERIOD}", s.candles.timeframe, enums.Bias.NEUTRAL,
                            f"close inside the channel at {pos:.0f}% of its range (no breakout)", vals)


def read_ema(s, i):
    close, f, sl = s.candles.c[i], s.ema_fast[i], s.ema_slow[i]
    vals = {"close": close, "ema50": _r(f), "ema200": _r(sl)}
    name = f"EMA {constants.EMA_FAST}/{constants.EMA_SLOW}"
    if close > sl and f > sl:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BULLISH,
                                "close above EMA200 and EMA50 above EMA200 (bullish structure)", vals)
    if close < sl and f < sl:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BEARISH,
                                "close below EMA200 and EMA50 below EMA200 (bearish structure)", vals)
    return IndicatorReading(name, s.candles.timeframe, enums.Bias.NEUTRAL,
                            "close and EMA50 are on opposite sides of EMA200 (mixed structure)", vals)


def read_rsi(s, i):
    v = s.rsi[i]
    vals = {"rsi": _r(v, 1)}
    name = f"RSI {constants.RSI_PERIOD}"
    if v >= constants.RSI_OVERBOUGHT:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BULLISH, f"RSI {v:.1f}: strong momentum but overbought (above {constants.RSI_OVERBOUGHT:.0f})", vals)
    if v > constants.RSI_MIDLINE:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BULLISH, f"RSI {v:.1f}: above 50, bullish momentum", vals)
    if v <= constants.RSI_OVERSOLD:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BEARISH, f"RSI {v:.1f}: weak momentum and oversold (below {constants.RSI_OVERSOLD:.0f})", vals)
    if v < constants.RSI_MIDLINE:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BEARISH, f"RSI {v:.1f}: below 50, bearish momentum", vals)
    return IndicatorReading(name, s.candles.timeframe, enums.Bias.NEUTRAL, "RSI exactly 50", vals)


def read_macd(s, i):
    line, sig, hist = s.macd[i], s.macd_signal[i], s.macd_hist[i]
    prev_hist = s.macd_hist[i - 1] if i >= 1 else None
    vals = {"macd": _r(line), "signal": _r(sig), "histogram": _r(hist)}
    name = f"MACD {constants.MACD_FAST}/{constants.MACD_SLOW}/{constants.MACD_SIGNAL}"
    rising = prev_hist is not None and hist > prev_hist
    if line > sig:
        extra = ", histogram expanding" if rising else ", histogram shrinking"
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BULLISH,
                                f"MACD line above signal line{extra}" + (", MACD above zero" if line > 0 else ", MACD below zero"), vals)
    if line < sig:
        extra = ", histogram expanding" if (prev_hist is not None and hist < prev_hist) else ", histogram shrinking"
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BEARISH,
                                f"MACD line below signal line{extra}" + (", MACD below zero" if line < 0 else ", MACD above zero"), vals)
    return IndicatorReading(name, s.candles.timeframe, enums.Bias.NEUTRAL, "MACD line equals signal line", vals)


def read_adx(s, i):
    a, p, m = s.adx[i], s.plus_di[i], s.minus_di[i]
    vals = {"adx": _r(a, 1), "plus_di": _r(p, 1), "minus_di": _r(m, 1)}
    name = f"ADX {constants.ADX_PERIOD}"
    strength = ("strong trend" if a >= constants.ADX_TRENDING else "weak trend" if a >= constants.ADX_WEAK else "no trend")
    if a < constants.ADX_WEAK:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.NEUTRAL,
                                f"ADX {a:.1f}: {strength} (below {constants.ADX_WEAK:.0f}), direction not reliable", vals)
    if p > m:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BULLISH, f"ADX {a:.1f}: {strength}, +DI above -DI", vals)
    if m > p:
        return IndicatorReading(name, s.candles.timeframe, enums.Bias.BEARISH, f"ADX {a:.1f}: {strength}, -DI above +DI", vals)
    return IndicatorReading(name, s.candles.timeframe, enums.Bias.NEUTRAL, f"ADX {a:.1f}: +DI equals -DI", vals)


def read_all(s, i):
    return [read_donchian(s, i), read_ema(s, i), read_rsi(s, i), read_macd(s, i), read_adx(s, i)]


def trend_from_4h(readings_4h):
    """The 4H trend is the EMA structure. Other 4H readings describe how strongly it is supported."""
    ema_reading = next(r for r in readings_4h if r.name.startswith("EMA"))
    return ema_reading.bias


class Agreement(typing.TypedDict):
    bullish: int
    bearish: int
    neutral: int
    total: int


def agreement(readings):
    return Agreement(bullish=sum(r.bias == enums.Bias.BULLISH for r in readings),
                     bearish=sum(r.bias == enums.Bias.BEARISH for r in readings),
                     neutral=sum(r.bias == enums.Bias.NEUTRAL for r in readings), total=len(readings))


@dataclasses.dataclass(frozen=True)
class Assessment:
    as_of_utc: str                     # close time of the 1H candle the assessment is based on
    as_of_ts: int
    price: float
    recommendation: enums.Recommendation
    confidence: enums.Confidence
    leaning: enums.Bias                # direction the majority of readings point to
    trend_4h: enums.Bias
    readings_1h: list[IndicatorReading]
    readings_4h: list[IndicatorReading]
    agreement: Agreement
    reasons: list[str]          # why this recommendation
    missing_for_buy: list[str]  # what would still be needed for a BUY
    warnings: list[str]
    data_quality: DataQualityReport
    evidence_note: str = EVIDENCE_NOTE

    @property
    def confirmed_buy(self):
        return self.recommendation == enums.Recommendation.BUY

    def to_dict(self):
        d = dataclasses.asdict(self)
        for k in ("recommendation", "confidence", "leaning", "trend_4h"):
            d[k] = getattr(self, k).value
        for key in ("readings_1h", "readings_4h"):
            for r in d[key]:
                r["bias"] = r["bias"].value
        return d


def _confidence(readings, direction):
    aligned = sum(r.bias == direction for r in readings)
    if aligned >= constants.HIGH_CONFIDENCE_MIN_AGREEMENT:
        return enums.Confidence.HIGH
    if aligned >= constants.MEDIUM_CONFIDENCE_MIN_AGREEMENT:
        return enums.Confidence.MEDIUM
    return enums.Confidence.LOW


def _by_name(readings, prefix):
    return next(r for r in readings if r.name.startswith(prefix))


def assess(s1h, s4h, i, quality):
    """Assess the market at 1H candle index ``i`` (its close), using the last closed 4H candle at that time."""
    c1h = s1h.candles
    tc = c1h.close_time(i)
    k = aligned_4h_index(s4h.candles, tc)
    price = c1h.c[i]
    base = {"as_of_utc": fmt_utc(tc), "as_of_ts": tc, "price": price, "data_quality": quality}
    if not s1h.ready(i) or k < 0 or not s4h.ready(k):
        return Assessment(**base, recommendation=enums.Recommendation.AVOID, confidence=enums.Confidence.NONE,
                          leaning=enums.Bias.NEUTRAL, trend_4h=enums.Bias.NEUTRAL, readings_1h=[], readings_4h=[],
                          agreement=Agreement(bullish=0, bearish=0, neutral=0, total=0),
                          reasons=["indicators are not yet defined for this candle (not enough history)"],
                          missing_for_buy=["enough closed candles for EMA200 and ADX on both timeframes"],
                          warnings=list(quality["issues"]))
    r1, r4 = read_all(s1h, i), read_all(s4h, k)
    trend = trend_from_4h(r4)
    agr = agreement(r1 + r4)
    leaning = (enums.Bias.BULLISH if agr["bullish"] > agr["bearish"] else enums.Bias.BEARISH if agr["bearish"] > agr["bullish"]
               else enums.Bias.NEUTRAL)
    dc, ema_r, rsi_r, macd_r, adx_r = r1
    adx4 = _by_name(r4, "ADX")
    confirmers = [ema_r, rsi_r, macd_r, adx_r]
    bull_conf = [r for r in confirmers if r.bias == enums.Bias.BULLISH]
    bear_conf = [r for r in confirmers if r.bias == enums.Bias.BEARISH]
    fresh_up = dc.values.get("fresh_breakout") == 1.0
    fresh_down = dc.values.get("fresh_breakdown") == 1.0
    rsi_val = rsi_r.values["rsi"]
    warnings = list(quality["issues"])
    reasons, missing = [], []

    # ---- what a BUY needs, item by item (always reported so the user sees the distance to a signal)
    if trend == enums.Bias.BULLISH:
        reasons.append("4H trend gate passed: " + _by_name(r4, "EMA").summary)
    else:
        missing.append("4H trend gate: close above EMA200 and EMA50 above EMA200 (currently " + _by_name(r4, "EMA").summary + ")")
    if fresh_up:
        reasons.append("1H trigger: " + dc.summary)
    else:
        missing.append("1H trigger: a fresh close above the previous 20-bar high (currently " + dc.summary + ")")
    if len(bull_conf) >= constants.MIN_CONFIRMING_1H_INDICATORS and not bear_conf:
        reasons.append(f"1H confirmation: {len(bull_conf)} of 4 indicators bullish, none bearish "
                       f"({', '.join(r.name for r in bull_conf)})")
    else:
        missing.append(f"1H confirmation: at least {constants.MIN_CONFIRMING_1H_INDICATORS} of 4 bullish and none bearish "
                       f"(currently {len(bull_conf)} bullish, {len(bear_conf)} bearish"
                       + (": " + ", ".join(f"{r.name} {r.bias.value.lower()}" for r in bear_conf) if bear_conf else "") + ")")
    if rsi_val is not None and rsi_val > constants.RSI_EXTREME_HIGH:
        missing.append(f"1H RSI at or below {constants.RSI_EXTREME_HIGH:.0f} (currently {rsi_val:.1f}, stretched)")

    # ---- AVOID conditions
    if quality["quality"] == enums.DataQuality.UNUSABLE.value:
        return Assessment(**base, recommendation=enums.Recommendation.AVOID, confidence=enums.Confidence.NONE, leaning=leaning,
                          trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                          reasons=["market data is unusable: " + "; ".join(quality["issues"])],
                          missing_for_buy=["usable, fresh, gap-free data"] + missing, warnings=warnings)
    if (trend == enums.Bias.BULLISH and dc.bias == enums.Bias.BEARISH) or (trend == enums.Bias.BEARISH and dc.bias == enums.Bias.BULLISH):
        return Assessment(**base, recommendation=enums.Recommendation.AVOID, confidence=enums.Confidence.NONE, leaning=leaning,
                          trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                          reasons=[(f"1H Donchian {dc.bias.value.lower()} break against a {trend.value.lower()} 4H trend "
                                   "(counter-trend breakout; the separate study found these unreliable)")],
                          missing_for_buy=missing, warnings=warnings)
    adx1_val, adx4_val = adx_r.values["adx"], adx4.values["adx"]
    if trend == enums.Bias.NEUTRAL and adx1_val < constants.ADX_WEAK and adx4_val < constants.ADX_WEAK:
        return Assessment(**base, recommendation=enums.Recommendation.AVOID, confidence=enums.Confidence.NONE, leaning=leaning,
                          trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                          reasons=[(f"no trend on either timeframe: 4H EMA structure mixed, ADX {adx4_val:.1f} (4H) and "
                                   f"{adx1_val:.1f} (1H) both below {constants.ADX_WEAK:.0f}; breakouts in such conditions tend to fail")],
                          missing_for_buy=missing, warnings=warnings)

    # ---- BUY
    if trend == enums.Bias.BULLISH and fresh_up and len(bull_conf) >= constants.MIN_CONFIRMING_1H_INDICATORS and not bear_conf:
        if rsi_val > constants.RSI_EXTREME_HIGH:
            return Assessment(**base, recommendation=enums.Recommendation.WAIT, confidence=_confidence(r1 + r4, enums.Bias.BULLISH),
                              leaning=leaning, trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                              reasons=reasons + [(f"BUY conditions met but 1H RSI {rsi_val:.1f} is above {constants.RSI_EXTREME_HIGH:.0f}: "
                                                 "the move is stretched, so the signal is downgraded to WAIT")],
                              missing_for_buy=missing, warnings=warnings)
        conf = _confidence(r1 + r4, enums.Bias.BULLISH)
        if adx4_val < constants.ADX_WEAK:
            warnings.append(f"4H ADX {adx4_val:.1f} is below {constants.ADX_WEAK:.0f}: the higher-timeframe trend is weak")
        if quality["quality"] == enums.DataQuality.DEGRADED.value:
            warnings.append("data quality degraded (historical gaps); indicator values span exchange halts")
        return Assessment(**base, recommendation=enums.Recommendation.BUY, confidence=conf, leaning=leaning, trend_4h=trend,
                          readings_1h=r1, readings_4h=r4, agreement=agr,
                          reasons=reasons + [(f"agreement: {agr['bullish']} of {agr['total']} indicator readings bullish, "
                                             f"{agr['bearish']} bearish, {agr['neutral']} neutral")],
                          missing_for_buy=[], warnings=warnings)

    # ---- SELL (mirror)
    if trend == enums.Bias.BEARISH and fresh_down and len(bear_conf) >= constants.MIN_CONFIRMING_1H_INDICATORS and not bull_conf:
        sell_reasons = ["4H trend gate (bearish): " + _by_name(r4, "EMA").summary, "1H trigger: " + dc.summary,
                        f"1H confirmation: {len(bear_conf)} of 4 indicators bearish, none bullish ({', '.join(r.name for r in bear_conf)})",
                        f"agreement: {agr['bearish']} of {agr['total']} indicator readings bearish"]
        if rsi_val < constants.RSI_EXTREME_LOW:
            return Assessment(**base, recommendation=enums.Recommendation.WAIT, confidence=_confidence(r1 + r4, enums.Bias.BEARISH),
                              leaning=leaning, trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                              reasons=sell_reasons + [(f"SELL conditions met but 1H RSI {rsi_val:.1f} is below {constants.RSI_EXTREME_LOW:.0f}: "
                                                      "the drop is stretched, so the signal is downgraded to WAIT")],
                              missing_for_buy=missing, warnings=warnings)
        warnings.append("SELL means exit or do not hold longs. Short BTC breakouts failed in the separate study; "
                        "this is not a validated short entry.")
        return Assessment(**base, recommendation=enums.Recommendation.SELL, confidence=_confidence(r1 + r4, enums.Bias.BEARISH),
                          leaning=leaning, trend_4h=trend, readings_1h=r1, readings_4h=r4, agreement=agr,
                          reasons=sell_reasons, missing_for_buy=missing, warnings=warnings)

    # ---- WAIT
    wait_reasons = reasons + [f"{len(missing)} BUY condition(s) not met (see 'missing for BUY')",
                              f"agreement: {agr['bullish']} bullish, {agr['bearish']} bearish, {agr['neutral']} neutral of {agr['total']} readings"]
    conf = _confidence(r1 + r4, leaning) if leaning != enums.Bias.NEUTRAL else enums.Confidence.LOW
    return Assessment(**base, recommendation=enums.Recommendation.WAIT, confidence=conf, leaning=leaning, trend_4h=trend,
                      readings_1h=r1, readings_4h=r4, agreement=agr, reasons=wait_reasons, missing_for_buy=missing, warnings=warnings)


def assess_latest(c1h, c4h, now_s=None):
    """Convenience: compute series and assess the last closed 1H candle."""
    from signal_assistant import data as data_mod  # local import keeps module import order simple
    quality = data_mod.assess_quality(c1h, c4h, now_s)
    s1h, s4h = compute_series(c1h), compute_series(c4h)
    return assess(s1h, s4h, len(c1h) - 1, quality)
