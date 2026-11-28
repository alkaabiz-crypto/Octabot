"""TradingView batch 003 (PREREG.md). Part A: 13 indicators through IND batch 001's IC machinery (unchanged).
Part B: 10 double/triple combinations, common ATR management on 1h candles, random-entry benchmark.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_tv3.py
"""
import json, math, os, sys
import numpy as np, pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("ind_batch_001", "src"): sys.path.insert(0, os.path.join(ND, p))
import run_ind as RI, common as C  # noqa: E401,E402
RB = RI.RB; ema, sma, atr, rsi = RI.ema, RI.sma, RI.atr, RI.rsi
P = RI.P; SL, TP, HOLD = 1.5, 3.0, 48


def wma(x, n): w = np.arange(1, n + 1); return x.rolling(n).apply(lambda v: (v * w).sum() / w.sum(), raw=True)
def linreg(x, n):
    t = np.arange(n); tm = t.mean(); den = ((t - tm) ** 2).sum()
    return x.rolling(n).apply(lambda v: v.mean() + ((t - tm) * (v - v.mean())).sum() / den * (n - 1 - tm), raw=True)
def cross_up(a, b): return (a > b) & (a.shift() <= b.shift())


def trail_state(c, stop_long, stop_short):
    """generic ATR trailing state (UT Bot / Chandelier style): +1 above trailing stop, -1 below."""
    n = len(c); d = np.zeros(n); tr = np.full(n, np.nan)
    for i in range(1, n):
        if np.isnan(stop_long[i]): continue
        if np.isnan(tr[i - 1]): tr[i] = stop_long[i]; d[i] = 1; continue
        if d[i - 1] >= 0:
            tr[i] = max(tr[i - 1], stop_long[i]) if c[i] > tr[i - 1] else stop_short[i]; d[i] = 1 if c[i] > tr[i - 1] else -1
        else:
            tr[i] = min(tr[i - 1], stop_short[i]) if c[i] < tr[i - 1] else stop_long[i]; d[i] = -1 if c[i] < tr[i - 1] else 1
    return d, tr


def base(df):
    c, h, l = df.c, df.h, df.l; A = atr(df); Z = dict(A=A)
    hh, ll = h.rolling(20).max(), l.rolling(20).min(); mid = sma(c, 20); sd = c.rolling(20).std(); a20 = atr(df, 20)
    Z["sqz_mom"] = linreg(c - ((hh + ll) / 2 + mid) / 2, 20); Z["sqz_on"] = (mid - 2 * sd > mid - 1.5 * a20) & (mid + 2 * sd < mid + 1.5 * a20)
    ap = (h + l + c) / 3; esa = ema(ap, 10); dd = ema((ap - esa).abs(), 10); wt1 = ema((ap - esa) / (0.015 * dd), 21); Z["wt1"], Z["wt2"] = wt1, sma(wt1, 4)
    r6 = ema(rsi(c, 6), 5); dar = ema(ema(r6.diff().abs(), 27), 27) * 4.236; rv, dv = r6.values, dar.values; tl = np.full(len(c), np.nan)
    for i in range(1, len(c)):
        if np.isnan(dv[i]): continue
        p = tl[i - 1] if not np.isnan(tl[i - 1]) else rv[i]; lo, hi = rv[i] - dv[i], rv[i] + dv[i]
        tl[i] = max(p, lo) if (rv[i - 1] > p and rv[i] > p) else (min(p, hi) if (rv[i - 1] < p and rv[i] < p) else (lo if rv[i] > p else hi))
    Z["qqe"] = r6 - tl
    sh, sl_ = sma(h, 10), sma(l, 10); hl = np.where(c > sh, 1, np.where(c < sl_, -1, 0)).astype(float)
    for i in range(1, len(hl)):
        if hl[i] == 0: hl[i] = hl[i - 1]
    Z["ssl"] = pd.Series(hl, index=df.index)
    a10 = atr(df, 10).values; d, tr = trail_state(c.values, c.values - a10, c.values + a10); Z["ut"] = pd.Series(d, index=df.index); Z["ut_tr"] = pd.Series(tr, index=df.index)
    a22 = 3 * atr(df, 22).values; d2, _ = trail_state(c.values, h.rolling(22).max().values - a22, l.rolling(22).min().values + a22); Z["chand"] = pd.Series(d2, index=df.index)
    m = ema(c, 23) - ema(c, 50); st = lambda x: 100 * (x - x.rolling(10).min()) / (x.rolling(10).max() - x.rolling(10).min())
    Z["stc"] = st(st(m).ewm(alpha=0.5, adjust=False).mean()).ewm(alpha=0.5, adjust=False).mean()
    Z["mid"], Z["bbl"], Z["bbu"] = mid, mid - 2 * sd, mid + 2 * sd
    Z["macd"] = ema(c, 12) - ema(c, 26); Z["macds"] = ema(Z["macd"], 9); Z["rsi"] = rsi(c)
    k = 100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min()); Z["sk"] = k.rolling(3).mean(); Z["sd"] = Z["sk"].rolling(3).mean()
    tp = (h + l + c) / 3; Z["vwap"] = tp.groupby(df.index.floor("D")).expanding().mean().reset_index(level=0, drop=True)
    Z["st"] = RI.supertrend(df)
    return Z


