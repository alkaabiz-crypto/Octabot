"""Batch 003 (PREREG.md): round numbers, London metal fixes, BTC CME gap fill, Coinbase premium.
Decisions use closed 15-minute candles only; every entry is at a later candle's open. Execution at Exness bid/ask.
usage: DISCOVERY_DATA=<scratch with long/ and multi/bars/> B003_DATA=<dir with coinbase/binance hourly files> python3 -I run_batch.py
"""
import json, math, os, sys, zlib
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import common as C  # noqa: E402

SCR = os.environ.get("DISCOVERY_DATA", C.SCR); B3 = os.environ["B003_DATA"]; RUNS = 1000; SEED = 3003
EARLY_END = pd.Timestamp("2023-01-01", tz="UTC"); LON, CHI = "Europe/London", "America/Chicago"
GRID = {"XAUUSDm": 10.0, "USOILm": 1.0, "EURUSDm": 0.01, "USDJPYm": 1.0, "US500m": 50.0, "BTCUSDm": 1000.0}


def load(m):
    p = os.path.join(SCR, "long" if m in C.LONG else "multi/bars", f"{m}_15m.csv.gz"); d = pd.read_csv(p)
    d["dt"] = pd.to_datetime(d.t, unit="s", utc=True); d = d.set_index("dt").sort_index()
    d["mo"], d["mc"] = (d.bo + d.ao) / 2, (d.bc + d.ac) / 2; d["mh"], d["ml"] = (d.bh + d.ah) / 2, (d.bl + d.al) / 2
    return d


def period(ts):
    return "EARLY" if ts < EARLY_END else C.period_of(ts)


def spread_frac(d):
    return float(((d.ao - d.bo) / d.mo).median())


def net(d, sp, side, i, px_in=None, px_out=None, j=None, t_out=None):
    """Net returns (primary, stress) in bp for a trade entered at candle i's open (or px_in), exited at candle j's open (or px_out)."""
    ein = (d.ao.iat[i] if side > 0 else d.bo.iat[i]) if px_in is None else px_in
    eout = (d.bo.iat[j] if side > 0 else d.ao.iat[j]) if px_out is None else px_out
    g = side * (eout - ein) / ein; t1 = d.index[j] if t_out is None else t_out; days = (t1 - d.index[i]) / pd.Timedelta(days=1)
    return 1e4 * (g - C.slip(sp, "primary")), 1e4 * (g - C.slip(sp, "stress") - C.STRESS_PER_DAY * days)


def bench_p(d, sp, trades, hold_bars, rng, pool_fn=None):  # pool_fn unused (each trade carries its pool)
    """One-sided p of the mean (primary) against RUNS random sets: same count and sides, same hold, random candle opens."""
    if len(trades) < 2: return None
    act = np.mean([t["r"] for t in trades]); n = len(d); tot = np.zeros(RUNS)
    o_a, o_b = d.ao.values, d.bo.values
    for t in trades:                                       # vectorised over the RUNS random sets
        pool = t["pool"]; i = pool[rng.integers(len(pool), size=RUNS)]; j = np.minimum(i + hold_bars, n - 1); s = t["side"]
        ein, eout = (o_a[i], o_b[j]) if s > 0 else (o_b[i], o_a[j]); tot += 1e4 * (s * (eout - ein) / ein - C.slip(sp, "primary"))
    return float((tot / len(trades) >= act).mean())


def summarize(trades, d, sp, rng, hold_bars=None, pool_fn=None, ttest=False):
    out = {}
    for p in ("EARLY", "TRAIN", "VALIDATION", "TEST"):
        sel = [t for t in trades if t["period"] == p]
        if not sel: out[p] = {"trades": 0}; continue
        st = C.stats([t["r"] for t in sel]); st["mean_stress_bp"] = float(np.mean([t["rs"] for t in sel]))
        if ttest:
            r = np.array([t["r"] for t in sel]); tt = r.mean() / (r.std(ddof=1) / math.sqrt(len(r))) if len(r) > 2 else 0.0
            st["p_vs_benchmark"] = float(0.5 * math.erfc(tt / math.sqrt(2))); st["win_pct_target_or_better"] = st.get("win_pct")
        else:
            st["p_vs_benchmark"] = bench_p(d, sp, sel, hold_bars, rng, pool_fn)
        out[p] = st
    return out


