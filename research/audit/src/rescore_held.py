"""Audit fix 1: re-score every held-leg variant (strategies' own exits, hold-to-opposite-signal, 4-bar hold) of the
long-history and multi-market studies with the calibrated sequential benchmark (seq_held). Trades, expectancy and
everything else are recomputed exactly as the original run; only the benchmark changes.
usage: LONG_DATA=.. MULTI_DATA=.. python src/rescore_held.py long|multi <market> <outdir>"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
sys.path.insert(0, os.path.join(RESEARCH, "multi_market", "src"))
sys.path.insert(0, HERE)
import run_long as L  # noqa: E402
import run_multi as M  # noqa: E402
import seq_held as SH  # noqa: E402

B, I, R, S = L.B, L.I, L.R, L.S


def score(a, trades, w0, w1):
    rs = [t.r("primary") for t in trades]
    if len(rs) < 30:
        return {"trades": len(rs)}
    e = sum(rs) / len(rs)
    mu, sd = SH.seq_held(a, trades, w0, w1, runs=500)
    z = (e - mu) / sd if sd > 0 else 0.0
    return {"trades": len(rs), "expectancy_r": e, "random_mean_r": mu, "z": z, "p_z": 0.5 * math.erfc(z / math.sqrt(2))}


def main():
    study, mkt, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    t0 = time.time()
    if study == "long":
        a = B.BuiltinAsset(os.path.join(os.environ["LONG_DATA"], f"{mkt}_15m.csv.gz"), crypto=L.CRYPTO[mkt])
        wins = {"all": (S.ts(*L.START[mkt], 1), a.e.t[-1] + 3600)}
    else:
        a = B.BuiltinAsset(M.path_of(mkt), crypto=M.MARKET_CLASS[mkt] == "crypto")
        end = a.e.t[-1] + 3600
        wins = {k: (S.ts(*v0, 1), S.ts(*v1, 1) if v1 else end) for k, (v0, v1) in M.WINDOWS.items()}
    sig_ind, flt = I.signals(a.e), R.filters(a)
    strat, out = {}, {}
    for (part, name, d, ex) in L.variants(a, sig_ind):
        if part in ("B", "O") and ex not in ("FLIP", "NATIVE"):
            continue                                   # standard exits: benchmark already calibrated
        for fname in (None,) + R.FILTERS:
            ok = flt[fname][0 if d > 0 else 1] if fname else None
            key = f"{part}|{name}{'+' + fname if fname else ''}|{'BUY' if d > 0 else 'SELL'}|{ex}"
            res = {}
            for wname, (w0, w1) in wins.items():
                if part in ("A", "C"):
                    if name not in strat:
                        strat[name] = a.simulate_strategy(name)
                    trades = [t for t in strat[name] if t.direction == d and w0 <= t.entry_time < w1 and (ok is None or ok[t.signal_index])]
                else:
                    buy, sell = (sig_ind if part == "B" else a.sig)[name]
                    mine, other = (buy, sell) if d > 0 else (sell, buy)
                    if ok is not None:
                        mine = [m and f for m, f in zip(mine, ok)]
                    trades = R.flip_legs(a, mine, other, d, w0, w1) if ex == "FLIP" else a.run_signals(mine, d, "NATIVE", w0, w1)
                res[wname] = score(a, trades, w0, w1)
            out[key] = res
    os.makedirs(outdir, exist_ok=True)
    json.dump({"meta": {"study": study, "market": mkt, "seconds": round(time.time() - t0)}, "results": out},
              open(os.path.join(outdir, f"{study}_{mkt}.json"), "w"))
    print(study, mkt, len(out), round(time.time() - t0), "s", flush=True)


if __name__ == "__main__":
    main()
