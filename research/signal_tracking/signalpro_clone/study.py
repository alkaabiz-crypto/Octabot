"""SignalPro-style template clone: one-year Exness XAUUSDm tick backtest.

Implements PREREGISTRATION.md exactly (committed before any result). Research only: no orders, no accounts.

Usage: TICK_DIR=<dir with Exness_XAUUSDm_YYYY_MM.zip> CACHE_DIR=<scratch dir> python3 -I study.py
"""
import glob, hashlib, json, math, os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TICK_DIR = os.environ["TICK_DIR"]
CACHE = os.environ["CACHE_DIR"]
MONTHS = ["2025_11", "2025_12", "2026_01", "2026_02", "2026_03", "2026_04", "2026_05", "2026_06", "2026_07", "2026_08", "2026_09", "2026_10"]
HOUR = 3_600_000
RISK, TP1, TP2, TP3_MIN, ROUND = 10.0, 5.0, 10.0, 30.0, 10.0
MAX_MS = 7 * 86_400_000
ENTRY_WINDOW_MS = 60_000
N_RANDOM, N_BOOT, SEED = 2000, 10000, 20261110


# ---------------------------------------------------------------- data
def convert(m):
    zp = os.path.join(TICK_DIR, f"Exness_XAUUSDm_{m}.zip")
    out = os.path.join(CACHE, f"{m}.npz")
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    if not os.path.exists(out):
        df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"])
        assert (df["sym"] == "XAUUSDm").all(), "unexpected symbol"
        t = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
        assert 1.7e12 < t[0] < 1.9e12, "timestamp unit check failed"
        np.savez(out, t=t, bid=df["bid"].to_numpy(np.float64), ask=df["ask"].to_numpy(np.float64))
    return m, sha, os.path.getsize(zp)


def load():
    os.makedirs(CACHE, exist_ok=True)
    with Pool(4) as p:
        meta = p.map(convert, MONTHS)
    ts, bs, as_, q = [], [], [], {}
    for m, sha, size in meta:
        d = np.load(os.path.join(CACHE, f"{m}.npz"))
        t, b, a = d["t"], d["bid"], d["ask"]
        q[m] = dict(sha256=sha, zip_bytes=size, ticks=int(len(t)), ask_below_bid=int((a < b).sum()), nonpositive=int(((a <= 0) | (b <= 0)).sum()),
                    out_of_order=int((np.diff(t) < 0).sum()), first=fmt(t[0]), last=fmt(t[-1]),
                    spread_median=round(float(np.median(a - b)), 4), spread_p95=round(float(np.percentile(a - b, 95)), 4), spread_max=round(float((a - b).max()), 4))
        ts.append(t); bs.append(b); as_.append(a)
    t, b, a = np.concatenate(ts), np.concatenate(bs), np.concatenate(as_)
    order = np.argsort(t, kind="stable")
    if not (order == np.arange(len(t))).all():
        t, b, a = t[order], b[order], a[order]
    dup = int(((np.diff(t) == 0) & (np.diff(b) == 0) & (np.diff(a) == 0)).sum())
    return t, b, a, q, dup


def fmt(ms):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ms / 1000))


def hourly(t, bid):
    h = t // HOUR
    starts = np.flatnonzero(np.r_[True, h[1:] != h[:-1]])
    ends = np.r_[starts[1:], len(t)]
    o = bid[starts]; c = bid[ends - 1]
    hi = np.maximum.reduceat(bid, starts); lo = np.minimum.reduceat(bid, starts)
    return h[starts], o, hi, lo, c


# ---------------------------------------------------------------- simulation
def first_hit(x, i, end, lo, hi):
    """First index j in [i, end) with x[j] <= lo or x[j] >= hi, else None. Expanding windows."""
    w = 4096
    while i < end:
        j1 = min(end, i + w)
        seg = x[i:j1]
        m = (seg <= lo) | (seg >= hi)
        if m.any():
            return i + int(np.argmax(m))
        i = j1; w *= 4
    return None


