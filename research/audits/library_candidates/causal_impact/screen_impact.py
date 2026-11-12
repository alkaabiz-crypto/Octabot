"""Screen-level impact of the order-selection look-ahead on every affected theory/market/timeframe (scratch only).
FROZEN = the frozen screen functions, unchanged.  CAUSAL = the same signal, order, fill and exit code (engine.manage, frozen) with
the forward test's selection: several pending orders, at each candle the oldest pending order that fills is taken, the rest
cancelled; no new signal while a position is open; after an exit, the next signal is the candle after the exit candle.
Both are scored with engine.evaluate and engine.random_control (frozen) and run.py's verdict rule and seeds.
Also re-runs VERIFY_PREREG V2 (verify_neighbours.py's frozen 9-setting grids) under causal selection.
usage: python3 -I screen_impact.py <extract_dir> <bars_dir> <out_json>
"""
import json, os, sys, zlib
import numpy as np

EXT, BARS, OUT = sys.argv[1:4]; os.environ["BARS_DIR"] = BARS
sys.path.insert(0, os.path.join(EXT, "research", "theory_library"))
import engine as E, theories as T, theories_f as TF, verify_neighbours as VN, run as RUN  # noqa: E401,E402
from engine import Book, manage, sma  # noqa: E402
from theories import C  # noqa: E402
from theories_f import fractals  # noqa: E402


def causal_limit(m, tf, signal, life, start, stop_i):
    """Generic causal driver for limit-entry theories. signal(i) -> (side, lim, stop, tp) or None (decided at close of i)."""
    c = C(m, tf); bk = Book(c); o, h, l = c.o.values, c.h.values, c.l.values; pend = []; k = start
    while k < len(c):
        took = False
        pend = [p for p in pend if k <= p[0] + life]
        for (i0, side, lim, st, tp) in pend:                     # oldest first
            if (side > 0 and l[k] <= lim) or (side < 0 and h[k] >= lim):
                pe = min(o[k], lim) if side > 0 else max(o[k], lim); x, px = manage(c, k, side, st, tp, tmax=20, intrabar=True)
                bk.add(k, x, side, pe, px); pend = []; k = x + 1; took = True; break
        if took:
            if k < stop_i(c): s = signal(c, k)
            else: break
            if s: pend.append((k,) + s)
            k += 1; continue
        if k < stop_i(c):
            s = signal(c, k)
            if s: pend.append((k,) + s)
        k += 1
    return c, bk


def sig_b9(fib=0.618, look=20):
    cache = {}
    def f(c, i):
        if id(c) not in cache: cache[id(c)] = sma(c.c, 50).values
        s50 = cache[id(c)]; h, l, cl = c.h.values, c.l.values, c.c.values
        if i < 50: return None
        hh, ll = h[i - look + 1:i + 1], l[i - look + 1:i + 1]; ih, il = int(np.argmax(hh)), int(np.argmin(ll)); H, L = hh[ih], ll[il]
        side = 1 if (cl[i] > s50[i] and ih > il) else (-1 if (cl[i] < s50[i] and il > ih) else 0)
        if side == 0 or H <= L: return None
        lim = H - fib * (H - L) if side > 0 else L + fib * (H - L); st, tp = (L, H) if side > 0 else (H, L); return side, lim, st, tp
    return f


def sig_d4(rr=2.0):
    def f(c, i):
        h, l = c.h.values, c.l.values
        if i < 2: return None
        side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
        if not side: return None
        lim = h[i - 2] if side > 0 else l[i - 2]; st = l[i - 2] if side > 0 else h[i - 2]; R = side * (lim - st)
        if R <= 0: return None
        return side, lim, st, lim + side * rr * R
    return f


def b9_causal(m, tf, fib=0.618, look=20): return causal_limit(m, tf, sig_b9(fib, look), 10, 50, lambda c: len(c) - 2)
def d4_causal(m, tf, valid=10, rr=2.0): return causal_limit(m, tf, sig_d4(rr), valid, 2, lambda c: len(c) - 1)


