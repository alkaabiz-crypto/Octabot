"""DCA mix study. Implements PREREGISTRATION.md (this folder).

Usage: CACHE_DIR=<scratch screen_cache with XAUUSDm npz> python3 -I study.py
"""
import importlib.util, json, os, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); FEE = 0.001; PER_DAY = 10.0
MIXES = dict(SP500={"SP": 1}, NASDAQ={"NDX": 1}, GOLD={"XAU": 1}, BTC={"BTC": 1}, SP_GOLD={"SP": .5, "XAU": .5},
             SP_GOLD_BTC={"SP": .4, "XAU": .4, "BTC": .2}, EQUAL5={"SP": .2, "NDX": .2, "XAU": .2, "XAG": .2, "BTC": .2})
SINGLES = ["SP500", "NASDAQ", "GOLD", "BTC"]; MIXED = ["SP_GOLD", "SP_GOLD_BTC", "EQUAL5"]
HALVES = [("2025-01-01", "2025-07-01"), ("2025-07-01", "2026-01-01"), ("2026-01-01", "2026-07-01"), ("2026-07-01", "2026-11-01")]


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m


def closes():
    load_mod("study", os.path.join(ROOT, "daily_signal_dca", "study.py")); G = load_mod("screen", os.path.join(ROOT, "shortlist_2025", "screen.py"))
    s = {}
    for k, f in (("SP", "US500m"), ("NDX", "USTECm"), ("XAG", "XAGUSDm")):
        d = pd.read_csv(os.path.join(ROOT, "mom50_breadth", "data", f"{f}_daily.csv")); d = d[d.n >= 100]; s[k] = d.set_index("day").c
    parts = [np.load(os.path.join(G.CACHE, f"XAUUSDm_{m}.npz")) for m in G.MONTHS]
    t = np.concatenate([x["t"] for x in parts]); b = np.concatenate([x["bid"] for x in parts]); a = np.concatenate([x["ask"] for x in parts])
    o = np.argsort(t, kind="stable"); dg = G.daily(t[o], b[o], a[o]); s["XAU"] = pd.Series(dg.c.values, index=dg.day.dt.strftime("%Y-%m-%d"))
    bt = pd.read_csv(os.path.join(ROOT, "daily_signal_dca", "from_2025", "data", "BTCUSDT_1d_from2025.csv.gz"))
    s["BTC"] = pd.Series(bt.c.values, index=pd.to_datetime(bt.t, unit="ms", utc=True).dt.strftime("%Y-%m-%d"))
    for k, v in s.items(): assert v.index.min() >= "2025-01-01", k
    return s


def run(px, w, start, end):
    px = px[(px.index >= start) & (px.index < end)]
    units = {k: 0.0 for k in w}; put = 0.0; worst = 0.0; nav = [1.0]; prev_v = None
    for i, (day, row) in enumerate(px.iterrows()):
        v_before = sum(units[k] * row[k] for k in w)
        if prev_v: nav.append(nav[-1] * v_before / prev_v)
        for k, x in w.items(): units[k] += PER_DAY * x * (1 - FEE) / row[k]
        put += PER_DAY; v = sum(units[k] * row[k] for k in w); prev_v = v; worst = min(worst, v / put - 1)
    nav = np.array(nav)
    return dict(put_in=round(put, 2), final=round(v, 2), profit=round(v / put - 1, 4), worst_vs_put_in=round(worst, 4),
                max_dd_nav=round(float((nav / np.maximum.accumulate(nav) - 1).min()), 4), days=len(px), first=px.index[0], last=px.index[-1])


def main():
    s = closes(); out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), full={}, halves={})
    for name, w in MIXES.items():
        px = pd.concat({k: s[k] for k in w}, axis=1, join="inner").sort_index()
        out["full"][name] = run(px, w, "2025-01-01", "2026-11-01")
        out["halves"][name] = {a: run(px, w, a, b)["profit"] for a, b in HALVES}
        out["halves"][name]["worst"] = min(out["halves"][name].values())
    avg = lambda key, names: float(np.mean([out["full"][n][key] for n in names]))
    out["H1"] = dict(avg_single_max_dd=round(avg("max_dd_nav", SINGLES), 4), mixes={n: out["full"][n]["max_dd_nav"] for n in MIXED})
    out["H1"]["verdict"] = "PASS" if all(v > out["H1"]["avg_single_max_dd"] for v in out["H1"]["mixes"].values()) else "FAIL"
    aw = float(np.mean([out["halves"][n]["worst"] for n in SINGLES]))
    out["H2"] = dict(avg_single_worst_half=round(aw, 4), mixes={n: out["halves"][n]["worst"] for n in MIXED})
    out["H2"]["verdict"] = "PASS" if all(v > aw for v in out["H2"]["mixes"].values()) else "FAIL"
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1)
    for n in MIXES: print(n, out["full"][n], out["halves"][n])
    print("H1", out["H1"]); print("H2", out["H2"])


if __name__ == "__main__":
    main()
