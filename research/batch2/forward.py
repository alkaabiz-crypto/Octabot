"""Batch 2 FORWARD (confirmatory) paper test. Implements PREREGISTRATION.md unchanged; code shared with dev.py via common.py.
Run hourly. Before E (2026-11-14 00:00 UTC) it does nothing. After E it rebuilds signals from fresh data (inputs from 2025-01-01
for warm-ups, decisions only at or after E), appends newly closed trades to ledger.csv (append-only) and STOPs on any revision
of an already recorded trade. No decision is taken before each test's pre-registered evaluation date (monitoring only).

Usage: python3 -I forward.py      (raw data stays in memory / scratch, never committed)
"""
import csv, json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common as C  # noqa: E402

LEDGER, REPORT, STATE = (os.path.join(HERE, f) for f in ("ledger.csv", "REPORT.md", "state.json"))
FIELDS = ["test", "decision_utc", "side", "entry_utc", "entry", "exit_utc", "exit", "net_bp_primary", "net_bp_stress", "info", "processed_utc"]
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def stop(msg):
    print("STOPPED:", msg); open(os.path.join(HERE, "RUN_ALERT.md"), "w").write(f"STOPPED {fmt(time.time() * 1000)} UTC: {msg}\n"); raise SystemExit(1)


def main():
    now = int(time.time() * 1000) // C.M * C.M
    if now < C.E_MS:
        print(f"Batch 2 forward: not started; forward period begins {fmt(C.E_MS)} UTC (T0 {fmt(C.T0_MS)} UTC). Nothing processed."); return
    dev = json.load(open(os.path.join(HERE, "results", "development.json")))["tests"]
    old = list(csv.DictReader(open(LEDGER))) if os.path.exists(LEDGER) else []
    known = {(r["test"], r["decision_utc"]): r for r in old}; new_rows = []; open_pos = {}; stats = {}
    for coin in C.COINS:
        h1 = C.binance_klines(f"{coin}USDT", "1h", C.START_MS, now); m1 = C.binance_klines(f"{coin}USDT", "1m", C.E_MS, now)
        fund = C.hl_funding(coin, C.START_MS, now); dvol = C.deribit_dvol(coin, C.START_MS, now)
        futs = [(n, e, C.deribit_chart(n, max(C.START_MS, cr), min(e, now))) for n, e, cr in C.deribit_quarterlies(coin) if cr < now]
        if len(m1) == 0: stop(f"{coin}: no 1m candles after E")
        if (np.diff(m1.t.values) > 90 * C.M).any(): stop(f"{coin}: 1m feed gap > 90 min in the forward period")
        sigs = {"H1": C.h1_signals(fund), "H2": C.h2_signals(futs, h1), "H3": C.h3_signals(h1), "H4": C.h4_signals(dvol, h1)}
        for hid, sig in sigs.items():
            tid = f"{hid}_{coin}"; tr = C.simulate(sig, C.HOLD[hid], m1, C.E_MS, now)
            for x in tr:
                key = (tid, fmt(x["decision_ms"]))
                row = dict(test=tid, decision_utc=key[1], side=x["side"], entry_utc=fmt(x["entry_ms"]), entry=round(x["entry"], 6), exit_utc=fmt(x["exit_ms"]), exit=round(x["exit"], 6),
                           net_bp_primary=round(float(C.net(x, coin, "primary") * 1e4), 3), net_bp_stress=round(float(C.net(x, coin, "stress") * 1e4), 3),
                           info=json.dumps({k: v for k, v in x.items() if k not in ("decision_ms", "side", "entry_ms", "entry", "exit_ms", "exit")}), processed_utc=fmt(now))
                if key in known:
                    k0 = known[key]
                    if (int(k0["side"]), round(float(k0["entry"]), 6), round(float(k0["exit"]), 6), k0["entry_utc"], k0["exit_utc"]) != (row["side"], row["entry"], row["exit"], row["entry_utc"], row["exit_utc"]):
                        stop(f"DATA REVISION in {key}: recorded {k0['entry']}->{k0['exit']}, now {row['entry']}->{row['exit']}")
                else: new_rows.append(row); known[key] = row
            pend = [s for s in sig if s[0] >= C.E_MS and s[0] + C.M + C.HOLD[hid] > now and not any(x["decision_ms"] == s[0] for x in tr)]
            last_exit = max([x["exit_ms"] for x in tr], default=0)
            op = [s for s in pend if s[0] >= last_exit]
            if op: open_pos[tid] = dict(decision_utc=fmt(op[0][0]), side=op[0][1], exit_due_utc=fmt(op[0][0] + C.M + C.HOLD[hid]))
    if new_rows:
        first = not os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if first: w.writeheader()
            w.writerows(new_rows)
    allrows = list(csv.DictReader(open(LEDGER))) if os.path.exists(LEDGER) else []
    lines = [f"# Batch 2 forward PAPER test ({fmt(now)} UTC)", "",
             f"Pre-registered at T0 {fmt(C.T0_MS)} UTC (commit 33777e0a); forward period from {fmt(C.E_MS)} UTC. Binance spot proxy for Exness BTC/ETH CFDs, "
             "Exness spread costs. **Monitoring only: no decision before each test's evaluation date (PREREGISTRATION.md).**", "",
             "| Test | Closed trades | Mean bp primary | Mean bp stress | n_req (power) | Open position |", "|---|---|---|---|---|---|"]
    for tid in C.TESTS:
        r = [x for x in allrows if x["test"] == tid]; p = [float(x["net_bp_primary"]) for x in r]; s = [float(x["net_bp_stress"]) for x in r]
        nr = dev.get(tid, {}).get("power", {}).get("n_req"); op = open_pos.get(tid)
        lines.append(f"| {tid} | {len(r)} | {np.mean(p):+.2f} | {np.mean(s):+.2f} | {nr} | {(('LONG' if op['side'] > 0 else 'SHORT') + ' since ' + op['decision_utc'] + ', exit ' + op['exit_due_utc']) if op else 'none'} |"
                     if r else f"| {tid} | 0 | — | — | {nr} | {(('LONG' if op['side'] > 0 else 'SHORT') + ' since ' + op['decision_utc'] + ', exit ' + op['exit_due_utc']) if op else 'none'} |")
    open(REPORT, "w").write("\n".join(lines) + "\n"); json.dump(dict(last_run_utc=fmt(now), ledger_rows=len(allrows)), open(STATE, "w"), indent=1)
    print(f"Batch 2 forward: {len(new_rows)} new closed trade(s)"); print("\n".join(lines[4:]))


if __name__ == "__main__":
    main()
