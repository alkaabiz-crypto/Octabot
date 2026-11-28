"""Independent validation of the frozen Donchian 20 BUY strategy. Reads frozen code and data; writes reports/ only.

Usage: FROZEN_BTC_BREAKOUT=<frozen research/btc_breakout> python src/run_validation.py
Writes reports/validation.json. Nothing is optimised: every rule and parameter is the frozen one.
"""
import collections
import csv
import json
import math
import os
import random
import statistics
import sys
import time
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itertools

import config
import exness_lab
import frozen
import replica
import vstats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = config.COSTS[config.PRIMARY_COST]


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


def closed(trades):
    return [t for t in trades if t.reason != "data_end"]


def split(trades):
    return {name: [t for t in trades if w0 <= t.entry_time < w1] for name, w0, w1 in config.PERIODS}


def with_ci(rs, seed):
    s = vstats.summary(rs)
    if len(rs) > 1:
        s["ci95_iid"] = vstats.iid_bootstrap_ci(rs, config.BOOTSTRAP_RUNS, seed)
    return s


# ---------------------------------------------------------------------------------------------- 1. baseline
def baseline(trades, label):
    out = {}
    for name, tr in split(trades).items():
        out[name] = {c: with_ci([t.r_net(v) for t in tr], config.SEED) for c, v in config.COSTS.items()}
        out[name]["avg_hold_hours"] = statistics.mean(t.hold_hours for t in tr)
        out[name]["exit_reasons"] = dict(collections.Counter(t.reason for t in tr))
    print(label, {k: (v["mid"]["trades"], round(v["mid"]["expectancy_r"], 3), round(v["mid"]["t_stat"], 2)) for k, v in out.items()})
    return out


# ---------------------------------------------------------------------------------------------- 2. audit checks
def audit_overlap_and_timing(m, trades):
    overlaps = sum(1 for a, b in itertools.pairwise(trades) if b.entry_time < a.exit_time)
    E = m.E
    bad_entry = sum(1 for t in trades if t.entry_time != E["t"][t.signal_index] + 3600)
    not_signal = sum(1 for t in trades if not (m.sig[t.signal_index] and m.filter_on[t.signal_index]))
    return {"trades": len(trades), "overlapping_positions": overlaps, "entry_not_at_signal_close": bad_entry,
                "entries_without_valid_signal": not_signal}


def truncation_test(lab, m, trades, n_each=30, seed=config.SEED):
    """Recompute signal + 4H filter from candles truncated at the decision time; must equal the full-data value."""
    eng = frozen.engine_module()
    rnd = random.Random(seed)
    E, _H = lab.B["1h"], lab.B["4h"]
    accepted = [t.signal_index for t in trades]
    rejected = [i for i in range(300, len(E["t"])) if m.sig[i] and not m.filter_on[i]]
    other = [i for i in range(300, len(E["t"])) if not m.sig[i]]
    sample = rnd.sample(accepted, n_each) + rnd.sample(rejected, min(n_each, len(rejected))) + rnd.sample(other, n_each)
    mismatches = []
    for i in sample:
        tc = E["t"][i] + 3600
        raw1 = lab.raw["1h"][: i + 1]
        raw4 = [c for c in lab.raw["4h"] if c[0] + 14400 <= tc]
        b1, b4 = eng.build(raw1), eng.build(raw4)
        c, hh = b1["c"], b1["hh"][20]
        sig = c[-1] > hh[-1] and c[-2] <= hh[-2]
        filt = b4["c"][-1] > b4["e200"][-1]
        if sig != m.sig[i] or filt != m.filter_on[i]:
            mismatches.append(fmt(tc))
    return {"checked": len(sample), "accepted_signals": n_each, "rejected_signals": min(n_each, len(rejected)),
                "non_signal_bars": n_each, "mismatches": mismatches}


# ---------------------------------------------------------------------------------------------- 3. dependence
def months_between(w0, w1):
    out, y, mo = [], *time.gmtime(w0)[:2]
    while config.ts(y, mo) < w1:
        out.append((y, mo))
        y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
    return out


