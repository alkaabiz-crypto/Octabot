"""STR-025 (PREREG.md): volatility-scaled sizing of STR-023 trades. usage: BTC_DATA=<dir with btc_{15m,1h,1d}.json.gz> python3 -I run_str025.py"""
import gzip, json, math, os, sys, tempfile
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); STUDY = os.path.join(os.path.dirname(os.path.dirname(HERE)), "rsi_vwap_study")
sys.path.insert(0, os.path.join(STUDY, "src")); import study as S  # noqa: E402  (frozen)
SPLIT = S.ts(2023, 7, 1)


def unpack(src_files):
    tmp = tempfile.mkdtemp(); out = {}
    for iv, f in src_files.items():
        rows = json.load(gzip.open(f)); rows = [[r[0] // 1000 if r[0] > 1e11 else r[0]] + [float(v) for v in r[1:6]] for r in rows]
        out[iv] = os.path.join(tmp, f"{iv}.json"); json.dump(rows, open(out[iv], "w"))
    return out


def har_sigma(asset):
    t = np.array(asset.e.t); c = np.array(asset.e.c); r = np.diff(np.log(c)); day = t[1:] // 86400
    rv = pd.Series(r ** 2).groupby(day).sum(); rv = rv[rv > 0]; df = pd.DataFrame(dict(rv=rv))
    df["w"], df["m"] = df.rv.rolling(5).mean(), df.rv.rolling(22).mean(); df["y"] = df.rv.shift(-1); fc = pd.Series(np.nan, index=df.index)
    days = df.index.values
    for d0 in range(int(days[0]) + 150, int(days[-1]) + 1):
        if pd.Timestamp(d0 * 86400, unit="s").day != 1: continue
        tr = df[(df.index < d0 - 1)].dropna()
        if len(tr) < 100: continue
        b = np.linalg.lstsq(np.c_[np.ones(len(tr)), tr[["rv", "w", "m"]].values], tr.y.values, rcond=None)[0]
        te = df[(df.index >= d0 - 1) & (df.index < d0 + 31)].dropna(subset=["rv", "w", "m"])
        fc[te.index] = np.c_[np.ones(len(te)), te[["rv", "w", "m"]].values] @ b           # forecast for day+1, made at the end of `day`
    sig = np.sqrt(fc.clip(lower=1e-12)); sig.index = sig.index + 1                      # index = the day being forecast
    return sig


def stats(x):
    x = np.asarray(x); cum = np.cumsum(x); dd = float((np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max())
    w20 = float(min(np.convolve(x, np.ones(20), "valid"))) if len(x) >= 20 else float("nan")
    return dict(n=len(x), mean_R=round(float(x.mean()), 4), mean_over_sd=round(float(x.mean() / x.std(ddof=1)), 4), max_dd_R=round(dd, 2), worst_20_trades_R=round(w20, 2))


def main():
    eth = {iv: os.path.join(STUDY, "data", f"ethusdt_{iv}.json.gz") for iv in ("15m", "1h", "1d")}
    btc = {iv: os.path.join(os.environ["BTC_DATA"], f"btc_{iv}.json.gz") for iv in ("15m", "1h", "1d")}
    out = {}; score = 0; comps = 0
    for name, files in (("BTCUSDT", btc), ("ETHUSDT", eth)):
        p = unpack(files); A = S.Asset(name, p["15m"], p["1h"], p["1d"]); sig = har_sigma(A)
        trades = A.run("V1_VWAP_MOMENTUM", 1, "TRAIL", S.ts(2020, 1, 1), S.ts(2026, 11, 9))
        ref = sig.rolling(365, min_periods=120).median().shift(1)                       # sigma* from the previous 365 days
        rows = []
        for tr in trades:
            dday = tr.entry_time // 86400
            if dday not in sig.index or pd.isna(sig.get(dday)) or pd.isna(ref.get(dday)): continue
            rows.append((tr.entry_time, tr.r("primary"), float(np.clip(ref[dday] / sig[dday], 0.25, 2.0))))
        df = pd.DataFrame(rows, columns=["t", "r", "w"]); res = {}
        for half, sel in (("2020-01..2023-06", df.t < SPLIT), ("2023-07..2026-11", df.t >= SPLIT)):
            g = df[sel]; base = stats(g.r.values); sized = stats((g.w / g.w.mean() * g.r).values)
            better = sized["max_dd_R"] < base["max_dd_R"] and sized["mean_over_sd"] >= 0.95 * base["mean_over_sd"]
            res[half] = dict(unsized=base, sized=sized, mean_weight=round(float(g.w.mean()), 3), passes=bool(better)); comps += 1; score += int(better)
        out[name] = dict(trades_with_forecast=len(df), total_trades=len(trades), halves=res)
        print(name, json.dumps(res), flush=True)
    out["verdict"] = "USEFUL" if score == 4 else ("MIXED" if score >= 2 else "NOT USEFUL"); out["score"] = f"{score}/{comps}"
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1); print("VERDICT:", out["verdict"], out["score"])


if __name__ == "__main__":
    main()
