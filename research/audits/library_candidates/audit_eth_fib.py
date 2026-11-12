"""READ-ONLY statistical audit of the frozen ETH Fibonacci candidate (theory library B9, ETHUSDT 1h).

Nothing in research/theory_library or research/library_forward is modified. The frozen verify_minute.py functions are
imported from an untouched extract of branch claude/download-skill-27d08k (LIB_DIR) and run on Binance ETHUSDT 1-minute
klines re-downloaded with the library's own fetch_binance_1m.py, truncated to the frozen cutoff 2026-11-10 11:19 UTC.

Steps:
 1. reproduce the frozen numbers (2025: 326 trades +32.28 bp; 2026: 288 +19.62 bp; common cutoff 287 +19.09 bp, at 2x cost);
 2. dependence: serial correlation of trade returns, Ljung-Box Q(5), Newey-West t (5 lags), stationary block-bootstrap CI;
 3. exposure: time in market, simultaneous positions, mark-to-market (minute) drawdown of the compounded equity;
 4. order-selection sensitivity: the forward test's causal rule (several pending orders, the first to fill in time wins)
    versus the backtest's sequential rule (an older order that fills later beats a newer order that fills earlier);
 5. the forward pass rule (mean > 0 and >= 2 bp at 2x after 100 trades): its pass probability if the true mean were 0.
usage: LIB_DIR=<extract>/research/theory_library BIN_DIR=<dir with ETHUSDT_1m.npz> python3 audit_eth_fib.py"""
import json
import math
import os
import sys

import numpy as np

LIB = os.environ["LIB_DIR"]
sys.path.insert(0, LIB)
os.environ.setdefault("BARS_DIR", "/nonexistent")
import verify_minute as V  # noqa: E402  (frozen code, imported unchanged)

CUT_MIN = int(np.datetime64("2026-11-10T11:19:00").astype("datetime64[m]").astype(np.int64))
HOLD_MIN = V.HOLD_MS // 60000
SCREEN_LAST_CANDLE_MIN = int(np.datetime64("2026-11-09T23:00:00").astype("datetime64[m]").astype(np.int64))
H = 60


def net_returns(M, tr, mult):
    side = np.array([t[0] for t in tr]); f = np.array([t[1] for t in tr]); x = np.array([t[2] for t in tr])
    pe = np.array([t[3] for t in tr]); px = np.array([t[4] for t in tr])
    return (side * (px - pe) - mult * (M["hs"][f] + M["hs"][x])) / pe


