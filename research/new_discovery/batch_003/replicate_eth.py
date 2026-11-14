"""Single-test ETH replication of H4 (REPLICATION_ETH_PREREG.md). Uses run_batch.py's own h4 machinery with the asset swapped.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<dir with ETH coinbase/binance hourly files named as for BTC> python3 -I replicate_eth.py"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import run_batch as RB  # noqa: E402

cb = pd.read_csv(os.path.join(RB.B3, "coinbase_BTCUSD_1h.csv.gz")); bn = pd.read_csv(os.path.join(RB.B3, "binance_BTCUSDT_1h.csv.gz"))   # ETH data, same file names
x = cb.merge(bn, on="t").sort_values("t"); x["prem"] = np.log(x.cb / x.bn)
x["z"] = (x.prem - x.prem.rolling(720).mean().shift(1)) / x.prem.rolling(720).std().shift(1); x["close"] = pd.to_datetime(x.t + 3600, unit="s", utc=True)
d = RB.load("ETHUSDm"); sp = RB.spread_frac(d); idx = d.index; per = np.array([RB.period(t) for t in idx]); n = len(d)
pools = {p: np.flatnonzero(per[:n - 97] == p) for p in ("EARLY", "TRAIN", "VALIDATION", "TEST")}; tr = []; free = idx[0]
for _, row in x[x.z.abs() >= 2].iterrows():
    if row.close < free: continue
    i = int(idx.searchsorted(row.close))
    if i >= n: break
    j = int(idx.searchsorted(idx[i] + pd.Timedelta(hours=24)))
    if j >= n: break
    side = 1 if row.z > 0 else -1; r, rs = RB.net(d, sp, side, i, j=j); p = RB.period(idx[i]); free = idx[j]
    if p and p != "EARLY": tr.append(dict(period=p, side=side, r=r, rs=rs, pool=pools[p]))
out = RB.summarize(tr, d, sp, np.random.default_rng(RB.SEED + 44), hold_bars=96); out.pop("EARLY", None)
te = out["TEST"]; pos = all(out[p].get("mean_bp", -1) > 0 for p in ("TRAIN", "VALIDATION", "TEST"))
lab = "REPLICATED" if (pos and te.get("mean_stress_bp", -1) > 0 and (te.get("p_vs_benchmark") or 1) <= 0.05 and te.get("trades", 0) >= 30) else ("PARTIAL" if pos else "NOT REPLICATED")
out["decision"] = lab; json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results", "replication_eth.json"), "w"), indent=1, default=float)
for p in ("TRAIN", "VALIDATION", "TEST"):
    v = out[p]; print(p, v.get("trades"), "mean %+.2f bp, stress %+.2f, p %s" % (v.get("mean_bp", float("nan")), v.get("mean_stress_bp", float("nan")), v.get("p_vs_benchmark")))
print("DECISION:", lab)
