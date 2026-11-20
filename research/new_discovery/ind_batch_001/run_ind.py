"""Indicator information test, batch IND-001 (PREREG.md). Spearman IC of each indicator (oriented: higher = bullish) with
non-overlapping forward returns; partial IC controlling for the past return over the same horizon; BH across all TEST tests.
usage: DISCOVERY_DATA=<scratch with long/ and multi/bars/> B003_DATA=<b003data> python3 -I run_ind.py
"""
import json, math, os, sys
import numpy as np, pandas as pd


def rankdata(a): return pd.Series(np.asarray(a, float)).rank().values


def spearmanr(a, b): return (float(np.corrcoef(rankdata(a), rankdata(b))[0, 1]), None)

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ND, "batch_003")); sys.path.insert(0, os.path.join(ND, "src"))
import run_batch as RB, common as C  # noqa: E401,E402

MKTS = ["XAUUSDm", "USOILm", "BTCUSDm", "US500m", "EURUSDm"]; HORIZ = [1, 4, 24, 120]; P = ["EARLY", "TRAIN", "VALIDATION", "TEST"]


def hourly(m):
    d = RB.load(m); g = d.groupby(d.index.floor("h"))
    return pd.DataFrame(dict(o=g.mo.first(), h=g.mh.max(), l=g.ml.min(), c=g.mc.last()))


def ema(x, n): return x.ewm(span=n, adjust=False).mean()
def sma(x, n): return x.rolling(n).mean()


def atr(df, n=14):
    tr = pd.concat([df.h - df.l, (df.h - df.c.shift()).abs(), (df.l - df.c.shift()).abs()], axis=1).max(axis=1); return tr.ewm(alpha=1 / n, adjust=False).mean()


def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean(); return 100 - 100 / (1 + up / dn)


def supertrend(df, n=10, k=3.0):
    a = atr(df, n).values; hl2 = ((df.h + df.l) / 2).values; c = df.c.values; N = len(c); ub, lb = hl2 + k * a, hl2 - k * a; fu, fl = ub.copy(), lb.copy(); d = np.ones(N)
    for i in range(1, N):
        fu[i] = ub[i] if (ub[i] < fu[i - 1] or c[i - 1] > fu[i - 1]) else fu[i - 1]; fl[i] = lb[i] if (lb[i] > fl[i - 1] or c[i - 1] < fl[i - 1]) else fl[i - 1]
        d[i] = 1 if c[i] > fu[i - 1] else (-1 if c[i] < fl[i - 1] else d[i - 1])
    d[:n] = np.nan; return pd.Series(d, index=df.index)


