"""Builds INDICATOR_REVIEW.md from the committed results of TV batches 001-005 (read-only)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(H)
nm = json.load(open(os.path.join(ND, "tv_batch_004", "names.json")))
B = json.load(open(os.path.join(ND, "tv_batch_004", "results_B.json")))["picks"]; X = json.load(open(os.path.join(ND, "tv_batch_004", "results_B_exploratory_net.json")))
D = {  # what it measures | how traders use it for buy/sell
"IND-003": ("weighted sum of four smoothed rates of change", "buy when KST crosses above its signal line"),
"IND-004": ("distance of price from the volume-weighted average price of the session", "buy above VWAP / sell below; pullbacks to VWAP"),
"IND-005": ("speed of recent gains vs losses, 0–100", "buy below 30 (oversold), sell above 70; or 50-line trend filter"),
"IND-006": ("difference of a fast and slow EMA, and its signal line", "buy when MACD crosses above signal or zero"),
"IND-007": ("fast vs slow moving average", "buy on golden cross (fast above slow)"),
"IND-008": ("ATR trailing line that flips with trend", "buy when it flips below price"),
"IND-009": ("accelerating trailing stop dots", "buy when dots flip below price"),
"IND-010": ("trend strength (ADX) and direction (+DI/−DI)", "trade the DI direction only when ADX > 20–25"),
"IND-011": ("where price sits in its 20-bar high–low range", "buy breakouts of the 20-bar high (turtle rule)"),
"IND-012": ("cloud of mid-range averages, five lines", "buy above the cloud, Tenkan/Kijun crosses"),
"IND-013": ("price position inside 2-standard-deviation bands", "fade the bands in ranges; breakouts after a squeeze"),
"IND-014": ("close vs recent high–low range, 0–100", "buy %K crossing up from below 20"),
"IND-015": ("deviation of typical price from its average", "buy below −100, sell above +100"),
"IND-016": ("inverse of Stochastic, −100–0", "buy below −80, sell above −20"),
"IND-017": ("synthetic VIX: distance from 22-bar high close", "spikes mark panic lows → buy"),
"IND-020": ("20-day price change", "time-series momentum: long if positive"),
"IND-022": ("bars since highest high vs lowest low", "buy when Aroon Up crosses above Down"),
"IND-023": ("upward vs downward movement over 14 bars", "buy when VI+ crosses above VI−"),
"IND-024": ("rate of change of a triple-smoothed EMA", "buy on zero or signal cross"),
"IND-025": ("adaptive average that speeds up in trends", "trade its slope / price crossing it"),
"IND-026": ("three shifted smoothed averages (jaw, teeth, lips)", "trade when the lines open in order; sleep when tangled"),
"IND-027": ("low-lag weighted moving average", "trade its colour (slope) change"),
"IND-028": ("price vs EMA ± ATR channel", "breakouts outside the channel; mean reversion inside"),
"IND-029": ("smoothed candle colour", "stay in while candles keep one colour"),
"IND-030": ("5- vs 34-bar midpoint average", "saucer and zero-line cross signals"),
"IND-031": ("buying pressure over 7/14/28 bars", "divergence buys below 30"),
"IND-032": ("percent change over 12 bars", "zero-line cross / extremes"),
"IND-033": ("price turned into a normal-like distribution", "turning points at extremes"),
"IND-034": ("high and low vs EMA 13 (bull/bear power)", "buy when bear power rises below zero in an uptrend"),
"IND-036": ("Bollinger inside Keltner (squeeze) + momentum histogram", "trade the first bar after the squeeze fires, in the momentum direction"),
"IND-037": ("channel-index oscillator with two lines", "buy wt1/wt2 cross below −53 (oversold)"),
"IND-038": ("smoothed RSI with a volatility trailing line", "buy when it crosses above the line / 50"),
"IND-039": ("moving averages of highs and lows, flip channel", "buy when price closes above the high average"),
"IND-040": ("ATR trailing stop (key value 1)", "buy when price crosses above the trail"),
"IND-041": ("ATR stop from the 22-bar extreme", "used as a trailing exit and flip signal"),
"IND-042": ("MACD put through a double stochastic", "buy when it rises from below 25"),
"IND-043": ("long-term smoothed rate of change", "buy when it turns up from below zero (bottoms)"),
"IND-044": ("price vs a shifted moving average (cycles)", "cycle tops and bottoms"),
"IND-045": ("end point of a linear regression line", "trend slope / crosses"),
"IND-046": ("RSI 3 + streak RSI + percent rank", "buy below 10, sell above 90 (short-term reversal)"),
"IND-047": ("RSI on a four-stage Laguerre filter", "buy when it rises above 0.2"),
"IND-048": ("momentum only in trending (non-choppy) periods", "trend filter for momentum"),
}
D.update({
"IND-049": ("Gaussian-weighted moving average", "trade its slope / price crosses"), "IND-050": ("close minus open relative to range", "buyers vs sellers control; above zero bullish"),
"IND-051": ("short vs long Bollinger band spread", "positive = uptrend expansion"), "IND-052": ("volume-weighted close location over 20 bars", "buy when CMF > 0 (accumulation)"),
"IND-053": ("momentum of accumulation/distribution", "buy on zero-line cross up"), "IND-054": ("running sum of volume-weighted close location", "confirm trends; divergences"),
"IND-055": ("ATR stop pair from recent extremes", "flip signals and trailing stops"), "IND-056": ("up minus down moves, ±100", "buy below −50, sell above +50"),
"IND-057": ("EMA 34 angle colour bands", "trade in the colour's direction"), "IND-058": ("correlation of price with time", "trend strength / direction"),
"IND-059": ("double-smoothed EMA with less lag", "slope and crosses"), "IND-060": ("triple-smoothed EMA with less lag", "slope and crosses"),
"IND-061": ("price change per unit of volume", "buy when above zero (easy upward movement)"), "IND-062": ("price change × volume", "buy dips in force during uptrends"),
"IND-063": ("price vs a ±% band around an average", "fade the bands or trade breakouts"), "IND-064": ("short vs long groups of EMAs", "trade when the groups separate in one direction"),
"IND-065": ("distance from a 100-bar regression line", "fade the channel edges"), "IND-066": ("self-adjusting average", "price above it = bullish"),
"IND-067": ("price minus price n bars ago", "zero-line cross"), "IND-068": ("volume-weighted RSI", "buy below 20, sell above 80"),
"IND-069": ("up-volume minus down-volume", "positive = buying pressure"), "IND-070": ("running sum of signed volume", "rising OBV confirms an uptrend; divergences"),
"IND-071": ("MACD in percent", "signal-line crosses"), "IND-072": ("running sum of % change × volume", "confirm trends"),
"IND-073": ("rank correlation of price with time (RCI)", "buy when it turns up from −80"), "IND-074": ("close vs open relative to range", "signal-line crosses"),
"IND-075": ("RSI computed on volatility", "trend confirmation above/below 50"), "IND-076": ("double-smoothed momentum (TSI-like)", "signal-line crosses"),
"IND-077": ("Stochastic applied to RSI", "buy %K cross up from below 20"), "IND-078": ("close vs mid of the range, smoothed", "buy below −40, sell above +40"),
"IND-079": ("Wilder smoothed average", "slope / crosses"), "IND-080": ("TradingView's buy/sell vote of 15 MAs and 11 oscillators", "Strong Buy / Strong Sell readings"),
"IND-081": ("double-smoothed momentum", "signal-line and zero crosses"), "IND-082": ("ATR trailing stop on closes", "flip signals"),
"IND-083": ("volume-weighted vs simple average", "VWMA above SMA = volume backs the move"), "IND-084": ("5-bar swing highs/lows", "buy breaks above the last up-fractal"),
"IND-085": ("CCI 14 with turbo CCI 6 (Woodie's system)", "zero-line rejects and trend lines on CCI"), "IND-086": ("long-term money flow from volume", "signal-line crosses"),
"IND-087": ("yesterday's (H+L+C)/3 and support/resistance levels", "buy above the pivot, targets at R1/R2"), "IND-088": ("price makes a new low but RSI doesn't", "buy bullish divergence"),
})
V = {}
for b in ("ind_batch_001", "ind_batch_002", "tv_batch_003"):
    p = os.path.join(ND, b, "results.json")
    if os.path.exists(p): V.update({k: v["verdict"] for k, v in json.load(open(p)).get("verdicts", {}).items()})
V.update({k: v["verdict"] for k, v in json.load(open(os.path.join(ND, "tv_batch_004", "results_A.json")))["verdicts"].items()})
mk = lambda c: c.split("|")[1].rstrip("m")
rows = []
for k in sorted(D):
    w, u = D[k]; b = B.get(k); x = X.get(k)
    best = f"{mk(b['cell'])} {b['cell'].split('|')[2]} ({b['direction']}): {b['verdict'].lower()}, {b['test_net_bp']:+.0f} bp after costs" if b else "–"
    cost = f"{mk(x['cell'])} 24h {x['direction']}: {x['test_net_bp']:+.1f} bp" if x else "–"
    rows.append(f"| {k} | {nm.get(k, k)} | {w} | {u} | {V.get(k, 'NONE')} | {best} | {cost} |")
R5 = json.load(open(os.path.join(H, "results.json")))["results"]
A5 = {"STR-030a": "ATR (volatility breakout)", "STR-030b": "Bollinger Band Width (squeeze breakout)", "STR-030c": "Choppiness Index (chop→trend)", "STR-030d": "Mass Index (reversal bulge)",
      "STR-030e": "Volume / Relative Volume (spike follows candle)", "STR-030f": "Volume (climax fade)", "STR-030g": "Average Daily Range (exhaustion fade)", "STR-030h": "Historical Volatility (calm→breakout)",
      "STR-030i": "Volume Profile (value-area re-entry, 80% rule)", "STR-030j": "Zig Zag (causal swing break)", "STR-030k": "Seasonality (best/worst hour of week)", "STR-030l": "Moon Phases (Dichev–Janes)"}
nd = []
for sid, name in A5.items():
    cells = []
    for m in ("XAUUSDm", "USOILm", "BTCUSDm", "US500m", "EURUSDm"):
        r = R5[f"{sid}|{m}"]; te = r["results"]["TEST"]; v = te.get("mean_R", te.get("mean_net_bp")); u = "R" if "mean_R" in te else " bp"
        cells.append(f"{v:+.2f}{u}" if v is not None else "–")
    dec = sorted({R5[f'{sid}|{m}']['decision'] for m in ('XAUUSDm', 'USOILm', 'BTCUSDm', 'US500m', 'EURUSDm')})
    nd.append(f"| {name} | " + " | ".join(cells) + f" | {', '.join(dec)} |")
txt = open(os.path.join(H, "REVIEW_TEMPLATE.md")).read().replace("{{ROWS}}", "\n".join(rows)).replace("{{NONDIR}}", "\n".join(nd))
open(os.path.join(H, "INDICATOR_REVIEW.md"), "w").write(txt); print(len(rows), "indicators,", len(nd), "non-direction built-ins")
