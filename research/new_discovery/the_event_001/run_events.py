"""Theory event batch 001 (PREREG.md). usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_events.py"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ND, "ind_batch_001")); sys.path.insert(0, os.path.join(ND, "src"))
import run_ind as RI, common as C  # noqa: E401,E402
RB = RI.RB; MK = ["XAUUSDm", "USOILm", "US500m", "EURUSDm", "BTCUSDm"]; P = ["EARLY", "TRAIN", "VALIDATION", "TEST"]; RNG = np.random.default_rng(1001)


def shuffle_test(lab, ret, hour, runs=2000):
    """lab in {-1,0,+1}; effect = mean(lab*ret | lab != 0) in bp; null = labels shuffled within hour-of-day groups."""
    ev = lab != 0
    if ev.sum() < 30: return None
    eff = 1e4 * float((lab[ev] * ret[ev]).mean()); groups = [np.flatnonzero(hour == h) for h in np.unique(hour)]; sims = np.empty(runs)
    for k in range(runs):
        sh = lab.copy()
        for g in groups: sh[g] = RNG.permutation(lab[g])
        e = sh != 0; sims[k] = 1e4 * float((sh[e] * ret[e]).mean())
    return dict(events=int(ev.sum()), effect_bp=round(eff, 3), p=float((sims >= eff).mean()))


def per_period(idx, fn):
    per = np.array([RB.period(t) for t in idx]); return {p: fn(per == p) for p in P if (per == p).sum() > 0}


def zone_events(m, mode):
    d = RB.load(m); o, c = d.mo.values, d.mc.values; idx = d.index; mins = (idx.hour * 60 + idx.minute).values
    fwd = np.full(len(d), np.nan); fwd[:-17] = np.log(o[17:] / o[1:-16])                         # next open -> 16 candles later
    day = ((idx.tz_convert(None) - pd.Timestamp(0)) // pd.Timedelta(minutes=1) + 120).values // 1440  # Exness day (22:00 UTC start), unit-safe
    hi, lo = pd.Series(d.mh.values).groupby(day).transform("max").values, pd.Series(d.ml.values).groupby(day).transform("min").values
    if mode == "prev":
        dh = pd.Series(d.mh.values).groupby(day).max(); dl = pd.Series(d.ml.values).groupby(day).min()
        mid = ((dh.shift(1) + dl.shift(1)) / 2).reindex(day).values; ok = (mins < 20 * 60)
    else:
        inor = (mins < 7 * 60) | (mins >= 22 * 60); s = pd.DataFrame(dict(h=np.where(inor, d.mh.values, np.nan), l=np.where(inor, d.ml.values, np.nan), day=day))
        g = s.groupby("day"); mid = ((g.h.max() + g.l.min()) / 2).reindex(day).values; ok = (mins >= 7 * 60) & (mins < 20 * 60)
    bull, bear = c > o, c < o; lab = np.where(ok & bull & (c < mid), 1, np.where(ok & bear & (c > mid), -1, 0))
    keep = ~np.isnan(fwd) & ~np.isnan(mid)
    return per_period(idx, lambda s: shuffle_test(lab[s & keep], fwd[s & keep], idx.hour.values[s & keep]))


def pin_events(m):
    df = RI.hourly(m); o, h, l, c = (df[k].values for k in "ohlc"); rg = h - l; body = np.abs(c - o)
    bp = (np.minimum(o, c) - l >= 2 * body) & (np.minimum(o, c) >= l + 2 / 3 * rg) & (rg > 0)
    sp = (h - np.maximum(o, c) >= 2 * body) & (np.maximum(o, c) <= l + 1 / 3 * rg) & (rg > 0)
    lab = np.where(bp & ~sp, 1, np.where(sp & ~bp, -1, 0)); fwd = np.full(len(df), np.nan); fwd[:-5] = np.log(o[5:] / o[1:-4]); keep = ~np.isnan(fwd)
    return per_period(df.index, lambda s: shuffle_test(lab[s & keep], fwd[s & keep], df.index.hour.values[s & keep]))


def calendar_events(m, which):
    d = RB.load(m); x = d[(d.index.hour == 20) & (d.index.minute == 45)]; s = pd.Series(x.mc.values, index=x.index.normalize())
    r = np.log(s).diff().shift(-1).dropna()                                                        # return from this 21:00 to the next
    if which == "tom":
        mo = r.index.to_period("M"); pos_in = r.groupby(mo).cumcount(); last = r.groupby(mo).cumcount(ascending=False) == 0
        lab = np.where((pos_in.values < 3) | last.values, 1, 0)                                     # predicted positive vs others
        sign = lab * 2 - 1                                                                          # +1 tom, -1 others -> effect = mean(tom) - mean(other) via signed mean
    else:
        lab = np.where(r.index.weekday == 0, 1, 0); sign = -(lab * 2 - 1)                           # Monday predicted lower: signed -1 for Monday
    def test(sel):
        rr, ll = r.values[sel], lab[sel]
        if ll.sum() < 20: return None
        eff = 1e4 * (rr[ll == 1].mean() - rr[ll == 0].mean()) * (1 if which == "tom" else -1); sims = np.empty(2000)
        for k in range(2000):
            sh = RNG.permutation(ll); sims[k] = 1e4 * (rr[sh == 1].mean() - rr[sh == 0].mean()) * (1 if which == "tom" else -1)
        return dict(events=int(ll.sum()), effect_bp=round(float(eff), 3), p=float((sims >= eff).mean()))
    return per_period(r.index + pd.Timedelta(hours=21), test)


def fvg_events(m):
    df = RI.hourly(m); h, l, c = df.h.values, df.l.values, df.c.values; A = RI.atr(df).values; hrs = df.index.hour.values; per = np.array([RB.period(t) for t in df.index]); n = len(df)
    def retrace(i, dist, side):        # does price come back `dist` from close i within 10 candles?
        lvl = c[i] - side * dist; seg = (l[i + 1:i + 11] <= lvl) if side > 0 else (h[i + 1:i + 11] >= lvl)
        return bool(seg.any())
    out = {p: ([], []) for p in P}; byhp = {}
    for i in range(n - 11): byhp.setdefault((per[i], hrs[i]), []).append(i)
    for i in range(2, n - 11):
        p = per[i]
        if p is None or not A[i] > 0: continue
        side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
        if not side: continue
        edge = h[i - 2] if side > 0 else l[i - 2]; dist = side * (c[i] - edge)
        if dist <= 0: continue
        out[p][0].append(retrace(i, dist, side)); pool = byhp[(p, hrs[i])]
        for j in RNG.choice(pool, size=20):
            if A[j] > 0: out[p][1].append(retrace(j, dist * A[j] / A[i], side))
    res = {}
    for p, (a, b) in out.items():
        if len(a) < 30: continue
        p1, p2 = np.mean(a), np.mean(b); pp = (sum(a) + sum(b)) / (len(a) + len(b)); se = math.sqrt(pp * (1 - pp) * (1 / len(a) + 1 / len(b))); z = (p1 - p2) / se if se else 0
        res[p] = dict(events=len(a), fill_rate=round(float(p1), 4), random_rate=round(float(p2), 4), effect_bp=round(100 * float(p1 - p2), 2), p=float(0.5 * math.erfc(z / math.sqrt(2))))
    return res


def main():
    R = {}
    for m in MK:
        R[f"THE-001|{m}"] = zone_events(m, "prev"); R[f"THE-002|{m}"] = zone_events(m, "or"); R[f"THE-003|{m}"] = pin_events(m)
        R[f"THE-015a|{m}"] = calendar_events(m, "tom"); R[f"THE-015b|{m}"] = calendar_events(m, "mon"); R[f"THE-016|{m}"] = fvg_events(m)
        print(m, {k.split("|")[0]: {p: (v["effect_bp"], round(v["p"], 3)) for p, v in R[k].items() if v} for k in R if k.endswith(m)}, flush=True)
    keys = [k for k in R if R[k].get("TEST")]; ps = [R[k]["TEST"]["p"] for k in keys]; sig = C.bh(ps)
    verdict = {}
    for th in sorted({k.split("|")[0] for k in R}):
        ok = [k.split("|")[1] for i, k in enumerate(keys) if k.startswith(th + "|") and i in sig and R[k]["TEST"]["effect_bp"] > 0 and all(v["effect_bp"] > 0 for p, v in R[k].items() if v and p != "TEST")]
        early = [k.split("|")[1] for k in R if k.startswith(th + "|") and any(v and v["p"] <= 0.05 and v["effect_bp"] > 0 for p, v in R[k].items() if p in ("EARLY", "TRAIN"))]
        verdict[th] = dict(verdict="SUPPORTED" if len(ok) >= 3 else ("PARTLY SUPPORTED" if ok else ("DECAYED" if early else "NOT SUPPORTED")), markets=ok, early_significant=early)
    json.dump(dict(results=R, verdict=verdict), open(os.path.join(HERE, "results.json"), "w"), indent=1); print(json.dumps(verdict, indent=0))


if __name__ == "__main__":
    main()
