"""Audit 5: robustness of the two Pivot Reversal BUY passes to the benchmark's random seed and run count, and to the
small liberal bias of seq_held measured on BTC under the null (z sd 1.056)."""
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
sys.path.insert(0, HERE)
import run_long as L  # noqa: E402
import seq_held as SH  # noqa: E402

B, S = L.B, L.S
NULL_SD = 1.056


def check(path, w0, w1, label):
    a = B.BuiltinAsset(path, crypto=True)
    tr = [t for t in a.simulate_strategy("PIVOT_REVERSAL") if t.direction == 1 and w0 <= t.entry_time < w1]
    e = statistics.mean(t.r("primary") for t in tr)
    zs = []
    for seed in (1, 2, 3, 4, 5):
        mu, sd = SH.seq_held(a, tr, w0, w1, runs=2000, seed=seed)
        zs.append((e - mu) / sd)
    z = statistics.mean(zs)
    out = {"label": label, "trades": len(tr), "expectancy_r": e, "z_by_seed": zs, "z_mean": z, "p": 0.5 * math.erfc(z / math.sqrt(2)),
           "z_bias_adjusted": z / NULL_SD, "p_bias_adjusted": 0.5 * math.erfc(z / NULL_SD / math.sqrt(2))}
    print(json.dumps(out), flush=True)
    return out


def main():
    S_ = sys.argv[1]
    res = [check(f"{S_}/long/BTCUSDm_15m.csv.gz", S.ts(2020, 7), 10 ** 10, "BTC 2020-07..now (long-history study)"),
           check(f"{S_}/multi/bars/ETHUSDm_15m.csv.gz", S.ts(2025, 1), 10 ** 10, "ETH 2025-01..now (multi-market confirmation)"),
           check(f"{S_}/multi/bars/ETHUSDm_15m.csv.gz", S.ts(2023, 7), S.ts(2025, 1), "ETH 2023-07..2024-12 (multi-market discovery)")]
    json.dump(res, open(os.path.join(os.path.dirname(HERE), "reports", "pivot_robustness.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
