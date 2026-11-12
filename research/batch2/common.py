"""Batch 2 shared code: data fetchers (cached in scratch, never committed), signals H1-H4 and trade simulation.
Implements PREREGISTRATION.md exactly. Used unchanged by dev.py (DEVELOPMENT) and forward.py (FORWARD).
"""
import datetime as dt, hashlib, json, os, ssl, time, urllib.request, zlib
import numpy as np
import pandas as pd

CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
START_MS = 1735689600000                      # 2025-01-01 00:00 UTC (user rule)
T0_MS = 1794510631000                          # 2026-11-12 19:10:31 UTC, pre-registration commit 33777e0a
E_MS = 1794614400000                           # 2026-11-14 00:00 UTC, forward start
H, D, M = 3_600_000, 86_400_000, 60_000
COINS = ("BTC", "ETH")
SPREAD_BP = {"BTC": 0.79, "ETH": 4.13}
COST = {"primary": (1.5, 0.0003), "stress": (3.0, 0.0008)}   # (x spread round trip, financing per day)
TESTS = [f"{h}_{c}" for h in ("H1", "H2", "H3", "H4") for c in COINS]
HOLD = {"H1": 72 * H, "H2": 7 * D, "H3": 4 * H, "H4": 7 * D}


def get(url, data=None, headers=None, tries=5):
    for k in range(tries):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "curl/8.5.0"}), timeout=60, context=CTX).read())
        except Exception:
            if k == tries - 1: raise
            time.sleep(2 ** (k + 1))


# ------------------------------------------------------------------ fetchers (end_ms exclusive; only closed data)
def binance_klines(sym, iv, start_ms, end_ms):
    rows, t = [], int(start_ms); step = {"1m": M, "1h": H}[iv]
    while t < end_ms:
        r = get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={iv}&startTime={t}&endTime={int(end_ms) - 1}&limit=1000")
        if not r: break
        rows += r; t = r[-1][0] + step
        if len(r) < 1000: break
    d = pd.DataFrame([dict(t=int(x[0]), o=float(x[1]), h=float(x[2]), l=float(x[3]), c=float(x[4]), v=float(x[5]), close_ms=int(x[6]) + 1, tbv=float(x[9])) for x in rows])
    return d[(d.t >= start_ms) & (d.close_ms <= end_ms)].drop_duplicates("t").reset_index(drop=True) if len(d) else d


def hl_funding(coin, start_ms, end_ms):
    rows, t = [], int(start_ms)
    while t < end_ms:
        r = get("https://api.hyperliquid.xyz/info", data=json.dumps({"type": "fundingHistory", "coin": coin, "startTime": t, "endTime": int(end_ms) - 1}).encode(),
                headers={"Content-Type": "application/json"})
        if not r: break
        rows += r; nt = int(r[-1]["time"]) + 1
        if nt <= t: break
        t = nt
        if len(r) < 500: break
    d = pd.DataFrame([dict(t=int(x["time"]), rate=float(x["fundingRate"])) for x in rows])
    return d[(d.t >= start_ms) & (d.t < end_ms)].drop_duplicates("t").sort_values("t").reset_index(drop=True) if len(d) else d


def deribit_chart(instrument, start_ms, end_ms):
    out = {}; t = int(start_ms)
    while t < end_ms:
        e = min(t + 30 * D, int(end_ms))
        r = get(f"https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name={instrument}&start_timestamp={t}&end_timestamp={e}&resolution=60")["result"]
        if r.get("status") == "ok":
            for ts, c in zip(r["ticks"], r["close"]): out[int(ts)] = float(c)
        t = e
    s = pd.Series(out).sort_index(); return s[(s.index >= start_ms) & (s.index + H <= end_ms)]   # hourly bar start -> close


def deribit_dvol(coin, start_ms, end_ms):
    out = {}; t = int(start_ms)
    while t < end_ms:
        e = min(t + 40 * D, int(end_ms))
        r = get(f"https://www.deribit.com/api/v2/public/get_volatility_index_data?currency={coin}&start_timestamp={t}&end_timestamp={e}&resolution=3600")["result"]
        for x in r["data"]: out[int(x[0])] = float(x[4])
        t = e
    s = pd.Series(out).sort_index(); return s[(s.index >= start_ms) & (s.index + H <= end_ms)]


def deribit_quarterlies(coin):
    inst = []
    for exp in ("true", "false"):
        r = get(f"https://www.deribit.com/api/v2/public/get_instruments?currency={coin}&kind=future&expired={exp}")["result"]
        for x in r:
            ex = dt.datetime.fromtimestamp(x["expiration_timestamp"] / 1000, dt.timezone.utc)
            if x.get("settlement_period") == "month" and ex.month in (3, 6, 9, 12) and x["expiration_timestamp"] >= START_MS:
                inst.append((x["instrument_name"], int(x["expiration_timestamp"]), int(x["creation_timestamp"])))
    return sorted(set(inst), key=lambda z: z[1])


