"""Pre-registered untouched-data check (PROTOCOL.md): every variant that passed both 2025 and 2026 is re-run, unchanged,
on data no stage of this research selected on:
  * US oil: Exness USOILm ticks 2019-02 to 2024-12 (primary cost: real spread + 0.02%);
  * gold:   Exness XAUUSDm ticks 2020-01 to 2023-12 (same cost);
  * BTC:    Binance BTCUSDT 2020-01 to 2024-12 (no spread in the data, so 0.05% per round trip).
A variant is VALIDATED only with expectancy > 0 and p_random <= 0.05 there. Writes reports/untouched.json.
"""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builtin_strategies as B  # noqa: E402
import builtin_indicators as I  # noqa: E402
import oil  # noqa: E402
import run_everything as R  # noqa: E402
import run_scan  # noqa: E402
import study as S  # noqa: E402

SP = os.environ.get("UNTOUCHED_DIR", "")
FROZEN = os.environ.get("FROZEN_BTC_BREAKOUT", "")


def btc_path():
    sys.path.insert(0, os.path.join(B.RESEARCH, "community_indicators_2", "src"))
    import diagnostics_vixfix as DV
    with open(os.path.join(FROZEN, "data", "btc_15m.json")) as f:
        return DV.binance_to_csv(json.load(f))


DATA = {"USOILm": (lambda: os.path.join(SP, "USOILm_2019_2024_15m.csv.gz"), False, (2019, 2), (2025, 1), 0.0002),
        "XAUUSDm": (lambda: os.path.join(SP, "XAUUSDm_2020_2023_15m.csv.gz"), False, (2020, 1), (2024, 1), 0.0002),
        "BTCUSDm": (btc_path, True, (2020, 1), (2025, 1), 0.0005)}


def variant_result(a, key, w0, w1, sig, flt, cache):
    part, name, dn, ex = key.split("|")
    d = 1 if dn == "BUY" else -1
    fname = None
    if part == "D":
        name, fname = name.split("+")
        part = "C" if name in B.CHARTART else ("A" if name in B.NAMES else "B")
    ok = flt[fname][0 if d > 0 else 1] if fname else None
    if part in ("A", "C"):
        if name not in cache:
            cache[name] = a.simulate_strategy(name)
        legs = [t for t in cache[name] if t.direction == d and w0 <= t.entry_time < w1 and (ok is None or ok[t.signal_index])]
        return R.eval_held(a, legs, w0, w1)
    buy, sell = sig[name]
    mine, other = (buy, sell) if d > 0 else (sell, buy)
    if ok is not None:
        mine = [m and f for m, f in zip(mine, ok)]
    if ex == "FLIP":
        return R.eval_held(a, R.flip_legs(a, mine, other, d, w0, w1), w0, w1)
    return run_scan.evaluate(a, a.run_signals(mine, d, ex, w0, w1), d, ex, w0, w1)


def main():
    out = {}
    for mkt, (path_fn, crypto, y0, y1, slip) in DATA.items():
        res = json.load(open(os.path.join(B.ROOT, "reports", f"results_{mkt}.json")))["results"]
        keys = [k for k, r in res.items() if r["reliable"]]
        out[mkt] = {}
        if not keys:
            continue
        oil.SLIP["primary"] = slip
        a = B.BuiltinAsset(path_fn(), crypto=crypto)
        sig, flt, cache = I.signals(a.e), R.filters(a), {}
        w0, w1 = S.ts(*y0, 1), S.ts(*y1, 1)
        for k in keys:
            r = variant_result(a, k, w0, w1, sig, flt, cache)
            r["validated"] = r["trades"] >= 30 and r.get("expectancy_r", -1) > 0 and r.get("p_random", 1) <= 0.05
            out[mkt][k] = r
            print(mkt, k, r["trades"], round(r.get("win_rate_pct", 0), 1), round(r.get("expectancy_r", 0), 3),
                  round(r.get("p_random", 1), 3), "VALIDATED" if r["validated"] else "", flush=True)
    oil.SLIP["primary"] = 0.0002
    with open(os.path.join(B.ROOT, "reports", "untouched.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
