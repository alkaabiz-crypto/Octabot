"""Oil reconciliation: which benchmark do Exness USOILm and Hyperliquid xyz:CL track? 2025+ only.

Benchmarks: NYMEX WTI front-month futures CL=F and ICE Brent front-month futures BZ=F (Yahoo Finance daily, saved in
data/yahoo_*.json; EIA stopped publishing NYMEX futures prices in April 2024, so it cannot be used for 2025+), FRED WTI spot
(DCOILWTICO, = EIA RWTC), FRED Brent spot (DCOILBRENTEU). Hyperliquid xyz:BRENTOIL is compared with Brent for the WTI/Brent check.
Level differences and return correlations are reported separately.

Usage: BARS_DIR=<orb 1m bars> python3 -I oil_reconciliation.py
"""
import datetime as dt, io, json, os, ssl, time, urllib.request
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); NY = ZoneInfo("America/New_York")
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA)


def get(url, data=None, h=None):
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h or {"User-Agent": "curl/8.5.0"}), timeout=40, context=CTX).read()


def eia_cl1(path):
    """EIA weekly-row HTML table (Week Of, Mon..Fri). Returns daily settlement series from 2025-01-01."""
    t = [x for x in pd.read_html(path) if x.shape[1] >= 6][0]; t.columns = ["week", "Mon", "Tue", "Wed", "Thu", "Fri"] + list(t.columns[6:])
    out = {}
    for _, r in t.iterrows():
        try: start = pd.to_datetime(str(r["week"]).split(" to ")[0].replace("- ", "-").strip(), format="%Y %b-%d")
        except Exception: continue
        for k, d in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri")):
            v = pd.to_numeric(r[d], errors="coerce")
            if pd.notna(v): out[(start + pd.Timedelta(days=k)).strftime("%Y-%m-%d")] = float(v)
    s = pd.Series(out).sort_index(); return s[s.index >= "2025-01-01"]


def yahoo(path):
    r = json.load(open(path))["chart"]["result"][0]; ts = r["timestamp"]; cl = r["indicators"]["quote"][0]["close"]
    tz = ZoneInfo(r["meta"]["exchangeTimezoneName"])
    s = pd.Series({dt.datetime.fromtimestamp(t, tz).strftime("%Y-%m-%d"): v for t, v in zip(ts, cl) if v is not None}).sort_index()
    return s[s.index >= "2025-01-01"], r["meta"]


