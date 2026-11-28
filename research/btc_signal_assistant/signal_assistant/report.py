"""Human-readable rendering of an Assessment."""
import json

from signal_assistant import enums

_BIAS_MARK = {enums.Bias.BULLISH: "+", enums.Bias.BEARISH: "-", enums.Bias.NEUTRAL: "="}


def _table(readings):
    width = max((len(r.name) for r in readings), default=10)
    lines = []
    for r in readings:
        lines.append(f"  [{_BIAS_MARK[r.bias]}] {r.name:<{width}}  {r.bias.value:<8} {r.summary}")
    return lines


def render_text(a):
    L = []
    L.append("=" * 78)
    L.append(f"BTCUSDT signal assistant   as of 1H close {a.as_of_utc} UTC   close {a.price:,.2f}")
    L.append("=" * 78)
    L.append(f"RECOMMENDATION : {a.recommendation.value}")
    L.append(f"Confidence     : {a.confidence.value}  (rule agreement, not a probability)")
    L.append(f"4H trend       : {a.trend_4h.value}      Leaning of all readings: {a.leaning.value}")
    g = a.agreement
    L.append(f"Agreement      : {g['bullish']} bullish / {g['bearish']} bearish / {g['neutral']} neutral of {g['total']} readings")
    L.append("")
    L.append("4H trend confirmation (last closed 4H candle)")
    L.extend(_table(a.readings_4h) or ["  (indicators undefined)"])
    L.append("")
    L.append("1H entry timeframe (last closed 1H candle)")
    L.extend(_table(a.readings_1h) or ["  (indicators undefined)"])
    L.append("")
    L.append("Reasons")
    L.extend(f"  - {r}" for r in a.reasons)
    if a.missing_for_buy:
        L.append("")
        L.append("Missing for a BUY")
        L.extend(f"  - {m}" for m in a.missing_for_buy)
    if a.warnings:
        L.append("")
        L.append("Warnings")
        L.extend(f"  ! {w}" for w in a.warnings)
    L.append("")
    L.append(f"Data: {a.data_quality['quality']}, {a.data_quality['bars_1h']} 1H bars, {a.data_quality['bars_4h']} 4H bars, "
             f"last 4H close {a.data_quality['last_closed_4h_utc']} UTC")
    L.append("")
    L.append("Evidence note: " + a.evidence_note)
    L.append("=" * 78)
    return "\n".join(L)


def render_json(a):
    return json.dumps(a.to_dict(), indent=1)


def render_alert(a):
    """Short, loud text for a confirmed BUY notification."""
    g = a.agreement
    lines = [f"BTCUSDT CONFIRMED BUY SIGNAL  ({a.confidence.value} agreement)",
             f"1H close {a.as_of_utc} UTC at {a.price:,.2f}",
             f"Agreement {g['bullish']}/{g['total']} bullish. 4H trend {a.trend_4h.value}.", ""]
    lines += [f"- {r}" for r in a.reasons]
    if a.warnings:
        lines += [""] + [f"! {w}" for w in a.warnings]
    lines += ["", "Rule agreement is not a probability of profit. Paper-trade first; nothing here is validated for live use."]
    return "\n".join(lines)
