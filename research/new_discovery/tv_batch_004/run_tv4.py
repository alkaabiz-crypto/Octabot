"""TradingView batch 004 (PREREG.md). Part A: remaining built-ins, IND batch 001 IC machinery on its 5 markets.
Part B: best market x horizon per indicator chosen on TRAIN+VALIDATION across 33 Exness markets, checked on TEST.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_tv4.py [A|B|AB]
"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("ind_batch_001", "ind_batch_002", "tv_batch_003", "src"): sys.path.insert(0, os.path.join(ND, p))
import run_ind as RI, run_ind2 as RI2, run_tv3 as T3, common as C  # noqa: E401,E402
RB = RI.RB; ema, sma, atr, rsi = RI.ema, RI.sma, RI.atr, RI.rsi
SCR = os.environ["DISCOVERY_DATA"]
ALL = sorted({f[:-11] for f in os.listdir(os.path.join(SCR, "multi", "bars")) if f.endswith("_15m.csv.gz")} | C.LONG)


def hourly_v(m):
    d = RB.load(m); g = d.groupby(d.index.floor("h"))
    return pd.DataFrame(dict(o=g.mo.first(), h=g.mh.max(), l=g.ml.min(), c=g.mc.last(), v=g.ticks.sum().astype(float))), RB.spread_frac(d)


def wma(x, n): w = np.arange(1, n + 1); return x.rolling(n).apply(lambda v: (v * w).sum() / w.sum(), raw=True)
def slope(x): return np.log(x / x.shift())
def state_loop(c, up, dn):
    s = np.zeros(len(c))
    for i in range(1, len(c)): s[i] = 1 if c[i] > up[i] else (-1 if c[i] < dn[i] else s[i - 1])
    return s


def indicators4(df):
    o, h, l, c, v = df.o, df.h, df.l, df.c, df.v; A = atr(df); idx = df.index; X = {}; mid = sma(c, 20); sd = c.rolling(20).std()
    n, off, sg = 9, 0.85, 6; m_ = off * (n - 1); s_ = n / sg; w = np.exp(-((np.arange(n) - m_) ** 2) / (2 * s_ * s_)); w /= w.sum()
    X["IND-049"] = slope(c.rolling(n).apply(lambda z: (z * w).sum(), raw=True))
    X["IND-050"] = sma(((c - o) / (h - l)).replace([np.inf, -np.inf], 0).fillna(0), 14)
    m50, s50 = sma(c, 50), c.rolling(50).std(); X["IND-051"] = ((mid - 2 * sd - (m50 - 2 * s50)).abs() - (mid + 2 * sd - (m50 + 2 * s50)).abs()) / mid * 100
    mfm = (((c - l) - (h - c)) / (h - l)).replace([np.inf, -np.inf], 0).fillna(0); mfv = mfm * v
    X["IND-052"] = mfv.rolling(20).sum() / v.rolling(20).sum(); adl = mfv.cumsum()
    X["IND-053"] = (ema(adl, 3) - ema(adl, 10)) / sma(v, 10); X["IND-054"] = (adl - adl.shift(14)) / v.rolling(14).sum()
    a10 = atr(df, 10); fh, fl = h.rolling(10).max() - a10, l.rolling(10).min() + a10; X["IND-055"] = pd.Series(state_loop(c.values, fh.rolling(9).max().values, fl.rolling(9).min().values), index=idx)
    d = c.diff(); su, sdn = d.clip(lower=0).rolling(9).sum(), (-d.clip(upper=0)).rolling(9).sum(); X["IND-056"] = 100 * (su - sdn) / (su + sdn)
    e34 = ema(c, 34); X["IND-057"] = np.degrees(np.arctan((e34 - e34.shift()) / A))
    t = pd.Series(np.arange(len(c), dtype=float), index=idx); X["IND-058"] = c.rolling(14).corr(t)
    e = ema(c, 9); X["IND-059"] = slope(2 * e - ema(e, 9)); e2 = ema(e, 9); X["IND-060"] = slope(3 * e - 3 * e2 + ema(e2, 9))
    dm = ((h + l) / 2).diff(); box = (v / 10000) / (h - l).replace(0, np.nan); X["IND-061"] = sma(dm / box, 14) / A
    X["IND-062"] = ema(c.diff() * v, 13) / (A * sma(v, 13))
    X["IND-063"] = c / mid - 1
    sh = sum(ema(c, k) for k in (3, 5, 8, 10, 12, 15)) / 6; lg = sum(ema(c, k) for k in (30, 35, 40, 45, 50, 60)) / 6; X["IND-064"] = np.log(sh / lg)
    lr = T3.linreg(c, 100); res = (c - lr); X["IND-065"] = res / (2 * res.rolling(100).std())
    cv = c.values; md = np.full(len(c), np.nan); md[0] = cv[0]
    for i in range(1, len(c)): md[i] = md[i - 1] + (cv[i] - md[i - 1]) / (14 * (cv[i] / md[i - 1]) ** 4)
    X["IND-066"] = c / md - 1; X["IND-067"] = (c - c.shift(10)) / A
    tp = (h + l + c) / 3; rmf = tp * v; pos = rmf.where(tp > tp.shift(), 0).rolling(14).sum(); neg = rmf.where(tp < tp.shift(), 0).rolling(14).sum(); X["IND-068"] = 100 - 100 / (1 + pos / neg) - 50
    sv = v * np.sign(c.diff()); X["IND-069"] = sv.rolling(14).sum() / v.rolling(14).sum()
    obv = sv.fillna(0).cumsum(); X["IND-070"] = (obv - ema(obv, 20)) / v.rolling(20).sum()
    ppo = 100 * (ema(c, 12) - ema(c, 26)) / ema(c, 26); X["IND-071"] = ppo - ema(ppo, 9)
    pvt = (c.pct_change() * v).fillna(0).cumsum(); X["IND-072"] = (pvt - pvt.shift(14)) / sma(v, 14)
    X["IND-073"] = c.rolling(9).apply(lambda z: np.corrcoef(pd.Series(z).rank().values, np.arange(9))[0, 1], raw=True) * 100
    sw = lambda x: (x + 2 * x.shift() + 2 * x.shift(2) + x.shift(3)) / 6; rv = sw(c - o).rolling(10).sum() / sw(h - l).rolling(10).sum(); X["IND-074"] = rv - sw(rv)
    s10 = c.rolling(10).std(); u = ema(s10.where(c.diff() > 0, 0), 14); dn = ema(s10.where(c.diff() < 0, 0), 14); X["IND-075"] = 100 * u / (u + dn) - 50
    tsi = lambda r, a, b: 100 * ema(ema(r, a), b) / ema(ema(r.abs(), a), b)
    erg = tsi(c.diff(), 20, 5); X["IND-076"] = erg - ema(erg, 5)
    r = rsi(c); st = 100 * (r - r.rolling(14).min()) / (r.rolling(14).max() - r.rolling(14).min()); X["IND-077"] = sma(st, 3) - 50
    hh, ll = h.rolling(10).max(), l.rolling(10).min(); rel = c - (hh + ll) / 2; X["IND-078"] = 200 * ema(ema(rel, 3), 3) / ema(ema(hh - ll, 3), 3)
    X["IND-079"] = slope(c.ewm(alpha=1 / 7, adjust=False).mean())
    X["IND-080"] = tech_rating(df, A)
    ts = tsi(c.diff(), 25, 13); X["IND-081"] = ts - ema(ts, 13)
    a20 = atr(df, 20).values * 2; vs = np.zeros(len(c)); ext = cv[0]; stop = np.nan; up = True
    for i in range(1, len(c)):
        if np.isnan(a20[i]): continue
        ext = max(ext, cv[i]) if up else min(ext, cv[i]); stop = ext - a20[i] if up else ext + a20[i]
        if up and cv[i] < stop: up, ext = False, cv[i]
        elif (not up) and cv[i] > stop: up, ext = True, cv[i]
        vs[i] = 1 if up else -1
    X["IND-082"] = pd.Series(vs, index=idx)
    X["IND-083"] = (wma_v(c, v, 20) - sma(c, 20)) / A
    hv, lv = h.values, l.values; uf = np.full(len(c), np.nan); lf = np.full(len(c), np.nan); s = np.zeros(len(c)); lu = ld = np.nan
    for i in range(4, len(c)):
        j = i - 2
        if hv[j] == hv[j - 2:j + 3].max(): lu = hv[j]
        if lv[j] == lv[j - 2:j + 3].min(): ld = lv[j]
        s[i] = 1 if (not np.isnan(lu) and cv[i] > lu) else (-1 if (not np.isnan(ld) and cv[i] < ld) else s[i - 1])
    X["IND-084"] = pd.Series(s, index=idx)
    md6 = tp.rolling(6).apply(lambda z: np.abs(z - z.mean()).mean(), raw=True); X["IND-085"] = (tp - sma(tp, 6)) / (0.015 * md6) / 100
    dmk = np.sign((h + l + c).diff()); vf = v * dmk; kvo = ema(vf, 34) - ema(vf, 55); X["IND-086"] = (kvo - ema(kvo, 13)) / sma(v, 55)
    day = df.groupby(idx.floor("D")).agg(h=("h", "max"), l=("l", "min"), c=("c", "last")).shift(); pp = (day.h + day.l + day.c) / 3; rng_ = (day.h - day.l)
    X["IND-087"] = (c - pp.reindex(idx.floor("D")).values) / rng_.reindex(idx.floor("D")).values
    X["IND-088"] = rsi_div(c, l, h, r)
    return X


def wma_v(c, v, n): return (c * v).rolling(n).sum() / v.rolling(n).sum()


def rsi_div(c, l, h, r):
    lv, hv, rv = l.values, h.values, r.values; n = len(c); out = np.zeros(n); pl = ph = None; hold = 0; sgn = 0
    for i in range(10, n):
        j = i - 5
        if lv[j] == lv[j - 5:j + 6].min():
            if pl is not None and 5 <= j - pl <= 60 and lv[j] < lv[pl] and rv[j] > rv[pl]: sgn, hold = 1, 10
            pl = j
        if hv[j] == hv[j - 5:j + 6].max():
            if ph is not None and 5 <= j - ph <= 60 and hv[j] > hv[ph] and rv[j] < rv[ph]: sgn, hold = -1, 10
            ph = j
        out[i] = sgn if hold > 0 else 0; hold -= 1
    return pd.Series(out, index=c.index)


def tech_rating(df, A):
    """TradingView Technical Ratings, simplified to its documented votes: MA rating (price vs SMA/EMA 10..200, Ichimoku base,
    VWMA 20, HMA 9) and oscillator rating (RSI, Stoch, CCI, ADX/DI, AO, Momentum, MACD, Stoch RSI, %R, Bull Bear Power, UO); the average of the two."""
    c, h, l = df.c, df.h, df.l; mav = []
    for k in (10, 20, 30, 50, 100, 200): mav += [np.sign(c - sma(c, k)), np.sign(c - ema(c, k))]
    kij = (h.rolling(26).max() + l.rolling(26).min()) / 2; mav += [np.sign(c - kij), np.sign(c - wma_v(c, df.v, 20))]
    hma = T3.wma(2 * T3.wma(c, 4) - T3.wma(c, 9), 3); mav.append(np.sign(c - hma)); ma = sum(mav) / len(mav)
    X1 = RI.indicators(df); X2 = RI2.indicators2(df); r = rsi(c)
    ov = [np.where((r < 30) & (r.diff() > 0), 1, np.where((r > 70) & (r.diff() < 0), -1, 0)),
          np.where((X1["IND-014"] < -30), 1, np.where(X1["IND-014"] > 30, -1, 0)),
          np.where(X1["IND-015"] < -100, 1, np.where(X1["IND-015"] > 100, -1, 0)),
          np.sign(X1["IND-010"]) * (X1["IND-010"].abs() > 20), np.sign(X2["IND-030"]), np.sign(c - c.shift(10)), np.sign(X1["IND-006"]),
          np.where(X1["IND-016"] < -30, 1, np.where(X1["IND-016"] > 30, -1, 0)), np.sign(X2["IND-034"]),
          np.where(X2["IND-031"] < -20, 1, np.where(X2["IND-031"] > 20, -1, 0))]
    osc = sum(pd.Series(np.asarray(x, float), index=c.index) for x in ov) / len(ov)
    return (ma + osc) / 2


def all_indicators(df):
    X = {}; X.update(RI.indicators(df)); X.update(RI2.indicators2(df)); X.update(T3.indicators3(df, T3.base(df))); X.update(indicators4(df)); return X


def verdicts(IC):
    ik = [(k, h) for k, v in IC.items() for h, r in v.items() if "TEST" in r]; isig = C.bh([IC[k][h]["TEST"]["p"] for k, h in ik])
    for i, (k, h) in enumerate(ik): IC[k][h]["TEST"]["bh"] = i in isig
    out = {}; order = ["NONE", "WEAK", "REDUNDANT", "INFORMATIVE"]
    for ind in sorted({k.split("|")[0] for k in IC}):
        best, detail = "NONE", []
        for h in sorted({hh for k in IC if k.startswith(ind + "|") for hh in IC[k]}):
            mk = [k for k in IC if k.startswith(ind + "|") and h in IC[k] and "TEST" in IC[k][h]]
            pos = [k for k in mk if all(v["ic"] > 0 for v in IC[k][h].values())]
            bhs = [k for k in pos if IC[k][h]["TEST"].get("bh")]; part = [k for k in bhs if IC[k][h]["TEST"].get("partial_p", 1) <= 0.05]
            v = "INFORMATIVE" if (len(pos) >= 3 and part) else ("REDUNDANT" if bhs and not part else ("WEAK" if len(pos) >= 3 else "NONE"))
            detail.append(dict(h=h, markets_positive_every_period=[k.split("|")[1] for k in pos], verdict=v)); best = max(best, v, key=order.index)
        neg = [(k.split("|")[1], h) for k in IC if k.startswith(ind + "|") for h in IC[k] if "TEST" in IC[k][h] and len(IC[k][h]) >= 3 and all(v["ic"] < 0 for v in IC[k][h].values())]
        out[ind] = dict(verdict=best, by_horizon=detail, consistently_negative=neg)
    return len(ik), out


def part_a():
    IC = {}
    for m in RI.MKTS:
        df, _ = hourly_v(m)
        for k, x in indicators4(df).items(): IC[f"{k}|{m}"] = RI.ic_tests(x, df, k)
        print("A", m, flush=True)
    n, v = verdicts(IC); json.dump(dict(n_ic_test_tests=n, verdicts=v, ic=IC), open(os.path.join(HERE, "results_A.json"), "w"), indent=1, default=float)
    for k, x in v.items(): print(k, x["verdict"], [(d["h"], d["markets_positive_every_period"]) for d in x["by_horizon"] if d["markets_positive_every_period"]], "| neg:", x["consistently_negative"][:5])


TV0, TE0 = pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2025-07-01", tz="UTC")


def cell_stats(x, df, hz, spread):
    o, c = df.o.values, df.c.values; fwd = np.full(len(df), np.nan); fwd[:-hz - 1] = np.log(o[hz + 1:] / o[1:-hz])
    f = pd.DataFrame(dict(x=np.asarray(x, float), y=fwd), index=df.index).replace([np.inf, -np.inf], np.nan).dropna().iloc[::hz]; out = {}
    for name, sel in (("TV", (f.index >= TV0) & (f.index < TE0)), ("TEST", f.index >= TE0)):
        g = f[sel]
        if len(g) < 30 or g.x.nunique() < 2: return None
        ic = float(np.corrcoef(g.x.rank(), g.y.rank())[0, 1]); n = len(g); t = ic * math.sqrt((n - 2) / max(1e-12, 1 - ic * ic))
        sx = np.sign(g.x); nz = sx != 0; gr = (sx * g.y * 1e4)[nz]; cst = 1.5 * spread * 1e4
        out[name] = dict(n=n, ic=ic, t=t, net_follow_bp=float((gr - cst).mean()), net_contra_bp=float((-gr - cst).mean()))
    return out


def part_b():
    cells = {}
    for m in ALL:
        try: df, sp = hourly_v(m)
        except Exception as e: print("skip", m, e); continue
        for k, x in all_indicators(df).items():
            for hz in (1, 4, 24):
                s = cell_stats(x, df, hz, sp)
                if s: cells[f"{k}|{m}|h{hz}"] = s
        print("B", m, len(cells), flush=True)
    picks = {}
    for ind in sorted({k.split("|")[0] for k in cells}):
        cand = {k: v for k, v in cells.items() if k.startswith(ind + "|")}; k = max(cand, key=lambda q: abs(cand[q]["TV"]["t"])); v = cand[k]; sgn = 1 if v["TV"]["ic"] > 0 else -1
        te = v["TEST"]; tt = sgn * te["t"]; p = 0.5 * math.erfc(tt / math.sqrt(2))
        picks[ind] = dict(cell=k, n_cells=len(cand), direction="follow" if sgn > 0 else "contrarian", tv_ic=round(v["TV"]["ic"], 4), tv_t=round(v["TV"]["t"], 2),
                          test_ic_in_direction=round(sgn * te["ic"], 4), test_t=round(tt, 2), test_p=p, test_n=te["n"], test_net_bp=round(te["net_follow_bp"] if sgn > 0 else te["net_contra_bp"], 2))
    ks = list(picks); sig = C.bh([picks[k]["test_p"] for k in ks])
    for i, k in enumerate(ks):
        q = picks[k]; q["verdict"] = "HOLDS" if i in sig else ("SAME DIRECTION, NOT SIGNIFICANT" if q["test_ic_in_direction"] > 0 else "REVERSED")
    json.dump(dict(n_cells=len(cells), n_picks=len(picks), picks=picks), open(os.path.join(HERE, "results_B.json"), "w"), indent=1, default=float)
    json.dump(cells, open(os.path.join(os.environ.get("CELLS_OUT", HERE), "cells_B.json"), "w"), default=float)
    for k, q in picks.items(): print(k, q["cell"], q["direction"], "TV t", q["tv_t"], "| TEST ic", q["test_ic_in_direction"], "t", q["test_t"], "net", q["test_net_bp"], q["verdict"])


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "AB"
    if "A" in a: part_a()
    if "B" in a: part_b()
