"""Stage 1: walk-forward evaluation of all 48 variants on 2020H1..2025H1. Writes trade logs, metrics and the LOCKED pass
list. Does not touch the holdout period."""
import csv, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from protocol import MODELS, STOPS, DIRS, COSTS, WINDOWS, PASS
from engine import Lab, metrics
ROOT = os.path.join(os.path.dirname(__file__), "..")
L = Lab(f"{ROOT}/data"); results = {}
D = L.B["1d"]
def bh(w0, w1):  # buy-and-hold from first daily close >= w0 to last daily close < w1
    idx = [i for i, t in enumerate(D["t"]) if w0 <= t < w1]
    p = [D["c"][i] for i in idx]; peak, mdd = p[0], 0
    for x in p: peak = max(peak, x); mdd = max(mdd, 1 - x / peak)
    return dict(ret_pct=round((p[-1] / D["o"][idx[0]] - 1) * 100, 2), max_dd_pct=round(mdd * 100, 2))
baselines = {name: bh(w0, w1) for name, w0, w1 in WINDOWS}
baselines["ALL_WF"] = bh(WINDOWS[0][1], WINDOWS[-1][2])
os.makedirs(f"{ROOT}/logs/walkforward", exist_ok=True)
for tf in ("1h", "15m"):
    for model in MODELS:
        for d in DIRS:
            for stop in STOPS:
                vid = f"{tf}_{model}_{'LONG' if d > 0 else 'SHORT'}_{stop}"
                per_win = {name: L.simulate(tf, model, d, stop, w0, w1) for name, w0, w1 in WINDOWS}
                allt = [t for name, *_ in WINDOWS for t in per_win[name]]
                with open(f"{ROOT}/logs/walkforward/{vid}.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=["window", "entry_time_utc", "exit_time_utc", "side", "entry", "risk", "R_gross", "exit", "regime", "hold_h"])
                    w.writeheader()
                    for name, *_ in WINDOWS:
                        for t in per_win[name]:
                            w.writerow(dict(window=name, entry_time_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t["entry_time"])),
                                            exit_time_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t["exit_time"])), side=t["side"], entry=t["entry"],
                                            risk=t["risk"], R_gross=t["R_gross"], exit=t["exit"], regime=t["regime"], hold_h=t["hold_h"]))
                m = {c: metrics(allt, v) for c, v in COSTS.items()}
                win_mid = {name: metrics(per_win[name], COSTS["mid"]) for name, *_ in WINDOWS}
                pos_w = sum(1 for x in win_mid.values() if x["trades"] and x["expectancy"] > 0)
                reg = {g: metrics([t for t in allt if t["regime"] == g], COSTS["mid"]) for g in ("bull", "bear", "sideways")}
                mm = m["mid"]
                passed = (mm["trades"] >= PASS["min_trades"] and (mm["expectancy"] or 0) > 0 and (mm["t_stat"] or 0) >= PASS["min_t"]
                          and (mm["pf"] or 0) >= PASS["min_pf"] and pos_w >= PASS["min_pos_windows"] and (m["high"]["expectancy"] or 0) > 0)
                results[vid] = dict(metrics=m, positive_windows=pos_w, windows_mid=win_mid, regimes_mid=reg, passed_walkforward=passed)
                print(f"{vid:38} n={mm['trades']:4} E={mm['expectancy']!s:>8} t={mm['t_stat']!s:>6} PF={mm['pf']!s:>6} net={mm['net_pct']:7} DD={mm['max_dd_pct']:6} win%={mm['win_rate']!s:>5} hold={mm['avg_hold_h']!s:>6}h pos_w={pos_w:2}/11 {'PASS' if passed else ''}", flush=True)
json.dump(dict(results=results, baselines=baselines, audit=L.audit), open(f"{ROOT}/reports/walkforward_results.json", "w"), indent=1)
lock = dict(stage="walk-forward complete; holdout untouched", passed=[v for v, r in results.items() if r["passed_walkforward"]], criteria=PASS)
s = json.dumps(lock, indent=1, sort_keys=True); open(f"{ROOT}/reports/LOCKED_pass_list.json", "w").write(s)
print("\nLOCKED pass list:", lock["passed"], "sha256:", hashlib.sha256(s.encode()).hexdigest())
print("baselines (buy & hold):", json.dumps(baselines)); print("audit:", L.audit)
