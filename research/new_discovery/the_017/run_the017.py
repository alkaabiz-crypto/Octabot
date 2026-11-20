"""THE-017 event study (PREREG.md). usage: DISCOVERY_DATA=<scratch> B003_DATA=<b003data> python3 -I run_the017.py"""
import json, math, os, sys
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ND = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ND, "ind_batch_001")); sys.path.insert(0, os.path.join(ND, "src"))
import run_ind as RI, common as C  # noqa: E401,E402
RB = RI.RB
DISC, REPL = ["BTCUSDm", "EURUSDm"], ["XAUUSDm", "USOILm", "US500m", "USDJPYm", "GBPUSDm", "ETHUSDm"]; P = ["EARLY", "TRAIN", "VALIDATION", "TEST"]


def nw_t(x, L=5):
    x = np.asarray(x); n = len(x); m = x.mean(); d = x - m
    v = (d @ d) / n + 2 * sum((1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n for j in range(1, min(L, n - 1) + 1)); return float(m / math.sqrt(v / n)) if v > 0 else 0.0


def study(m, rng):
    df = RI.hourly(m); h, l, c, o = df.h, df.l, df.c, df.o
    wr = -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min())
    fwd = np.log(o.shift(-2) / o.shift(-1))                          # next hour, from the next open
    lab = pd.Series(np.where(wr >= -20, -1, np.where(wr <= -80, 1, 0)), index=df.index)   # +1 oversold (expect up), -1 overbought
    x = pd.DataFrame(dict(lab=lab, r=fwd, hr=df.index.hour)).dropna(); x["per"] = [RB.period(t) for t in x.index]
    sp = RB.spread_frac(RB.load(m)); out = {}
    for p in P:
        f = x[x.per == p]
        if (f.lab == 1).sum() < 30 or (f.lab == -1).sum() < 30: continue
        eff = 1e4 * (f.r[f.lab == 1].mean() - f.r[f.lab == -1].mean())
        sims = np.empty(2000); grp = [g.index for _, g in f.groupby("hr")]; labs = f.lab.values.copy(); pos = {t: i for i, t in enumerate(f.index)}
        idx_groups = [np.array([pos[t] for t in g]) for g in grp]; r = f.r.values
        for k in range(2000):
            sh = labs.copy()
            for ig in idx_groups: sh[ig] = rng.permutation(labs[ig])
            sims[k] = 1e4 * (r[sh == 1].mean() - r[sh == -1].mean())
        ev = f[f.lab != 0]; signed = (ev.lab * ev.r).values * 1e4
        out[p] = dict(n_oversold=int((f.lab == 1).sum()), n_overbought=int((f.lab == -1).sum()), effect_bp=round(float(eff), 3),
                      p_matched_null=float((sims >= eff).mean()), nw_t_signed=round(nw_t(signed), 2), per_event_bp=round(float(signed.mean()), 3),
                      cost_bp=round(float(1e4 * 1.5 * sp), 2))
    return out


def main():
    rng = np.random.default_rng(17017); R = {m: study(m, rng) for m in DISC + REPL}
    for m, v in R.items(): print(m, {p: (x["effect_bp"], round(x["p_matched_null"], 4), x["per_event_bp"], x["cost_bp"]) for p, x in v.items()}, flush=True)
    disc_ok = all(all(x["effect_bp"] > 0 for x in R[m].values()) and R[m].get("TEST", {}).get("p_matched_null", 1) <= 0.05 for m in DISC)
    rp = [R[m].get("TEST", {}).get("p_matched_null", 1.0) for m in REPL]; sig = C.bh(rp)
    rep_ok = [m for i, m in enumerate(REPL) if i in sig and R[m]["TEST"]["effect_bp"] > 0]
    early_sig = any(R[m].get("EARLY", {}).get("p_matched_null", 1) <= 0.05 for m in DISC + REPL)
    verdict = "SUPPORTED" if (disc_ok and len(rep_ok) >= 3) else ("PARTLY SUPPORTED" if disc_ok else ("DECAYED" if early_sig else "NOT SUPPORTED"))
    trad = {m: (R[m]["TEST"]["per_event_bp"], R[m]["TEST"]["cost_bp"]) for m in R if "TEST" in R[m]}
    out = dict(results=R, discovery_holds=disc_ok, replicated_markets=rep_ok, verdict=verdict, tradability_test_per_event_vs_cost_bp=trad)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1); print("VERDICT:", verdict, "| replicated:", rep_ok); print("per-event vs cost (TEST):", trad)


if __name__ == "__main__":
    main()
