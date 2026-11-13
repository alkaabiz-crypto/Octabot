"""Batch 3 signal library (PREREGISTRATION.md). Every array is decided at the CLOSE of bar i using bars <= i only.
Triggers / strategies / theories return (long_mask, short_mask). Filters return (bull_state, bear_state)."""
import numpy as np
import pandas as pd
from engine import ema, sma, rma, atr, rsi, supertrend, psar, adx, x_up, x_dn, roll_prev_max, roll_prev_min

B = lambda x: np.nan_to_num(np.asarray(x, dtype=float), nan=0).astype(bool) if np.asarray(x).dtype != bool else np.asarray(x)


def dst_us(day):   # True if US daylight time (2nd Sun Mar .. 1st Sun Nov), day = epoch day
    d = pd.to_datetime(day, unit="D"); y = d.year
    s = pd.to_datetime([f"{a}-03-08" for a in y]) + pd.to_timedelta((6 - pd.to_datetime([f"{a}-03-08" for a in y]).dayofweek) % 7, "D")
    e = pd.to_datetime([f"{a}-11-01" for a in y]) + pd.to_timedelta((6 - pd.to_datetime([f"{a}-11-01" for a in y]).dayofweek) % 7, "D")
    return np.asarray((d >= s) & (d < e))


def dst_eu(day):   # last Sun Mar .. last Sun Oct
    d = pd.to_datetime(day, unit="D"); y = d.year
    s = pd.to_datetime([f"{a}-03-31" for a in y]); s = s - pd.to_timedelta((s.dayofweek + 1) % 7, "D")
    e = pd.to_datetime([f"{a}-10-31" for a in y]); e = e - pd.to_timedelta((e.dayofweek + 1) % 7, "D")
    return np.asarray((d >= s) & (d < e))


