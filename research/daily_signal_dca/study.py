"""Daily signal DCA bot: backtest of pre-registered, literature-based signals (spot, 1x). Implements PREREGISTRATION.md.

Usage: python3 -I study.py      (downloads Binance klines into data/ on first run)
"""
import csv, gzip, json, math, os, ssl, time, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data"); os.makedirs(DATA, exist_ok=True)
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
START, MID, END = "2018-01-01", "2022-01-01", "2026-11-01"
FEES = [0.001, 0.002]; DCA_PER_DAY = 10.0


def klines(sym, iv):
    path = os.path.join(DATA, f"{sym}_{iv}.csv.gz")
    if os.path.exists(path): return pd.read_csv(path)
    rows, t = [], 1502928000000; end = int(pd.Timestamp(END, tz="UTC").value // 10**6)
    while t < end:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={iv}&startTime={t}&limit=1000"
        r = json.loads(urllib.request.urlopen(url, timeout=30, context=CTX).read())
        if not r: break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4])] for x in r]; t = r[-1][0] + 1
    df = pd.DataFrame(rows, columns=["t", "o", "h", "l", "c"]).drop_duplicates("t")
    df = df[df.t < end]; df.to_csv(path, index=False, compression="gzip"); return df


def rsi(c, n):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def signals(d):
    c = d.c; s = {}
    smas = {n: c.rolling(n).mean() for n in (20, 50, 100, 200)}
    s["TREND_ENS"] = sum((c > smas[n]).astype(float) for n in smas) / 4
    s["SMA50"] = (c > smas[50]).astype(float); s["SMA200"] = (c > smas[200]).astype(float)
    hi, lo = c == c.rolling(10).max(), c == c.rolling(10).min()
    st = pd.Series(np.where(hi, 1.0, np.where(lo, 0.0, np.nan)), index=c.index).ffill().fillna(0.0); s["MAX10"] = st
    s["MOM1"] = (c.pct_change() > 0).astype(float)
    r2 = rsi(c, 2); st = pd.Series(np.where(r2 < 10, 1.0, np.where(r2 > 70, 0.0, np.nan)), index=c.index).ffill().fillna(0.0); s["REV_RSI2"] = st
    vol = np.log(c).diff().rolling(30).std() * math.sqrt(365)
    s["TREND_ENS_VOL"] = s["TREND_ENS"] * np.minimum(1.0, 0.5 / vol)
    s["BUY_HOLD"] = pd.Series(1.0, index=c.index)
    return s


def lump(d, w, fee):
    """w[i] decided at close of day i, held from open i+1 to open i+2. Returns daily returns indexed by day i+1."""
    o = d.o.values; ret = np.zeros(len(d)); w = np.nan_to_num(w.values)
    prev = 0.0
    for i in range(len(d) - 2):
        cost = abs(w[i] - prev) * fee; prev = w[i]
        ret[i + 1] = (1 - cost) * (1 + w[i] * (o[i + 2] / o[i + 1] - 1)) - 1
    return pd.Series(ret, index=d.date)


def hour_strategy(h, fee):
    h = h.copy(); h["dt"] = pd.to_datetime(h.t, unit="ms", utc=True); h["date"] = h.dt.dt.normalize(); h["hr"] = h.dt.dt.hour
    o21 = h[h.hr == 21].set_index("date").o; o23 = h[h.hr == 23].set_index("date").o
    j = pd.concat([o21, o23], axis=1, keys=["a", "b"]).dropna()
    r = (1 - fee) * (1 - fee) * (j.b / j.a) - 1
    return r


def metrics(r, s, e):
    r = r[(r.index >= pd.Timestamp(s, tz="UTC")) & (r.index < pd.Timestamp(e, tz="UTC"))]
    eq = (1 + r).cumprod(); yrs = len(r) / 365
    dd = float((eq / eq.cummax() - 1).min())
    return dict(total_return=round(float(eq.iloc[-1] - 1), 4), cagr=round(float(eq.iloc[-1] ** (1 / yrs) - 1), 4),
                sharpe=round(float(r.mean() / r.std() * math.sqrt(365)), 3) if r.std() > 0 else None, max_dd=round(dd, 4), days=len(r))


def dca(d, w, fee, s, e):
    m = (d.date >= pd.Timestamp(s, tz="UTC")) & (d.date < pd.Timestamp(e, tz="UTC")); dd = d[m].reset_index(drop=True); ww = np.nan_to_num(w[m].values)
    o = dd.o.values; coin = cash = contributed = 0.0; worst = 0.0; trades = 0
    for i in range(1, len(dd)):
        cash += DCA_PER_DAY; contributed += DCA_PER_DAY
        V = coin * o[i] + cash; target = ww[i - 1] * V; delta = target - coin * o[i]
        if abs(delta) > 1e-9:
            if abs(delta) > DCA_PER_DAY * 1.5: trades += 1
            cost = abs(delta) * fee; coin += delta / o[i]; cash -= delta + cost
        V = coin * o[i] + cash; worst = min(worst, (V - contributed) / contributed)
    V = coin * o[-1] + cash
    return dict(contributed=round(contributed, 2), final_value=round(V, 2), profit_pct=round(V / contributed - 1, 4), worst_vs_contributed=round(worst, 4), big_trades=trades)


def main():
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), periods=dict(full=[START, END], early=[START, MID], late=[MID, END]), lump={}, dca={}, hour={})
    for sym in ("BTCUSDT", "ETHUSDT"):
        d = klines(sym, "1d"); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True)
        sig = signals(d)
        for fee in FEES:
            for name, w in sig.items():
                r = lump(d, w, fee)
                trades = int((np.abs(np.diff(np.nan_to_num(w.values))) > 1e-9).sum())
                out["lump"][f"{sym}|{name}|{fee}"] = dict(full=metrics(r, START, END), early=metrics(r, START, MID), late=metrics(r, MID, END),
                                                         position_changes=trades, avg_exposure=round(float(np.nanmean(w[d.date >= pd.Timestamp(START, tz='UTC')])), 3))
        for name, w in sig.items():
            for per, (s, e) in (("full", (START, END)), ("late", (MID, END))):
                out["dca"][f"{sym}|{name}|{per}"] = dca(d, w, 0.001, s, e)
        h = klines(sym, "1h")
        for fee in (0.001, 0.0002):
            r = hour_strategy(h, fee)
            out["hour"][f"{sym}|HOUR_21_23|{fee}"] = dict(full=metrics(r, START, END), early=metrics(r, START, MID), late=metrics(r, MID, END))
    L = out["lump"]
    def ok(sym, per):
        a, b = L[f"{sym}|TREND_ENS|0.001"][per], L[f"{sym}|BUY_HOLD|0.001"][per]
        return bool(a["sharpe"] > b["sharpe"] and a["max_dd"] > b["max_dd"])
    checks = dict(btc_early=ok("BTCUSDT", "early"), btc_late=ok("BTCUSDT", "late"), eth_late=ok("ETHUSDT", "late"))
    out["primary_checks"] = checks; out["PASS"] = bool(all(checks.values()))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print(json.dumps(checks), "PASS" if out["PASS"] else "FAIL")


if __name__ == "__main__":
    main()
