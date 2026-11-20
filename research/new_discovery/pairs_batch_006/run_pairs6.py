"""Pairs / relative-value batch 006 (PREREG.md). usage: python3 -I run_pairs6.py <config.json>
config: {"MULTI": dir of Exness <SYM>_15m.csv.gz, "ACAD_CFG": acad batch 005 config (1m sources), "BTC1H": path, "ETH1H": path}"""
import gzip, json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "acad_batch_005"))
import run_acad5 as A5  # noqa: E402  (Px for 1-minute sources, utc_min, PER)
PER = A5.PER; WIN, ZIN, ZSTOP, MAXD = 60, 2.0, 4.0, 20


def period(d): return A5.period(d)


def daily_from_15m(path, tz, hh, mm):
    d = pd.read_csv(path); mid = ((d.bo + d.ao) / 2).values; sp = (d.ao - d.bo).values; t = d.t.values.astype(np.int64)
    loc = pd.to_datetime(t, unit="s", utc=True).tz_convert(tz); sel = (loc.hour == hh) & (loc.minute == mm) & (loc.dayofweek < 5 if tz != "UTC" else True)
    return pd.DataFrame(dict(p=mid[sel], sp=sp[sel]), index=pd.Index(loc[sel].date, name="d"))


def daily_from_px(P, tz, hh, mm, days):
    rows = {}
    for d in days:
        x = P.at(A5.utc_min(d, hh, mm, tz))
        if x: rows[d] = x
    return pd.DataFrame(rows, index=["p", "sp"]).T


def daily_binance(path):
    q = np.array(json.load(gzip.open(path)), float); t = pd.to_datetime(q[:, 0], unit="s", utc=True); sel = t.hour == 0
    return pd.DataFrame(dict(p=q[sel, 1], sp=q[sel, 1] * 0.001), index=pd.Index(t[sel].date, name="d"))


def pair_trades(A, B, smult=2.0):
    j = A.join(B, how="inner", lsuffix="A", rsuffix="B").dropna(); la, lb = np.log(j.pA.values), np.log(j.pB.values); n = len(j); days = list(j.index)
    z = np.full(n, np.nan); beta = np.full(n, np.nan)
    for t in range(WIN, n):
        x, y = lb[t - WIN:t], la[t - WIN:t]; b = np.polyfit(x, y, 1)[0]; s = y - b * x; sd = s.std(ddof=1)
        if sd > 0: z[t] = (la[t] - b * lb[t] - s.mean()) / sd; beta[t] = b
    cost = lambda i, k, b: (j.spA.values[i] / j.pA.values[i] + j.spA.values[k] / j.pA.values[k]) / 2 + abs(b) * (j.spB.values[i] / j.pB.values[i] + j.spB.values[k] / j.pB.values[k]) / 2
    ret = lambda i, k, side, b: side * ((j.pA.values[k] / j.pA.values[i] - 1) - b * (j.pB.values[k] / j.pB.values[i] - 1))
    out = []; t = WIN
    while t < n - 1:
        if np.isnan(z[t]) or abs(z[t]) <= ZIN: t += 1; continue
        side = -1 if z[t] > 0 else 1; b = beta[t]; k = t + 1
        while k < n - 1 and k - t < MAXD and not np.isnan(z[k]) and np.sign(z[k]) == np.sign(z[t]) and abs(z[k]) <= ZSTOP: k += 1
        c = cost(t, k, b); g = ret(t, k, side, b) * 1e4; out.append(dict(d=days[t], side=side, hold=k - t, i=t, b=b, net=g - c * 1e4, stress=g - smult * c * 1e4)); t = k + 1
    return out, j, ret, cost


