"""Apply the pre-registered prospective protocol (PROTOCOL.md) to the forward paper-test ledger. READ-ONLY.

Usage: FROZEN_BTC_BREAKOUT=<research/btc_breakout of a CURRENT checkout of the forward branch> \
       python src/evaluate_forward.py [--no-benchmark]

Reads forward/trades.csv (trades in recorded order) and the forward candles; never writes to the forward
directory. Writes reports/forward_evaluation_latest.json and .md in this project.

Evaluation happens only at looks of 40, 80, 120, ... completed trades. Between looks it reports progress only.
The matched random-entry benchmark for the forward period is rebuilt from the frozen research candles joined to the
forward candles (the overlap must agree exactly), with seed config.SEED, so it is reproducible and fixed in advance.
"""
import csv
import gzip
import json
import math
import os
import random
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
import frozen
import replica
import run_validation as rv
import vstats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOK = 40
STEP = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}


def read_trades(fwd):
    path = os.path.join(fwd, "trades.csv")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def parse(s):
    t = time.strptime(s, "%Y-%m-%d %H:%M")
    return config.ts(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour) + t.tm_min * 60


def merged_lab():
    """Frozen research candles + forward candles, joined after checking that the overlap is identical."""
    frozen.check_integrity()
    eng = frozen.engine_module()
    data = os.path.join(config.FROZEN_DIR, "data")
    fwd = os.path.join(config.FROZEN_DIR, "forward")
    raw = {}
    for tf in ("15m", "1h", "4h"):
        with open(os.path.join(data, f"btc_{tf}.json")) as f:
            base = {r[0]: r for r in json.load(f)}
        with gzip.open(os.path.join(fwd, f"candles_{tf}_forward.csv.gz"), "rt") as f:
            new = {parse(r["open_time_utc"]): [parse(r["open_time_utc"]), float(r["open"]), float(r["high"]), float(r["low"]),
                                                float(r["close"]), float(r["volume"])] for r in csv.DictReader(f)}
        for t, r in new.items():
            if t in base and any(abs(a - b) > 1e-6 for a, b in zip(base[t][1:5], r[1:5])):
                raise SystemExit(f"{tf} candle {t} differs between research data and forward candles")
            base[t] = r
        raw[tf] = [base[t] for t in sorted(base)]
    # daily candles for regime labels: research daily candles, then days after them aggregated from hourly candles
    with open(os.path.join(data, "btc_1d.json")) as f:
        daily = json.load(f)
    last_d = daily[-1][0]
    last_1h_close = raw["1h"][-1][0] + 3600
    agg = {}
    for r in raw["1h"]:
        d = r[0] // 86400 * 86400
        if d <= last_d:
            continue
        if d not in agg:
            agg[d] = [d, r[1], r[2], r[3], r[4], r[5]]
        else:
            x = agg[d]
            x[2], x[3], x[4], x[5] = max(x[2], r[2]), min(x[3], r[3]), r[4], x[5] + r[5]
    raw["1d"] = daily + [agg[d] for d in sorted(agg) if d + 86400 <= last_1h_close]
    lab = object.__new__(eng.Lab)
    lab.raw = raw
    lab.B = {tf: eng.build(cs) for tf, cs in raw.items()}
    lab.p_idx = {tt: i for i, tt in enumerate(lab.B["15m"]["t"])}
    lab.audit = {"htf_closed": [0, 0], "daily_closed": [0, 0], "entry_after_signal": [0, 0]}
    lab.sig_cache = {}
    return lab


