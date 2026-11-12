"""MOM50 breadth test. Implements PREREGISTRATION.md (this folder). Needs data/ from build.py.

Usage: CACHE_DIR=<any dir> python3 -I study.py      (CACHE_DIR only satisfies screen.py's import)
"""
import importlib.util, json, math, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); DATA = os.path.join(HERE, "data")
N = 1000; SEED = 20261112; S0 = 55; MIN_DAYS = 300


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


load_mod("study", os.path.join(ROOT, "daily_signal_dca", "study.py"))
G = load_mod("screen", os.path.join(ROOT, "shortlist_2025", "screen.py"))
from build import SYMS  # noqa: E402


def mom50_weights(d):
    c = d.c
    tr_ = pd.concat([d.h - d.l, (d.h - c.shift()).abs(), (d.l - c.shift()).abs()], axis=1).max(axis=1); atr = tr_.ewm(alpha=1 / 14, adjust=False).mean()
    sma20 = c.rolling(20).mean(); entry_sig = (c > c.shift(50)) & (sma20 > sma20.shift(5))
    w = np.zeros(len(d)); pos = False; ep = pk = 0.0; held = 0
    for i in range(len(d)):                                                # identical to screen.py gold() G_MOM50_ATR
        if pos:
            held += 1; pk = max(pk, c[i])
            if c[i] < ep - 2 * atr[i] or c[i] < pk - 1.5 * atr[i] or held >= 30: pos = False
        elif bool(entry_sig[i]): pos, ep, pk, held = True, c[i], c[i], 0
        w[i] = 1.0 if pos else 0.0
    return w


def sharpe(eq):
    e = eq[S0:]; r = e[1:] / e[:-1] - 1
    return float(r.mean() / r.std() * math.sqrt(252)) if r.std() > 0 else 0.0


def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); D, W, dropped = {}, {}, {}
    for s in SYMS:
        p = os.path.join(DATA, f"{s}_daily.csv")
        if not os.path.exists(p): dropped[s] = "no data"; continue
        d = pd.read_csv(p); d = d[d.n >= 100].reset_index(drop=True); d["day"] = pd.to_datetime(d.day, utc=True)
        if len(d) < MIN_DAYS: dropped[s] = len(d); continue
        D[s], W[s] = d, mom50_weights(d)
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), markets=list(D), dropped=dropped, per_market={})
    base = {}
    for s, d in D.items():
        eq, tr = G.run_daily(d, W[s], 2); base[s] = sharpe(eq); st = G.stats(eq, tr, S0); bh = G.bh(d, S0, 2)
        eqb, _ = G.run_daily(d, np.r_[np.zeros(S0 - 1), np.ones(len(d) - S0 + 1)], 2)
        out["per_market"][s] = dict(sharpe=round(base[s], 3), net=st["net"], max_dd=st["max_dd"], trades=tr, exposure=round(float(W[s][S0 - 1:].mean()), 3),
                                    bh_net=bh["net"], bh_max_dd=bh["max_dd"], bh_sharpe=round(sharpe(eqb), 3), days=len(d),
                                    first=str(d.day.iloc[0].date()), last=str(d.day.iloc[-1].date()), ask_below_bid=int(d.ask_below_bid.sum()))
    draws = np.zeros(N); per = {s: [] for s in D}
    for k in range(N):
        vals = []
        for s, d in D.items():
            seg = W[s][S0 - 1:]; ww = W[s].copy(); ww[S0 - 1:] = np.roll(seg, int(rng.integers(20, len(seg) - 20 + 1)))
            e2, _ = G.run_daily(d, ww, 2); v = sharpe(e2); vals.append(v); per[s].append(v)
        draws[k] = np.mean(vals)
        if k % 100 == 0: print(k, f"{time.time() - t0:.0f}s", flush=True)
    for s in D: out["per_market"][s]["percentile_vs_own_shifts"] = round(float((np.array(per[s]) < base[s]).mean() * 100), 1)
    m = float(np.mean(list(base.values())))
    out["primary"] = dict(mean_sharpe=round(m, 3), random_p50=round(float(np.percentile(draws, 50)), 3), random_p95=round(float(np.percentile(draws, 95)), 3),
                          percentile=round(float((draws < m).mean() * 100), 1), verdict="PASS" if m > np.percentile(draws, 95) else "FAIL",
                          mean_bh_sharpe=round(float(np.mean([v["bh_sharpe"] for v in out["per_market"].values()])), 3))
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print(json.dumps(out["primary"], indent=1))
    for s, v in out["per_market"].items(): print(s, v)
    print("dropped", dropped, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
