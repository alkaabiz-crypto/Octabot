"""Correctness check of the three frozen library candidates (information only; no theory, parameter or selection change).

Found 2026-11-12: the backtest (theories.py) and the minute-level verification (verify_minute.py) handle overlapping limit
orders sequentially: signal i's order is searched over its whole 10-candle life before signal i+1 is considered. If order i
fills at candle i+8 while order i+1 would have filled at i+3, the historical code takes the LATER fill, which uses future
information. The forward test (library_forward/forward.py, FORWARD_RULES.md) is chronological: every signal while flat places
an order; the first order to fill in time wins (oldest on a tie); the others are cancelled.

Precisely: when order i expires unfilled, the historical code steps back to signal i+1 and takes fills from candles that
had already passed, knowing order i never filled - a non-causal choice.
This script re-runs verify_minute.py's exact data, signals, fills, exits and costs, changing ONLY the order handling, under
two causal rules: (a) the forward test's chronological rule, (b) one pending order at a time (signals ignored while pending). Usage:
  BARS_DIR=<exness 1m npz> BIN_DIR=<binance 1m npz> python3 -I order_overlap.py
"""
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "theory_library"))
import verify_minute as V  # noqa: E402  (frozen; imported, not modified)


def manage(M, Hc, f, side, stop, tp, pe, tmax_hours=20):
    """Identical to the management part of V.run_limit, starting from fill minute f."""
    fill_hour = np.searchsorted(Hc["s"], f, side="right") - 1; last_k = min(fill_hour + tmax_hours, len(Hc["s"]) - 1); end = Hc["e"][last_k]
    for q in range(f, end):
        if q > f and ((side > 0 and M["o"][q] <= stop) or (side < 0 and M["o"][q] >= stop)): return q, M["o"][q]
        if (side > 0 and M["l"][q] <= stop) or (side < 0 and M["h"][q] >= stop): return q, stop
        if q > f and ((side > 0 and M["h"][q] >= tp + M["pen"][q]) or (side < 0 and M["l"][q] <= tp - M["pen"][q])): return q, tp
    return end - 1, M["c"][end - 1]


def sig_b9(Hc, s50, i, fib=0.618, look=20):
    h, l, c = Hc["h"], Hc["l"], Hc["c"]
    if i < 50: return None
    hh, ll = h[i - look + 1:i + 1], l[i - look + 1:i + 1]; ih, il = int(np.argmax(hh)), int(np.argmin(ll)); Hh, Ll = hh[ih], ll[il]
    side = 1 if (c[i] > s50[i] and ih > il) else (-1 if (c[i] < s50[i] and il > ih) else 0)
    if side == 0 or Hh <= Ll: return None
    lim = Hh - fib * (Hh - Ll) if side > 0 else Ll + fib * (Hh - Ll); stop, tp = (Ll, Hh) if side > 0 else (Hh, Ll)
    return side, lim, stop, tp


def sig_d4(Hc, s50, i):
    h, l = Hc["h"], Hc["l"]
    if i < 2: return None
    side = 1 if l[i] > h[i - 2] else (-1 if h[i] < l[i - 2] else 0)
    if not side: return None
    lim = h[i - 2] if side > 0 else l[i - 2]; stop = l[i - 2] if side > 0 else h[i - 2]; R = side * (lim - stop)
    return (side, lim, stop, lim + side * 2 * R) if R > 0 else None


