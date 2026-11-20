"""Academic batch 005 data (copy of str_033/build_data.py with the symbol as an argument): Exness ticks (public monthly zips, ticks.ex2archive.com) -> 1-minute mid OHLC + median spread.
Raw zips are deleted after use; outputs stay in scratch (never committed). Months already covered by the causal-impact
1m build (2025-01..2026-10) are reused from there. usage: python3 -I build_data.py <SYMBOL> <scratch_out_dir> <first YYYY-MM> <last YYYY-MM>"""
import hashlib, json, os, sys, time, ssl, urllib.request
from multiprocessing import Pool
import numpy as np, pandas as pd
SYM = sys.argv[1]; OUT = sys.argv[2]; F = sys.argv[3]; L = sys.argv[4]
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()


def job(ym):
    y, m = ym; part = f"{OUT}/part_{y}_{m:02d}.npz"
    if os.path.exists(part): return y, m, "cached"
    url = f"https://ticks.ex2archive.com/ticks/{SYM}/{y}/{m:02d}/Exness_{SYM}_{y}_{m:02d}.zip"; zp = f"{OUT}/{y}_{m:02d}.zip"
    for k in range(4):
        try:
            with urllib.request.urlopen(url, timeout=300, context=CTX) as r, open(zp, "wb") as f:
                while (ch := r.read(1 << 20)): f.write(ch)
            break
        except urllib.error.HTTPError as e:
            if e.code == 404: return y, m, "missing"
            if k == 3: raise
            time.sleep(2 ** (k + 1))
        except Exception:
            if k == 3: raise
            time.sleep(2 ** (k + 1))
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    df = pd.read_csv(zp, compression="zip", usecols=[2, 3, 4], header=0, names=["ts", "bid", "ask"]); os.remove(zp)
    t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("s").astype("int64").to_numpy() // 60
    mid = (df.bid.to_numpy(float) + df.ask.to_numpy(float)) / 2; sp = df.ask.to_numpy(float) - df.bid.to_numpy(float)
    g = pd.DataFrame(dict(m=t, p=mid, s=sp)).groupby("m")
    b = dict(m=g.p.first().index.to_numpy(np.int64), o=g.p.first().to_numpy(), h=g.p.max().to_numpy(), l=g.p.min().to_numpy(), c=g.p.last().to_numpy(), sp=g.s.median().to_numpy())
    np.savez(part, **b); json.dump(dict(url=url, sha256=sha, ticks=len(df)), open(part + ".json", "w")); return y, m, len(df)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    months = [(d.year, d.month) for d in pd.period_range(F, L, freq="M")]
    with Pool(3) as p:
        for r in p.imap_unordered(job, months): print(*r, time.strftime("%H:%M:%S"), flush=True)
