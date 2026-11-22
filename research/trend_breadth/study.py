"""Trend breadth test: frozen TREND_ENS on 18 other coins, 2025+ data. Implements PREREGISTRATION.md (this folder).

Usage: python3 -I study.py
"""
import importlib.util, json, math, os, sys, time, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data"); os.makedirs(DATA, exist_ok=True)
COINS = ["BNB", "SOL", "XRP", "DOGE", "ADA", "TRX", "LINK", "AVAX", "DOT", "LTC", "BCH", "XLM", "UNI", "ATOM", "ETC", "FIL", "NEAR", "APT"]
START_MS = int(pd.Timestamp("2025-01-01", tz="UTC").value // 10**6); FEE = 0.001; N = 1000; SEED = 20261112; MIN_DAYS = 600


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


S = load_mod("study", os.path.join(ROOT, "daily_signal_dca", "study.py"))
R = load_mod("from2025_run", os.path.join(ROOT, "daily_signal_dca", "from_2025", "run.py"))
END_MS = int(pd.Timestamp(time.strftime("%Y-%m-%d", time.gmtime()), tz="UTC").value // 10**6)


def klines(sym):
    path = os.path.join(DATA, f"{sym}_1d_from2025.csv.gz")
    if os.path.exists(path): return pd.read_csv(path)
    rows, t = [], START_MS
    while t < END_MS:
        r = json.loads(urllib.request.urlopen(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1d&startTime={t}&limit=1000",
                                              timeout=30, context=S.CTX).read())
        if not r: break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in r]; t = r[-1][0] + 1
    df = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t"); df = df[(df.t >= START_MS) & (df.t < END_MS)]
    assert len(df) == 0 or df.t.min() >= START_MS
    df.to_csv(path, index=False, compression="gzip"); return df


def sharpe(r):
    r = r.dropna(); return float(r.mean() / r.std() * math.sqrt(365)) if r.std() > 0 else 0.0


def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); data = {}; dropped = {}
    for c in COINS:
        d = klines(c + "USDT"); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True)
        if len(d) < MIN_DAYS: dropped[c] = len(d); continue
        gaps = d.date.diff().dt.days.dropna()
        assert (gaps == 1).all(), f"{c}: daily gap"
        data[c] = d
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), coins=list(data), dropped=dropped, per_coin={}, primary={}, secondary={})
    for name in ("TREND_ENS", "SMA50"):
        W = {c: R.signals(d)[name].astype(float).fillna(0.0).reset_index(drop=True) for c, d in data.items()}
        base_sh = {}
        for c, d in data.items():
            r = S.lump(d, W[c], FEE); bh = S.lump(d, pd.Series(np.ones(len(d))), FEE)
            eq, eqb = (1 + r).cumprod(), (1 + bh).cumprod(); base_sh[c] = sharpe(r)
            out["per_coin"][f"{c}|{name}"] = dict(sharpe=round(base_sh[c], 3), ret=round(float(eq.iloc[-1] - 1), 4), max_dd=round(float((eq / eq.cummax() - 1).min()), 4),
                                                  bh_ret=round(float(eqb.iloc[-1] - 1), 4), bh_max_dd=round(float((eqb / eqb.cummax() - 1).min()), 4),
                                                  bh_sharpe=round(sharpe(bh), 3), exposure=round(float(W[c].mean()), 3), days=len(d))
        draws = np.zeros(N); per = {c: [] for c in data}
        for k in range(N):
            vals = []
            for c, d in data.items():
                s = int(rng.integers(20, len(d) - 20 + 1)); v = sharpe(S.lump(d, pd.Series(np.roll(W[c].values, s)), FEE)); vals.append(v); per[c].append(v)
            draws[k] = np.mean(vals)
        for c in data: out["per_coin"][f"{c}|{name}"]["percentile_vs_own_shifts"] = round(float((np.array(per[c]) < base_sh[c]).mean() * 100), 1)
        mean_sh = float(np.mean(list(base_sh.values())))
        res = dict(mean_sharpe=round(mean_sh, 3), random_p50=round(float(np.percentile(draws, 50)), 3), random_p95=round(float(np.percentile(draws, 95)), 3),
                   percentile=round(float((draws < mean_sh).mean() * 100), 1), verdict="PASS" if mean_sh > np.percentile(draws, 95) else "FAIL",
                   share_beat_bh=round(float(np.mean([out["per_coin"][f"{c}|{name}"]["ret"] > out["per_coin"][f"{c}|{name}"]["bh_ret"] for c in data])), 3),
                   share_smaller_dd=round(float(np.mean([out["per_coin"][f"{c}|{name}"]["max_dd"] > out["per_coin"][f"{c}|{name}"]["bh_max_dd"] for c in data])), 3),
                   mean_bh_sharpe=round(float(np.mean([out["per_coin"][f"{c}|{name}"]["bh_sharpe"] for c in data])), 3))
        (out["primary"] if name == "TREND_ENS" else out["secondary"])[name] = res
        print(name, res, f"{time.time() - t0:.0f}s", flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    for k, v in out["per_coin"].items():
        if k.endswith("TREND_ENS"): print(k, v)
    print("dropped:", dropped)


if __name__ == "__main__":
    main()