def month_groups(trades, w0, w1, cost=MID):
    groups = collections.OrderedDict((k, []) for k in months_between(w0, w1))
    for t in trades:
        g = time.gmtime(t.entry_time)
        if (g.tm_year, g.tm_mon) in groups:
            groups[(g.tm_year, g.tm_mon)].append(t.r_net(cost))
    return groups


def dependence(trades):
    out = {}
    for name, w0, w1 in config.PERIODS:
        tr = [t for t in trades if w0 <= t.entry_time < w1]
        rs = [t.r_net(MID) for t in tr]
        groups = month_groups(tr, w0, w1)
        lo, hi, means = vstats.block_bootstrap_mean_ci(list(groups.values()), config.BOOTSTRAP_RUNS, config.SEED, config.BLOCK_MONTHS)
        counts = [len(v) for v in groups.values()]
        iid = vstats.iid_bootstrap_ci(rs, config.BOOTSTRAP_RUNS, config.SEED)
        lag1 = statistics.correlation(rs[:-1], rs[1:]) if len(rs) > 3 else None
        out[name] = {"trades": len(rs), "ljung_box_10": vstats.ljung_box(rs, 10), "runs_test_wins": vstats.runs_test([r > 0 for r in rs]),
                         "lag1_correlation": lag1, "ci95_iid": iid, "ci95_block_bootstrap_months": (lo, hi),
                         "block_bootstrap_share_mean_le_0": sum(x <= 0 for x in means) / len(means),
                         "ci_width_ratio_block_vs_iid": (hi - lo) / (iid[1] - iid[0]),
                         "trades_per_month_mean": statistics.mean(counts), "trades_per_month_var": statistics.pvariance(counts),
                         "months_without_trades": sum(c == 0 for c in counts), "months": len(counts)}
    return out


# ---------------------------------------------------------------------------------------------- 4. multiple testing
def load_log(path):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        t = time.strptime(r["entry_time_utc"], "%Y-%m-%d %H:%M")
        out.append((config.ts(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour) + t.tm_min * 60,
                    float(r["R_gross"]) - MID * float(r["entry"]) / float(r["risk"])))
    return out


def reality_check():
    """White's Reality Check / Hansen-style max-t over all 48 variants of the original walk-forward."""
    log_dir = os.path.join(config.FROZEN_DIR, "logs", "walkforward")
    names = sorted(f[:-4] for f in os.listdir(log_dir) if f.endswith(".csv"))
    w0, w1 = config.DEV[1], config.DEV[2]
    months = months_between(w0, w1)
    mi = {k: i for i, k in enumerate(months)}
    series, per_trade = {}, {}
    for nm in names:
        tr = load_log(os.path.join(log_dir, nm + ".csv"))
        x = [0.0] * len(months)
        for t, r in tr:
            g = time.gmtime(t)
            x[mi[(g.tm_year, g.tm_mon)]] += r
        series[nm] = x
        rs = [r for _, r in tr]
        s = vstats.summary(rs)
        per_trade[nm] = {"trades": s["trades"], "expectancy_r": s.get("expectancy_r"), "t_stat": s.get("t_stat"), "p_one_sided": s.get("p_one_sided")}
    T = len(months)

    def tstat(x):
        m = statistics.mean(x)
        sd = statistics.stdev(x)
        return m / (sd / math.sqrt(T)) if sd > 0 else 0.0

    obs = {nm: tstat(x) for nm, x in series.items()}
    target = "1h_M2_DONCHIAN20_LONG_TRAIL"
    demeaned = {nm: [v - statistics.mean(x) for v in x] for nm, x in series.items()}
    rnd = random.Random(config.SEED)
    max_null, target_null = [], []
    for _ in range(config.BOOTSTRAP_RUNS):
        idx = vstats.stationary_bootstrap_indices(T, config.BLOCK_MONTHS, rnd)
        best = -1e9
        for nm, x in demeaned.items():
            tv = tstat([x[i] for i in idx])
            best = max(best, tv)
            if nm == target:
                target_null.append(tv)
        max_null.append(best)
    p_single = (sum(v >= obs[target] for v in target_null) + 1) / (len(target_null) + 1)
    p_family = (sum(v >= obs[target] for v in max_null) + 1) / (len(max_null) + 1)
    ranked = sorted(obs.items(), key=lambda kv: -kv[1])
    # Holm and Bonferroni on per-trade one-sided p-values
    ps = sorted((v["p_one_sided"], k) for k, v in per_trade.items() if v["p_one_sided"] is not None)
    holm, running = {}, 0.0
    for rank, (p, k) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - rank) * p))
        holm[k] = running
    return {"variants": len(names), "months": T, "target": target, "target_monthly_t": obs[target],
                "target_rank_among_variants": [k for k, _ in ranked].index(target) + 1,
                "p_block_bootstrap_single_test": p_single, "p_reality_check_family_of_48": p_family,
                "target_per_trade": per_trade[target], "target_bonferroni_p": min(1.0, per_trade[target]["p_one_sided"] * len(names)),
                "target_holm_p": holm[target], "top5_by_monthly_t": ranked[:5],
                "variants_with_per_trade_t_ge_2": sum(1 for v in per_trade.values() if (v["t_stat"] or 0) >= 2)}