def fred(sid):
    d = pd.read_csv(io.BytesIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=2025-01-01"))); d.columns = ["date", "v"]
    d["v"] = pd.to_numeric(d.v, errors="coerce"); return d.dropna().set_index("date").v


def hl_1h(coin):
    b = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": 1735689600000, "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(get("https://api.hyperliquid.xyz/info", data=b, h={"Content-Type": "application/json"}))
    return pd.Series({int(x["t"]) // 60000: float(x["o"]) for x in r})        # open of each hour = price at that minute


def at_ny(series_by_minute, dates, hh, mm, tol=10):
    idx = series_by_minute.index.values; out = {}
    for d in dates:
        t = int(dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=NY).timestamp() // 60); i = int(np.searchsorted(idx, t, side="right")) - 1
        if i >= 0 and t - idx[i] <= tol: out[str(d)] = float(series_by_minute.iloc[i])
    return pd.Series(out)


def cmp(a, b):
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    if len(j) < 10: return dict(days=int(len(j)))
    d = (j.a / j.b - 1) * 100; ra, rb = np.log(j.a).diff(), np.log(j.b).diff()
    return dict(days=int(len(j)), level_diff_pct=dict(median=round(float(d.median()), 3), p05=round(float(d.quantile(0.05)), 3), p95=round(float(d.quantile(0.95)), 3),
                abs_max=round(float(d.abs().max()), 3), share_abs_over_2pct=round(float((d.abs() > 2).mean()), 3)),
                daily_return_corr=round(float(ra.corr(rb)), 4), daily_return_tracking_error_pct=round(float((ra - rb).std() * 100), 3),
                monthly_median_level_diff_pct={str(k): round(float(v), 2) for k, v in d.groupby(pd.to_datetime(j.index).to_period("M")).median().items()})


def main():
    z = np.load(os.path.join(os.environ["BARS_DIR"], "USOILm_1m.npz")); ex = pd.Series(z["c"], index=z["m"])
    dates = [d.date() for d in pd.date_range("2025-01-01", "2026-10-31", freq="B")]
    (cl1, m_cl), (bz1, m_bz) = yahoo(os.path.join(HERE, "data", "yahoo_CL=F_daily.json")), yahoo(os.path.join(HERE, "data", "yahoo_BZ=F_daily.json"))
    wti, brent = fred("DCOILWTICO"), fred("DCOILBRENTEU")
    ex1430 = at_ny(ex, dates, 14, 30); hl = hl_1h("xyz:CL"); hlb = hl_1h("xyz:BRENTOIL")
    hd = [d.date() for d in pd.date_range("2026-01-01", time.strftime("%Y-%m-%d"), freq="B")]
    hl1430 = at_ny(hl, hd, 15, 0, tol=1)          # hourly open at 15:00 New York = price at 15:00 (settlement is 14:30)
    hlb1430 = at_ny(hlb, hd, 15, 0, tol=1)
    ex1700 = at_ny(ex, dates, 16, 59)
    R = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()),
             sources=dict(CL_F=f"{m_cl.get('symbol')} {m_cl.get('fullExchangeName')} {m_cl.get('instrumentType')}, {len(cl1)} days {cl1.index[0]}..{cl1.index[-1]}",
                          BZ_F=f"{m_bz.get('symbol')} {m_bz.get('fullExchangeName')} {m_bz.get('instrumentType')}, {len(bz1)} days", FRED_WTI_spot=f"{len(wti)} days", FRED_Brent_spot=f"{len(brent)} days"),
             exness_1430_vs_WTI_front_month_CL_F=cmp(ex1430, cl1), exness_1659_vs_WTI_front_month_CL_F=cmp(ex1700, cl1),
             exness_1430_vs_Brent_front_month_BZ_F=cmp(ex1430, bz1), exness_1430_vs_FRED_WTI_spot=cmp(ex1430, wti), exness_1430_vs_FRED_Brent_spot=cmp(ex1430, brent),
             hyperliquid_CL_vs_WTI_front_month_CL_F=cmp(hl1430, cl1), hyperliquid_CL_vs_Brent_front_month_BZ_F=cmp(hl1430, bz1), hyperliquid_CL_vs_FRED_WTI_spot=cmp(hl1430, wti),
             hyperliquid_BRENTOIL_vs_Brent_front_month_BZ_F=cmp(hlb1430, bz1), WTI_front_month_vs_FRED_WTI_spot=cmp(cl1, wti),
             WTI_front_month_vs_Brent_front_month=cmp(cl1, bz1), FRED_WTI_vs_Brent_spot=cmp(wti, brent))
    # roll check: Exness minus front month around the CL expiry (last ~5 business days before the 25th) vs mid-month
    j = pd.concat([ex1430, cl1], axis=1, keys=["ex", "cl"]).dropna(); dd = (j.ex / j.cl - 1) * 100; day = pd.to_datetime(j.index).day
    R["exness_minus_front_month_by_day_of_month_pct"] = {"days_1_10": round(float(dd[day <= 10].median()), 3), "days_11_19": round(float(dd[(day > 10) & (day < 20)].median()), 3),
                                                         "days_20_31": round(float(dd[day >= 20].median()), 3)}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(R, open(os.path.join(HERE, "results", "oil_reconciliation.json"), "w"), indent=1)
    for k, v in R.items():
        if isinstance(v, dict) and "monthly_median_level_diff_pct" in v: v = {kk: vv for kk, vv in v.items() if kk != "monthly_median_level_diff_pct"}
        print(k, v)


if __name__ == "__main__":
    main()