def psar(df, step=0.02, mx=0.2):
    h, l = df.h.values, df.l.values; n = len(h); s = np.zeros(n); up = True; af = step; ep = h[0]; s[0] = l[0]; side = np.ones(n)
    for i in range(1, n):
        s[i] = s[i - 1] + af * (ep - s[i - 1])
        if up:
            s[i] = min(s[i], l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < s[i]: up, s[i], ep, af = False, ep, l[i], step
            elif h[i] > ep: ep, af = h[i], min(af + step, mx)
        else:
            s[i] = max(s[i], h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > s[i]: up, s[i], ep, af = True, ep, h[i], step
            elif l[i] < ep: ep, af = l[i], min(af + step, mx)
        side[i] = 1 if up else -1
    return pd.Series(side, index=df.index)


def indicators(df):
    c, h, l = df.c, df.h, df.l; A = atr(df); X = {}
    roc = lambda n: 100 * (c / c.shift(n) - 1); kst = sma(roc(10), 10) + 2 * sma(roc(15), 10) + 3 * sma(roc(20), 10) + 4 * sma(roc(30), 15); X["IND-003"] = kst - sma(kst, 9)
    tp = (h + l + c) / 3; X["IND-004"] = (c - tp.groupby(df.index.floor("D")).expanding().mean().reset_index(level=0, drop=True)) / A
    X["IND-005"] = rsi(c) - 50
    mac = ema(c, 12) - ema(c, 26); X["IND-006"] = (mac - ema(mac, 9)) / c
    X["IND-007"] = np.log(ema(c, 9) / ema(c, 21)); X["IND-008"] = supertrend(df); X["IND-009"] = psar(df)
    up, dn = h.diff(), -l.diff(); pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index); mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    pdi = 100 * pdm.ewm(alpha=1 / 14, adjust=False).mean() / A; mdi = 100 * mdm.ewm(alpha=1 / 14, adjust=False).mean() / A
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean(); X["IND-010"] = adx * np.sign(pdi - mdi)
    hh, ll = h.rolling(20).max(), l.rolling(20).min(); X["IND-011"] = (c - ll) / (hh - ll) - 0.5
    ten = (h.rolling(9).max() + l.rolling(9).min()) / 2; kij = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((ten + kij) / 2).shift(26); sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26); X["IND-012"] = (c - (sa + sb) / 2) / A
    mid, sd = sma(c, 20), c.rolling(20).std(); X["IND-013"] = (c - (mid - 2 * sd)) / (4 * sd) - 0.5
    X["IND-014"] = (100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min())).rolling(3).mean() - 50
    tpm = sma(tp, 20); md = tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True); X["IND-015"] = (tp - tpm) / (0.015 * md)
    X["IND-016"] = -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min()) + 50
    X["IND-017"] = -(100 * (c.rolling(22).max() - l) / c.rolling(22).max())
    X["IND-020"] = np.log(c / c.shift(20))
    return X


def ic_tests(x, df, key, rng=None):
    """IC per horizon and period; samples every h candles starting at the first valid value; target from the next open."""
    o = df.o.values; c = df.c.values; idx = df.index; out = {}
    for h in HORIZ:
        fwd = np.full(len(df), np.nan); fwd[:-h - 1] = np.log(o[h + 1:] / o[1:-h]) if len(df) > h + 1 else np.nan
        past = pd.Series(np.log(c / np.r_[np.full(h, np.nan), c[:-h]]), index=idx)
        frame = pd.DataFrame(dict(x=x.values, y=fwd, b=past.values), index=idx).dropna().iloc[::h]
        res = {}
        for p in P:
            f = frame[[RB.period(t) == p for t in frame.index]]
            if len(f) < 30: continue
            ic = spearmanr(f.x, f.y)[0]; n = len(f); t = ic * math.sqrt((n - 2) / max(1e-12, 1 - ic * ic))
            rx, rb, ry = rankdata(f.x), rankdata(f.b), rankdata(f.y)                      # partial IC: residualise ranks on the past return
            ex = rx - np.polyval(np.polyfit(rb, rx, 1), rb); ey = ry - np.polyval(np.polyfit(rb, ry, 1), rb); pic = float(np.corrcoef(ex, ey)[0, 1])
            pt = pic * math.sqrt((n - 3) / max(1e-12, 1 - pic * pic))
            res[p] = dict(n=n, ic=round(float(ic), 4), p=float(0.5 * math.erfc(t / math.sqrt(2))), partial_ic=round(pic, 4), partial_p=float(0.5 * math.erfc(pt / math.sqrt(2))))
        out[f"h{h}"] = res
    return out


