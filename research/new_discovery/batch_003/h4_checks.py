"""The two pre-registered H4 checks (H4_CHECKS_PREREG.md). Rule unchanged: |z| >= 2 over a 720-hour window, 24 h hold, one position.
usage: DISCOVERY_DATA=<scratch with long/> B003_DATA=<b003data dir> H4C_DATA=<dir with the check files> python3 -I h4_checks.py
"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import run_batch as RB  # noqa: E402
D = os.environ["H4C_DATA"]; FEE = 0.0010; H = 3600


def zscore(prem):
    return (prem - prem.rolling(720).mean().shift(1)) / prem.rolling(720).std().shift(1)


def check_a():
    cb = pd.read_csv(os.path.join(D, "coinbase_2017_2019.csv.gz")); bn = pd.read_csv(os.path.join(D, "binance_2017_2019.csv.gz"))
    x = cb.merge(bn, on="t").sort_values("t").reset_index(drop=True); x["z"] = zscore(np.log(x.cb / x.bn)); x["close"] = x.t + H
    opens = bn.set_index("t").bo; ot = opens.index.values; ov = opens.values; end = int(pd.Timestamp("2020-01-01", tz="UTC").timestamp())
    def trade(i_entry, side, fee):
        j = int(np.searchsorted(ot, ot[i_entry] + 24 * H))
        if j >= len(ot): return None, None
        return 1e4 * (side * (ov[j] - ov[i_entry]) / ov[i_entry] - 2 * fee), j
    tr, free = [], 0
    for r in x[(x.z.abs() >= 2) & (x.close < end)].itertuples():
        if r.close < free: continue
        i = int(np.searchsorted(ot, r.close))
        if i >= len(ot) or ot[i] >= end: break
        side = 1 if r.z > 0 else -1; net1, j = trade(i, side, FEE)
        if net1 is None: break
        net2, _ = trade(i, side, 2 * FEE); tr.append(dict(t=int(ot[i]), side=side, r=net1, r2=net2)); free = ot[j]
    r = np.array([t["r"] for t in tr]); sides = np.array([t["side"] for t in tr])
    pool = np.flatnonzero((ot >= tr[0]["t"]) & (ot + 24 * H < end)); rng = np.random.default_rng(31); means = np.zeros(1000)
    for s in sides:                                                      # random entries, same sides and 24 h hold
        i = pool[rng.integers(len(pool), size=1000)]; j = np.searchsorted(ot, ot[i] + 24 * H); j = np.minimum(j, len(ot) - 1)
        means += 1e4 * (s * (ov[j] - ov[i]) / ov[i] - 2 * FEE)
    p = float((means / len(sides) >= r.mean()).mean()); n = len(r); se = r.std(ddof=1) / math.sqrt(n)
    lab = "CONFIRMED" if (r.mean() > 0 and p <= 0.05 and n >= 30) else ("POSITIVE, NOT SIGNIFICANT" if r.mean() > 0 else "NOT CONFIRMED")
    by_year = {str(y): dict(trades=int(((pd.to_datetime([t["t"] for t in tr], unit="s").year == y)).sum()),
                            mean_bp=round(float(r[pd.to_datetime([t["t"] for t in tr], unit="s").year == y].mean()), 2)) for y in (2017, 2018, 2019)}
    return dict(first_trade=str(pd.Timestamp(tr[0]["t"], unit="s")), trades=n, mean_bp_primary=round(float(r.mean()), 2), mean_bp_2x_fee=round(float(np.mean([t["r2"] for t in tr])), 2),
                ci95_bp=[round(float(r.mean() - 1.96 * se), 1), round(float(r.mean() + 1.96 * se), 1)], win_pct=round(float((r > 0).mean() * 100), 1),
                longs=int((sides > 0).sum()), long_mean_bp=round(float(r[sides > 0].mean()), 2), short_mean_bp=round(float(r[sides < 0].mean()), 2),
                p_vs_benchmark=p, by_year=by_year, decision=lab)


def check_b():
    cb = pd.read_csv(os.path.join(os.environ["B003_DATA"], "coinbase_BTCUSD_1h.csv.gz")); bs = pd.read_csv(os.path.join(D, "bitstamp_BTCUSD_1h.csv.gz"))
    x = cb.merge(bs, on="t").sort_values("t"); x["z"] = zscore(np.log(x.cb / x.bs)); x["close"] = pd.to_datetime(x.t + H, unit="s", utc=True)
    d = RB.load("BTCUSDm"); sp = RB.spread_frac(d); idx = d.index; per = np.array([RB.period(t) for t in idx]); n = len(d)
    pools = {p: np.flatnonzero(per[:n - 97] == p) for p in ("EARLY", "TRAIN", "VALIDATION", "TEST")}; tr = []; free = idx[0]
    for _, row in x[x.z.abs() >= 2].iterrows():
        if row.close < free: continue
        i = int(idx.searchsorted(row.close))
        if i >= n: break
        j = int(idx.searchsorted(idx[i] + pd.Timedelta(hours=24)))
        if j >= n: break
        side = 1 if row.z > 0 else -1; r, rs = RB.net(d, sp, side, i, j=j); p = RB.period(idx[i]); free = idx[j]
        if p: tr.append(dict(period=p, side=side, r=r, rs=rs, pool=pools[p]))
    out = RB.summarize(tr, d, sp, np.random.default_rng(RB.SEED + 55), hold_bars=96); te = out["TEST"]
    pos = all(out[p].get("mean_bp", -1) > 0 for p in ("EARLY", "TRAIN", "VALIDATION", "TEST"))
    out["decision"] = "REPLICATED" if (pos and te.get("mean_stress_bp", -1) > 0 and (te.get("p_vs_benchmark") or 1) <= 0.05 and te.get("trades", 0) >= 30) else ("PARTIAL" if pos else "NOT REPLICATED")
    out["corr_with_binance_premium_z"] = None
    return out


if __name__ == "__main__":
    A = check_a(); print("CHECK A (2017-09..2019-12, Binance prices, 0.10%/side):", json.dumps(A))
    B = check_b()
    for p in ("EARLY", "TRAIN", "VALIDATION", "TEST"):
        v = B[p]; print("CHECK B", p, v.get("trades"), "mean %+.2f stress %+.2f p %s" % (v.get("mean_bp", float("nan")), v.get("mean_stress_bp", float("nan")), v.get("p_vs_benchmark")))
    print("CHECK B decision:", B["decision"])
    json.dump(dict(check_a=A, check_b=B), open(os.path.join(HERE, "results", "h4_checks.json"), "w"), indent=1, default=float)
