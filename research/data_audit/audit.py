"""Data integrity audit of every price source used in this repository, against independent public sources (2025+ only).

Sources checked:
  Exness 1-minute bars built from ticks (all backtests)       -> internal checks + cross-check against independent closes
  Binance BTC/ETH klines (trend bot, Donchian, library)       -> Coinbase and Kraken daily closes
  Hyperliquid xyz:GOLD / xyz:CL (forward tests)               -> Exness and the independent references, on overlapping days
Independent references: FRED (WTI spot DCOILWTICO, Brent DCOILBRENTEU, SP500, NASDAQ100), Kraken PAXGUSD and Binance
PAXGUSDT (gold tokens), Coinbase BTC-USD / ETH-USD, Kraken XBTUSD / ETHUSD.

Usage: BARS_DIR=<orb 1m bars> python3 -I audit.py
"""
import datetime as dt, io, json, os, ssl, time, urllib.request
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); BARS = os.environ["BARS_DIR"]
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
NY, BER = ZoneInfo("America/New_York"), ZoneInfo("Europe/Berlin"); START = "2025-01-01"


def get(url, data=None, headers=None):
    for k in range(4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "curl/8.5.0", "Accept": "*/*"})
            return urllib.request.urlopen(req, timeout=40, context=CTX).read()
        except Exception:
            if k == 3: raise
            time.sleep(2 ** (k + 1))


