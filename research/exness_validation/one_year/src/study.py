"""ONE-YEAR EXNESS BTCUSDm VALIDATION of the frozen Donchian 20 strategy (research only; no live trading).

Pre-specified design (written before any one-year result was computed):
  PRIMARY window: 2025-11-01 00:00 UTC .. 2026-11-01 00:00 UTC (signal candle close inside the window).
  Older Exness data (from 2019-01) is used ONLY for indicator warm-up. No older trades are reported.
  Strategy: the frozen engine (research/btc_breakout/src/engine.py, read-only), model M2_DONCHIAN20, LONG, TRAIL, defaults:
            Donchian 20 on previous completed 1H candles, closed-4H EMA200 filter, ATR14 Wilder, initial stop 2 x ATR,
            trailing stop 3 x ATR, one position at a time, 0.5% equity risk per trade.
  Exness candles: BID prices (as MT5 charts), built from Exness ticks; gaps are never filled.
  A. Frozen engine on Exness bid candles and on Binance BTCUSDT candles, independently: signals, entries, exits, R.
  B. Tick replay on Exness (SIMULATED fills from historical ticks; NOT broker executions):
     entry  = ASK of the first tick at or after the signal-candle close T (variant: first tick at or after T + 8 min);
     stop   = entry fill - 2 x ATR14 (signal candle); every 1H close: stop = max(stop, best 1H bid close - 3 x ATR14);
     exit   = BID of the first tick with bid <= stop (gaps fill at the worse tick price).
     The spread is paid via ask-in / bid-out. Commission: 0 on the Standard account (advertised, UNVERIFIED).
     Swap/admin fees: UNKNOWN; the report gives swap-days and break-even fees plus labelled hypothetical sensitivities.
  C. Parity: a candle-level replay must reproduce the frozen engine trades exactly before being used.
  D. Statistics: win rate, PF, expectancy, max drawdown, longest losing streak, monthly, t and bootstrap 95% CI,
     regimes, and a matched random-entry benchmark (1000 runs, same execution model, unconditional and 4H-uptrend-only).
  E. Data quality: every missing Exness period in the window and its effect on each signal and trade; clean-data subset.
"""
import calendar, csv, glob, gzip, io, json, math, os, random, statistics, sys, time, zipfile
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OY = os.path.dirname(HERE); EV = os.path.dirname(OY); REPO = os.path.dirname(os.path.dirname(EV))
sys.path.insert(0, os.path.join(REPO, "research", "btc_breakout", "src"))
from engine import Lab, last_closed  # frozen, read-only
TMP = os.environ["STUDY_TMP"]; TICKS = os.environ["TICK_DIR"]
W0, W1 = calendar.timegm((2025, 11, 1, 0, 0, 0)), calendar.timegm((2026, 11, 1, 0, 0, 0))
RISK, LAT = 0.005, 8 * 60
rng = random.Random(20261110)
fmt = lambda t: time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


# ------------------------------------------------------------------ data
def exness_candles():
    rows = []
    for f in sorted(glob.glob(os.path.join(EV, "data", "bars15m", "BTCUSDm_*.csv.gz"))):
        rows += list(csv.DictReader(gzip.open(f, "rt")))
    rows.sort(key=lambda r: int(r["open_time_utc"]))
    m15 = [[int(r["open_time_utc"]), float(r["bid_o"]), float(r["bid_h"]), float(r["bid_l"]), float(r["bid_c"]), float(r["ticks"])] for r in rows]
    spread_open = {int(r["open_time_utc"]): float(r["spread_open"]) for r in rows}
    def res(step):
        out, cur = [], None
        for t, o, h, l, c, v in m15:
            b = t - t % step
            if cur and cur[0] == b: cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c; cur[5] += v; cur[6] += 1
            else:
                if cur: out.append(cur)
                cur = [b, o, h, l, c, v, 1]
        out.append(cur); return out
    s = {"15m": [r + [1] for r in m15], "1h": res(3600), "4h": res(14400), "1d": res(86400)}
    d = os.path.join(TMP, "exness_bid"); os.makedirs(d, exist_ok=True)
    for tf, v in s.items(): json.dump([x[:6] for x in v], open(os.path.join(d, f"btc_{tf}.json"), "w"))
    counts = {tf: {x[0]: x[6] for x in v} for tf, v in s.items()}  # number of 15m bars inside each candle
    return d, spread_open, counts, m15


