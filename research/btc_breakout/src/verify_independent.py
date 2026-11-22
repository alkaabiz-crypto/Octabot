"""Independent re-implementation (pandas/numpy, written separately from engine.py) of the 3 holdout survivors:
1H long, 4H close > EMA200, trailing stop (2 ATR initial, highest close - 3 ATR), entry next 15m open, stop-first.
Compares trade-by-trade with engine.py, then runs a truncation (repainting) test."""
import json, os, random, sys
import numpy as np, pandas as pd
ROOT = os.path.join(os.path.dirname(__file__), ".."); sys.path.insert(0, os.path.dirname(__file__))
from protocol import WINDOWS, HOLDOUT
def load(tf):
    a = np.array(json.load(open(f"{ROOT}/data/btc_{tf}.json"))); return pd.DataFrame(a[:, :6], columns=list("tohlcv")).astype({"t": "int64"})
h1, h4, m15 = load("1h"), load("4h"), load("15m")
def wilder(x, n):
    x = np.asarray(x, float); out = np.full(len(x), np.nan); out[n - 1] = x[:n].mean()
    for i in range(n, len(x)): out[i] = (out[i - 1] * (n - 1) + x[i]) / n
    return out
prev_c = h1.c.shift(1)
tr = np.maximum.reduce([(h1.h - h1.l).to_numpy(), (h1.h - prev_c).abs().fillna(0).to_numpy(), (h1.l - prev_c).abs().fillna(0).to_numpy()]); tr[0] = h1.h[0] - h1.l[0]
atr14 = wilder(tr, 14)
h4["e200"] = h4.c.ewm(span=200, adjust=False).mean()
hh20 = h1.h.rolling(20).max().shift(1).to_numpy()
vavg = h1.v.rolling(20).mean().shift(1).to_numpy()
sma = h1.c.rolling(20).mean(); sd = h1.c.rolling(20).std(ddof=0); upper = (sma + 2 * sd).to_numpy(); bw = (4 * sd / sma).to_numpy()
bwpct = pd.Series(bw).rolling(120).apply(lambda w: (w <= w[-1]).mean(), raw=True).to_numpy()
c = h1.c.to_numpy(); n = len(c)
sig = {"M2_DONCHIAN20": np.zeros(n, bool), "M4_DONCHIAN_VOL": np.zeros(n, bool), "M1_BB_SQUEEZE": np.zeros(n, bool)}
for i in range(260, n):
    dc = c[i] > hh20[i] and c[i - 1] <= hh20[i - 1]
    sig["M2_DONCHIAN20"][i] = dc; sig["M4_DONCHIAN_VOL"][i] = dc and h1.v[i] > 1.5 * vavg[i]
    sq = np.nanmin(bwpct[i - 5:i]) <= 0.2 if not np.all(np.isnan(bwpct[i - 5:i])) else False
    sig["M1_BB_SQUEEZE"][i] = sq and c[i] > upper[i] and c[i - 1] <= upper[i - 1]
h4close = (h4.t + 14400).to_numpy(); e4 = h4.e200.to_numpy(); c4 = h4.c.to_numpy()
mt = m15.t.to_numpy(); mo, mh, ml, mc = (m15[k].to_numpy() for k in "ohlc"); mpos = {t: i for i, t in enumerate(mt)}
t1 = h1.t.to_numpy(); t1close = t1 + 3600
def run(model, w0, w1):
    out, i = [], 260
    while i < n and t1[i] < w1:
        if t1[i] < w0 or not sig[model][i]: i += 1; continue
        k = np.searchsorted(h4close, t1close[i], side="right") - 1
        if not c4[k] > e4[k]: i += 1; continue
        j = mpos.get(t1close[i])
        if j is None or mt[j] >= w1: i += 1; continue
        e = mo[j]; sl = e - 2 * atr14[i]; r = e - sl; best = e
        while True:
            if ml[j] <= sl: px = mo[j] if mo[j] < sl else sl; R = (px - e) / r; break
            bc = mt[j] + 900
            if bc % 3600 == 0:
                kk = np.searchsorted(t1close, bc, side="right") - 1; best = max(best, mc[j]); sl = max(sl, best - 3 * atr14[kk])
            if bc >= w1: R = (mc[j] - e) / r; break
            j += 1
            if j >= len(mt): j -= 1; R = (mc[j] - e) / r; break
        out.append((int(t1close[i]), round(R, 6)))
        i = np.searchsorted(t1close, mt[j] + 900, side="right") - 1 + 1
    return out
from engine import Lab
L = Lab(f"{ROOT}/data"); ok_all = True
for model in ("M1_BB_SQUEEZE", "M2_DONCHIAN20", "M4_DONCHIAN_VOL"):
    a, b = [], []
    for _, w0, w1 in WINDOWS + [HOLDOUT]:
        a += [(t["entry_time"], round(t["R_gross"], 6)) for t in L.simulate("1h", model, 1, "TRAIL", w0, w1)]; b += run(model, w0, w1)
    da, db = dict(a), dict(b); mism = len(set(da) ^ set(db)) + sum(1 for t in set(da) & set(db) if abs(da[t] - db[t]) > 1e-4)
    ok_all &= mism == 0
    print(f"{model:16} engine: {len(a)} trades, sum R {sum(x[1] for x in a):.4f} | independent: {len(b)} trades, sum R {sum(x[1] for x in b):.4f} | mismatches: {mism}")
# truncation / repainting test on signals and 4H filter
import engine
random.seed(11); raw1 = json.load(open(f"{ROOT}/data/btc_1h.json"))
cands = [i for i in range(3000, len(raw1)) if any(L.signals("1h", m, 1)[i] for m in ("M1_BB_SQUEEZE", "M2_DONCHIAN20", "M4_DONCHIAN_VOL"))]
sample = random.sample(cands, 20) + random.sample(range(3000, len(raw1)), 20); diffs = 0
for i in sample:
    Lt = Lab.__new__(Lab); Lt.B = {"1h": engine.build(raw1[:i + 1])}; Lt.sig_cache = {}
    for m in ("M1_BB_SQUEEZE", "M2_DONCHIAN20", "M4_DONCHIAN_VOL"):
        if Lt.signals("1h", m, 1)[i] != L.signals("1h", m, 1)[i]: diffs += 1
    if abs(Lt.B["1h"]["atr"][i] - L.B["1h"]["atr"][i]) > 1e-9: diffs += 1
print(f"truncation test: {len(sample)} bars x 3 signals + ATR recomputed on history up to that bar -> differences: {diffs}")
print("INDEPENDENT VERIFICATION:", "PASS" if ok_all and diffs == 0 else "FAIL")