# ---------------------------------------------------------------------------------------------- 5. regimes and years
def regimes_and_years(trades):
    out = {}
    for name, tr in split(trades).items():
        reg = {}
        for r in ("bull", "bear", "sideways"):
            rs = [t.r_net(MID) for t in tr if t.regime == r]
            reg[r] = with_ci(rs, config.SEED) if len(rs) > 1 else vstats.summary(rs)
        out[name] = reg
    years = {}
    for t in trades:
        years.setdefault(time.gmtime(t.entry_time).tm_year, []).append(t.r_net(MID))
    out["by_year"] = {y: vstats.summary(rs) for y, rs in sorted(years.items())}
    out["by_half_year"] = {}
    for t in trades:
        g = time.gmtime(t.entry_time)
        out["by_half_year"].setdefault(f"{g.tm_year}H{1 if g.tm_mon <= 6 else 2}", []).append(t.r_net(MID))
    out["by_half_year"] = {k: {"trades": len(v), "expectancy_r": statistics.mean(v), "total_r": sum(v)} for k, v in sorted(out["by_half_year"].items())}
    hy = list(out["by_half_year"].values())
    out["half_years_positive"] = f"{sum(h['expectancy_r'] > 0 for h in hy)} of {len(hy)}"
    return out


# ---------------------------------------------------------------------------------------------- 6. concentration
def concentration(trades, cost=MID):
    out = {}
    for name, tr in split(trades).items():
        rs = sorted((t.r_net(cost) for t in tr), reverse=True)
        total = sum(rs)
        res = {"trades": len(rs), "total_r": total, "top5_r": sum(rs[:5]), "top5_share_of_total_pct": sum(rs[:5]) / total * 100 if total > 0 else None,
                   "top5_trades_r": rs[:5], "gross_profit_r": sum(r for r in rs if r > 0)}
        res["top5_share_of_gross_profit_pct"] = sum(rs[:5]) / res["gross_profit_r"] * 100
        drops = {}
        for k in (1, 3, 5, 10, round(0.05 * len(rs)), round(0.10 * len(rs))):
            rest = rs[k:]
            s = vstats.summary(rest)
            drops[str(k)] = {"removed": k, "expectancy_r": s["expectancy_r"], "t_stat": s["t_stat"], "total_r": s["total_r"], "profit_factor": s["profit_factor"]}
        res["after_removing_top_k"] = drops
        cum, k_zero = 0.0, None
        for k in range(len(rs) + 1):
            if total - cum <= 0:
                k_zero = k
                break
            if k < len(rs):
                cum += rs[k]
        res["top_trades_whose_removal_makes_total_le_0"] = k_zero
        res["share_of_trades_needed_pct"] = k_zero / len(rs) * 100 if k_zero is not None else None
        out[name] = res
    return out


