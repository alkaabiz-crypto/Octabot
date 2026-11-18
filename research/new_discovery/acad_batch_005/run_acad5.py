"""Academic batch 005 (PREREG.md): STR-034..038. usage: python3 -I run_acad5.py <config.json>
config: {"SYM": [[dir_or_npz, ...], ...], "BTC15": path, "XAU15": path, "FOMC": [YYYY-MM-DD, ...]}"""
import glob, gzip, json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
PER = [("EARLY", "2000-01-01", "2023-01-01"), ("TRAIN", "2023-01-01", "2024-07-01"), ("VALIDATION", "2024-07-01", "2025-07-01"), ("TEST", "2025-07-01", "2100-01-01")]
NY, BER = "America/New_York", "Europe/Berlin"


class Px:
    """minute-indexed mid open + spread; px(minute) = open at that minute or the nearest earlier minute within 5."""
    def __init__(self, sources):
        parts = []
        for s in sources:
            parts += [np.load(f) for f in sorted(glob.glob(os.path.join(s, "part_*.npz")))] if os.path.isdir(s) else [np.load(s)]
        m = np.concatenate([p["m"] for p in parts]); o = np.concatenate([p["o"] for p in parts]); sp = np.concatenate([p["sp"] for p in parts])
        i = np.argsort(m, kind="stable"); m, o, sp = m[i], o[i], sp[i]; k = np.r_[True, np.diff(m) > 0]; self.m, self.o, self.sp = m[k], o[k], sp[k]

    def at(self, minute):
        j = np.searchsorted(self.m, minute, side="right") - 1
        if j < 0 or minute - self.m[j] > 5: return None
        return float(self.o[j]), float(self.sp[j])


def utc_min(day, hh, mm, tz):
    return int(pd.Timestamp(f"{day} {hh:02d}:{mm:02d}", tz=tz).tz_convert("UTC").timestamp()) // 60


def period(d):
    for n, a, b in PER:
        if a <= str(d) < b: return n


def trading_days(P, tz, open_hm, close_hm):
    first = pd.Timestamp(int(P.m[0]) * 60, unit="s", tz="UTC").tz_convert(tz).date(); last = pd.Timestamp(int(P.m[-1]) * 60, unit="s", tz="UTC").tz_convert(tz).date()
    return [d.date() for d in pd.bdate_range(first, last) if P.at(utc_min(d.date(), *open_hm, tz)) and P.at(utc_min(d.date(), *close_hm, tz))]


def leg(P, a, b, side, cost_mult=1.0):
    x, y = P.at(a), P.at(b)
    if not x or not y: return None
    g = side * (y[0] / x[0] - 1) * 1e4; c = (x[1] / x[0] + y[1] / y[0]) / 2 * 1e4
    return g - cost_mult * c, g - 2 * cost_mult * c, g


def summarize(rows, rng, mode, bench=None):
    res = {}
    for n, *_ in PER:
        s = [r for r in rows if period(r["d"]) == n]
        if len(s) < 3: res[n] = dict(trades=len(s)); continue
        net = np.array([r["net"] for r in s]); st = np.array([r["stress"] for r in s]); se = net.std(ddof=1) / math.sqrt(len(s))
        q = dict(trades=len(s), mean_net_bp=round(float(net.mean()), 2), mean_stress_bp=round(float(st.mean()), 2), win_pct=round(float((net > 0).mean() * 100), 1), t=round(float(net.mean() / se), 2))
        if mode == "random":
            L = np.array([r["L"] for r in s]); c = np.array([r["cost"] for r in s]); sides = rng.choice([-1, 1], size=(1000, len(s)))
            rnd = (sides * L - c).mean(axis=1); q["random_dir_mean_bp"] = round(float(rnd.mean()), 2); q["p"] = float((rnd >= net.mean()).mean())
        else:
            b = np.array(bench.get(n, [])) if bench else np.array([])
            ex = net - (b.mean() if len(b) > 2 else 0.0); sx = ex.std(ddof=1) / math.sqrt(len(ex)); tt = ex.mean() / sx
            q["benchmark_mean_bp"] = round(float(b.mean()), 2) if len(b) > 2 else 0.0; q["excess_bp"] = round(float(ex.mean()), 2); q["p"] = float(0.5 * math.erfc(tt / math.sqrt(2)))
        res[n] = q
    return res


def run_index(sym, P, fomc, rng):
    out = {}; dax = sym == "DE30m"; tz = BER if dax else NY; o_hm, c_hm = ((9, 0), (17, 30)) if dax else ((9, 30), (16, 0))
    D = trading_days(P, tz, o_hm, c_hm)
    # STR-034 intraday momentum
    rows = []
    for p, d in zip(D[:-1], D[1:]):
        a = utc_min(p, *c_hm, tz); b = utc_min(d, *((9, 30) if dax else (10, 0)), tz); x, y = P.at(a), P.at(b)
        if not x or not y or y[0] == x[0]: continue
        side = 1 if y[0] > x[0] else -1; r = leg(P, utc_min(d, *((17, 0) if dax else (15, 30)), tz), utc_min(d, *c_hm, tz), 1)
        if r: rows.append(dict(d=d, net=side * r[2] - (r[2] - r[0]), stress=side * r[2] - (r[2] - r[1]), L=r[2], cost=r[2] - r[0]))
    out["STR-034"] = dict(mode="random", results=summarize(rows, rng, "random"), trades=len(rows))
    if dax: return out
    # STR-036 overnight drift
    rows = []
    for d, n in zip(D[:-1], D[1:]):
        r = leg(P, utc_min(d, 16, 0, NY), utc_min(n, 9, 30, NY), 1)
        if r: rows.append(dict(d=d, net=r[0], stress=r[1], nights=(n - d).days))
    res = summarize(rows, rng, "excess", {}); be = {k: round(v["mean_net_bp"] / np.mean([r["nights"] for r in rows if period(r["d"]) == k]), 2) for k, v in res.items() if "mean_net_bp" in v}
    out["STR-036"] = dict(mode="vs_zero", results=res, breakeven_swap_bp_per_night=be, trades=len(rows))
    # STR-037 pre-FOMC drift
    F = set(fomc); ev, oth = [], {}
    for p, d in zip(D[:-1], D[1:]):
        r = leg(P, utc_min(p, 14, 0, NY), utc_min(d, 13, 55, NY), 1)
        if not r: continue
        if str(d) in F: ev.append(dict(d=d, net=r[0], stress=r[1]))
        else: oth.setdefault(period(d), []).append(r[0])
    out["STR-037"] = dict(mode="excess", results=summarize(ev, rng, "excess", oth), trades=len(ev))
    out["STR-038"] = tom(P, D, lambda d: utc_min(d, 16, 0, NY), rng)
    return out


