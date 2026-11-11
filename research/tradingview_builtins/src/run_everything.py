"""Run the 'everything' phase (PROTOCOL.md): built-in strategies (A), built-in indicators (B), ChartArt community
strategies (C), and the four fixed filters on every 2025-positive variant (D), on US oil, gold and BTC.
Writes reports/results_<market>.json. One process per market."""
import bisect
import json
import multiprocessing
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builtin_strategies as B  # noqa: E402  (imports ports first, which sets up the paths)
import builtin_indicators as I  # noqa: E402
import oil  # noqa: E402
import run_scan  # noqa: E402
import study as S  # noqa: E402
import ta_lib as T  # noqa: E402

MARKETS = {"USOILm": (os.path.join(B.RESEARCH, "oil_rsi_vwap", "data", "USOILm_15m.csv.gz"), False),
           "XAUUSDm": (os.path.join(B.RESEARCH, "gold_rsi_vwap", "data", "XAUUSDm_15m.csv.gz"), False),
           "BTCUSDm": (os.path.join(B.RESEARCH, "community_indicators", "data", "BTCUSDm_15m.csv.gz"), True)}
STANDARD = ("HW", "SYM", "TRAIL")
FILTERS = ("F_4H_EMA200", "F_DAILY_EMA200", "F_ADX14_GT20", "F_SESSION_VWAP")
SEL, CON = "selection 2025", "confirmation 2026"


def eval_held(a, trades, w0, w1):
    s = S.summary([t.r("primary") for t in trades])
    if s["trades"] < 2:
        return s
    s["expectancy_stress_r"] = statistics.mean(t.r("stress") for t in trades)
    s["avg_hold_hours"] = statistics.mean(t.hold_hours for t in trades)
    s.update(a.duration_benchmark(trades, w0, w1))
    return s


def verdict(res):
    sel, con = res[SEL], res[CON]
    res["passes_selection"] = sel["trades"] >= 30 and sel.get("expectancy_r", -1) > 0 and sel.get("p_random", 1) <= 0.05
    res["passes_confirmation"] = con["trades"] >= 20 and con.get("expectancy_r", -1) > 0 and con.get("p_random", 1) <= 0.05
    res["reliable"] = res["passes_selection"] and res["passes_confirmation"]
    res["win_rate_70_both"] = all(r.get("win_rate_pct", 0) >= 70 for r in (sel, con))
    return res


def flip_legs(a, mine, other, d, w0, w1):
    E, n = a.e, len(a.e.t)
    out, i = [], 0
    while i < n:
        if not mine[i] or not (w0 <= E.t[i] + 3600 < w1):
            i += 1
            continue
        j = next((k for k in range(i + 1, n) if other[k]), None)
        if j is None:
            break
        tr = a.hold(i, d, E.t[j] - E.t[i])
        if tr is not None:
            out.append(tr)
        i = j
    return out


def filters(a):
    """Per 1H bar i (known at its close): (buy_ok, sell_ok) for each fixed filter."""
    E = a.e
    n = len(E.t)
    out = {}
    h4 = oil.aggregate(E.t, E.o, E.h, E.l, E.c, E.v, 14400)
    e4 = S.ema_from_first(h4.c, 200)
    b, s = [False] * n, [False] * n
    for i in range(n):
        k = bisect.bisect_right(h4.t, E.t[i] + 3600 - 14400) - 1       # last 4H candle closed by this bar's close
        if k >= 200 and e4[k] is not None:
            b[i], s[i] = h4.c[k] > e4[k], h4.c[k] < e4[k]
    out["F_4H_EMA200"] = (b, s)
    b, s = [False] * n, [False] * n
    for i in range(n):
        k = bisect.bisect_right(a.d.t, E.t[i] + 3600 - 86400) - 1
        if k >= 200 and a.d_e200[k] is not None:
            b[i], s[i] = a.d.c[k] > a.d_e200[k], a.d.c[k] < a.d_e200[k]
    out["F_DAILY_EMA200"] = (b, s)
    adx = T.dmi(E.h, E.l, E.c, 14, 14)[2]
    ok = [x is not None and x > 20 for x in adx]
    out["F_ADX14_GT20"] = (ok, ok)
    out["F_SESSION_VWAP"] = ([w is not None and c > w for c, w in zip(E.c, a.vwap)],
                             [w is not None and c < w for c, w in zip(E.c, a.vwap)])
    return out