def bench(trades, j, ret, cost, rng, sets=1000):
    res = {}
    for name, *_ in PER:
        s = [x for x in trades if period(x["d"]) == name]
        if len(s) < 3: continue
        pool = [i for i, d in enumerate(j.index) if period(d) == name]; act = np.mean([x["net"] for x in s]); sims = np.empty((sets, len(s)))
        for u, x in enumerate(s):
            ok = [i for i in pool if i + x["hold"] < len(j)]
            for v in range(sets):
                i = ok[rng.integers(len(ok))]; sims[v, u] = (ret(i, i + x["hold"], x["side"], x["b"]) - cost(i, i + x["hold"], x["b"])) * 1e4
        m = sims.mean(axis=1); res[name] = (float(m.mean()), float((m >= act).mean()))
    return res


def summarize(trades, b, unit_key="net"):
    out = {}
    for name, *_ in PER:
        s = [x for x in trades if period(x["d"]) == name]
        if len(s) < 3: out[name] = dict(trades=len(s)); continue
        net = np.array([x["net"] for x in s]); st = np.array([x["stress"] for x in s])
        q = dict(trades=len(s), mean_net_bp=round(float(net.mean()), 2), mean_stress_bp=round(float(st.mean()), 2), win_pct=round(float((net > 0).mean() * 100), 1),
                 t=round(float(net.mean() / (net.std(ddof=1) / math.sqrt(len(net)))), 2), avg_hold_days=round(float(np.mean([x.get("hold", 7) for x in s])), 1))
        if name in b: q["random_mean_bp"], q["p"] = round(b[name][0], 2), b[name][1]
        out[name] = q
    return out


def xs_momentum(multi, rng, binance_dir=None, smult=2.0):
    coins = ["BTCUSDm", "ETHUSDm", "SOLUSDm", "BNBUSDm", "XRPUSDm", "LTCUSDm", "ADAUSDm", "BCHUSDm"]; D = {}
    for c in coins:
        if binance_dir:   # DEVIATION (RESULTS.md): Exness crypto 15m files lack BTC, end ADA in 2024-08 and have a 418-day SOL/BNB gap -> Binance daily opens, 0.05% per side
            q = json.load(open(os.path.join(binance_dir, c[:3] + ".json"))); t = pd.to_datetime([x[0] for x in q], unit="s", utc=True)
            D[c] = pd.DataFrame(dict(p=[x[1] for x in q], sp=[x[1] * 0.001 for x in q]), index=pd.Index(t.date, name="d")); continue
        p = os.path.join(multi, f"{c}_15m.csv.gz")
        if os.path.exists(p): D[c] = daily_from_15m(p, "UTC", 0, 0)
    px = pd.concat({c: d.p for c, d in D.items()}, axis=1).dropna(); sp = pd.concat({c: d.sp for c, d in D.items()}, axis=1).reindex(px.index)
    mondays = [d for d in px.index if pd.Timestamp(d).weekday() == 0]; out = []; rnd_all = {}
    for a, b in zip(mondays[:-1], mondays[1:]):
        prev = a - pd.Timedelta(days=7)
        if prev not in px.index or (b - a).days != 7: continue
        past = px.loc[a] / px.loc[prev] - 1; fwd = px.loc[b] / px.loc[a] - 1; cst = (sp.loc[a] / px.loc[a] + sp.loc[b] / px.loc[b]) / 2
        order = past.sort_values().index; L, S = list(order[-2:]), list(order[:2])
        g = (fwd[L].mean() - fwd[S].mean()) * 1e4; c = (cst[L].mean() + cst[S].mean()) * 1e4
        sims = []
        for _ in range(1000):
            perm = rng.permutation(len(px.columns)); l, s_ = px.columns[perm[:2]], px.columns[perm[2:4]]; sims.append((fwd[l].mean() - fwd[s_].mean()) * 1e4 - (cst[l].mean() + cst[s_].mean()) * 1e4)
        out.append(dict(d=a, net=g - c, stress=g - smult * c, hold=7)); rnd_all[a] = sims
    b = {}
    for name, *_ in PER:
        ds = [x for x in out if period(x["d"]) == name]
        if len(ds) < 3: continue
        m = np.array([rnd_all[x["d"]] for x in ds]).mean(axis=0); b[name] = (float(m.mean()), float((m >= np.mean([x["net"] for x in ds])).mean()))
    return out, b


