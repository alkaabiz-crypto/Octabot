"""STR-033 (PREREG.md): NY-open first 5m candle + EMA 12, 6 h hold, on Exness USTECm 1m (mid + spread).
usage: python3 -I run_str033.py <dir with part_YYYY_MM.npz> <USTECm_1m.npz for 2025-01..2026-10>"""
import glob, json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
P = [("EARLY", "2000-01-01", "2023-01-01"), ("TRAIN", "2023-01-01", "2024-07-01"), ("VALIDATION", "2024-07-01", "2025-07-01"), ("TEST", "2025-07-01", "2100-01-01")]
MIN_RISK = 0.0002; HOLD = 360


def load(pdir, recent):
    parts = [np.load(f) for f in sorted(glob.glob(os.path.join(pdir, "part_*.npz")))] + [np.load(recent)]
    d = {k: np.concatenate([p[k] for p in parts]) for k in ("m", "o", "h", "l", "c", "sp")}
    order = np.argsort(d["m"], kind="stable"); d = {k: v[order] for k, v in d.items()}
    keep = np.r_[True, np.diff(d["m"]) > 0]; return {k: v[keep] for k, v in d.items()}


def days(d):
    m = d["m"]; idx = {int(x): i for i, x in enumerate(m)}
    f5 = pd.DataFrame(dict(k=m // 5, c=d["c"])).groupby("k").c.last(); ema = f5.ewm(span=12, adjust=False).mean()
    first = pd.Timestamp(int(m[0]) * 60, unit="s", tz="UTC").tz_convert("America/New_York").normalize()
    last = pd.Timestamp(int(m[-1]) * 60, unit="s", tz="UTC").tz_convert("America/New_York").normalize()
    out = []
    for day in pd.date_range(first, last, freq="B", tz="America/New_York"):
        t0 = int((day + pd.Timedelta(hours=9, minutes=30)).tz_convert("UTC").timestamp()) // 60
        mins = [idx.get(t0 + j) for j in range(5)]
        if mins[0] is None or mins[4] is None: continue
        ii = [i for i in mins if i is not None]; O = d["o"][ii[0]]; C = d["c"][ii[-1]]; H = d["h"][ii].max(); L = d["l"][ii].min()
        k5 = t0 // 5; e = ema.get(k5)
        ent = next((idx[t0 + 5 + j] for j in range(3) if (t0 + 5 + j) in idx), None)
        ex = next((idx[t0 + 5 + HOLD + j] for j in range(15) if (t0 + 5 + HOLD + j) in idx), None)
        if e is None or ent is None or ex is None: continue
        out.append(dict(day=day.date(), O=O, H=H, L=L, C=C, ema=float(e), ent=ent, ex=ex))
    return out


def trade(d, x, side, use_stop=True, risk_override=None):
    e = d["o"][x["ent"]]; stop = x["L"] if side > 0 else x["H"]; risk = (e - stop) * side
    if risk_override is not None: risk = risk_override; stop = e - side * risk
    if risk <= 0 or risk / e < MIN_RISK: return None
    cost = (d["sp"][x["ent"]] + d["sp"][x["ex"]]) / 2; px = d["o"][x["ex"]]
    if use_stop:
        for i in range(x["ent"], x["ex"]):
            if i > x["ent"] and (d["o"][i] - stop) * side <= 0: px = d["o"][i]; cost = (d["sp"][x["ent"]] + d["sp"][i]) / 2; break
            if ((d["l"][i] if side > 0 else d["h"][i]) - stop) * side <= 0: px = stop; cost = (d["sp"][x["ent"]] + d["sp"][i]) / 2; break
    g = (px - e) * side / risk; return dict(r=g - cost / risk, rs=g - 2 * cost / risk, pct=((px - e) * side - cost) / e, risk=risk)


def summarize(rows, rng):
    res = {}
    for name, a, b in P:
        s = [r for r in rows if pd.Timestamp(a).date() <= r["day"] < pd.Timestamp(b).date()]
        if not s: res[name] = dict(trades=0); continue
        r = np.array([x["r"] for x in s]); rs = np.array([x["rs"] for x in s]); q = dict(trades=len(s), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4),
             win_pct=round(float((r > 0).mean() * 100), 1), t=round(float(r.mean() / (r.std(ddof=1) / math.sqrt(len(r)))), 2) if len(r) > 2 else None,
             always_long_mean_R=round(float(np.mean([x["r_always_long"] for x in s])), 4))
        alt = np.array([[x["r_long"], x["r_short"]] for x in s]); picks = rng.integers(2, size=(1000, len(s))); rand = alt[np.arange(len(s)), picks].mean(axis=1)
        q["random_dir_mean_R"] = round(float(rand.mean()), 4); q["p_random_dir"] = float((rand >= r.mean()).mean()); res[name] = q
    eq = np.cumprod(1 + 0.01 * np.array([x["r"] for x in rows])); dd = float((eq / np.maximum.accumulate(eq) - 1).min())
    yrs = {}
    for x in rows: yrs.setdefault(x["day"].year, []).append(x["r"])
    return dict(periods=res, total_trades=len(rows), equity_1pct_risk_total_return_pct=round(float(eq[-1] - 1) * 100, 1), max_drawdown_pct=round(dd * 100, 1),
                by_year={y: dict(trades=len(v), mean_R=round(float(np.mean(v)), 3), return_1pct_pct=round(float(np.prod(1 + 0.01 * np.array(v)) - 1) * 100, 1)) for y, v in sorted(yrs.items())},
                first_day=str(rows[0]["day"]), last_day=str(rows[-1]["day"]))


def main():
    d = load(sys.argv[1], sys.argv[2]); D = days(d); rng = np.random.default_rng(3033); out = {}
    for var in ("A", "B", "C"):
        rows = []
        for x in D:
            bull, bear = x["C"] > x["O"], x["C"] < x["O"]; above, below = x["C"] > x["ema"], x["C"] < x["ema"]
            side = (1 if (bull and above) else -1 if (bear and below) else 0) if var in ("A", "C") else (1 if above else -1 if below else 0)
            if not side: continue
            us = var != "C"; t = trade(d, x, side, us)
            if t is None: continue
            rl = trade(d, x, 1, us, t["risk"]); rsh = trade(d, x, -1, us, t["risk"]); al = trade(d, x, 1, us)   # random side: SAME stop distance (PREREG); always-long: its own stop
            rows.append(dict(day=x["day"], side=side, r=t["r"], rs=t["rs"], pct=t["pct"], r_long=rl["r"], r_short=rsh["r"], r_always_long=(al["r"] if al else rl["r"])))
        out[var] = summarize(rows, rng)
    ps = [out[v]["periods"]["TEST"].get("p_random_dir", 1.0) for v in "ABC"]; order = np.argsort(ps); sig = set()
    for rank, i in enumerate(order):
        if ps[i] <= 0.05 * (rank + 1) / 3: sig = set(order[:rank + 1])
    for i, v in enumerate("ABC"):
        f = out[v]["periods"]; av = [p for p, *_ in P if f[p].get("trades", 0) > 0]; pos = all(f[p]["mean_R"] > 0 for p in av); te = f["TEST"]
        out[v]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
    out["n_days_with_data"] = len(D); json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    for v in "ABC": print(v, out[v]["decision"], out[v]["total_trades"], out[v]["equity_1pct_risk_total_return_pct"], out[v]["max_drawdown_pct"], json.dumps(out[v]["periods"]))


if __name__ == "__main__":
    main()
