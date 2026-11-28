"""Batch 001 (PREREG.md): D001 pairs, D002 cross-market relative strength, D003 regime-adaptive trend/MR,
D004 walk-forward logistic model. Writes results/batch_001.json. No parameter search."""
import json
import math
import multiprocessing
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import common as C  # noqa: E402

RUNS = 1000
RNG_SEED = 20261112


# ------------------------------------------------------------------------------------------------ helpers
def leg_returns(d, t_in, t_out):
    """Executable long and short returns between the first 15m opens at/after t_in and t_out."""
    idx = d.index
    i, j = idx.searchsorted(t_in), idx.searchsorted(t_out)
    if i >= len(idx) or j >= len(idx) or j <= i:
        return None
    ao_i, bo_i, ao_j, bo_j = d.ao.iat[i], d.bo.iat[i], d.ao.iat[j], d.bo.iat[j]
    return (bo_j - ao_i) / ao_i, (bo_i - ao_j) / bo_i, idx[i], idx[j]


def per_period(rows, key_r, key_stress, pfun):
    """rows: list of dicts with 'entry' timestamp; returns {period: stats(+p)} plus the 2025+ slice."""
    out = {}
    for per in list(C.PERIODS) + ["SINCE_2025"]:
        sel = [r for r in rows if (r["period"] == per if per != "SINCE_2025" else r["entry"] >= C.SLICE_2025)]
        s = C.stats([r[key_r] for r in sel])
        if len(sel) >= 2:
            s["mean_stress_bp"] = float(np.mean([r[key_stress] for r in sel]))
            s["p_vs_benchmark"] = pfun(sel)
        out[per] = s
    return out


def signflip_p(sel, rng):
    lo = np.array([r["r_long"] for r in sel])
    sh = np.array([r["r_short"] for r in sel])
    sg = np.array([r["dir"] for r in sel])
    act = np.where(sg > 0, lo, sh).mean()
    flips = rng.choice([-1, 1], size=(RUNS, len(sel)))
    perm = np.where(flips * sg > 0, lo, sh).mean(axis=1)
    return float((np.sum(perm >= act) + 1) / (RUNS + 1))