def compute(df, tf, market, htf_df):
    """All indicators for one market/timeframe. df: bars (t in epoch minutes, o,h,l,c). htf_df: next-higher-timeframe bars."""
    o, h, l, c = df.o, df.h, df.l, df.c; t = df.t.values; tfm = tf
    I = {}
    I["ema9"], I["ema21"], I["ema50"], I["ema200"], I["ema20"], I["ema55"] = (ema(c, n) for n in (9, 21, 50, 200, 20, 55))
    I["sma20"], I["sma50"], I["sma200"], I["sma5"] = (sma(c, n) for n in (20, 50, 200, 5))
    I["rsi14"], I["rsi2"] = rsi(c, 14), rsi(c, 2)
    m = ema(c, 12) - ema(c, 26); I["macd"], I["macds"] = m, ema(m, 9)
    k = 100 * (c - l.rolling(14).min()) / (h.rolling(14).max() - l.rolling(14).min()); I["stk"] = k.rolling(3).mean(); I["std"] = I["stk"].rolling(3).mean()
    tp = (h + l + c) / 3; I["cci"] = (tp - sma(tp, 20)) / (0.015 * tp.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True))
    bm, bs = sma(c, 20), c.rolling(20).std(ddof=0); I["bbu"], I["bbl"], I["bbm"] = bm + 2 * bs, bm - 2 * bs, bm
    A = atr(df); I["atr"] = A; I["kcu"], I["kcl"] = ema(c, 20) + 2 * A, ema(c, 20) - 2 * A
    I["st"] = supertrend(df); I["psar"] = psar(df)
    I["adx"], I["pdi"], I["ndi"] = adx(df)
    I["wr"] = -100 * (h.rolling(14).max() - c) / (h.rolling(14).max() - l.rolling(14).min())
    tk = (h.rolling(9).max() + l.rolling(9).min()) / 2; kj = (h.rolling(26).max() + l.rolling(26).min()) / 2
    sa = ((tk + kj) / 2).shift(26); sb = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
    I["tk"], I["kj"], I["cloud_top"], I["cloud_bot"] = tk, kj, np.maximum(sa, sb), np.minimum(sa, sb)
    hac = (o + h + l + c) / 4; hao = np.empty(len(c)); hao[0] = (o.iloc[0] + c.iloc[0]) / 2
    hv = hac.values
    for i in range(1, len(c)): hao[i] = (hao[i - 1] + hv[i - 1]) / 2
    I["ha_up"] = hv > hao
    I["roc"] = c.pct_change(10)
    ar_up = h.rolling(26).apply(lambda x: 100 * np.argmax(x) / 25, raw=True); ar_dn = l.rolling(26).apply(lambda x: 100 * np.argmin(x) / 25, raw=True)
    I["arup"], I["ardn"] = ar_up, ar_dn
    tr3 = ema(ema(ema(c, 15), 15), 15); I["trix"] = tr3.pct_change(); I["trixs"] = sma(I["trix"], 9)
    mp = (h + l) / 2; I["ao"] = sma(mp, 5) - sma(mp, 34)
    dlt = c.diff(); su, sd = dlt.clip(lower=0).rolling(14).sum(), (-dlt.clip(upper=0)).rolling(14).sum(); I["cmo"] = 100 * (su - sd) / (su + sd)
    pc = c.shift(); bp = c - pd.concat([l, pc], axis=1).min(axis=1); trr = pd.concat([h, pc], axis=1).max(axis=1) - pd.concat([l, pc], axis=1).min(axis=1)
    av = lambda n: bp.rolling(n).sum() / trr.rolling(n).sum(); I["uo"] = 100 * (4 * av(7) + 2 * av(14) + av(28)) / 7
    body = (c - o).abs(); rng = (h - l).replace(0, np.nan); lw = np.minimum(o, c) - l; uw = h - np.maximum(o, c)
    I["wick_long"] = B((lw >= 2 * body) & (lw >= 0.6 * rng) & (c > l + 0.6 * rng)); I["wick_short"] = B((uw >= 2 * body) & (uw >= 0.6 * rng) & (c < h - 0.6 * rng))
    # session (UTC day) quantities
    day = t // 1440; I["day"] = day; I["mod"] = t % 1440
    g = pd.Series(tp.values).groupby(day); I["vwap"] = g.cumsum().values / g.cumcount().add(1).values
    I["vwsd"] = pd.Series(tp.values).groupby(day).expanding().std(ddof=0).reset_index(level=0, drop=True).sort_index().values
    dh = pd.Series(h.values).groupby(day).max(); dl = pd.Series(l.values).groupby(day).min()
    I["pdh"] = pd.Series(day).map(dh.shift(1)).values; I["pdl"] = pd.Series(day).map(dl.shift(1)).values
    wk = (day + 3) // 7; wh = pd.Series(h.values).groupby(wk).max(); wl = pd.Series(l.values).groupby(wk).min()
    I["pwh"] = pd.Series(wk).map(wh.shift(1)).values; I["pwl"] = pd.Series(wk).map(wl.shift(1)).values
    bw = (I["bbu"] - I["bbl"]) / bm; I["squeeze"] = B(bw <= bw.rolling(100).quantile(0.2))
    # higher timeframe EMA50 trend, last CLOSED HTF bar
    he = ema(htf_df.c, 50).values; hclose = htf_df.t.values + (htf_df.t.values[1] - htf_df.t.values[0] if len(htf_df) > 1 else 0)
    hs = (htf_df.c.values > he).astype(int) - (htf_df.c.values < he).astype(int)
    j = np.searchsorted(hclose, t + tfm, side="right") - 1; I["htf"] = np.where(j >= 50, hs[np.clip(j, 0, None)], 0)
    for kk in list(I):
        if isinstance(I[kk], pd.Series): I[kk] = I[kk].values
    I["o"], I["h"], I["l"], I["c"], I["t"] = o.values, h.values, l.values, c.values, t
    return I


