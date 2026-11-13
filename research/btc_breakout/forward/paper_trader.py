"""Forward paper trader - Donchian 20 breakout, 1H entries, 4H trend, LONG ONLY, ATR trailing stop. PAPER ONLY.

Venue: BINANCE_PROXY (Binance BTCUSDT closed candles via data-api.binance.vision). These are NOT Exness results.
Strategy logic is the validated research engine (../src/engine.py) with the locked defaults; this file never changes
parameters. Each run:
  1. downloads CLOSED candles only (Binance closeTime < now), warm-up from WARMUP_START;
  2. refuses to run if the strategy files or the frozen config differ from FROZEN.json (parameter lock);
  3. replays the strategy from FORWARD_START to the last closed candle (deterministic, causal);
  4. checks that every previously recorded signal/trade is unchanged (append-only + repaint/data-revision guard);
  5. writes signals.csv (incl. rejected), trades.csv, open_position.json, daily.csv, weekly.csv, REPORT.md.
Costs: hypothetical round-trip spread+fees+slippage scenarios (Exness costs unverified): 0.02% / 0.05% (primary) / 0.10%.
"""
import calendar, csv, datetime, gzip, hashlib, io, json, math, os, ssl, statistics, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
from engine import Lab  # validated research engine, locked defaults

def ts(y, m, d, h=0): return calendar.timegm((y, m, d, h, 0, 0))
CONFIG = dict(venue="BINANCE_PROXY", symbol="BTCUSDT", entry_tf="1h", trend_tf="4h", model="M2_DONCHIAN20", direction="LONG",
              stop="TRAIL", initial_stop_atr=2.0, trail_atr=3.0, donchian_len=20, risk_per_trade=0.005,
              start_equity_usd=round(10000 / 3.6725, 2), forward_start_utc="2026-11-09 07:00", forward_start=ts(2026, 11, 9, 7),
              warmup_start=ts(2025, 1, 1), cost_round_trip={"low": 0.0002, "mid": 0.0005, "high": 0.0010}, primary_cost="mid",
              target_trades=40, target_end_utc="2027-05-09")
STRATEGY_FILES = [os.path.join(ROOT, "src", "engine.py"), os.path.join(ROOT, "src", "protocol.py")]
STEP = {"15m": 900, "1h": 3600, "4h": 14400, "1d": 86400}

def fingerprint():
    h = hashlib.sha256(json.dumps(CONFIG, sort_keys=True).encode())
    for f in STRATEGY_FILES: h.update(open(f, "rb").read())
    return h.hexdigest()

def fetch(tf, start_ms, now_ms):
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
    out, t = [], start_ms
    while True:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval={tf}&limit=1000&startTime={t}"
        for a in range(6):
            try: rows = json.loads(urllib.request.urlopen(url, timeout=30, context=ctx).read()); break
            except Exception as e: err = e; time.sleep(2 ** a)
        else: raise SystemExit(f"DATA UNAVAILABLE ({tf}): {err} - no update performed")
        closed = [r for r in rows if r[6] < now_ms]          # never use an unfinished candle
        out += closed
        if len(rows) < 1000 or len(closed) < len(rows): break
        t = rows[-1][0] + STEP[tf] * 1000
    return [[r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in out]

def fmt(t): return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))

def stats(rs):
    if not rs: return dict(trades=0)
    pos, neg = sum(r for r in rs if r > 0), -sum(r for r in rs if r < 0); m = statistics.mean(rs)
    sd = statistics.stdev(rs) if len(rs) > 1 else 0
    streak = worst = 0
    for r in rs: streak = streak + 1 if r <= 0 else 0; worst = max(worst, streak)
    return dict(trades=len(rs), expectancy_R=round(m, 4), t_stat=round(m / (sd / math.sqrt(len(rs))), 2) if sd else None,
                profit_factor=round(pos / neg, 3) if neg else None, win_rate_pct=round(sum(r > 0 for r in rs) / len(rs) * 100, 1),
                total_R=round(sum(rs), 3), max_losing_streak=worst, current_losing_streak=streak)