# ---------------------------------------------------------------------------------------------- 7. costs
def eu_dst(t):
    """True if EU summer time is in force at UTC time t (last Sunday of March 01:00 UTC .. last Sunday of October)."""
    y = time.gmtime(t).tm_year

    def last_sunday(month):
        d = 31
        while True:
            wd = time.gmtime(config.ts(y, month, d)).tm_wday
            if wd == 6:
                return config.ts(y, month, d, 1)
            d -= 1
    return last_sunday(3) <= t < last_sunday(10)


def rollovers(entry, exit_):
    """(number of rollovers crossed, swap-days counting Friday triple)."""
    n = days = 0
    d = entry // 86400 * 86400 - 86400
    while d <= exit_:
        for hour in (config.ROLLOVER_HOUR_SUMMER, config.ROLLOVER_HOUR_WINTER):
            r = d + hour * 3600
            if (hour == config.ROLLOVER_HOUR_SUMMER) == eu_dst(r) and entry < r <= exit_:
                n += 1
                days += 3 if time.gmtime(r).tm_wday == config.TRIPLE_SWAP_WEEKDAY else 1
        d += 86400
    return n, days


def costs(trades_binance, trades_exness, exness_lab_obj, ask):
    out = {}
    P = exness_lab_obj.B["15m"]
    pidx = exness_lab_obj.p_idx
    for name, tr in split(trades_exness).items():
        sp = []
        for t in tr:
            j = pidx[t.entry_time]
            sp.append({"spread_frac": (ask["o"][j] - P["o"][j]) / P["o"][j], "spread_r": (ask["o"][j] - P["o"][j]) / t.risk})
        rolls = [rollovers(t.entry_time, t.exit_time) for t in tr]
        swap_days = [d for _, d in rolls]
        rs = [t.r_net(0) for t in tr]
        mean_r = statistics.mean(rs)
        mean_k_days = statistics.mean(t.k * d for t, d in zip(tr, swap_days))
        res = {"trades": len(tr), "entry_spread_pct_of_price_median": statistics.median(x["spread_frac"] for x in sp) * 100,
                   "entry_spread_r_mean": statistics.mean(x["spread_r"] for x in sp),
                   "rollovers_per_trade_mean": statistics.mean(n for n, _ in rolls), "swap_days_per_trade_mean": statistics.mean(swap_days),
                   "trades_holding_over_a_rollover_pct": sum(n > 0 for n, _ in rolls) / len(rolls) * 100,
                   "expectancy_spread_only_r": mean_r,
                   "breakeven_swap_per_day_pct_of_price": mean_r / mean_k_days * 100 if mean_k_days > 0 else None}
        scen = {}
        for label, slip, swap_day, admin_usd, comm_usd_rt in (
                ("spread only", 0.0, 0.0, 0.0, 0.0),
                ("spread + 0.02% slippage", 0.0002, 0.0, 0.0, 0.0),
                ("spread + 0.05% slippage", 0.0005, 0.0, 0.0, 0.0),
                ("spread + 0.02% slip + swap 0.01%/day", 0.0002, 0.0001, 0.0, 0.0),
                ("spread + 0.02% slip + swap 0.03%/day", 0.0002, 0.0003, 0.0, 0.0),
                ("spread + 0.02% slip + admin fee 50 USD/lot/night", 0.0002, 0.0, 50.0, 0.0),
                ("spread + 0.02% slip + commission 8 USD/lot round trip", 0.0002, 0.0, 0.0, 8.0)):
            vals = []
            for t, d in zip(tr, swap_days):
                frac = slip + swap_day * d + (admin_usd * d + comm_usd_rt) / t.entry
                vals.append(t.r_gross - frac * t.k)
            s = vstats.summary(vals)
            scen[label] = {"expectancy_r": s["expectancy_r"], "t_stat": s["t_stat"], "profit_factor": s["profit_factor"], "win_rate_pct": s["win_rate_pct"]}
        res["scenarios"] = scen
        out[name] = res
    # spread history by year at all hours (context)
    years = {}
    for j in range(0, len(P["t"]), 4):
        years.setdefault(time.gmtime(P["t"][j]).tm_year, []).append((ask["o"][j] - P["o"][j]) / P["o"][j] * 100)
    out["exness_spread_pct_by_year_median"] = {y: statistics.median(v) for y, v in sorted(years.items())}
    # Binance trades with the Exness spread observed at the same moment (half at entry + half at exit)
    out["binance_trades_with_exness_spread"] = {}
    for name, tr in split(trades_binance).items():
        vals = []
        for t in tr:
            je, jx = pidx.get(t.entry_time), pidx.get(t.exit_time - 900)
            if je is None or jx is None:
                continue
            se = (ask["o"][je] - P["o"][je]) / P["o"][je]
            sx = (ask["c"][jx] - P["c"][jx]) / P["c"][jx]
            vals.append(t.r_gross - (se / 2 + sx / 2 + 0.0002) * t.k)
        s = vstats.summary(vals)
        out["binance_trades_with_exness_spread"][name] = {"trades": s["trades"], "expectancy_r": s["expectancy_r"], "t_stat": s["t_stat"]}
    return out


