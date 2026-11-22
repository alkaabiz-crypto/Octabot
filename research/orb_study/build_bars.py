"""Build 1-minute mid bars (open/high/low/close + median spread) from Exness ticks, 2025-01..2026-10.

XAUUSDm and USOILm come from the cached npz ticks (CACHE_DIR); DE30m, US500m and USTECm are downloaded month by
month into TMP_DIR and deleted after use (SHA-256 kept). Output: OUT_DIR/<sym>_1m.npz and OUT_DIR/<sym>_sha256.json.

Usage: CACHE_DIR=<screen_cache> TMP_DIR=<empty dir> OUT_DIR=<dir> python3 -I build_bars.py
"""
import hashlib, json, os, ssl, time, urllib.request
from multiprocessing import Pool
import numpy as np
import pandas as pd

CACHE, TMP, OUT = os.environ["CACHE_DIR"], os.environ["TMP_DIR"], os.environ["OUT_DIR"]; os.makedirs(OUT, exist_ok=True)
MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
START_MS = int(pd.Timestamp("2025-01-01", tz="UTC").value // 10**6)
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
CACHED = ("XAUUSDm", "USOILm"); DOWNLOAD = ("DE30m", "US500m", "USTECm")


def bars(t, b, a):
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]; assert t[0] >= START_MS
    mid = (b + a) / 2; sp = a - b; k = t // 60_000
    st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(t)]
    med = np.array([np.median(sp[s:e]) for s, e in zip(st, en)])
    return dict(m=k[st], o=mid[st], h=np.maximum.reduceat(mid, st), l=np.minimum.reduceat(mid, st), c=mid[en - 1], sp=med)


def month(args):
    sym, y, m = args
    if sym in CACHED:
        z = np.load(os.path.join(CACHE, f"{sym}_{y}_{m:02d}.npz")); return sym, f"{y}_{m:02d}", "cached-npz", bars(z["t"], z["bid"], z["ask"])
    url = f"https://ticks.ex2archive.com/ticks/{sym}/{y}/{m:02d}/Exness_{sym}_{y}_{m:02d}.zip"; zp = os.path.join(TMP, f"{sym}_{y}_{m:02d}.zip")
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120, context=CTX) as r, open(zp, "wb") as f:
                while True:
                    ch = r.read(1 << 20)
                    if not ch: break
                    f.write(ch)
            break
        except Exception:
            if k == 3: raise
            time.sleep(2 ** (k + 1))
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"]); os.remove(zp)
    assert (df.sym == sym).all()
    t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
    return sym, f"{y}_{m:02d}", sha, bars(t, df.bid.to_numpy(float), df.ask.to_numpy(float))


def main():
    t0 = time.time(); acc = {}; shas = {}
    jobs = [(s, y, m) for s in CACHED + DOWNLOAD for y, m in MONTHS if not os.path.exists(os.path.join(OUT, f"{s}_1m.npz"))]
    with Pool(4) as p:
        for sym, mo, sha, bd in p.imap_unordered(month, jobs):
            acc.setdefault(sym, []).append(bd); shas.setdefault(sym, {})[mo] = sha
            if len(acc[sym]) == len(MONTHS):
                parts = acc.pop(sym); d = {k: np.concatenate([x[k] for x in parts]) for k in parts[0]}
                o = np.argsort(d["m"], kind="stable"); d = {k: v[o] for k, v in d.items()}
                keep = np.r_[True, d["m"][1:] != d["m"][:-1]]; d = {k: v[keep] for k, v in d.items()}   # month-edge duplicates
                np.savez_compressed(os.path.join(OUT, f"{sym}_1m.npz"), **d)
                json.dump(shas[sym], open(os.path.join(OUT, f"{sym}_sha256.json"), "w"), indent=1)
                print(sym, len(d["m"]), "bars", f"{time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
