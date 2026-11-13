"""Gate tests for src/causal_orders.py. Run: python3 -I tests/test_causal_orders.py   (exit code 1 on any failure)
1. State-machine cases (crafted, signals injected): newer-fills-first, oldest-wins tie, expiry, gap fill, fill-minute stop, one position.
2. Prefix invariance: replacing all prices after a cut never changes any decision taken before the cut (random walks, both clocks).
3. Negative control: a deliberately look-ahead selection (simulate_lookahead) DOES fail prefix invariance, so the test has power."""
import os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import causal_orders as S  # noqa: E402

T0 = 1736121600 // 60; PEN = lambda px, q: px * 1e-4; fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name, detail); (None if ok else fails.append(name))


def flat(hours, px=100.0):
    n = hours * 60; m = T0 + np.arange(n); o = np.full(n, px); return m, o.copy(), o.copy(), o.copy(), o.copy()


def poke(a, q, lo=None, hi=None, op=None):
    m, o, h, l, c = a
    if op is not None: o[q] = op
    if lo is not None: l[q] = min(l[q], lo)
    if hi is not None: h[q] = max(h[q], hi)
    h[q] = max(h[q], o[q], c[q]); l[q] = min(l[q], o[q], c[q])


def run(a, sigs):
    tr, _ = S.simulate(*a, "fvg", PEN, clock="wall", sigfun=lambda Hc, k: sigs.get(k))
    return [(t["side"], int(t["ft"] - T0), round(t["entry"], 4), t["reason"]) for t in tr]


def crafted():
    a = flat(30); poke(a, 370, lo=99.4); poke(a, 485, lo=97.9)
    check("newer order fills first -> newer taken", run(a, {2: (1, 98.0, 96.0, 102.0), 4: (1, 99.5, 96.0, 103.0)}) == [(1, 370, 99.5, "time")])
    a = flat(30); poke(a, 361, lo=98.9)
    check("same-minute fills -> oldest wins", run(a, {2: (1, 99.0, 96.0, 102.0), 3: (1, 99.6, 96.0, 103.0)}) == [(1, 361, 99.0, "time")])
    a = flat(40); poke(a, 780, lo=97.95); poke(a, 930, lo=96.9)
    check("expired order never fills", run(a, {2: (1, 98.0, 90.0, 120.0), 8: (1, 97.0, 90.0, 120.0)}) == [(1, 930, 97.0, "time")])
    a = flat(30); poke(a, 307, op=98.2, lo=98.1)
    check("gap through limit fills at open", run(a, {2: (1, 99.0, 90.0, 120.0)}) == [(1, 307, 98.2, "time")])
    a = flat(30); poke(a, 307, lo=98.4, hi=99.9)
    check("fill-minute stop beats target", run(a, {2: (1, 99.0, 98.5, 99.5)}) == [(1, 307, 99.0, "stop")])
    a = flat(40); poke(a, 210, lo=98.9); poke(a, 315, hi=101.2); poke(a, 440, lo=98.8)
    sig = {2: (1, 99.0, 98.0, 101.0), 3: (1, 98.5, 97.0, 101.0), 5: (1, 99.0, 98.0, 101.0), 6: (1, 99.0, 98.0, 101.0)}
    check("one position; next check exit hour + 2 h", run(a, sig) == [(1, 210, 99.0, "target"), (1, 440, 99.0, "time")])


def walk(seed, days=12):
    r = np.random.default_rng(seed); n = days * 1440; c = 100 * np.exp(np.cumsum(r.normal(0, 6e-4, n) + np.repeat(r.normal(0, 1e-4, n // 600 + 1), 600)[:n]))
    o = np.r_[100.0, c[:-1]]; w = np.abs(r.normal(0, 6e-4, (2, n))); return T0 + np.arange(n), o, np.maximum(o, c) * np.exp(w[0]), np.minimum(o, c) * np.exp(-w[1]), c


def prefix(fn, seeds=range(1, 13)):
    bad = tot = 0
    for sd in seeds:
        m, o, h, l, c = walk(sd); m2, o2, h2, l2, c2 = walk(sd + 777)
        for kind in ("fib", "fvg"):
            for frac in (0.4, 0.7):
                q0 = int(len(m) * frac) + 17; s = o[q0] / o2[q0]
                b = [np.r_[x[:q0], y[q0:] * s] for x, y in ((o, o2), (h, h2), (l, l2), (c, c2))]; T = int(m[q0 - 1])
                A, B = fn(m, o, h, l, c, kind), fn(m, *b, kind)
                key = lambda tr: [(x["side"], int(m[x["f"]]), round(x["entry"], 6)) for x in tr if m[x["f"]] <= T] + [(int(m[x["x"]]), round(x["exit"], 6)) for x in tr if m[x["x"]] <= T]
                tot += 1; bad += key(A) != key(B)
    return bad, tot


if __name__ == "__main__":
    crafted()
    for clock in ("wall", "candle"):
        b, t = prefix(lambda m, o, h, l, c, k, cl=clock: S.simulate(m, o, h, l, c, k, PEN, clock=cl, fib_need=51)[0])
        check(f"prefix invariance, {clock} clock", b == 0, f"{b}/{t} cuts changed past decisions")
    b, t = prefix(lambda m, o, h, l, c, k: S.simulate_lookahead(m, o, h, l, c, k, PEN)[0], seeds=range(1, 41))
    check("negative control: look-ahead selection is detected", b > 0, f"{b}/{t} cuts changed past decisions")
    print("FAILED:" if fails else "ALL PASSED", fails); sys.exit(1 if fails else 0)
