"""STR-050 (PREREG.md). usage: python3 -I run_negcorr.py <pairs_cfg.json from batch 006>"""
import json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pairs_batch_006"))
import run_pairs6 as P6  # noqa: E402  daily_from_15m, pair_trades, bench, summarize, PER
PER = P6.PER


def main():
    cfg = json.load(open(sys.argv[1])); M = cfg["MULTI"]; rng = np.random.default_rng(3050); R = {}; LL = {}
    f15 = lambda s: P6.daily_from_15m(os.path.join(M, f"{s}_15m.csv.gz"), "America/New_York", 16, 0)
    xau = P6.daily_from_15m(cfg["XAU15"], "America/New_York", 16, 0); oil = P6.daily_from_15m(cfg["OIL15"], "America/New_York", 16, 0)
    xau = xau[[str(d) >= "2023-01-01" for d in xau.index]]; oil = oil[[str(d) >= "2023-01-01" for d in oil.index]]
    pairs = {"a|EURUSD~USDCHF": (f15("EURUSDm"), f15("USDCHFm")), "b|GBPUSD~USDCHF": (f15("GBPUSDm"), f15("USDCHFm")),
             "c|XAU~USDCHF": (xau, f15("USDCHFm")), "d|XAU~USDJPY": (xau, f15("USDJPYm")), "e|USOIL~USDCAD": (oil, f15("USDCADm"))}
    for k, (a, b) in pairs.items():
        tr, j, ret, cost = P6.pair_trades(a, b, 2.0); res = P6.summarize(tr, P6.bench(tr, j, ret, cost, rng))
        ra, rb = np.log(j.pA).diff(), np.log(j.pB).diff(); corr = ra.rolling(60).corr(rb)
        for p, lo, hi in PER:
            sel = [lo <= str(d) < hi for d in j.index]
            if p in res and any(sel): res[p]["mean_60d_corr"] = round(float(corr[sel].mean()), 3) if corr[sel].notna().any() else None
        res["avg_beta"] = round(float(np.mean([t["b"] for t in tr])), 3) if tr else None
        R["STR-050" + k] = dict(results=res, trades=len(tr)); print(k, json.dumps({p: (v.get("trades"), v.get("mean_net_bp"), v.get("p"), v.get("mean_60d_corr")) for p, v in res.items() if isinstance(v, dict)}), "beta", res["avg_beta"], flush=True)
        for nameX, X, Y in ((k + " A->B", ra, rb), (k + " B->A", rb, ra)):
            LL[nameX] = {}
            for p, lo, hi in PER:
                df = pd.DataFrame(dict(x=X, y=Y.shift(-1))).dropna(); df = df[[lo <= str(d) < hi for d in df.index]]
                if len(df) < 30: continue
                ic = float(np.corrcoef(df.x.rank(), df.y.rank())[0, 1]); n = len(df); t = ic * math.sqrt((n - 2) / (1 - ic * ic))
                LL[nameX][p] = dict(n=n, ic=round(ic, 4), t=round(t, 2), p_two_sided=float(math.erfc(abs(t) / math.sqrt(2))))
    keys = list(R); ps = [R[k]["results"].get("TEST", {}).get("p", 1.0) for k in keys]; o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / len(ps): sig = set(o[:r + 1])
    for i, k in enumerate(keys):
        f = R[k]["results"]; av = [p for p, *_ in PER if f.get(p, {}).get("mean_net_bp") is not None]; pos = bool(av) and all(f[p]["mean_net_bp"] > 0 for p in av); te = f.get("TEST", {})
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_stress_bp", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED"); print(k, R[k]["decision"])
    lk = [k for k in LL if "TEST" in LL[k]]; lp = [LL[k]["TEST"]["p_two_sided"] for k in lk]; o = np.argsort(lp); sig = set()
    for r, i in enumerate(o):
        if lp[i] <= 0.05 * (r + 1) / len(lp): sig = set(o[:r + 1])
    for i, k in enumerate(lk):
        LL[k]["TEST"]["bh_significant"] = i in sig; same = len({np.sign(LL[k][p]["ic"]) for p in ("TRAIN", "VALIDATION", "TEST") if p in LL[k]}) == 1
        LL[k]["consistent_sign_all_periods"] = same; print("lead-lag", k, {p: (v["ic"], v["t"]) for p, v in LL[k].items() if isinstance(v, dict)}, "BH" if i in sig else "", "same-sign" if same else "")
    json.dump(dict(mean_reversion=R, lead_lag=LL), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
