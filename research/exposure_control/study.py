"""Exposure-matched random-timing control (circular shifts). Implements PREREGISTRATION.md (this folder).

Usage: CACHE_DIR=<scratch screen_cache with XAUUSDm_YYYY_MM npz> python3 -I study.py
"""
import importlib.util, json, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
N = 1000; SEED = 20261112; FEE = 0.001


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


S = load_mod("study", os.path.join(ROOT, "daily_signal_dca", "study.py"))
R = load_mod("from2025_run", os.path.join(ROOT, "daily_signal_dca", "from_2025", "run.py"))
G = load_mod("screen", os.path.join(ROOT, "shortlist_2025", "screen.py"))


def shifts(n, rng):
    return rng.integers(20, n - 20 + 1, size=N)


def control(rule_value, values):
    v = np.array(values)
    return dict(rule=round(float(rule_value), 4), p50=round(float(np.percentile(v, 50)), 4), p90=round(float(np.percentile(v, 90)), 4),
                p95=round(float(np.percentile(v, 95)), 4), percentile=round(float((v < rule_value).mean() * 100), 1),
                verdict="PASS" if rule_value > np.percentile(v, 95) else "FAIL")


def crypto(out, rng):
    for sym in ("BTCUSDT", "ETHUSDT"):
        d = R.klines(sym, "1d"); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True); sig = R.signals(d)
        s, e = R.SPLITS["full"]
        for name in ("TREND_ENS", "TREND_ENS_VOL", "SMA50"):
            w = sig[name].fillna(0.0).reset_index(drop=True)
            base = S.metrics(S.lump(d, w, FEE), s, e)["total_return"]
            vals = [S.metrics(S.lump(d, pd.Series(np.roll(w.values, k)), FEE), s, e)["total_return"] for k in shifts(len(w), rng)]
            out[f"{sym}|{name}"] = control(base, vals) | dict(avg_exposure=round(float(w.mean()), 3), buy_hold=S.metrics(S.lump(d, pd.Series(np.ones(len(d))), FEE), s, e)["total_return"])
            print(sym, name, out[f"{sym}|{name}"], flush=True)


def gold(out, rng):
    parts = [np.load(os.path.join(G.CACHE, f"XAUUSDm_{m}.npz")) for m in G.MONTHS]
    t = np.concatenate([x["t"] for x in parts]); b = np.concatenate([x["bid"] for x in parts]); a = np.concatenate([x["ask"] for x in parts])
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]; assert t[0] >= G.START_MS
    d = G.daily(t, b, a); c = d.c
    tr_ = pd.concat([d.h - d.l, (d.h - c.shift()).abs(), (d.l - c.shift()).abs()], axis=1).max(axis=1); atr = tr_.ewm(alpha=1 / 14, adjust=False).mean()
    sma20 = c.rolling(20).mean(); entry_sig = (c > c.shift(50)) & (sma20 > sma20.shift(5))
    w = np.zeros(len(d)); pos = False; ep = pk = 0.0; held = 0
    for i in range(len(d)):                                                # identical to screen.py gold() G_MOM50_ATR
        if pos:
            held += 1; pk = max(pk, c[i])
            if c[i] < ep - 2 * atr[i] or c[i] < pk - 1.5 * atr[i] or held >= 30: pos = False
        elif bool(entry_sig[i]): pos, ep, pk, held = True, c[i], c[i], 0
        w[i] = 1.0 if pos else 0.0
    s0 = 55
    eq, tr = G.run_daily(d, w, 2); base = G.stats(eq, tr, s0)["net"]
    seg = w[s0 - 1:].copy()                                               # shift only the active period, so exposure is matched there
    vals = []
    for k in shifts(len(seg), rng):
        ww = w.copy(); ww[s0 - 1:] = np.roll(seg, k); e2, t2 = G.run_daily(d, ww, 2); vals.append(G.stats(e2, t2, s0)["net"])
    out["XAUUSDm|G_MOM50_ATR|x2"] = control(base, vals) | dict(avg_exposure=round(float(seg.mean()), 3), trades=tr, buy_hold=G.bh(d, s0, 2)["net"])
    print("gold", out["XAUUSDm|G_MOM50_ATR|x2"], flush=True)


def main():
    t0 = time.time(); rng = np.random.default_rng(SEED); out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), n_shifts=N)
    crypto(out, rng); gold(out, rng)
    out["primary_verdicts"] = {k: out[k]["verdict"] for k in ("BTCUSDT|TREND_ENS", "ETHUSDT|TREND_ENS", "XAUUSDm|G_MOM50_ATR|x2")}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    print(json.dumps(out["primary_verdicts"], indent=1), f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
