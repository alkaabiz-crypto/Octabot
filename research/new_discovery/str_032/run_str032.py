"""STR-032 (PREREG.md): GainzAlgo-style engulfing + RSI. usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_str032.py"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
for p in ("ind_batch_001", "ind_batch_002", "tv_batch_003", "tv_batch_004", "tv_batch_005", "src"): sys.path.insert(0, os.path.join(ND, p))
import run_ind as RI, run_tv4 as T4, run_tv5 as T5, common as C  # noqa: E401,E402


def signals(df, k):
    o, c = df.o, df.c; r = RI.rsi(c)
    bull = (c > o) & (c.shift() < o.shift()) & (o <= c.shift()) & (c >= o.shift()) & (r < k)
    bear = (c < o) & (c.shift() > o.shift()) & (o >= c.shift()) & (c <= o.shift()) & (r > 100 - k)
    L = np.zeros(len(df), bool); S = np.zeros(len(df), bool); last = 0
    for i, (b, s) in enumerate(zip(bull.fillna(False).values, bear.fillna(False).values)):
        if b and last != 1: L[i], last = True, 1
        elif s and last != -1: S[i], last = True, -1
    return pd.Series(L, index=df.index), pd.Series(S, index=df.index)


def main():
    R = {}; rng = np.random.default_rng(3032)
    for m in RI.MKTS:
        df, sp = T4.hourly_v(m); A = RI.atr(df)
        for name, k in (("A_k50", 50), ("B_k30", 30)):
            L, S = signals(df, k); R[f"STR-032{name[0]}|{m}"] = dict(kind="trade", k=k, results=T5.evaluate(df, A, L, S, 1.5 * sp, rng))
        print(m, flush=True)
    keys = list(R); sig = C.bh([R[k]["results"]["TEST"].get("p_random", 1.0) for k in keys])
    for i, k in enumerate(keys):
        f = R[k]["results"]; av = [p for p in RI.P if f[p].get("mean_R") is not None]; pos = bool(av) and all(f[p]["mean_R"] > 0 for p in av); te = f["TEST"]
        R[k]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(k, R[k]["decision"], {p: (v.get("trades"), v.get("mean_R"), v.get("win_pct")) for p, v in f.items()}, te.get("p_random"), te.get("random_mean_R"))
    json.dump(dict(n_tests=len(keys), results=R), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
