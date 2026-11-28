"""Operating characteristics of the proposed paper-test decision rule (PROMOTION_RULE_V2.md), by simulation.
Trade returns are resampled (stationary block bootstrap, mean block 5) from each candidate's CAUSAL forward-model trades at 2x
cost (research/audits/library_candidates/causal_impact), re-centred to a chosen true mean.
Rule: looks at 100, 300, 600, 1000 closed trades. At each look: PASS if Newey-West t (5 lags) >= Z_CRIT and mean >= 2 bp;
STOP for futility if the one-sided 95% upper bound (mean + 1.645 NW se) < 2 bp. Z_CRIT = z(1 - 0.05 / (3 tests x 4 looks)).
usage: LIB_DIR=<theory_library extract> BARS_DIR=<exness 1m> BIN_DIR=<binance 1m> AUDIT_DIR=<causal_impact dir> python3 -I operating_characteristics.py
"""
import json, math, os, sys
import numpy as np
from statistics import NormalDist

LOOKS = (100, 300, 600, 1000); Z_CRIT = NormalDist().inv_cdf(1 - 0.05 / 12); MIN_BP = 2e-4
sys.path.insert(0, os.environ["AUDIT_DIR"]); import sim as S  # noqa: E402
sys.path.insert(0, os.environ["LIB_DIR"]); import verify_minute as V  # noqa: E402


def nw(x, L=5):
    n = len(x); d = x - x.mean(); v = (d @ d) / n + 2 * sum((1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n for j in range(1, L + 1)); return x.mean(), math.sqrt(max(v, 1e-30) / n)


def paths(x, B, n, rng):
    idx = np.empty((B, n), int); idx[:, 0] = rng.integers(len(x), size=B)
    for k in range(1, n): idx[:, k] = np.where(rng.random(B) < 0.2, rng.integers(len(x), size=B), (idx[:, k - 1] + 1) % len(x))
    return x[idx]


def oc(r, mu, B=4000, seed=7):
    rng = np.random.default_rng(seed); P = paths(r - r.mean() + mu, B, LOOKS[-1], rng); res = dict(pass_=0, futile=0, open_=0, pass_at={}, old_rule_pass_at_100=0)
    for p in P:
        res["old_rule_pass_at_100"] += p[:100].mean() >= MIN_BP; done = False
        for n in LOOKS:
            m, se = nw(p[:n])
            if m / se >= Z_CRIT and m >= MIN_BP: res["pass_"] += 1; res["pass_at"][n] = res["pass_at"].get(n, 0) + 1; done = True; break
            if m + 1.645 * se < MIN_BP: res["futile"] += 1; done = True; break
        if not done: res["open_"] += 1
    return dict(P_pass=round(res["pass_"] / B, 4), P_futility_stop=round(res["futile"] / B, 4), P_undecided_at_1000=round(res["open_"] / B, 4),
                pass_by_look={k: round(v / B, 4) for k, v in sorted(res["pass_at"].items())}, frozen_rule_P_pass_at_100=round(res["old_rule_pass_at_100"] / B, 4))


def main():
    out = dict(z_crit=round(Z_CRIT, 3), looks=LOOKS, markets={})
    cfg = {"ETHUSDT": ("fib", lambda px, q: px * 1e-4, lambda a, b: 0.0005 * (a + b) / a), "USOILm": ("fib", lambda px, q: 0.02, lambda a, b: 0.02 / a),
           "XAUUSDm": ("fvg", lambda px, q: 0.22, lambda a, b: 0.22 / a)}
    for mkt, (kind, pen, cost) in cfg.items():
        M, _ = V.load(mkt); tr, _ = S.simulate(M["m"], M["o"], M["h"], M["l"], M["c"], kind, pen, clock="wall")
        r = np.array([t["side"] * (t["exit"] - t["entry"]) / t["entry"] - 2 * cost(t["entry"], t["exit"]) for t in tr])
        out["markets"][mkt] = dict(trades=len(r), sd_bp=round(float(r.std(ddof=1) * 1e4), 1), causal_mean_bp=round(float(r.mean() * 1e4), 2),
                                   **{f"true_mean_{int(mu * 1e4)}bp": oc(r, mu) for mu in (0.0, 5e-4, 10e-4, 20e-4)},
                                   true_mean_causal=oc(r, r.mean()))
        print(mkt, json.dumps(out["markets"][mkt]), flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "operating_characteristics.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
