"""Full-history test of every variant (PROTOCOL.md). usage: LONG_DATA=dir python run_long.py
Writes reports/raw_<market>_<chunk>.json; src/report.py applies the pass rule."""
import bisect
import json
import math
import multiprocessing
import os
import random
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "tradingview_builtins", "src"))
sys.path.insert(0, HERE)
import builtin_strategies as B  # noqa: E402  (sets up all research paths)
import builtin_indicators as I  # noqa: E402
import run_everything as R  # noqa: E402
import study as S  # noqa: E402
import fast_bench as FB  # noqa: E402

DATA = os.environ.get("LONG_DATA", "")
START = {"USOILm": (2019, 7), "XAUUSDm": (2020, 7), "BTCUSDm": (2020, 7)}
CRYPTO = {"USOILm": False, "XAUUSDm": False, "BTCUSDm": True}
RUNS = 200
CHUNKS = 2
FLIP_ORIGINALS = {"UT_BOT", "SSL_CHANNEL", "CHANDELIER_EXIT", "HALFTREND", "SUPERTREND_KIVANC", "RANGE_FILTER", "CORAL_TREND", "QQE_MOD"}


def held_benchmark(a, trades, w0, w1, runs=RUNS, seed=20261111):
    E = a.e
    by_q = {}
    for i, t in enumerate(E.t):
        if w0 <= t + 3600 < w1:
            by_q.setdefault(S.quarter(t + 3600), []).append(i)
    rnd, means = random.Random(seed), []
    for _ in range(runs):
        vals = []
        for tr in trades:
            pool = by_q.get(S.quarter(tr.entry_time))
            for _a in range(20):
                rt = a.hold(rnd.choice(pool), tr.direction, tr.exit_time - tr.entry_time)
                if rt is not None:
                    vals.append(rt.r("primary"))
                    break
        if vals:
            means.append(statistics.mean(vals))
    return statistics.mean(means), statistics.pstdev(means)


def summarise(a, trades, kind, d, ex, w0, w1, mid):
    rs = [t.r("primary") for t in trades]
    out = {"trades": len(rs)}
    if len(rs) < 30:
        return out
    out.update(win_rate_pct=100 * sum(r > 0 for r in rs) / len(rs), expectancy_r=statistics.mean(rs),
               expectancy_stress_r=statistics.mean(t.r("stress") for t in trades))
    if kind == "standard":
        mu, sd, out["random_win_rate_pct"] = FB.standard(a, trades, d, ex, w0, w1, runs=RUNS)
    else:
        mu, sd = FB.held(a, trades, w0, w1, runs=RUNS)
    z = (out["expectancy_r"] - mu) / sd if sd > 0 else 0.0
    out.update(random_mean_r=mu, z=z, p_z=0.5 * math.erfc(z / math.sqrt(2)))
    years = {}
    for t in trades:
        years.setdefault(S.fmt(t.entry_time)[:4], []).append(t.r("primary"))
    out["years"] = {y: [len(v), statistics.mean(v)] for y, v in sorted(years.items())}
    h1 = [t.r("primary") for t in trades if t.entry_time < mid]
    h2 = [t.r("primary") for t in trades if t.entry_time >= mid]
    out["halves"] = [statistics.mean(h1) if h1 else None, statistics.mean(h2) if h2 else None]
    return out


def variants(a, sig_ind):
    """(key, part, name, d, exit, source) for every single variant, without filters."""
    out = []
    for name in B.NAMES + B.CHARTART:
        for d in (1, -1):
            out.append(("C" if name in B.CHARTART else "A", name, d, "OWN"))
    for part, sigs, flips in (("B", sig_ind, {k for k, (b, s) in sig_ind.items() if I.alternates(b, s)}), ("O", a.sig, FLIP_ORIGINALS)):
        for name in sigs:
            exits = list(R.STANDARD) + (["FLIP"] if name in flips else []) + (["NATIVE"] if name == "LORENTZIAN_V6" else [])
            for d in (1, -1):
                out += [(part, name, d, ex) for ex in exits]
    return out


def run(task):
    mkt, chunk = task
    t0 = time.time()
    a = B.BuiltinAsset(os.path.join(DATA, f"{mkt}_15m.csv.gz"), crypto=CRYPTO[mkt])
    w0, w1 = S.ts(*START[mkt], 1), a.e.t[-1] + 3600
    mid = (w0 + w1) // 2
    sig_ind, flt = I.signals(a.e), R.filters(a)
    jobs = [(v, f) for v in variants(a, sig_ind) for f in (None,) + R.FILTERS]
    jobs = jobs[chunk::CHUNKS]
    strat = {}
    out = {}
    log = open(os.path.join(ROOT, "reports", f"progress_{mkt}_{chunk}.log"), "w")
    for (part, name, d, ex), fname in jobs:
        ok = flt[fname][0 if d > 0 else 1] if fname else None
        if part in ("A", "C"):
            if name not in strat:
                strat[name] = a.simulate_strategy(name)
            trades = [t for t in strat[name] if t.direction == d and w0 <= t.entry_time < w1 and (ok is None or ok[t.signal_index])]
            kind = "held"
        else:
            buy, sell = (sig_ind if part == "B" else a.sig)[name]
            mine, other = (buy, sell) if d > 0 else (sell, buy)
            if ok is not None:
                mine = [m and f for m, f in zip(mine, ok)]
            if ex == "FLIP":
                trades, kind = R.flip_legs(a, mine, other, d, w0, w1), "held"
            elif ex == "NATIVE":
                trades, kind = a.run_signals(mine, d, "NATIVE", w0, w1), "held"
            else:
                trades, kind = a.run_signals(mine, d, ex, w0, w1), "standard"
        key = f"{part}|{name}{'+' + fname if fname else ''}|{'BUY' if d > 0 else 'SELL'}|{ex}"
        res = summarise(a, trades, kind, d, ex, w0, w1, mid)
        out[key] = res
        log.write(f"{key:60} n={res['trades']:>5} win={res.get('win_rate_pct', 0):5.1f} E={res.get('expectancy_r', 0):+.3f} "
                  f"z={res.get('z', 0):+.2f} [{time.time() - t0:.0f}s]\n")
        log.flush()
    with open(os.path.join(ROOT, "reports", f"raw_{mkt}_{chunk}.json"), "w") as f:
        json.dump({"meta": {"market": mkt, "chunk": chunk, "test_start": w0, "test_end": w1, "runs": RUNS,
                            "seconds": round(time.time() - t0)}, "results": out}, f)
    return task


def main():
    tasks = [(m, c) for m in ("USOILm", "XAUUSDm", "BTCUSDm") for c in range(CHUNKS)]
    if len(sys.argv) > 1:
        tasks = [t for t in tasks if t[0] in sys.argv[1:]]
    with multiprocessing.Pool(4) as pool:
        for t in pool.imap_unordered(run, tasks):
            print("finished", t, flush=True)


if __name__ == "__main__":
    main()