def tom(P, D, close_min, rng, smult=2):
    idx = {d: i for i, d in enumerate(D)}; months = {}
    for d in D: months.setdefault((d.year, d.month), []).append(d)
    keys = sorted(months); ev, oth = [], {}; used = set()
    for k0, k1 in zip(keys[:-1], keys[1:]):
        a, b = months[k0], months[k1]
        if len(a) < 2 or len(b) < 3: continue
        s, e = a[-2], b[2]; r = leg(P, close_min(s), close_min(e), 1)
        if r: ev.append(dict(d=e, net=r[0], stress=r[2] - smult * (r[2] - r[0]))); used.update(range(idx[s], idx[e] + 1))
    n = 4                                                                          # same 4-trading-day window length
    for i in range(len(D) - n):
        if i in used or (i + n) in used: continue
        r = leg(P, close_min(D[i]), close_min(D[i + n]), 1)
        if r: oth.setdefault(period(D[i + n]), []).append(r[0])
    return dict(mode="excess", results=summarize(ev, rng, "excess", oth), trades=len(ev))


class Px15:
    def __init__(self, t, o, sp):
        self.m = (np.asarray(t, np.int64) // 60); self.o = np.asarray(o, float); self.sp = np.asarray(sp, float)
    at = Px.at


def main():
    cfg = json.load(open(sys.argv[1])); rng = np.random.default_rng(3034); R = {}
    for sym in ("US500m", "USTECm", "US30m", "DE30m"):
        P = Px(cfg[sym]); r = run_index(sym, P, cfg["FOMC"], rng)
        for k, v in r.items(): R[f"{k}{'-DAX' if sym == 'DE30m' else ''}|{sym}"] = v
        print(sym, "done", flush=True)
    q = np.array(json.load(gzip.open(cfg["BTC15"])), float); B = Px15(q[:, 0], q[:, 1], q[:, 1] * 0.0010)   # 0.05% per side = 0.10% round trip in spread terms
    days = sorted({pd.Timestamp(int(t), unit="s", tz="UTC").date() for t in q[:, 0]}); rows = []
    for d in days:
        b0, b1 = utc_min(d, 0, 0, "UTC"), utc_min(d, 0, 30, "UTC"); x, y = B.at(b0), B.at(b1)
        if not x or not y or x[0] == y[0]: continue
        side = 1 if y[0] > x[0] else -1; r = leg(B, utc_min(d, 23, 30, "UTC"), utc_min(d, 23, 30, "UTC") + 30, 1)
        if r: c = r[2] - r[0]; rows.append(dict(d=d, net=side * r[2] - c, stress=side * r[2] - 4 * c, L=r[2], cost=c))   # 0.05% per side primary, 0.20% stress
    R["STR-035|BTCUSDT"] = dict(mode="random", results=summarize(rows, rng, "random"), trades=len(rows))
    bd = [d for d in days if B.at(utc_min(d, 0, 0, "UTC"))]; R["STR-038|BTCUSDT"] = tom(B, bd, lambda d: utc_min(d, 0, 0, "UTC"), rng, smult=4)
    g = pd.read_csv(cfg["XAU15"]); X = Px15(g.t.values, ((g.bo + g.ao) / 2).values, (g.ao - g.bo).values)
    xd = [d for d in sorted({pd.Timestamp(int(t), unit="s", tz="UTC").tz_convert(NY).date() for t in g.t.values}) if pd.Timestamp(d).weekday() < 5 and X.at(utc_min(d, 16, 0, NY))]
    xd = [d for d in xd if str(d) >= "2019-08-01"]; R["STR-038|XAUUSDm"] = tom(X, xd, lambda d: utc_min(d, 16, 0, NY), rng)
    keys = [k for k in R if R[k]["results"].get("TEST", {}).get("p") is not None]; ps = [R[k]["results"]["TEST"]["p"] for k in keys]
    o = np.argsort(ps); sig = set()
    for rank, i in enumerate(o):
        if ps[i] <= 0.05 * (rank + 1) / len(ps): sig = set(o[:rank + 1])
    for i, k in enumerate(keys):
        f = R[k]["results"]; av = [p for p, *_ in PER if f[p].get("mean_net_bp") is not None]; pos = bool(av) and all(f[p]["mean_net_bp"] > 0 for p in av); te = f["TEST"]
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_stress_bp", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
    json.dump(dict(n_tests=len(keys), results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    for k in keys: print(k, R[k]["decision"], {p: (v.get("trades"), v.get("mean_net_bp"), v.get("p")) for p, v in R[k]["results"].items()}, R[k].get("breakeven_swap_bp_per_night", ""))


if __name__ == "__main__":
    main()