def indicators3(df, Z):
    c, h, l = df.c, df.h, df.l; A = Z["A"]; X = {}
    X["IND-036"] = Z["sqz_mom"] / A; X["IND-037"] = Z["wt1"] - Z["wt2"]; X["IND-038"] = Z["qqe"]; X["IND-039"] = Z["ssl"]; X["IND-040"] = Z["ut"]; X["IND-041"] = Z["chand"]
    X["IND-042"] = Z["stc"] - 50; roc = lambda n: 100 * (c / c.shift(n) - 1); X["IND-043"] = wma(roc(14) + roc(11), 10)
    X["IND-044"] = (c.shift(11) - sma(c, 20)) / A
    lsma = linreg(c, 50); X["IND-045"] = np.log(lsma / lsma.shift())
    d = np.sign(c.diff()).values; streak = np.zeros(len(c))
    for i in range(1, len(c)): streak[i] = (streak[i - 1] + d[i] if np.sign(streak[i - 1]) == d[i] and d[i] != 0 else d[i])
    pr = c.pct_change().rolling(101).apply(lambda v: (v[:-1] < v[-1]).mean() * 100, raw=True)
    X["IND-046"] = (rsi(c, 3) + rsi(pd.Series(streak, index=c.index), 2) + pr) / 3 - 50
    g = 0.5; cv = c.values; L = np.zeros((4, len(c))); lr = np.full(len(c), np.nan)
    for i in range(1, len(c)):
        L[0, i] = (1 - g) * cv[i] + g * L[0, i - 1]; L[1, i] = -g * L[0, i] + L[0, i - 1] + g * L[1, i - 1]
        L[2, i] = -g * L[1, i] + L[1, i - 1] + g * L[2, i - 1]; L[3, i] = -g * L[2, i] + L[2, i - 1] + g * L[3, i - 1]
        cu = max(L[0, i] - L[1, i], 0) + max(L[1, i] - L[2, i], 0) + max(L[2, i] - L[3, i], 0); cd = max(L[1, i] - L[0, i], 0) + max(L[2, i] - L[1, i], 0) + max(L[3, i] - L[2, i], 0)
        lr[i] = cu / (cu + cd) if cu + cd > 0 else 0.5
    X["IND-047"] = pd.Series(lr, index=c.index) - 0.5; X["IND-047"].iloc[:50] = np.nan
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    chop = 100 * np.log10(tr.rolling(14).sum() / (h.rolling(14).max() - l.rolling(14).min())) / np.log10(14)
    X["IND-048"] = roc(12) * (chop < 38.2)
    return X


