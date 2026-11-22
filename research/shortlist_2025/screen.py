"""Screen of the research shortlist on 2025+ data only. Implements PREREGISTRATION.md (this folder).

Usage: XAU_DIR=<Exness XAUUSDm zips> OIL_DIR=<Exness USOILm zips> CACHE_DIR=<scratch> python3 -I screen.py
"""
import hashlib, json, math, os, sys, time
from multiprocessing import Pool
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "daily_signal_dca")); import study as S  # noqa: E402  (crypto engine; unchanged)
CACHE = os.environ["CACHE_DIR"]; os.makedirs(CACHE, exist_ok=True)
MONTHS = [f"{y}_{m:02d}" for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
START_MS = int(pd.Timestamp("2025-01-01", tz="UTC").value // 10**6)
NY = ZoneInfo("America/New_York"); DAY = 86_400_000; SHIFT = 2 * 3_600_000   # trading day = UTC date of (t + 2h)


def convert(args):
    sym, d, m = args
    out = os.path.join(CACHE, f"{sym}_{m}.npz"); zp = os.path.join(d, f"Exness_{sym}_{m}.zip")
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    if not os.path.exists(out):
        df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"])
        assert (df.sym == sym).all()
        t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
        np.savez(out, t=t, bid=df.bid.to_numpy(np.float64), ask=df.ask.to_numpy(np.float64))
    return m, sha


def ticks(sym, d):
    with Pool(4) as p: shas = dict(p.map(convert, [(sym, d, m) for m in MONTHS]))
    parts = [np.load(os.path.join(CACHE, f"{sym}_{m}.npz")) for m in MONTHS]
    t = np.concatenate([x["t"] for x in parts]); b = np.concatenate([x["bid"] for x in parts]); a = np.concatenate([x["ask"] for x in parts])
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    assert t[0] >= START_MS, "pre-2025 data"
    q = dict(ticks=int(len(t)), first=str(pd.Timestamp(t[0], unit="ms")), last=str(pd.Timestamp(t[-1], unit="ms")), ask_below_bid=int((a < b).sum()),
             spread_median=float(np.median(a - b)), sha256=shas)
    return t, b, a, q


def daily(t, b, a):
    mid = (b + a) / 2; k = (t + SHIFT) // DAY
    st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(t)]
    d = pd.DataFrame(dict(day=pd.to_datetime(k[st] * DAY, unit="ms", utc=True), o=mid[st], h=np.maximum.reduceat(mid, st), l=np.minimum.reduceat(mid, st),
                          c=mid[en - 1], spread_open=(a - b)[st], n=en - st))
    return d[d.n >= 100].reset_index(drop=True)                         # drop stub sessions


def run_daily(d, w, m):
    """w[i] decided at close of day i, executed at open of day i+1 (mid +/- half spread x m). Equity marked at opens."""
    E = 1.0; units = 0.0; eq = [1.0]; trades = 0; w = np.nan_to_num(np.asarray(w, float))
    for i in range(len(d) - 1):
        P = d.o[i + 1]; s = d.spread_open[i + 1] * m
        if i > 0: E = E + units * (P - d.o[i])
        tgt = w[i] * E / P
        if abs(tgt - units) > 1e-12:
            if abs(w[i]) > 0 and (units == 0 or np.sign(tgt) != np.sign(units)): trades += 1
            E -= abs(tgt - units) * s / 2; units = tgt
        eq.append(E)
    return np.array(eq), trades


def stats(eq, trades, start_idx):
    e = eq[start_idx:] / eq[start_idx] if start_idx < len(eq) else np.array([1.0])
    dd = float((e / np.maximum.accumulate(e) - 1).min()); return dict(net=round(float(e[-1] - 1), 4), max_dd=round(dd, 4), trades=trades, days=len(e))


def bh(d, start_idx, m):
    w = np.zeros(len(d)); w[max(start_idx - 1, 0):] = 1.0
    eq, _ = run_daily(d, w, m); return stats(eq, 1, start_idx)


def first_at(t, ms, tol):
    i = int(np.searchsorted(t, ms)); return i if i < len(t) and t[i] - ms <= tol else None


def window_trades(t, b, a, windows, m):
    """windows: list of (entry_ms, exit_ms, side). Long buys ask/sells bid; spread scaled by m around mid."""
    rs = []
    for e_ms, x_ms, side in windows:
        i, j = first_at(t, e_ms, 90 * 60_000), first_at(t, x_ms, 90 * 60_000)
        if i is None or j is None or j <= i: continue
        me, se = (b[i] + a[i]) / 2, (a[i] - b[i]) * m; mx, sx = (b[j] + a[j]) / 2, (a[j] - b[j]) * m
        rs.append(((mx - side * sx / 2) - (me + side * se / 2)) * side / me)
    r = np.array(rs); eq = np.cumprod(1 + r) if len(r) else np.array([1.0])
    return dict(net=round(float(eq[-1] - 1), 4), max_dd=round(float((eq / np.maximum.accumulate(eq) - 1).min()), 4), trades=len(r),
                win_rate=round(float((r > 0).mean()), 3) if len(r) else None, mean_bp=round(float(r.mean() * 1e4), 2) if len(r) else None)


def utc_ms(date, hh, mm, tz):
    return int(pd.Timestamp(year=date.year, month=date.month, day=date.day, hour=hh, minute=mm, tz=tz).tz_convert("UTC").value // 10**6)


def gold(t, b, a):
    d = daily(t, b, a); c = d.c; out = {}
    sma200 = c.rolling(200).mean(); w = (c > sma200).astype(float).where(sma200.notna(), 0.0); s0 = int(sma200.notna().idxmax()) + 1
    for m in (1, 2): eq, tr = run_daily(d, w, m); out[f"G_SMA200|x{m}"] = dict(rule=stats(eq, tr, s0), buy_hold=bh(d, s0, m), active_from=str(d.day[s0].date()))
    tr_ = pd.concat([d.h - d.l, (d.h - c.shift()).abs(), (d.l - c.shift()).abs()], axis=1).max(axis=1); atr = tr_.ewm(alpha=1 / 14, adjust=False).mean()
    sma20 = c.rolling(20).mean(); entry_sig = (c > c.shift(50)) & (sma20 > sma20.shift(5))
    w = np.zeros(len(d)); pos = False; ep = pk = 0.0; held = 0
    for i in range(len(d)):
        if pos:
            held += 1; pk = max(pk, c[i])
            if c[i] < ep - 2 * atr[i] or c[i] < pk - 1.5 * atr[i] or held >= 30: pos = False
        elif bool(entry_sig[i]): pos, ep, pk, held = True, c[i], c[i], 0
        w[i] = 1.0 if pos else 0.0
    s0 = 55
    for m in (1, 2): eq, tr = run_daily(d, w, m); out[f"G_MOM50_ATR|x{m}"] = dict(rule=stats(eq, tr, s0), buy_hold=bh(d, s0, m), active_from=str(d.day[s0].date()))
    w = d.day.dt.month.isin([9, 11]).astype(float).values
    w = np.r_[w[1:], 0.0]                                                 # decided the day before, so the position covers the month
    for m in (1, 2): eq, tr = run_daily(d, w, m); out[f"G_SEPNOV_control|x{m}"] = dict(rule=stats(eq, tr, 1), buy_hold=bh(d, 1, m), active_from=str(d.day[1].date()))
    days = pd.date_range("2025-01-01", "2026-10-31", freq="D", tz="UTC")
    asia = [(utc_ms(x, 22, 0, "UTC"), utc_ms(x + pd.Timedelta(days=1), 7, 0, "UTC"), 1) for x in days if x.weekday() in (6, 0, 1, 2, 3)]
    us = [(utc_ms(x, 13, 0, "UTC"), utc_ms(x, 21, 0, "UTC"), 1) for x in days if x.weekday() < 5]
    for m in (1, 2):
        out[f"G_ASIA_long|x{m}"] = dict(rule=window_trades(t, b, a, asia, m)); out[f"G_US_long|x{m}"] = dict(rule=window_trades(t, b, a, us, m))
    out["_buy_hold_full"] = bh(d, 1, 1); return out, d


def oil(t, b, a):
    d = daily(t, b, a); c = d.c; out = {}
    me = d.groupby(d.day.dt.to_period("M")).tail(1).index.values          # month-end rows
    w = np.zeros(len(d)); cur = 0.0; first = None
    for i in range(len(d)):
        if i in me:
            p = d.day[i].to_period("M"); sig = []
            for k in (1, 3, 12):
                prev = d[d.day.dt.to_period("M") == p - k]
                if prev.empty: sig = None; break
                sig.append(np.sign(c[i] - prev.c.iloc[-1]))
            if sig is not None:
                cur = float(np.mean(sig)); first = first if first is not None else i + 1
        w[i] = cur
    s0 = first if first is not None else len(d) - 1
    for m in (1, 2): eq, tr = run_daily(d, w, m); out[f"O_MOM_BLEND|x{m}"] = dict(rule=stats(eq, tr, s0), buy_hold=bh(d, s0, m), active_from=str(d.day[s0].date()), note="swap not deducted")
    hi55, lo55 = c.rolling(55).max(), c.rolling(55).min(); hi20, lo20 = c.rolling(20).max(), c.rolling(20).min()
    w = np.zeros(len(d)); pos = 0
    for i in range(55, len(d)):
        if pos == 1 and c[i] <= lo20[i]: pos = 0
        if pos == -1 and c[i] >= hi20[i]: pos = 0
        if pos == 0: pos = 1 if c[i] >= hi55[i] else (-1 if c[i] <= lo55[i] else 0)
        w[i] = pos
    for m in (1, 2): eq, tr = run_daily(d, w, m); out[f"O_TURTLE|x{m}"] = dict(rule=stats(eq, tr, 55), buy_hold=bh(d, 55, m), active_from=str(d.day[55].date()), note="swap not deducted")
    mid = (b + a) / 2; wins = []
    for x in pd.date_range("2025-01-01", "2026-10-31", freq="D"):
        if x.weekday() >= 5: continue
        a0, a1 = ((10, 30), (11, 0)) if x.weekday() == 2 else ((9, 30), (10, 0))
        i, j = first_at(t, utc_ms(x, *a0, NY), 5 * 60_000), first_at(t, utc_ms(x, *a1, NY), 5 * 60_000)
        if i is None or j is None: continue
        sgn = int(np.sign(mid[j] - mid[i]))
        if sgn: wins.append((utc_ms(x, 15, 30, NY), utc_ms(x, 16, 0, NY), sgn))
    for m in (1, 2): out[f"O_INTRADAY|x{m}"] = dict(rule=window_trades(t, b, a, wins, m))
    out["_buy_hold_full"] = bh(d, 1, 1); return out, d


def crypto(sym):
    d = pd.read_csv(os.path.join(ROOT, "daily_signal_dca", "from_2025", "data", f"{sym}_1d_from2025.csv.gz")); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True)
    c = d.c; out = {}; sigs = {}
    subs = []
    for L in (5, 10, 20, 30, 60, 90, 150, 250, 360):
        hi, lo = c.shift(1).rolling(L).max(), c.shift(1).rolling(L).min(); s = np.zeros(len(d)); pos = False; stop = 0.0
        for i in range(len(d)):
            if np.isnan(hi[i]): continue
            if pos:
                stop = max(stop, (hi[i] + lo[i]) / 2)
                if c[i] < stop: pos = False
            elif c[i] > hi[i]: pos, stop = True, (hi[i] + lo[i]) / 2
            s[i] = 1.0 if pos else 0.0
        subs.append(s)
    avg = np.mean(subs, axis=0); vol = np.log(c).diff().rolling(90, min_periods=20).std() * math.sqrt(365)
    sigs["C_DONCH_ENS"] = pd.Series(np.minimum(1.0, avg * np.nan_to_num(0.25 / vol, nan=0.0)), index=c.index)
    sigs["C_SMA50"] = (c > c.rolling(50).mean()).astype(float)
    for n in (20, 10): sigs[f"C_MAX{n}"] = (c >= c.rolling(n).max()).astype(float).where(c.rolling(n).max().notna(), 0.0)
    sigs["C_MIN10_control"] = (c <= c.rolling(10).min()).astype(float).where(c.rolling(10).min().notna(), 0.0)
    sigs["BUY_HOLD"] = pd.Series(1.0, index=c.index)
    start = {"C_DONCH_ENS": 6, "C_SMA50": 50, "C_MAX20": 20, "C_MAX10": 10, "C_MIN10_control": 10, "BUY_HOLD": 1}
    for name, w in sigs.items():
        for fee, tag in ((0.001, "x1"), (0.002, "x2")):
            r = S.lump(d, w, fee); s = str(d.date[start[name]].date()); rr = r[r.index >= pd.Timestamp(s, tz="UTC")]
            eq = (1 + rr).cumprod(); trades = int(((w.diff() > 0) & (w > 0)).sum())
            out[f"{sym}|{name}|{tag}"] = dict(net=round(float(eq.iloc[-1] - 1), 4), max_dd=round(float((eq / eq.cummax() - 1).min()), 4), trades=trades, active_from=s,
                                             avg_exposure=round(float(w[start[name]:].mean()), 3))
    return out


def verdict(res):
    v = {}
    for k in list(res):
        if "|x2" not in k: continue
        base = k.replace("|x2", "")
        r2, r1 = res[k]["rule"], res[base + "|x1"]["rule"]
        if "buy_hold" in res[k]:
            ok = r2["net"] > 0 and r2["max_dd"] > res[k]["buy_hold"]["max_dd"] and r2["trades"] >= 10
        else:
            ok = r1["net"] > 0 and r2["net"] > 0 and r2["trades"] >= 10
        v[base] = "CONSISTENT WITH PUBLISHED EVIDENCE" if ok else "NOT CONFIRMED"
    return v


def crypto_verdict(res, sym):
    v = {}; bhr = res[f"{sym}|BUY_HOLD|x2"]
    for name in ("C_DONCH_ENS", "C_SMA50", "C_MAX20", "C_MAX10", "C_MIN10_control"):
        r = res[f"{sym}|{name}|x2"]
        ok = r["net"] > 0 and r["max_dd"] > bhr["max_dd"] and r["trades"] >= 10
        v[f"{sym}|{name}"] = "CONSISTENT WITH PUBLISHED EVIDENCE" if ok else "NOT CONFIRMED"
    return v


def main():
    t0 = time.time(); res = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()))
    for name, sym, env, fn in (("gold", "XAUUSDm", "XAU_DIR", gold), ("oil", "USOILm", "OIL_DIR", oil)):
        t, b, a, q = ticks(sym, os.environ[env]); r, d = fn(t, b, a)
        res[name] = dict(data=q, daily_rows=len(d), results=r, verdicts=verdict({k: v for k, v in r.items() if not k.startswith("_")}))
        print(name, json.dumps(res[name]["verdicts"]), f"{time.time() - t0:.0f}s", flush=True)
        del t, b, a
    res["crypto"] = {}; res["crypto_verdicts"] = {}
    for sym in ("BTCUSDT", "ETHUSDT"):
        r = crypto(sym); res["crypto"].update(r); res["crypto_verdicts"].update(crypto_verdict(r, sym))
    print("crypto", json.dumps(res["crypto_verdicts"]))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