def chrono(M, Hc, sig):
    """Forward-test order handling. pending: (made_i, side, lim, stop, tp); active over candles made_i+1 .. made_i+10."""
    n = len(Hc["s"]); s50 = V.sma(Hc["c"], 50); out = []; pending = []; k = 0; next_sig = 0
    while k < n - 1:
        if k >= next_sig:                                         # signal at the close of candle k (flat)
            g = sig(Hc, s50, k)
            if g: pending.append((k,) + g)
        k += 1                                                    # minutes of candle k
        pending = [p for p in pending if k <= p[0] + 10]
        if not pending: continue
        a, b = Hc["s"][k], Hc["e"][k]; best = None
        for p in pending:                                         # oldest first; strict < keeps the oldest on a tie
            _, side, lim, stop, tp = p; lo, hi, pen = M["l"][a:b], M["h"][a:b], M["pen"][a:b]
            hit = np.flatnonzero(lo <= lim - pen) if side > 0 else np.flatnonzero(hi >= lim + pen)
            if len(hit) and (best is None or a + hit[0] < best[0]): best = (a + hit[0], p)
        if best is None: continue
        f, (_, side, lim, stop, tp) = best; pe = min(M["o"][f], lim) if side > 0 else max(M["o"][f], lim)
        x, px = manage(M, Hc, f, side, stop, tp, pe); out.append((side, f, x, pe, px)); pending = []
        xk = int(np.searchsorted(Hc["s"], x, side="right") - 1); next_sig = xk + 1; k = xk + 1
    return out


def single(M, Hc, sig):
    """Alternative causal rule: one pending order at a time; signals are ignored while it is pending; after it expires
    unfilled (end of candle i+10) the next signal check is the close of candle i+10."""
    n = len(Hc["s"]); s50 = V.sma(Hc["c"], 50); out = []; i = 0
    while i < n - 2:
        g = sig(Hc, s50, i)
        if not g: i += 1; continue
        side, lim, stop, tp = g; r = V.run_limit(M, Hc, i + 1, i + 11, side, lim, stop, tp, 20)
        if r is None: i += 10; continue                          # expired: next check at the close of candle i+10
        out.append((side,) + r); i = int(np.searchsorted(Hc["s"], r[1], side="right") - 1) + 1
    return out


def ci(M, trades, mult):
    r = {"dev": [], "holdout": []}
    for side, f, x, pe, px in trades:
        r["holdout" if M["m"][f] * 60000 >= V.HOLD_MS else "dev"].append(side * (px - pe) / pe - mult * (M["hs"][f] + M["hs"][x]) / pe)
    out = {}
    for p, v in r.items():
        v = np.array(v); se = v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else np.nan
        out[p] = dict(trades=len(v), mean_bp=round(float(v.mean() * 1e4), 2) if len(v) else None,
                      ci95_bp=[round(float((v.mean() - 1.96 * se) * 1e4), 2), round(float((v.mean() + 1.96 * se) * 1e4), 2)] if len(v) > 1 else None,
                      t=round(float(v.mean() / se), 2) if len(v) > 1 and se > 0 else None, win=round(float((v > 0).mean()), 3) if len(v) else None)
    return out


def main():
    out = {}
    for tid, mkt, seq, sig in (("OIL_FIB", "USOILm", V.b9, sig_b9), ("ETH_FIB", "ETHUSDT", V.b9, sig_b9), ("GOLD_FVG", "XAUUSDm", V.d4, sig_d4)):
        M, Hc = V.load(mkt); a = seq(M, Hc); b = chrono(M, Hc, sig); c1 = single(M, Hc, sig)
        same = len(set((x[1], x[2]) for x in a) & set((x[1], x[2]) for x in b))
        out[tid] = dict(market=mkt, sequential_historical=dict(x1=ci(M, a, 1), x2=ci(M, a, 2)), chronological_forward=dict(x1=ci(M, b, 1), x2=ci(M, b, 2)),
                        one_order_at_a_time=dict(x1=ci(M, c1, 1), x2=ci(M, c1, 2)),
                        identical_trades=same, trades_sequential=len(a), trades_chronological=len(b))
        print(tid, json.dumps(out[tid]["sequential_historical"]["x2"]), "->", json.dumps(out[tid]["chronological_forward"]["x2"]), f"identical {same}/{len(a)}", "| one-at-a-time:", json.dumps(out[tid]["one_order_at_a_time"]["x2"]), flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "order_overlap.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