def combos(df, Z):
    c = df.c; e9, e21, e50, e200 = ema(c, 9), ema(c, 21), ema(c, 50), ema(c, 200); hist = Z["macd"] - Z["macds"]; r = Z["rsi"]; S = {}
    def both(L, Sh): return L.fillna(False).astype(bool), Sh.fillna(False).astype(bool)
    S["STR-028a"] = both(cross_up(e9, e21) & (r > 50) & (hist > 0), cross_up(e21, e9) & (r < 50) & (hist < 0))
    S["STR-028b"] = both(cross_up(c, e9) & (c > Z["vwap"]) & (r > 50), cross_up(e9, c) & (c < Z["vwap"]) & (r < 50))
    S["STR-028c"] = both(cross_up(Z["macd"], Z["macds"]) & (c > Z["mid"]), cross_up(Z["macds"], Z["macd"]) & (c < Z["mid"]))
    off = (~Z["sqz_on"]) & Z["sqz_on"].shift(fill_value=False)
    S["STR-028d"] = both(off & (Z["sqz_mom"] > 0) & (c > e200), off & (Z["sqz_mom"] < 0) & (c < e200))
    S["STR-028e"] = both(cross_up(Z["wt1"], Z["wt2"]) & (Z["wt1"] < 0) & (Z["ssl"] > 0), cross_up(Z["wt2"], Z["wt1"]) & (Z["wt1"] > 0) & (Z["ssl"] < 0))
    flip_ut = Z["ut"].diff()
    S["STR-028f"] = both((flip_ut > 0) & (c > e200), (flip_ut < 0) & (c < e200))
    fst = Z["st"].diff()
    S["STR-028g"] = both((fst > 0) & (r > 50) & (c > e200), (fst < 0) & (r < 50) & (c < e200))
    S["STR-028h"] = both(cross_up(Z["sk"], Z["sd"]) & (hist > 0) & (r > 50), cross_up(Z["sd"], Z["sk"]) & (hist < 0) & (r < 50))
    lo, hi = (c < Z["bbl"]) & (r < 30), (c > Z["bbu"]) & (r > 70)
    S["STR-028i"] = both(lo & ~lo.shift(fill_value=False), hi & ~hi.shift(fill_value=False))
    S["STR-028j"] = both(cross_up(e50, e200) & (Z["macd"] > 0), cross_up(e200, e50) & (Z["macd"] < 0))
    return S


@njit(cache=True)
def manage(o, h, l, c, i, side, a, hold):
    """entry at o[i]; stop SL*a, target TP*a; stop first; gap through stop fills at open. Returns (R gross, exit index)."""
    e = o[i]; risk = 1.5 * a; stop = e - side * risk; tgt = e + side * 3.0 * a; end = min(i + hold - 1, len(o) - 1)
    for k in range(i, end + 1):
        if (k > i) and (o[k] - stop) * side <= 0: return (o[k] - e) * side / risk, k
        if ((l[k] if side > 0 else h[k]) - stop) * side <= 0: return -1.0, k
        if ((h[k] if side > 0 else l[k]) - tgt) * side >= 0: return 2.0, k
    return (c[end] - e) * side / risk, end


def run_combo(df, A, L, S, cost):
    o, h, l, c, a = df.o.values, df.h.values, df.l.values, df.c.values, A.values; Lv, Sv = L.values, S.values; out = []; i = 1; n = len(o)
    while i < n - 1:
        j = i - 1                                                     # signal at close of j, entry at open of i
        side = 1 if Lv[j] else (-1 if Sv[j] else 0)
        if side and not np.isnan(a[j]) and a[j] > 0:
            rg, x = manage(o, h, l, c, i, side, a[j], HOLD); f = 1.5 * a[j] / o[i]
            out.append(dict(t=df.index[i], side=side, j=j, r=rg - cost / f, rs=rg - 2 * cost / f, f=f)); i = x + 1; continue
        i += 1
    return out


def bench(df, A, sel, cost, lo, hi, rng, sets=1000, per=40):
    o, h, l, c, a = df.o.values, df.h.values, df.l.values, df.c.values, A.values; idx = df.index
    pool = np.flatnonzero((idx >= lo) & (idx < hi) & ~np.isnan(np.r_[np.nan, a[:-1]])); pool = pool[pool < len(o) - HOLD]; sims = np.empty((len(sel), per))
    for u, tr in enumerate(sel):
        for b in range(per):
            i = int(pool[rng.integers(len(pool))]); rg, _ = manage(o, h, l, c, i, tr["side"], a[i - 1], HOLD); sims[u, b] = rg - cost / (1.5 * a[i - 1] / o[i])
    pick = rng.integers(per, size=(sets, len(sel))); m = sims[np.arange(len(sel)), pick].mean(axis=1); act = np.mean([x["r"] for x in sel])
    return float((m >= act).mean()), float(m.mean())