def run_market(mkt):
    path, crypto = MARKETS[mkt]
    t0 = time.time()
    log = open(os.path.join(B.ROOT, "reports", f"progress_{mkt}.log"), "w")
    a = B.BuiltinAsset(path, crypto=crypto)
    end = a.e.t[-1] + 3600
    periods = {SEL: (S.ts(2025, 1), S.ts(2026, 1)), CON: (S.ts(2026, 1), end)}
    res_all = {}
    flt = filters(a)

    def record(key, res):
        res_all[key] = verdict(res)
        s, c = res[SEL], res[CON]
        log.write(f"{key:60} sel n={s['trades']:>4} win={s.get('win_rate_pct', 0):5.1f} E={s.get('expectancy_r', 0):+.3f} "
                  f"p={s.get('p_random', 1):.3f} | conf n={c['trades']:>4} win={c.get('win_rate_pct', 0):5.1f} "
                  f"E={c.get('expectancy_r', 0):+.3f} p={c.get('p_random', 1):.3f}{'  RELIABLE' if res['reliable'] else ''} "
                  f"[{time.time() - t0:.0f}s]\n")
        log.flush()

    # A and C: strategies, legs split by direction, evaluated per period
    strat_trades = {}
    for name in B.NAMES + B.CHARTART:
        trades = a.simulate_strategy(name)
        part = "C" if name in B.CHARTART else "A"
        for d in (1, -1):
            legs = [t for t in trades if t.direction == d]
            key = f"{part}|{name}|{'BUY' if d > 0 else 'SELL'}|OWN"
            strat_trades[key] = legs
            record(key, {p: eval_held(a, [t for t in legs if w0 <= t.entry_time < w1], w0, w1) for p, (w0, w1) in periods.items()})
    # B: indicators
    sig = I.signals(a.e)
    for name, (buy, sell) in sig.items():
        flip = I.alternates(buy, sell)
        for d, mine, other in ((1, buy, sell), (-1, sell, buy)):
            dn = "BUY" if d > 0 else "SELL"
            for ex in STANDARD:
                record(f"B|{name}|{dn}|{ex}", {p: run_scan.evaluate(a, a.run_signals(mine, d, ex, w0, w1), d, ex, w0, w1)
                                              for p, (w0, w1) in periods.items()})
            if flip:
                record(f"B|{name}|{dn}|FLIP", {p: eval_held(a, flip_legs(a, mine, other, d, w0, w1), w0, w1)
                                              for p, (w0, w1) in periods.items()})
    # D: every 2025-positive variant x each fixed filter (filter applied at the signal bar)
    base = [k for k, r in res_all.items() if r[SEL]["trades"] >= 2 and r[SEL].get("expectancy_r", -1) > 0]
    for key in base:
        part, name, dn, ex = key.split("|")
        d = 1 if dn == "BUY" else -1
        for fname in FILTERS:
            ok = flt[fname][0 if d > 0 else 1]
            res = {}
            for p, (w0, w1) in periods.items():
                if part in ("A", "C"):
                    res[p] = eval_held(a, [t for t in strat_trades[key] if w0 <= t.entry_time < w1 and ok[t.signal_index]], w0, w1)
                else:
                    buy, sell = sig[name]
                    mine, other = (buy, sell) if d > 0 else (sell, buy)
                    fm = [m and f for m, f in zip(mine, ok)]
                    if ex == "FLIP":
                        res[p] = eval_held(a, flip_legs(a, fm, other, d, w0, w1), w0, w1)
                    else:
                        res[p] = run_scan.evaluate(a, a.run_signals(fm, d, ex, w0, w1), d, ex, w0, w1)
            record(f"D|{name}+{fname}|{dn}|{ex}", res)
    out = {"meta": {"generated_utc": S.fmt(time.time()), "runs": 1000, "seconds": round(time.time() - t0)}, "results": res_all}
    with open(os.path.join(B.ROOT, "reports", f"results_{mkt}.json"), "w") as f:
        json.dump(out, f, indent=1)
    log.write(f"done in {time.time() - t0:.0f}s\n")
    return mkt


def main():
    os.makedirs(os.path.join(B.ROOT, "reports"), exist_ok=True)
    mkts = sys.argv[1:] or list(MARKETS)
    with multiprocessing.Pool(len(mkts)) as pool:
        for m in pool.imap_unordered(run_market, mkts):
            print("finished", m, flush=True)


if __name__ == "__main__":
    main()
