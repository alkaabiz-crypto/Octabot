"""STR-049 (PREREG.md): first 5m candle after the NY open, direction = close vs EMA12 (5m), trailing stop T1/T2/T3, flat by 16:00.
usage: python3 -I run_str049.py <USTEC part dir> <USTECm_1m.npz>"""
import json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "str_033"))
import run_str033 as S33  # noqa: E402  load(), days(), utc helpers, P (periods), MIN_RISK
P = S33.P


def five_min(d):
    k = d["m"] // 5; df = pd.DataFrame(dict(k=k, o=d["o"], h=d["h"], l=d["l"], c=d["c"]))
    g = df.groupby("k"); b = pd.DataFrame(dict(o=g.o.first(), h=g.h.max(), l=g.l.min(), c=g.c.last()))
    b["ema"] = b.c.ewm(span=12, adjust=False).mean(); pc = b.c.shift()
    tr = pd.concat([b.h - b.l, (b.h - pc).abs(), (b.l - pc).abs()], axis=1).max(axis=1); b["atr"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    return b


def run_day(d, b, x, side, var, risk, t_end):
    o, h, l, sp, m = d["o"], d["h"], d["l"], d["sp"], d["m"]; i0 = x["ent"]; e = o[i0]; stop = e - side * risk; best = e; px = None; ix = None
    i = i0
    while i < len(m) and m[i] < t_end:
        if i > i0 and (o[i] - stop) * side <= 0: px, ix = o[i], i; break
        if ((l[i] if side > 0 else h[i]) - stop) * side <= 0: px, ix = stop, i; break
        if m[i] % 5 == 4:                                                  # a 5-minute candle closes at the end of this minute
            k = m[i] // 5
            if k in b.index:
                r = b.loc[k]
                if var == "T1": stop = max(stop, r.l) if side > 0 else min(stop, r.h)
                elif var == "T2":
                    best = max(best, r.c) if side > 0 else min(best, r.c); cand = best - side * 2 * r.atr
                    stop = max(stop, cand) if side > 0 else min(stop, cand)
                elif var == "T3" and (r.c - r.ema) * side < 0 and i + 1 < len(m): px, ix = o[i + 1], i + 1; break
        i += 1
    if px is None: ix = min(i, len(m) - 1); px = o[ix]
    cost = (sp[i0] + sp[ix]) / 2; g = (px - e) * side / risk
    return g - cost / risk, g - 2 * cost / risk


def main():
    d = S33.load(sys.argv[1], sys.argv[2]); D = S33.days(d); b = five_min(d); rng = np.random.default_rng(3049); out = {}
    for var in ("T1", "T2", "T3"):
        rows = []
        for x in D:
            side = 1 if x["C"] > x["ema"] else (-1 if x["C"] < x["ema"] else 0)
            if not side: continue
            e = d["o"][x["ent"]]; risk = (e - (x["L"] if side > 0 else x["H"])) * side
            if risk <= 0 or risk / e < S33.MIN_RISK: continue
            t_end = S33_utc_close(x["day"])
            r, rs = run_day(d, b, x, side, var, risk, t_end); ro, _ = run_day(d, b, x, -side, var, risk, t_end)
            rows.append(dict(day=x["day"], r=r, rs=rs, r_long=r if side > 0 else ro, r_short=ro if side > 0 else r, r_always_long=r if side > 0 else ro))
        res = S33.summarize(rows, rng); R = np.array([z["r"] for z in rows]); res["win_pct_all"] = round(float((R > 0).mean() * 100), 1)
        res["profit_factor"] = round(float(R[R > 0].sum() / -R[R < 0].sum()), 3); res["mean_R_all"] = round(float(R.mean()), 4); out[var] = res
        print(var, len(rows), res["equity_1pct_risk_total_return_pct"], res["max_drawdown_pct"], res["win_pct_all"], res["profit_factor"], json.dumps({p: (v.get("trades"), v.get("mean_R"), v.get("p_random_dir")) for p, v in res["periods"].items()}), flush=True)
    ps = [out[v]["periods"]["TEST"].get("p_random_dir", 1.0) for v in ("T1", "T2", "T3")]; o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / 3: sig = set(o[:r + 1])
    for i, v in enumerate(("T1", "T2", "T3")):
        f = out[v]["periods"]; av = [p for p, *_ in P if f[p].get("trades", 0) > 0]; pos = all(f[p]["mean_R"] > 0 for p in av); te = f["TEST"]
        out[v]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(v, out[v]["decision"], out[v]["by_year"])
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)


def S33_utc_close(day):
    return int(pd.Timestamp(f"{day} 16:00", tz="America/New_York").tz_convert("UTC").timestamp()) // 60


if __name__ == "__main__":
    main()