def har_test(m):
    d = RB.load(m); lr = np.log(d.mc).diff(); key = (d.index - pd.Timedelta(hours=21)).floor("D")
    rv = lr.pow(2).groupby(key).sum(); rv = rv[rv > 0]; df = pd.DataFrame(dict(rv=rv)); df["rvw"], df["rvm"] = df.rv.rolling(5).mean(), df.rv.rolling(22).mean(); df["target"] = df.rv.shift(-1); df = df.dropna()
    fc = pd.Series(np.nan, index=df.index)
    for mo in pd.date_range(df.index[0] + pd.Timedelta(days=150), df.index[-1], freq="MS"):
        tr = df[df.index < mo - pd.Timedelta(days=1)]; te = df[(df.index >= mo) & (df.index < mo + pd.offsets.MonthBegin(1))]
        if len(tr) < 100 or te.empty: continue
        b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["rv", "rvw", "rvm"]].values], tr.target.values, rcond=None)[0]; fc[te.index] = np.c_[np.ones(len(te)), te[["rv", "rvw", "rvm"]].values] @ b
    df["fc"] = fc; df = df.dropna(); res = {}
    for p in P:
        f = df[[RB.period(t + pd.Timedelta(hours=21)) == p for t in df.index]]
        if len(f) < 30: continue
        ic = spearmanr(f.fc, f.target)[0]; n = len(f); t = ic * math.sqrt((n - 2) / max(1e-12, 1 - ic * ic))
        pic = spearmanr(f.fc - f.rv, f.target - f.rv)[0]                                    # beyond "tomorrow = today"
        res[p] = dict(n=n, ic=round(float(ic), 4), p=float(0.5 * math.erfc(t / math.sqrt(2))), partial_ic=round(float(pic), 4))
    return {"d1": res}


def main():
    R = {}
    cb = pd.read_csv(os.path.join(RB.B3, "coinbase_BTCUSD_1h.csv.gz")); bn = pd.read_csv(os.path.join(RB.B3, "binance_BTCUSDT_1h.csv.gz"))
    zz = cb.merge(bn, on="t").sort_values("t"); zz["z"] = (np.log(zz.cb / zz.bn) - np.log(zz.cb / zz.bn).rolling(720).mean().shift(1)) / np.log(zz.cb / zz.bn).rolling(720).std().shift(1)
    zz.index = pd.to_datetime(zz.t, unit="s", utc=True)
    for m in MKTS:
        df = hourly(m); X = indicators(df)
        for k, x in X.items(): R[f"{k}|{m}"] = ic_tests(x, df, k)
        if m == "BTCUSDm": R[f"IND-001|{m}"] = ic_tests(zz.z.reindex(df.index), df, "IND-001")
        R[f"IND-018|{m}"] = har_test(m); print(m, "done", flush=True)
    keys = [(k, h) for k, v in R.items() for h, r in v.items() if "TEST" in r]
    ps = [R[k][h]["TEST"]["p"] for k, h in keys]; sig = C.bh(ps)
    for i, (k, h) in enumerate(keys): R[k][h]["TEST"]["bh"] = i in sig
    verdict = {}
    for ind in sorted({k.split("|")[0] for k in R}):
        best = "NONE"; detail = []
        for h in (["d1"] if ind == "IND-018" else [f"h{x}" for x in HORIZ]):
            mk = [k for k in R if k.startswith(ind + "|") and h in R[k]]
            same = [k for k in mk if R[k][h] and all(np.sign(v["ic"]) == np.sign(R[k][h]["TEST"]["ic"]) for v in R[k][h].values()) and "TEST" in R[k][h]]
            pos = [k for k in same if R[k][h]["TEST"]["ic"] > 0]
            bhs = [k for k in pos if R[k][h]["TEST"].get("bh")]; part = [k for k in bhs if R[k][h]["TEST"].get("partial_p", 0) <= 0.05 or ind == "IND-018"]
            need = 1 if ind in ("IND-001",) else 3
            v = "INFORMATIVE" if (len(pos) >= need and part) else ("REDUNDANT" if bhs and not part else ("WEAK" if len(pos) >= need else "NONE"))
            detail.append(dict(h=h, markets_same_sign_positive=[k.split("|")[1] for k in pos], bh_test=[k.split("|")[1] for k in bhs], verdict=v))
            order = ["NONE", "WEAK", "REDUNDANT", "INFORMATIVE"]; best = max(best, v, key=order.index)
        verdict[ind] = dict(verdict=best, by_horizon=detail)
    out = dict(n_test_tests=len(keys), n_bh_significant=len(sig), verdicts=verdict, results=R)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print("TEST tests", len(keys), "BH significant", len(sig))
    for ind, v in verdict.items(): print(ind, v["verdict"], [(d["h"], d["markets_same_sign_positive"], d["bh_test"]) for d in v["by_horizon"] if d["verdict"] != "NONE"])


if __name__ == "__main__":
    main()
