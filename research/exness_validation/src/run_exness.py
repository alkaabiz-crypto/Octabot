"""Run the FROZEN Donchian 20 strategy on Exness BTCUSDm tick-derived candles and compare it with Binance BTCUSDT.

The frozen engine (research/btc_breakout/src/engine.py) is imported read-only and called with its locked defaults:
simulate("1h", "M2_DONCHIAN20", LONG, "TRAIL"). No rule or parameter is changed.

Price convention on Exness (documented, not a rule change):
  - Signals, ATR, the 4H EMA200 and stop triggers use BID candles, which is what MT5 charts show and what triggers a long's sell stop.
  - A buy fills at the ASK. The engine's entry is the 15m bid open; the real fill = bid open + the measured spread at
    that 15m open (spread_open column). The exit is at the bid, which is the engine's exit price.
  - Deviation: the engine anchors the initial stop to the bid open, so it sits one spread below where an MT5 stop
    placed "fill - 2 x ATR" would be (about 25-40 USD vs about 800 USD of risk). This is reported as an approximation.

Cost layers:
  - MEASURED: the Exness bid/ask spread from tick data.
  - HYPOTHETICAL slippage: 0 / 0.01% / 0.03% of price per side (not measured).
  - UNKNOWN: commission (account dependent; Standard advertises none, unverified), and overnight swap or admin fee
    (rates not obtainable). For these, the report gives nights held and the break-even fee per night, NOT a cost.
R is the rule risk = 2 x ATR14 at the signal (the engine's risk). Sizing for returns: 0.5% of equity per R, compounding.
"""
import calendar, csv, glob, gzip, json, math, os, statistics, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); REPO = os.path.dirname(os.path.dirname(ROOT))
sys.path.insert(0, os.path.join(REPO, "research", "btc_breakout", "src"))
from engine import Lab  # frozen, read-only
from protocol import WINDOWS  # frozen research windows (2020H1..2025H1)

END = calendar.timegm((2026, 11, 1, 0, 0, 0))  # last Exness month processed: 2026-10 (no overlap with the forward test)
HOLDOUT = ("HOLDOUT_to_2026-10", calendar.timegm((2025, 7, 1, 0, 0, 0)), END)
CONTINUOUS = ("CONTINUOUS_2020-01_to_2026-10", calendar.timegm((2020, 1, 1, 0, 0, 0)), END)
SLIP = {"spread_only": 0.0, "spread+slip_0.01%": 0.0001, "spread+slip_0.03%": 0.0003}
BINANCE_COST = {"binance_gross": 0.0, "binance_0.05%_rt_hypothetical": 0.0005, "binance_0.10%_rt_hypothetical": 0.0010}
RISK = 0.005
TF = {"1h": 3600, "4h": 14400, "1d": 86400}


def load_exness():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "bars15m", "BTCUSDm_*.csv.gz"))):
        rows += list(csv.DictReader(gzip.open(f, "rt")))
    m15 = [[int(r["open_time_utc"]), float(r["bid_o"]), float(r["bid_h"]), float(r["bid_l"]), float(r["bid_c"]), float(r["ticks"])] for r in rows]
    spread_open = {int(r["open_time_utc"]): float(r["spread_open"]) for r in rows}
    return m15, spread_open, rows


def resample(m15, step):
    out, cur = [], None
    for t, o, h, l, c, v in m15:
        b = t - t % step
        if cur and cur[0] == b:
            cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c; cur[5] += v
        else:
            if cur: out.append(cur)
            cur = [b, o, h, l, c, v]
    out.append(cur)
    return out


def gaps(series, step):
    return [(a[0], b[0]) for a, b in zip(series, series[1:]) if b[0] - a[0] != step]


def nights(t_in, t_out):
    """Count daily swap cut-offs crossed. ASSUMED cut-off 21:00 UTC (Apr-Oct) / 22:00 UTC (Nov-Mar) and triple on Friday,
    taken from unverified secondary descriptions of Exness. Returns (cutoffs crossed, swap-days charged incl. triple)."""
    n = days = 0; d = t_in - t_in % 86400
    while d <= t_out:
        mo = time.gmtime(d).tm_mon; cut = d + (21 if 4 <= mo <= 10 else 22) * 3600
        if t_in < cut <= t_out:
            n += 1; days += 3 if time.gmtime(d).tm_wday == 4 else 1
        d += 86400
    return n, days


