"""Independent tick-level re-test of gold SCHOOL ORB. Implements VERIFY_PREREG.md (this folder).

Usage: CACHE_DIR=<screen_cache with XAUUSDm_YYYY_MM npz ticks> BARS_DIR=<orb bars> python3 -I verify_tick.py
"""
import datetime as dt, importlib.util, json, os, time
from zoneinfo import ZoneInfo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.environ["CACHE_DIR"]; NY = ZoneInfo("America/New_York")
MONTHS = [(y, m) for y in (2025, 2026) for m in range(1, 13) if not (y == 2026 and m > 10)]
WINDOWS = {"SCHOOL_0825": (8, 25), "SHIFT_0820": (8, 20), "SHIFT_0830": (8, 30)}


def ms(d, h, m):
    return int(dt.datetime(d.year, d.month, d.day, h, m, tzinfo=NY).timestamp() * 1000)


def day_trade(t, b, a, d, start, xc):
    s0 = ms(d, *start); s1 = s0 + 5 * 60_000; fx = ms(d, 13, 30)
    i, j = np.searchsorted(t, s0), np.searchsorted(t, s1)
    if j - i < 20 or t[i] - s0 > 60_000: return None
    mid = (b[i:j] + a[i:j]) / 2; rh, rl = mid.max(), mid.min(); H = rh - rl; hs0 = (a[i] - b[i]) / 2
    if H <= 0: return None
    k, e = j, np.searchsorted(t, fx)
    if e - k < 10: return None
    up = np.flatnonzero(a[k:e] >= rh + hs0); dn = np.flatnonzero(b[k:e] <= rl - hs0)
    fu = up[0] if len(up) else None; fd = dn[0] if len(dn) else None
    if fu is None and fd is None: return None
    side = 1 if (fd is None or (fu is not None and fu < fd)) else -1; q = k + (fu if side > 0 else fd)
    entry = a[q] if side > 0 else b[q]; model_fill = (rh + hs0) if side > 0 else (rl - hs0)
    sp_in = a[q] - b[q]
    if side > 0: stop_lvl, tp_lvl = rl - hs0, rh + H - hs0
    else: stop_lvl, tp_lvl = rh + hs0, rl - H + hs0
    bb, aa, tt = b[q + 1:e], a[q + 1:e], t[q + 1:e]
    st = np.flatnonzero(bb <= stop_lvl) if side > 0 else np.flatnonzero(aa >= stop_lvl)
    tp = np.flatnonzero(bb >= tp_lvl) if side > 0 else np.flatnonzero(aa <= tp_lvl)
    s_i = st[0] if len(st) else 10**12; t_i = tp[0] if len(tp) else 10**12
    if s_i < t_i: x_i, px, why = s_i, (bb[s_i] if side > 0 else aa[s_i]), "stop"
    elif t_i < 10**12: x_i, px, why = t_i, tp_lvl, "tp"
    else: x_i, px, why = len(bb) - 1, (bb[-1] if side > 0 else aa[-1]), "time"
    if xc:
        ce = s1 + ((t[q] - s1) // 300_000 + 1) * 300_000; c_i = int(np.searchsorted(tt, ce)) - 1
        if 0 <= c_i < x_i:
            m_c = (bb[c_i] + aa[c_i]) / 2
            if rl <= m_c <= rh: x_i, px, why = c_i, (bb[c_i] if side > 0 else aa[c_i]), "close_inside"
    sp_out = aa[x_i] - bb[x_i]
    r1 = side * (px - entry) / H; r2 = r1 - (sp_in / 2 + sp_out / 2) / H
    return dict(day=str(d), side=side, r1=r1, r2=r2, H=H, slip=side * (entry - model_fill), why=why, sp_in=sp_in)


def bar_sides():
    spec = importlib.util.spec_from_file_location("orb_main", os.path.join(HERE, "study.py")); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    M.setup("XAUUSDm"); g = M.D["XAUUSDm"]; out = {}
    for d, o_m, f_m in g["days"]:
        i, j = M.idx("XAUUSDm", o_m + 5, o_m + 10)
        if j - i < 4 or g["m"][i] != o_m + 5: continue
        rh, rl = g["h"][i:j].max(), g["l"][i:j].min(); k, e = M.idx("XAUUSDm", o_m + 10, f_m)
        if e - k < 2: continue
        up, dn = g["h"][k:e] > rh, g["l"][k:e] < rl
        fu = int(np.argmax(up)) if up.any() else 10**9; fd = int(np.argmax(dn)) if dn.any() else 10**9
        if fu == fd: continue
        out[str(d)] = 1 if fu < fd else -1
    return out


def summ(rows, key):
    r = np.array([x[key] for x in rows]); return dict(trades=int(len(r)), mean_R=round(float(r.mean()), 4) if len(r) else None, win=round(float((r > 0).mean()), 3) if len(r) else None)


def main():
    t0 = time.time(); res = {w: {"X0": [], "XC": []} for w in WINDOWS}; news = {}
    for y, m in MONTHS:
        z = np.load(os.path.join(CACHE, f"XAUUSDm_{y}_{m:02d}.npz")); t, b, a = z["t"], z["bid"], z["ask"]; o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
        d = dt.date(y, m, 1)
        while d.month == m:
            if d.weekday() < 5:
                for w, st in WINDOWS.items():
                    for xc in (False, True):
                        r = day_trade(t, b, a, d, st, xc)
                        if r: res[w]["XC" if xc else "X0"].append(r)
                i, j = np.searchsorted(t, ms(d, 8, 30)), np.searchsorted(t, ms(d, 8, 31))
                if j > i: mm = (b[i:j] + a[i:j]) / 2; news[str(d)] = float(mm.max() - mm.min())
            d += dt.timedelta(days=1)
        print(y, m, f"{time.time() - t0:.0f}s", flush=True)
    keys = sorted(news); vals = np.array([news[k] for k in keys]); is_news = {}
    for n, k in enumerate(keys):
        base = np.median(vals[max(0, n - 20):n]) if n >= 5 else np.nan
        is_news[k] = bool(base == base and vals[n] > 3 * base)
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), windows={})
    for w in WINDOWS:
        out["windows"][w] = {}
        for x in ("X0", "XC"):
            rows = res[w][x]
            out["windows"][w][x] = {p: {k: summ([r for r in rows if (r["day"] < "2026") == (p == "2025")], k) for k in ("r1", "r2")} for p in ("2025", "2026")}
            if w == "SCHOOL_0825":
                out["windows"][w][x]["news_days_r2"] = summ([r for r in rows if is_news.get(r["day"])], "r2")
                out["windows"][w][x]["other_days_r2"] = summ([r for r in rows if not is_news.get(r["day"])], "r2")
                out["windows"][w][x]["exit_reasons"] = {k: sum(r["why"] == k for r in rows) for k in ("tp", "stop", "time", "close_inside")}
    sch = res["SCHOOL_0825"]["X0"]; bs = bar_sides(); shared = [r for r in sch if r["day"] in bs]
    out["agreement"] = dict(shared_days=len(shared), same_side=round(float(np.mean([bs[r["day"]] == r["side"] for r in shared])), 4))
    out["slippage_vs_model_usd"] = dict(mean=round(float(np.mean([r["slip"] for r in sch])), 4), p90=round(float(np.percentile([r["slip"] for r in sch], 90)), 4),
                                        mean_entry_spread=round(float(np.mean([r["sp_in"] for r in sch])), 4), mean_H=round(float(np.mean([r["H"] for r in sch])), 3))
    x0 = out["windows"]["SCHOOL_0825"]["X0"]
    out["verdict"] = "CONFIRMED" if (x0["2025"]["r2"]["mean_R"] > 0 and x0["2026"]["r2"]["mean_R"] > 0 and out["agreement"]["same_side"] >= 0.95) else "NOT CONFIRMED"
    json.dump(out, open(os.path.join(HERE, "results", "verify_tick.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
