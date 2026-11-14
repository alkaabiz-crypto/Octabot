"""Prospective validation design: sample size, interim looks and stopping boundaries, by simulation.

Inputs are the REAL per-trade results of the frozen rules on Exness BTCUSDm quotes 2020-01..2026-11 (measured
spread + 0.02% slippage), and the REAL results of random entries taken under the same 4H filter with the same exit.
Trades are resampled independently (the validation found no serial dependence: Ljung-Box p > 0.5).

Two endpoints:
  RELATIVE  does the Donchian trigger beat random entry under identical filter, exit and costs?
            H0: forward trades come from the random-entry distribution.  The validation measured an excess of only
            about +0.04R (not significant), so designs are shown for +0.05, +0.15 and +0.30R to show what each needs.
  ABSOLUTE  is the all-in expectancy above zero?  H0: mean R <= 0.  Design effect: +0.15R (about the backtest
            all-in estimate before any allowance for selection bias, so this is optimistic).
Group-sequential plan: looks every 40 trades. Efficacy boundary of O'Brien-Fleming shape calibrated to one-sided
alpha = 0.025; non-binding futility boundary calibrated to lose at most 10% power at the design effect.
Writes reports/protocol_design.json.
"""
import itertools
import json
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
import exness_lab
import replica

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COST = 0.0002
LOOK = 40
SIMS = 10000
ALPHA, BETA_FUT, POWER_TARGET = 0.025, 0.10, 0.80
TRADES_PER_YEAR = None   # filled from data


def pools():
    lab, ask = exness_lab.build_lab()
    m = replica.Market(lab, exec_open=ask["o"])
    w0, w1 = config.ALL[1], config.ALL[2]
    strat = [t for t in m.run(w0, 10 ** 11) if t.reason != "data_end" and w0 <= t.entry_time < w1]
    rand = []
    for i in range(len(m.E["t"])):
        tc = m.E["t"][i] + 3600
        if w0 <= tc < w1 and m.filter_on[i]:
            tr = m.simulate_from(i)
            if tr is not None and tr.reason != "data_end":
                rand.append(tr.r_net(COST))
    years = (w1 - w0) / (365.25 * 86400)
    return [t.r_net(COST) for t in strat], rand, len(strat) / years


def paths(pool, shift, n_max, sims, seed):
    """Cumulative sums and sums of squares at each look, for ``sims`` resampled sequences."""
    rnd = random.Random(seed)
    looks = list(range(LOOK, n_max + 1, LOOK))
    out = []
    for _ in range(sims):
        x = [v + shift for v in rnd.choices(pool, k=n_max)]
        cs = list(itertools.accumulate(x))
        out.append([cs[n - 1] for n in looks])
    return looks, out


def design(pool_h0, mu0, sd0, pool_h1, shift_h1, n_max, seed):
    """Calibrate boundaries for z = (mean - mu0) / (sd0 / sqrt(n)) and return operating characteristics."""
    looks, null = paths(pool_h0, 0.0, n_max, SIMS, seed)
    _, alt = paths(pool_h1, shift_h1, n_max, SIMS, seed + 1)
    w = [math.sqrt(n / n_max) for n in looks]

    def z(path):
        return [(s / n - mu0) / (sd0 / math.sqrt(n)) for s, n in zip(path, looks)]
    zn = [z(p) for p in null]
    za = [z(p) for p in alt]
    c = sorted(max(zk * wk for zk, wk in zip(zz, w)) for zz in zn)[int((1 - ALPHA) * SIMS)]
    eff = [c / wk for wk in w]
    delta = (statistics.mean(pool_h1) + shift_h1 - mu0) / sd0
    drift = [delta * math.sqrt(n) for n in looks]
    d = sorted(max((dr - zk) * wk for zk, dr, wk in zip(zz, drift, w)) for zz in za)[int((1 - BETA_FUT) * SIMS)]
    fut = [min(dr - d / wk, e) for dr, wk, e in zip(drift, w, eff)]
    fut[-1] = eff[-1]

    def run(zs):
        for k, zk in enumerate(zs):
            if zk >= eff[k]:
                return "efficacy", looks[k]
            if zk < fut[k] and looks[k] >= 2 * LOOK:      # no futility stop at the 40-trade checkpoint
                return "futility", looks[k]
        return "futility", looks[-1]

    def oc(zs_all):
        res = [run(zz) for zz in zs_all]
        return {"p_efficacy": sum(r[0] == "efficacy" for r in res) / len(res), "expected_trades": statistics.mean(r[1] for r in res),
                    "p_stop_by_120": sum(r[1] <= 120 for r in res) / len(res), "p_stop_by_240": sum(r[1] <= 240 for r in res) / len(res)}
    return {"n_max": n_max, "looks": looks, "efficacy_z": eff, "futility_z": fut,
                "efficacy_mean_r": [mu0 + e * sd0 / math.sqrt(n) for e, n in zip(eff, looks)],
                "futility_mean_r": [mu0 + f * sd0 / math.sqrt(n) for f, n in zip(fut, looks)],
                "under_h0": oc(zn), "under_h1": oc(za)}


