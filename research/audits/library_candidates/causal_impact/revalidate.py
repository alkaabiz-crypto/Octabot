"""Frozen vs causal revalidation of ETH_FIB (B9 ETHUSDT), OIL_FIB (B9 USOILm), GOLD_FVG (D4 XAUUSDm). Scratch only.
Engines:  FROZEN        verify_minute.b9/d4 imported unchanged, data loaded by verify_minute.load unchanged
          SIM_LOOKAHEAD the frozen selection re-expressed in sim.py (must equal FROZEN)
          CAUSAL_CANDLE sim.py, candle clock: identical to FROZEN except order selection  (the minimal correction)
          CAUSAL_WALL   sim.py, wall clock: the forward state machine, with the backtest's per-minute costs
          FORWARD_COSTS sim.py, wall clock, forward.py's own fill and cost rules (fixed spread / fee on prices)
          FORWARD_PY    (ETH only) the frozen forward.py replayed unchanged
usage: python3 -I revalidate.py <extract_dir> <bars_dir> <bin_dir> <forward_copy_dir> <out_json>
"""
import json, os, sys, time
import numpy as np

EXT, BARS, BIN, FWDDIR, OUT = sys.argv[1:6]
os.environ["BARS_DIR"], os.environ["BIN_DIR"] = BARS, BIN
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import sim as S  # noqa: E402
sys.path.insert(0, os.path.join(EXT, "research", "theory_library")); import verify_minute as V  # noqa: E402
HOLD = 1767225600000 // 60000                       # 2026-01-01 00:00 UTC (frozen split)
COMMON_LAST = int(np.datetime64("2026-11-09T23:00", "m").astype(np.int64)) + 60   # ETH common cutoff: exit before 2026-11-10 00:00
FROZEN_REF = {"ETHUSDT": {"2025": (326, 32.28), "2026": (288, 19.62)}, "USOILm": {"2025": (211, 12.87), "2026": (178, 17.30)},
              "XAUUSDm": {"2025": (388, 4.78), "2026": (311, 10.97)}}            # results/verify_minute.json / candidate_stats.json, 2x


