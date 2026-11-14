"""Batch 002 (PREREG.md): E005 vol-managed exposure, E006 HAR vs EWMA, E007 HMM regime filter, E008 BTC<->ETH lead-lag,
E009 pre-holiday. Writes results/batch_002.json. One pre-set setting per idea."""
import datetime
import json
import math
import multiprocessing
import os
import sys
import time
import zoneinfo

import holidays
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import common as C  # noqa: E402

SEED = 20261112
BOOT = 2000
PER = list(C.PERIODS) + ["SINCE_2025"]


def in_per(ts, per):
    return ts >= C.SLICE_2025 if per == "SINCE_2025" else C.period_of(ts) == per


def daily(m):
    d = C.load(m)
    x = d[(d.index.hour == 20) & (d.index.minute == 45)]
    s = pd.Series(x.mc.values, index=x.index.normalize())
    return d, s[s.index >= C.START - pd.Timedelta(days=60)]


def sharpe(x):
    x = np.asarray(x)
    return float(x.mean() / x.std(ddof=1) * math.sqrt(252)) if len(x) > 20 and x.std() > 0 else float("nan")


def block_boot_p(a, b, rng, mean_block=20):
    """One-sided p for Sharpe(a) - Sharpe(b) > 0 by the stationary bootstrap (paired days)."""
    n = len(a)
    obs = sharpe(a) - sharpe(b)
    cnt = 0
    for _ in range(BOOT):
        idx = np.empty(n, int)
        i = rng.integers(n)
        for k in range(n):
            idx[k] = i
            i = rng.integers(n) if rng.random() < 1 / mean_block else (i + 1) % n
        if sharpe(a[idx]) - sharpe(b[idx]) <= 0:
            cnt += 1
    return obs, (cnt + 1) / (BOOT + 1)


def exposure_test(m, rule):
    d, s = daily(m)
    sp = C.median_spread_frac(d)
    r = np.log(s).diff()
    simple = s.pct_change()
    if rule == "volman":
        v = r.pow(2).ewm(alpha=0.06, adjust=False).mean()
        sig = np.sqrt(v)
        train_mask = (sig.index >= C.START) & (sig.index < C.PERIODS["TRAIN"][1])
        star = float(sig[train_mask].median())
        w = np.minimum(2.0, star / sig)
    else:
        w = hmm_positions(r)
    w = w.reindex(s.index).fillna(0.0)
    held = w.shift(1)                                  # weight decided at t, applied to the return t -> t+1
    turn = held.diff().abs().fillna(0)
    ret = held * simple - turn * (sp / 2 + C.slip(sp, "primary"))
    ret_s = held * simple - turn * (sp / 2 + C.slip(sp, "stress")) - held.abs() * C.STRESS_PER_DAY
    out = {}
    rng = np.random.default_rng(SEED)
    for per in PER:
        msk = np.array([in_per(t, per) for t in s.index]) & held.notna().values & simple.notna().values
        if msk.sum() < 40:
            out[per] = {"days": int(msk.sum())}
            continue
        a, a_s = ret[msk].values, ret_s[msk].values
        wbar = float(held[msk].mean())
        b = wbar * simple[msk].values
        diff, p = block_boot_p(a, b, rng)
        eq = np.cumsum(a)
        out[per] = {"days": int(msk.sum()), "sharpe_strategy": sharpe(a), "sharpe_strategy_stress": sharpe(a_s), "sharpe_benchmark": sharpe(b),
                    "sharpe_diff": diff, "p_vs_benchmark": p, "mean_daily_bp": float(a.mean() * 1e4), "mean_exposure": wbar,
                    "max_weight": float(held[msk].max()), "max_drawdown_pct": float((np.maximum.accumulate(np.r_[0, eq])[1:] - eq).max() * 100),
                    "annual_turnover": float(turn[msk].sum() / msk.sum() * 252)}
    return out