# ------------------------------------------------------------------ signals: list of (decision_ms, side, info) per test
def zscore_prev(vals, n):
    """z of each value against the previous n values (excluding itself); NaN until n are available."""
    s = pd.Series(vals); m = s.shift(1).rolling(n).mean(); sd = s.shift(1).rolling(n).std()
    return ((s - m) / sd).values


def h1_signals(fund):
    if fund.empty: return []
    t0 = (fund.t.min() // D + 1) * D; days = np.arange(t0, fund.t.max() + 1, D)
    tv, rv = fund.t.values, fund.rate.values; F = []
    for d0 in days:
        m = (tv > d0 - D) & (tv <= d0); F.append(rv[m].sum() if m.sum() >= 20 else np.nan)
    z = zscore_prev(F, 90); return [(int(d0), -1 if zz >= 2 else 1, dict(F=float(f), z=round(float(zz), 3))) for d0, f, zz in zip(days, F, z) if not np.isnan(zz) and abs(zz) >= 2]


def h2_signals(fut_series, spot1h):
    """fut_series: list of (name, expiry_ms, hourly close Series keyed by bar start). Monday 00:00 UTC decisions."""
    sc = dict(zip(spot1h.close_ms.values, spot1h.c.values)); rows = []
    mondays = [int(x.value // 1_000_000) for x in pd.date_range(pd.Timestamp(START_MS, unit="ms", tz="UTC"), pd.Timestamp(spot1h.close_ms.max(), unit="ms", tz="UTC"), freq="W-MON")]
    for d0 in mondays:
        elig = [(n, e, s) for n, e, s in fut_series if e - d0 >= 30 * D and (d0 - H) in s.index]
        if not elig or d0 not in sc: rows.append((d0, np.nan, None)); continue
        n, e, s = min(elig, key=lambda z: z[1]); F, S = s[d0 - H], sc[d0]
        rows.append((d0, (F / S - 1) * 365 * D / (e - d0), n))
    out = []
    b = [r[1] for r in rows]
    for k, (d0, bb, n) in enumerate(rows):
        prev = [x for x in b[max(0, k - 26):k] if not np.isnan(x)]
        if np.isnan(bb) or k < 26 or len(prev) < 26: continue
        p = float(np.mean(np.array(prev) < bb))
        if p >= 0.8 or p <= 0.2: out.append((d0, -1 if p >= 0.8 else 1, dict(basis_ann=round(float(bb), 5), pct=round(p, 3), future=n)))
    return out


def h3_signals(spot1h):
    v = spot1h.v.values; I = np.where(v > 0, (2 * spot1h.tbv.values - v) / np.where(v > 0, v, 1), np.nan); z = zscore_prev(I, 720)
    return [(int(cm), 1 if zz >= 2 else -1, dict(I=round(float(i), 4), z=round(float(zz), 3))) for cm, i, zz in zip(spot1h.close_ms.values, I, z) if not np.isnan(zz) and abs(zz) >= 2]


def h4_signals(dvol, spot1h):
    sc = dict(zip(spot1h.close_ms.values, spot1h.c.values)); t0 = (spot1h.close_ms.min() // D + 1) * D
    days = np.arange(t0, spot1h.close_ms.max() + 1, D); rows = []
    for d0 in days:
        cl = [sc.get(int(d0 - k * D)) for k in range(31)]
        if any(x is None for x in cl) or (d0 - H) not in dvol.index: rows.append((d0, np.nan)); continue
        r = np.diff(np.log(np.array(cl[::-1]))); rv = float(np.std(r, ddof=1) * np.sqrt(365) * 100); rows.append((d0, dvol[d0 - H] - rv))
    z = zscore_prev([x[1] for x in rows], 180)
    return [(int(d0), 1 if zz >= 1 else -1, dict(vrp=round(float(v), 3), z=round(float(zz), 3))) for (d0, v), zz in zip(rows, z) if not np.isnan(zz) and abs(zz) >= 1]


# ------------------------------------------------------------------ trades
def simulate(signals, hold, m1, start_ms, end_ms):
    """One position at a time. Entry: open of first 1m candle >= D + 1 min; exit: open of first 1m candle >= entry decision + hold."""
    t, o = m1.t.values, m1.o.values; out = []; free = -1
    for d0, side, info in sorted(signals, key=lambda z: z[0]):
        if d0 < start_ms or d0 >= end_ms or d0 < free: continue
        i = int(np.searchsorted(t, d0 + M)); j = int(np.searchsorted(t, d0 + M + hold))
        if i >= len(t) or j >= len(t) or t[j] > end_ms: continue
        out.append(dict(decision_ms=int(d0), side=int(side), entry_ms=int(t[i]), entry=float(o[i]), exit_ms=int(t[j]), exit=float(o[j]), **{k: v for k, v in info.items()}))
        free = int(t[j])
    return out


def net(tr, coin, which):
    k, fin = COST[which]
    gross = tr["side"] * (tr["exit"] / tr["entry"] - 1); days = (tr["exit_ms"] - tr["entry_ms"]) / D
    return gross - k * SPREAD_BP[coin] / 1e4 - fin * days


def summarize(trs, coin, which="primary"):
    if not trs: return dict(trades=0)
    r = np.array([net(x, coin, which) for x in trs]); eq = np.cumprod(1 + r)
    se = r.std(ddof=1) / np.sqrt(len(r)) if len(r) > 1 else np.nan; gp, gl = r[r > 0].sum(), -r[r < 0].sum()
    return dict(trades=int(len(r)), mean_bp=round(float(r.mean() * 1e4), 2), median_bp=round(float(np.median(r) * 1e4), 2),
                ci95_bp=[round(float((r.mean() - 1.96 * se) * 1e4), 2), round(float((r.mean() + 1.96 * se) * 1e4), 2)] if len(r) > 1 else None,
                sd_bp=round(float(r.std(ddof=1) * 1e4), 2) if len(r) > 1 else None, win_rate=round(float((r > 0).mean()), 3),
                profit_factor=round(float(gp / gl), 3) if gl > 0 else None, sum_pct=round(float(r.sum() * 100), 2), compounded_pct=round(float((eq[-1] - 1) * 100), 2),
                max_dd_pct=round(float((eq / np.maximum.accumulate(eq) - 1).min() * 100), 2))


def schedule(hid, m1, start_ms, end_ms):
    """Eligible decision times for B1: hourly (H3), daily 00:00 (H1, H4), Monday 00:00 (H2)."""
    a = (start_ms // H + 1) * H; hrs = np.arange(a, end_ms, H)
    if hid == "H3": return hrs
    days = hrs[hrs % D == 0]
    return days if hid != "H2" else days[pd.to_datetime(days, unit="ms").weekday == 0]


def bench_random(trs, hid, coin, m1, start_ms, end_ms, seed, draws=1000):
    """B1: same sides and holding times, random eligible start times in the same period (overlaps allowed)."""
    if not trs: return None
    rng = np.random.default_rng(seed); sch = schedule(hid, m1, start_ms, end_ms - HOLD[hid] - 2 * M); t, o = m1.t.values, m1.o.values
    sides = np.array([x["side"] for x in trs]); means = np.empty(draws)
    for k in range(draws):
        d0 = rng.choice(sch, size=len(trs)); i = np.searchsorted(t, d0 + M); j = np.searchsorted(t, d0 + M + HOLD[hid])
        ok = (i < len(t)) & (j < len(t)); i, j, s = i[ok], j[ok], sides[ok]
        tr = dict(side=s, entry=o[i], exit=o[j], entry_ms=t[i], exit_ms=t[j]); means[k] = net(tr, coin, "primary").mean()
    return means


def test_seed(test_id):
    return 20261113 + zlib.crc32(test_id.encode()) % 100000


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


STEP = {"H1": D, "H2": 7 * D, "H3": H, "H4": D}


def bench_placebo(raw_signals, hid, coin, m1, start_ms, end_ms, seed, draws=1000):
    """B2: shift the whole signal series by a random offset >= 30 days (multiple of the decision step), wrapping within the
    period, then re-apply the one-position rule and execution. Returns the mean net (primary) per draw."""
    sig = [s for s in raw_signals if start_ms <= s[0] < end_ms]
    if not sig: return None
    rng = np.random.default_rng(seed + 1); span = end_ms - start_ms; step = STEP[hid]; out = []
    lo = int(np.ceil(30 * D / step)); hi = max(lo + 1, int(span // step) - lo)
    for _ in range(draws):
        off = int(rng.integers(lo, hi)) * step
        sh = [(start_ms + (d0 - start_ms + off) % span, sd, info) for d0, sd, info in sig]
        tr = simulate(sh, HOLD[hid], m1, start_ms, end_ms)
        out.append(np.mean([net(x, coin, "primary") for x in tr]) if tr else np.nan)
    return np.array(out)


def pval(observed, draws):
    d = draws[~np.isnan(draws)]
    return round(float((1 + (d >= observed).sum()) / (1 + len(d))), 4) if len(d) else None