def main():
    now = time.time(); now_ms = int(now * 1000)
    frozen_path = os.path.join(HERE, "FROZEN.json")
    fp = fingerprint()
    if not os.path.exists(frozen_path):
        json.dump(dict(fingerprint=fp, config=CONFIG, frozen_at_utc=fmt(now)), open(frozen_path, "w"), indent=1)
    frozen = json.load(open(frozen_path))
    if frozen["fingerprint"] != fp: raise SystemExit("PARAMETER LOCK VIOLATION: strategy files or config changed since freeze - refusing to run")
    cache = os.path.join(HERE, "cache"); os.makedirs(cache, exist_ok=True)
    for tf in STEP:
        json.dump(fetch(tf, CONFIG["warmup_start"] * 1000, now_ms), open(os.path.join(cache, f"btc_{tf}.json"), "w"))
    L = Lab(cache); E = L.B["1h"]
    last_1h_close = E["t"][-1] + 3600
    trades_raw = L.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", CONFIG["forward_start"], 10 ** 11)
    closed = [t for t in trades_raw if t["exit"] != "data_end"]; open_tr = [t for t in trades_raw if t["exit"] == "data_end"]
    # ---- trades ledger (sequential equity at primary cost)
    c_mid = CONFIG["cost_round_trip"]["mid"]; eq = peak = CONFIG["start_equity_usd"]; mdd = 0.0; trade_rows = []
    for n, t in enumerate(closed, 1):
        risk_usd = eq * CONFIG["risk_per_trade"]; size = risk_usd / t["risk"]
        R_net = {k: round(t["R_gross"] - v * t["k"], 4) for k, v in CONFIG["cost_round_trip"].items()}
        exit_px = t["entry"] + t["R_gross"] * t["risk"]
        fees_usd = (t["R_gross"] - R_net["mid"]) * risk_usd
        sig_i = [i for i in range(len(E["t"])) if E["t"][i] + 3600 == t["entry_time"]][0]
        eq_before = eq; eq *= 1 + CONFIG["risk_per_trade"] * R_net["mid"]; peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
        trade_rows.append(dict(trade_no=n, venue=CONFIG["venue"], side="LONG", signal_close_utc=fmt(t["entry_time"]),
            signal_close_price=E["c"][sig_i], entry_utc=fmt(t["entry_time"]), entry_price=t["entry"],
            entry_slippage_vs_signal_close=round(t["entry"] - E["c"][sig_i], 2), initial_stop=round(t["entry"] - t["risk"], 2),
            risk_per_btc=round(t["risk"], 2), equity_before_usd=round(eq_before, 2), risk_usd=round(risk_usd, 2), size_btc=round(size, 6),
            exit_utc=fmt(t["exit_time"]), exit_price=round(exit_px, 2), exit_reason=t["exit"], hold_hours=t["hold_h"],
            R_gross=round(t["R_gross"], 4), R_net_low=R_net["low"], R_net_mid=R_net["mid"], R_net_high=R_net["high"],
            modeled_costs_usd_mid=round(fees_usd, 2), pnl_usd_mid=round(eq - eq_before, 2), equity_after_usd=round(eq, 2),
            drawdown_pct=round((1 - eq / peak) * 100, 2), regime_at_entry=t["regime"]))
    # ---- signals ledger (every confirmed breakout on a closed 1H candle, accepted or rejected)
    sig = L.signals("1h", "M2_DONCHIAN20", 1); sig_rows = []
    for i in range(len(E["t"])):
        if E["t"][i] < CONFIG["forward_start"] or not sig[i]: continue
        tc = E["t"][i] + 3600; H = L.B["4h"]
        k = max(j for j in range(len(H["t"])) if H["t"][j] + 14400 <= tc)
        trend_ok = H["c"][k] > H["e200"][k]
        active = any(t["entry_time"] < tc < t["exit_time"] for t in trades_raw)
        entered = any(t["entry_time"] == tc for t in trades_raw)
        status = ("ACCEPTED" if entered else "REJECTED: 4H close not above EMA200" if not trend_ok
                  else "REJECTED: position already open (no pyramiding/averaging)" if active else "PENDING: next 15m candle not closed yet")
        sig_rows.append(dict(signal_close_utc=fmt(tc), venue=CONFIG["venue"], close=E["c"][i], prev20_high=round(E["hh"][20][i], 2),
                             atr14=round(E["atr"][i], 2), h4_close=H["c"][k], h4_ema200=round(H["e200"][k], 2), status=status))
    # ---- integrity: previously recorded rows must be unchanged (pending -> decided is the only allowed change)
    def read(p): return list(csv.DictReader(open(p))) if os.path.exists(p) else []
    old_t, old_s = read(os.path.join(HERE, "trades.csv")), read(os.path.join(HERE, "signals.csv"))
    new_t = [{k: str(v) for k, v in r.items()} for r in trade_rows]; new_s = [{k: str(v) for k, v in r.items()} for r in sig_rows]
    bad = [r for r, n in zip(old_t, new_t) if r != n] + (["missing trades"] if len(new_t) < len(old_t) else [])
    for r in old_s:
        m = [n for n in new_s if n["signal_close_utc"] == r["signal_close_utc"]]
        if not m or (r != m[0] and not r["status"].startswith("PENDING")): bad.append(r)
    if bad:
        open(os.path.join(HERE, "INTEGRITY_ALERT.md"), "w").write(f"# INTEGRITY ALERT {fmt(now)}\nPreviously recorded rows changed:\n{json.dumps(bad[:5], indent=1)}\n")
        raise SystemExit("INTEGRITY ALERT: previously recorded data changed - ledgers NOT overwritten")
    for name, rows in (("trades.csv", trade_rows), ("signals.csv", sig_rows)):
        if rows:
            with open(os.path.join(HERE, name), "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    # ---- open position (mark to market on last closed 15m candle)
    P = L.B["15m"]; last_px = P["c"][-1]
    op = None
    if open_tr:
        t = open_tr[0]; op = dict(venue=CONFIG["venue"], entry_utc=fmt(t["entry_time"]), entry_price=t["entry"], initial_stop=round(t["entry"] - t["risk"], 2),
                                  risk_per_btc=round(t["risk"], 2), last_closed_15m_utc=fmt(P["t"][-1]), mark_price=last_px,
                                  unrealized_R_gross=round((last_px - t["entry"]) / t["risk"], 3))
    json.dump(op, open(os.path.join(HERE, "open_position.json"), "w"), indent=1)
    # ---- daily / weekly (by exit date, UTC)
    def bucket(key):
        agg = {}
        for r in trade_rows:
            d = key(r["exit_utc"]); a = agg.setdefault(d, dict(period=d, trades_closed=0, R_net_mid=0.0, pnl_usd_mid=0.0))
            a["trades_closed"] += 1; a["R_net_mid"] = round(a["R_net_mid"] + r["R_net_mid"], 4); a["pnl_usd_mid"] = round(a["pnl_usd_mid"] + r["pnl_usd_mid"], 2)
        return list(agg.values())
    def iso_week(s):
        y, wk, _ = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").isocalendar()
        return f"{y}-W{wk:02d}"
    for name, rows in (("daily.csv", bucket(lambda s: s[:10])), ("weekly.csv", bucket(iso_week))):
        with open(os.path.join(HERE, name), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["period", "trades_closed", "R_net_mid", "pnl_usd_mid"]); w.writeheader(); w.writerows(rows)
    # ---- forward candles actually used (for reproducibility)
    for tf in ("1h", "15m", "4h"):
        B = L.B[tf]; buf = io.StringIO(); w = csv.writer(buf); w.writerow(["open_time_utc", "open", "high", "low", "close", "volume"])
        for j in range(len(B["t"])):
            if B["t"][j] >= CONFIG["forward_start"] - 3 * 86400: w.writerow([fmt(B["t"][j]), B["o"][j], B["h"][j], B["l"][j], B["c"][j], B["v"][j]])
        with gzip.open(os.path.join(HERE, f"candles_{tf}_forward.csv.gz"), "wt") as g: g.write(buf.getvalue())
    # ---- report
    s = {k: stats([r[f"R_net_{k}"] for r in trade_rows]) for k in ("low", "mid", "high")}
    gross = stats([r["R_gross"] for r in trade_rows])
    days = max(0.0, (last_1h_close - CONFIG["forward_start"]) / 86400)
    acc = sum(r["status"] == "ACCEPTED" for r in sig_rows); rej = sum(r["status"].startswith("REJECTED") for r in sig_rows)
    status = dict(updated_utc=fmt(now), last_closed_1h_candle_close_utc=fmt(last_1h_close), forward_days=round(days, 1),
                  completed_trades=len(trade_rows), target_trades=CONFIG["target_trades"], signals_total=len(sig_rows), accepted=acc, rejected=rej,
                  equity_usd_mid=round(eq, 2), return_pct_mid=round((eq / CONFIG["start_equity_usd"] - 1) * 100, 2), max_drawdown_pct_mid=round(mdd * 100, 2),
                  stats_gross=gross, stats_net=s, open_position=op, fingerprint=fp)
    json.dump(status, open(os.path.join(HERE, "status.json"), "w"), indent=1)
    done = len(trade_rows) >= CONFIG["target_trades"] and now >= ts(2027, 5, 9)
    lines = [f"# Donchian 20 forward paper test - {'COMPLETE' if done else 'IN PROGRESS'}", "",
             "**Venue: BINANCE PROXY (Binance BTCUSDT). These are NOT Exness BTCUSDm results.** Paper only - no live orders.", "",
             f"- Forward start: {CONFIG['forward_start_utc']} UTC (after all previously examined data). Parameters frozen, fingerprint `{fp[:16]}...`",
             f"- Last closed 1H candle used: {status['last_closed_1h_candle_close_utc']} UTC | forward days: {status['forward_days']} | updated {status['updated_utc']} UTC",
             f"- Completed trades: **{len(trade_rows)} / {CONFIG['target_trades']}** | signals: {len(sig_rows)} (accepted {acc}, rejected {rej})",
             f"- Paper equity (mid cost): ${status['equity_usd_mid']} ({status['return_pct_mid']}%), max drawdown {status['max_drawdown_pct_mid']}%",
             f"- Open position: {json.dumps(op) if op else 'none'}", "",
             "| Costs (round trip, hypothetical) | Trades | Expectancy R | t | PF | Win % | Max losing streak |", "|---|---|---|---|---|---|---|",
             f"| gross (0%) | {gross.get('trades', 0)} | {gross.get('expectancy_R')} | {gross.get('t_stat')} | {gross.get('profit_factor')} | {gross.get('win_rate_pct')} | {gross.get('max_losing_streak')} |"]
    for k, lab in (("low", "0.02%"), ("mid", "0.05% (primary)"), ("high", "0.10%")):
        x = s[k]; lines.append(f"| {lab} | {x.get('trades', 0)} | {x.get('expectancy_R')} | {x.get('t_stat')} | {x.get('profit_factor')} | {x.get('win_rate_pct')} | {x.get('max_losing_streak')} |")
    lines += ["", "Research expectation (walk-forward, Binance proxy): about +0.22R/trade at 0.05% cost, ~34% win rate, losing streaks of 10+ are normal.",
              "Ledgers: signals.csv (all signals incl. rejected), trades.csv, daily.csv, weekly.csv, open_position.json, status.json."]
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