def simulate(x, t, i0, E, tp3, be):
    """BUY-oriented path on series x (for SELL, x and levels are negated). Returns R, outcome, exit index."""
    end = int(np.searchsorted(t, t[i0] + MAX_MS, side="left"))
    targets = [E + TP1, E + TP2, tp3]
    stop = E - RISK; k = 0; pnl = 0.0; i = i0 + 1; outcome = None; j = None
    while k < 3:
        j = first_hit(x, i, end, stop, targets[k])
        if j is None:
            j = end - 1
            pnl += (3 - k) * (x[j] - E)
            outcome = f"TIMEOUT_after_TP{k}" if k else "TIMEOUT"
            if end >= len(t): outcome += "_DATA_END"
            break
        if x[j] <= stop:
            pnl += (3 - k) * (x[j] - E)
            outcome = "STOP" if k == 0 else (f"BE_after_TP{k}" if be else f"STOP_after_TP{k}")
            break
        while k < 3 and x[j] >= targets[k]:
            pnl += targets[k] - E; k += 1
        if be and k >= 1: stop = E
        i = j + 1
    if k == 3: outcome = "TP3"
    return pnl / 3 / RISK, outcome, j


def tp3_level(E, side):
    return math.ceil((E + TP3_MIN) / ROUND) * ROUND if side > 0 else math.floor((E - TP3_MIN) / ROUND) * ROUND