# ------------------------------------------------------------------ Part A triggers
def triggers(I):
    c = I["c"]; T = {}
    T["RSI14_30_70"] = (x_up(I["rsi14"], np.full(len(c), 30)), x_dn(I["rsi14"], np.full(len(c), 70)))
    T["RSI2_10_90"] = (I["rsi2"] < 10, I["rsi2"] > 90)
    T["MACD_signal_cross"] = (x_up(I["macd"], I["macds"]), x_dn(I["macd"], I["macds"]))
    T["MACD_zero_cross"] = (x_up(I["macd"], 0 * c), x_dn(I["macd"], 0 * c))
    T["EMA9_21_cross"] = (x_up(I["ema9"], I["ema21"]), x_dn(I["ema9"], I["ema21"]))
    T["EMA50_200_cross"] = (x_up(I["ema50"], I["ema200"]), x_dn(I["ema50"], I["ema200"]))
    T["close_x_EMA50"] = (x_up(c, I["ema50"]), x_dn(c, I["ema50"]))
    T["Stoch_cross_zone"] = (x_up(I["stk"], I["std"]) & (I["stk"] < 20), x_dn(I["stk"], I["std"]) & (I["stk"] > 80))
    T["CCI_100"] = (x_up(I["cci"], np.full(len(c), -100)), x_dn(I["cci"], np.full(len(c), 100)))
    T["BB_reentry"] = (x_up(c, I["bbl"]), x_dn(c, I["bbu"]))
    T["BB_breakout"] = (x_up(c, I["bbu"]), x_dn(c, I["bbl"]))
    T["Donchian20_break"] = (c > roll_prev_max(I["h"], 20), c < roll_prev_min(I["l"], 20))
    T["Keltner_break"] = (x_up(c, I["kcu"]), x_dn(c, I["kcl"]))
    T["Supertrend_flip"] = (x_up(I["st"], 0 * c), x_dn(I["st"], 0 * c))
    T["PSAR_flip"] = (x_up(I["psar"], 0 * c), x_dn(I["psar"], 0 * c))
    T["DI_cross"] = (x_up(I["pdi"], I["ndi"]), x_dn(I["pdi"], I["ndi"]))
    T["WilliamsR_80_20"] = (x_up(I["wr"], np.full(len(c), -80)), x_dn(I["wr"], np.full(len(c), -20)))
    T["Ichimoku_TK_cross"] = (x_up(I["tk"], I["kj"]), x_dn(I["tk"], I["kj"]))
    ha = I["ha_up"].astype(float); T["HeikinAshi_flip"] = (x_up(ha, np.full(len(c), 0.5)), x_dn(ha, np.full(len(c), 0.5)))
    T["ROC10_zero"] = (x_up(I["roc"], 0 * c), x_dn(I["roc"], 0 * c))
    T["Aroon_cross"] = (x_up(I["arup"], I["ardn"]), x_dn(I["arup"], I["ardn"]))
    T["TRIX_signal"] = (x_up(I["trix"], I["trixs"]), x_dn(I["trix"], I["trixs"]))
    T["AO_zero"] = (x_up(I["ao"], 0 * c), x_dn(I["ao"], 0 * c))
    T["CMO_50"] = (x_up(I["cmo"], np.full(len(c), -50)), x_dn(I["cmo"], np.full(len(c), 50)))
    T["UO_30_70"] = (x_up(I["uo"], np.full(len(c), 30)), x_dn(I["uo"], np.full(len(c), 70)))
    T["Wick_rejection"] = (I["wick_long"], I["wick_short"])
    return {k: (B(a), B(b)) for k, (a, b) in T.items()}


def filters(I):
    c = I["c"]; F = {}; both = lambda x: (B(x), B(x))
    F["above_EMA200"] = (c > I["ema200"], c < I["ema200"])
    F["EMA50_vs_200"] = (I["ema50"] > I["ema200"], I["ema50"] < I["ema200"])
    F["ADX_gt25"] = both(I["adx"] > 25); F["ADX_lt20"] = both(I["adx"] < 20)
    F["RSI_vs_50"] = (I["rsi14"] > 50, I["rsi14"] < 50)
    F["MACD_vs_0"] = (I["macd"] > 0, I["macd"] < 0)
    F["Supertrend_dir"] = (I["st"] > 0, I["st"] < 0)
    F["VWAP_side"] = (c > I["vwap"], c < I["vwap"])
    F["HTF_trend"] = (I["htf"] > 0, I["htf"] < 0)
    F["Ichimoku_cloud"] = (c > I["cloud_top"], c < I["cloud_bot"])
    F["BB_squeeze"] = both(I["squeeze"])
    F["Session_07_20"] = both((I["mod"] >= 420) & (I["mod"] < 1200))
    F["above_SMA20"] = (c > I["sma20"], c < I["sma20"])
    e20 = I["ema20"]; sl = np.r_[np.zeros(3), e20[3:] - e20[:-3]]; F["EMA20_slope"] = (sl > 0, sl < 0)
    return {k: (B(a), B(b)) for k, (a, b) in F.items()}


