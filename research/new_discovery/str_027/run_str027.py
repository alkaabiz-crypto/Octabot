"""STR-027 (PREREG.md): Volumetric Order Blocks + EMA 21/50 + TP1-TP5 management. Causal: blocks are known only at the
1h close that confirms them; limits are pending orders filled on later 15m candles; newest block replaces the pending one.
usage: BTC_DATA=<dir with btc_{15m,1h}.json.gz> DISCOVERY_DATA=<scratch with long/> python3 -I run_str027.py
"""
import gzip, json, math, os, sys
import numpy as np, pandas as pd
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src")); import common as C  # noqa: E402
PER = [("EARLY", 0, 1672531200), ("TRAIN", 1672531200, 1719792000), ("VALIDATION", 1719792000, 1751328000), ("TEST", 1751328000, 2 * 10 ** 9)]
HOLD = 72 * 4; VALID_H = 48; MIN_RISK = 0.0015


def load(m):
    if m in ("BTCUSDT", "ETHUSDT"):
        src = (os.path.join(os.environ["BTC_DATA"], "btc_{}.json.gz") if m == "BTCUSDT" else os.path.join(ROOT, "rsi_vwap_study", "data", "ethusdt_{}.json.gz"))
        q = np.array(json.load(gzip.open(src.format("15m"))), float); hh = np.array(json.load(gzip.open(src.format("1h"))), float)
        return dict(t=q[:, 0].astype(np.int64), o=q[:, 1], h=q[:, 2], l=q[:, 3], c=q[:, 4]), dict(t=hh[:, 0].astype(np.int64), o=hh[:, 1], h=hh[:, 2], l=hh[:, 3], c=hh[:, 4], v=hh[:, 5]), None
    d = pd.read_csv(os.path.join(os.environ["DISCOVERY_DATA"], "long", f"{m}_15m.csv.gz"))
    o, h, l, c = (d.bo + d.ao) / 2, (d.bh + d.ah) / 2, (d.bl + d.al) / 2, (d.bc + d.ac) / 2; sp = float(((d.ao - d.bo) / o).median())
    q = dict(t=d.t.values.astype(np.int64), o=o.values, h=h.values, l=l.values, c=c.values)
    g = pd.DataFrame(dict(o=o, h=h, l=l, c=c, v=d.ticks, k=d.t // 3600 * 3600)).groupby("k")
    H = dict(t=np.array(g.o.first().index, np.int64), o=g.o.first().values, h=g.h.max().values, l=g.l.min().values, c=g.c.last().values, v=g.v.sum().values.astype(float))
    return q, H, sp


@njit(cache=True)
def manage(o, h, l, c, i0, side, entry, risk, hold):
    """From fill candle i0: stop first; TP k at k*R closes 20% (not on the fill candle); breakeven after TP1; time exit. Returns (R_gross, exit_idx)."""
    stop = entry - side * risk; hit = 0; got = 0.0; n = len(o); end = min(i0 + hold, n - 1)
    for i in range(i0, end + 1):
        adverse = l[i] if side > 0 else h[i]; favor = h[i] if side > 0 else l[i]
        if (adverse - stop) * side <= 0:
            px = stop
            if i > i0 and (o[i] - stop) * side < 0: px = o[i]
            return got + (1.0 - 0.2 * hit) * (px - entry) * side / risk, i
        if i > i0:
            while hit < 5 and (favor - (entry + side * (hit + 1) * risk)) * side >= 0:
                hit += 1; got += 0.2 * hit
                if hit == 1: stop = entry
            if hit == 5: return got, i
    return got + (1.0 - 0.2 * hit) * (c[end] - entry) * side / risk, end


def blocks(H, use_ema=True, use_vol=True):
    """Return orders: (t_active, t_expire, side, edge, far) known at the 1h close that created them."""
    o, h, l, c, v, t = H["o"], H["h"], H["l"], H["c"], H["v"], H["t"]; n = len(c)
    ema = lambda x, s: pd.Series(x).ewm(span=s, adjust=False).mean().values
    e21, e50 = ema(c, 21), ema(c, 50); out = []; shi = slo = None; sh_broken = sl_broken = True
    for i in range(60, n):
        j = i - 5                                                          # swing at j confirmed at close of i
        if h[j] == h[j - 5:j + 6].max(): shi, sh_broken = j, False
        if l[j] == l[j - 5:j + 6].min(): slo, sl_broken = j, False
        for side in (1, -1):
            sw, broken = (shi, sh_broken) if side > 0 else (slo, sl_broken)
            if sw is None or broken: continue
            lvl = h[sw] if side > 0 else l[sw]
            if not ((c[i] - lvl) * side > 0): continue
            if side > 0: sh_broken = True
            else: sl_broken = True
            if use_ema and (e21[i] - e50[i]) * side <= 0: continue
            k = next((q for q in range(i - 1, max(sw, i - 20), -1) if (c[q] - o[q]) * side < 0), None)
            if k is None or k + 2 > i: continue
            vv = v[k:k + 3]; tot = vv.sum(); share = vv[(c[k:k + 3] - o[k:k + 3]) * side > 0].sum() / tot if tot > 0 else 0
            if use_vol and share < 0.5: continue
            edge, far = (h[k], l[k]) if side > 0 else (l[k], h[k])
            out.append((int(t[i] + 3600), int(t[i] + 3600 + VALID_H * 3600), side, float(edge), float(far), i))
    return out


def run(Q, H, orders, cost_pr, cost_st):
    t, o, h, l, c = Q["t"], Q["o"], Q["h"], Q["l"], Q["c"]; Hc, Ht = H["c"], H["t"]; trades = []; pend = None; oi = 0; i = 0; n = len(t); free_t = 0
    hidx = {int(x): k for k, x in enumerate(Ht)}
    while i < n:
        while oi < len(orders) and orders[oi][0] <= t[i]:
            if orders[oi][0] >= free_t: pend = orders[oi]                # newest replaces
            oi += 1
        if pend is not None:
            ta, te, side, edge, far, _ = pend
            k = hidx.get(int(t[i] // 3600 * 3600 - 3600))                 # last closed hour: invalidation
            if t[i] >= te or (k is not None and Ht[k] >= ta - 3600 and (Hc[k] - far) * side < 0): pend = None
            elif (l[i] <= edge if side > 0 else h[i] >= edge):
                e = min(o[i], edge) if side > 0 else max(o[i], edge); risk = abs(e - far)
                if risk / e >= MIN_RISK and (e - far) * side > 0:
                    rg, x = manage(o, h, l, c, i, side, e, risk, HOLD)
                    trades.append(dict(t=int(t[i]), side=side, i=i, x=int(x), risk_pct=risk / e, r=rg - cost_pr * e / risk, rs=rg - cost_st * e / risk))
                    free_t = int(t[x]) + 900; pend = None; i = x + 1; continue
                pend = None
        i += 1
    return trades


def bench(Q, trades, cost_pr, lo, hi, rng, sets=1000, per_trade=40):
    t, o, h, l, c = Q["t"], Q["o"], Q["h"], Q["l"], Q["c"]; pool = np.flatnonzero((t >= lo) & (t < hi - HOLD * 900)); sims = np.empty((len(trades), per_trade))
    for a, tr in enumerate(trades):
        for b in range(per_trade):
            i = int(pool[rng.integers(len(pool))]); e = o[i]; risk = tr["risk_pct"] * e
            rg, _ = manage(o, h, l, c, i, tr["side"], e, risk, HOLD); sims[a, b] = rg - cost_pr * e / risk
    pick = rng.integers(per_trade, size=(sets, len(trades))); means = sims[np.arange(len(trades)), pick].mean(axis=1)
    act = np.mean([x["r"] for x in trades]); return float((means >= act).mean()), float(means.mean())


def summarize(Q, trades, cost_pr, rng, with_bench=True):
    out = {}
    for p, lo, hi in PER:
        sel = [x for x in trades if lo <= x["t"] < hi]
        if not sel: out[p] = dict(trades=0); continue
        r = np.array([x["r"] for x in sel]); rs = np.array([x["rs"] for x in sel])
        d = dict(trades=len(sel), mean_R=round(float(r.mean()), 4), mean_R_stress=round(float(rs.mean()), 4), win_pct=round(float((r > 0).mean() * 100), 1),
                 t=round(float(r.mean() / (r.std(ddof=1) / math.sqrt(len(r)))), 2) if len(r) > 2 else None)
        if with_bench and len(sel) >= 10: d["p_random"], d["random_mean_R"] = bench(Q, sel, cost_pr, lo, hi, rng); d["random_mean_R"] = round(d["random_mean_R"], 4)
        out[p] = d
    return out


def main():
    R = {}; rng = np.random.default_rng(2027)
    for m in ("BTCUSDT", "ETHUSDT", "XAUUSDm", "USOILm"):
        Q, H, sp = load(m); cp, cs = (0.0005, 0.0020) if sp is None else (1.5 * sp, 3 * sp); res = {}
        for name, ue, uv in (("FULL", True, True), ("NO_EMA", False, True), ("NO_VOLUME", True, False)):
            tr = run(Q, H, blocks(H, ue, uv), cp, cs); res[name] = summarize(Q, tr, cp, rng, with_bench=(name == "FULL"))
        R[m] = dict(cost_primary=cp, cost_stress=cs, results=res)
        print(m, {k: {p: (v.get("trades"), v.get("mean_R"), v.get("p_random")) for p, v in r.items()} for k, r in res.items()}, flush=True)
    keys = list(R); ps = [R[m]["results"]["FULL"]["TEST"].get("p_random", 1.0) for m in keys]; sig = C.bh(ps)
    for i, m in enumerate(keys):
        f = R[m]["results"]["FULL"]; te = f["TEST"]; avail = [p for p, *_ in PER if f[p].get("trades", 0) > 0]
        pos = all(f[p]["mean_R"] > 0 for p in avail)
        R[m]["decision"] = "SCREEN-PASS" if (pos and te.get("mean_R_stress", -1) > 0 and i in sig and te.get("trades", 0) >= 30) else ("WATCH" if pos else "REJECTED")
        print(m, "DECISION:", R[m]["decision"])
    json.dump(R, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
