"""V1 of VERIFY_PREREG.md: independent minute-by-minute re-implementation of B9 (Fibonacci pullback) and D4 (FVG fill).
Written separately from theories.py / engine.py. Signals come from 1h candles built here from 1-minute bars; fills and exits
are simulated minute by minute. A limit order fills only if the minute low (buy) trades at least one full spread below
the limit (Exness: that minute's spread; Binance: 1 bp), at the limit price. Target limits need the same penetration.

Usage: BARS_DIR=<exness 1m> BIN_DIR=<binance 1m> python3 -I verify_minute.py
"""
import json, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); BARS = os.environ["BARS_DIR"]; BIN = os.environ["BIN_DIR"]
HOLD_MS = 1767225600000; FEE = 0.0005


def load(mkt):
    if mkt.endswith("USDT"):
        z = np.load(os.path.join(BIN, f"{mkt}_1m.npz")); m, o, h, l, c = z["m"], z["o"], z["h"], z["l"], z["c"]
        hs = o * FEE; pen = o * 1e-4
    else:
        z = np.load(os.path.join(BARS, f"{mkt}_1m.npz")); m, o, h, l, c = z["m"], z["o"], z["h"], z["l"], z["c"]; hs = z["sp"] / 2; pen = z["sp"]
    assert m[0] * 60000 >= 1735689600000
    hr = m // 60; st = np.flatnonzero(np.r_[True, hr[1:] != hr[:-1]]); en = np.r_[st[1:], len(m)]
    H = dict(o=o[st], h=np.maximum.reduceat(h, st), l=np.minimum.reduceat(l, st), c=c[en - 1], s=st, e=en, hr=hr[st])
    return dict(m=m, o=o, h=h, l=l, c=c, hs=hs, pen=pen), H


def run_limit(M, Hc, k_from, k_to, side, lim, stop, tp, tmax_hours):
    """Limit order active over 1h candles [k_from, k_to); then minute management. Returns (fill_min, exit_min, entry, exit) or None."""
    a = Hc["s"][k_from]; b = Hc["e"][min(k_to, len(Hc["s"])) - 1]
    lo, hi, pen = M["l"][a:b], M["h"][a:b], M["pen"][a:b]
    hit = np.flatnonzero(lo <= lim - pen) if side > 0 else np.flatnonzero(hi >= lim + pen)
    if not len(hit): return None
    f = a + hit[0]; pe = min(M["o"][f], lim) if side > 0 else max(M["o"][f], lim)
    fill_hour = np.searchsorted(Hc["s"], f, side="right") - 1; last_k = min(fill_hour + tmax_hours, len(Hc["s"]) - 1); end = Hc["e"][last_k]
    for q in range(f, end):
        if q > f and ((side > 0 and M["o"][q] <= stop) or (side < 0 and M["o"][q] >= stop)): return f, q, pe, M["o"][q]
        if (side > 0 and M["l"][q] <= stop) or (side < 0 and M["h"][q] >= stop): return f, q, pe, stop
        if q > f and ((side > 0 and M["h"][q] >= tp + M["pen"][q]) or (side < 0 and M["l"][q] <= tp - M["pen"][q])): return f, q, pe, tp
    return f, end - 1, pe, M["c"][end - 1]


def sma(x, n):
    out = np.full(len(x), np.nan); cs = np.cumsum(np.r_[0, x]); out[n - 1:] = (cs[n:] - cs[:-n]) / n; return out


def b9(M, Hc, fib=0.618, look=20):
    o, h, l, c = Hc["o"], Hc["h"], Hc["l"], Hc["c"]; s50 = sma(c, 50); out = []; i = 50
    while i < len(c) - 2:
        hh, ll = h[i - look + 1:i + 1], l[i - look + 1:i + 1]; ih, il = int(np.argmax(hh)), int(np.argmin(ll)); Hh, Ll = hh[ih], ll[il]
        side = 1 if (c[i] > s50[i] and ih > il) else (-1 if (c[i] < s50[i] and il > ih) else 0)
        if side == 0 or Hh <= Ll: i += 1; continue
        lim = Hh - fib * (Hh - Ll) if side > 0 else Ll + fib * (Hh - Ll); stop, tp = (Ll, Hh) if side > 0 else (Hh, Ll)
        r = run_limit(M, Hc, i + 1, i + 11, side, lim, stop, tp, 20)
        if r is None: i += 1; continue
        out.append((side,) + r); i = int(np.searchsorted(Hc["s"], r[1], side="right") - 1) + 1
    return out


def d4(M, Hc):
    h, l = Hc["h"], Hc["l"]; out = []; i = 2
    while i < len(h) - 1:
        side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
        if not side: i += 1; continue
        lim = h[i - 2] if side > 0 else l[i - 2]; stop = l[i - 2] if side > 0 else h[i - 2]; R = side * (lim - stop)
        if R <= 0: i += 1; continue
        r = run_limit(M, Hc, i + 1, i + 11, side, lim, stop, lim + side * 2 * R, 20)
        if r is None: i += 1; continue
        out.append((side,) + r); i = int(np.searchsorted(Hc["s"], r[1], side="right") - 1) + 1
    return out


def score(M, trades, mult):
    res = {"dev": [], "holdout": []}
    for side, f, x, pe, px in trades:
        net = side * (px - pe) / pe - mult * (M["hs"][f] + M["hs"][x]) / pe
        res["holdout" if M["m"][f] * 60000 >= HOLD_MS else "dev"].append(net)
    return {p: dict(trades=len(v), mean_bp=round(float(np.mean(v) * 1e4), 2) if v else None, win=round(float(np.mean(np.array(v) > 0)), 3) if v else None) for p, v in res.items()}


def main():
    t0 = time.time(); out = {}
    for tid, mkt, fn in (("B9", "USOILm", b9), ("B9", "ETHUSDT", b9), ("D4", "XAUUSDm", d4)):
        M, Hc = load(mkt); tr = fn(M, Hc); s1, s2 = score(M, tr, 1), score(M, tr, 2)
        ok = s2["dev"]["mean_bp"] is not None and s2["holdout"]["mean_bp"] is not None and s2["dev"]["mean_bp"] > 0 and s2["holdout"]["mean_bp"] > 0
        big = ok and s2["dev"]["mean_bp"] >= 2 and s2["holdout"]["mean_bp"] >= 2
        out[f"{tid}|{mkt}|1h"] = dict(x1=s1, x2=s2, V1="PASS" if ok else "FAIL", V3="PASS" if big else "FAIL")
        print(tid, mkt, out[f"{tid}|{mkt}|1h"], f"{time.time() - t0:.0f}s", flush=True)
    json.dump(out, open(os.path.join(HERE, "results", "verify_minute.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