# ------------------------------------------------------------------ Part B strategies (published rule sets)
def strategies(I, T, F):
    c, o, h, l = I["c"], I["o"], I["h"], I["l"]; S = {}; up200, dn200 = F["above_EMA200"]; up50, dn50 = c > I["ema50"], c < I["ema50"]
    p = lambda a: np.r_[False, np.asarray(a)[:-1]]
    S["S01_golden_cross"] = T["EMA50_200_cross"]
    S["S02_MACD_EMA200"] = (T["MACD_signal_cross"][0] & up200 & (I["macd"] < 0), T["MACD_signal_cross"][1] & dn200 & (I["macd"] > 0))
    S["S03_Connors_RSI2"] = ((c > I["sma200"]) & (I["rsi2"] < 10), (c < I["sma200"]) & (I["rsi2"] > 90))
    S["S04_BB_RSI_reversion"] = ((c < I["bbl"]) & (I["rsi14"] < 30), (c > I["bbu"]) & (I["rsi14"] > 70))
    S["S05_Supertrend_EMA200"] = (T["Supertrend_flip"][0] & up200, T["Supertrend_flip"][1] & dn200)
    al_u = (I["ema9"] > I["ema21"]) & (I["ema21"] > I["ema55"]); al_d = (I["ema9"] < I["ema21"]) & (I["ema21"] < I["ema55"])
    S["S06_triple_EMA"] = (al_u & ~p(al_u), al_d & ~p(al_d))
    S["S07_Stoch_trend"] = (T["Stoch_cross_zone"][0] & up200, T["Stoch_cross_zone"][1] & dn200)
    S["S08_Ichimoku_TK_cloud"] = (T["Ichimoku_TK_cross"][0] & F["Ichimoku_cloud"][0], T["Ichimoku_TK_cross"][1] & F["Ichimoku_cloud"][1])
    S["S09_Turtle_20"] = T["Donchian20_break"]
    sq = (I["bbu"] < I["kcu"]) & (I["bbl"] > I["kcl"]); was = p(sq)
    S["S10_TTM_squeeze_break"] = (was & ~sq & (c > I["bbm"]), was & ~sq & (c < I["bbm"]))
    S["S11_PSAR_EMA200"] = (T["PSAR_flip"][0] & up200, T["PSAR_flip"][1] & dn200)
    S["S12_HeikinAshi_EMA50"] = (T["HeikinAshi_flip"][0] & up50, T["HeikinAshi_flip"][1] & dn50)
    S["S13_DI_cross_ADX25"] = (T["DI_cross"][0] & (I["adx"] > 25), T["DI_cross"][1] & (I["adx"] > 25))
    S["S14_CCI_EMA200"] = (T["CCI_100"][0] & up200, T["CCI_100"][1] & dn200)
    S["S15_WilliamsR_pullback"] = (T["WilliamsR_80_20"][0] & up50, T["WilliamsR_80_20"][1] & dn50)
    ib = p((h < np.r_[np.inf, h[:-1]]) & (l > np.r_[-np.inf, l[:-1]])); ph, pl = np.r_[np.nan, h[:-1]], np.r_[np.nan, l[:-1]]
    S["S16_inside_bar_break"] = (ib & (c > ph) & up50, ib & (c < pl) & dn50)
    po, pcl = np.r_[np.nan, o[:-1]], np.r_[np.nan, c[:-1]]
    S["S17_engulfing_trend"] = ((c > o) & (pcl < po) & (c >= po) & (o <= pcl) & up50, (c < o) & (pcl > po) & (c <= po) & (o >= pcl) & dn50)
    S["S18_VWAP_EMA200"] = (x_up(c, I["vwap"]) & up200, x_dn(c, I["vwap"]) & dn200)
    S["S19_MACD_RSI50"] = (T["MACD_signal_cross"][0] & (I["rsi14"] > 50), T["MACD_signal_cross"][1] & (I["rsi14"] < 50))
    rib_u = (I["ema9"] > I["ema21"]) & (I["ema21"] > I["ema55"]) ; e21 = I["ema21"]
    S["S20_EMA_ribbon_pullback"] = (rib_u & (l <= e21) & (c > e21), al_d & (h >= e21) & (c < e21))
    S["S21_AO_EMA200"] = (T["AO_zero"][0] & up200, T["AO_zero"][1] & dn200)
    S["S22_Aroon_EMA200"] = (T["Aroon_cross"][0] & up200, T["Aroon_cross"][1] & dn200)
    g3 = (c > o) & p(c > o) & p(p(c > o)) & (c > np.r_[np.nan, c[:-1]]) & p(c > np.r_[np.nan, c[:-1]]); r3 = (c < o) & p(c < o) & p(p(c < o)) & (c < np.r_[np.nan, c[:-1]]) & p(c < np.r_[np.nan, c[:-1]])
    S["S23_three_soldiers"] = (g3 & ~p(g3), r3 & ~p(r3))
    r14 = I["rsi14"]; ll14, rl14 = roll_prev_min(l, 14), roll_prev_min(r14, 14); hh14, rh14 = roll_prev_max(h, 14), roll_prev_max(r14, 14)
    S["S24_RSI_divergence"] = ((l < ll14) & (r14 > rl14) & (r14 < 40), (h > hh14) & (r14 < rh14) & (r14 > 60))
    S["S25_Keltner_pullback_ADX"] = ((I["adx"] > 25) & up50 & (l <= I["ema20"]) & (c > I["ema20"]), (I["adx"] > 25) & dn50 & (h >= I["ema20"]) & (c < I["ema20"]))
    return {k: (B(a), B(b)) for k, (a, b) in S.items()}


