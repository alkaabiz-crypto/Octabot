"""Build daily mid candles (screen.py daily definition) from Exness monthly tick zips, 2025-01..2026-10. Zips are deleted after use.

Usage: TMP_DIR=<empty scratch dir> python3 -I build.py
"""
import hashlib, json, os, ssl, sys, time, urllib.request
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "data"); os.makedirs(DATA, exist_ok=True); TMP = os.environ["TMP_DIR"]
SYMS = ["XAGUSDm", "XPTUSDm", "XPDUSDm", "UKOILm", "XNGUSDm", "US30m", "US500m", "USTECm", "DE30m", "UK100m", "JP225m", "HK50m", "FR40m", "AUS200m", "STOXX50m"]
MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
START_MS = int(pd.Timestamp("2025-01-01", tz="UTC").value // 10**6); DAY = 86_400_000; SHIFT = 2 * 3_600_000
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def month(args):
    sym, y, m = args
    url = f"https://ticks.ex2archive.com/ticks/{sym}/{y}/{m:02d}/Exness_{sym}_{y}_{m:02d}.zip"
    zp = os.path.join(TMP, f"{sym}_{y}_{m:02d}.zip")
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120, context=CTX) as r, open(zp, "wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk: break
                    f.write(chunk)
            break
        except Exception as e:  # network retry with backoff
            if k == 3: raise
            time.sleep(2 ** (k + 1))
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"])
    os.remove(zp)
    assert (df.sym == sym).all(), f"{sym} {y}-{m}: symbol mismatch"
    t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
    b, a = df.bid.to_numpy(float), df.ask.to_numpy(float); o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    assert t[0] >= START_MS
    mid = (b + a) / 2; k = (t + SHIFT) // DAY
    st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(t)]
    part = pd.DataFrame(dict(k=k[st], t_first=t[st], o=mid[st], spread_open=(a - b)[st], h=np.maximum.reduceat(mid, st), l=np.minimum.reduceat(mid, st),
                             t_last=t[en - 1], c=mid[en - 1], n=en - st, ask_below_bid=[int((a[s:e] < b[s:e]).sum()) for s, e in zip(st, en)]))
    return sym, f"{y}_{m:02d}", sha, part


def main():
    t0 = time.time(); shas = {}
    jobs = [(s, y, m) for s in SYMS for y, m in MONTHS if not os.path.exists(os.path.join(DATA, f"{s}_daily.csv"))]
    parts = {}
    with Pool(4) as p:
        for sym, mo, sha, part in p.imap_unordered(month, jobs):
            shas.setdefault(sym, {})[mo] = sha; parts.setdefault(sym, []).append(part)
            if len(parts[sym]) == len(MONTHS):
                P = pd.concat(parts.pop(sym)).sort_values("t_first")
                g = P.groupby("k")
                d = pd.DataFrame(dict(o=g.o.first(), spread_open=g.spread_open.first(), h=g.h.max(), l=g.l.min(), c=g.c.last(), n=g.n.sum(),
                                      ask_below_bid=g.ask_below_bid.sum())).reset_index()
                d["day"] = pd.to_datetime(d.k * DAY, unit="ms", utc=True).dt.strftime("%Y-%m-%d"); d = d.drop(columns="k")
                d.to_csv(os.path.join(DATA, f"{sym}_daily.csv"), index=False)
                json.dump(shas[sym], open(os.path.join(DATA, f"{sym}_sha256.json"), "w"), indent=1)
                print(sym, len(d), "days", f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
