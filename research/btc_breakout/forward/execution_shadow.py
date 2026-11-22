"""Execution-realism shadow log for the Donchian 20 forward paper test (BINANCE PROXY, paper only).

Why this exists: the frozen paper trader (paper_trader.py, unchanged) models an idealized fill at the open of the 15m
candle that starts at the signal close (time T). The hourly worker only runs at about T+6 minutes and then needs
time to download and compute, so that open price is not executable. This script records what a worker running
on this schedule could actually have done.

For every ACCEPTED signal not yet in execution_log.csv, it records:
  - candle_close_utc: the signal candle close, T
  - signal_calc_utc: when this run computed the signal (now)
  - execution_utc: when the first executable quote was taken (Binance bookTicker, immediately after calculation)
  - bid, ask, spread; execution price = ASK (a market buy)
  - 1s trade price at the same second (cross-check)
  - slippage vs the frozen modeled entry (15m open at T) and vs the signal close
  - latency_min = execution - T
  - status:
      LIVE: latency <= 20 min and the trade was still open in the frozen ledger
      LATE: latency > 20 min (worker outage/catch-up), still open
      NOT_EXECUTABLE: the frozen ledger had already exited before the signal was processed
execution_log.csv is append-only (existing rows are never changed). EXECUTION_REPORT.md is regenerated each run:
for closed trades it computes the execution-adjusted R = (frozen exit - ask fill) / rule risk (2 x ATR) under the same
hypothetical cost scenarios. Approximation: the stop stays anchored to the frozen modeled entry (the frozen rules),
so it sits (fill - modeled entry) away from where a stop placed relative to the actual fill would be.
No strategy rule or parameter is changed. The frozen ledgers are only read.
"""
import calendar, csv, json, os, ssl, statistics, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "execution_log.csv")
LIVE_MAX_MIN = 20
COSTS = {"optimistic_0.02%": 0.0002, "moderate_0.05%": 0.0005, "pessimistic_0.10%": 0.0010}
FIELDS = ["signal_close_utc", "candle_close_unix", "signal_calc_utc", "execution_utc", "execution_unix", "latency_min",
          "bid", "ask", "spread", "execution_price_ask", "trade_price_1s", "modeled_entry_15m_open", "signal_close_price",
          "slippage_vs_modeled_entry", "slippage_vs_signal_close", "rule_risk_per_btc", "status", "note"]


def get(url):
    ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
    for a in range(4):
        try:
            return json.loads(urllib.request.urlopen(url, timeout=15, context=ctx).read())
        except Exception as e:
            err = e; time.sleep(1 + a)
    raise RuntimeError(f"quote unavailable: {err}")


def utc(s): return calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M"))
def fmt(t, sec=False): return time.strftime("%Y-%m-%d %H:%M:%S" if sec else "%Y-%m-%d %H:%M", time.gmtime(t))


def read(name):
    p = os.path.join(HERE, name)
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []


