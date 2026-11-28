"""POST-HOC diagnostics for the one variant that passed (V1 VWAP momentum, BUY, TRAIL). Not part of the pass rule.

Added after the results were seen, to judge how fragile the pass is:
  1. how independent the ETH replication is from BTC (timing overlap, correlation of monthly results);
  2. execution realism on BTC: the measured Exness BTCUSDm spread at each entry, and a 15-minute entry delay;
  3. swap break-even, using the rollover rule from research/donchian_validation (imported read-only);
  4. the program-wide multiple-testing picture and the forward sample size needed.
Writes reports/diagnostics.json.
"""
import csv
import glob
import gzip
import json
import math
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_study
import study as S

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "donchian_validation", "src"))
import run_validation as dv

ROOT = os.path.dirname(HERE)
KEY = ("V1_VWAP_MOMENTUM", 1, "TRAIL")
W0, W1 = S.ts(2020, 1), S.ts(2026, 11, 9)


def monthly(trades):
    out = {}
    for t in trades:
        g = time.gmtime(t.entry_time)
        out.setdefault((g.tm_year, g.tm_mon), []).append(t.r("primary"))
    return {k: sum(v) for k, v in out.items()}


def exness_spreads():
    bars = os.path.join(os.environ["FROZEN_BTC_BREAKOUT"], "..", "exness_validation", "data", "bars15m")
    sp = {}
    for path in sorted(glob.glob(os.path.join(bars, "BTCUSDm_*.csv.gz"))):
        with gzip.open(path, "rt") as f:
            for r in csv.DictReader(f):
                sp[int(r["open_time_utc"])] = (float(r["ask_o"]) - float(r["bid_o"]), float(r["ask_c"]) - float(r["bid_c"]))
    return sp


def main():
    assets = run_study.load_assets()
    btc, eth = assets["BTCUSDT"], assets["ETHUSDT"]
    tb = btc.run(*KEY, W0, W1)
    te = eth.run(*KEY, W0, W1)
    out = {}
    # 1. independence of the replication
    hours_b = {t.entry_time for t in tb}
    within_2h = sum(1 for t in te if any(abs(t.entry_time - x) <= 7200 for x in (t.entry_time - 3600, t.entry_time, t.entry_time + 3600) if x in hours_b))
    mb, me = monthly(tb), monthly(te)
    keys = sorted(set(mb) & set(me))
    out["replication_independence"] = {
        "eth_trades": len(te), "eth_entries_within_1h_of_a_btc_entry_pct": within_2h / len(te) * 100,
        "monthly_result_correlation": statistics.correlation([mb[k] for k in keys], [me[k] for k in keys]), "months": len(keys)}
    # 2. execution: Exness spread at entry and exit (half each, as Binance prices are near the mid), and 15m delay
    sp = exness_spreads()
    vals = []
    for t in tb:
        e, x = sp.get(t.entry_time), sp.get(t.exit_time - 900)
        if e and x:
            vals.append((t, (e[0] / 2 + x[1] / 2) / t.risk))
    years = {}
    for t, c in vals:
        years.setdefault(time.gmtime(t.entry_time).tm_year, []).append(c)
    out["exness_spread"] = {"trades_matched": len(vals), "mean_spread_cost_r": statistics.mean(c for _, c in vals),
                                "by_year_mean_r": {y: statistics.mean(v) for y, v in sorted(years.items())},
                                "expectancy_exness_spread_plus_0_02pct_r": statistics.mean(t.r_gross - c - 0.0002 * t.entry / t.risk for t, c in vals),
                                "expectancy_2024_on_exness_spread_plus_0_02pct_r": statistics.mean(
                                    t.r_gross - c - 0.0002 * t.entry / t.risk for t, c in vals if t.entry_time >= S.ts(2024, 1))}
    delayed = [btc.simulate(t.signal_index, 1, "TRAIL", delay=1) for t in tb]
    delayed = [d for d in delayed if d is not None]
    out["delay_15min"] = {"trades": len(delayed), "expectancy_primary_r": statistics.mean(d.r("primary") for d in delayed),
                              "expectancy_no_delay_r": statistics.mean(t.r("primary") for t in tb)}
    # 3. swap break-even
    days = [dv.rollovers(t.entry_time, t.exit_time)[1] for t in tb]
    mean_r = statistics.mean(t.r("primary") for t in tb)
    out["swap"] = {"swap_days_per_trade": statistics.mean(days), "trades_over_a_rollover_pct": sum(d > 0 for d in days) / len(days) * 100,
                       "breakeven_swap_per_day_pct_of_price": mean_r / statistics.mean(t.entry / t.risk * d for t, d in zip(tb, days)) * 100}
    # 4. multiplicity and forward sample size
    p_raw = S.summary([t.r("primary") for t in tb])["p_one_sided"]
    sd = statistics.stdev(t.r("primary") for t in tb)
    per_year = len(tb) / ((W1 - W0) / (365.25 * 86400))
    excess = 0.063

    def n_needed(effect):
        return math.ceil(((2.0 + 0.84) * sd / effect) ** 2)
    out["multiplicity_and_sample_size"] = {
        "p_one_sided_btc": p_raw, "tests_in_this_study": 8,
        "tests_in_research_program_at_least": 48 + 24 + 8,
        "bonferroni_over_program": min(1.0, p_raw * 80),
        "trades_per_year": per_year, "sd_r": sd,
        "forward_trades_needed_absolute_0_167R": n_needed(0.167), "years_absolute": n_needed(0.167) / per_year,
        "forward_trades_needed_relative_0_063R": n_needed(excess), "years_relative": n_needed(excess) / per_year}
    with open(os.path.join(ROOT, "reports", "diagnostics.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
