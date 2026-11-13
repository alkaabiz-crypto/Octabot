"""IND batch 002 (PREREG.md). Imports batch 001's data, IC and verdict machinery unchanged.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_ind2.py"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("ind_batch_001", "src"): sys.path.insert(0, os.path.join(ND, p))
import run_ind as RI, common as C  # noqa: E401,E402
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("b2run", os.path.join(ND, "batch_002", "run_batch.py")); B2 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B2)  # batch 002: hmm_fit, hmm_filter
RB = RI.RB


def smma(x, n): return x.ewm(alpha=1 / n, adjust=False).mean()
def wma(x, n): w = np.arange(1, n + 1); return x.rolling(n).apply(lambda v: (v * w).sum() / w.sum(), raw=True)


def indicators2(df):
    c, h, l, o = df.c, df.h, df.l, df.o; A = RI.atr(df); X = {}
    n = 25; X["IND-022"] = 100 * (h.rolling(n + 1).apply(np.argmax, raw=True) - l.rolling(n + 1).apply(np.argmin, raw=True)) / n
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    X["IND-023"] = ((h - l.shift()).abs().rolling(14).sum() - (l - h.shift()).abs().rolling(14).sum()) / tr.rolling(14).sum()
    t3 = RI.ema(RI.ema(RI.ema(c, 15), 15), 15); X["IND-024"] = 100 * t3.pct_change()
    ch = (c - c.shift(10)).abs(); vol = c.diff().abs().rolling(10).sum(); er = (ch / vol).fillna(0); sc = (er * (2 / 3 - 2 / 31) + 2 / 31) ** 2
    k = np.full(len(c), np.nan); cv = c.values; scv = sc.values
    for i in range(10, len(c)): k[i] = cv[i] if np.isnan(k[i - 1]) else k[i - 1] + scv[i] * (cv[i] - k[i - 1])
    kama = pd.Series(k, index=c.index); X["IND-025"] = np.log(kama / kama.shift())
    med = (h + l) / 2; X["IND-026"] = (smma(med, 5).shift(3) - smma(med, 13).shift(8)) / A
    hma = wma(2 * wma(c, 27) - wma(c, 55), int(math.sqrt(55))); X["IND-027"] = np.log(hma / hma.shift())
    X["IND-028"] = (c - RI.ema(c, 20)) / (2 * RI.atr(df, 20))
    hc = ((o + h + l + c) / 4).values; ho = np.zeros(len(c)); ho[0] = (o.iloc[0] + c.iloc[0]) / 2
    for i in range(1, len(c)): ho[i] = (ho[i - 1] + hc[i - 1]) / 2
    col = np.sign(hc - ho); run = np.zeros(len(c))
    for i in range(1, len(c)): run[i] = (run[i - 1] + col[i] if np.sign(run[i - 1]) == col[i] else col[i])
    X["IND-029"] = pd.Series(np.clip(run, -10, 10), index=c.index)
    X["IND-030"] = (RI.sma(med, 5) - RI.sma(med, 34)) / A
    bp = c - pd.concat([l, c.shift()], axis=1).min(axis=1); avg = lambda n: bp.rolling(n).sum() / tr.rolling(n).sum()
    X["IND-031"] = 100 * (4 * avg(7) + 2 * avg(14) + avg(28)) / 7 - 50
    X["IND-032"] = 100 * (c / c.shift(12) - 1)
    hh, ll = med.rolling(10).max(), med.rolling(10).min(); v = (2 * ((med - ll) / (hh - ll) - 0.5)).clip(-0.999, 0.999)
    v = v.ewm(alpha=0.33, adjust=False).mean().clip(-0.999, 0.999); X["IND-033"] = (0.5 * np.log((1 + v) / (1 - v))).ewm(alpha=0.5, adjust=False).mean()
    e13 = RI.ema(c, 13); X["IND-034"] = ((h - e13) + (l - e13)) / A
    return X


def hmm_ic(m):
    d = RB.load(m); x = d[(d.index.hour == 20) & (d.index.minute == 45)]; s = pd.Series(x.mc.values, index=x.index.normalize())
    r = np.log(s).diff().dropna(); rng = np.random.default_rng(B2.SEED); prob = pd.Series(np.nan, index=r.index)
    for mo in pd.date_range(r.index[0] + pd.Timedelta(days=380), r.index[-1], freq="MS"):
        hist = r[r.index < mo]
        if len(hist) < 250: continue
        mu, sd, Am, pi = B2.hmm_fit(hist.values, rng=rng); bull = int(np.argmax(mu)); upto = r[r.index < mo + pd.offsets.MonthBegin(1)]
        al = B2.hmm_filter(upto.values, mu, sd, Am, pi); sel = upto.index >= mo; prob[upto.index[sel]] = al[sel, bull] - 0.5
    res = {}
    for hz, nd in (("d1", 1), ("d5", 5)):
        fwd = np.log(s.shift(-nd) / s).reindex(prob.index); past = np.log(s / s.shift(nd)).reindex(prob.index)
        f = pd.DataFrame(dict(x=prob, y=fwd, b=past)).dropna().iloc[::nd]; out = {}
        for p in RI.P:
            g = f[[RB.period(t + pd.Timedelta(hours=21)) == p for t in f.index]]
            if len(g) < 30: continue
            ic = RI.spearmanr(g.x, g.y)[0]; n = len(g); t = ic * math.sqrt((n - 2) / max(1e-12, 1 - ic * ic))
            rx, rb, ry = RI.rankdata(g.x), RI.rankdata(g.b), RI.rankdata(g.y); ex = rx - np.polyval(np.polyfit(rb, rx, 1), rb); ey = ry - np.polyval(np.polyfit(rb, ry, 1), rb)
            pic = float(np.corrcoef(ex, ey)[0, 1]); pt = pic * math.sqrt((n - 3) / max(1e-12, 1 - pic * pic))
            out[p] = dict(n=n, ic=round(float(ic), 4), p=float(0.5 * math.erfc(t / math.sqrt(2))), partial_ic=round(pic, 4), partial_p=float(0.5 * math.erfc(pt / math.sqrt(2))))
        res[hz] = out
    return res


def main():
    R = {}
    for m in RI.MKTS:
        df = RI.hourly(m)
        for k, x in indicators2(df).items(): R[f"{k}|{m}"] = RI.ic_tests(x, df, k)
        R[f"IND-019|{m}"] = hmm_ic(m); print(m, "done", flush=True)
    keys = [(k, h) for k, v in R.items() for h, r in v.items() if "TEST" in r]; ps = [R[k][h]["TEST"]["p"] for k, h in keys]; sig = C.bh(ps)
    for i, (k, h) in enumerate(keys): R[k][h]["TEST"]["bh"] = i in sig
    verdict = {}; order = ["NONE", "WEAK", "REDUNDANT", "INFORMATIVE"]
    for ind in sorted({k.split("|")[0] for k in R}):
        best, detail = "NONE", []
        for h in sorted({hh for k in R if k.startswith(ind + "|") for hh in R[k]}):
            mk = [k for k in R if k.startswith(ind + "|") and h in R[k] and "TEST" in R[k][h]]
            pos = [k for k in mk if all(v["ic"] > 0 for v in R[k][h].values())]
            bhs = [k for k in pos if R[k][h]["TEST"].get("bh")]; part = [k for k in bhs if R[k][h]["TEST"].get("partial_p", 1) <= 0.05]
            v = "INFORMATIVE" if (len(pos) >= 3 and part) else ("REDUNDANT" if bhs and not part else ("WEAK" if len(pos) >= 3 else "NONE"))
            detail.append(dict(h=h, markets_positive_every_period=[k.split("|")[1] for k in pos], bh_test=[k.split("|")[1] for k in bhs], verdict=v)); best = max(best, v, key=order.index)
        neg = [(k.split("|")[1], h) for k in R if k.startswith(ind + "|") for h in R[k] if "TEST" in R[k][h] and len(R[k][h]) >= 3 and all(v["ic"] < 0 for v in R[k][h].values())]
        verdict[ind] = dict(verdict=best, by_horizon=detail, consistently_negative=neg)
    json.dump(dict(n_test_tests=len(keys), n_bh_significant=len(sig), verdicts=verdict, results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print("TEST tests", len(keys), "BH significant", len(sig))
    for ind, v in verdict.items(): print(ind, v["verdict"], [(d["h"], d["markets_positive_every_period"]) for d in v["by_horizon"] if d["markets_positive_every_period"]], "| neg:", v["consistently_negative"][:6])


if __name__ == "__main__":
    main()
