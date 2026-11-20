"""STR-045 (PREREG.md). usage: python3 -I run_str045.py <scratch dir with bitcoin-etf-flows.html, ethereum-etf-flows.html>"""
import json, math, os, re, ssl, sys, time, urllib.request
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
COST, STRESS, SPLIT = 0.0005, 0.0020, "2025-07-01"


def flows(path):
    t = open(path, errors="ignore").read().replace('\\"', '"'); rows = {}
    for m in re.finditer(r'\{"date":"(\d{4}-\d{2}-\d{2})","flow":(-?[\d.eE+-]+)', t): rows[m.group(1)] = float(m.group(2))
    s = pd.Series(rows).sort_index(); s.index = pd.to_datetime(s.index); return s


def opens(sym):
    out, t = [], 1704067200000
    while True:
        r = json.loads(urllib.request.urlopen(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1d&startTime={t}&limit=1000", timeout=30, context=CTX).read())
        out += [(pd.Timestamp(x[0], unit="ms"), float(x[1])) for x in r]
        if len(r) < 1000: break
        t = r[-1][0] + 1
    return pd.Series(dict(out))


def main():
    S = sys.argv[1]; R = {}; rng = np.random.default_rng(3045)
    for asset, f, sym in (("BTC", "bitcoin-etf-flows.html", "BTCUSDT"), ("ETH", "ethereum-etf-flows.html", "ETHUSDT")):
        fl = flows(os.path.join(S, f)); px = opens(sym); z = (fl - fl.rolling(60).mean().shift(1)) / fl.rolling(60).std().shift(1); z = z.dropna()
        R[asset] = dict(flow_days=len(fl), first=str(fl.index[0].date()), last=str(fl.index[-1].date()), z_days=len(z))
        for h in (1, 5):
            ent = z.index + pd.Timedelta(days=2); ex = ent + pd.Timedelta(days=h); ok = ent.isin(px.index) & ex.isin(px.index)
            zz = z[ok]; ret = pd.Series(px.reindex(ex[ok]).values / px.reindex(ent[ok]).values - 1, index=zz.index)
            res = {}
            for per, sel in (("VALIDATION", zz.index < SPLIT), ("TEST", zz.index >= SPLIT)):
                a, b = zz[sel], ret[sel]
                if h == 5: a, b = a.iloc[::5], b.iloc[::5]
                ic = float(np.corrcoef(a.rank(), b.rank())[0, 1]); n = len(a); tt = ic * math.sqrt((n - 2) / (1 - ic * ic))
                # rule: follow, non-overlapping
                tr = []; nxt = None
                for d, zv in zz[sel].items():
                    if nxt is not None and d < nxt: continue
                    if abs(zv) >= 1: side = 1 if zv > 0 else -1; tr.append((d, side, side * ret[d])); nxt = d + pd.Timedelta(days=h)
                g = np.array([x[2] for x in tr]); sides = np.array([x[1] for x in tr]); q = dict(ic=round(ic, 4), ic_t=round(tt, 2), ic_n=n, trades=len(tr))
                if len(tr) >= 3:
                    pool = ret[sel].values; sims = np.array([(rng.choice([-1, 1], len(tr)) * rng.choice(pool, len(tr))).mean() - 2 * COST for _ in range(1000)])
                    q.update(mean_net_pct=round(float((g.mean() - 2 * COST) * 100), 3), mean_stress_pct=round(float((g.mean() - 2 * STRESS) * 100), 3), win_pct=round(float(((g - 2 * COST) > 0).mean() * 100), 1),
                             fade_mean_net_pct=round(float((-g.mean() - 2 * COST) * 100), 3), random_mean_pct=round(float(sims.mean() * 100), 3), p=float((sims >= g.mean() - 2 * COST).mean()), long_share=round(float((sides > 0).mean()), 2))
                res[per] = q
            R[asset][f"h{h}"] = res
            print(asset, h, res, flush=True)
    keys = [(a, h) for a in ("BTC", "ETH") for h in ("h1", "h5")]; ps = [R[a][h]["TEST"].get("p", 1.0) for a, h in keys]; o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / len(ps): sig = set(o[:r + 1])
    for i, (a, h) in enumerate(keys):
        v, t = R[a][h]["VALIDATION"], R[a][h]["TEST"]; pos = v.get("mean_net_pct", -1) > 0 and t.get("mean_net_pct", -1) > 0
        R[a][h]["decision"] = "SCREEN-PASS" if (pos and t.get("mean_stress_pct", -1) > 0 and i in sig and t["trades"] >= 30) else ("WATCH" if pos else "REJECTED")
        print(a, h, R[a][h]["decision"])
    json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
