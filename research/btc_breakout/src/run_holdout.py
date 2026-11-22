"""Stage 2: single evaluation of the untouched holdout (2025-07-01 .. end). Refuses to run if the locked pass list changed.
Passing variants are judged against the holdout criteria. All other variants are also reported, marked 'not eligible'
(transparency only; nothing is re-selected)."""
import csv, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from protocol import MODELS, STOPS, DIRS, COSTS, HOLDOUT, PASS
from engine import Lab, metrics
ROOT = os.path.join(os.path.dirname(__file__), ".."); EXPECTED = sys.argv[1]
s = open(f"{ROOT}/reports/LOCKED_pass_list.json").read()
if hashlib.sha256(s.encode()).hexdigest() != EXPECTED: raise SystemExit("locked pass list changed - refusing to evaluate holdout")
locked = json.loads(s)["passed"]
L = Lab(f"{ROOT}/data"); _, w0, w1 = HOLDOUT; D = L.B["1d"]
idx = [i for i, t in enumerate(D["t"]) if t >= w0]; p = [D["c"][i] for i in idx]; peak = p[0]; mdd = 0
for x in p: peak = max(peak, x); mdd = max(mdd, 1 - x / peak)
bh = dict(ret_pct=round((p[-1] / D["o"][idx[0]] - 1) * 100, 2), max_dd_pct=round(mdd * 100, 2))
os.makedirs(f"{ROOT}/logs/holdout", exist_ok=True); out = {}
for tf in ("1h", "15m"):
    for model in MODELS:
        for d in DIRS:
            for stop in STOPS:
                vid = f"{tf}_{model}_{'LONG' if d > 0 else 'SHORT'}_{stop}"
                tr = L.simulate(tf, model, d, stop, w0, w1)
                with open(f"{ROOT}/logs/holdout/{vid}.csv", "w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=["entry_time_utc", "exit_time_utc", "side", "entry", "risk", "R_gross", "exit", "regime", "hold_h"]); w.writeheader()
                    for t in tr: w.writerow(dict(entry_time_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t["entry_time"])), exit_time_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(t["exit_time"])),
                                                 side=t["side"], entry=t["entry"], risk=t["risk"], R_gross=t["R_gross"], exit=t["exit"], regime=t["regime"], hold_h=t["hold_h"]))
                m = {c: metrics(tr, v) for c, v in COSTS.items()}
                reg = {g: metrics([t for t in tr if t["regime"] == g], COSTS["mid"]) for g in ("bull", "bear", "sideways")}
                eligible = vid in locked; mm = m["mid"]
                ok = eligible and mm["trades"] >= PASS["holdout_min_trades"] and (mm["expectancy"] or 0) > 0 and (mm["pf"] or 0) >= PASS["holdout_min_pf"]
                out[vid] = dict(eligible=eligible, passed_holdout=ok, metrics=m, regimes_mid=reg)
                tag = ("PASS" if ok else "FAIL") if eligible else "(not eligible)"
                print(f"{vid:38} n={mm['trades']:3} E={mm['expectancy']!s:>8} PF={mm['pf']!s:>6} net={mm['net_pct']:7} DD={mm['max_dd_pct']:6} win%={mm['win_rate']!s:>5} hold={mm['avg_hold_h']!s:>5}h  {tag}", flush=True)
json.dump(dict(holdout=out, buy_and_hold=bh, audit=L.audit), open(f"{ROOT}/reports/holdout_results.json", "w"), indent=1)
print("\nbuy & hold over holdout:", bh, "| audit:", L.audit)
print("FINAL:", [v for v, r in out.items() if r["passed_holdout"]] or "NO EDGE FOUND")
