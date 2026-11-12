"""Round 2 (IDEAS.md): entry filters on KST + session VWAP BUY, and stand-alone time/event ideas.
usage: GOLD_DATA=<dir> python src/ideas.py"""
import bisect
import csv
import datetime
import json
import math
import os
import random
import statistics
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as G  # noqa: E402
import optimize as O  # noqa: E402

S = G.S
oil = G.oil
FIT = O.FIT


def p_of(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def kst_lines(c):
    n = len(c)
    roc = lambda k: [None] * k + [100 * (c[i] - c[i - k]) / c[i - k] for i in range(k, n)]  # noqa: E731

    def sma(x, k):
        out = [None] * len(x)
        for i in range(k - 1, len(x)):
            w = x[i - k + 1:i + 1]
            if None not in w:
                out[i] = sum(w) / k
        return out
    kst = [None if None in (a, b, d, e) else a + 2 * b + 3 * d + 4 * e
           for a, b, d, e in zip(sma(roc(10), 10), sma(roc(15), 10), sma(roc(20), 10), sma(roc(30), 15))]
    return kst, sma(kst, 9)


def fred(name):
    out = []
    with open(os.path.join(os.environ.get("FRED_DIR", os.path.join(G.ROOT, "data")), f"fred_{name}.csv")) as f:
        for r in csv.DictReader(f):
            v = r[name]
            if v not in ("", "."):
                out.append((datetime.date.fromisoformat(r["observation_date"]), float(v)))
    return out


def falling_flags(g, series, lag_days=2, back=5):
    """Hourly bar i: True if the series' last value dated <= signal day - lag_days is below the value `back` obs earlier."""
    dates = [d for d, _ in series]
    vals = [v for _, v in series]
    out = []
    for t in g.th:
        d = datetime.datetime.fromtimestamp(int(t) + 3600, datetime.timezone.utc).date() - datetime.timedelta(days=lag_days)
        k = bisect.bisect_right(dates, d) - 1
        out.append(k >= back and vals[k] < vals[k - back])
    return out


def filters(g):
    E = g.e
    n = len(E.t)
    out = {}
    hour = [time.gmtime(int(t) + 3600).tm_hour for t in E.t]       # UTC hour of the signal close (= entry time)
    wday = [time.gmtime(int(t) + 3600).tm_wday for t in E.t]
    for name, (a, b) in {"SESSION_ASIA": (0, 7), "SESSION_LONDON": (7, 12), "SESSION_NY": (12, 20), "SESSION_LATE": (20, 24)}.items():
        out[name] = [a <= h < b for h in hour]
    kst, _ = kst_lines(E.c)
    out["KST_BELOW_ZERO"] = [k is not None and k < 0 for k in kst]
    out["KST_ABOVE_ZERO"] = [k is not None and k > 0 for k in kst]
    h4 = oil.aggregate(E.t, E.o, E.h, E.l, E.c, E.v, 14400)
    k4, s4 = kst_lines(h4.c)
    f = []
    for i in range(n):
        k = bisect.bisect_right(h4.t, E.t[i] + 3600 - 14400) - 1
        f.append(k >= 0 and k4[k] is not None and s4[k] is not None and k4[k] > s4[k])
    out["H4_KST_UP"] = f
    d = oil.aggregate(E.t, E.o, E.h, E.l, E.c, E.v, 86400)
    e50 = S.ema_from_first(d.c, 50)
    f = []
    for i in range(n):
        k = bisect.bisect_right(d.t, E.t[i] + 3600 - 86400) - 1
        f.append(k >= 50 and e50[k] is not None and d.c[k] > e50[k])
    out["DAILY_EMA50"] = f
    atr = g.atr
    med = [None] * n
    for i in range(100, n):
        w = [x for x in atr[i - 99:i + 1] if x is not None]
        med[i] = statistics.median(w) if len(w) > 50 else None
    out["VOL_HIGH"] = [m is not None and a is not None and a > m for a, m in zip(atr, med)]
    out["VOL_LOW"] = [m is not None and a is not None and a < m for a, m in zip(atr, med)]
    out["NEAR_VWAP"] = [w is not None and a is not None and c - w <= a for c, w, a in zip(E.c, g.vwap, atr)]
    out["NO_FRIDAY"] = [w != 4 for w in wday]
    out["NO_MONDAY"] = [w != 0 for w in wday]
    out["REAL_YIELD_FALLING"] = falling_flags(g, fred("DFII10"))
    out["DOLLAR_FALLING"] = falling_flags(g, fred("DTWEXBGS"))
    return out


# ------------------------------------------------------------------------------------------------- part B
def long_trade(g, t0, t1, cost="primary"):
    """Buy at the 15m open at t0 (ask), sell at the 15m open at/after t1 (bid), 2 x ATR14 stop."""
    q, tq = g.q, g.tq
    j = int(np.searchsorted(tq, t0))
    if j >= len(tq) or tq[j] - t0 > 900:
        return None
    k = int(np.searchsorted(g.th, t0, side="right")) - 2
    if k < 0 or not g.atr_np[k] > 0:
        return None
    a = g.atr_np[k]
    entry, risk = q["ao"][j], 2 * a
    sl = entry - risk
    tstart = tq[j]
    while j < len(tq) and tq[j] < t1:
        if q["bl"][j] <= sl:
            px = min(q["bo"][j], sl)
            return (px - entry) / risk - (G.SLIP[cost] + G.SWAP_PER_DAY[cost] * (tq[j] - tstart) / 86400) * entry / risk
        j += 1
    if j >= len(tq):
        return None
    return (q["bo"][j] - entry) / risk - (G.SLIP[cost] + G.SWAP_PER_DAY[cost] * (tq[j] - tstart) / 86400) * entry / risk


def standalone(g, windows, w0, w1, runs=300, seed=20261112):
    sel = [(a, b) for a, b in windows if w0 <= a < w1]
    rs = [long_trade(g, a, b) for a, b in sel]
    keep = [(w, r) for w, r in zip(sel, rs) if r is not None]
    if len(keep) < 5:
        return {"trades": len(keep)}
    rp = np.array([r for _, r in keep])
    rst = np.array([long_trade(g, a, b, "stress") for (a, b), _ in keep])
    tq = g.tq
    rnd = random.Random(seed)
    lo, hi = int(np.searchsorted(tq, w0)), int(np.searchsorted(tq, w1))
    by_q = {}
    for j in range(lo, hi, 4):
        by_q.setdefault(S.quarter(int(tq[j])), []).append(int(tq[j]))
    means = []
    for _ in range(runs):
        v = []
        for (a, b), _r in keep:
            pool = by_q.get(S.quarter(a), [])
            for _x in range(20):
                if not pool:
                    break
                s = rnd.choice(pool)
                r = long_trade(g, s, s + (b - a))
                if r is not None:
                    v.append(r)
                    break
        if v:
            means.append(statistics.mean(v))
    mu, sd = statistics.mean(means), statistics.pstdev(means)
    return {"trades": len(rp), "win_rate_pct": float((rp > 0).mean() * 100), "expectancy_r": float(rp.mean()),
            "expectancy_stress_r": float(rst.mean()), "total_r": float(rp.sum()), "random_mean_r": mu,
            "z": (float(rp.mean()) - mu) / sd if sd > 0 else 0.0}


def main():
    g = G.Gold(os.path.join(os.environ.get("GOLD_DATA", ""), "XAUUSDm_15m.csv.gz"))
    ev = G.all_events()
    R = G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])
    end = int(g.th[-1]) + 3600
    summ = json.load(open(os.path.join(G.ROOT, "reports", "summary.json")))
    chosen = summ["chosen"]
    cp = dict(x.split("=") for x in chosen.split("|"))
    chosen_p = (float(cp["stop"]), float(cp["trail"]), int(cp["be"]), int(cp["time"]), int(cp["lose"]), cp["news"])
    exits = {"ORIGINAL": O.BASE, "CHOSEN": chosen_p}
    flt = filters(g)
    res = {}
    for fname, ok in flt.items():
        sig = np.array([b and o for b, o in zip(g.buy, ok)])
        for ename, p in exits.items():
            r = {}
            for per, (w0, w1) in (("fit", FIT), ("test", (FIT[1], end))):
                L = R.legs(p, w0, w1, sig=sig)
                rp, rs = R.r(L, "primary"), R.r(L, "stress")
                if len(rp) < 5:
                    r[per] = {"trades": len(rp)}
                    continue
                mu, sd = R.bench(p, L, w0, w1)
                r[per] = {"trades": len(rp), "win_rate_pct": float((rp > 0).mean() * 100), "expectancy_r": float(rp.mean()),
                          "expectancy_stress_r": float(rs.mean()), "total_r": float(rp.sum()),
                          "max_drawdown_r": G.max_drawdown(rp), "random_mean_r": mu, "z": (float(rp.mean()) - mu) / sd if sd > 0 else 0.0}
            res[f"A|{fname}|{ename}"] = r
            print(fname, ename, {k: (v["trades"], round(v.get("expectancy_r", 0), 3), round(v.get("z", 0), 2)) for k, v in r.items()}, flush=True)
    # part B
    days = range(int(g.tq[0]) // 86400 + 1, int(g.tq[-1]) // 86400)
    asia = [(d * 86400 - 3600, d * 86400 + 7 * 3600) for d in days if time.gmtime(d * 86400).tm_wday < 5]
    pre = {k: [(t - 86400, t - 900) for t in ev[k]] for k in ("FOMC", "CPI", "NFP")}
    for name, wins in (("ASIA_DRIFT", asia), ("PRE_FOMC", pre["FOMC"]), ("PRE_CPI", pre["CPI"]), ("PRE_NFP", pre["NFP"])):
        res[f"B|{name}"] = {"fit": standalone(g, wins, *FIT), "test": standalone(g, wins, FIT[1], end)}
        print(name, {k: (v["trades"], round(v.get("expectancy_r", 0), 3), round(v.get("z", 0), 2)) for k, v in res[f"B|{name}"].items()}, flush=True)
    # decision (IDEAS.md)
    passed = [k for k, r in res.items() if r["fit"].get("z", 0) >= 1.645 and r["fit"].get("expectancy_stress_r", -1) > 0
              and "z" in r["test"]]
    sys.path.insert(0, os.path.join(G.RESEARCH, "long_history", "src"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("lr", os.path.join(G.RESEARCH, "long_history", "src", "report.py"))
    lr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lr)
    rej = lr.benjamini_hochberg([p_of(res[k]["test"]["z"]) for k in passed]) if passed else set()
    confirmed = [passed[i] for i in sorted(rej) if res[passed[i]]["test"].get("expectancy_stress_r", -1) > 0]
    with open(os.path.join(G.ROOT, "reports", "ideas.json"), "w") as f:
        json.dump({"meta": {"generated_utc": S.fmt(time.time()), "chosen_exit": chosen}, "passed_fit": passed,
                   "confirmed": confirmed, "results": res}, f, indent=1)
    print("passed fit:", passed, "confirmed:", confirmed)


if __name__ == "__main__":
    main()
