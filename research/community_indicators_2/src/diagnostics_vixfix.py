"""POST-HOC checks of the one round-2 pass (Williams Vix Fix BUY, trailing exit, BTC). Not part of the pass rule.

Added after the result was seen. The rule is applied unchanged to data never used to select it:
  1. BTC 2020-01 to 2024-12 (Binance research data, frozen branch);
  2. ETH 2020-01 to now (Binance, from research/rsi_vwap_study).
Binance prices have no broker spread, so a 0.05% round-trip cost is applied instead of the Exness spread.
Also reports, on the Exness BTC test itself: stress cost, top-5 concentration, regimes and a 15-minute entry delay.
Writes reports/diagnostics_vixfix.json.
"""
import csv
import gzip
import json
import os
import statistics
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import community2 as C
import oil
import study as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESEARCH = os.path.dirname(ROOT)
FROZEN = os.environ.get("FROZEN_BTC_BREAKOUT", "")


def binance_to_csv(rows):
    """Write Binance [t,o,h,l,c,v] 15m candles in the bid/ask format, with ask = bid (no broker spread)."""
    path = os.path.join(tempfile.mkdtemp(), "q.csv.gz")
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "bo", "bh", "bl", "bc", "ao", "ah", "al", "ac", "ticks"])
        for t, o, h, l, c, _ in rows:
            w.writerow([int(t), o, h, l, c, o, h, l, c, 1])
    return path


def evaluate(a, w0, w1, label):
    sig = a.c2_signals("VIX_FIX", 1)
    tr = a.run_signals(sig, 1, "TRAIL", w0, w1)
    rs = [t.r("primary") for t in tr]
    s = S.summary(rs)
    b = S.random_benchmark(a, tr, 1, "TRAIL", w0, w1, runs=1000)
    s.update(random_mean_r=b["random_mean_r"], p_random=b["p_random"], label=label)
    years = {}
    for t in tr:
        years.setdefault(S.fmt(t.entry_time)[:4], []).append(t.r("primary"))
    s["by_year"] = {y: {"trades": len(v), "expectancy_r": statistics.mean(v)} for y, v in sorted(years.items())}
    print(label, s["trades"], round(s["expectancy_r"], 3), "t", round(s["t_stat"], 2), "random", round(b["random_mean_r"], 3), "p", round(b["p_random"], 3),
          {y: (v["trades"], round(v["expectancy_r"], 2)) for y, v in s["by_year"].items()}, flush=True)
    return s, tr


def main():
    out = {}
    # 1-2. untouched data, 0.05% cost on spread-free Binance prices
    oil.SLIP["primary"] = 0.0005
    with open(os.path.join(FROZEN, "data", "btc_15m.json")) as f:
        btc = C.Community2Asset(binance_to_csv(json.load(f)))
    out["btc_binance_2020_2024"], _ = evaluate(btc, S.ts(2020, 1), S.ts(2025, 1), "BTC Binance 2020-2024")
    with gzip.open(os.path.join(RESEARCH, "rsi_vwap_study", "data", "ethusdt_15m.json.gz"), "rt") as f:
        eth = C.Community2Asset(binance_to_csv(json.load(f)))
    out["eth_binance_2020_now"], _ = evaluate(eth, S.ts(2020, 1), S.ts(2026, 12), "ETH Binance 2020-now")
    # 3. robustness on the Exness BTC result itself (real spread + 0.02% slippage)
    oil.SLIP["primary"] = 0.0002
    ex = C.Community2Asset(os.path.join(RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz"))
    s, tr = evaluate(ex, S.ts(2025, 1), ex.e.t[-1] + 3600, "BTC Exness 2025-now")
    s["stress_expectancy_r"] = statistics.mean(t.r("stress") for t in tr)
    reg = {}
    for t in tr:
        reg.setdefault(t.regime, []).append(t.r("primary"))
    s["regimes"] = {k: {"trades": len(v), "expectancy_r": statistics.mean(v)} for k, v in reg.items()}
    delayed = [ex.simulate(t.signal_index, 1, "TRAIL", delay=1) for t in tr]
    s["delay_15min_expectancy_r"] = statistics.mean(d.r("primary") for d in delayed if d is not None)
    out["btc_exness_2025_now"] = s
    print("stress", round(s["stress_expectancy_r"], 3), "top5 share", s["top5_share_of_total_pct"] and round(s["top5_share_of_total_pct"]),
          "without top5", round(s["expectancy_without_top5_r"], 3), "delay", round(s["delay_15min_expectancy_r"], 3),
          {k: (v["trades"], round(v["expectancy_r"], 2)) for k, v in s["regimes"].items()})
    with open(os.path.join(ROOT, "reports", "diagnostics_vixfix.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
