"""STR-025 read-only shadow on STR-023's forward ledger: what the volatility-scaled sizing (PREREG.md rule, unchanged) would
have done to the forward trades. Uses run_str025.har_sigma (frozen here) on Binance hourly closes. Changes nothing.
usage: python3 -I research/new_discovery/str_025/shadow.py
"""
import csv, json, os, ssl, sys, time, types, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_str025 as R25  # noqa: E402
LEDGER = os.path.join(os.path.dirname(HERE), "forward_str023", "ledger.csv")
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()


def hourly_closes(sym, days=560):
    t, out = int((time.time() - days * 86400) * 1000), []
    while True:
        r = json.loads(urllib.request.urlopen(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1h&startTime={t}&limit=1000", timeout=30, context=CTX).read())
        out += [(x[0] // 1000, float(x[4])) for x in r if x[6] < time.time() * 1000]
        if len(r) < 1000: return out
        t = r[-1][0] + 1


def main():
    rows = list(csv.DictReader(open(LEDGER))) if os.path.exists(LEDGER) else []
    if not rows: print("STR-025 shadow: no closed STR-023 forward trades yet"); return
    for sym in sorted({r["market"] for r in rows}):
        hc = hourly_closes(sym); asset = types.SimpleNamespace(e=types.SimpleNamespace(t=[a for a, _ in hc], c=[b for _, b in hc]))
        sig = R25.har_sigma(asset); ref = sig.rolling(365, min_periods=120).median().shift(1); x = []
        for r in (r for r in rows if r["market"] == sym):
            day = int(pd.Timestamp(r["signal_close_utc"], tz="UTC").timestamp()) // 86400
            if day in sig.index and not pd.isna(sig[day]) and not pd.isna(ref.get(day)):
                x.append((float(r["r_primary"]), float(np.clip(ref[day] / sig[day], 0.25, 2.0))))
        if not x: print(f"STR-025 shadow {sym}: no trade with a forecast yet"); continue
        r_, w = np.array([a for a, _ in x]), np.array([b for _, b in x]); sized = w / w.mean() * r_
        print(f"STR-025 shadow {sym}: {len(x)} trades | unsized mean {r_.mean():+.3f}R | volatility-sized mean {sized.mean():+.3f}R "
              f"(same average exposure) | mean weight {w.mean():.2f}")


if __name__ == "__main__":
    main()
