"""TradingView batch 005 (PREREG.md): STR-030a-l (non-direction built-ins as rules) and STR-031a-j (3-5+ indicator combos).
Reuses batch 003's management/benchmark (run_tv3.run_combo / bench) and batch 004's indicator set, unchanged.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_tv5.py
"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("ind_batch_001", "ind_batch_002", "tv_batch_003", "tv_batch_004", "src"): sys.path.insert(0, os.path.join(ND, p))
import run_ind as RI, run_tv3 as T3, run_tv4 as T4, common as C  # noqa: E401,E402
RB = RI.RB; ema, sma, atr, rsi = RI.ema, RI.sma, RI.atr, RI.rsi; P = RI.P
TR0, TR1 = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-07-01", tz="UTC")


def first(x): x = x.fillna(False).astype(bool); return x & ~x.shift(fill_value=False)
def pair(L, S): return first(L), first(S)


def part_a_signals(df, X):
    o, h, l, c, v = df.o, df.h, df.l, df.c, df.v; A = atr(df); idx = df.index; S = {}
    S["STR-030a"] = (c > c.shift() + A.shift(), c < c.shift() - A.shift())
    mid, sd = sma(c, 20), c.rolling(20).std(); bbw = 4 * sd / mid; sq = (bbw <= bbw.rolling(120).min()).rolling(5).max().astype(bool)
    up, dn = mid + 2 * sd, mid - 2 * sd; S["STR-030b"] = (sq & T3.cross_up(c, up), sq & T3.cross_up(dn, c))
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    chop = 100 * np.log10(tr.rolling(14).sum() / (h.rolling(14).max() - l.rolling(14).min())) / np.log10(14)
    tr_ = T3.cross_up(pd.Series(38.2, index=idx), chop) & (chop.rolling(20).max() > 61.8); d14 = np.sign(c - c.shift(14))
    S["STR-030c"] = (tr_ & (d14 > 0), tr_ & (d14 < 0))
    e1 = ema(h - l, 9); mi = (e1 / ema(e1, 9)).rolling(25).sum(); bul = T3.cross_up(pd.Series(26.5, index=idx), mi) & (mi.rolling(10).max() > 27)
    e9 = ema(c, 9); sl9 = e9 - e9.shift(9); S["STR-030d"] = (bul & (sl9 < 0), bul & (sl9 > 0))
    spike = v > 2 * sma(v, 20).shift()
    S["STR-030e"] = (spike & (c > o), spike & (c < o)); S["STR-030f"] = (spike & (c < o), spike & (c > o))
    day = idx.floor("D"); dopen = o.groupby(day).transform("first"); drange = (h.groupby(day).max() - l.groupby(day).min()); adr = drange.rolling(14).mean().shift().reindex(day).values
    lo, hi = c < dopen - 1.5 * adr, c > dopen + 1.5 * adr
    S["STR-030g"] = (lo & ~lo.groupby(day).shift(fill_value=False).groupby(day).cummax(), hi & ~hi.groupby(day).shift(fill_value=False).groupby(day).cummax())
    lr = np.log(c).diff(); hv = lr.rolling(10).std() / lr.rolling(100).std(); calm = hv < 0.5
    S["STR-030h"] = (calm & (c > h.shift().rolling(20).max()), calm & (c < l.shift().rolling(20).min()))
    S["STR-030i"] = value_area(df)
    S["STR-030j"] = zigzag(df, A)
    return {k: tuple(first(z) for z in pr) for k, pr in S.items()}


def value_area(df):
    tp = (df.h + df.l + df.c) / 3; day = df.index.floor("D"); va = {}
    for dd, g in pd.DataFrame(dict(tp=tp, v=df.v)).groupby(day):
        g = g.sort_values("v", ascending=False); k = int(np.searchsorted(g.v.cumsum().values, 0.7 * g.v.sum())) + 1; s = g.iloc[:k]; va[dd] = (s.tp.min(), s.tp.max())
    days = sorted(va); prev = {days[i]: va[days[i - 1]] for i in range(1, len(days))}
    o, c = df.o.values, df.c.values; L = np.zeros(len(df), bool); S = np.zeros(len(df), bool); cur = None; fired = False; opn = None
    for i, t in enumerate(df.index):
        d = day[i]
        if d != cur: cur, fired, opn = d, False, o[i]
        if d not in prev or fired: continue
        val, vah = prev[d]
        if opn < val and val <= c[i] <= vah: L[i], fired = True, True
        elif opn > vah and val <= c[i] <= vah: S[i], fired = True, True
    return pd.Series(L, index=df.index), pd.Series(S, index=df.index)


def zigzag(df, A):
    c, a = df.c.values, A.values; n = len(c); L = np.zeros(n, bool); S = np.zeros(n, bool); up = True; ext = c[0]; sh = sl = np.nan
    for i in range(1, n):
        if np.isnan(a[i]): continue
        if up:
            if c[i] > ext: ext = c[i]
            elif c[i] < ext - 2 * a[i]: sh, up, ext = ext, False, c[i]
        else:
            if c[i] < ext: ext = c[i]
            elif c[i] > ext + 2 * a[i]: sl, up, ext = ext, True, c[i]
        L[i] = (not np.isnan(sh)) and c[i] > sh and c[i - 1] <= sh; S[i] = (not np.isnan(sl)) and c[i] < sl and c[i - 1] >= sl
    return pd.Series(L, index=df.index), pd.Series(S, index=df.index)


def zroll(x, n=500): return (x - x.rolling(n, min_periods=200).mean()) / x.rolling(n, min_periods=200).std()


def part_b_signals(df, X):
    c, v = df.c, df.v; A = atr(df); S = {}; e50, e200 = ema(c, 50), ema(c, 200); r = rsi(c); obv_up = X["IND-070"] > 0
    a_L = (e50 > e200) & T3.cross_up(r, pd.Series(50, index=c.index)) & obv_up; a_S = (e50 < e200) & T3.cross_up(pd.Series(50, index=c.index), r) & ~obv_up
    S["STR-031a"] = (a_L, a_S); adx = X["IND-010"]
    S["STR-031b"] = (a_L & (adx > 25), a_S & (adx < -25)); vw = X["IND-004"]
    S["STR-031c"] = (a_L & (adx > 25) & (vw > 0), a_S & (adx < -25) & (vw < 0))
    mid, sd = sma(c, 20), c.rolling(20).std(); bbw = sd / mid; rising = bbw > sma(bbw, 20)
    votes_L = [(X["IND-008"] > 0), (X["IND-006"] > 0), (X["IND-052"] > 0), rising, (X["IND-087"] > 0)]
    votes_S = [(X["IND-008"] < 0), (X["IND-006"] < 0), (X["IND-052"] < 0), rising, (X["IND-087"] < 0)]
    nL = sum(z.fillna(False).astype(int) for z in votes_L); nS = sum(z.fillna(False).astype(int) for z in votes_S)
    S["STR-031d"] = (nL == 5, nS == 5); S["STR-031f"] = (nL >= 4, nS >= 4)
    S["STR-031e"] = ((r < 30) & (X["IND-014"] < -30) & (X["IND-013"] < -0.5) & (X["IND-016"] < -30) & (X["IND-015"] < -100),
                     (r > 70) & (X["IND-014"] > 30) & (X["IND-013"] > 0.5) & (X["IND-016"] > 30) & (X["IND-015"] > 100))
    keys = sorted(k for k in X if k.startswith("IND-")); vote = sum(np.sign(X[k].astype(float)).fillna(0) for k in keys) / len(keys)
    S["STR-031g"] = (vote > 0.5, vote < -0.5)
    hi = c > df.h.shift().rolling(20).max(); lo = c < df.l.shift().rolling(20).min(); rv = v > 1.5 * sma(v, 20).shift()
    S["STR-031h"] = (hi & rv & (X["IND-068"] > 0), lo & rv & (X["IND-068"] < 0))
    o = df.o.values; tr_mask = (df.index >= TR0) & (df.index < TR1); sel = {}
    for name, hz in (("STR-031i", 4), ("STR-031j", 24)):
        fwd = np.full(len(df), np.nan); fwd[:-hz - 1] = np.log(o[hz + 1:] / o[1:-hz]); ics = []
        for k in keys:
            f = pd.DataFrame(dict(x=X[k].astype(float).values, y=fwd), index=df.index)[tr_mask].replace([np.inf, -np.inf], np.nan).dropna().iloc[::hz]
            if len(f) > 50 and f.x.nunique() > 1: ics.append((abs(np.corrcoef(f.x.rank(), f.y.rank())[0, 1]), np.sign(np.corrcoef(f.x.rank(), f.y.rank())[0, 1]), k))
        top = sorted(ics, reverse=True)[:5]; sel[name] = [(k, int(s)) for _, s, k in top]
        comp = sum(s * zroll(X[k].astype(float)) for _, s, k in top) / 5
        S[name] = (T3.cross_up(comp, pd.Series(1.0, index=c.index)), T3.cross_up(pd.Series(-1.0, index=c.index), comp))
    return {k: (z[0].fillna(False).astype(bool) if k in ("STR-031i", "STR-031j") else first(z[0]), z[1].fillna(False).astype(bool) if k in ("STR-031i", "STR-031j") else first(z[1])) for k, z in S.items()}, sel


def seasonality(df, cost):
    o = df.o.values; ret = pd.Series(np.r_[np.log(o[1:] / o[:-1]), np.nan], index=df.index); how = df.index.dayofweek * 24 + df.index.hour
    tr = ret[(df.index >= TR0) & (df.index < TR1)]; m = tr.groupby(how[(df.index >= TR0) & (df.index < TR1)]).mean()
    top, bot = set(m[m >= m.quantile(0.9)].index), set(m[m <= m.quantile(0.1)].index)
    side = np.where(np.isin(how, list(top)), 1, np.where(np.isin(how, list(bot)), -1, 0))
    r = pd.Series(side * ret.values * 1e4 - cost * 1e4, index=df.index)[side != 0].dropna(); return r


def moon(df, cost):
    syn = 29.530588853; ep = pd.Timestamp("2000-01-06 18:14", tz="UTC")
    day0 = df[df.index.hour == 0]; age = ((day0.index - ep) / pd.Timedelta(days=1)) % syn; ph = np.where((age < syn / 4) | (age >= 3 * syn / 4), 1, -1)
    sw = np.flatnonzero(np.r_[True, ph[1:] != ph[:-1]]); o = day0.o.values; out = []
    for a, b in zip(sw[:-1], sw[1:]): out.append((day0.index[a], ph[a] * np.log(o[b] / o[a]) * 1e4 - cost * 1e4))
    return pd.Series([x for _, x in out], index=[t for t, _ in out])


def evaluate(df, A, L, S, cost, rng):
    tr = T3.run_combo(df, A, L, S, cost); per = pd.Series([RB.period(t) for t in df.index], index=df.index); B, _ = T3.bounds(df); res = {}
    for p in P:
        sel = [x for x in tr if per[x["t"]] == p]
        if not sel: res[p] = dict(trades=0); continue
        r = np.array([x["r"] for x in sel]); rs = np.array([x["rs"] for x in sel])
        q = dict(trades=len(sel), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1))
        if p == "TEST" and len(sel) >= 10: q["p_random"], q["random_mean_R"] = T3.bench(df, A, sel, cost, *B[p], rng); q["random_mean_R"] = round(q["random_mean_R"], 4)
        res[p] = q
    return res


def ttest_periods(r, cost_unit="bp"):
    res = {}
    for p in P:
        g = r[[RB.period(t) == p for t in r.index]]
        if len(g) < 3: res[p] = dict(trades=len(g)); continue
        t = g.mean() / (g.std(ddof=1) / math.sqrt(len(g))); res[p] = dict(trades=len(g), mean_net_bp=round(float(g.mean()), 3), t=round(float(t), 2))
        if p == "TEST": res[p]["p_one_sided"] = float(0.5 * math.erfc(t / math.sqrt(2)))
    return res


def main():
    R = {}; SEL = {}; rng = np.random.default_rng(3031)
    for m in RI.MKTS:
        df, sp = T4.hourly_v(m); cost = 1.5 * sp; X = T4.all_indicators(df); A = atr(df)
        sigs = part_a_signals(df, X); sb, SEL[m] = part_b_signals(df, X); sigs.update(sb)
        for k, (L, S) in sigs.items(): R[f"{k}|{m}"] = dict(kind="trade", results=evaluate(df, A, L, S, cost, rng))
        R[f"STR-030k|{m}"] = dict(kind="ttest", results=ttest_periods(seasonality(df, cost)))
        R[f"STR-030l|{m}"] = dict(kind="ttest", results=ttest_periods(moon(df, cost)))
        print(m, "done", flush=True)
    keys = list(R); ps = [(R[k]["results"]["TEST"].get("p_random") if R[k]["kind"] == "trade" else R[k]["results"]["TEST"].get("p_one_sided")) for k in keys]
    sig = C.bh([1.0 if p is None else p for p in ps])
    for i, k in enumerate(keys):
        f = R[k]["results"]; rid = k.split("|")[0]; skip_train = rid in ("STR-030k", "STR-031i", "STR-031j")
        meanf = (lambda q: q.get("mean_R")) if R[k]["kind"] == "trade" else (lambda q: q.get("mean_net_bp"))
        av = [p for p in P if meanf(f[p]) is not None and not (skip_train and p == "TRAIN")]; pos = bool(av) and all(meanf(f[p]) > 0 for p in av)
        te = f["TEST"]; stress_ok = te.get("mean_R_stress", -1) > 0 if R[k]["kind"] == "trade" else (te.get("mean_net_bp", -1) - 0) > 0
        R[k]["decision"] = "SCREEN-PASS" if (pos and stress_ok and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
    json.dump(dict(n_tests=len(keys), selected_top5=SEL, results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    for k in keys: print(k, R[k]["decision"], {p: (v.get("trades"), v.get("mean_R", v.get("mean_net_bp"))) for p, v in R[k]["results"].items()}, R[k]["results"]["TEST"].get("p_random", R[k]["results"]["TEST"].get("p_one_sided")))


if __name__ == "__main__":
    main()