def binance_dir():
    d = os.path.join(TMP, "binance"); os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(REPO, "research", "btc_breakout", "data", "btc_*.json.gz")):
        open(os.path.join(d, os.path.basename(f)[:-3]), "wb").write(gzip.open(f).read())
    return d


def load_ticks():
    ts, bid, ask = [], [], []
    for f in sorted(glob.glob(os.path.join(TICKS, "Exness_BTCUSDm_*.zip"))):
        with zipfile.ZipFile(f) as z:
            df = pd.read_csv(z.open(z.namelist()[0]), usecols=["Timestamp", "Bid", "Ask"])
        t = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S.%fZ", utc=True)
        ts.append(((t - pd.Timestamp("1970-01-01", tz="UTC")) // pd.Timedelta(milliseconds=1)).to_numpy(np.int64))
        bid.append(df["Bid"].to_numpy(np.float64)); ask.append(df["Ask"].to_numpy(np.float64))
    ts, bid, ask = np.concatenate(ts), np.concatenate(bid), np.concatenate(ask)
    o = np.argsort(ts, kind="stable"); return ts[o], bid[o], ask[o]


# ------------------------------------------------------------------ candidate signals (frozen engine functions)
def candidates(L):
    E = L.B["1h"]; sig = L.signals("1h", "M2_DONCHIAN20", 1); out = []
    for i in range(len(E["t"])):
        tc = E["t"][i] + 3600
        if sig[i] and W0 <= tc <= W1:
            H = L.B["4h"]; k = last_closed(H["t"], 14400, tc)
            out.append(dict(i=i, tc=tc, trend_ok=H["c"][k] > H["e200"][k], close=E["c"][i], atr=E["atr"][i], hh20=E["hh"][20][i], k4=k))
    return out


# ------------------------------------------------------------------ candle-level replay (parity + random benchmark)
def candle_replay(L, entries, spread_open=None, use_ask=False):
    """entries: chronological signal closes tc (with signal index i). Frozen rules on candles; optional ask fill."""
    E, P = L.B["1h"], L.B["15m"]; pidx = L.p_idx; t1 = {t + 3600: k for k, t in enumerate(E["t"])}; res = []; busy = -1
    for e in entries:
        tc, i = e["tc"], e["i"]
        if tc <= busy: continue
        j = pidx.get(tc)
        if j is None: continue
        bid_open = P["o"][j]; fill = bid_open + (spread_open.get(P["t"][j], float("nan")) if use_ask else 0.0)
        anchor = fill if use_ask else bid_open
        sl = anchor - 2 * E["atr"][i]; risk = abs(anchor - sl); best = anchor; R = None
        while j < len(P["t"]):
            if P["l"][j] <= sl:
                px = P["o"][j] if P["o"][j] < sl else sl; R = (px - fill) / risk; break
            bc = P["t"][j] + 900
            if bc % 3600 == 0 and bc in t1:
                best = max(best, P["c"][j]); sl = max(sl, best - 3 * E["atr"][t1[bc]])
            if bc >= W1: R = (P["c"][j] - fill) / risk; break
            j += 1
        if R is None: j = len(P["t"]) - 1; R = (P["c"][j] - fill) / risk
        t_exit = P["t"][j] + 900; busy = t_exit
        res.append(dict(entry_time=tc, exit_time=t_exit, R=R, risk=risk, fill=fill))
    return res


# ------------------------------------------------------------------ tick replay (realistic simulated execution)
def tick_replay(L, cands, ticks, latency=0):
    ts, bid, ask = ticks; E = L.B["1h"]; t1 = {t + 3600: k for k, t in enumerate(E["t"])}; out = []; busy = -1
    for c in cands:
        if not c["trend_ok"] or c["tc"] <= busy: continue
        a = int(np.searchsorted(ts, (c["tc"] + latency) * 1000, side="left"))
        if a >= len(ts): break
        fill = ask[a]; t_fill = ts[a] / 1000; atr = c["atr"]; sl = fill - 2 * atr; risk = 2 * atr; best = fill
        hours = [h for h in range(int(c["tc"]) + 3600, W1 + 1, 3600)]; seg_start = a; exit_px = exit_t = None; reason = None; missed_updates = 0
        for h in hours + [None]:
            seg_end = int(np.searchsorted(ts, h * 1000, side="left")) if h else len(ts)
            if h is None or h > W1: seg_end = int(np.searchsorted(ts, W1 * 1000, side="left"))
            seg = bid[seg_start:seg_end]
            hit = np.nonzero(seg <= sl)[0]
            if hit.size:
                k = seg_start + int(hit[0]); exit_px = bid[k]; exit_t = ts[k] / 1000; reason = "stop"; break
            if h is None or h >= W1:
                k = max(seg_end - 1, a); exit_px = bid[k]; exit_t = ts[k] / 1000; reason = "window_end"; break
            if h in t1:
                kk = t1[h]; best = max(best, E["c"][kk]); sl = max(sl, best - 3 * E["atr"][kk])
            else:
                missed_updates += 1
            seg_start = seg_end
        sd = swap_days(t_fill, exit_t)
        out.append(dict(signal_close=c["tc"], entry_time=t_fill, entry_ask=fill, entry_bid=bid[a], spread_entry=fill - bid[a],
                        entry_delay_s=t_fill - c["tc"], initial_stop=fill - 2 * atr, final_stop=sl, exit_time=exit_t, exit_bid=exit_px,
                        exit_slippage_vs_stop=(sl - exit_px) if reason == "stop" else 0.0, reason=reason, risk=risk,
                        R_net=(exit_px - fill) / risk, hold_h=(exit_t - t_fill) / 3600, swap_days=sd, missed_trail_updates=missed_updates, i=c["i"]))
        busy = exit_t
    return out


def swap_days(t_in, t_out):
    """ASSUMED (unverified) Exness rollover: 21:00 UTC Apr-Oct / 22:00 UTC Nov-Mar, triple on Friday."""
    n = 0; d = int(t_in) - int(t_in) % 86400
    while d <= t_out:
        g = time.gmtime(d); cut = d + (21 if 4 <= g.tm_mon <= 10 else 22) * 3600
        if t_in < cut <= t_out: n += 3 if g.tm_wday == 4 else 1
        d += 86400
    return n


# ------------------------------------------------------------------ statistics
def stats(rs, months=None):
    if not rs: return dict(trades=0)
    eq = peak = 1.0; mdd = 0.0; st = worst = 0
    for r in rs:
        eq *= 1 + RISK * r; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak); st = st + 1 if r <= 0 else 0; worst = max(worst, st)
    w = [r for r in rs if r > 0]; l = [r for r in rs if r <= 0]; m = statistics.mean(rs); sd = statistics.stdev(rs) if len(rs) > 1 else 0
    se = sd / math.sqrt(len(rs)) if sd else 0
    boots = sorted(statistics.mean(rng.choices(rs, k=len(rs))) for _ in range(5000))
    return dict(trades=len(rs), win_rate_pct=round(len(w) / len(rs) * 100, 1), profit_factor=round(sum(w) / -sum(l), 3) if l and sum(l) < 0 else None,
                expectancy_R=round(m, 4), avg_R=round(m, 4), t_stat=round(m / se, 2) if se else None,
                ci95_t=[round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], ci95_bootstrap=[round(boots[125], 4), round(boots[4874], 4)],
                max_drawdown_pct=round(mdd * 100, 2), longest_losing_streak=worst, net_return_pct=round((eq - 1) * 100, 2))


def main():
    xdir, spread_open, counts, m15 = exness_candles(); bdir = binance_dir()
    LX, LB = Lab(xdir), Lab(bdir)
    out = {"design": __doc__.strip().splitlines()[0]}
    # ---- A. frozen engine on each dataset
    ex_eng = [t for t in LX.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", W0, W1)]
    bn_eng = [t for t in LB.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", W0, W1)]
    cx, cb = candidates(LX), candidates(LB)
    # ---- C. parity of the candle replay vs frozen engine (zero spread)
    par = candle_replay(LX, [c for c in cx if c["trend_ok"]])
    ndiff = sum(1 for a, b in zip(ex_eng, par) if a["entry_time"] != b["entry_time"] or a["exit_time"] != b["exit_time"] or abs(a["R_gross"] - b["R"]) > 1e-4)
    out["parity_candle_replay_vs_frozen_engine"] = dict(engine_trades=len(ex_eng), replay_trades=len(par), differing_trades=ndiff + abs(len(ex_eng) - len(par)),
                                                        identical=ndiff == 0 and len(ex_eng) == len(par), tolerance_R=1e-4)
    # ---- B. tick replay
    ticks = load_ticks()
    out["ticks"] = dict(count=int(len(ticks[0])), first=fmt(ticks[0][0] / 1000), last=fmt(ticks[0][-1] / 1000),
                        bad_ask_lt_bid=int((ticks[2] < ticks[1]).sum()), non_monotonic=int((np.diff(ticks[0]) < 0).sum()))
    tr0 = tick_replay(LX, cx, ticks, 0); tr8 = tick_replay(LX, cx, ticks, LAT)
    # ---- E. data quality: gaps and their effect
    ts15 = sorted(t for t in counts["15m"] if W0 - 40 * 86400 <= t < W1)
    gaps = [(a + 900, b) for a, b in zip(ts15, ts15[1:]) if b - a > 900]
    gap_list = [dict(start=fmt(a), end=fmt(b), missing_15m=(b - a) // 900) for a, b in gaps]
    def in_gap(t0, t1_):
        return [g for g in gaps if g[0] < t1_ and g[1] > t0]
    E1 = LX.B["1h"]
    def flags_for_signal(c, hold=None):
        f = []
        i = c["i"]; tc = c["tc"]
        if counts["1h"].get(E1["t"][i], 0) < 4: f.append("signal candle incomplete")
        lb = E1["t"][i - 20:i]
        if lb and (lb[-1] - lb[0] != 19 * 3600 or any(counts["1h"].get(t, 0) < 4 for t in lb)): f.append("Donchian lookback spans missing/incomplete hours")
        H = LX.B["4h"]; k = c["k4"]
        if counts["4h"].get(H["t"][k], 0) < 16: f.append("4H trend candle incomplete")
        if in_gap(H["t"][max(0, k - 200)], H["t"][k] + 14400): f.append("gap inside 200 x 4H EMA window (minor)")
        if hold and in_gap(hold[0], hold[1]): f.append("gap during holding period (stop/trail/exit unverifiable)")
        return f
    for t in tr0:
        c = next(x for x in cx if x["tc"] == t["signal_close"])
        t["data_flags"] = flags_for_signal(c, (t["entry_time"], t["exit_time"]))
        if t["entry_delay_s"] > 900: t["data_flags"].append(f"entry tick delayed {t['entry_delay_s'] / 60:.0f} min")
    sig_flags = [dict(signal_close=fmt(c["tc"]), trend_ok=c["trend_ok"], flags=flags_for_signal(c)) for c in cx]
    serious = lambda fl: [x for x in fl if "minor" not in x]
    out["data_quality"] = dict(gaps_in_window_and_warmup=gap_list, signals_with_flags=[s for s in sig_flags if serious(s["flags"])],
                               trades_with_serious_flags=[dict(signal=fmt(t["signal_close"]), flags=t["data_flags"]) for t in tr0 if serious(t["data_flags"])])
    # ---- D. statistics
    R0 = [t["R_net"] for t in tr0]; R8 = [t["R_net"] for t in tr8]
    clean = [t["R_net"] for t in tr0 if not serious(t["data_flags"])]
    srt = sorted(R0)
    out["robustness"] = dict(median_R=round(statistics.median(R0), 4), expectancy_without_top1=round(statistics.mean(srt[:-1]), 4),
                             expectancy_without_top3=round(statistics.mean(srt[:-3]), 4), top1_share_of_total_R=round(srt[-1] / sum(R0), 2) if sum(R0) > 0 else None,
                             largest_trade_R=round(srt[-1], 3))
    out["results"] = {"exness_tick_replay_entry_first_tick_after_close": stats(R0), "exness_tick_replay_entry_T+8min": stats(R8),
                      "exness_tick_replay_CLEAN_DATA_ONLY": stats(clean),
                      "exness_frozen_engine_bid_candles_no_spread": stats([t["R_gross"] for t in ex_eng]),
                      "binance_frozen_engine_no_costs": stats([t["R_gross"] for t in bn_eng]),
                      "binance_frozen_engine_0.05%_rt_hypothetical": stats([t["R_gross"] - 0.0005 * t["entry"] / t["risk"] for t in bn_eng])}
    # costs: swaps unknown -> break-even + hypothetical sensitivity
    notional_R = [t["entry_ask"] / t["risk"] for t in tr0]; sdays = [t["swap_days"] for t in tr0]
    denom = sum(s * k for s, k in zip(sdays, notional_R))
    out["swap_sensitivity_HYPOTHETICAL"] = dict(
        total_swap_days=sum(sdays), trades_held_over_rollover=sum(1 for s in sdays if s),
        breakeven_swap_pct_of_notional_per_swap_day=round(sum(R0) / denom * 100, 4) if denom and sum(R0) > 0 else "expectancy already <= 0 before swaps",
        expectancy_if_swap_per_day={f"{p}%": round(statistics.mean(r - p / 100 * s * k for r, s, k in zip(R0, sdays, notional_R)), 4) for p in (0.01, 0.02, 0.05)} if R0 else {})
    lots = [RISK * 2722.94 / t["risk"] for t in tr0]
    out["commission_sensitivity_HYPOTHETICAL"] = {f"{usd}_usd_per_lot_round_trip": round(statistics.mean(r - usd / t["risk"] for r, t in zip(R0, tr0)), 4) for usd in (0, 2, 4, 8)} if R0 else {}
    # monthly
    mon = {}
    for t in tr0:
        m = time.strftime("%Y-%m", time.gmtime(t["exit_time"])); e = mon.setdefault(m, [0, 0.0, 0]); e[0] += 1; e[1] += t["R_net"]; e[2] += t["R_net"] > 0
    allm = []
    y, mo = 2025, 11
    while (y, mo) <= (2026, 10): allm.append(f"{y}-{mo:02d}"); y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
    for m in allm: mon.setdefault(m, [0, 0.0, 0])
    out["monthly_by_exit"] = {m: dict(trades=v[0], wins=v[2], sum_R=round(v[1], 3), approx_return_pct=round(v[1] * RISK * 100, 2)) for m, v in sorted(mon.items())}
    # regimes
    reg = {}
    for t in tr0:
        g = LX.regime(t["signal_close"]); reg.setdefault(g, []).append(t["R_net"])
    out["regimes"] = {g: stats(v) for g, v in reg.items()}
    # ---- A/B comparison Exness vs Binance
    sx = {c["tc"]: c for c in cx}; sb = {c["tc"]: c for c in cb}
    both = sorted(set(sx) & set(sb)); only_x = sorted(set(sx) - set(sb)); only_b = sorted(set(sb) - set(sx))
    trend_disagree = [fmt(t) for t in both if sx[t]["trend_ok"] != sb[t]["trend_ok"]]
    ex_by = {t["entry_time"]: t for t in ex_eng}; bn_by = {t["entry_time"]: t for t in bn_eng}
    matched = sorted(set(ex_by) & set(bn_by))
    out["exness_vs_binance"] = dict(
        breakout_signals=dict(exness=len(sx), binance=len(sb), same_hour=len(both), only_exness=len(only_x), only_binance=len(only_b),
                              trend_filter_disagreements=trend_disagree, only_exness_list=[fmt(t) for t in only_x], only_binance_list=[fmt(t) for t in only_b]),
        trades=dict(exness=len(ex_eng), binance=len(bn_eng), same_entry_hour=len(matched),
                    same_exit_time=sum(1 for t in matched if ex_by[t]["exit_time"] == bn_by[t]["exit_time"]),
                    median_entry_price_diff_pct=round(statistics.median((ex_by[t]["entry"] - bn_by[t]["entry"]) / bn_by[t]["entry"] * 100 for t in matched), 4) if matched else None,
                    median_abs_R_diff=round(statistics.median(abs(ex_by[t]["R_gross"] - bn_by[t]["R_gross"]) for t in matched), 3) if matched else None))
    # ---- matched random-entry benchmark (candle-level, ask fill + bid stops; same model applied to the strategy)
    strat_candle = candle_replay(LX, [c for c in cx if c["trend_ok"]], spread_open, use_ask=True)
    strat_mean = statistics.mean(t["R"] for t in strat_candle if not math.isnan(t["R"]))
    hours_all = [dict(tc=t + 3600, i=k) for k, t in enumerate(E1["t"]) if W0 <= t + 3600 <= W1 and k > 300]
    H4 = LX.B["4h"]
    up = [h for h in hours_all if (lambda k: H4["c"][k] > H4["e200"][k])(last_closed(H4["t"], 14400, h["tc"]))]
    n_att = sum(1 for c in cx if c["trend_ok"])
    def bench(pool):
        means = []
        for _ in range(1000):
            pick = sorted(rng.sample(pool, min(n_att, len(pool))), key=lambda h: h["tc"])
            r = [t["R"] for t in candle_replay(LX, pick, spread_open, use_ask=True) if not math.isnan(t["R"])]
            if r: means.append(statistics.mean(r))
        means.sort(); return dict(runs=len(means), median=round(means[len(means) // 2], 4), p5=round(means[int(.05 * len(means))], 4),
                                  p95=round(means[int(.95 * len(means))], 4), strategy_percentile=round(sum(m < strat_mean for m in means) / len(means) * 100, 1))
    out["random_benchmark"] = dict(strategy_expectancy_same_model=round(strat_mean, 4), strategy_trades_same_model=len(strat_candle),
                                   random_any_hour=bench(hours_all), random_4h_uptrend_hours_only=bench(up))
    # buy & hold over the window (bid)
    D = LX.B["1d"]; di = [k for k, t in enumerate(D["t"]) if W0 <= t < W1]
    out["buy_and_hold_bid_pct"] = round((D["c"][di[-1]] / D["o"][di[0]] - 1) * 100, 2)
    # ---- save
    json.dump(out, open(os.path.join(OY, "results", "one_year_results.json"), "w"), indent=1, default=str)
    for name, rows in (("tick_replay_trades.csv", tr0), ("tick_replay_trades_T+8min.csv", tr8)):
        with open(os.path.join(OY, "trades", name), "w", newline="") as f:
            keys = [k for k in rows[0] if k != "i"] if rows else []
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader()
            for r in rows:
                d = {k: r[k] for k in keys}
                for k in ("signal_close", "entry_time", "exit_time"): d[k] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(r[k]))
                if "data_flags" in d: d["data_flags"] = "; ".join(d["data_flags"])
                w.writerow(d)
    for name, rows in (("frozen_engine_exness_bid.csv", ex_eng), ("frozen_engine_binance.csv", bn_eng)):
        with open(os.path.join(OY, "trades", name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["entry_utc", "exit_utc", "entry", "risk", "R_gross", "exit", "hold_h"]); w.writeheader()
            for t in rows: w.writerow(dict(entry_utc=fmt(t["entry_time"]), exit_utc=fmt(t["exit_time"]), entry=t["entry"], risk=t["risk"], R_gross=t["R_gross"], exit=t["exit"], hold_h=t["hold_h"]))
    print(json.dumps({k: out[k] for k in ("parity_candle_replay_vs_frozen_engine", "ticks", "results", "exness_vs_binance", "random_benchmark", "buy_and_hold_bid_pct")}, indent=1, default=str))


if __name__ == "__main__":
    main()