# ------------------------------------------------------------------ references
def fred(series):
    d = pd.read_csv(io.BytesIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={START}")))
    d.columns = ["date", "v"]; d["v"] = pd.to_numeric(d.v, errors="coerce"); return d.dropna().set_index("date").v


def kraken(pair):
    r = json.loads(get(f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval=1440&since=1735689600"))["result"]; k = [x for x in r if x != "last"][0]
    return pd.Series({time.strftime("%Y-%m-%d", time.gmtime(x[0])): float(x[4]) for x in r[k]})


def coinbase(prod):
    out = {}; t = pd.Timestamp(START, tz="UTC"); stop_at = pd.Timestamp.now(tz="UTC").floor("D")   # fixed end, so the loop always ends
    while t < stop_at:
        e = min(t + pd.Timedelta(days=299), stop_at)
        r = json.loads(get(f"https://api.exchange.coinbase.com/products/{prod}/candles?granularity=86400&start={t.isoformat()}&end={e.isoformat()}"))
        for x in r: out[time.strftime("%Y-%m-%d", time.gmtime(x[0]))] = float(x[4])
        t = e
    return pd.Series(out).sort_index()


def binance_daily(sym):
    rows, t = [], 1735689600000
    while True:
        r = json.loads(get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1d&startTime={t}&limit=1000"))
        if not r: break
        rows += r; t = r[-1][0] + 1
        if len(r) < 1000: break
    return pd.Series({time.strftime("%Y-%m-%d", time.gmtime(x[0] / 1000)): float(x[4]) for x in rows if x[6] < time.time() * 1000})


def hyperliquid_daily(coin):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1d", "startTime": 1735689600000, "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(get("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}))
    return pd.Series({time.strftime("%Y-%m-%d", time.gmtime(x["t"] / 1000)): float(x["c"]) for x in r if x["T"] < time.time() * 1000})


# ------------------------------------------------------------------ Exness internal checks
def exness(sym):
    z = np.load(os.path.join(BARS, f"{sym}_1m.npz")); m, o, h, l, c, sp = z["m"], z["o"], z["h"], z["l"], z["c"], z["sp"]
    out = dict(bars=int(len(m)), first=str(pd.Timestamp(m[0] * 60, unit="s")), last=str(pd.Timestamp(m[-1] * 60, unit="s")),
               duplicate_minutes=int((np.diff(m) == 0).sum()), unsorted=int((np.diff(m) < 0).sum()), nonpositive=int(((o <= 0) | (l <= 0)).sum()),
               high_below_low=int((h < l).sum()), open_or_close_outside_range=int(((o > h + 1e-9) | (o < l - 1e-9) | (c > h + 1e-9) | (c < l - 1e-9)).sum()),
               negative_spread=int((sp < 0).sum()), spread_median=round(float(np.median(sp)), 5), spread_p99=round(float(np.percentile(sp, 99)), 5), spread_max=round(float(sp.max()), 4))
    r = np.diff(np.log(c)); sd = pd.Series(r).rolling(1440, min_periods=200).std().values; jump = np.abs(r) > np.maximum(12 * np.nan_to_num(sd, nan=1), 0.01)
    big = np.flatnonzero(jump)
    out["one_minute_jumps_over_12sd_and_1pct"] = int(len(big))
    out["largest_jumps"] = [dict(utc=str(pd.Timestamp(m[i + 1] * 60, unit="s")), ret_pct=round(float(r[i] * 100), 2)) for i in big[np.argsort(-np.abs(r[big]))][:5]]
    g = np.diff(m); wk = pd.to_datetime(m[1:] * 60, unit="s").weekday.values
    gaps = np.flatnonzero((g > 180) & (wk < 5))
    out["weekday_gaps_over_3h"] = int(len(gaps))
    out["largest_weekday_gaps"] = [dict(after_utc=str(pd.Timestamp(m[i] * 60, unit="s")), hours=round(float(g[i] / 60), 1)) for i in gaps[np.argsort(-g[gaps])][:5]]
    mon = pd.to_datetime(m * 60, unit="s").to_period("M"); cnt = pd.Series(1, index=mon).groupby(level=0).sum()
    out["bars_per_month_min_max"] = [int(cnt.min()), int(cnt.max())]; out["months"] = int(len(cnt))
    return out, m, c


def close_at(m, c, local_dates, tz, hh, mm):
    """Last bar close at or before local hh:mm on each date (within 10 minutes)."""
    out = {}
    for d in local_dates:
        t = int(dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz).timestamp() // 60); i = int(np.searchsorted(m, t, side="right")) - 1
        if i >= 0 and t - m[i] <= 10: out[str(d)] = float(c[i])
    return pd.Series(out)


def compare(a, b, name_a, name_b):
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    if len(j) < 10: return dict(days=int(len(j)), note="too few overlapping days")
    diff = (j.a / j.b - 1) * 100; ra, rb = np.log(j.a).diff().dropna(), np.log(j.b).diff().dropna()
    worst = diff.abs().sort_values(ascending=False).head(5)
    return dict(pair=f"{name_a} vs {name_b}", days=int(len(j)), level_diff_pct_median=round(float(diff.median()), 3), level_diff_pct_abs_p95=round(float(diff.abs().quantile(0.95)), 3),
                level_diff_pct_abs_max=round(float(diff.abs().max()), 3), daily_return_correlation=round(float(ra.corr(rb)), 4),
                days_level_diff_over_2pct=int((diff.abs() > 2).sum()), worst_days={k: round(float(v), 2) for k, v in worst.items()},
                first_last=dict(a=[round(float(j.a.iloc[0]), 2), round(float(j.a.iloc[-1]), 2)], b=[round(float(j.b.iloc[0]), 2), round(float(j.b.iloc[-1]), 2)]))


def main():
    t0 = time.time(); R = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), exness={}, cross={})
    dates = [d.date() for d in pd.date_range(START, "2026-10-31", freq="B")]
    ref = dict(wti=fred("DCOILWTICO"), brent=fred("DCOILBRENTEU"), spx=fred("SP500"), ndx=fred("NASDAQ100"), paxg_kraken=kraken("PAXGUSD"), paxg_binance=binance_daily("PAXGUSDT"))
    print("references loaded", {k: len(v) for k, v in ref.items()}, f"{time.time() - t0:.0f}s", flush=True)
    for sym in ("XAUUSDm", "USOILm", "DE30m", "US500m", "USTECm"):
        R["exness"][sym], m, c = exness(sym); print(sym, R["exness"][sym], flush=True)
        if sym == "XAUUSDm":
            R["cross"]["XAUUSDm_vs_PAXG_kraken"] = compare(close_at(m, c, dates, dt.timezone.utc, 23, 59), ref["paxg_kraken"], "Exness gold 23:59 UTC", "Kraken PAXG daily close")
            R["cross"]["XAUUSDm_vs_PAXG_binance"] = compare(close_at(m, c, dates, dt.timezone.utc, 23, 59), ref["paxg_binance"], "Exness gold 23:59 UTC", "Binance PAXG daily close")
        if sym == "USOILm":
            R["cross"]["USOILm_vs_FRED_WTI"] = compare(close_at(m, c, dates, NY, 14, 30), ref["wti"], "Exness USOIL 14:30 NY", "FRED WTI spot")
            R["cross"]["USOILm_vs_FRED_Brent"] = compare(close_at(m, c, dates, NY, 14, 30), ref["brent"], "Exness USOIL 14:30 NY", "FRED Brent spot")
        if sym == "US500m": R["cross"]["US500m_vs_FRED_SP500"] = compare(close_at(m, c, dates, NY, 16, 0), ref["spx"], "Exness US500 16:00 NY", "FRED S&P 500 close")
        if sym == "USTECm": R["cross"]["USTECm_vs_FRED_NASDAQ100"] = compare(close_at(m, c, dates, NY, 16, 0), ref["ndx"], "Exness USTEC 16:00 NY", "FRED Nasdaq-100 close")
    for sym, cb, kr in (("BTCUSDT", "BTC-USD", "XBTUSD"), ("ETHUSDT", "ETH-USD", "ETHUSD")):
        b = pd.read_csv(os.path.join(ROOT, "daily_signal_dca", "from_2025", "data", f"{sym}_1d_from2025.csv.gz")); bs = pd.Series(b.c.values, index=pd.to_datetime(b.t, unit="ms").dt.strftime("%Y-%m-%d"))
        R["cross"][f"{sym}_vs_coinbase"] = compare(bs, coinbase(cb), f"Binance {sym} (repo file)", f"Coinbase {cb}")
        R["cross"][f"{sym}_vs_kraken"] = compare(bs, kraken(kr), f"Binance {sym} (repo file)", f"Kraken {kr}")
        R["cross"][f"{sym}_repo_vs_live_binance"] = compare(bs, binance_daily(sym), f"Binance {sym} (repo file)", "Binance live API")
    for coin, refs in (("xyz:GOLD", [("paxg_kraken", "Kraken PAXG")]), ("xyz:CL", [("wti", "FRED WTI spot"), ("brent", "FRED Brent spot")])):
        hl = hyperliquid_daily(coin)
        for k, nm in refs: R["cross"][f"{coin}_vs_{k}"] = compare(hl, ref[k], f"Hyperliquid {coin} daily", nm)
    R["cross"]["FRED_WTI_vs_Brent"] = compare(ref["wti"], ref["brent"], "FRED WTI", "FRED Brent")
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(R, open(os.path.join(HERE, "results", "audit.json"), "w"), indent=1, default=str)
    for k, v in R["cross"].items(): print(k, v, flush=True)
    print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