def metrics(rs, extra=None):
    if not rs: return dict(trades=0)
    eq = peak = 1.0; mdd = 0.0; streak = worst = 0
    for r in rs:
        eq *= 1 + RISK * r; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
        streak = streak + 1 if r <= 0 else 0; worst = max(worst, streak)
    w = [r for r in rs if r > 0]; l = [r for r in rs if r <= 0]; m = statistics.mean(rs); sd = statistics.stdev(rs) if len(rs) > 1 else 0
    d = dict(trades=len(rs), expectancy_R=round(m, 4), t_stat=round(m / (sd / math.sqrt(len(rs))), 2) if sd else None,
             profit_factor=round(sum(w) / -sum(l), 3) if l and sum(l) < 0 else None, win_rate_pct=round(len(w) / len(rs) * 100, 1),
             max_drawdown_pct=round(mdd * 100, 2), longest_losing_streak=worst, net_return_pct=round((eq - 1) * 100, 2))
    if extra: d.update(extra)
    return d


def run(L, w0, w1):
    return L.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", w0, w1)


def main():
    tmp = os.environ.get("EXNESS_TMP", "/tmp"); xdir = os.path.join(tmp, "exness_engine_input"); os.makedirs(xdir, exist_ok=True)
    m15, spread_open, raw = load_exness()
    series = {"15m": m15, "1h": resample(m15, 3600), "4h": resample(m15, 14400), "1d": resample(m15, 86400)}
    for tf, s in series.items():
        json.dump(s, open(os.path.join(xdir, f"btc_{tf}.json"), "w"))
    data_quality = {tf: dict(candles=len(s), first=time.strftime("%Y-%m-%d %H:%M", time.gmtime(s[0][0])),
                             last=time.strftime("%Y-%m-%d %H:%M", time.gmtime(s[-1][0])), gaps=len(gaps(s, 900 if tf == "15m" else TF[tf])),
                             missing_periods=sum((b - a) // (900 if tf == "15m" else TF[tf]) - 1 for a, b in gaps(s, 900 if tf == "15m" else TF[tf])))
                    for tf, s in series.items()}
    LX = Lab(xdir)
    LB = Lab(os.path.join(tmp, "binance_engine_input"))
    out = dict(data_quality=data_quality, periods={})
    for name, w0, w1 in [("WALKFORWARD_2020H1-2025H1", None, None), HOLDOUT, CONTINUOUS]:
        if name.startswith("WALKFORWARD"):
            tx = [t for _, a, b in WINDOWS for t in run(LX, a, b)]; tb = [t for _, a, b in WINDOWS for t in run(LB, a, b)]
        else:
            tx = run(LX, w0, w1); tb = run(LB, w0, w1)
        tx = [t for t in tx if t["exit"] != "data_end"]; tb = [t for t in tb if t["exit"] != "data_end"]
        res = {}
        recs = []
        for t in tx:
            s_open = spread_open.get(t["entry_time"])
            ask_entry = t["entry"] + (s_open if s_open is not None else float("nan"))
            exit_bid = t["entry"] + t["R_gross"] * t["risk"]
            n, sd = nights(t["entry_time"], t["exit_time"])
            recs.append(dict(entry_time=t["entry_time"], exit_time=t["exit_time"], bid_entry=t["entry"], ask_entry=ask_entry, exit_bid=exit_bid,
                             risk=t["risk"], spread_at_entry=s_open, R_bid_gross=t["R_gross"], hold_h=t["hold_h"], cutoffs=n, swap_days=sd, regime=t["regime"]))
        missing_spread = sum(1 for r in recs if r["spread_at_entry"] is None)
        for k, slip in SLIP.items():
            rs = [(r["exit_bid"] - r["ask_entry"] - slip * (r["ask_entry"] + r["exit_bid"])) / r["risk"] for r in recs if r["spread_at_entry"] is not None]
            res[f"exness_{k}"] = metrics(rs)
        res["exness_bid_gross_no_costs"] = metrics([r["R_bid_gross"] for r in recs])
        for k, c in BINANCE_COST.items():
            res[k] = metrics([t["R_gross"] - c * t["entry"] / t["risk"] for t in tb])
        # break-even overnight fee per swap-day (as % of notional) for spread-only expectancy
        base = [(r["exit_bid"] - r["ask_entry"]) / r["risk"] for r in recs if r["spread_at_entry"] is not None]
        sdays = [r["swap_days"] for r in recs if r["spread_at_entry"] is not None]
        notional_R = [r["ask_entry"] / r["risk"] for r in recs if r["spread_at_entry"] is not None]
        denom = sum(d * k for d, k in zip(sdays, notional_R))
        be = (sum(base) / denom * 100) if denom else None
        common = {t["entry_time"] for t in tb} & {r["entry_time"] for r in recs}
        out["periods"][name] = dict(results=res, exness_trades_missing_spread=missing_spread,
                                    nights=dict(trades_held_overnight=sum(1 for d in sdays if d), mean_swap_days=round(statistics.mean(sdays), 2) if sdays else None,
                                                breakeven_fee_pct_of_notional_per_swap_day=round(be, 4) if be else None),
                                    trade_overlap=dict(exness=len(recs), binance=len(tb), same_signal_hour=len(common)),
                                    spread_at_entry=dict(median=round(statistics.median([r["spread_at_entry"] for r in recs if r["spread_at_entry"] is not None]), 2) if recs else None,
                                                         median_pct=round(statistics.median([r["spread_at_entry"] / r["bid_entry"] * 100 for r in recs if r["spread_at_entry"] is not None]), 4) if recs else None))
        if name.startswith("CONTINUOUS"):
            monthly = {}
            for k, slip in (("exness_spread_only", 0.0), ("exness_spread+slip_0.03%", 0.0003)):
                for r in recs:
                    if r["spread_at_entry"] is None: continue
                    mth = time.strftime("%Y-%m", time.gmtime(r["exit_time"]))
                    R = (r["exit_bid"] - r["ask_entry"] - slip * (r["ask_entry"] + r["exit_bid"])) / r["risk"]
                    m = monthly.setdefault(mth, {}); e = m.setdefault(k, [0, 0.0]); e[0] += 1; e[1] += R
            for t in tb:
                mth = time.strftime("%Y-%m", time.gmtime(t["exit_time"]))
                e = monthly.setdefault(mth, {}).setdefault("binance_0.05%_rt_hypothetical", [0, 0.0]); e[0] += 1; e[1] += t["R_gross"] - 0.0005 * t["entry"] / t["risk"]
            out["monthly_R_by_exit_month"] = {m: {k: dict(trades=v[0], sum_R=round(v[1], 3), return_pct_approx=round(v[1] * RISK * 100, 2)) for k, v in d.items()} for m, d in sorted(monthly.items())}
            with open(os.path.join(ROOT, "reports", "exness_trades_continuous.csv"), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=["entry_utc", "exit_utc", "bid_entry", "spread_at_entry", "ask_entry", "exit_bid", "risk_R_usd", "R_bid_gross",
                                                  "R_spread_only", "hold_h", "swap_cutoffs_crossed_assumed", "swap_days_assumed", "regime"])
                w.writeheader()
                for r in recs:
                    w.writerow(dict(entry_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["entry_time"])), exit_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(r["exit_time"])),
                                    bid_entry=r["bid_entry"], spread_at_entry=r["spread_at_entry"], ask_entry=round(r["ask_entry"], 2), exit_bid=round(r["exit_bid"], 2),
                                    risk_R_usd=round(r["risk"], 2), R_bid_gross=round(r["R_bid_gross"], 4),
                                    R_spread_only=round((r["exit_bid"] - r["ask_entry"]) / r["risk"], 4) if r["spread_at_entry"] is not None else "",
                                    hold_h=r["hold_h"], swap_cutoffs_crossed_assumed=r["cutoffs"], swap_days_assumed=r["swap_days"], regime=r["regime"]))
    json.dump(out, open(os.path.join(ROOT, "reports", "results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "monthly_R_by_exit_month"}, indent=1))


if __name__ == "__main__":
    main()