def nw_t(x, L=5):
    n = len(x); d = x - x.mean(); g0 = (d @ d) / n; v = g0 + 2 * sum((1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n for j in range(1, L + 1))
    return float(x.mean() / np.sqrt(v / n))


def stat_boot(x, B=4000, p=0.2, seed=1):
    """Stationary bootstrap (Politis-Romano), mean block length 1/p = 5 trades, vectorised over resamples."""
    r = np.random.default_rng(seed); n = len(x); idx = np.empty((B, n), int); idx[:, 0] = r.integers(n, size=B)
    for k in range(1, n):
        reset = r.random(B) < p; idx[:, k] = np.where(reset, r.integers(n, size=B), (idx[:, k - 1] + 1) % n)
    return np.percentile(x[idx].mean(axis=1), [2.5, 97.5])


def summarise(r2, r1, held_min, total_min, cost2):
    if not len(r2): return dict(trades=0)
    eq = np.cumprod(1 + r2); dd = float((eq / np.maximum.accumulate(eq) - 1).min()); pos, neg = r2[r2 > 0].sum(), -r2[r2 < 0].sum()
    lo, hi = stat_boot(r2) if len(r2) >= 20 else (np.nan, np.nan)
    se = r2.std(ddof=1) / np.sqrt(len(r2))
    return dict(trades=int(len(r2)), mean_bp_1x=round(float(r1.mean() * 1e4), 2), mean_bp_2x=round(float(r2.mean() * 1e4), 2), median_bp_2x=round(float(np.median(r2) * 1e4), 2),
                win_rate_2x=round(float((r2 > 0).mean()), 3), profit_factor_2x=round(float(pos / neg), 3) if neg > 0 else None, sum_pct_2x=round(float(r2.sum() * 100), 2),
                compounded_pct_2x=round(float((eq[-1] - 1) * 100), 2), max_dd_pct_2x_trade_close=round(dd * 100, 2), cost_bp_per_trade_2x=round(float(cost2.mean() * 1e4), 2),
                exposure_pct_of_data_minutes=round(100 * held_min / total_min, 1), t_iid=round(float(r2.mean() / se), 2), t_newey_west5=round(nw_t(r2), 2),
                ci95_t_bp=[round(float((r2.mean() - 1.96 * se) * 1e4), 1), round(float((r2.mean() + 1.96 * se) * 1e4), 1)],
                ci95_stationary_bootstrap_bp=[round(float(lo * 1e4), 1), round(float(hi * 1e4), 1)], sd_bp=round(float(r2.std(ddof=1) * 1e4), 1))


def score(M, trades, cost):
    """trades: list of (side, f, x, entry, exit). cost='bt' -> verify_minute's score() formula; else a callable(entry, exit, f, x)->cost fraction at 1x."""
    side = np.array([t[0] for t in trades]); f = np.array([t[1] for t in trades], int); x = np.array([t[2] for t in trades], int)
    pe = np.array([t[3] for t in trades]); px = np.array([t[4] for t in trades]); g = side * (px - pe) / pe
    c1 = (M["hs"][f] + M["hs"][x]) / pe if cost == "bt" else np.array([cost(a, b) for a, b in zip(pe, px)])
    return g - c1, g - 2 * c1, 2 * c1, f, x


def periods(M, trades, cost, common=False):
    if not trades: return {}
    r1, r2, c2, f, x = score(M, trades, cost); fm = M["m"][f]; out = {}
    sel = {"2025": fm < HOLD, "2026": fm >= HOLD, "full": np.ones(len(f), bool)}
    if common: sel["2026_common_cutoff"] = (fm >= HOLD) & (M["m"][x] < COMMON_LAST)
    for p, s in sel.items():
        lo, hi = (M["m"][0], HOLD) if p == "2025" else ((HOLD, M["m"][-1] + 1) if p.startswith("2026") else (M["m"][0], M["m"][-1] + 1))
        tot = int(((M["m"] >= lo) & (M["m"] < hi)).sum()); held = int((x[s] - f[s] + 1).sum())
        out[p] = summarise(r2[s], r1[s], held, tot, c2[s])
    return out


def as_tuples(tr):
    return [(t["side"], t["f"], t["x"], t["entry"], t["exit"]) for t in tr]


def gap_stops(M, tr_wall_log):
    """Weekday 1m gaps > 90 min while an order or position was active (forward.py would STOP there)."""
    return tr_wall_log


def run(mkt, kind):
    t0 = time.time(); M, Hc = V.load(mkt); m, o, h, l, c = M["m"], M["o"], M["h"], M["l"], M["c"]
    eth = mkt == "ETHUSDT"; pen_bt = lambda px, q: M["pen"][q]
    res = {"data": dict(first=str(np.datetime64(int(m[0]), "m")), last=str(np.datetime64(int(m[-1]), "m")), minutes=int(len(m)), hours=int(len(Hc["s"])))}
    fz = V.b9(M, Hc) if kind == "fib" else V.d4(M, Hc)
    FZ = [(s, f, x, pe, px) for s, f, x, pe, px in fz]
    la, _ = S.simulate_lookahead(m, o, h, l, c, kind, pen_bt)
    cc, _ = S.simulate(m, o, h, l, c, kind, pen_bt, clock="candle", fib_need=51)
    log = []; cw, _ = S.simulate(m, o, h, l, c, kind, pen_bt, clock="wall", log=log)
    if eth: pen_f, cost_f = (lambda px, q: px * 1e-4), (lambda a, b: 0.0005 * (a + b) / a)
    else:
        sp = 0.22 if mkt == "XAUUSDm" else 0.02; pen_f, cost_f = (lambda px, q: sp), (lambda a, b, sp=sp: sp / a)
    fwc, _ = S.simulate(m, o, h, l, c, kind, pen_f, clock="wall")
    res["lookahead_equals_frozen"] = as_tuples(la) == [(a, b, cx, float(d), float(e)) for a, b, cx, d, e in FZ]
    res["FROZEN"] = periods(M, FZ, "bt", eth); res["CAUSAL_CANDLE"] = periods(M, as_tuples(cc), "bt", eth)
    res["CAUSAL_WALL"] = periods(M, as_tuples(cw), "bt", eth); res["FORWARD_COSTS"] = periods(M, as_tuples(fwc), cost_f, eth)
    # how many frozen trades survive unchanged under causal selection, and why the others differ
    fset = {(t[0], t[1]) for t in FZ}; cset = {(t["side"], t["f"]) for t in cc}
    res["overlap"] = dict(frozen_trades=len(FZ), causal_candle_trades=len(cc), identical_entries=len(fset & cset), frozen_only=len(fset - cset), causal_only=len(cset - fset))
    # trades in the frozen set whose order was NOT the earliest fill among the orders a causal trader would hold at that time
    fills = [ev for ev in log if ev[0] == "fill"]; res["causal_wall_fills_with_other_orders_pending"] = int(sum(ev[3] > 0 for ev in fills))
    res["causal_wall_fills"] = len(fills)
    # weekday gaps > 90 minutes (forward.py would STOP if an order/position were active)
    gaps = np.flatnonzero(np.diff(m) > 90); wd = ((m[gaps + 1] // 1440) + 3) % 7       # 0 = Monday
    res["weekday_gaps_over_90min"] = int((wd < 5).sum())
    res["frozen_reference_2x"] = FROZEN_REF[mkt]; res["secs"] = round(time.time() - t0)
    for name in ("FROZEN", "CAUSAL_CANDLE", "CAUSAL_WALL", "FORWARD_COSTS"):
        print(mkt, name, {p: (v.get("trades"), v.get("mean_bp_2x")) for p, v in res[name].items()}, flush=True)
    print(mkt, "lookahead==frozen", res["lookahead_equals_frozen"], res["overlap"], flush=True)
    return res


if __name__ == "__main__":
    out = {}
    for mkt, kind in (("ETHUSDT", "fib"), ("USOILm", "fib"), ("XAUUSDm", "fvg")):
        out[mkt] = run(mkt, kind); json.dump(out, open(OUT, "w"), indent=1)
