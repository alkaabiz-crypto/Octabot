"""Oil bot: backtest of each single entry condition the user's bot app offers. Implements PREREGISTRATION.md (this folder).

Usage: CACHE_DIR=<scratch screen_cache with USOILm npz> python3 -I study.py
"""
import json, os, sys, time
from multiprocessing import Pool
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("TICK_DIR", "/nonexistent")
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "optimize")); sys.path.insert(0, os.path.join(ROOT, "smart_entry"))
import bot  # noqa: E402
import study as SE  # noqa: E402  (smart_entry: load, features, run, summarize, EXITS, G)

RAND_P90 = {"X1_user_grid": -808.61, "X2_simple": 208.72}; ACCOUNT = 2722.94


def psar(h, l, step=0.02, mx=0.2):
    n = len(h); s = np.zeros(n); up = True; af = step; ep = h[0]; s[0] = l[0]
    for i in range(1, n):
        s[i] = s[i - 1] + af * (ep - s[i - 1])
        if up:
            s[i] = min(s[i], l[i - 1], l[i - 2] if i > 1 else l[i - 1])
            if l[i] < s[i]: up, s[i], ep, af = False, ep, l[i], step
            elif h[i] > ep: ep, af = h[i], min(af + step, mx)
        else:
            s[i] = max(s[i], h[i - 1], h[i - 2] if i > 1 else h[i - 1])
            if h[i] > s[i]: up, s[i], ep, af = True, ep, h[i], step
            elif l[i] < ep: ep, af = l[i], min(af + step, mx)
    return s


def conditions(df):
    c, h, l, v = df.c, df.h, df.l, df.v.astype(float); sig = lambda b, s: np.where(b, 1, np.where(s, -1, 0))
    out = {}
    r = bot.rating(df); out["IndicatorsSummary"] = np.where(np.isnan(r), 0, sig(r > 0.1, r < -0.1))
    e = SE.ema(c, 200).where(df.index >= 199); out["EMA200"] = sig(c > e, c < e)
    s = c.rolling(200).mean(); out["SMA200"] = sig(c > s, c < s)
    m, sd = c.rolling(20).mean(), c.rolling(20).std(); out["Bollinger"] = sig(c < m - 2 * sd, c > m + 2 * sd)
    bp = c - pd.concat([l, c.shift()], axis=1).min(axis=1); trr = pd.concat([h, c.shift()], axis=1).max(axis=1) - pd.concat([l, c.shift()], axis=1).min(axis=1)
    avg = lambda n: bp.rolling(n).sum() / trr.rolling(n).sum(); uo = 100 * (4 * avg(7) + 2 * avg(14) + avg(28)) / 7; out["UltimateOsc"] = sig(uo < 30, uo > 70)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    dm_p = np.where((h.diff() > -l.diff()) & (h.diff() > 0), h.diff(), 0.0); dm_m = np.where((-l.diff() > h.diff()) & (-l.diff() > 0), -l.diff(), 0.0)
    atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    pdi = 100 * pd.Series(dm_p, index=c.index).ewm(alpha=1 / 14, adjust=False).mean() / atr; mdi = 100 * pd.Series(dm_m, index=c.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
    adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean(); out["ADX"] = sig((adx > 20) & (pdi > mdi), (adx > 20) & (mdi > pdi))
    rs = SE.rsi(c, 14); out["RSI"] = sig(rs < 30, rs > 70)
    tp = (h + l + c) / 3; cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)); out["CCI"] = sig(cci < -100, cci > 100)
    k = (100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min())).rolling(3).mean(); d = k.rolling(3).mean()
    out["Stochastic"] = sig((k < 20) & (k > d), (k > 80) & (k < d))
    macd = SE.ema(c, 12) - SE.ema(c, 26); out["MACD"] = sig(macd > SE.ema(macd, 9), macd < SE.ema(macd, 9))
    ps = psar(h.values, l.values); out["ParabolicSAR"] = sig(c.values > ps, c.values < ps)
    mf = tp * v; pos = mf.where(tp > tp.shift(), 0.0).rolling(14).sum(); neg = mf.where(tp < tp.shift(), 0.0).rolling(14).sum()
    mfi = 100 - 100 / (1 + pos / neg); out["MFI"] = sig(mfi < 20, mfi > 80)
    return {k2: np.nan_to_num(np.asarray(v2, dtype=float)).astype(int) for k2, v2 in out.items()}


def job(args):
    name, ex, m = args
    rows = SE.run(SE.G["E"][name], SE.EXITS[ex], m)
    return name, ex, m, SE.summarize(rows, *SE.DEV), SE.summarize(rows, *SE.HOLD)


def main():
    t0 = time.time(); t, b, a = SE.load(); mid = (b + a) / 2; s = a - b
    h1, _ = SE.features(t, b); h4 = bot.candles(t, b, SE.H4)
    E = {}
    for k, v in conditions(h1).items(): E[f"{k}|1H"] = v
    c4 = conditions(h4); i4 = np.searchsorted(h4.close_ms.values, h1.close_ms.values, side="right") - 1
    for k, v in c4.items(): E[f"{k}|4H"] = np.where(i4 >= 0, v[np.clip(i4, 0, None)], 0)
    SE.G.update(t=t, b=b, a=a, b2=mid - s, a2=mid + s, closes=h1.close_ms.values, trend=h1.trend.values, rangepos=h1.rangepos.values, E=E)
    print(f"prepared {len(E)} conditions, {time.time() - t0:.0f}s", flush=True)
    with Pool(4) as p: res = p.map(job, [(n, x, m) for n in E for x in SE.EXITS for m in (1, 2)])
    out = dict(generated_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime()), results={}, verdicts={})
    for n, x, m, dv, ho in res: out["results"][f"{n}|{x}|x{m}"] = dict(dev=dv, holdout=ho)
    rank = []
    for n in E:
        for x in SE.EXITS:
            r1, r2 = out["results"][f"{n}|{x}|x1"], out["results"][f"{n}|{x}|x2"]
            ok = (r1["dev"]["net"] > 0 and r2["dev"]["net"] > 0 and r1["holdout"]["net"] > 0 and r2["holdout"]["net"] > 0 and r1["holdout"]["net"] > RAND_P90[x]
                  and r1["holdout"]["max_dd"] < 0.15 * ACCOUNT and r1["holdout"]["baskets"] >= 30)
            out["verdicts"][f"{n}|{x}"] = "PASS" if ok else "FAIL"
            rank.append((f"{n}|{x}", r2["holdout"]["net"], r1["holdout"]["net"], r1["dev"]["net"], r1["holdout"]["max_dd"], r1["holdout"]["baskets"],
                         r1["holdout"].get("win_rate"), r1["holdout"].get("pct_sells_at_bottom"), r1["holdout"].get("pct_against_4h_trend"), out["verdicts"][f"{n}|{x}"]))
    rank.sort(key=lambda z: -z[1]); out["ranking_holdout_2x"] = rank
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "results", "results.json"), "w"), indent=1, default=str)
    print("rank | holdout 2x | holdout 1x | dev 1x | dd | n | win | sellBottom | vsTrend | verdict")
    for z in rank: print(z)
    print(f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