def bounds(df):
    per = pd.Series([RB.period(t) for t in df.index], index=df.index); return {p: (per.index[per == p][0], per.index[per == p][-1] + pd.Timedelta(hours=1)) for p in P if (per == p).any()}, per


def main():
    R, IC = {}, {}; rng = np.random.default_rng(3028)
    for m in RI.MKTS:
        d15 = RB.load(m); cost = 1.5 * RB.spread_frac(d15); df = RI.hourly(m); Z = base(df)
        for k, x in indicators3(df, Z).items(): IC[f"{k}|{m}"] = RI.ic_tests(x, df, k)
        B, per = bounds(df)
        for sid, (L, S) in combos(df, Z).items():
            tr = run_combo(df, Z["A"], L, S, cost); res = {}
            for p in P:
                sel = [x for x in tr if per[x["t"]] == p]
                if not sel: res[p] = dict(trades=0); continue
                r = np.array([x["r"] for x in sel]); rs = np.array([x["rs"] for x in sel])
                q = dict(trades=len(sel), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1))
                if p == "TEST" and len(sel) >= 10: q["p_random"], q["random_mean_R"] = bench(df, Z["A"], sel, cost, *B[p], rng); q["random_mean_R"] = round(q["random_mean_R"], 4)
                res[p] = q
            R[f"{sid}|{m}"] = dict(cost=cost, results=res)
        print(m, "done", {k.split("|")[0]: (v["results"]["TEST"].get("trades"), v["results"]["TEST"].get("mean_R"), v["results"]["TEST"].get("p_random")) for k, v in R.items() if k.endswith(m)}, flush=True)
    keys = list(R); sig = C.bh([R[k]["results"]["TEST"].get("p_random", 1.0) for k in keys])
    for i, k in enumerate(keys):
        f = R[k]["results"]; te = f["TEST"]; av = [p for p in P if f[p].get("trades", 0) > 0]; pos = bool(av) and all(f[p]["mean_R"] > 0 for p in av)
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
    ik = [(k, h) for k, v in IC.items() for h, r in v.items() if "TEST" in r]; isig = C.bh([IC[k][h]["TEST"]["p"] for k, h in ik])
    for i, (k, h) in enumerate(ik): IC[k][h]["TEST"]["bh"] = i in isig
    verdict = {}; order = ["NONE", "WEAK", "REDUNDANT", "INFORMATIVE"]
    for ind in sorted({k.split("|")[0] for k in IC}):
        best, detail = "NONE", []
        for h in sorted({hh for k in IC if k.startswith(ind + "|") for hh in IC[k]}):
            mk = [k for k in IC if k.startswith(ind + "|") and h in IC[k] and "TEST" in IC[k][h]]
            pos = [k for k in mk if all(v["ic"] > 0 for v in IC[k][h].values())]
            bhs = [k for k in pos if IC[k][h]["TEST"].get("bh")]; part = [k for k in bhs if IC[k][h]["TEST"].get("partial_p", 1) <= 0.05]
            v = "INFORMATIVE" if (len(pos) >= 3 and part) else ("REDUNDANT" if bhs and not part else ("WEAK" if len(pos) >= 3 else "NONE"))
            detail.append(dict(h=h, markets_positive_every_period=[k.split("|")[1] for k in pos], bh_test=[k.split("|")[1] for k in bhs], verdict=v)); best = max(best, v, key=order.index)
        neg = [(k.split("|")[1], h) for k in IC if k.startswith(ind + "|") for h in IC[k] if "TEST" in IC[k][h] and len(IC[k][h]) >= 3 and all(v["ic"] < 0 for v in IC[k][h].values())]
        verdict[ind] = dict(verdict=best, by_horizon=detail, consistently_negative=neg)
    json.dump(dict(n_ic_test_tests=len(ik), n_combo_tests=len(keys), verdicts=verdict, combos=R, ic=IC), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    for ind, v in verdict.items(): print(ind, v["verdict"], [(d["h"], d["markets_positive_every_period"]) for d in v["by_horizon"] if d["markets_positive_every_period"]], "| neg:", v["consistently_negative"][:5])
    for k in keys: print(k, R[k]["decision"], {p: (v.get("trades"), v.get("mean_R")) for p, v in R[k]["results"].items()}, R[k]["results"]["TEST"].get("p_random"))


if __name__ == "__main__":
    main()