# ---------------------------------------------------------------- H1 round numbers
def h1(m, rule):
    d = load(m); sp = spread_frac(d); G = GRID[m]; h, l, c = d.mh.values, d.ml.values, d.mc.values; n = len(d); tr = []; k = 8; idx = d.index
    per = np.array([period(t) for t in idx]); pools = {p: np.flatnonzero(per[:n - 5] == p) for p in ("EARLY", "TRAIN", "VALIDATION", "TEST")}
    while k < n - 5:
        side = 0
        if rule == "R1":
            hi8, lo8 = h[k - 8:k].max(), l[k - 8:k].min()
            Ls = math.floor(h[k] / G) * G; sh = Ls > hi8 and Ls <= h[k] and c[k] < Ls            # nearest level touched from below
            Ll = math.ceil(l[k] / G) * G; lg = Ll < lo8 and Ll >= l[k] and c[k] > Ll            # nearest level touched from above
            side = -1 if (sh and not lg) else (1 if (lg and not sh) else 0)
        else:
            mx, mn = c[k - 8:k].max(), c[k - 8:k].min()
            Lu = math.floor(c[k] / G) * G; up = Lu > mx                                           # crossed up through Lu, closes at/above
            Ld = math.ceil(c[k] / G) * G; dn = Ld < mn                                            # crossed down through Ld, closes at/below
            side = 1 if (up and not dn) else (-1 if (dn and not up) else 0)
        if side:
            i, j = k + 1, k + 5; r, rs = net(d, sp, side, i, j=j); p = period(idx[i])
            if p: tr.append(dict(period=p, side=side, r=r, rs=rs, pool=pools[p]))
            k = j; continue
        k += 1
    return summarize(tr, d, sp, np.random.default_rng(SEED + zlib.crc32(f"{m}|{rule}".encode()) % 1000), hold_bars=4)


# ---------------------------------------------------------------- H2 London fixes
def h2(m, hh, mm):
    d = load(m); sp = spread_frac(d); loc = d.index.tz_convert(LON); pos = {t: i for i, t in enumerate(d.index)}; tr = []
    lmin = loc.hour * 60 + loc.minute; day = loc.normalize()
    by_day = pd.Series(np.arange(len(d)), index=day)
    for dte in day.unique():
        if dte.weekday() >= 5: continue
        a = pd.Timestamp(dte.date()).replace(hour=hh, minute=mm).tz_localize(LON); b = a + pd.Timedelta(minutes=30)
        i, j = pos.get(a.tz_convert("UTC")), pos.get(b.tz_convert("UTC"))
        if i is None or j is None: continue
        sel = by_day.get(dte); sel = np.atleast_1d(sel.values if hasattr(sel, "values") else sel)
        cand = [q for q in sel if 8 * 60 <= lmin[q] <= 16 * 60 + 30 and pos.get(d.index[q] + pd.Timedelta(minutes=30)) is not None]
        r, rs = net(d, sp, -1, i, j=j); p = period(d.index[i])
        if p and cand: tr.append(dict(period=p, side=-1, r=r, rs=rs, pool=np.array(cand)))
    return summarize(tr, d, sp, np.random.default_rng(SEED + hh), hold_bars=2)