def stop_break_causal(m, tf, setup, valid):
    """Causal stop_break: every setup's bracket stays pending for `valid` candles; at each candle the oldest pending bracket that
    triggers is taken (a bracket whose both sides trade in the same candle is cancelled, exactly as the frozen rule skips it)."""
    c = C(m, tf); bk = Book(c); o, h, l = c.o.values, c.h.values, c.l.values; pend = []; k = 8
    while k < len(c):
        pend = [p for p in pend if k <= p[0] + valid]; took = False; keep = []
        for idx, (i0, hi, lo) in enumerate(pend):
            up, dn = h[k] >= hi, l[k] <= lo
            if up and dn: continue                                     # ambiguous candle: this setup is skipped (frozen rule)
            if up or dn:
                side = 1 if up else -1; lvl = hi if up else lo; pe = max(o[k], lvl) if up else min(o[k], lvl); st = lo if up else hi; R = hi - lo
                x, px = manage(c, k, side, st, pe + side * 2 * R, tmax=20, intrabar=True); bk.add(k, x, side, pe, px); took = True; break
            keep.append((i0, hi, lo))
        if took:
            pend = []; k = x + 1
            if k >= len(c) - 1: break
            lv = setup(h, l, k)
            if lv: pend.append((k,) + tuple(lv))
            k += 1; continue
        pend = keep
        if k < len(c) - 1:
            lv = setup(h, l, k)
            if lv: pend.append((k,) + tuple(lv))
        k += 1
    return c, bk


def c3_causal(m, tf): return stop_break_causal(m, tf, lambda h, l, i: (h[i - 1], l[i - 1]) if (h[i] < h[i - 1] and l[i] > l[i - 1]) else None, 5)
def c4_causal(m, tf): return stop_break_causal(m, tf, lambda h, l, i: (h[i], l[i]) if (h[i] - l[i]) <= (h[i - 6:i + 1] - l[i - 6:i + 1]).min() else None, 3)


def f9_causal(m, tf):
    """F9 with its fractal state machine unchanged; its 20-candle limit orders are kept pending (oldest fill first)."""
    c = C(m, tf); o, h, l, x = c.o.values, c.h.values, c.l.values, c.c.values; sh, sl = fractals(h, l); bk = Book(c); lh = ll = None; i = 4; pend = []
    while i < len(c) - 1:
        pend = [p for p in pend if i <= p[0] + 20]; took = False
        for (i0, side, lim, stop) in pend:
            if (side > 0 and l[i] <= lim) or (side < 0 and h[i] >= lim):
                R = side * (lim - stop); pe = min(o[i], lim) if side > 0 else max(o[i], lim); e, px = manage(c, i, side, stop, lim + side * 2 * R, tmax=20, intrabar=True)
                bk.add(i, e, side, pe, px); took = True; break
        if took: pend = []; i = e + 1; continue
        if sh[i - 2]: lh = i - 2
        if sl[i - 2]: ll = i - 2
        trade = None
        if lh is not None and x[i] > h[lh] and x[i - 1] <= h[lh]:
            k = next((q for q in range(i - 1, max(lh, i - 20), -1) if x[q] < o[q]), None)
            if k is not None: trade = (1, h[k], l[k]); lh = None
        elif ll is not None and x[i] < l[ll] and x[i - 1] >= l[ll]:
            k = next((q for q in range(i - 1, max(ll, i - 20), -1) if x[q] > o[q]), None)
            if k is not None: trade = (-1, l[k], h[k]); ll = None
        if trade and trade[0] * (trade[1] - trade[2]) > 0: pend.append((i,) + trade)
        i += 1
    return c, bk


PAIRS = {"B9": (T.b9, b9_causal, ["1h"]), "D4": (T.d4_fvg, d4_causal, ["1h"]), "C3": (T.c3, c3_causal, ["1h", "1d"]),
         "C4": (T.c4, c4_causal, ["1d"]), "F9": (TF.f9, f9_causal, ["1h"])}
MKTS = E.EXNESS + E.CRYPTO


