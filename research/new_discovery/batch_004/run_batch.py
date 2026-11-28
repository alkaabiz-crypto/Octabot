"""Batch 004 (PREREG.md): commodity term structure, monthly backwardation/contango rule on WTI and Henry Hub natural gas.
usage: B004_DATA=<scratch dir> python3 -I run_batch.py     (downloads EIA files into B004_DATA if missing)
"""
import json, math, os, ssl, sys, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.environ["B004_DATA"]; os.makedirs(DATA, exist_ok=True)
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
SRC = {"WTI": ("pet", "RCLC1", "RCLC2", (15, 28)), "NG": ("ng", "RNGC1", "RNGC2", None)}
COST, COST_HI = 0.0010, 0.0025; DEV_END = pd.Timestamp("2010-01-01"); END = pd.Timestamp("2026-11-01")


def series(area, code):
    p = os.path.join(DATA, f"{code}d.xls")
    if not os.path.exists(p):
        open(p, "wb").write(urllib.request.urlopen(f"https://www.eia.gov/dnav/{area}/hist_xls/{code}d.xls", timeout=60, context=CTX).read())
    d = pd.read_excel(p, sheet_name="Data 1", header=2); d.columns = ["date", code]; d["date"] = pd.to_datetime(d.date)
    return d.dropna().set_index("date")[code].astype(float)


def in_window(ts, mkt):
    if mkt == "WTI": return 15 <= ts.day <= 28
    return ts.day >= 20 or ts.day <= 3


def daily_returns(f1, f2, mkt):
    x = pd.concat([f1, f2], axis=1, keys=["f1", "f2"]).dropna(); p1, p2 = x.f1.shift(1), x.f2.shift(1)
    with np.errstate(divide="ignore", invalid="ignore"):
        score = np.abs(np.log(x.f1 / p1)) - np.abs(np.log(x.f1 / p2))
    roll = pd.Series(False, index=x.index)
    key = [(t.year, t.month) if (mkt == "WTI" or t.day >= 20) else ((t - pd.offsets.MonthBegin(1)).year, (t - pd.offsets.MonthBegin(1)).month) for t in x.index]
    sc = pd.DataFrame(dict(score=score, key=key, ok=[in_window(t, mkt) for t in x.index]), index=x.index)
    for _, g in sc[sc.ok & sc.score.notna()].groupby("key"):
        t = g.score.idxmax()
        if g.score[t] > 0: roll[t] = True
    r = np.where(roll, x.f1 / p2 - 1, x.f1 / p1 - 1)
    return pd.DataFrame(dict(r=r, f1=x.f1, f2=x.f2, roll=roll), index=x.index).iloc[1:]


def monthly(d, exclude_apr2020):
    me = d.groupby([d.index.year, d.index.month]).tail(1).index      # last trading day of each month
    rows = []
    for a, b in zip(me[:-1], me[1:]):
        s = math.log(d.f1[a] / d.f2[a]) if d.f1[a] > 0 and d.f2[a] > 0 else float("nan")
        side = 1 if s > 0 else (-1 if s < 0 else 0)
        seg = d.r[(d.index > a) & (d.index <= b)]
        if exclude_apr2020 and b.year == 2020 and b.month == 4: continue
        if not len(seg) or math.isnan(s): continue
        gross = float(np.prod(1 + seg.values) - 1)
        rows.append(dict(month=b, side=side, long_only=gross, gross=side * gross, net=side * gross - COST, net_hi=side * gross - COST_HI, slope=s))
    return pd.DataFrame(rows).set_index("month")


def nw_p(x, L=3):
    x = np.asarray(x); n = len(x); m = x.mean(); d = x - m
    v = (d @ d) / n + 2 * sum((1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n for j in range(1, L + 1)); t = m / math.sqrt(v / n)
    return float(t), float(0.5 * math.erfc(t / math.sqrt(2)))


def stats(m):
    if len(m) < 12: return dict(months=len(m))
    t, p = nw_p(m.net.values); rng = np.random.default_rng(404)
    flips = rng.choice([-1, 1], size=(10000, len(m))); rand = ((flips * m.long_only.values).mean(axis=1) - COST)   # random-sign benchmark
    return dict(months=len(m), mean_net_pct=round(float(m.net.mean() * 100), 3), mean_net_hi_cost_pct=round(float(m.net_hi.mean() * 100), 3),
                nw_t=round(t, 2), p_one_sided=round(p, 4), p_random_sign=round(float((rand >= m.net.mean()).mean()), 4),
                long_only_mean_pct=round(float(m.long_only.mean() * 100), 3), share_backwardated=round(float((m.side > 0).mean()), 3),
                ann_net_pct=round(float(m.net.mean() * 1200), 1), win_pct=round(float((m.net > 0).mean() * 100), 1))


def main():
    out = {}
    for mkt, (area, c1, c2, _) in SRC.items():
        d = daily_returns(series(area, c1), series(area, c2), mkt)
        rolls = d.roll.groupby(d.index.year).sum(); out[f"{mkt}_rolls_per_year"] = {int(k): int(v) for k, v in rolls.items()}
        for lab, ex in (("decision_excl_apr2020", True), ("incl_apr2020", False)):
            m = monthly(d, ex); res = {}
            for p, (a, b) in {"DEV": (m.index.min(), DEV_END), "HOLDOUT": (DEV_END, END), "since_2023": (pd.Timestamp("2023-01-01"), END)}.items():
                res[p] = stats(m[(m.index >= a) & (m.index < b)])
            out[f"{mkt}|{lab}"] = res
            print(mkt, lab, {p: (v.get("months"), v.get("mean_net_pct"), v.get("p_one_sided")) for p, v in res.items()}, flush=True)
    ps = [out[f"{m}|decision_excl_apr2020"]["HOLDOUT"]["p_one_sided"] for m in SRC]; order = sorted(range(2), key=lambda i: ps[i])
    k = max([r + 1 for r, i in enumerate(order) if ps[i] <= 0.05 * (r + 1) / 2], default=0); sig = set(order[:k])
    for i, mkt in enumerate(SRC):
        r = out[f"{mkt}|decision_excl_apr2020"]; pos = r["DEV"]["mean_net_pct"] > 0 and r["HOLDOUT"]["mean_net_pct"] > 0
        r["decision"] = "CONFIRMED" if (pos and i in sig) else ("WATCH" if pos else "REJECT"); print(mkt, "DECISION:", r["decision"])
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "batch_004.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
