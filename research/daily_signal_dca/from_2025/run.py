"""Daily signal DCA bot re-run using ONLY data from 2025-01-01 onward (user instruction 2026-11-10: never use data
before January 2025). Same signals and costs as ../study.py, with one forced adaptation: moving averages that do not
yet have enough post-2025 history are left out of TREND_ENS until they do (SMA200 becomes available around mid-July 2025).

Usage: python3 -I run.py
"""
import json, math, os, sys, time, urllib.request
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study as S  # noqa: E402  (signal helpers, engine, metrics; study.py unchanged)

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data"); os.makedirs(DATA, exist_ok=True)
START = "2025-01-01"; START_MS = int(pd.Timestamp(START, tz="UTC").value // 10**6)
END = time.strftime("%Y-%m-%d", time.gmtime())                      # up to the last fully closed day
SPLITS = dict(full=(START, END), y2025=(START, "2026-01-01"), y2026=("2026-01-01", END))


def klines(sym, iv):
    path = os.path.join(DATA, f"{sym}_{iv}_from2025.csv.gz")
    if os.path.exists(path): return pd.read_csv(path)
    rows, t = [], START_MS; end = int(pd.Timestamp(END, tz="UTC").value // 10**6)
    while t < end:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={iv}&startTime={t}&limit=1000"
        r = json.loads(urllib.request.urlopen(url, timeout=30, context=S.CTX).read())
        if not r: break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in r]; t = r[-1][0] + 1
    df = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t"); df = df[(df.t >= START_MS) & (df.t < end)]
    assert df.t.min() >= START_MS, "pre-2025 data must not be used"
    df.to_csv(path, index=False, compression="gzip"); return df


def signals(d):
    s = S.signals(d); c = d.c
    votes = [(c > c.rolling(n).mean()).where(c.rolling(n).mean().notna()) for n in (20, 50, 100, 200)]
    v = pd.concat(votes, axis=1)
    s["TREND_ENS"] = v.mean(axis=1, skipna=True)                       # share of AVAILABLE averages the close is above
    vol = np.log(c).diff().rolling(30).std() * math.sqrt(365)
    s["TREND_ENS_VOL"] = s["TREND_ENS"] * np.minimum(1.0, 0.5 / vol)
    return s


def main():
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), data_start=START, data_end=END, splits=SPLITS, lump={}, dca={}, hour={})
    for sym in ("BTCUSDT", "ETHUSDT"):
        d = klines(sym, "1d"); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True); sig = signals(d)
        for fee in S.FEES:
            for name, w in sig.items():
                r = S.lump(d, w, fee)
                out["lump"][f"{sym}|{name}|{fee}"] = {k: S.metrics(r, a, b) for k, (a, b) in SPLITS.items()}
                out["lump"][f"{sym}|{name}|{fee}"]["position_changes"] = int((np.abs(np.diff(np.nan_to_num(w.values))) > 1e-9).sum())
                out["lump"][f"{sym}|{name}|{fee}"]["avg_exposure"] = round(float(np.nanmean(w.values)), 3)
        for name, w in sig.items(): out["dca"][f"{sym}|{name}"] = S.dca(d, w, 0.001, START, END)
        h = klines(sym, "1h")
        for fee in (0.001, 0.0002):
            r = S.hour_strategy(h, fee); out["hour"][f"{sym}|HOUR_21_23|{fee}"] = {k: S.metrics(r, a, b) for k, (a, b) in SPLITS.items()}
        out[f"{sym}_first_last"] = [str(d.date.iloc[0].date()), str(d.date.iloc[-1].date()), len(d)]
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print("ok", out["BTCUSDT_first_last"], out["ETHUSDT_first_last"])


if __name__ == "__main__":
    main()