def screen(key, c, bk):
    r1, _ = E.evaluate(c, bk, 1); r2, meta = E.evaluate(c, bk, 2)
    rng = np.random.default_rng(RUN.SEED + zlib.crc32(key.encode()) % 100000)
    rc = E.random_control(c, meta, 2, RUN.DRAWS, rng) if len(meta) else {"dev": None, "holdout": None}
    d, h = RUN.summ(r2["dev"]), RUN.summ(r2["holdout"])
    p95 = {p: (round(float(v[1] * 1e4), 2) if v is not None else None) for p, v in rc.items()}
    ok = (d["mean_bp"] is not None and h["mean_bp"] is not None and d["mean_bp"] > 0 and h["mean_bp"] > 0 and h["trades"] >= 30
          and p95["dev"] is not None and p95["holdout"] is not None and d["mean_bp"] > p95["dev"] and h["mean_bp"] > p95["holdout"])
    sd = lambda r: round(float(r.mean() / (r.std(ddof=1) / np.sqrt(len(r)))), 2) if len(r) > 2 else None
    return dict(dev=d, holdout=h, random_p95=p95, verdict="PASS" if ok else "FAIL", t_dev=sd(r2["dev"]), t_holdout=sd(r2["holdout"]))


def main():
    frozen_ref = json.load(open(os.path.join(EXT, "research", "theory_library", "results", "results.json")))["results"]
    out = {"screen": {}, "neighbours": {}}
    for tid, (ff, fc, tfs) in PAIRS.items():
        for mkt in MKTS:
            for tf in tfs:
                key = f"{tid}|{mkt}|{tf}"
                if E.candles(mkt, tf) is None: continue
                cf, bf = ff(mkt, tf); cc, bc = fc(mkt, tf)
                a, b = screen(key, cf, bf), screen(key, cc, bc); ref = frozen_ref.get(key, {})
                repro = ref.get("x2") == {"dev": a["dev"], "holdout": a["holdout"]} and ref.get("verdict") == a["verdict"]
                same = len({(r[0], r[2]) for r in bf.rows} & {(r[0], r[2]) for r in bc.rows})
                out["screen"][key] = dict(frozen=a, causal=b, frozen_reproduced=repro, frozen_trades=len(bf.rows), causal_trades=len(bc.rows), identical_entries=same)
                print(key, "repro" if repro else "NOT-REPRO", "| frozen", a["dev"]["mean_bp"], a["holdout"]["mean_bp"], a["verdict"],
                      "| causal", b["dev"]["mean_bp"], b["holdout"]["mean_bp"], b["verdict"], f"| same {same}/{len(bf.rows)}", flush=True)
    # V2 neighbours under causal selection (verify_neighbours.py's frozen grids and candidates)
    for tid, mkt, tf in VN.CANDIDATES:
        if tid not in ("B9", "D4"): continue
        fn_f, grid = VN.GRID[tid]; fn_c = b9_causal if tid == "B9" else d4_causal; rows = []
        for p in grid:
            for lab, fn in (("frozen", fn_f), ("causal", fn_c)):
                c, bk = fn(mkt, tf, **p); r, _ = E.evaluate(c, bk, 2)
                rows.append(dict(params=p, engine=lab, dev_bp=round(float(r["dev"].mean() * 1e4), 2), hold_bp=round(float(r["holdout"].mean() * 1e4), 2)))
        fz = [r for r in rows if r["engine"] == "frozen"]; ca = [r for r in rows if r["engine"] == "causal"]
        out["neighbours"][f"{tid}|{mkt}|{tf}"] = dict(rows=rows, frozen_holdout_positive=f"{sum(r['hold_bp'] > 0 for r in fz)}/9",
                                                    causal_holdout_positive=f"{sum(r['hold_bp'] > 0 for r in ca)}/9",
                                                    causal_both_periods_positive=f"{sum(r['hold_bp'] > 0 and r['dev_bp'] > 0 for r in ca)}/9")
        print("V2", tid, mkt, out["neighbours"][f"{tid}|{mkt}|{tf}"]["frozen_holdout_positive"], "->", out["neighbours"][f"{tid}|{mkt}|{tf}"]["causal_holdout_positive"], flush=True)
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