def main():
    sigs = [s for s in read("signals.csv") if s["status"] == "ACCEPTED"]
    trades = read("trades.csv"); status = json.load(open(os.path.join(HERE, "status.json")))
    op = status.get("open_position")
    done = {r["signal_close_utc"] for r in read("execution_log.csv")}
    new_rows = []
    for s in sigs:
        if s["signal_close_utc"] in done:
            continue
        T = utc(s["signal_close_utc"]); calc = time.time()
        tr = next((t for t in trades if t["signal_close_utc"] == s["signal_close_utc"]), None)
        modeled = float(tr["entry_price"]) if tr else (float(op["entry_price"]) if op and op["entry_utc"] == s["signal_close_utc"] else None)
        risk = float(tr["risk_per_btc"]) if tr else (float(op["risk_per_btc"]) if op and op["entry_utc"] == s["signal_close_utc"] else None)
        already_exited = tr is not None and utc(tr["exit_utc"]) <= calc
        q = get("https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=BTCUSDT"); t_exec = time.time()
        k = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1s&startTime={int(t_exec) * 1000}&limit=1")
        bid, ask = float(q["bidPrice"]), float(q["askPrice"]); lat = (t_exec - T) / 60
        st = "NOT_EXECUTABLE" if already_exited else ("LIVE" if lat <= LIVE_MAX_MIN else "LATE")
        new_rows.append(dict(signal_close_utc=s["signal_close_utc"], candle_close_unix=T, signal_calc_utc=fmt(calc, True),
                             execution_utc=fmt(t_exec, True), execution_unix=round(t_exec, 3), latency_min=round(lat, 2), bid=bid, ask=ask,
                             spread=round(ask - bid, 2), execution_price_ask=ask, trade_price_1s=float(k[0][4]) if k else "",
                             modeled_entry_15m_open=modeled if modeled is not None else "", signal_close_price=float(s["close"]),
                             slippage_vs_modeled_entry=round(ask - modeled, 2) if modeled is not None else "",
                             slippage_vs_signal_close=round(ask - float(s["close"]), 2), rule_risk_per_btc=risk if risk is not None else "",
                             status=st, note="frozen ledger exited before processing" if already_exited else ""))
    if new_rows:
        new = not os.path.exists(LOG)
        with open(LOG, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new: w.writeheader()
            w.writerows(new_rows)
    # ---- report (derived; regenerated)
    rows = read("execution_log.csv"); by_sig = {r["signal_close_utc"]: r for r in rows}
    closed = []
    for t in trades:
        r = by_sig.get(t["signal_close_utc"])
        if r and r["status"] in ("LIVE", "LATE") and r["rule_risk_per_btc"]:
            risk = float(t["risk_per_btc"]); fill = float(r["execution_price_ask"]); ex = float(t["exit_price"])
            closed.append(dict(trade_no=int(t["trade_no"]), status=r["status"], R_frozen_gross=float(t["R_gross"]), R_exec_gross=(ex - fill) / risk,
                               k=fill / risk, latency=float(r["latency_min"]), slip=float(r["slippage_vs_modeled_entry"])))
    lines = ["# Execution-realism report - BINANCE PROXY (paper only, not Exness)", "",
             f"Generated {fmt(time.time())} UTC. Fill = Binance ASK at the first quote after this worker computed the signal. "
             "Exit = frozen-ledger exit (resting stop). Costs below are HYPOTHETICAL and are added on top of the measured Binance spread "
             "already included in the ask fill. Overnight swap/admin fees: unknown, not modelled.", "",
             f"- Accepted signals logged: {len(rows)} (LIVE {sum(r['status'] == 'LIVE' for r in rows)}, LATE {sum(r['status'] == 'LATE' for r in rows)}, "
             f"NOT_EXECUTABLE {sum(r['status'] == 'NOT_EXECUTABLE' for r in rows)})",
             f"- Closed trades with an execution record: {len(closed)}"]
    ex_rows = [r for r in rows if r["status"] in ("LIVE", "LATE")]  # executable fills only
    if ex_rows:
        lat = [float(r["latency_min"]) for r in ex_rows]; sl = [float(r["slippage_vs_modeled_entry"]) for r in ex_rows if r["slippage_vs_modeled_entry"] != ""]
        lines.append(f"- Executable fills ({len(ex_rows)}): latency after candle close median {statistics.median(lat):.1f} min, max {max(lat):.1f} min; "
                     f"slippage vs modeled open: median {statistics.median(sl) if sl else 'n/a'} USD")
    if closed:
        lines += ["", "| Scenario | Trades | Expectancy R (frozen fill) | Expectancy R (executable fill) |", "|---|---|---|---|"]
        for n, c in [("gross", 0.0)] + list(COSTS.items()):
            a = statistics.mean(x["R_frozen_gross"] - c * x["k"] for x in closed); b = statistics.mean(x["R_exec_gross"] - c * x["k"] for x in closed)
            lines.append(f"| {n} | {len(closed)} | {a:.4f} | {b:.4f} |")
    open(os.path.join(HERE, "EXECUTION_REPORT.md"), "w").write("\n".join(lines) + "\n")
    print(f"execution shadow: {len(new_rows)} new signal(s) logged" + "".join(f"\n  {r['signal_close_utc']} {r['status']} ask {r['ask']} spread {r['spread']} latency {r['latency_min']} min" for r in new_rows))


if __name__ == "__main__":
    main()