def benchmark(fwd_start, n_done):
    lab = merged_lab()
    m = replica.Market(lab)
    last = lab.B["1h"]["t"][-1] + 3600
    strat = [t for t in m.run(fwd_start, 10 ** 11) if t.reason != "data_end"][:n_done]
    if not strat:
        return None
    w1 = strat[-1].exit_time
    outcomes = [t for t in rv.outcome_list(m, fwd_start, last, lambda i: m.filter_on[i]) if t.exit_time <= w1]
    rate = len(strat) / max(1, len(outcomes))
    p = {q: min(1.0, rate * 4) for q in {rv.quarter(t.entry_time) for t in outcomes}}
    rnd = random.Random(config.SEED)
    means = []
    for _ in range(config.RANDOM_RUNS):
        ch = rv.sequential_random(outcomes, p, rnd)[: len(strat)]
        if len(ch) >= max(5, len(strat) // 2):
            means.append(statistics.mean(t.r_net(config.COSTS["mid"]) for t in ch))
    s_mean = statistics.mean(t.r_net(config.COSTS["mid"]) for t in strat)
    return {"replayed_trades": len(strat), "strategy_mean_r": s_mean, "random_mean_r": statistics.mean(means) if means else None,
                "p_random_ge_strategy": (sum(x >= s_mean for x in means) + 1) / (len(means) + 1) if means else None, "runs": len(means)}


def main():
    fwd = os.path.join(config.FROZEN_DIR, "forward")
    with open(os.path.join(fwd, "FROZEN.json")) as f:
        fwd_start = json.load(f)["config"]["forward_start"]
    with open(os.path.join(ROOT, "reports", "protocol_design.json")) as f:
        design = json.load(f)
    rows = read_trades(fwd)
    n = len(rows)
    look = (n // LOOK) * LOOK
    out = {"evaluated_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "completed_trades": n, "look_reached": look,
               "note": "Forward ledger is a BINANCE PROXY with hypothetical 0.05% cost (R_net_mid). Trades are evaluated in recorded order."}
    if look == 0:
        out["decision"] = f"NO LOOK YET: {n} of {LOOK} trades. Progress only; nothing is evaluated before the first look."
    else:
        rs = [float(r["R_net_mid"]) for r in rows[:look]]
        s = vstats.summary(rs)
        k = look // LOOK - 1
        abs_d = next(d for d in design["absolute_designs"] if d["n_max"] == 480)
        rel_d = next(d for d in design["relative_designs"] if d["n_max"] == 480 and d["design_effect_r"] == 0.30)
        sd0 = design["inputs"]["strategy_sd_r"]
        z_abs = s["expectancy_r"] / (sd0 / math.sqrt(look))
        cp = design["checkpoint_40_trades"]["true edge = backtest all-in estimate"]
        harm_cum = sum(rs) <= cp["cumulative_r_p01"] * look / 40
        harm_dd = s["max_drawdown_r"] >= cp["max_drawdown_r_p50_p95_p99"][2] * math.sqrt(look / 40)
        out.update(summary=s, ci95=vstats.iid_bootstrap_ci(rs, config.BOOTSTRAP_RUNS, config.SEED),
                   absolute={"z": z_abs, "efficacy_z": abs_d["efficacy_z"][k], "futility_z": abs_d["futility_z"][k]},
                   harm={"cumulative_r": sum(rs), "harm_threshold_cumulative_r": cp["cumulative_r_p01"] * look / 40,
                             "max_drawdown_r": s["max_drawdown_r"], "harm_threshold_drawdown_r": cp["max_drawdown_r_p50_p95_p99"][2] * math.sqrt(look / 40),
                             "triggered": harm_cum or harm_dd})
        if "--no-benchmark" not in sys.argv:
            bm = benchmark(fwd_start, look)
            out["benchmark"] = bm
            if bm and bm["random_mean_r"] is not None:
                sd_r = design["inputs"]["random_sd_r"]
                z_rel = (s["expectancy_r"] - bm["random_mean_r"]) / (sd_r / math.sqrt(look))
                out["relative"] = {"z": z_rel, "efficacy_z": rel_d["efficacy_z"][k], "futility_z": rel_d["futility_z"][k]}
        decision = []
        if out["harm"]["triggered"]:
            decision.append("HARM BOUNDARY CROSSED: stop the paper test and treat the model as broken.")
        rel = out.get("relative")
        if rel and look >= 2 * LOOK and rel["z"] < rel["futility_z"]:
            decision.append("RELATIVE FUTILITY: the trigger is not beating random entry; reject the strategy.")
        if rel and rel["z"] >= rel["efficacy_z"]:
            decision.append("RELATIVE EFFICACY reached: the trigger beats random entry at the pre-registered level.")
        if out["absolute"]["z"] >= out["absolute"]["efficacy_z"]:
            decision.append("ABSOLUTE EFFICACY reached (Binance proxy costs). Re-check with verified Exness costs before any decision.")
        if look == LOOK:
            decision.append("40-trade checkpoint: operational review only (see PROTOCOL.md). No profitability verdict.")
        out["decision"] = " ".join(decision) or "CONTINUE: no boundary crossed."
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    with open(os.path.join(ROOT, "reports", "forward_evaluation_latest.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(out["decision"])


if __name__ == "__main__":
    main()
