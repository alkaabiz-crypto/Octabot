"""STR-026 backtest (G6_DECISIONS.md step 3): Coinbase premium vs the mean of Binance and OKX USDT. Same harness as H4.
usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> H4C_DATA=<h4checks> python3 -I backtest.py"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); B3 = os.path.join(os.path.dirname(HERE), "batch_003"); sys.path.insert(0, B3)
import h4_checks as HC, run_batch as RB  # noqa: E401,E402
cb = pd.read_csv(os.path.join(os.environ["B003_DATA"], "coinbase_BTCUSD_1h.csv.gz")); bn = pd.read_csv(os.path.join(os.environ["B003_DATA"], "binance_BTCUSDT_1h.csv.gz"))
ok = pd.read_csv(os.path.join(HC.D, "okx_BTCUSDT_1h.csv.gz")).rename(columns={"bs": "ok"})
x = cb.merge(bn, on="t").merge(ok, on="t").sort_values("t"); x["ref"] = (x.bn + x.ok) / 2
x["z"] = HC.zscore(np.log(x.cb / x.ref)); x["close"] = pd.to_datetime(x.t + 3600, unit="s", utc=True)
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
out = RB.summarize(tr, d, sp, np.random.default_rng(RB.SEED + 26), hold_bars=96); te = out["TEST"]
pos = all(out[p].get("mean_bp", -1) > 0 for p in ("EARLY", "TRAIN", "VALIDATION", "TEST"))
out["screen"] = "SCREEN-PASS" if (pos and te.get("mean_stress_bp", -1) > 0 and (te.get("p_vs_benchmark") or 1) <= 0.05 and te.get("trades", 0) >= 30) else "REJECTED"
out["hours_used"] = int(len(x))
for p in ("EARLY", "TRAIN", "VALIDATION", "TEST"):
    v = out[p]; print(p, v.get("trades"), "mean %+.2f stress %+.2f p %s" % (v.get("mean_bp", float("nan")), v.get("mean_stress_bp", float("nan")), v.get("p_vs_benchmark")))
print("SCREEN:", out["screen"]); json.dump(out, open(os.path.join(HERE, "backtest_results.json"), "w"), indent=1, default=float)
