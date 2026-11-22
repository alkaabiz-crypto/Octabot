"""Full statistics for the candidates (FREEZE reconciliation items 4 and 5), from the V1 minute-level trades of verify_minute.py.
No rule is changed: verify_minute's functions are called as they are; run_limit is only wrapped to record each trade's stop (for R).

Per period at 1x and 2x cost: trades, mean bp, median bp, 95% CI of the mean (t), win rate, average R, profit factor, simple sum %,
compounded % (whole account in every trade, no leverage), max drawdown of the compounded equity, longest losing streak,
average hold. Random benchmark: percentile of the minute-level mean against the screen's 500-draw random control (same seeds).

Usage: BARS_DIR=<orb 1m bars> BIN_DIR=<binance 1m> python3 -I candidate_stats.py
"""
import json, os, sys, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import verify_minute as V  # noqa: E402
import engine as E  # noqa: E402
import theories as T  # noqa: E402
from sensitivity_hole import rand_means, SEED  # noqa: E402

CANDS = [("B9", "ETHUSDT", V.b9, T.b9), ("B9", "USOILm", V.b9, T.b9), ("D4", "XAUUSDm", V.d4, T.d4_fvg)]


def sem(x):
    return x.std(ddof=1) / np.sqrt(len(x))


def t975(df):
    """Two-sided 95% Student-t quantile (Cornish-Fisher expansion; error < 0.001 for df >= 30)."""
    z = 1.959964; return z + (z ** 3 + z) / (4 * df) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * df ** 2)


def trades_with_stops(M, Hc, fn):
    stops = []; orig = V.run_limit
    def wrap(M_, Hc_, k_from, k_to, side, lim, stop, tp, tmax):
        r = orig(M_, Hc_, k_from, k_to, side, lim, stop, tp, tmax)
        if r is not None: stops.append(stop)
        return r
    V.run_limit = wrap
    try: tr = fn(M, Hc)
    finally: V.run_limit = orig
    assert len(tr) == len(stops)
    return [t + (s,) for t, s in zip(tr, stops)]


def block(M, tr, mult):
    if not tr: return dict(trades=0)
    side = np.array([t[0] for t in tr]); f = np.array([t[1] for t in tr]); x = np.array([t[2] for t in tr]); pe = np.array([t[3] for t in tr]); px = np.array([t[4] for t in tr]); sl = np.array([t[5] for t in tr])
    cost = mult * (M["hs"][f] + M["hs"][x]); net = (side * (px - pe) - cost) / pe; R = (side * (px - pe) - cost) / np.abs(pe - sl)
    eq = np.cumprod(1 + net); dd = (eq / np.maximum.accumulate(eq) - 1).min(); h = t975(len(net) - 1) * sem(net); ci = (net.mean() - h, net.mean() + h)
    loss = net < 0; streak = cur = 0
    for v in loss: cur = cur + 1 if v else 0; streak = max(streak, cur)
    gains, losses = net[net > 0].sum(), -net[net < 0].sum()
    return dict(trades=int(len(net)), mean_bp=round(float(net.mean() * 1e4), 2), median_bp=round(float(np.median(net) * 1e4), 2),
                ci95_bp=[round(float(ci[0] * 1e4), 2), round(float(ci[1] * 1e4), 2)], t_stat=round(float(net.mean() / sem(net)), 2), win_rate=round(float((net > 0).mean()), 3),
                avg_R=round(float(R.mean()), 3), median_risk_bp=round(float(np.median(np.abs(pe - sl) / pe) * 1e4), 1), profit_factor=round(float(gains / losses), 3) if losses > 0 else None,
                simple_sum_pct=round(float(net.sum() * 100), 2), compounded_pct=round(float((eq[-1] - 1) * 100), 2), max_drawdown_pct=round(float(dd * 100), 2),
                longest_losing_streak=int(streak), avg_hold_hours=round(float(((M["m"][x] - M["m"][f]) / 60).mean()), 1),
                first_entry_utc=str(np.datetime64(int(M["m"][f[0]]) * 60, "s")), last_exit_utc=str(np.datetime64(int(M["m"][x[-1]]) * 60, "s")))


def main():
    out = {}
    for tid, mkt, vfn, sfn in CANDS:
        M, Hc = V.load(mkt); tr = trades_with_stops(M, Hc, vfn); hold = [t for t in tr if M["m"][t[1]] * 60000 >= V.HOLD_MS]; dev = [t for t in tr if M["m"][t[1]] * 60000 < V.HOLD_MS]
        key = f"{tid}|{mkt}|1h"; c, bk = sfn(mkt, "1h"); _, meta = E.evaluate(c, bk, 2); rnd = rand_means(c, meta, np.random.default_rng(SEED + zlib.crc32(key.encode()) % 100000))
        res = dict(data=dict(first_minute_utc=str(np.datetime64(int(M["m"][0]) * 60, "s")), last_minute_utc=str(np.datetime64(int(M["m"][-1]) * 60, "s")),
                             screen_last_candle_utc=str(np.datetime64(int(c.m.values[-1]) * 60, "s")), dev_period="2025-01-01 .. 2025-12-31", holdout_period=f"2026-01-01 .. last minute above"))
        for p, t in (("2025", dev), ("2026", hold)):
            res[p] = {"x1": block(M, t, 1), "x2": block(M, t, 2)}
            r = rnd["dev" if p == "2025" else "holdout"]; m2 = res[p]["x2"]["mean_bp"] / 1e4
            res[p]["random_control_x2"] = dict(draws=int(len(r)), median_bp=round(float(np.median(r) * 1e4), 2), p95_bp=round(float(np.percentile(r, 95) * 1e4), 2),
                                               p99_bp=round(float(np.percentile(r, 99) * 1e4), 2), minute_level_mean_percentile=round(float((r < m2).mean() * 100), 1))
        if mkt == "ETHUSDT":                                       # same cutoff as the screen's 1h file, for consistency
            cut = int(c.m.values[-1]) + 60; h2 = [t for t in hold if M["m"][t[2]] < cut]
            res["2026_truncated_to_screen_cutoff"] = {"x2": block(M, h2, 2)}
        out[key] = res; print(key, json.dumps(res, indent=1), flush=True)
    json.dump(out, open(os.path.join(HERE, "results", "candidate_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
