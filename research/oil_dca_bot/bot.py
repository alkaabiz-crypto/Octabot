"""Rebuild of the user's USOIL DCA bot (#16) and a one-year Exness tick backtest. Implements PREREGISTRATION.md.

Research only: no broker connection, no orders.
Usage: TICK_DIR=<dir with Exness_USOILm_YYYY_MM.zip> CACHE_DIR=<scratch> python3 -I bot.py
"""
import hashlib, json, math, os, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
TICK_DIR, CACHE = os.environ["TICK_DIR"], os.environ["CACHE_DIR"]
MONTHS = ["2025_09", "2025_10", "2025_11", "2025_12", "2026_01", "2026_02", "2026_03", "2026_04", "2026_05", "2026_06",
          "2026_07", "2026_08", "2026_09", "2026_10"]
START, END = "2025-11-01", "2026-11-01"
# bot settings (user's screenshot)
LOTS = [0.01, 0.02, 0.03]            # initial, extra 1 (0.02), extra 2 (0.02 x 1.5)
STEPS = [0.63, 0.63 * 1.3]           # 63 pips, then x1.3 (1 pip = 0.01)
TP, TRAIL = 0.15, 0.04               # 15 pips from average, trailing 4 pips
BARRELS = 1000                       # per lot
BASKET_STOP_USD = 50.0               # V1/V2
TF_MS, H4_MS = 15 * 60_000, 4 * 3_600_000
N_RANDOM, SEED = 500, 20261110


def fmt(ms): return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ms / 1000))