# ------------------------------------------------------------------ Part C theories
def theories(I, tf, market):
    c, o, h, l, t, day, mod = I["c"], I["o"], I["h"], I["l"], I["t"], I["day"], I["mod"]; N = len(c); Th = {}
    Th["T1_theory2_prevday_zone"] = ((l <= I["pdl"]) & (c > I["pdl"]), (h >= I["pdh"]) & (c < I["pdh"]))
    h2, l2 = np.r_[np.nan, np.nan, h[:-2]], np.r_[np.nan, np.nan, l[:-2]]
    Th["T2_FVG"] = (l > h2, h < l2)
    ph20, pl20 = roll_prev_max(h, 20), roll_prev_min(l, 20)
    Th["T3_liquidity_sweep"] = ((l < pl20) & (c > pl20), (h > ph20) & (c < ph20))
    # 5-bar fractal swings, confirmed 2 bars later
    fh = np.zeros(N, bool); fl = np.zeros(N, bool)
    fh[2:-2] = (h[2:-2] > h[1:-3]) & (h[2:-2] > h[:-4]) & (h[2:-2] > h[3:-1]) & (h[2:-2] > h[4:])
    fl[2:-2] = (l[2:-2] < l[1:-3]) & (l[2:-2] < l[:-4]) & (l[2:-2] < l[3:-1]) & (l[2:-2] < l[4:])
    sh = pd.Series(np.where(fh, h, np.nan)).shift(2).ffill().values; slw = pd.Series(np.where(fl, l, np.nan)).shift(2).ffill().values
    Th["T4_break_of_structure"] = (x_up(c, sh), x_dn(c, slw))
    if tf <= 60:
        if market in ("US500m", "USTECm", "XAUUSDm", "USOILm"): op = np.where(dst_us(day), 810, 870)          # NY cash open 13:30/14:30 UTC
        elif market == "DE30m": op = np.where(dst_eu(day), 420, 480)                                         # Xetra 07:00/08:00 UTC
        else: op = np.zeros(N, dtype=int)                                                                      # crypto: 00:00 UTC
        inr = (mod >= op) & (mod + tf <= op + 60); key = day
        rh = pd.Series(np.where(inr, h, np.nan)).groupby(key).transform("max").values; rl = pd.Series(np.where(inr, l, np.nan)).groupby(key).transform("min").values
        after = mod >= op + 60
        bu = after & (c > rh); bd = after & (c < rl)
        first = lambda m: m & (pd.Series(m.astype(int)).groupby(key).cumsum().values == 1)
        Th["T5_opening_range_break"] = (first(bu), first(bd))
        ina = mod < 420
        ah = pd.Series(np.where(ina, h, np.nan)).groupby(key).transform("max").values; al = pd.Series(np.where(ina, l, np.nan)).groupby(key).transform("min").values
        win = (mod >= 420) & (mod < 720)
        Th["T6_asian_range_break"] = (first(win & (c > ah)), first(win & (c < al)))
    from numpy.lib.stride_tricks import sliding_window_view as sw
    W = 20; hw, lw = sw(h, W), sw(l, W); ih, il = hw.argmax(1), lw.argmin(1); Hh, Ll = hw.max(1), lw.min(1)
    pad = lambda x: np.r_[np.full(W - 1, np.nan), x]
    Hh, Ll, ih, il = pad(Hh), pad(Ll), pad(ih.astype(float)), pad(il.astype(float))
    s50 = I["sma50"]; fu = Hh - 0.618 * (Hh - Ll); fd = Ll + 0.618 * (Hh - Ll)
    Th["T7_fib618_reclaim"] = ((c > s50) & (ih > il) & x_up(c, fu), (c < s50) & (il > ih) & x_dn(c, fd))
    Th["T8_prev_week_break"] = (x_up(c, I["pwh"]), x_dn(c, I["pwl"]))
    vu, vl = I["vwap"] + 2 * I["vwsd"], I["vwap"] - 2 * I["vwsd"]
    Th["T9_VWAP_2sd_revert"] = (x_up(c, vl), x_dn(c, vu))
    return {k: (B(a), B(b)) for k, (a, b) in Th.items()}