def fixed_n(sd, effect, alpha=ALPHA, power=POWER_TARGET):
    za, zb = 2.0, 0.84   # one-sided 0.025 -> 1.96, rounded up slightly for heavy tails
    return math.ceil(((za + zb) * sd / effect) ** 2)


def checkpoint40(pool, mu_alt):
    rnd = random.Random(config.SEED)
    m = statistics.mean(pool)
    res = {}
    for label, shift in (("true edge = backtest all-in estimate", 0.0), ("true edge = 0", -m)):
        means, dds, cums = [], [], []
        for _ in range(SIMS):
            x = [v + shift for v in rnd.choices(pool, k=40)]
            means.append(statistics.mean(x))
            cum = peak = dd = 0.0
            for v in x:
                cum += v
                peak = max(peak, cum)
                dd = max(dd, peak - cum)
            dds.append(dd)
            cums.append(cum)
        means.sort()
        dds.sort()
        res[label] = {"mean_r_p05_p50_p95": (means[int(0.05 * SIMS)], means[SIMS // 2], means[int(0.95 * SIMS)]),
                          "p_mean_negative": sum(v < 0 for v in means) / SIMS, "p_mean_above_backtest": sum(v >= m for v in means) / SIMS,
                          "max_drawdown_r_p50_p95_p99": (dds[SIMS // 2], dds[int(0.95 * SIMS)], dds[int(0.99 * SIMS)]),
                          "cumulative_r_p01": sorted(cums)[int(0.01 * SIMS)]}
    return res


def main():
    strat, rand, per_year = pools()
    mu_s, sd_s = statistics.mean(strat), statistics.stdev(strat)
    mu_r, sd_r = statistics.mean(rand), statistics.stdev(rand)
    print(f"strategy trades {len(strat)} mean {mu_s:.3f} sd {sd_s:.3f}; random-entry outcomes {len(rand)} mean {mu_r:.3f} sd {sd_r:.3f}; {per_year:.1f} trades/yr")
    out = {"inputs": {"strategy_trades": len(strat), "strategy_mean_r": mu_s, "strategy_sd_r": sd_s, "random_outcomes": len(rand),
                           "random_mean_r": mu_r, "random_sd_r": sd_r, "trades_per_year": per_year, "cost": "Exness measured spread + 0.02% slippage",
                           "look_every": LOOK, "sims": SIMS, "alpha_one_sided": ALPHA, "futility_power_loss": BETA_FUT}}
    # fixed-sample sizes for reference
    out["fixed_sample_trades_80pct_power"] = {
        f"absolute edge {e:.2f}R": {"trades": fixed_n(sd_s, e), "years": fixed_n(sd_s, e) / per_year} for e in (0.05, 0.10, 0.15, 0.20, 0.25)}
    out["fixed_sample_trades_80pct_power"].update({
        f"relative edge {e:.2f}R over random": {"trades": fixed_n(sd_r, e), "years": fixed_n(sd_r, e) / per_year} for e in (0.04, 0.05, 0.10, 0.15, 0.30)})
    # relative endpoint: H0 = random-entry distribution; H1 = strategy distribution shifted to mu_r + 0.30
    rel = []
    for n_max in (480, 960):
        for eff in (0.05, 0.15, 0.30):
            d = design(rand, mu_r, sd_r, strat, (mu_r + eff) - mu_s, n_max, config.SEED + n_max)
            d["design_effect_r"] = eff
            rel.append(d)
            print("relative", n_max, eff, round(d["under_h1"]["p_efficacy"], 3), round(d["under_h0"]["p_efficacy"], 4))
    out["relative_designs"] = rel
    # absolute endpoint: what a sequential design would need
    absd = []
    for n_max in (480, 960, 1920):
        d = design([v - mu_s for v in strat], 0.0, sd_s, strat, 0.15 - mu_s, n_max, config.SEED + 7 * n_max)
        d["design_effect_r"] = 0.15
        absd.append(d)
        print("absolute", n_max, round(d["under_h1"]["p_efficacy"], 3), round(d["under_h0"]["p_efficacy"], 4),
              "futility by 240 under H0", round(d["under_h0"]["p_stop_by_240"], 3))
    out["absolute_designs"] = absd
    out["checkpoint_40_trades"] = checkpoint40(strat, mu_s)
    with open(os.path.join(ROOT, "reports", "protocol_design.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("written")


if __name__ == "__main__":
    main()