def convert(m):
    zp = os.path.join(TICK_DIR, f"Exness_USOILm_{m}.zip"); out = os.path.join(CACHE, f"{m}.npz")
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    if not os.path.exists(out):
        df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"])
        assert (df["sym"] == "USOILm").all()
        t = pd.to_datetime(df["ts"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
        assert 1.7e12 < t[0] < 1.9e12
        np.savez(out, t=t, bid=df["bid"].to_numpy(np.float64), ask=df["ask"].to_numpy(np.float64))
    return m, sha


def load():
    os.makedirs(CACHE, exist_ok=True)
    with Pool(4) as p: meta = p.map(convert, MONTHS)
    parts = [np.load(os.path.join(CACHE, f"{m}.npz")) for m in MONTHS]
    t = np.concatenate([d["t"] for d in parts]); b = np.concatenate([d["bid"] for d in parts]); a = np.concatenate([d["ask"] for d in parts])
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    q = {}
    for (m, sha), d in zip(meta, parts):
        s = d["ask"] - d["bid"]
        q[m] = dict(sha256=sha, ticks=int(len(d["t"])), ask_below_bid=int((s < 0).sum()), first=fmt(d["t"][0]), last=fmt(d["t"][-1]),
                    spread_median=round(float(np.median(s)), 4), spread_p95=round(float(np.percentile(s, 95)), 4), spread_max=round(float(s.max()), 4))
    return t, b, a, q


def candles(t, px, tf):
    k = t // tf; st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(t)]
    return pd.DataFrame(dict(close_ms=(k[st] + 1) * tf, o=px[st], h=np.maximum.reduceat(px, st), l=np.minimum.reduceat(px, st), c=px[en - 1], v=en - st))


# ---------------------------------------------------------------- TradingView-style technical rating (approximation)
def rating(df):
    c, h, l, v = df.c, df.h, df.l, df.v.astype(float)
    vote = lambda buy, sell: np.where(buy, 1.0, np.where(sell, -1.0, 0.0))
    ma = []
    for n in (10, 20, 30, 50, 100, 200):
        for m in (c.rolling(n).mean(), c.ewm(span=n, adjust=False).mean()):
            ma.append(vote(m < c, m > c) + np.where(m.isna(), np.nan, 0))
    base = (h.rolling(26).max() + l.rolling(26).min()) / 2                                     # Ichimoku base line (simplified)
    ma.append(vote(base < c, base > c) + np.where(base.isna(), np.nan, 0))
    vwma = (c * v).rolling(20).sum() / v.rolling(20).sum(); ma.append(vote(vwma < c, vwma > c) + np.where(vwma.isna(), np.nan, 0))
    wma = lambda s, n: s.rolling(n).apply(lambda x: np.dot(x, np.arange(1, n + 1)) / (n * (n + 1) / 2), raw=True)
    hma = wma(2 * wma(c, 4) - wma(c, 9), 3); ma.append(vote(hma < c, hma > c) + np.where(hma.isna(), np.nan, 0))
    osc = []
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn); osc.append(vote((rsi < 30) & (rsi > rsi.shift()), (rsi > 70) & (rsi < rsi.shift())))
    k = (100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min())).rolling(3).mean(); dd = k.rolling(3).mean()
    osc.append(vote((k < 20) & (dd < 20) & (k > dd), (k > 80) & (dd > 80) & (k < dd)))
    tp = (h + l + c) / 3; cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True))
    osc.append(vote((cci < -100) & (cci > cci.shift()), (cci > 100) & (cci < cci.shift())))
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    pdm = np.where((h.diff() > -l.diff()) & (h.diff() > 0), h.diff(), 0.0); mdm = np.where((-l.diff() > h.diff()) & (-l.diff() > 0), -l.diff(), 0.0)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    pdi = 100 * pd.Series(pdm, index=c.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
    mdi = 100 * pd.Series(mdm, index=c.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean()
    osc.append(vote((adx > 20) & (pdi.shift() < mdi.shift()) & (pdi > mdi), (adx > 20) & (pdi.shift() > mdi.shift()) & (pdi < mdi)))
    mid = (h + l) / 2; ao = mid.rolling(5).mean() - mid.rolling(34).mean()
    osc.append(vote(((ao > 0) & (ao.shift() <= 0)) | ((ao > 0) & (ao > ao.shift()) & (ao.shift() < ao.shift(2))),
                    ((ao < 0) & (ao.shift() >= 0)) | ((ao < 0) & (ao < ao.shift()) & (ao.shift() > ao.shift(2)))))
    mom = c - c.shift(10); osc.append(vote(mom > mom.shift(), mom < mom.shift()))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean(); sig = macd.ewm(span=9, adjust=False).mean()
    osc.append(vote(macd > sig, macd < sig))
    srsi = (rsi - rsi.rolling(14).min()) / (rsi.rolling(14).max() - rsi.rolling(14).min()) * 100; sk = srsi.rolling(3).mean(); sd = sk.rolling(3).mean()
    osc.append(vote((sk < 20) & (sd < 20) & (sk > sd), (sk > 80) & (sd > 80) & (sk < sd)))
    wr = -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min())
    osc.append(vote((wr < -80) & (wr > wr.shift()), (wr > -20) & (wr < wr.shift())))
    e13 = c.ewm(span=13, adjust=False).mean(); bull, bear = h - e13, l - e13
    osc.append(vote((c > e13) & (bear < 0) & (bear > bear.shift()), (c < e13) & (bull > 0) & (bull < bull.shift())))
    bp = c - pd.concat([l, c.shift()], axis=1).min(axis=1); trr = pd.concat([h, c.shift()], axis=1).max(axis=1) - pd.concat([l, c.shift()], axis=1).min(axis=1)
    avg = lambda n: bp.rolling(n).sum() / trr.rolling(n).sum()
    uo = 100 * (4 * avg(7) + 2 * avg(14) + avg(28)) / 7; osc.append(vote(uo > 70, uo < 30))
    assert len(ma) + len(osc) == 26
    r = (np.nanmean(np.vstack(ma), axis=0) + np.mean(np.vstack(osc), axis=0)) / 2
    r[np.isnan(np.vstack(ma)).any(axis=0)] = np.nan                                            # require full warm-up
    return r


# ---------------------------------------------------------------- basket simulation
def first(mask_fn, i, end):
    w = 2048
    while i < end:
        j = min(end, i + w); m = mask_fn(i, j)
        if m.any(): return i + int(np.argmax(m))
        i = j; w *= 4
    return None


def basket(t, bid, ask, i0, side, stop_usd):
    """One basket starting at tick i0. side +1 BUY, -1 SELL. Returns dict with P&L, exit index, worst floating."""
    n = len(t)
    ent = ask if side > 0 else bid          # side we fill on
    ext = bid if side > 0 else ask          # side we exit on
    fills = [(LOTS[0], float(ent[i0]))]; levels = []
    lvl = fills[0][1]
    for s in STEPS: lvl = lvl - side * s; levels.append(lvl)
    i = i0 + 1; worst = 0.0
    while True:
        L = sum(x for x, _ in fills); avg = sum(x * p for x, p in fills) / L
        tp_px = avg + side * TP
        stop_px = avg - side * stop_usd / (BARRELS * L) if stop_usd else None
        nxt = levels[len(fills) - 1] if len(fills) < len(LOTS) else None
        def m(a, b):
            e = ext[a:b]; f = ent[a:b]
            mk = (e - tp_px) * side >= 0
            if nxt is not None: mk |= (f - nxt) * side <= 0
            if stop_px is not None: mk |= (e - stop_px) * side <= 0
            return mk
        j = first(m, i, n)
        seg_end = n if j is None else j + 1
        adverse = ext[i:seg_end].min() if side > 0 else ext[i:seg_end].max()
        worst = min(worst, (adverse - avg) * side * BARRELS * L)
        if j is None:
            return dict(pnl=(ext[n - 1] - avg) * side * BARRELS * L, exit=n - 1, outcome="OPEN_AT_END", orders=len(fills), worst=worst, lots=L)
        if stop_px is not None and (ext[j] - stop_px) * side <= 0:
            return dict(pnl=(ext[j] - avg) * side * BARRELS * L, exit=j, outcome="STOP", orders=len(fills), worst=worst, lots=L)
        if (ext[j] - tp_px) * side >= 0:
            # trailing: exit when price pulls back TRAIL from its best level since activation
            k = j
            while True:
                b2 = min(n, k + 4096); seg = ext[k:b2]
                best = np.maximum.accumulate(seg) if side > 0 else np.minimum.accumulate(seg)
                if k > j: best = np.maximum(best, best_prev) if side > 0 else np.minimum(best, best_prev)
                hit = (best - seg) * side >= TRAIL
                if hit.any():
                    x = k + int(np.argmax(hit))
                    return dict(pnl=(ext[x] - avg) * side * BARRELS * L, exit=x, outcome=f"TP_after_{len(fills)}_orders", orders=len(fills), worst=worst, lots=L)
                if b2 >= n:
                    return dict(pnl=(ext[n - 1] - avg) * side * BARRELS * L, exit=n - 1, outcome="OPEN_AT_END", orders=len(fills), worst=worst, lots=L)
                best_prev = best[-1]; k = b2
        fills.append((LOTS[len(fills)], nxt)); i = j + 1


def run(t, bid, ask, closes_ms, dirs, stop_usd, record=False):
    """Sequential baskets: one at a time; a new one opens at the first 15m close after the previous exit."""
    pos = np.searchsorted(t, closes_ms, side="left")
    eq = 0.0; peak = 0.0; maxdd = 0.0; out = []; k = 0; nC = len(closes_ms)
    while k < nC:
        if dirs[k] == 0: k += 1; continue
        i0 = pos[k]
        if i0 >= len(t) or t[i0] - closes_ms[k] > 60_000: k += 1; continue
        r = basket(t, bid, ask, i0, int(dirs[k]), stop_usd)
        maxdd = max(maxdd, peak - (eq + r["worst"]))
        eq += r["pnl"]; peak = max(peak, eq); maxdd = max(maxdd, peak - eq)
        if record: out.append(dict(open=fmt(int(t[i0])), side="BUY" if dirs[k] > 0 else "SELL", close=fmt(int(t[r["exit"]])),
                                   hours=round((t[r["exit"]] - t[i0]) / 3.6e6, 2), orders=r["orders"], lots=round(r["lots"], 2),
                                   pnl_usd=round(r["pnl"], 2), worst_floating_usd=round(r["worst"], 2), outcome=r["outcome"]))
        k = int(np.searchsorted(closes_ms, t[r["exit"]], side="right"))
    return eq, maxdd, out


def summary(rows, eq, dd):
    df = pd.DataFrame(rows)
    if df.empty: return dict(baskets=0)
    w = df[df.pnl_usd > 0].pnl_usd; ls = df[df.pnl_usd <= 0].pnl_usd
    return dict(baskets=len(df), net_usd=round(eq, 2), gross_profit_usd=round(w.sum(), 2), gross_loss_usd=round(ls.sum(), 2),
                win_rate=round(len(w) / len(df), 4), avg_win_usd=round(w.mean(), 2) if len(w) else None, avg_loss_usd=round(ls.mean(), 2) if len(ls) else None,
                worst_basket_usd=round(df.pnl_usd.min(), 2), worst_floating_usd=round(df.worst_floating_usd.min(), 2),
                max_drawdown_usd=round(dd, 2), longest_basket_hours=round(df.hours.max(), 1), median_basket_hours=round(df.hours.median(), 2),
                baskets_reaching_all_3_orders=int((df.orders == 3).sum()), outcomes=df.outcome.value_counts().to_dict(),
                by_side={s: dict(n=int((df.side == s).sum()), net_usd=round(float(df[df.side == s].pnl_usd.sum()), 2)) for s in ("BUY", "SELL")},
                monthly_usd={m: round(float(v), 2) for m, v in df.groupby(df.close.str[:7]).pnl_usd.sum().items()})


def main():
    t0 = time.time()
    t, bid, ask, q = load()
    print(f"ticks {len(t):,} load {time.time() - t0:.0f}s", flush=True)
    c15 = candles(t, bid, TF_MS); r = rating(c15)
    c4 = candles(t, bid, H4_MS); c4["ema200"] = c4.c.ewm(span=200, adjust=False).mean(); c4.loc[c4.index < 200, "ema200"] = np.nan
    idx = np.searchsorted(c4.close_ms.values, c15.close_ms.values, side="right") - 1
    ema = np.where(idx >= 0, c4.ema200.values[np.clip(idx, 0, None)], np.nan)
    s, e = (int(pd.Timestamp(x, tz="UTC").as_unit("ns").value // 1_000_000) for x in (START, END))
    sel = (c15.close_ms.values > s) & (c15.close_ms.values <= e) & ~np.isnan(r)
    closes = c15.close_ms.values[sel]; rr = r[sel]; cl = c15.c.values[sel]; em = ema[sel]
    d_sig = np.where(rr > 0.1, 1, np.where(rr < -0.1, -1, 0))
    d_trend = np.where(np.isnan(em), 0, np.where((d_sig > 0) & (cl > em), 1, np.where((d_sig < 0) & (cl < em), -1, 0)))
    tick_end = int(np.searchsorted(t, e)); T, B, A = t[:tick_end], bid[:tick_end], ask[:tick_end]   # nothing after the window
    res = dict(generated_utc=fmt(int(time.time() * 1000)), data=q, settings=dict(lots=LOTS, steps=STEPS, tp=TP, trail=TRAIL, basket_stop_usd=BASKET_STOP_USD),
               rating_15m_share=dict(buy=float((d_sig > 0).mean()), sell=float((d_sig < 0).mean()), neutral=float((d_sig == 0).mean())), variants={})
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    for name, dirs, stop in (("V0_as_configured_no_stop", d_sig, None), ("V1_basket_stop_50usd", d_sig, BASKET_STOP_USD), ("V2_stop_plus_4h_trend_filter", d_trend, BASKET_STOP_USD)):
        eq, dd, rows = run(T, B, A, closes, dirs, stop, record=True)
        res["variants"][name] = summary(rows, eq, dd)
        pd.DataFrame(rows).to_csv(os.path.join(HERE, "results", f"{name}_baskets.csv"), index=False)
        print(name, json.dumps({k: v for k, v in res["variants"][name].items() if k not in ("monthly_usd", "outcomes", "by_side")}), f"{time.time() - t0:.0f}s", flush=True)
    rng = np.random.default_rng(SEED); nets, dds = [], []
    for n in range(N_RANDOM):
        dirs = rng.choice([-1, 1], size=len(closes))
        eq, dd, _ = run(T, B, A, closes, dirs, BASKET_STOP_USD); nets.append(eq); dds.append(dd)
        if (n + 1) % 50 == 0: print(f"  random {n + 1}/{N_RANDOM} {time.time() - t0:.0f}s", flush=True)
    nets, dds = np.array(nets), np.array(dds)
    res["random_direction_V1"] = dict(runs=N_RANDOM, net_median=round(float(np.median(nets)), 2), net_p5=round(float(np.percentile(nets, 5)), 2),
                                      net_p95=round(float(np.percentile(nets, 95)), 2), maxdd_median=round(float(np.median(dds)), 2),
                                      V1_net_percentile=round(float((nets < res["variants"]["V1_basket_stop_50usd"]["net_usd"]).mean() * 100), 1))
    v1, v2 = res["variants"]["V1_basket_stop_50usd"], res["variants"]["V2_stop_plus_4h_trend_filter"]
    res["V2_better_than_V1"] = bool(v2["net_usd"] > v1["net_usd"] and v2["max_drawdown_usd"] <= v1["max_drawdown_usd"])
    json.dump(res, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print("done", f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