def causal_b9(M, Hc, fib=0.618, look=20):
    """B9 with the forward test's order selection (library_forward/forward.py): orders live 10 candles, several can be
    pending, at each minute the oldest pending order that fills is taken and the rest cancelled; after an exit new signals
    are considered from the second hour boundary after the exit minute's hour. Fill/stop/target/time rules as run_limit."""
    o, h, l, c = Hc["o"], Hc["h"], Hc["l"], Hc["c"]
    s50 = V.sma(c, 50)
    m = M["m"]; mo, mh, ml, mc, pen = M["o"], M["h"], M["l"], M["c"], M["pen"]
    out, pending, pos = [], [], None
    next_check_min = 0
    start_of = Hc["s"]
    for k in range(50, len(c) - 1):
        hour_open_min = m[start_of[k + 1]] if k + 1 < len(start_of) else None
        if hour_open_min is None:
            break
        # signal at the close of candle k (only when flat and allowed)
        if pos is None and hour_open_min >= next_check_min:
            hh, ll = h[k - look + 1:k + 1], l[k - look + 1:k + 1]
            ih, il = int(np.argmax(hh)), int(np.argmin(ll)); Hh, Ll = hh[ih], ll[il]
            side = 1 if (c[k] > s50[k] and ih > il) else (-1 if (c[k] < s50[k] and il > ih) else 0)
            if side and Hh > Ll:
                lim = Hh - fib * (Hh - Ll) if side > 0 else Ll + fib * (Hh - Ll)
                stop, tp = (Ll, Hh) if side > 0 else (Hh, Ll)
                pending.append(dict(side=side, lim=lim, stop=stop, tp=tp, exp_k=k + 11))
        # minutes of candle k+1
        a, b = start_of[k + 1], Hc["e"][k + 1]
        for q in range(a, b):
            if pos is None and pending:
                pending = [p for p in pending if k + 1 < p["exp_k"]]
                for p in pending:
                    if (p["side"] > 0 and ml[q] <= p["lim"] - pen[q]) or (p["side"] < 0 and mh[q] >= p["lim"] + pen[q]):
                        e = min(mo[q], p["lim"]) if p["side"] > 0 else max(mo[q], p["lim"])
                        pos = dict(side=p["side"], f=q, pe=e, stop=p["stop"], tp=p["tp"], last_k=min(k + 1 + 20, len(start_of) - 1))
                        pending = []
                        break
            if pos is not None:
                sd = pos["side"]; ex = None
                if q > pos["f"] and ((sd > 0 and mo[q] <= pos["stop"]) or (sd < 0 and mo[q] >= pos["stop"])): ex = mo[q]
                elif (sd > 0 and ml[q] <= pos["stop"]) or (sd < 0 and mh[q] >= pos["stop"]): ex = pos["stop"]
                elif q > pos["f"] and ((sd > 0 and mh[q] >= pos["tp"] + pen[q]) or (sd < 0 and ml[q] <= pos["tp"] - pen[q])): ex = pos["tp"]
                elif q == Hc["e"][pos["last_k"]] - 1: ex = mc[q]
                if ex is not None:
                    out.append((sd, pos["f"], q, pos["pe"], ex))
                    next_check_min = (m[q] // H) * H + 2 * H
                    pos = None
    return out


def dependence(r):
    n = len(r); x = r - r.mean()
    ac = [float((x[k:] @ x[:-k]) / (x @ x)) for k in range(1, 6)]
    q = n * (n + 2) * sum(a * a / (n - k) for k, a in enumerate(ac, 1))
    lrv = (x @ x) / n + 2 * sum((1 - k / 6) * (x[k:] @ x[:-k]) / n for k in range(1, 6))
    nw_t = r.mean() / math.sqrt(lrv / n)
    rng = np.random.default_rng(1)
    bs = []
    for _ in range(4000):
        idx = np.empty(n, int); i = rng.integers(n)
        for k in range(n):
            idx[k] = i; i = rng.integers(n) if rng.random() < 0.1 else (i + 1) % n
        bs.append(r[idx].mean())
    return dict(autocorr_lag1_5=[round(a, 3) for a in ac], ljung_box_Q5=round(q, 2), ljung_box_crit_5pct=11.07,
                iid_t=round(float(r.mean() / (r.std(ddof=1) / math.sqrt(n))), 2), newey_west_t=round(float(nw_t), 2),
                block_bootstrap_ci95_bp=[round(float(np.percentile(bs, 2.5) * 1e4), 2), round(float(np.percentile(bs, 97.5) * 1e4), 2)])


def exposure(M, tr, r):
    f = np.array([t[1] for t in tr]); x = np.array([t[2] for t in tr])
    overlap = int(np.sum(f[1:] <= x[:-1]))
    in_mkt = float((M["m"][x] - M["m"][f]).sum() / (M["m"][x[-1]] - M["m"][f[0]]))
    # mark-to-market drawdown of the compounded equity (whole account in every trade), minute closes inside trades
    eq, peak, worst = 1.0, 1.0, 0.0
    for (sd, fi, xi, pe, px), rr in zip(tr, r):
        path = sd * (M["c"][fi:xi] - pe) / pe
        if len(path):
            worst = min(worst, (eq * (1 + path.min())) / peak - 1)
        eq *= 1 + rr; peak = max(peak, eq); worst = min(worst, eq / peak - 1)
    return dict(overlapping_trades=overlap, time_in_market_pct=round(100 * in_mkt, 1), mtm_max_drawdown_pct=round(100 * worst, 2))


def summary(r):
    return dict(trades=int(len(r)), mean_bp=round(float(r.mean() * 1e4), 2), t=round(float(r.mean() / (r.std(ddof=1) / math.sqrt(len(r)))), 2),
                sd_bp=round(float(r.std(ddof=1) * 1e4), 1), simple_sum_pct=round(float(r.sum() * 100), 2),
                compounded_pct=round(float((np.prod(1 + r) - 1) * 100), 2))


def main():
    z = np.load(os.path.join(os.environ["BIN_DIR"], "ETHUSDT_1m.npz"))
    keep = z["m"] <= CUT_MIN
    np.savez_compressed("/tmp/eth_cut.npz", **{k: z[k][keep] for k in ("m", "o", "h", "l", "c")})
    os.environ["BIN_DIR_CUT"] = "/tmp"
    V.BIN = "/tmp"
    os.replace("/tmp/eth_cut.npz", "/tmp/ETHUSDT_1m.npz")
    M, Hc = V.load("ETHUSDT")
    out = {"data": dict(first_minute=str(np.datetime64(int(M["m"][0]), "m")), last_minute=str(np.datetime64(int(M["m"][-1]), "m")), minutes=int(len(M["m"])))}
    for name, fn in (("frozen_sequential_rule", V.b9), ("forward_causal_rule", causal_b9)):
        tr = fn(M, Hc)
        dev = [t for t in tr if M["m"][t[1]] < HOLD_MIN]
        hold = [t for t in tr if M["m"][t[1]] >= HOLD_MIN]
        hold_cut = [t for t in hold if M["m"][t[2]] < SCREEN_LAST_CANDLE_MIN + 60]
        res = {}
        for p, t in (("2025", dev), ("2026", hold), ("2026_common_cutoff", hold_cut)):
            r2 = net_returns(M, t, 2)
            res[p] = dict(x2=summary(r2), x1=summary(net_returns(M, t, 1)), dependence_x2=dependence(r2), exposure=exposure(M, t, r2))
        out[name] = res
        print(name, json.dumps({p: v["x2"] for p, v in res.items()}), flush=True)
    # forward pass rule under a zero true mean (normal approximation, observed per-trade sd)
    sd2026 = out["frozen_sequential_rule"]["2026"]["x2"]["sd_bp"]
    se100 = sd2026 / 10.0
    out["forward_rule_zero_edge_pass_probability"] = dict(per_trade_sd_bp=sd2026, se_of_mean_at_100_trades_bp=round(se100, 1),
                                                         p_mean_ge_2bp_if_true_mean_0=round(0.5 * math.erfc((2 / se100) / math.sqrt(2)), 3))
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "eth_fib_audit.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
