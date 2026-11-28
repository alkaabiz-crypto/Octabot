"""Promotion-rule audit, mechanism decomposition and alternative causal execution policies (scratch only).
usage: python3 -I stats_audit.py <extract_dir> <bars_dir> <bin_dir> <out_json>
"""
import json, math, os, sys
import numpy as np

EXT, BARS, BIN, OUT = sys.argv[1:5]; os.environ["BARS_DIR"], os.environ["BIN_DIR"] = BARS, BIN
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import sim as S  # noqa: E402
sys.path.insert(0, os.path.join(EXT, "research", "theory_library")); import verify_minute as V  # noqa: E402
HOLD = 1767225600000 // 60000
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))


def net2_bt(M, side, f, x, pe, px): return side * (px - pe) / pe - 2 * (M["hs"][f] + M["hs"][x]) / pe


def pass_prob(r, mu, n=100, B=20000, block=None, seed=3):
    """P(mean of the first n trades >= 2 bp) when the true mean is mu: (a) normal approx with the observed sd,
    (b) iid bootstrap of the re-centred trades, (c) stationary block bootstrap (mean block 5) of the re-centred trades."""
    x = r - r.mean() + mu; sd = r.std(ddof=1); rng = np.random.default_rng(seed)
    normal = 1 - Phi((2e-4 - mu) / (sd / math.sqrt(n)))
    iid = float((x[rng.integers(len(x), size=(B, n))].mean(axis=1) >= 2e-4).mean())
    idx = np.empty((B, n), int); idx[:, 0] = rng.integers(len(x), size=B)
    for k in range(1, n):
        idx[:, k] = np.where(rng.random(B) < 0.2, rng.integers(len(x), size=B), (idx[:, k - 1] + 1) % len(x))
    blk = float((x[idx].mean(axis=1) >= 2e-4).mean())
    return dict(normal=round(normal, 3), iid_bootstrap=round(iid, 3), block_bootstrap=round(blk, 3))


def main():
    out = {}
    cfg = {"ETHUSDT": ("fib", lambda px, q: px * 1e-4, lambda a, b: 0.0005 * (a + b) / a), "USOILm": ("fib", lambda px, q: 0.02, lambda a, b: 0.02 / a),
           "XAUUSDm": ("fvg", lambda px, q: 0.22, lambda a, b: 0.22 / a)}
    for mkt, (kind, pen_f, cost_f) in cfg.items():
        M, Hc = V.load(mkt); m, o, h, l, c = M["m"], M["o"], M["h"], M["l"], M["c"]; pen_bt = lambda px, q: M["pen"][q]; res = {}
        # forward model (wall clock, forward.py's own costs) -> the distribution the paper test will draw from
        fw, _ = S.simulate(m, o, h, l, c, kind, pen_f, clock="wall")
        r_fw = np.array([t["side"] * (t["exit"] - t["entry"]) / t["entry"] - 2 * cost_f(t["entry"], t["exit"]) for t in fw])
        res["forward_model_trades"] = len(r_fw); res["forward_model_mean_bp_2x"] = round(float(r_fw.mean() * 1e4), 2); res["forward_model_sd_bp"] = round(float(r_fw.std(ddof=1) * 1e4), 1)
        res["P_pass_true_mean_0"] = pass_prob(r_fw, 0.0)
        res["P_pass_true_mean_eq_causal_backtest"] = pass_prob(r_fw, r_fw.mean())
        res["P_pass_true_mean_plus10bp"] = pass_prob(r_fw, 10e-4)
        sd = r_fw.std(ddof=1); res["trades_needed_for_80pct_power_at_alpha5_one_sided"] = {f"+{e}bp": int(math.ceil(((1.645 + 0.8416) * sd / (e * 1e-4)) ** 2)) for e in (5, 10, 20)}
        # mechanism: which frozen trades survive causal selection, and what they earn (backtest costs, 2x, candle clock)
        fz = V.b9(M, Hc) if kind == "fib" else V.d4(M, Hc); cc, _ = S.simulate(m, o, h, l, c, kind, pen_bt, clock="candle", fib_need=51)
        F = {(s, f): net2_bt(M, s, f, x, pe, px) for s, f, x, pe, px in fz}; Cc = {(t["side"], t["f"]): net2_bt(M, t["side"], t["f"], t["x"], t["entry"], t["exit"]) for t in cc}
        both = F.keys() & Cc.keys(); fo = F.keys() - Cc.keys(); co = Cc.keys() - F.keys()
        mb = lambda d, ks: dict(n=len(ks), mean_bp=round(float(np.mean([d[k] for k in ks]) * 1e4), 2) if ks else None, sum_pct=round(float(np.sum([d[k] for k in ks]) * 100), 1) if ks else 0)
        res["mechanism"] = dict(identical_entries_frozen=mb(F, both), identical_entries_causal=mb(Cc, both), frozen_only=mb(F, fo), causal_only=mb(Cc, co))
        # among frozen-only trades: was a NEWER order (a causal trader would hold) filled first? -> measure from the causal set
        # alternative causal execution policies (adversarial robustness; not a parameter search: 2 disclosed policies)
        pol = {}
        for p in ("multi", "single", "replace"):
            tr, _ = S.simulate(m, o, h, l, c, kind, pen_bt, clock="candle", fib_need=51, policy=p)
            r = np.array([net2_bt(M, t["side"], t["f"], t["x"], t["entry"], t["exit"]) for t in tr]); fm = np.array([m[t["f"]] for t in tr])
            pol[p] = {per: dict(trades=int(s.sum()), mean_bp_2x=round(float(r[s].mean() * 1e4), 2)) for per, s in (("2025", fm < HOLD), ("2026", fm >= HOLD))}
        res["causal_policies_candle_clock_backtest_costs"] = pol
        out[mkt] = res; print(mkt, json.dumps(res), flush=True)
    # three tests evaluated together: chance that at least one zero-edge test passes
    mk = [k for k in out]; p0 = [out[k]["P_pass_true_mean_0"]["block_bootstrap"] for k in mk]
    out["P_at_least_one_of_three_passes_if_all_zero_edge"] = round(1 - float(np.prod([1 - p for p in p0])), 3)
    pc = [out[k]["P_pass_true_mean_eq_causal_backtest"]["block_bootstrap"] for k in mk]
    out["P_at_least_one_of_three_passes_at_causal_backtest_means"] = round(1 - float(np.prod([1 - p for p in pc])), 3)
    json.dump(out, open(OUT, "w"), indent=1); print(out["P_at_least_one_of_three_passes_if_all_zero_edge"], out["P_at_least_one_of_three_passes_at_causal_backtest_means"])


if __name__ == "__main__":
    main()
