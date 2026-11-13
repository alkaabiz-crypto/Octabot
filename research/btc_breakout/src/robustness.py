"""Stage 3 diagnostics for the holdout survivors (no re-selection). Significance, costs, tail dependence, regimes,
parameter-neighbourhood stability and overlap between survivors."""
import json, math, os, statistics, sys
sys.path.insert(0, os.path.dirname(__file__))
import engine
from engine import Lab, metrics
from protocol import COSTS, WINDOWS, HOLDOUT
ROOT = os.path.join(os.path.dirname(__file__), "..")
SURV = [("1h", "M1_BB_SQUEEZE", 1, "TRAIL"), ("1h", "M2_DONCHIAN20", 1, "TRAIL"), ("1h", "M4_DONCHIAN_VOL", 1, "TRAIL")]
L = Lab(f"{ROOT}/data"); W0, W1 = WINDOWS[0][1], WINDOWS[-1][2]; H0, H1 = HOLDOUT[1], HOLDOUT[2]
rep = {}
def pooled(tf, m, d, s):
    wf = [t for _, a, b in WINDOWS for t in L.simulate(tf, m, d, s, a, b)]
    ho = L.simulate(tf, m, d, s, H0, H1); return wf, ho
for tf, m, d, s in SURV:
    vid = f"{tf}_{m}_LONG_{s}"; wf, ho = pooled(tf, m, d, s); r = {}
    for name, tr in (("walkforward", wf), ("holdout", ho)):
        x = {c: metrics(tr, v) for c, v in COSTS.items()}
        net = sorted([t["R_gross"] - COSTS["mid"] * t["k"] for t in tr], reverse=True)
        cut = max(1, len(net) // 20)
        x["without_top5pct_trades_E_mid"] = round(statistics.mean(net[cut:]), 4)
        x["top5pct_share_of_total_R"] = round(sum(net[:cut]) / sum(net), 2) if sum(net) > 0 else None
        x["exit_reasons"] = {k: sum(1 for t in tr if t["exit"] == k) for k in {t["exit"] for t in tr}}
        x["regimes_mid"] = {g: metrics([t for t in tr if t["regime"] == g], COSTS["mid"]) for g in ("bull", "bear", "sideways")}
        r[name] = x
    rep[vid] = r
    print(f"\n### {vid}")
    for name in ("walkforward", "holdout"):
        x = r[name]
        print(f"  {name:11} mid: n={x['mid']['trades']} E={x['mid']['expectancy']} t={x['mid']['t_stat']} PF={x['mid']['pf']} net={x['mid']['net_pct']}% DD={x['mid']['max_dd_pct']}% win={x['mid']['win_rate']}% hold={x['mid']['avg_hold_h']}h | high-cost E={x['high']['expectancy']} PF={x['high']['pf']}")
        print(f"              without top 5% trades E={x['without_top5pct_trades_E_mid']} (top 5% = {x['top5pct_share_of_total_R']} of total R) exits={x['exit_reasons']}")
        print("              regimes:", {g: (v['trades'], v['expectancy'], v['pf']) for g, v in x["regimes_mid"].items()})
# overlap between survivors (same entry candle)
sets = {}
for tf, m, d, s in SURV:
    wf, ho = pooled(tf, m, d, s); sets[m] = {t["entry_time"] for t in wf + ho}
names = list(sets); print("\nentry overlap (share of row's trades also taken by column):")
for a in names: print(f"  {a:16}", {b: round(len(sets[a] & sets[b]) / len(sets[a]), 2) for b in names if b != a})
# parameter neighbourhood (diagnostic only, NOT used to choose anything)
print("\nparameter neighbourhood, 1H Donchian long + trailing stop (4H trend), mid cost. Locked default = DC20 / stop 2.0 / trail 3.0")
nb = {}
for dc in (15, 20, 30, 40):
    for stop_m in (1.5, 2.0, 2.5):
        for trail_m in (2.0, 3.0, 4.0):
            wf = [t for _, a, b in WINDOWS for t in L.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", a, b, stop_mult=stop_m, trail_mult=trail_m, dc_len=dc)]
            ho = L.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", H0, H1, stop_mult=stop_m, trail_mult=trail_m, dc_len=dc)
            a, b = metrics(wf, COSTS["mid"]), metrics(ho, COSTS["mid"])
            nb[f"dc{dc}_stop{stop_m}_trail{trail_m}"] = dict(walkforward=a, holdout=b)
            print(f"  DC{dc:2} stop {stop_m} trail {trail_m}: WF n={a['trades']:4} E={a['expectancy']!s:>7} t={a['t_stat']!s:>5} PF={a['pf']!s:>6} | HOLDOUT n={b['trades']:3} E={b['expectancy']!s:>7} PF={b['pf']!s:>6}")
wf_pos = sum(1 for v in nb.values() if (v["walkforward"]["expectancy"] or 0) > 0); ho_pos = sum(1 for v in nb.values() if (v["holdout"]["expectancy"] or 0) > 0)
print(f"  neighbours with positive expectancy: walk-forward {wf_pos}/{len(nb)}, holdout {ho_pos}/{len(nb)}")
rep["neighbourhood"] = nb
json.dump(rep, open(f"{ROOT}/reports/robustness.json", "w"), indent=1)
