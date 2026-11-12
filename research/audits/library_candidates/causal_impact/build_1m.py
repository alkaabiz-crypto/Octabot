"""Rebuild the theory library's Exness 1m bars (XAUUSDm, USOILm, 2025-01..2026-10) from the public monthly tick zips,
using the FROZEN build_bars.bars() function unchanged (imported from the read-only extract). Zips deleted after use; SHA-256 kept."""
import hashlib, json, os, sys, time, ssl, urllib.request
from multiprocessing import Pool
import numpy as np, pandas as pd
S = sys.argv[1]; EXT = sys.argv[2]; SYMS = sys.argv[3].split(",") if len(sys.argv) > 3 else ["USOILm", "XAUUSDm"]
os.environ.update(CACHE_DIR=S + "/cia/none", TMP_DIR=S + "/cia/tickzip", OUT_DIR=S + "/cia/bars1m")
sys.path.insert(0, EXT + "/research/orb_study"); import build_bars as BB  # frozen, unchanged
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
def job(a):
    sym, y, m = a; url = f"https://ticks.ex2archive.com/ticks/{sym}/{y}/{m:02d}/Exness_{sym}_{y}_{m:02d}.zip"; zp = f"{S}/cia/tickzip/{sym}_{y}_{m:02d}.zip"
    part = f"{S}/cia/bars1m/part_{sym}_{y}_{m:02d}.npz"
    if os.path.exists(part): return sym, y, m, "cached", 0
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=300, context=CTX) as r, open(zp, "wb") as f:
                while (ch := r.read(1 << 20)): f.write(ch)
            break
        except Exception as e:
            if k == 3: raise
            time.sleep(2 ** (k + 1))
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"]); os.remove(zp)
    assert (df.sym == sym).all()
    t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
    b = BB.bars(t, df.bid.to_numpy(float), df.ask.to_numpy(float)); np.savez(part, **b)
    json.dump(dict(url=url, sha256=sha, ticks=len(df)), open(part + ".json", "w"))
    return sym, y, m, sha, len(df)
if __name__ == "__main__":
    jobs = [(s, y, m) for s in SYMS for (y, m) in BB.MONTHS]
    with Pool(3) as p:
        for r in p.imap_unordered(job, jobs): print(*r, time.strftime("%H:%M:%S"), flush=True)
    for s in SYMS:
        parts = [np.load(f"{S}/cia/bars1m/part_{s}_{y}_{m:02d}.npz") for (y, m) in BB.MONTHS]
        out = {k: np.concatenate([p[k] for p in parts]) for k in ("m", "o", "h", "l", "c", "sp")}
        assert (np.diff(out["m"]) > 0).all(); np.savez(f"{S}/cia/bars1m/{s}_1m.npz", **out); print(s, len(out["m"]), "minutes", flush=True)