# ------------------------------------------------------------------------------------------------ HMM
def hmm_fit(x, iters=100, starts=3, rng=None):
    best = None
    for s in range(starts):
        if s == 0:
            q = np.abs(x) > np.quantile(np.abs(x), 0.7)
            mu = np.array([x[~q].mean(), x[q].mean()]); sd = np.array([x[~q].std(), x[q].std()])
        else:
            mu = rng.normal(x.mean(), x.std(), 2); sd = x.std() * rng.uniform(0.5, 1.5, 2)
        A = np.array([[0.95, 0.05], [0.05, 0.95]]); pi = np.array([0.5, 0.5])
        ll_old = -np.inf
        for _ in range(iters):
            B = np.exp(-0.5 * ((x[:, None] - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi)) + 1e-300
            T = len(x); al = np.zeros((T, 2)); c = np.zeros(T)
            al[0] = pi * B[0]; c[0] = al[0].sum(); al[0] /= c[0]
            for t in range(1, T):
                al[t] = (al[t - 1] @ A) * B[t]; c[t] = al[t].sum(); al[t] /= c[t]
            be = np.ones((T, 2))
            for t in range(T - 2, -1, -1):
                be[t] = (A @ (B[t + 1] * be[t + 1])) / c[t + 1]
            g = al * be; g /= g.sum(1, keepdims=True)
            xi = np.zeros((2, 2))
            for t in range(T - 1):
                z = al[t][:, None] * A * (B[t + 1] * be[t + 1])[None, :] / c[t + 1]
                xi += z
            A = xi / xi.sum(1, keepdims=True); pi = g[0]
            mu = (g * x[:, None]).sum(0) / g.sum(0); sd = np.sqrt((g * (x[:, None] - mu) ** 2).sum(0) / g.sum(0)) + 1e-8
            ll = np.log(c).sum()
            if ll - ll_old < 1e-7:
                break
            ll_old = ll
        if best is None or ll > best[0]:
            best = (ll, mu, sd, A, pi)
    return best[1:]


def hmm_filter(x, mu, sd, A, pi):
    B = np.exp(-0.5 * ((x[:, None] - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi)) + 1e-300
    al = np.zeros((len(x), 2)); a = pi * B[0]; al[0] = a / a.sum()
    for t in range(1, len(x)):
        a = (al[t - 1] @ A) * B[t]; al[t] = a / a.sum()
    return al


def hmm_positions(r):
    r = r.dropna()
    rng = np.random.default_rng(SEED)
    pos = pd.Series(np.nan, index=r.index)
    months = pd.date_range(pd.Timestamp("2023-07-01", tz="UTC"), r.index[-1], freq="MS")
    for mo in months:
        hist = r[r.index < mo]
        if len(hist) < 250:
            continue
        mu, sd, A, pi = hmm_fit(hist.values, rng=rng)
        bull = int(np.argmax(mu))
        upto = r[r.index < mo + pd.offsets.MonthBegin(1)]
        al = hmm_filter(upto.values, mu, sd, A, pi)
        sel = (upto.index >= mo)
        pos[upto.index[sel]] = (al[sel, bull] > 0.5).astype(float)
    return pos


# ------------------------------------------------------------------------------------------------ E006
def e006(m):
    d, s = daily(m)
    lr = np.log(d.mc).diff()
    key = (d.index - pd.Timedelta(hours=21)).floor("D")
    rv = lr.pow(2).groupby(key).sum()
    rv.index = rv.index + pd.Timedelta(days=1)                   # aligned with the 21:00 snapshot that closes the day
    rv.index = rv.index.normalize()
    rv = rv[rv > 0]
    r = np.log(s).diff().dropna()
    ew = r.pow(2).ewm(alpha=0.06, adjust=False).mean()           # sigma^2 for t+1 made at t
    df = pd.DataFrame({"rv": rv}).dropna()
    df["rvw"], df["rvm"] = df.rv.rolling(5).mean(), df.rv.rolling(22).mean()
    df["target"] = df.rv.shift(-1)
    df["ewma_fc"] = ew.reindex(df.index)
    df = df.dropna()
    fc = pd.Series(np.nan, index=df.index)
    for mo in pd.date_range(pd.Timestamp("2023-07-01", tz="UTC"), df.index[-1], freq="MS"):
        tr = df[df.index < mo - pd.Timedelta(days=1)]
        te = df[(df.index >= mo) & (df.index < mo + pd.offsets.MonthBegin(1))]
        if len(tr) < 100 or te.empty:
            continue
        X = np.c_[np.ones(len(tr)), tr[["rv", "rvw", "rvm"]].values]
        b = np.linalg.lstsq(X, tr.target.values, rcond=None)[0]
        fc[te.index] = np.c_[np.ones(len(te)), te[["rv", "rvw", "rvm"]].values] @ b
    df["har_fc"] = fc.clip(lower=df.rv.min())
    df = df.dropna()

    def qlike(y, f):
        return y / f - np.log(y / f) - 1
    out = {}
    for per in PER:
        x = df[[in_per(t, per) for t in df.index]]
        if len(x) < 40:
            out[per] = {"days": len(x)}
            continue
        dl = (qlike(x.target, x.ewma_fc) - qlike(x.target, x.har_fc)).values       # > 0: HAR better
        n = len(dl); mu = dl.mean(); g = dl - mu
        lrv = (g @ g) / n + 2 * sum((1 - k / 6) * (g[k:] @ g[:-k]) / n for k in range(1, 6))
        dm = mu / math.sqrt(lrv / n) if lrv > 0 else 0.0
        out[per] = {"days": n, "qlike_ewma": float(qlike(x.target, x.ewma_fc).mean()), "qlike_har": float(qlike(x.target, x.har_fc).mean()),
                    "loss_reduction": float(mu), "dm_stat": float(dm), "p_vs_benchmark": float(0.5 * math.erfc(dm / math.sqrt(2)))}
    return m, out


# ------------------------------------------------------------------------------------------------ E008
def e008(lead_sym, trade_sym):
    L, T = C.load(lead_sym), C.load(trade_sym)
    sp = C.median_spread_frac(T)
    j = pd.concat([L.mc.rename("l"), T.mc.rename("t")], axis=1, join="inner")
    j = j[j.index >= C.START - pd.Timedelta(days=5)]
    rl, rt = np.log(j.l).diff(), np.log(j.t).diff()
    z = rl / rl.rolling(96).std().shift(1)
    sig = np.where((z >= 2) & (rt < 0.5 * rl), 1, np.where((z <= -2) & (rt > 0.5 * rl), -1, 0))
    idx = T.index
    trades, busy = [], None
    for k in np.flatnonzero(sig):
        t_close = j.index[k] + pd.Timedelta(minutes=15)
        if busy is not None and t_close < busy or t_close < C.START:
            continue
        i = idx.searchsorted(t_close)
        if i + 1 >= len(idx) or idx[i] != t_close or idx[i + 1] != t_close + pd.Timedelta(minutes=15):
            continue
        ao, bo, ao2, bo2 = T.ao.iat[i], T.bo.iat[i], T.ao.iat[i + 1], T.bo.iat[i + 1]
        lo, sh = (bo2 - ao) / ao, (bo - ao2) / bo
        cp, cs = C.slip(sp, "primary"), C.slip(sp, "stress")
        dirn = int(sig[k])
        trades.append({"entry": idx[i], "period": C.period_of(idx[i]), "dir": dirn, "r_long": 1e4 * (lo - cp), "r_short": 1e4 * (sh - cp),
                       "r": 1e4 * ((lo if dirn > 0 else sh) - cp), "r_stress": 1e4 * ((lo if dirn > 0 else sh) - cs)})
        busy = idx[i + 1]
    rng = np.random.default_rng(SEED)
    out = {}
    for per in PER:
        sel = [t for t in trades if in_per(t["entry"], per)]
        st = C.stats([t["r"] for t in sel])
        if len(sel) >= 2:
            lo = np.array([t["r_long"] for t in sel]); sh = np.array([t["r_short"] for t in sel]); sg = np.array([t["dir"] for t in sel])
            act = np.where(sg > 0, lo, sh).mean()
            fl = rng.choice([-1, 1], size=(1000, len(sel)))
            perm = np.where(fl * sg > 0, lo, sh).mean(1)
            st["p_vs_benchmark"] = float((np.sum(perm >= act) + 1) / 1001)
            st["mean_stress_bp"] = float(np.mean([t["r_stress"] for t in sel]))
        out[per] = st
    return f"{lead_sym}->{trade_sym}", out


# ------------------------------------------------------------------------------------------------ E009
def e009(m):
    d = C.load(m)
    sp = C.median_spread_frac(d)
    cal, tz, hhmm = (("XETR", "Europe/Berlin", (17, 30)) if m == "DE30m" else ("NYSE", "America/New_York", (16, 0)))
    Z = zoneinfo.ZoneInfo(tz)
    hol = holidays.financial_holidays(cal, years=range(2022, 2027))
    days = [d0 for d0 in pd.date_range("2022-12-01", "2026-11-10", freq="D").date if d0.weekday() < 5 and d0 not in hol]
    pre = set()
    for h in hol:
        prev = [x for x in days if x < h]
        if prev:
            pre.add(prev[-1])

    def leg(day_prev, day):
        t0 = pd.Timestamp(datetime.datetime(day_prev.year, day_prev.month, day_prev.day, *hhmm, tzinfo=Z)).tz_convert("UTC")
        t1 = pd.Timestamp(datetime.datetime(day.year, day.month, day.day, *hhmm, tzinfo=Z)).tz_convert("UTC")
        # amendment (data availability): the last 15-minute open at or before the clock time that day, within 4 hours
        i, k = d.index.searchsorted(t0, side="right") - 1, d.index.searchsorted(t1, side="right") - 1
        if i < 0 or k < 0 or t0 - d.index[i] > pd.Timedelta(hours=4) or t1 - d.index[k] > pd.Timedelta(hours=4) or k <= i:
            return None
        t0 = d.index[i]
        return t0, (d.bo.iat[k] - d.ao.iat[i]) / d.ao.iat[i]
    allr = []
    for a, b in zip(days[:-1], days[1:]):
        x = leg(a, b)
        if x and x[0] >= C.START:
            allr.append((x[0], b in pre, 1e4 * (x[1] - C.slip(sp, "primary")), 1e4 * (x[1] - C.slip(sp, "stress") - C.STRESS_PER_DAY)))
    rng = np.random.default_rng(SEED)
    out = {}
    for per in PER:
        ev = [x for x in allr if x[1] and in_per(x[0], per)]
        pool = np.array([x[2] for x in allr if not x[1] and in_per(x[0], per)])
        st = C.stats([x[2] for x in ev])
        if len(ev) >= 2 and len(pool) > 10:
            act = np.mean([x[2] for x in ev])
            sims = np.array([rng.choice(pool, len(ev), replace=False).mean() for _ in range(1000)])
            st["p_vs_benchmark"] = float((np.sum(sims >= act) + 1) / 1001)
            st["mean_stress_bp"] = float(np.mean([x[3] for x in ev]))
            st["ordinary_day_mean_bp"] = float(pool.mean())
        out[per] = st
    return m, out


def e005(m):
    return m, exposure_test(m, "volman")


def e007(m):
    return m, exposure_test(m, "hmm")


def main():
    t0 = time.time()
    out = {"meta": {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "boot": BOOT}}
    path = os.path.join(HERE, "results", "batch_002.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with multiprocessing.Pool(4) as pool:
        for name, fn, args in (("E006", e006, C.MARKETS), ("E009", e009, ["US500m", "USTECm", "DE30m"]), ("E005", e005, C.MARKETS),
                               ("E007", e007, C.MARKETS)):
            out[name] = dict(pool.map(fn, args))
            json.dump(out, open(path, "w"), indent=1, default=str)
            print(name, "done", round(time.time() - t0), flush=True)
        out["E008"] = dict(pool.starmap(e008, [("BTCUSDm", "ETHUSDm"), ("ETHUSDm", "BTCUSDm")]))
    json.dump(out, open(path, "w"), indent=1, default=str)
    print("E008 done", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