# ---------------------------------------------------------------- H3 CME gap
def h3():
    d = load("BTCUSDm"); sp = spread_frac(d); pos = {t: i for i, t in enumerate(d.index)}; tr = []
    loc = lambda day, h, mi: (pd.Timestamp(day) + pd.Timedelta(hours=h, minutes=mi)).tz_localize(CHI).tz_convert("UTC")   # local wall-clock time
    for f in pd.date_range("2019-12-27", "2026-11-06", freq="W-FRI"):
        fc = pos.get(loc(f, 15, 45)); so = pos.get(loc(f + pd.Timedelta(days=2), 17, 0)); nf = pos.get(loc(f + pd.Timedelta(days=7), 16, 0))
        if fc is None or so is None or nf is None: continue
        PF = d.mc.iat[fc]; PS = d.mo.iat[so]; g = PS / PF - 1
        if abs(g) < 0.01: continue
        side = 1 if PF > PS else -1; dist = abs(PF - PS); tgt, stp = PS + side * dist, PS - side * dist; px_out = None; t_out = None
        for q in range(so, nf):
            if side > 0:
                if d.bl.iat[q] <= stp: px_out = stp; break
                if d.bh.iat[q] >= tgt: px_out = tgt; break
            else:
                if d.ah.iat[q] >= stp: px_out = stp; break
                if d.al.iat[q] <= tgt: px_out = tgt; break
        if px_out is None: r, rs = net(d, sp, side, so, j=nf)
        else: r, rs = net(d, sp, side, so, px_out=px_out, j=q, t_out=d.index[q])
        p = period(d.index[so])
        if p: tr.append(dict(period=p, side=side, r=r, rs=rs, gap_pct=round(100 * g, 2), hit=("target" if px_out == tgt else ("stop" if px_out == stp else "time"))))
    out = summarize(tr, d, sp, None, ttest=True)
    for p in out:
        sel = [t for t in tr if t["period"] == p]
        if sel: out[p]["hits"] = {k: sum(t["hit"] == k for t in sel) for k in ("target", "stop", "time")}
    return out


# ---------------------------------------------------------------- H4 Coinbase premium
def h4():
    cb = pd.read_csv(os.path.join(B3, "coinbase_BTCUSD_1h.csv.gz")); bn = pd.read_csv(os.path.join(B3, "binance_BTCUSDT_1h.csv.gz"))
    x = cb.merge(bn, on="t").sort_values("t"); x["prem"] = np.log(x.cb / x.bn)
    mu, sd = x.prem.rolling(720).mean().shift(1), x.prem.rolling(720).std().shift(1); x["z"] = (x.prem - mu) / sd
    x["close"] = pd.to_datetime(x.t + 3600, unit="s", utc=True)
    d = load("BTCUSDm"); sp = spread_frac(d); idx = d.index; per = np.array([period(t) for t in idx]); n = len(d)
    pools = {p: np.flatnonzero(per[:n - 97] == p) for p in ("EARLY", "TRAIN", "VALIDATION", "TEST")}; tr = []; free = idx[0]
    for _, row in x[x.z.abs() >= 2].iterrows():
        if row.close < free: continue
        i = int(idx.searchsorted(row.close));
        if i >= n: break
        j = int(idx.searchsorted(idx[i] + pd.Timedelta(hours=24)))
        if j >= n: break
        side = 1 if row.z > 0 else -1; r, rs = net(d, sp, side, i, j=j); p = period(idx[i]); free = idx[j]
        if p: tr.append(dict(period=p, side=side, r=r, rs=rs, pool=pools[p]))
    return summarize(tr, d, sp, np.random.default_rng(SEED + 4), hold_bars=96)


def main():
    R = {}
    for m in GRID:
        for rule in ("R1", "R2"):
            R[f"H1-{rule}|{m}"] = h1(m, rule); print(f"H1-{rule}|{m}", {p: (v.get('trades'), round(v.get('mean_bp', float('nan')), 2)) for p, v in R[f"H1-{rule}|{m}"].items()}, flush=True)
    R["H2|XAUUSDm"] = h2("XAUUSDm", 14, 45); R["H2|XAGUSDm"] = h2("XAGUSDm", 11, 45)
    R["H3|BTCUSDm"] = h3(); R["H4|BTCUSDm"] = h4()
    for k in ("H2|XAUUSDm", "H2|XAGUSDm", "H3|BTCUSDm", "H4|BTCUSDm"):
        print(k, {p: (v.get('trades'), round(v.get('mean_bp', float('nan')), 2)) for p, v in R[k].items()}, flush=True)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(R, open(os.path.join(HERE, "results", "batch_003.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