# ------------------------------------------------------------------------------------------------ D001
def d001(pair):
    a_sym, b_sym = pair
    A, B = C.load(a_sym), C.load(b_sym)
    sa, sb = C.median_spread_frac(A), C.median_spread_frac(B)
    # hourly closes: the 15m candle starting at hh:45, its mid close; both legs required
    def hourly(d):
        x = d[d.index.minute == 45]
        return pd.Series(x.mc.values, index=x.index + pd.Timedelta(minutes=15))
    ha, hb = hourly(A), hourly(B)
    h = pd.concat([ha, hb], axis=1, join="inner").dropna()
    h.columns = ["a", "b"]
    h = h[h.index >= C.START - pd.Timedelta(days=60)]
    s = np.log(h.a) - np.log(h.b)
    mu, sd = s.rolling(480).mean().shift(1), s.rolling(480).std().shift(1)
    z = ((s - mu) / sd).values
    times = h.index
    # roll / jump diagnostic
    ds = s.diff()
    jump = (ds.abs() > 6 * ds.rolling(480).std().shift(1)).values
    trades, pos, t_in, k_in, d_in = [], 0, None, None, 0
    for k in range(len(times)):
        if np.isnan(z[k]) or times[k] < C.START:
            continue
        if pos == 0:
            if z[k] >= 2:
                pos, t_in, k_in = -1, times[k], k
            elif z[k] <= -2:
                pos, t_in, k_in = 1, times[k], k
            continue
        held = (times[k] - t_in) / pd.Timedelta(hours=1)
        cross = (pos == -1 and z[k] <= 0) or (pos == 1 and z[k] >= 0)
        if cross or abs(z[k]) >= 4 or held >= 120:
            ra, rb = leg_returns(A, t_in, times[k]), leg_returns(B, t_in, times[k])
            if ra and rb:
                # pos = +1: long A, short B; pos = -1: short A, long B
                gross_dir = 0.5 * ((ra[0] if pos > 0 else ra[1]) + (rb[1] if pos > 0 else rb[0]))
                gross_opp = 0.5 * ((ra[1] if pos > 0 else ra[0]) + (rb[0] if pos > 0 else rb[1]))
                days = (ra[3] - ra[2]) / pd.Timedelta(days=1)
                cp = 0.5 * (C.slip(sa, "primary") + C.slip(sb, "primary"))
                cs = 0.5 * (C.slip(sa, "stress") + C.slip(sb, "stress")) + C.STRESS_PER_DAY * days
                trades.append({"entry": ra[2], "period": C.period_of(ra[2]), "dir": pos, "hours": held,
                               "r": 1e4 * (gross_dir - cp), "r_stress": 1e4 * (gross_dir - cs), "r_opp": 1e4 * (gross_opp - cp),
                               "exit_reason": "zero" if cross else ("stop" if abs(z[k]) >= 4 else "time"),
                               "spans_jump": bool(jump[k_in:k + 1].any())})
            pos = 0
    rng = np.random.default_rng(RNG_SEED)
    hour_list = [t for t in times if t >= C.START]

    def bench_p(sel):
        act = np.mean([r["r"] for r in sel])
        per = sel[0]["period"] if all(r["period"] == sel[0]["period"] for r in sel) else None
        pool = [t for t in hour_list if (per is None and t >= C.SLICE_2025) or (per and C.period_of(t) == per)]
        means = []
        cp = 0.5 * (C.slip(sa, "primary") + C.slip(sb, "primary"))
        for _ in range(RUNS // 5):                         # 200 runs (pairs are slow to evaluate)
            v = []
            for r in sel:
                t0 = pool[rng.integers(len(pool))]
                t1 = t0 + pd.Timedelta(hours=r["hours"])
                ra, rb = leg_returns(A, t0, t1), leg_returns(B, t0, t1)
                if ra and rb:
                    v.append(1e4 * (0.5 * ((ra[0] if r["dir"] > 0 else ra[1]) + (rb[1] if r["dir"] > 0 else rb[0])) - cp))
            if v:
                means.append(np.mean(v))
        return float((np.sum(np.array(means) >= act) + 1) / (len(means) + 1))
    res = per_period(trades, "r", "r_stress", bench_p)
    diag = {"hours_both_quoted": int(len(h)), "spread_jumps_detected": int(jump.sum()),
            "trades_spanning_a_jump": int(sum(t["spans_jump"] for t in trades)),
            "exit_reasons": {k: sum(t["exit_reason"] == k for t in trades) for k in ("zero", "stop", "time")},
            "median_spread_frac": {a_sym: sa, b_sym: sb}}
    return f"{a_sym}/{b_sym}", {"results": res, "diagnostics": diag}


# ------------------------------------------------------------------------------------------------ D002
def d002():
    snaps, spreads = {}, {}
    for m in C.MARKETS:
        d = C.load(m)
        spreads[m] = C.median_spread_frac(d)
        x = d[(d.index.hour == 20) & (d.index.minute == 45)]
        snaps[m] = pd.Series(x.mc.values, index=x.index.normalize())
    P = pd.DataFrame(snaps)
    P = P[P.count(axis=1) >= 8]
    R = np.log(P).diff()
    mondays = [t for t in P.index if t.weekday() == 0 and t >= C.START]
    weeks = []
    w_prev = pd.Series(0.0, index=P.columns)
    rng = np.random.default_rng(RNG_SEED)
    perm_store = []
    for k in range(len(mondays) - 1):
        t, t2 = mondays[k], mondays[k + 1]
        hist = R.loc[:t].tail(60)
        ok = [m for m in P.columns if hist[m].count() >= 55 and not np.isnan(P.at[t, m]) and not np.isnan(P.at[t2, m])]
        if len(ok) < 8:
            continue
        ret60 = hist[ok].sum()
        vol = hist[ok].std()
        score = ret60 / (vol * math.sqrt(60))
        fwd = (P.loc[t2, ok] / P.loc[t, ok] - 1)

        def weights(sc):
            o = sc.sort_values()
            lo, hi = list(o.index[:3]), list(o.index[-3:])
            w = pd.Series(0.0, index=P.columns)
            iv = 1 / vol
            w[hi] = iv[hi] / iv[hi].sum()
            w[lo] = -iv[lo] / iv[lo].sum()
            return w
        w = weights(score)
        cost = sum(abs(w[m] - w_prev[m]) * (spreads[m] / 2 + C.slip(spreads[m], "primary")) for m in P.columns)
        cost_s = sum(abs(w[m] - w_prev[m]) * (spreads[m] / 2 + C.slip(spreads[m], "stress")) for m in P.columns) + 2 * 7 * C.STRESS_PER_DAY
        gross = float((w[ok] * fwd).sum())
        perm = []
        for _ in range(RUNS):
            sc = pd.Series(rng.permutation(score.values), index=score.index)
            wp = weights(sc)
            perm.append(float((wp[ok] * fwd).sum()) - cost)      # same cost level as the strategy (conservative proxy)
        weeks.append({"entry": t, "period": C.period_of(t), "r": 1e4 * (gross - cost), "r_stress": 1e4 * (gross - cost_s),
                      "eqw_long": 1e4 * float(fwd.mean()), "top3_long": 1e4 * float((w[w > 0] * fwd.reindex(w[w > 0].index)).sum()),
                      "long": list(w[w > 0].index), "short": list(w[w < 0].index)})
        perm_store.append(1e4 * np.array(perm))
        w_prev = w
    P_ = np.array(perm_store)

    def bench_p(sel):
        idx = [i for i, wk in enumerate(weeks) if wk in sel]
        act = np.mean([weeks[i]["r"] for i in idx])
        perm_means = P_[idx].mean(axis=0)
        return float((np.sum(perm_means >= act) + 1) / (RUNS + 1))
    res = per_period(weeks, "r", "r_stress", bench_p)
    for per in res:
        sel = [w for w in weeks if (w["period"] == per if per != "SINCE_2025" else w["entry"] >= C.SLICE_2025)]
        if sel:
            r = np.array([w["r"] for w in sel])
            res[per]["sharpe_annual"] = float(r.mean() / r.std(ddof=1) * math.sqrt(52)) if len(r) > 2 else None
            res[per]["benchmark_equal_weight_long_mean_bp"] = float(np.mean([w["eqw_long"] for w in sel]))
            res[per]["benchmark_top3_long_mean_bp"] = float(np.mean([w["top3_long"] for w in sel]))
    return "portfolio", {"results": res, "weeks": len(weeks)}


# ------------------------------------------------------------------------------------------------ D003 / D004
def bars(d, hours):
    g = d.copy()
    g["blk"] = g.index.floor(f"{hours}h")
    agg = g.groupby("blk").agg(c=("mc", "last"), n=("mc", "size"))
    agg = agg[agg.n >= max(1, 4 * hours // 4)]
    agg.index = agg.index + pd.Timedelta(hours=hours)                # time at which the candle is complete
    return agg


def run_positions(d, times, pos, spread):
    """pos[k] applies from times[k] (next 15m open) to times[k+1]; returns trades (runs of the same sign)."""
    trades, cur, t_in = [], 0, None
    for k in range(len(times)):
        p = int(pos[k])
        if p != cur:
            if cur != 0:
                lr = leg_returns(d, t_in, times[k])
                if lr:
                    days = (lr[3] - lr[2]) / pd.Timedelta(days=1)
                    cp, cs = C.slip(spread, "primary"), C.slip(spread, "stress") + C.STRESS_PER_DAY * days
                    trades.append({"entry": lr[2], "period": C.period_of(lr[2]), "dir": cur,
                                   "r_long": 1e4 * (lr[0] - cp), "r_short": 1e4 * (lr[1] - cp),
                                   "r": 1e4 * ((lr[0] if cur > 0 else lr[1]) - cp), "r_stress": 1e4 * ((lr[0] if cur > 0 else lr[1]) - cs)})
            cur, t_in = p, times[k]
    return [t for t in trades if t["entry"] >= C.START]


def d003(m):
    d = C.load(m)
    sp = C.median_spread_frac(d)
    b = bars(d, 4)
    c = b.c
    er = (c - c.shift(20)).abs() / c.diff().abs().rolling(20).sum()
    z = (c - c.rolling(20).mean()) / c.rolling(20).std()
    trend = np.sign(c - c.shift(20))
    pos = np.where(er >= 0.35, trend, np.where(er <= 0.15, np.where(z >= 1.5, -1, np.where(z <= -1.5, 1, 0)), 0))
    pos = np.nan_to_num(pos)
    out = {}
    rng = np.random.default_rng(RNG_SEED)
    for name, pp in (("adaptive", pos), ("trend_only (info)", np.where(er >= 0.35, np.nan_to_num(trend), 0)),
                     ("range_only (info)", np.where(er <= 0.15, np.where(z >= 1.5, -1, np.where(z <= -1.5, 1, 0)), 0))):
        tr = run_positions(d, list(b.index), np.nan_to_num(pp), sp)
        out[name] = per_period(tr, "r", "r_stress", lambda sel: signflip_p(sel, rng))
    return m, out


def logit_fit(X, y, lam=1.0, iters=25):
    w = np.zeros(X.shape[1] + 1)
    Xb = np.hstack([np.ones((len(X), 1)), X])
    I = np.eye(len(w))
    I[0, 0] = 0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-Xb @ w))
        g = Xb.T @ (p - y) + lam * I @ w
        H = Xb.T @ (Xb * (p * (1 - p))[:, None]) + lam * I
        w -= np.linalg.solve(H, g)
    return w


def d004(m):
    d = C.load(m)
    sp = C.median_spread_frac(d)
    hb = bars(d, 1)
    c = hb.c
    lr = np.log(c)
    f = pd.DataFrame(index=hb.index)
    f["r1"], f["r4"], f["r24"] = lr.diff(1), lr.diff(4), lr.diff(24)
    f["vol"] = lr.diff().rolling(24).std()
    f["er"] = (c - c.shift(20)).abs() / c.diff().abs().rolling(20).sum()
    f["dist"] = (c - c.rolling(24).mean()) / (c.rolling(24).std())
    hr = (hb.index - pd.Timedelta(hours=1)).hour
    f["hs"], f["hc"] = np.sin(2 * np.pi * hr / 24), np.cos(2 * np.pi * hr / 24)
    # label: mid open of the next hour -> 4 hours later (approximated by candle closes of hours t and t+4)
    fut = lr.shift(-4) - lr
    f["y"] = (fut > 0).astype(float)
    f["label_end"] = pd.Series(hb.index, index=hb.index).shift(-4)
    f = f.replace([np.inf, -np.inf], np.nan).dropna()
    months = pd.date_range(pd.Timestamp("2023-07-01", tz="UTC"), f.index[-1].tz_convert("UTC"), freq="MS")
    feats = ["r1", "r4", "r24", "vol", "er", "dist", "hs", "hc"]
    preds = pd.Series(np.nan, index=f.index)
    for mo in months:
        tr = f[(f.label_end < mo) & (f.index >= C.START)]
        te = f[(f.index >= mo) & (f.index < mo + pd.offsets.MonthBegin(1))]
        if len(tr) < 500 or te.empty:
            continue
        mu, sd = tr[feats].mean(), tr[feats].std().replace(0, 1)
        w = logit_fit(((tr[feats] - mu) / sd).values, tr.y.values)
        Xt = np.hstack([np.ones((len(te), 1)), ((te[feats] - mu) / sd).values])
        preds[te.index] = 1 / (1 + np.exp(-Xt @ w))
    trades, busy = [], None
    rng = np.random.default_rng(RNG_SEED)
    for t, p in preds.dropna().items():
        if busy is not None and t < busy:
            continue
        dirn = 1 if p >= 0.55 else (-1 if p <= 0.45 else 0)
        if dirn == 0:
            continue
        lr_ = leg_returns(d, t, t + pd.Timedelta(hours=4))
        if not lr_:
            continue
        days = (lr_[3] - lr_[2]) / pd.Timedelta(days=1)
        cp, cs = C.slip(sp, "primary"), C.slip(sp, "stress") + C.STRESS_PER_DAY * days
        trades.append({"entry": lr_[2], "period": C.period_of(lr_[2]), "dir": dirn, "r_long": 1e4 * (lr_[0] - cp),
                       "r_short": 1e4 * (lr_[1] - cp), "r": 1e4 * ((lr_[0] if dirn > 0 else lr_[1]) - cp),
                       "r_stress": 1e4 * ((lr_[0] if dirn > 0 else lr_[1]) - cs)})
        busy = lr_[3]
    res = per_period(trades, "r", "r_stress", lambda sel: signflip_p(sel, rng))
    res["share_hours_traded_pct"] = float(len(trades) * 4 / max(1, preds.notna().sum()) * 100)
    return m, res


def main():
    t0 = time.time()
    out = {"meta": {"generated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "runs": RUNS,
                    "periods": {k: [str(a.date()), str(b.date())] for k, (a, b) in C.PERIODS.items()}}}
    with multiprocessing.Pool(4) as pool:
        out["D001"] = dict(pool.map(d001, [("UKOILm", "USOILm"), ("EURUSDm", "GBPUSDm"), ("USTECm", "US500m")]))
        print("D001 done", round(time.time() - t0), flush=True)
        json.dump(out, open(os.path.join(HERE, "results", "batch_001.json"), "w"), indent=1, default=str)
        out["D003"] = dict(pool.map(d003, C.MARKETS))
        print("D003 done", round(time.time() - t0), flush=True)
        json.dump(out, open(os.path.join(HERE, "results", "batch_001.json"), "w"), indent=1, default=str)
        out["D004"] = dict(pool.map(d004, C.MARKETS))
        print("D004 done", round(time.time() - t0), flush=True)
    out["D002"] = dict([d002()])
    print("D002 done", round(time.time() - t0), flush=True)
    json.dump(out, open(os.path.join(HERE, "results", "batch_001.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
