"""Independent check of the order-selection finding: replay the FROZEN forward.py (library_forward, unchanged copy) over
historical Binance ETHUSDT minutes. Only its network fetch is replaced by the historical data; its state starts at
2025-01-01 00:00 UTC; it runs in a scratch copy, so no repository file or live ledger is touched.
usage: REPLAY_DIR=<dir with an unmodified copy of forward.py> BIN_DIR=<dir with ETHUSDT_1m.npz> python3 replay_forward_eth.py"""
import csv, json, os, sys
import numpy as np

R = os.environ["REPLAY_DIR"]; sys.path.insert(0, R)
import forward as F  # noqa: E402  (unchanged frozen code)

z = np.load(os.path.join(os.environ["BIN_DIR"], "ETHUSDT_1m.npz"))
CUT = int(np.datetime64("2026-11-10T11:19:00").astype("datetime64[m]").astype(np.int64))
keep = z["m"] <= CUT
m = z["m"][keep] * 60000; o, h, l, c = z["o"][keep], z["h"][keep], z["l"][keep], z["c"][keep]
M1 = [(int(t), float(a), float(b), float(d), float(e)) for t, a, b, d, e in zip(m, o, h, l, c)]
hr = m // 3600000; st = np.flatnonzero(np.r_[True, hr[1:] != hr[:-1]]); en = np.r_[st[1:], len(m)]
H1 = [(int(hr[s] * 3600000), float(o[s]), float(h[s:e].max()), float(l[s:e].min()), float(c[e - 1])) for s, e in zip(st, en)]
H1 = H1[:-1] if (m[-1] + 60000) % 3600000 else H1          # drop a last hour that is not complete


def fake_candles(coin, iv, start_ms, source="hyperliquid"):
    return [x for x in M1 if x[0] >= start_ms] if iv == "1m" else H1


F.candles = fake_candles
cfg = F.TESTS["ETH_FIB"]
json.dump(dict(cursor=int(m[0]) - 60000, pending=[], pos=None, next_check=0, trades=0, net1=0.0, net2=0.0, bp2=0.0, wins2=0, started="replay"),
          open(os.path.join(R, "state_ETH_FIB.json"), "w"))
rows, _ = F.run("ETH_FIB", cfg)
HOLD = "2026-01-01 00:00"
out = {}
for p, sel in (("2025", [r for r in rows if r["fill_utc"] < HOLD]), ("2026", [r for r in rows if r["fill_utc"] >= HOLD])):
    x = np.array([r["net_bp_2x"] for r in sel], float)
    out[p] = dict(trades=len(x), mean_bp_2x=round(float(x.mean()), 2), t=round(float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), 2))
print(json.dumps(out))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "replay_forward_eth.json"), "w"), indent=1)
