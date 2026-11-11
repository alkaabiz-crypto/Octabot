"""Independent re-computation of three shortlist rules with separate, simple code (no imports from screen.py or study.py).

Checks: gold G_MOM50_ATR (x1), US oil O_INTRADAY (x1), BTC C_SMA50 (0.1% fee). Prints recomputed vs recorded values.
Usage: CACHE_DIR=<scratch screen_cache> python3 -I verify_independent.py
"""
import json, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.environ["CACHE_DIR"]
MONTHS = [f"{y}_{m:02d}" for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
rec = json.load(open(os.path.join(HERE, "results", "results.json")))


def load(sym):
    p = [np.load(os.path.join(CACHE, f"{sym}_{m}.npz")) for m in MONTHS]
    df = pd.DataFrame({"t": np.concatenate([x["t"] for x in p]), "bid": np.concatenate([x["bid"] for x in p]), "ask": np.concatenate([x["ask"] for x in p])})
    return df.sort_values("t", kind="stable").reset_index(drop=True)


def days(df):
    x = df.assign(mid=(df.bid + df.ask) / 2, spr=df.ask - df.bid, key=pd.to_datetime(df.t + 7_200_000, unit="ms").dt.floor("D"))
    g = x.groupby("key")
    d = pd.DataFrame({"o": g.mid.first(), "h": g.mid.max(), "l": g.mid.min(), "c": g.mid.last(), "s": g.spr.first(), "n": g.size()})
    return d[d.n >= 100].reset_index()


# --- gold MOM50 + ATR exits, equity via returns
g = days(load("XAUUSDm"))
atr = pd.concat([g.h - g.l, (g.h - g.c.shift()).abs(), (g.l - g.c.shift()).abs()], axis=1).max(axis=1).ewm(alpha=1 / 14, adjust=False).mean()
sma20 = g.c.rolling(20).mean()
pos, w = False, []
for i in range(len(g)):
    if pos:
        held += 1; peak = max(peak, g.c[i])
        if g.c[i] < entry - 2 * atr[i] or g.c[i] < peak - 1.5 * atr[i] or held >= 30: pos = False
    elif i >= 50 and g.c[i] > g.c[i - 50] and sma20[i] > sma20[i - 5]:
        pos, entry, peak, held = True, g.c[i], g.c[i], 0
    w.append(1.0 if pos else 0.0)
eq, prev = 1.0, 0.0; curve = []
for i in range(len(g) - 2):
    eq *= 1 - abs(w[i] - prev) * g.s[i + 1] / 2 / g.o[i + 1]; prev = w[i]
    eq *= 1 + w[i] * (g.o[i + 2] / g.o[i + 1] - 1); curve.append(eq)
c = np.array(curve[54:]) / curve[54]
gold_net = c[-1] - 1

# --- oil intraday momentum
o = load("USOILm"); T = o.t.values; MID = ((o.bid + o.ask) / 2).values; B, A = o.bid.values, o.ask.values
def at(ms, tol):
    i = np.searchsorted(T, ms); return i if i < len(T) and T[i] - ms <= tol else None
def ny(d, h, m): return int(pd.Timestamp(d.year, d.month, d.day, h, m, tz="America/New_York").tz_convert("UTC").value // 10**6)
rets = []
for d in pd.date_range("2025-01-01", "2026-10-31"):
    if d.weekday() > 4: continue
    s0, s1 = ((10, 30), (11, 0)) if d.weekday() == 2 else ((9, 30), (10, 0))
    i, j = at(ny(d, *s0), 300_000), at(ny(d, *s1), 300_000)
    if i is None or j is None or MID[j] == MID[i]: continue
    side = 1 if MID[j] > MID[i] else -1
    e, x = at(ny(d, 15, 30), 5_400_000), at(ny(d, 16, 0), 5_400_000)
    if e is None or x is None or x <= e: continue
    entry = A[e] if side > 0 else B[e]; exitp = B[x] if side > 0 else A[x]
    rets.append((exitp - entry) * side / MID[e])
oil_net = np.prod(1 + np.array(rets)) - 1

# --- BTC close above SMA50, 0.1% fee, trade at next open
k = pd.read_csv(os.path.join(os.path.dirname(HERE), "daily_signal_dca", "from_2025", "data", "BTCUSDT_1d_from2025.csv.gz"))
w = (k.c > k.c.rolling(50).mean()).astype(float).values
eq, prev, curve = 1.0, 0.0, []
for i in range(len(k) - 2):
    eq *= (1 - abs(w[i] - prev) * 0.001) * (1 + w[i] * (k.o[i + 2] / k.o[i + 1] - 1)); prev = w[i]; curve.append(eq)
dates = pd.to_datetime(k.t, unit="ms")[1:len(curve) + 1].reset_index(drop=True)
c = np.array(curve)[(dates >= "2025-02-20").values]; btc_net = c[-1] / c[0] * 1 - 1
first = np.array(curve)[(dates >= "2025-02-20").values]
out = {
    "gold_G_MOM50_ATR_x1": dict(independent=round(float(gold_net), 4), recorded=rec["gold"]["results"]["G_MOM50_ATR|x1"]["rule"]["net"]),
    "oil_O_INTRADAY_x1": dict(independent=round(float(oil_net), 4), recorded=rec["oil"]["results"]["O_INTRADAY|x1"]["rule"]["net"], trades_independent=len(rets),
                              trades_recorded=rec["oil"]["results"]["O_INTRADAY|x1"]["rule"]["trades"]),
    "btc_C_SMA50_x1": dict(independent=round(float(btc_net), 4), recorded=rec["crypto"]["BTCUSDT|C_SMA50|x1"]["net"]),
}
for v in out.values(): v["abs_diff"] = round(abs(v["independent"] - v["recorded"]), 4); v["match_within_1pt"] = v["abs_diff"] <= 0.01
json.dump(out, open(os.path.join(HERE, "results", "independent_check.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
