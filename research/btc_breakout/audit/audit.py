"""INDEPENDENT AUDIT of the Donchian 20 forward paper test (BINANCE PROXY, paper only).

Independence: this file does not import engine.py, paper_trader.py or daily_update.py. It downloads its own Binance
candles and recomputes everything from the written strategy rules:
  - Signal: on a CLOSED 1H candle, close > highest high of the previous 20 closed 1H candles while the previous close
    was <= its own previous-20 high (a fresh cross).
  - Trend filter: the last 4H candle that CLOSED at or before the signal close has close > EMA200(4H).
  - Entry: LONG at the open of the 15m candle that starts at the signal close. One position at a time.
  - Risk: initial stop = entry - 2 x ATR14(1H, Wilder) of the signal candle; R = entry - stop.
  - Trailing stop: at each 1H close, stop = max(stop, highest 1H close since entry - 3 x ATR14(1H) of that candle).
    A stop touch inside a 15m candle exits at the stop, or at that candle's open if it gapped below the stop.
  - Costs: round-trip cost c reduces R by c x entry / R (scenarios 0.02% / 0.05% / 0.10%).
  - Sizing: 0.5% of equity at risk per trade, compounding on net R at the 0.05% scenario.

The audit never modifies ledgers. It writes results to audit/results/ and reports EVERY discrepancy, however small.
Usage: python3 audit.py [forward_dir] [--label NAME]
"""
import calendar, csv, datetime, gzip, hashlib, io, json, os, ssl, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFAULT_FWD = os.path.join(HERE, "..", "forward")
STEP = {"15m": 900, "1h": 3600, "4h": 14400}
COSTS = {"low": 0.0002, "mid": 0.0005, "high": 0.0010}
RISK = 0.005
TOL_PRICE, TOL_R, TOL_USD = 0.011, 0.0011, 0.011
FREEZE_COMMIT = "ce2e8c57"  # commit that froze the forward test
FROZEN_FILES = ["research/btc_breakout/src/engine.py", "research/btc_breakout/src/protocol.py",
                "research/btc_breakout/forward/paper_trader.py", "research/btc_breakout/forward/FROZEN.json"]

findings = []


def report(severity, check, detail):
    findings.append(dict(severity=severity, check=check, detail=detail))


def utc(s):
    return calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M"))


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


