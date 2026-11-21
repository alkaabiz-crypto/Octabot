"""STR-047 (funding carry) and STR-048 (yields -> gold), PREREG.md. Downloads public data into scratch.
usage: DISCOVERY_DATA=<scratch with long/XAUUSDm_15m.csv.gz> python3 -I run.py <scratch_dir>"""
import io, json, math, os, ssl, sys, urllib.request, zipfile
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
PER = [("EARLY", "2000-01-01", "2023-01-01"), ("TRAIN", "2023-01-01", "2024-07-01"), ("VALIDATION", "2024-07-01", "2025-07-01"), ("TEST", "2025-07-01", "2100-01-01")]
period = lambda d: next(n for n, a, b in PER if a <= str(d)[:10] < b)


def get(url):
    for k in range(5):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120, context=CTX).read()
        except urllib.error.HTTPError:
            raise
        except Exception:
            if k == 4: raise
            __import__("time").sleep(3 * (k + 1))


def funding(sym, S):
    f = os.path.join(S, f"funding_{sym}.csv")
    if not os.path.exists(f):
        parts = []
        for m in pd.period_range("2020-01", "2026-10", freq="M"):
            try: z = zipfile.ZipFile(io.BytesIO(get(f"https://data.binance.vision/data/futures/um/monthly/fundingRate/{sym}/{sym}-fundingRate-{m.year}-{m.month:02d}.zip")))
            except Exception: continue
            d = pd.read_csv(z.open(z.namelist()[0]), header=None); d = d[pd.to_numeric(d[0], errors="coerce").notna()]
            parts.append(pd.DataFrame(dict(t=d[0].astype("int64"), rate=d[2].astype(float))))
        pd.concat(parts).drop_duplicates("t").sort_values("t").to_csv(f, index=False)
    d = pd.read_csv(f); return pd.Series(d.rate.values, index=pd.to_datetime(d.t, unit="ms", utc=True))


def fred(series, S):
    f = os.path.join(S, f"{series}.csv")
    if not os.path.exists(f) or os.path.getsize(f) == 0: raw = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"); open(f, "wb").write(raw)
    d = pd.read_csv(f); d.columns = ["date", "v"]; d["v"] = pd.to_numeric(d.v, errors="coerce"); return pd.Series(d.v.values, index=pd.to_datetime(d.date)).dropna()


def carry(rate, tbill):
    out = {}
    day = rate.groupby(rate.index.floor("D")).sum()                    # daily funding (3 payments)
    ann7 = day.rolling(7).mean() * 365; avg3 = day.rolling(3).mean()
    on = False; held = []; trades = 0
    for d in day.index:
        if not on and ann7.get(d, 0) > 0.10: on = True; trades += 1; held.append((d, -0.0015)); continue
        if on and avg3.get(d, 0) < 0: on = False; held.append((d, -0.0015)); continue
        if on: held.append((d, day[d]))
    b = pd.Series([x[1] for x in held], index=[x[0] for x in held])
    for n, a, z in PER:
        da = day[(day.index.tz_localize(None) >= a) & (day.index.tz_localize(None) < z)]
        if len(da) < 30: continue
        yrs = len(da) / 365; db = b[(b.index.tz_localize(None) >= a) & (b.index.tz_localize(None) < z)]
        tb = tbill[(tbill.index >= a) & (tbill.index < z)].mean() / 100
        A = (da.sum() - 0.003) / yrs; B = db.sum() / yrs
        out[n] = dict(days=len(da), always_on_net_yield_pct=round(A * 100, 2), always_on_margin_adjusted_pct=round(A / 1.2 * 100, 2),
                      conditional_net_yield_pct=round(B * 100, 2), conditional_margin_adjusted_pct=round(B / 1.2 * 100, 2),
                      conditional_time_in_market_pct=round(float((db != -0.0015).sum() / len(da) * 100), 1), tbill_pct=round(tb * 100, 2),
                      negative_funding_days_pct=round(float((da < 0).mean() * 100), 1))
    best = {n: max(v["always_on_margin_adjusted_pct"], v["conditional_margin_adjusted_pct"]) > v["tbill_pct"] for n, v in out.items()}
    out["verdict"] = "WORTH IT" if all(best.values()) else ("SOMETIMES" if any(best.values()) else "NOT WORTH IT"); out["entries_conditional"] = trades
    return out


def gold_daily():
    d = pd.read_csv(os.path.join(os.environ["DISCOVERY_DATA"], "long", "XAUUSDm_15m.csv.gz")); t = pd.to_datetime(d.t, unit="s", utc=True).dt.tz_convert("America/New_York")
    sel = (t.dt.hour == 16) & (t.dt.minute == 0); mid = (d.bo + d.ao) / 2; sp = (d.ao - d.bo) / mid
    return pd.Series(mid[sel].values, index=pd.to_datetime(t[sel].dt.date.values)), float(sp.median())


def yields_gold(y, gold, sp, rng):
    days = gold.index; yv = y.reindex(days, method="ffill"); chg = yv - yv.shift(20); res = {}; tr = []; i = 21
    pos = {d: k for k, d in enumerate(days)}
    while i < len(days) - 22:
        d = days[i]; c = chg.iloc[i]
        if np.isnan(c) or c == 0: i += 1; continue
        e, x = i + 2, i + 22; side = 1 if c < 0 else -1; g = side * (gold.iloc[x] / gold.iloc[e] - 1)
        tr.append(dict(d=days[e], side=side, g=g, net=g - 1.5 * sp, stress=g - 3 * sp)); i = x
    allret = np.array([gold.iloc[k + 20] / gold.iloc[k] - 1 for k in range(len(days) - 21)])
    for n, a, z in PER:
        s = [t for t in tr if a <= str(t["d"])[:10] < z]
        if len(s) < 3: res[n] = dict(trades=len(s)); continue
        net = np.array([t["net"] for t in s]); m = net.mean(); sims = np.array([(rng.choice([-1, 1], len(s)) * rng.choice(allret, len(s))).mean() - 1.5 * sp for _ in range(1000)])
        res[n] = dict(trades=len(s), mean_net_pct=round(m * 100, 3), mean_stress_pct=round(float(np.mean([t["stress"] for t in s]) * 100), 3), win_pct=round(float((net > 0).mean() * 100), 1),
                      long_share=round(float(np.mean([t["side"] > 0 for t in s])), 2), random_mean_pct=round(float(sims.mean() * 100), 3), p=float((sims >= m).mean()))
    return res


def main():
    S = sys.argv[1]; os.makedirs(S, exist_ok=True); rng = np.random.default_rng(3047); R = {}
    tb = fred("DTB3", S)
    for sym in ("BTCUSDT", "ETHUSDT"):
        R[f"STR-047|{sym}"] = carry(funding(sym, S), tb); print(sym, json.dumps(R[f"STR-047|{sym}"]), flush=True)
    gold, sp = gold_daily()
    for var, ser in (("A_nominal_DGS10", "DGS10"), ("B_real_DFII10", "DFII10")):
        r = yields_gold(fred(ser, S), gold, sp, rng); R[f"STR-048{var}"] = dict(results=r)
        f = r; av = [p for p, *_ in PER if f[p].get("mean_net_pct") is not None]; pos = bool(av) and all(f[p]["mean_net_pct"] > 0 for p in av); te = f["TEST"]
        R[f"STR-048{var}"]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_stress_pct", -1) > 0 and te.get("p", 1) <= 0.025 and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(var, R[f"STR-048{var}"]["decision"], json.dumps(r), flush=True)
    json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
