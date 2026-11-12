"""Session (time-of-day) study. Implements PREREGISTRATION.md (this folder).

Usage: CACHE_DIR=<scratch screen_cache with XAUUSDm_/USOILm_ YYYY_MM npz> python3 -I study.py
"""
import json, os, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.environ["CACHE_DIR"]
MONTHS = [f"{y}_{m:02d}" for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
START_MS = int(pd.Timestamp("2025-01-01", tz="UTC").value // 10**6); MIN = 60_000; HOLD = (9 * 60 + 55) * MIN; TOL = 90 * MIN
N_RANDOM = 1000; SEED = 20261112
DAYS = pd.date_range("2025-01-01", "2026-10-31", freq="D", tz="UTC"); ENTRY_DAYS = [x for x in DAYS if x.weekday() in (6, 0, 1, 2, 3)]
DAY0 = np.array([x.value // 10**6 for x in ENTRY_DAYS], dtype=np.int64)


def load(sym):
    parts = [np.load(os.path.join(CACHE, f"{sym}_{m}.npz")) for m in MONTHS]
    t = np.concatenate([x["t"] for x in parts]); b = np.concatenate([x["bid"] for x in parts]); a = np.concatenate([x["ask"] for x in parts])
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    assert t[0] >= START_MS, "pre-2025 data"
    return t, b, a


def windows(t, b, a, e_ms, x_ms, side, m):
    """Vectorised window_trades: returns per-trade net return (fraction) and the entry ms of each valid trade."""
    i = np.searchsorted(t, e_ms); j = np.searchsorted(t, x_ms); n = len(t)
    ok = (i < n) & (j < n)
    i, j, e_ms, x_ms = i[ok], j[ok], e_ms[ok], x_ms[ok]
    ok = (t[i] - e_ms <= TOL) & (t[j] - x_ms <= TOL) & (j > i)
    i, j, e = i[ok], j[ok], e_ms[ok]
    me, se = (b[i] + a[i]) / 2, (a[i] - b[i]) * m; mx, sx = (b[j] + a[j]) / 2, (a[j] - b[j]) * m
    return ((mx - side * sx / 2) - (me + side * se / 2)) * side / me, e


def summ(r):
    eq = np.cumprod(1 + r)
    return dict(trades=int(len(r)), mean_bp=round(float(r.mean() * 1e4), 3), net=round(float(eq[-1] - 1), 4),
                max_dd=round(float((eq / np.maximum.accumulate(eq) - 1).min()), 4), win_rate=round(float((r > 0).mean()), 3),
                t_stat=round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2))


def by_year(r, e):
    y = pd.to_datetime(e, unit="ms", utc=True).year
    return {str(k): summ(r[y == k]) for k in (2025, 2026)}


def session_test(t, b, a, side):
    e_ms = DAY0 + (22 * 60 + 5) * MIN; x_ms = DAY0 + 31 * 60 * MIN   # 07:00 next day
    out = {}
    for m in (1, 2):
        r, e = windows(t, b, a, e_ms, x_ms, side, m); out[f"rule_x{m}"] = summ(r); out[f"rule_x{m}_by_year"] = by_year(r, e)
    rng = np.random.default_rng(SEED); means = []
    for _ in range(N_RANDOM):
        st = DAY0 + rng.integers(0, 1440, size=len(DAY0)) * MIN
        r, _ = windows(t, b, a, st, st + HOLD, side, 2); means.append(r.mean() * 1e4)
    means = np.array(means)
    out["random_x2_mean_bp"] = dict(p50=round(float(np.percentile(means, 50)), 3), p90=round(float(np.percentile(means, 90)), 3),
                                    p95=round(float(np.percentile(means, 95)), 3), p99=round(float(np.percentile(means, 99)), 3))
    out["rule_percentile_vs_random"] = round(float((means < out["rule_x2"]["mean_bp"]).mean() * 100), 1)
    return out


def hour_map(t, b, a):
    mid = (b + a) / 2
    hrs = np.arange(START_MS, int(pd.Timestamp("2026-11-01", tz="UTC").value // 10**6), 3_600_000, dtype=np.int64)
    i = np.searchsorted(t, hrs); ok = i < len(t); i = np.where(ok, i, len(t) - 1)
    valid = ok & (t[i] - hrs <= 10 * MIN); p = np.where(valid, mid[i], np.nan)
    r = p[1:] / p[:-1] - 1; h0 = pd.to_datetime(hrs[:-1], unit="ms", utc=True)
    df = pd.DataFrame(dict(r=r, hour=h0.hour, year=h0.year, wd=h0.weekday)).dropna()
    df = df[~((df.wd == 4) & (df.hour >= 21)) & ~(df.wd == 5) & ~((df.wd == 6) & (df.hour < 22))]
    out = {}
    for yr, g in df.groupby("year"):
        s = g.groupby("hour").r.agg(["mean", "std", "count"])
        out[str(yr)] = {int(h): dict(mean_bp=round(float(v["mean"] * 1e4), 2), t=round(float(v["mean"] / (v["std"] / np.sqrt(v["count"]))), 2), n=int(v["count"]))
                        for h, v in s.iterrows()}
    return out


def main():
    t0 = time.time(); res = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), n_entry_days=len(DAY0))
    for sym in ("XAUUSDm", "USOILm"):
        t, b, a = load(sym)
        res[sym] = dict(ticks=int(len(t)), first=str(pd.Timestamp(t[0], unit="ms")), last=str(pd.Timestamp(t[-1], unit="ms")),
                        asia_long=session_test(t, b, a, 1), hour_map=hour_map(t, b, a))
        if sym == "USOILm": res[sym]["asia_short_info"] = session_test(t, b, a, -1)
        print(sym, f"{time.time() - t0:.0f}s", flush=True)
    g, o = res["XAUUSDm"]["asia_long"], res["USOILm"]["asia_long"]
    res["verdicts"] = dict(
        T1_gold_vs_random="PASS" if g["rule_x2"]["mean_bp"] > g["random_x2_mean_bp"]["p95"] else "FAIL",
        T2_gold_each_year="PASS" if all(g["rule_x2_by_year"][y]["mean_bp"] > 0 for y in ("2025", "2026")) else "FAIL",
        T3_oil_long="PASS" if (o["rule_x2"]["mean_bp"] > o["random_x2_mean_bp"]["p95"] and all(o["rule_x2_by_year"][y]["mean_bp"] > 0 for y in ("2025", "2026"))) else "FAIL")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    for sym in ("XAUUSDm", "USOILm"):
        print(sym, json.dumps({k: v for k, v in res[sym].items() if k != "hour_map"}, indent=1))
    print(json.dumps(res["verdicts"], indent=1)); print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