# ---------------------------------------------------------------------------------------------- 8. execution
def execution(m_bin, m_exn):
    out = {}
    for label, m, cost in (("binance (mid cost)", m_bin, MID), ("exness bid/ask + 0.02% slippage", m_exn, 0.0002)):
        res = {}
        for delay in config.DELAYS_15M:
            for slip in config.STOP_SLIPPAGE:
                tr = closed(m.run(config.ALL[1], 10 ** 11, delay=delay, stop_slip=slip))
                per = {}
                for name, ptr in split(tr).items():
                    s = vstats.summary([t.r_net(cost) for t in ptr])
                    per[name] = {"trades": s["trades"], "expectancy_r": s["expectancy_r"], "t_stat": s["t_stat"]}
                res[f"delay {delay * 15} min, stop slippage {slip * 100:.2f}%"] = per
        out[label] = res
    stops = [t for t in closed(m_bin.run(config.ALL[1], 10 ** 11)) if t.reason == "stop"]
    gap_fills = sum(1 for t in stops if t.r_gross < -1.0 - 1e-9)   # only a gap through the stop can lose more than 1R
    out["stop_exits"] = len(stops)
    out["initial_stop_gap_fills_worse_than_minus_1R"] = gap_fills
    return out


# ---------------------------------------------------------------------------------------------- 9. random benchmark
def quarter(t):
    g = time.gmtime(t)
    return (g.tm_year, (g.tm_mon - 1) // 3)


def outcome_list(m, w0, w1, eligible):
    """Every eligible 1H close in [w0, w1) with the trade the frozen exit rule would produce from it, in time order."""
    out = []
    for i in range(len(m.E["t"])):
        tc = m.E["t"][i] + 3600
        if w0 <= tc < w1 and eligible(i):
            tr = m.simulate_from(i)
            if tr is not None and tr.reason != "data_end":
                out.append(tr)
    return out


def sequential_random(outcomes, p, rnd):
    """Walk forward in time. When flat, enter at an eligible hour with probability p[quarter]; then hold to exit.

    This is the same one-position rule the strategy follows. (A shuffle-then-reject-overlaps sampler is
    length-biased: long trades, which are the big winners, overlap more often and get rejected.)
    """
    chosen, busy_until = [], -1
    for t in outcomes:
        if t.entry_time < busy_until:
            continue
        if rnd.random() < p[quarter(t.entry_time)]:
            chosen.append(t)
            busy_until = t.exit_time
    return chosen


def pct(sorted_values, x):
    return sorted_values[int(x * (len(sorted_values) - 1))]


def random_benchmark(m, trades, label, eligible, runs=config.RANDOM_RUNS, seed=config.SEED):
    """Random entries with the same filter state, exit rule, costs, one-position rule and trades per quarter."""
    w0, w1 = config.ALL[1], config.ALL[2]
    tr_all = [t for t in trades if w0 <= t.entry_time < w1]
    target = collections.Counter(quarter(t.entry_time) for t in tr_all)
    outcomes = outcome_list(m, w0, w1, eligible)
    per_q = collections.Counter(quarter(t.entry_time) for t in outcomes)
    p = {q: min(1.0, target.get(q, 0) / per_q[q] * 4) for q in per_q}
    rnd = random.Random(seed + zlib.crc32(label.encode()))
    for _ in range(6):   # calibrate entry probabilities so expected trades per quarter match the strategy
        counts = collections.Counter()
        for _ in range(100):
            counts.update(quarter(t.entry_time) for t in sequential_random(outcomes, p, rnd))
        for q in list(p):
            got = counts[q] / 100
            want = target.get(q, 0)
            p[q] = 0.0 if want == 0 else min(1.0, p[q] * (want / got if got > 0 else 4))
    runs_out = [sequential_random(outcomes, p, rnd) for _ in range(runs)]
    res = {"eligible": label, "runs": runs, "eligible_hours": len(outcomes),
               "unconditional_mean_r_all_eligible_hours": statistics.mean(t.r_net(MID) for t in outcomes)}
    periods = {}
    for name, a, b in config.PERIODS:
        srs = [t.r_net(MID) for t in tr_all if a <= t.entry_time < b]
        s_mean = statistics.mean(srs)
        means, counts, wins, expo, bull, top5_wo = [], [], [], [], [], []
        for ch in runs_out:
            rr = [t for t in ch if a <= t.entry_time < b]
            if not rr:
                continue
            rs = sorted((t.r_net(MID) for t in rr), reverse=True)
            means.append(sum(rs) / len(rs))
            counts.append(len(rs))
            wins.append(sum(r > 0 for r in rs) / len(rs))
            expo.append(sum(t.hold_hours for t in rr))
            bull.append(sum(t.regime == "bull" for t in rr) / len(rr))
            top5_wo.append(sum(rs[5:]) / max(1, len(rs) - 5))
        ms = sorted(means)
        s_sorted = sorted(srs, reverse=True)
        periods[name] = {"strategy_trades": len(srs), "random_trades_mean": statistics.mean(counts), "strategy_expectancy_r": s_mean,
                             "random_expectancy_mean_r": statistics.mean(ms), "random_expectancy_p05_p50_p95": (pct(ms, 0.05), pct(ms, 0.5), pct(ms, 0.95)),
                             "excess_expectancy_r": s_mean - statistics.mean(ms),
                             "p_random_ge_strategy": (sum(x >= s_mean for x in ms) + 1) / (len(ms) + 1),
                             "strategy_win_rate_pct": sum(r > 0 for r in srs) / len(srs) * 100, "random_win_rate_mean_pct": statistics.mean(wins) * 100,
                             "strategy_exposure_hours": sum(t.hold_hours for t in tr_all if a <= t.entry_time < b),
                             "random_exposure_hours_mean": statistics.mean(expo),
                             "strategy_bull_share": sum(t.regime == "bull" for t in tr_all if a <= t.entry_time < b) / len(srs),
                             "random_bull_share_mean": statistics.mean(bull),
                             "strategy_expectancy_without_top5_r": sum(s_sorted[5:]) / (len(s_sorted) - 5),
                             "random_expectancy_without_top5_mean_r": statistics.mean(top5_wo)}
    res["periods"] = periods
    years = {}
    for y in sorted({time.gmtime(t.entry_time).tm_year for t in tr_all}):
        a, b = config.ts(y, 1), config.ts(y + 1, 1)
        srs = [t.r_net(MID) for t in tr_all if a <= t.entry_time < b]
        ms = []
        for ch in runs_out:
            rr = [t.r_net(MID) for t in ch if a <= t.entry_time < b]
            if rr:
                ms.append(sum(rr) / len(rr))
        years[y] = {"strategy_trades": len(srs), "strategy_expectancy_r": statistics.mean(srs), "random_expectancy_mean_r": statistics.mean(ms),
                        "excess_r": statistics.mean(srs) - statistics.mean(ms),
                        "p_random_ge_strategy": (sum(x >= statistics.mean(srs) for x in ms) + 1) / (len(ms) + 1)}
    res["by_year"] = years
    return res


def main():
    t0 = time.time()
    lab = frozen.lab()
    m_bin = replica.Market(lab)
    trades_bin = closed(m_bin.run(config.ALL[1], 10 ** 11))
    exl, ask = exness_lab.build_lab()
    m_exn = replica.Market(exl, exec_open=ask["o"])
    trades_exn = closed(m_exn.run(config.ALL[1], 10 ** 11))
    R = {"meta": {"frozen_commit": config.FROZEN_COMMIT, "freeze_commit": config.FREEZE_COMMIT, "generated_utc": fmt(time.time()),
                       "binance_last_bar": fmt(lab.B["15m"]["t"][-1]), "exness_last_bar": fmt(exl.B["15m"]["t"][-1]),
                       "note": "Binance = frozen research data. Exness = BTCUSDm bid/ask quotes, same frozen rules."}}
    R["baseline_binance"] = baseline(trades_bin, "binance")
    R["baseline_exness_spread_only"] = baseline(trades_exn, "exness")
    R["audit_overlap_timing_binance"] = audit_overlap_and_timing(m_bin, trades_bin)
    R["audit_overlap_timing_exness"] = audit_overlap_and_timing(m_exn, trades_exn)
    sys.path.insert(0, os.path.join(config.FROZEN_DIR, "src"))
    import protocol as fp  # frozen
    windowed = []
    for _, w0, w1 in fp.WINDOWS:
        windowed += lab.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", w0, w1)
    R["audit_original_windowed_run"] = {"trades": len(windowed), "forced_window_end_exits": sum(t["exit"] == "window_end" for t in windowed),
                                            "expectancy_mid": statistics.mean(t["R_gross"] - MID * t["k"] for t in windowed)}
    print("truncation test ...", flush=True)
    R["audit_truncation_binance"] = truncation_test(lab, m_bin, trades_bin)
    print("dependence ...", flush=True)
    R["dependence_binance"] = dependence(trades_bin)
    print("reality check ...", flush=True)
    R["multiple_testing"] = reality_check()
    R["regimes_binance"] = regimes_and_years(trades_bin)
    R["regimes_exness"] = regimes_and_years(trades_exn)
    R["concentration_binance_mid"] = concentration(trades_bin)
    R["concentration_exness_spread_slip"] = concentration(trades_exn, 0.0002)
    print("costs ...", flush=True)
    R["costs"] = costs(trades_bin, trades_exn, exl, ask)
    print("execution ...", flush=True)
    R["execution"] = execution(m_bin, m_exn)
    print("random benchmark ...", flush=True)
    R["random_benchmark"] = []
    for m, tr, label, elig in ((m_bin, trades_bin, "BINANCE, 4H filter on (same exposure as strategy)", lambda i: m_bin.filter_on[i]),
                               (m_bin, trades_bin, "BINANCE, any hour (no filter)", lambda i: True),
                               (m_exn, trades_exn, "EXNESS bid/ask, 4H filter on", lambda i: m_exn.filter_on[i])):
        t1 = time.time()
        res = random_benchmark(m, tr, label, elig)
        R["random_benchmark"].append(res)
        for name, v in res["periods"].items():
            print(" ", label[:30], name[:12], round(v["strategy_expectancy_r"], 3), round(v["random_expectancy_mean_r"], 3),
                  round(v["random_trades_mean"], 1), v["strategy_trades"], round(v["p_random_ge_strategy"], 4), flush=True)
        print(f"  ({time.time() - t1:.0f}s)", flush=True)
    with open(os.path.join(ROOT, "reports", "validation.json"), "w") as f:
        json.dump(R, f, indent=1, default=str)
    # per-trade ledgers for transparency
    for label, tr in (("binance", trades_bin), ("exness", trades_exn)):
        with open(os.path.join(ROOT, "reports", f"trades_{label}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["entry_utc", "exit_utc", "entry", "risk", "r_gross", "r_net_mid", "exit_reason", "regime", "hold_hours"])
            for t in tr:
                w.writerow([fmt(t.entry_time), fmt(t.exit_time), round(t.entry, 2), round(t.risk, 4), round(t.r_gross, 6), round(t.r_net(MID), 6),
                            t.reason, t.regime, round(t.hold_hours, 2)])
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
