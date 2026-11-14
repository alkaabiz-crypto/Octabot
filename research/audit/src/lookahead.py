"""Audit 1: look-ahead test of the whole pipeline. The 15-minute file is cut at random points and every signal
(62 built-in indicators, community indicators) and every closed strategy trade (26 built-in + ChartArt
strategies) known by the cut must be identical to the full-data run.
usage: python src/lookahead.py <15m csv.gz> <workdir> [crypto]"""
import gzip
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(RESEARCH, "tradingview_builtins", "src"))
import builtin_strategies as B  # noqa: E402
import builtin_indicators as I  # noqa: E402
import study as S  # noqa: E402

KEEP_FROM = None


def write_cut(src, dst, t0, t1):
    with gzip.open(src, "rt") as f, gzip.open(dst, "wt") as g:
        hdr = f.readline()
        g.write(hdr)
        for line in f:
            t = int(line.split(",", 1)[0])
            if t0 <= t < t1:
                g.write(line)


def trade_key(t):
    return (t.signal_index_time, t.entry_time, t.exit_time, t.direction, round(t.r_gross, 9))


def run(path, crypto):
    a = B.BuiltinAsset(path, crypto=crypto)
    sig = I.signals(a.e)
    trades = {}
    for nm in B.NAMES + B.CHARTART:
        trades[nm] = [(a.e.t[t.signal_index], t.entry_time, t.exit_time, t.direction, round(t.r_gross, 9))
                      for t in a.simulate_strategy(nm)]
    return a, sig, trades


def main():
    src, work = sys.argv[1], sys.argv[2]
    crypto = len(sys.argv) > 3
    os.makedirs(work, exist_ok=True)
    with gzip.open(src, "rt") as f:
        f.readline()
        ts = [int(l.split(",", 1)[0]) for l in f]
    t0 = ts[max(0, len(ts) - 40000)]                     # last ~40,000 15-minute bars (about 14 months)
    base = os.path.join(work, "base.csv.gz")
    write_cut(src, base, t0, ts[-1] + 1)
    A, SIG, TR = run(base, crypto)
    rnd = random.Random(11)
    cuts = sorted(rnd.sample(range(len(A.e.t) // 2, len(A.e.t) - 50), 3))
    problems = {}
    for ci in cuts:
        tcut = A.e.t[ci] + 3600                          # data ends at the close of hourly bar ci
        p = os.path.join(work, f"cut_{ci}.csv.gz")
        write_cut(base, p, t0, tcut)
        a, sig, tr = run(p, crypto)
        k = len(a.e.t)
        assert a.e.t == A.e.t[:k], "bars differ"
        for nm, (b, s) in sig.items():
            fb, fs = SIG[nm]
            diff = [i for i in range(k) if b[i] != fb[i] or s[i] != fs[i]]
            if diff:
                problems.setdefault(f"indicator {nm}", []).append(f"cut at bar {k}: {len(diff)} bars differ, last {k - diff[-1]} bar(s) before the cut, first {k - diff[0]}")
        for nm, (b, s) in a.sig.items():
            fb, fs = A.sig[nm]
            diff = [i for i in range(k) if b[i] != fb[i] or s[i] != fs[i]]
            if diff:
                problems.setdefault(f"community {nm}", []).append(f"cut at bar {k}: {len(diff)} bars differ, last {k - diff[-1]} bar(s) before the cut, first {k - diff[0]}")
        for nm, lst in tr.items():
            full = set(TR[nm])
            closed = [x for x in lst if x[2] < tcut - 3600]    # trades that closed well before the cut
            miss = [x for x in closed if x not in full]
            if miss:
                problems.setdefault(f"strategy {nm}", []).append(f"cut at bar {k}: {len(miss)} of {len(closed)} closed trades differ")
        os.remove(p)
    out = {"market": os.path.basename(src), "hourly_bars": len(A.e.t), "cuts": cuts, "indicators": len(SIG),
           "community": len(A.sig), "strategies": len(TR), "problems": problems, "generated_utc": S.fmt(time.time())}
    json.dump(out, open(os.path.join(os.path.dirname(HERE), "reports", f"lookahead_{os.path.basename(src).split('_')[0]}.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