def main():
    t0 = time.time()
    t, bid, ask, q, dup = load()
    mid = (bid + ask) / 2
    neg_ask, neg_mid = -ask, -mid
    hk, o, hi, lo, c = hourly(t, bid)
    print(f"ticks {len(t):,}  hours {len(hk):,}  load {time.time() - t0:.0f}s", flush=True)

    start_ms = int(pd.Timestamp("2025-11-01", tz="UTC").as_unit("ns").value // 1_000_000)
    end_ms = int(pd.Timestamp("2026-11-01", tz="UTC").as_unit("ns").value // 1_000_000)
    rows = []
    for n in range(3, len(hk)):
        C = int((hk[n] + 1) * HOUR)
        if not (start_ms < C <= end_ms): continue
        i0 = int(np.searchsorted(t, C, side="left"))
        if i0 >= len(t) or t[i0] - C > ENTRY_WINDOW_MS: continue
        d1 = 1 if c[n] > o[n] else (-1 if c[n] < o[n] else 0)
        d2 = 1 if c[n] > hi[n - 3:n].max() else (-1 if c[n] < lo[n - 3:n].min() else 0)
        r = dict(candle_close=fmt(C), month=fmt(C)[:7], entry_time=fmt(int(t[i0])), latency_ms=int(t[i0] - C), D1=d1, D2=d2,
                 spread=round(float(ask[i0] - bid[i0]), 4))
        for side, name in ((1, "BUY"), (-1, "SELL")):
            for cost, (xs, entry) in (("net", ((bid, ask[i0]) if side > 0 else (neg_ask, -bid[i0]))),
                                      ("gross", ((mid, mid[i0]) if side > 0 else (neg_mid, -mid[i0])))):
                E_real = entry if side > 0 else -entry
                tp3 = tp3_level(E_real, side) * side
                for mg, be in (("M1", True), ("M2", False)):
                    R, oc, j = simulate(xs, t, i0, entry, tp3, be)
                    r[f"{name}_{mg}_{cost}_R"] = round(R, 4); r[f"{name}_{mg}_{cost}_out"] = oc
                    if cost == "net" and mg == "M1": r[f"{name}_exit"] = fmt(int(t[j])); r[f"{name}_exit_ms"] = int(t[j])
            r[f"{name}_entry"] = round(float(ask[i0] if side > 0 else bid[i0]), 3)
        rows.append(r)
        if len(rows) % 1000 == 0: print(f"  {len(rows)} hours simulated, {time.time() - t0:.0f}s", flush=True)
    df = pd.DataFrame(rows)
    print(f"eligible hours {len(df)}  sim {time.time() - t0:.0f}s", flush=True)

    rng = np.random.default_rng(SEED)

    def stats(R):
        R = np.asarray(R, float); n = len(R)
        if n == 0: return dict(n=0)
        boot = rng.choice(R, size=(N_BOOT, n), replace=True).mean(1)
        w, l = R[R > 0].sum(), -R[R < 0].sum()
        return dict(n=n, mean_R=round(R.mean(), 4), median_R=round(float(np.median(R)), 4), win_rate=round(float((R > 0).mean()), 4),
                    pf=round(w / l, 3) if l > 0 else None, t_stat=round(R.mean() / (R.std(ddof=1) / math.sqrt(n)), 2) if n > 1 else None,
                    ci95_boot=[round(float(np.percentile(boot, 2.5)), 4), round(float(np.percentile(boot, 97.5)), 4)], sum_R=round(R.sum(), 2),
                    usd_per_oz_total=round(R.sum() * RISK, 1))

    def pick(rule, mg, cost):
        s = df[df[rule] != 0]
        R = np.where(s[rule] > 0, s[f"BUY_{mg}_{cost}_R"], s[f"SELL_{mg}_{cost}_R"])
        out = np.where(s[rule] > 0, s[f"BUY_{mg}_{cost}_out"], s[f"SELL_{mg}_{cost}_out"])
        return s, R, out

    res = dict(generated_utc=fmt(int(time.time() * 1000)), data=q, duplicate_ticks=dup, eligible_hours=len(df),
               median_entry_spread=float(df["spread"].median()), median_latency_ms=float(df["latency_ms"].median()), results={})
    trades = []
    for rule in ("D1", "D2"):
        for mg in ("M1", "M2"):
            for cost in ("net", "gross"):
                s, R, out = pick(rule, mg, cost)
                st = stats(R)
                st["outcomes"] = {k: int(v) for k, v in pd.Series(out).value_counts().items()}
                if cost == "net" and mg == "M1":
                    st["monthly_sum_R"] = {m: round(float(v), 2) for m, v in pd.Series(R, index=s["month"].values).groupby(level=0).sum().items()}
                    st["by_side"] = {nm: stats(R[s[rule].values == sd]) for sd, nm in ((1, "BUY"), (-1, "SELL"))}
                    ex = np.where(s[rule] > 0, s["BUY_exit_ms"], s["SELL_exit_ms"])
                    en = pd.to_datetime(s["entry_time"], utc=True).dt.as_unit("ms").astype("int64").values
                    open_ends, overlap = [], 0
                    for a_, b_ in zip(en, ex):
                        open_ends = [e for e in open_ends if e > a_]
                        overlap += bool(open_ends); open_ends.append(b_)
                    st["signals_while_previous_open"] = int(overlap)
                    if rule == "D2":
                        for k, (_, rr) in enumerate(s.iterrows()):
                            sd = "BUY" if rr[rule] > 0 else "SELL"
                            trades.append(dict(candle_close=rr["candle_close"], entry_time=rr["entry_time"], side=sd, entry=rr[f"{sd}_entry"], spread=rr["spread"],
                                               R_M1_net=rr[f"{sd}_M1_net_R"], out_M1_net=rr[f"{sd}_M1_net_out"], R_M2_net=rr[f"{sd}_M2_net_R"],
                                               R_M1_gross=rr[f"{sd}_M1_gross_R"], exit_M1=rr[f"{sd}_exit"]))
                res["results"][f"{rule}_{mg}_{cost}"] = st
    # random-direction benchmark on every eligible hour
    for mg in ("M1", "M2"):
        B, S = df[f"BUY_{mg}_net_R"].values, df[f"SELL_{mg}_net_R"].values
        means = np.array([np.where(rng.random(len(df)) < 0.5, B, S).mean() for _ in range(N_RANDOM)])
        res["results"][f"RANDOM_{mg}_net"] = dict(runs=N_RANDOM, hours=len(df), median=round(float(np.median(means)), 4),
                                                   p5=round(float(np.percentile(means, 5)), 4), p95=round(float(np.percentile(means, 95)), 4),
                                                   all_buy_mean=round(float(B.mean()), 4), all_sell_mean=round(float(S.mean()), 4))
    p = res["results"]["D2_M1_net"]; rb = res["results"]["RANDOM_M1_net"]
    checks = dict(mean_positive=p["mean_R"] > 0, ci_above_zero=p["ci95_boot"][0] > 0, beats_random_p95=p["mean_R"] > rb["p95"])
    res["primary_test"] = dict(test="D2 + M1, net of spread", **checks, PASS=all(checks.values()))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    pd.DataFrame(trades).to_csv(os.path.join(HERE, "results", "D2_trades.csv"), index=False)
    df.drop(columns=[c_ for c_ in df.columns if c_.endswith("_exit_ms")]).to_csv(os.path.join(CACHE, "all_hours.csv.gz"), index=False)
    print(json.dumps(res["primary_test"]), f"total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