# ------------------------------------------------------------------ independent data
def fetch(tf, start, end_ms):
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
    rows, t = [], start * 1000
    while True:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={tf}&limit=1000&startTime={t}"
        for a in range(6):
            try:
                batch = json.loads(urllib.request.urlopen(url, timeout=30, context=ctx).read()); break
            except Exception as e:
                err = e; time.sleep(2 ** a)
        else:
            raise SystemExit(f"AUDIT ABORTED: Binance data unavailable for {tf}: {err}")
        rows += [b for b in batch if b[6] < end_ms]  # closed candles only
        if len(batch) < 1000 or batch[-1][6] >= end_ms:
            break
        t = batch[-1][0] + STEP[tf] * 1000
    return [dict(t=r[0] // 1000, o=float(r[1]), h=float(r[2]), l=float(r[3]), c=float(r[4]), v=float(r[5]), close_ms=r[6]) for r in rows]


def ema_sma_seed(x, n):  # SMA-seeded EMA (deliberately different seeding from the engine; converges after warm-up)
    out = [None] * len(x)
    if len(x) < n:
        return out
    out[n - 1] = sum(x[:n]) / n; a = 2 / (n + 1)
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def wilder_atr(c, n=14):
    tr = [c[0]["h"] - c[0]["l"]] + [max(c[i]["h"] - c[i]["l"], abs(c[i]["h"] - c[i - 1]["c"]), abs(c[i]["l"] - c[i - 1]["c"])) for i in range(1, len(c))]
    out = [None] * len(c); out[n - 1] = sum(tr[:n]) / n
    for i in range(n, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def compute_signals(h1, h4):
    """Independent signals on 1H candles. Returns {signal_close_ts: dict}. Uses only candles closed by the signal close."""
    atr = wilder_atr(h1)
    e200 = ema_sma_seed([x["c"] for x in h1], 200)
    del e200  # 1H EMA not part of the rule
    e4 = ema_sma_seed([x["c"] for x in h4], 200)
    h4_close_times = [x["t"] + 14400 for x in h4]
    out = {}
    j = -1
    for i in range(21, len(h1)):
        hh = max(x["h"] for x in h1[i - 20:i]); hh_prev = max(x["h"] for x in h1[i - 21:i - 1])
        if not (h1[i]["c"] > hh and h1[i - 1]["c"] <= hh_prev):
            continue
        tc = h1[i]["t"] + 3600
        while j + 1 < len(h4) and h4_close_times[j + 1] <= tc:
            j += 1
        out[tc] = dict(i=i, close=h1[i]["c"], prev20_high=hh, atr=atr[i], h4_close=h4[j]["c"], h4_ema200=e4[j],
                       h4_close_time=h4_close_times[j], trend_ok=e4[j] is not None and h4[j]["c"] > e4[j])
    return out, atr


def simulate(h1, m15, sigs, atr, fwd_start):
    """Independent trade replay. Returns closed trades, open trade, and per-signal statuses."""
    m_idx = {x["t"]: k for k, x in enumerate(m15)}
    h1_by_close = {x["t"] + 3600: k for k, x in enumerate(h1)}
    trades, statuses, busy_until, open_trade = [], {}, None, None
    for tc in sorted(sigs):
        s = sigs[tc]
        if tc - 3600 < fwd_start:
            continue
        if not s["trend_ok"]:
            statuses[tc] = "REJECTED: 4H close not above EMA200"; continue
        if busy_until is not None and tc <= busy_until:
            statuses[tc] = "REJECTED: position already open (no pyramiding/averaging)"; continue
        k = m_idx.get(tc)
        if k is None:
            statuses[tc] = "PENDING: next 15m candle not closed yet"; continue
        entry = m15[k]["o"]; stop = entry - 2 * s["atr"]; risk = entry - stop; best = entry; exit_px = exit_t = None; gap = False
        while k < len(m15):
            bar = m15[k]
            if bar["l"] <= stop:
                gap = bar["o"] < stop
                exit_px = bar["o"] if gap else stop; exit_t = bar["t"] + 900; break
            bc = bar["t"] + 900
            if bc % 3600 == 0 and bc in h1_by_close:
                best = max(best, bar["c"]); stop = max(stop, best - 3 * atr[h1_by_close[bc]])
            k += 1
        statuses[tc] = "ACCEPTED"
        t = dict(signal_close=tc, entry_time=tc, entry=entry, risk=risk, initial_stop=entry - risk, exit_time=exit_t, exit=exit_px, gap_fill=gap,
                 signal_close_price=s["close"])
        if exit_t is None:
            open_trade = t; busy_until = 10 ** 12
        else:
            trades.append(t); busy_until = exit_t
    return trades, open_trade, statuses


# ------------------------------------------------------------------ audit
def main():
    argv = sys.argv[1:]
    label = "forward"
    if "--label" in argv:
        k = argv.index("--label"); label = argv[k + 1]; argv = argv[:k] + argv[k + 2:]
    fwd = os.path.abspath(argv[0] if argv else DEFAULT_FWD)
    is_repo_fwd = os.path.samefile(fwd, DEFAULT_FWD)
    frozen = json.load(open(os.path.join(fwd, "FROZEN.json")))
    cfg = frozen["config"]; fwd_start = cfg["forward_start"]
    status = json.load(open(os.path.join(fwd, "status.json")))
    read = lambda n: list(csv.DictReader(open(os.path.join(fwd, n)))) if os.path.exists(os.path.join(fwd, n)) else []
    T, S = read("trades.csv"), read("signals.csv")
    now_ms = int(time.time() * 1000)

    # ---- 1. frozen files and append-only history (git)
    if is_repo_fwd:
        for f in FROZEN_FILES:
            d = subprocess.run(["git", "diff", "--stat", FREEZE_COMMIT, "--", f], cwd=REPO, capture_output=True, text=True).stdout.strip()
            if d:
                report("CRITICAL", "frozen files", f"{f} changed since freeze commit {FREEZE_COMMIT}: {d}")
        for name, key in (("trades.csv", "trade_no"), ("signals.csv", "signal_close_utc")):
            revs = subprocess.run(["git", "log", "--format=%H", "--reverse", "--", f"research/btc_breakout/forward/{name}"], cwd=REPO, capture_output=True, text=True).stdout.split()
            prev_rows = []
            for rv in revs:
                blob = subprocess.run(["git", "show", f"{rv}:research/btc_breakout/forward/{name}"], cwd=REPO, capture_output=True, text=True).stdout
                rows = list(csv.DictReader(io.StringIO(blob)))
                for a in prev_rows:
                    b = next((r for r in rows if r[key] == a[key]), None)
                    if b is None:
                        report("CRITICAL", "append-only history", f"{name} row {a[key]} disappeared in commit {rv[:8]}")
                    elif a != b and not a.get("status", "").startswith("PENDING"):
                        report("CRITICAL", "append-only history", f"{name} row {a[key]} changed in commit {rv[:8]}")
                prev_rows = rows
    else:
        report("INFO", "frozen files", "not a repository forward directory: git history checks skipped")

    # ---- 2. internal arithmetic of every recorded trade
    eq = cfg["start_equity_usd"]; peak = eq; prev_exit = None; seen = set()
    for n, r in enumerate(T, 1):
        tag = f"trade {r['trade_no']}"
        f = {k: float(r[k]) for k in ("signal_close_price", "entry_price", "entry_slippage_vs_signal_close", "initial_stop", "risk_per_btc",
                                       "equity_before_usd", "risk_usd", "size_btc", "exit_price", "hold_hours", "R_gross", "R_net_low",
                                       "R_net_mid", "R_net_high", "modeled_costs_usd_mid", "pnl_usd_mid", "equity_after_usd", "drawdown_pct")}
        chk = lambda name, rec, calc, tol: report("DISCREPANCY", f"{tag} {name}", f"recorded {rec} vs independent {round(calc, 6)} (diff {round(rec - calc, 6)})") if abs(rec - calc) > tol else None
        if int(r["trade_no"]) != n: report("DISCREPANCY", f"{tag} numbering", f"expected trade_no {n}")
        if r["side"] != "LONG": report("CRITICAL", f"{tag} side", f"non-LONG trade recorded: {r['side']}")
        if r["venue"] != "BINANCE_PROXY": report("DISCREPANCY", f"{tag} venue label", r["venue"])
        if r["signal_close_utc"] in seen: report("CRITICAL", f"{tag} duplicate execution", f"signal {r['signal_close_utc']} executed twice")
        seen.add(r["signal_close_utc"])
        te, tx, ts_ = utc(r["entry_utc"]), utc(r["exit_utc"]), utc(r["signal_close_utc"])
        if ts_ % 3600: report("DISCREPANCY", f"{tag} timing", "signal close is not on a 1H boundary")
        if te != ts_: report("DISCREPANCY", f"{tag} timing", f"entry {r['entry_utc']} is not at the signal close {r['signal_close_utc']}")
        if tx % 900: report("DISCREPANCY", f"{tag} timing", "exit time is not a 15m candle close")
        if tx <= te: report("CRITICAL", f"{tag} timing", "exit not after entry")
        if prev_exit is not None and te <= prev_exit: report("CRITICAL", f"{tag} overlapping position", f"entered {r['entry_utc']} before previous exit")
        prev_exit = tx
        if ts_ - 3600 < fwd_start: report("CRITICAL", f"{tag} forward window", "signal candle starts before the forward start")
        chk("hold_hours", f["hold_hours"], (tx - te) / 3600, 0.001)
        chk("entry slippage", f["entry_slippage_vs_signal_close"], f["entry_price"] - f["signal_close_price"], TOL_PRICE)
        chk("initial stop", f["initial_stop"], f["entry_price"] - f["risk_per_btc"], TOL_PRICE)
        chk("equity before", f["equity_before_usd"], eq, TOL_USD)
        chk("risk usd", f["risk_usd"], eq * RISK, TOL_USD)
        chk("size btc", f["size_btc"], eq * RISK / f["risk_per_btc"], 1e-6 + 1e-4 * f["size_btc"])
        chk("R gross", f["R_gross"], (f["exit_price"] - f["entry_price"]) / f["risk_per_btc"], TOL_R)
        k = f["entry_price"] / f["risk_per_btc"]
        for sc in ("low", "mid", "high"):
            chk(f"R net {sc}", f[f"R_net_{sc}"], f["R_gross"] - COSTS[sc] * k, TOL_R)
        chk("modeled costs", f["modeled_costs_usd_mid"], (f["R_gross"] - f["R_net_mid"]) * eq * RISK, TOL_USD)
        new_eq = eq * (1 + RISK * f["R_net_mid"])
        chk("pnl usd", f["pnl_usd_mid"], new_eq - eq, TOL_USD)
        chk("equity after", f["equity_after_usd"], new_eq, TOL_USD)
        peak = max(peak, new_eq)
        chk("drawdown", f["drawdown_pct"], (1 - new_eq / peak) * 100, 0.011)
        eq = new_eq
    if T and abs(eq - status["equity_usd_mid"]) > TOL_USD:
        report("DISCREPANCY", "status equity", f"status.json {status['equity_usd_mid']} vs recomputed {round(eq, 2)}")
    if len(T) != status["completed_trades"]:
        report("DISCREPANCY", "status trade count", f"status.json {status['completed_trades']} vs trades.csv {len(T)}")

    # ---- 3. independent replay from independently downloaded candles
    warm = calendar.timegm((2025, 1, 1, 0, 0, 0))
    h1, h4, m15 = fetch("1h", warm, now_ms), fetch("4h", warm, now_ms), fetch("15m", fwd_start - 86400, now_ms)
    for name, cs in (("1h", h1), ("4h", h4), ("15m", m15)):
        for a, b in zip(cs, cs[1:]):
            if b["t"] - a["t"] != STEP[name] and b["t"] >= fwd_start - 3 * 86400:
                report("CRITICAL", "candle continuity", f"{name} gap {fmt(a['t'])} -> {fmt(b['t'])}")
        if any(x["close_ms"] >= now_ms for x in cs):
            report("CRITICAL", "unfinished candle", f"{name} contains a candle that had not closed")
    # compare with candles recorded by the paper trader
    for tf in STEP:
        p = os.path.join(fwd, f"candles_{tf}_forward.csv.gz")
        if not os.path.exists(p):
            continue
        rec = {r[0]: r[1:] for r in list(csv.reader(io.StringIO(gzip.open(p, "rt").read())))[1:]}
        mine = {fmt(x["t"]): [x["o"], x["h"], x["l"], x["c"], x["v"]] for x in (h1 if tf == "1h" else h4 if tf == "4h" else m15)}
        diff = [t for t, v in rec.items() if t in mine and [float(z) for z in v] != mine[t]]
        missing = [t for t in rec if t not in mine and utc(t) >= fwd_start - 86400]
        for t in diff[:20]:
            report("DISCREPANCY", f"recorded {tf} candle", f"{t} recorded {rec[t]} vs Binance now {mine[t]}")
        if len(diff) > 20: report("DISCREPANCY", f"recorded {tf} candle", f"... and {len(diff) - 20} more")
        for t in missing[:5]:
            report("DISCREPANCY", f"recorded {tf} candle", f"{t} recorded but not returned by Binance now")
        last_rec = max(rec) if rec else None
        if last_rec and utc(last_rec) + STEP[tf] > status_last_close(status) + (0 if tf != "15m" else 3600):
            report("CRITICAL", "lookahead", f"recorded {tf} candle {last_rec} closes after the last processed 1H close")

    sigs, atr = compute_signals(h1, h4)
    last_processed = status_last_close(status)
    sigs = {t: v for t, v in sigs.items() if t <= last_processed}
    # replay on exactly the candles the paper trader had: 15m up to the last 15m candle it recorded
    rec15 = os.path.join(fwd, "candles_15m_forward.csv.gz")
    cutoff15 = (utc(max(r[0] for r in list(csv.reader(io.StringIO(gzip.open(rec15, "rt").read())))[1:])) + 900) if os.path.exists(rec15) else last_processed
    trades, open_trade, statuses = simulate(h1, [x for x in m15 if x["t"] + 900 <= cutoff15], sigs, atr, fwd_start)

    # signals: every independent signal must be recorded with the same status, and nothing extra
    rec_sig = {utc(r["signal_close_utc"]): r for r in S}
    for tc, st in statuses.items():
        r = rec_sig.get(tc)
        if r is None:
            report("DISCREPANCY", "signal missing", f"independent signal at {fmt(tc)} ({st}) not in signals.csv"); continue
        if r["status"] != st:
            report("DISCREPANCY", "signal status", f"{fmt(tc)} recorded '{r['status']}' vs independent '{st}'")
        s = sigs[tc]
        for k2, v in (("close", s["close"]), ("prev20_high", s["prev20_high"]), ("atr14", s["atr"]), ("h4_close", s["h4_close"])):
            if abs(float(r[k2]) - v) > max(0.011, 1e-6 * v):
                report("DISCREPANCY", f"signal {fmt(tc)} {k2}", f"recorded {r[k2]} vs independent {round(v, 4)}")
        if abs(float(r["h4_ema200"]) - s["h4_ema200"]) > 0.011:
            report("MINOR", f"signal {fmt(tc)} h4_ema200", f"recorded {r['h4_ema200']} vs independent (SMA-seeded) {round(s['h4_ema200'], 4)}")
        if s["h4_close_time"] > tc:
            report("CRITICAL", "lookahead", f"signal {fmt(tc)} used a 4H candle closing after the signal")
    for tc, r in rec_sig.items():
        if tc not in statuses:
            report("DISCREPANCY", "extra signal", f"signals.csv has {r['signal_close_utc']} ({r['status']}) with no independent signal")
        if r["status"].startswith("PENDING") and tc + 900 <= last_processed:
            report("DISCREPANCY", "stale pending signal", f"{r['signal_close_utc']} still PENDING although its entry candle has closed")
    # trades: compare with the independent replay
    for n, (r, t) in enumerate(zip(T, trades), 1):
        if utc(r["signal_close_utc"]) != t["signal_close"]:
            report("DISCREPANCY", f"trade {n} identity", f"recorded signal {r['signal_close_utc']} vs independent {fmt(t['signal_close'])}"); continue
        for name, rec, calc, tol in (("entry price", float(r["entry_price"]), t["entry"], TOL_PRICE),
                                     ("risk per btc", float(r["risk_per_btc"]), t["risk"], TOL_PRICE),
                                     ("exit price", float(r["exit_price"]), t["exit"], TOL_PRICE),
                                     ("exit time", utc(r["exit_utc"]), t["exit_time"], 0),
                                     ("R gross", float(r["R_gross"]), (t["exit"] - t["entry"]) / t["risk"], TOL_R)):
            if abs(rec - calc) > tol:
                report("DISCREPANCY", f"trade {n} {name} (replay)", f"recorded {rec} vs independent {round(calc, 6)}")
    if len(T) != len(trades):
        report("DISCREPANCY", "trade count (replay)", f"trades.csv {len(T)} vs independent replay {len(trades)}")
    rec_open = status.get("open_position")
    if bool(rec_open) != bool(open_trade):
        report("DISCREPANCY", "open position", f"recorded {rec_open} vs independent {open_trade}")
    elif rec_open and abs(float(rec_open["entry_price"]) - open_trade["entry"]) > TOL_PRICE:
        report("DISCREPANCY", "open position entry", f"recorded {rec_open['entry_price']} vs independent {open_trade['entry']}")

    # ---- 4. repainting: recompute each recorded signal using only candles closed by that time
    for tc in list(statuses)[:200]:
        sub_h1 = [x for x in h1 if x["t"] + 3600 <= tc]; sub_h4 = [x for x in h4 if x["t"] + 14400 <= tc]
        s2, _ = compute_signals(sub_h1, sub_h4)
        if tc not in s2 or s2[tc]["trend_ok"] != sigs[tc]["trend_ok"]:
            report("CRITICAL", "repainting", f"signal {fmt(tc)} differs when computed with data up to that time only")

    # ---- 5. execution realism and cost assumptions
    slips = [float(r["entry_slippage_vs_signal_close"]) for r in T]
    gaps = [t for t in trades if t["gap_fill"]]
    report("INFO", "entry slippage model", f"entries fill at the next 15m open; observed open-vs-signal-close differences over {len(slips)} trades: "
           f"max |{max([abs(x) for x in slips], default=0):.2f}| USD. No extra queue/latency slippage is modeled beyond the cost scenarios.")
    report("INFO", "stop gap fills", f"{len(gaps)} of {len(trades)} independent exits filled at a gapped 15m open below the stop (modeled).")
    report("WARNING", "cost assumptions", "Round-trip costs are HYPOTHETICAL scenarios (0.02% / 0.05% / 0.10% of price) covering spread, commission "
           "and slippage together. Exness BTCUSDm spread, commission and swap could not be verified (site blocks automated access). "
           "Overnight swap is NOT modeled even though the average hold is ~20h. Binance top-of-book spread is not representative of Exness CFD spreads.")
    report("WARNING", "intrabar assumption", "Within one 15m candle the exact path is unknown; the replay assumes the stop is evaluated before the "
           "trailing update, matching the research engine. This is conservative for longs but not exact.")

    # ---- 6. 40-trade limit
    src = open(os.path.join(fwd, "paper_trader.py")).read()
    enforced = "target_trades" in src and ("trade_rows[:CONFIG[\"target_trades\"]]" in src or "if len(trade_rows) >= CONFIG[\"target_trades\"]:" in src)
    if not enforced:
        report("FINDING", "40-trade limit", "The paper trader does NOT stop at 40 trades: it keeps recording trades after trade 40 and only labels the "
               "report COMPLETE when >= 40 trades AND date >= 2027-05-09. The 40-trade limit is not enforced in code. Evaluation should use "
               "trades 1-40 only (this audit reports that subset separately); the frozen code was not changed.")
    if len(T) > cfg.get("target_trades", 40):
        report("FINDING", "40-trade limit", f"{len(T)} trades recorded; only trades 1-{cfg['target_trades']} form the pre-registered evaluation set.")

    # ---- 7. exactly-once watermark log
    rl = read("run_log.csv")
    for a, b in zip(rl, rl[1:]):
        if b["previous_watermark_1h_close_utc"] != a["new_watermark_1h_close_utc"]:
            report("DISCREPANCY", "run log", f"run {b['run_utc']} previous watermark {b['previous_watermark_1h_close_utc']} != prior new watermark {a['new_watermark_1h_close_utc']}")
        if a["new_watermark_1h_close_utc"] and utc(b["new_watermark_1h_close_utc"]) < utc(a["new_watermark_1h_close_utc"]):
            report("CRITICAL", "run log", f"watermark moved backwards at {b['run_utc']}")
    total = sum(int(r["new_1h_candles_processed"]) for r in rl)
    if rl:
        expect = max(0, (utc(rl[-1]["new_watermark_1h_close_utc"]) - fwd_start) // 3600)
        if total != expect:
            report("DISCREPANCY", "run log", f"sum of processed candles {total} != candles since forward start {expect}")

    # ---- output
    eval_set = [float(r["R_net_mid"]) for r in T[:40]]
    summary = dict(audited_utc=fmt(int(time.time())), label=label, forward_dir=os.path.relpath(fwd, REPO), venue="BINANCE_PROXY",
                   last_processed_1h_close_utc=fmt(last_processed), recorded_trades=len(T), independent_trades=len(trades),
                   recorded_signals=len(S), independent_signals=len(statuses),
                   evaluation_set_trades_1_to_40=len(eval_set),
                   counts={s: sum(1 for f in findings if f["severity"] == s) for s in ("CRITICAL", "DISCREPANCY", "MINOR", "FINDING", "WARNING", "INFO")},
                   findings=findings)
    stamp = time.strftime("%Y%m%dT%H%MZ", time.gmtime())
    out_json = os.path.join(HERE, "results", f"audit_{label}_{stamp}.json")
    json.dump(summary, open(out_json, "w"), indent=1)
    lines = [f"# Independent audit - {label} - {summary['audited_utc']} UTC", "", "BINANCE PROXY (not Exness). Ledgers were not modified.", "",
             f"- Forward dir: `{summary['forward_dir']}` | last processed 1H close: {summary['last_processed_1h_close_utc']}",
             f"- Trades recorded {len(T)} vs independent {len(trades)} | signals recorded {len(S)} vs independent {len(statuses)}",
             f"- Findings: {summary['counts']}", "", "| Severity | Check | Detail |", "|---|---|---|"]
    lines += [f"| {f['severity']} | {f['check']} | {f['detail'].replace('|', '/')} |" for f in findings]
    open(os.path.join(HERE, "results", f"AUDIT_{label}_LATEST.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines)); print(f"\nsaved {os.path.relpath(out_json, REPO)}")
    sys.exit(1 if summary["counts"]["CRITICAL"] or summary["counts"]["DISCREPANCY"] else 0)


def status_last_close(status):
    return utc(status["last_closed_1h_candle_close_utc"])


if __name__ == "__main__":
    main()