def main():
    cfg = json.load(open(sys.argv[1])); acad = json.load(open(cfg["ACAD_CFG"])); M = cfg["MULTI"]; rng = np.random.default_rng(3039); R = {}
    f15 = lambda s, tz="America/New_York", hh=16, mm=0: daily_from_15m(os.path.join(M, f"{s}_15m.csv.gz"), tz, hh, mm)
    idx = {s: A5.Px(acad[s]) for s in ("USTECm", "US500m", "US30m")}
    days = A5.trading_days(idx["US500m"], "America/New_York", (9, 30), (16, 0)); dpx = {s: daily_from_px(P, "America/New_York", 16, 0, days) for s, P in idx.items()}
    pairs = {"STR-039a|XAU/XAG": (f15("XAUUSDm") if os.path.exists(os.path.join(M, "XAUUSDm_15m.csv.gz")) else daily_from_15m(cfg["XAU15"], "America/New_York", 16, 0), f15("XAGUSDm"), 2.0),
             "STR-039b|USOIL/UKOIL": (daily_from_15m(cfg["OIL15"], "America/New_York", 16, 0), f15("UKOILm"), 2.0),
             "STR-039c|USTEC/US500": (dpx["USTECm"], dpx["US500m"], 2.0), "STR-039d|US30/US500": (dpx["US30m"], dpx["US500m"], 2.0),
             "STR-039e|AUD/NZD": (f15("AUDUSDm"), f15("NZDUSDm"), 2.0), "STR-039f|EUR/GBP": (f15("EURUSDm"), f15("GBPUSDm"), 2.0),
             "STR-039g|DE30/STOXX50": (f15("DE30m", "Europe/Berlin", 17, 30), f15("STOXX50m", "Europe/Berlin", 17, 30), 2.0),
             "STR-039h|BTC/ETH": (daily_binance(cfg["BTC1H"]), daily_binance(cfg["ETH1H"]), 4.0)}
    for k, (a, b, sm) in pairs.items():
        a = a[[str(d) >= "2019-08-01" for d in a.index]] if "BTC" not in k else a
        tr, j, ret, cost = pair_trades(a, b, sm); R[k] = dict(results=summarize(tr, bench(tr, j, ret, cost, rng)), trades=len(tr), first=str(j.index[0]), last=str(j.index[-1]))
        print(k, {p: (v.get("trades"), v.get("mean_net_bp"), v.get("p")) for p, v in R[k]["results"].items()}, flush=True)
    xs, b = xs_momentum(M, rng, cfg.get("XS_BINANCE"), 4.0 if cfg.get("XS_BINANCE") else 2.0); R["STR-040|crypto XS momentum"] = dict(results=summarize(xs, b), trades=len(xs))
    print("STR-040", {p: (v.get("trades"), v.get("mean_net_bp"), v.get("p")) for p, v in R["STR-040|crypto XS momentum"]["results"].items()})
    keys = list(R); ps = [R[k]["results"].get("TEST", {}).get("p", 1.0) for k in keys]; o = np.argsort(ps); sig = set()
    for rank, i in enumerate(o):
        if ps[i] <= 0.05 * (rank + 1) / len(ps): sig = set(o[:rank + 1])
    for i, k in enumerate(keys):
        f = R[k]["results"]; av = [p for p, *_ in PER if f[p].get("mean_net_bp") is not None]; pos = bool(av) and all(f[p]["mean_net_bp"] > 0 for p in av); te = f.get("TEST", {})
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_stress_bp", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(k, R[k]["decision"])
    json.dump(dict(n_tests=len(keys), results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
