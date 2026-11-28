"""STR-023 replication (PREREG.md). usage: DISCOVERY_DATA=<scratch with multi/bars/> python3 -I run_rep.py"""
import json, math, os, statistics, sys, tempfile
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ND), "rsi_vwap_study", "src")); import study as S  # noqa: E402  (frozen)
sys.path.insert(0, os.path.join(ND, "src")); import common as C  # noqa: E402
MK = ["SOLUSDm", "BNBUSDm", "XRPUSDm", "LTCUSDm", "BCHUSDm"]; W0, W1 = S.ts(2023, 1, 31), S.ts(2026, 11, 9)


def build(m):
    d = pd.read_csv(os.path.join(os.environ["DISCOVERY_DATA"], "multi", "bars", f"{m}_15m.csv.gz"))
    d["o"], d["h"], d["l"], d["c"] = (d.bo + d.ao) / 2, (d.bh + d.ah) / 2, (d.bl + d.al) / 2, (d.bc + d.ac) / 2
    sp = float(((d.ao - d.bo) / ((d.bo + d.ao) / 2))[d.t >= W0].median()); tmp = tempfile.mkdtemp(); paths = {}
    for iv, sec in (("15m", 900), ("1h", 3600), ("1d", 86400)):
        g = d.groupby(d.t // sec * sec)
        rows = [[int(t), float(r.o), float(r.h), float(r.l), float(r.c), float(r.v)] for t, r in pd.DataFrame(dict(o=g.o.first(), h=g.h.max(), l=g.l.min(), c=g.c.last(), v=g.ticks.sum())).iterrows()]
        paths[iv] = os.path.join(tmp, f"{iv}.json"); json.dump(rows, open(paths[iv], "w"))
    return S.Asset(m, paths["15m"], paths["1h"], paths["1d"]), sp


def main():
    R = {}
    for m in MK:
        A, sp = build(m); cost = 1.5 * sp
        tr = A.run("V1_VWAP_MOMENTUM", 1, "TRAIL", W0, W1)
        r_dec = [t.r_gross - cost * t.entry / t.risk for t in tr]; r_005 = [t.r("primary") for t in tr]
        rb = S.random_benchmark(A, tr, 1, "TRAIL", W0, W1, "primary") if len(tr) > 10 else {}
        n = len(tr); sd = statistics.stdev(r_dec) if n > 2 else float("nan")
        R[m] = dict(trades=n, median_spread_pct=round(100 * sp, 4), decision_cost_pct=round(100 * cost, 4), mean_R_decision_cost=round(statistics.mean(r_dec), 4) if n else None,
                    t_decision_cost=round(statistics.mean(r_dec) / (sd / math.sqrt(n)), 2) if n > 2 else None, mean_R_study_cost=round(statistics.mean(r_005), 4) if n else None,
                    random_mean_R_study_cost=round(rb.get("random_mean_r", float("nan")), 4), p_random=rb.get("p_random"),
                    avg_risk_pct_of_price=round(100 * statistics.mean(t.risk / t.entry for t in tr), 3) if n else None)
        print(m, R[m], flush=True)
    ps = [R[m]["p_random"] if R[m]["p_random"] is not None else 1.0 for m in MK]; sig = C.bh(ps)
    pos = [m for m in MK if (R[m]["mean_R_decision_cost"] or -1) > 0]; ok = [m for i, m in enumerate(MK) if i in sig and m in pos]
    verdict = "REPLICATED" if len(ok) >= 3 else ("PARTIAL" if len(pos) >= 3 else "NOT REPLICATED")
    json.dump(dict(results=R, positive_at_decision_cost=pos, significant_and_positive=ok, verdict=verdict), open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("VERDICT:", verdict, "| positive:", pos, "| significant:", ok)


if __name__ == "__main__":
    main()
