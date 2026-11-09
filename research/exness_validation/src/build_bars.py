"""Build 15-minute bid/ask candles from Exness BTCUSDm tick history (no synthetic data).

Source: https://ticks.ex2archive.com/ticks/BTCUSDm/YYYY/MM/Exness_BTCUSDm_YYYY_MM.zip
This is the public Exness tick-history archive. Each CSV row is "exness","BTCUSDm",timestamp in UTC,bid,ask.

For each month, the script:
  - downloads the zip and records its SHA256, size and tick count in data/manifest.csv;
  - writes data/bars15m/BTCUSDm_YYYY_MM.csv.gz with these columns:
      open_time_utc (unix seconds), bid OHLC, ask OHLC, ticks,
      spread_open, spread_mean, spread_max (spread = ask - bid);
  - deletes the zip afterwards (it can be re-downloaded and checked against the recorded SHA256).

Candles are only formed from ticks that exist. A 15-minute period with no ticks produces no candle, and gaps are
reported later, never filled.
Usage: python build_bars.py 2019-01 2026-10
"""
import csv, gzip, hashlib, io, os, ssl, sys, time, urllib.request, zipfile
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "bars15m"); os.makedirs(OUT, exist_ok=True)
MANIFEST = os.path.join(ROOT, "data", "manifest.csv")
TMP = os.environ.get("EXNESS_TMP", "/tmp")
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()


def months(a, b):
    y, m = map(int, a.split("-")); y2, m2 = map(int, b.split("-"))
    while (y, m) <= (y2, m2):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def done():
    return {r["month"] for r in csv.DictReader(open(MANIFEST))} if os.path.exists(MANIFEST) else set()


def process(y, m):
    name = f"Exness_BTCUSDm_{y}_{m:02d}"
    url = f"https://ticks.ex2archive.com/ticks/BTCUSDm/{y}/{m:02d}/{name}.zip"
    path = os.path.join(TMP, name + ".zip")
    for a in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120, context=ctx) as r, open(path, "wb") as f:
                while chunk := r.read(1 << 20): f.write(chunk)
            break
        except Exception as e:
            err = e; time.sleep(2 ** a * 3)
    else:
        raise SystemExit(f"download failed {url}: {err}")
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest(); size = os.path.getsize(path)
    with zipfile.ZipFile(path) as z:
        inner = z.namelist()[0]
        df = pd.read_csv(z.open(inner), usecols=["Symbol", "Timestamp", "Bid", "Ask"])
    if set(df["Symbol"].unique()) != {"BTCUSDm"}:
        raise SystemExit(f"unexpected symbols in {name}: {df['Symbol'].unique()[:5]}")
    df["t"] = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
    df = df.sort_values("t", kind="stable")
    bad = int(((df["Ask"] < df["Bid"]) | (df["Bid"] <= 0)).sum())
    df["spr"] = df["Ask"] - df["Bid"]
    g = df.groupby(df["t"].dt.floor("15min"))
    bars = pd.DataFrame({
        "bid_o": g["Bid"].first(), "bid_h": g["Bid"].max(), "bid_l": g["Bid"].min(), "bid_c": g["Bid"].last(),
        "ask_o": g["Ask"].first(), "ask_h": g["Ask"].max(), "ask_l": g["Ask"].min(), "ask_c": g["Ask"].last(),
        "ticks": g.size(), "spread_open": g["spr"].first(), "spread_mean": g["spr"].mean(), "spread_max": g["spr"].max()})
    bars.index = ((bars.index - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(seconds=1)).astype("int64")  # unit-independent
    bars.index.name = "open_time_utc"
    buf = io.StringIO(); bars.round(5).to_csv(buf)
    with gzip.open(os.path.join(OUT, f"BTCUSDm_{y}_{m:02d}.csv.gz"), "wt") as f: f.write(buf.getvalue())
    os.remove(path)
    row = dict(month=f"{y}-{m:02d}", url=url, zip_sha256=sha, zip_bytes=size, csv_name=inner, ticks=len(df), bad_ticks=bad,
               bars15m=len(bars), first_tick=str(df["t"].iloc[0]), last_tick=str(df["t"].iloc[-1]),
               median_spread=round(float(df["spr"].median()), 4), median_spread_pct=round(float((df["spr"] / df["Bid"]).median() * 100), 5))
    new = not os.path.exists(MANIFEST)
    with open(MANIFEST, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new: w.writeheader()
        w.writerow(row)
    print(row["month"], row["ticks"], "ticks", row["bars15m"], "bars, median spread", row["median_spread"], f"({row['median_spread_pct']}%)", flush=True)


if __name__ == "__main__":
    have = done()
    for y, m in months(sys.argv[1], sys.argv[2]):
        if f"{y}-{m:02d}" not in have:
            process(y, m)
    print("ALL DONE", flush=True)
