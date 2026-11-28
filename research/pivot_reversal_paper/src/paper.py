"""Pivot Reversal BUY forward paper test on Exness BTCUSDm. Run any time:  python src/paper.py
1. checks that the engine files are byte-identical to the frozen versions;
2. rebuilds 15-minute bid/ask candles from the Exness tick archive (the current month is re-downloaded each run);
3. replays the strategy and writes every BUY leg entered since START_UTC to ledger/trades.csv;
4. refuses to continue if any previously recorded leg changed (the ledger is append-only);
5. writes ledger/STATUS.md: the pending buy-stop (the live signal), the open leg, running statistics and checkpoints.
"""
import csv
import hashlib
import json
import math
import os
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, HERE)
import config as C  # noqa: E402

CACHE = os.path.join(ROOT, "cache")
LEDGER = os.path.join(ROOT, "ledger", "trades.csv")
STATUS = os.path.join(ROOT, "ledger", "STATUS.md")
FIELDS = ["entry_utc", "exit_utc", "entry", "exit_r_gross", "r_primary", "r_stress", "hold_hours", "risk_2atr"]


class FrozenError(Exception):
    pass


class LedgerChangedError(Exception):
    pass


def check_frozen():
    for rel, want in C.FROZEN_SHA256.items():
        got = hashlib.sha256(open(os.path.join(RESEARCH, rel), "rb").read()).hexdigest()
        if got != want:
            raise FrozenError(f"{rel} changed since the paper test was frozen ({got[:12]} != {want[:12]})")


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


def rebuild_bars():
    os.makedirs(CACHE, exist_ok=True)
    work = os.path.join(CACHE, "parts")
    os.makedirs(work, exist_ok=True)
    now = time.gmtime()
    cur = f"{now.tm_year}-{now.tm_mon:02d}"
    prev_y, prev_m = (now.tm_year, now.tm_mon - 1) if now.tm_mon > 1 else (now.tm_year - 1, 12)
    for y, m in ((now.tm_year, now.tm_mon), (prev_y, prev_m)):          # still being filled: always refetch
        p = os.path.join(work, f"{C.SYMBOL}_{y}_{m:02d}.csv")
        if os.path.exists(p):
            os.remove(p)
    out = os.path.join(CACHE, f"{C.SYMBOL}_15m.csv.gz")
    subprocess.run([sys.executable, os.path.join(RESEARCH, "oil_rsi_vwap", "src", "build_bars.py"), C.SYMBOL,
                    C.WARMUP_FIRST_MONTH, cur, out, work, "2"], check=True, capture_output=True)
    return out


def legs(path):
    sys.path.insert(0, os.path.join(RESEARCH, "tradingview_builtins", "src"))
    sys.path.insert(0, os.path.join(RESEARCH, "long_history", "src"))
    import builtin_strategies as B
    import fast_bench as FB
    a = B.BuiltinAsset(path, crypto=True)
    trades = [t for t in a.simulate_strategy(C.STRATEGY) if t.direction == C.DIRECTION and t.entry_time >= C.START_UTC]
    pending = [o.price for o in B.strategy_orders(C.STRATEGY, a.e, a.atr)[-1] if o.d == C.DIRECTION]
    last_bar = a.e.t[-1] + 3600
    bench = FB.held(a, trades, C.START_UTC, last_bar + 1, runs=1000) if len(trades) >= 5 else None
    return a, trades, pending, last_bar, bench


def row(t):
    return {"entry_utc": fmt(t.entry_time), "exit_utc": fmt(t.exit_time), "entry": f"{t.entry:.2f}",
            "exit_r_gross": f"{t.r_gross:.4f}", "r_primary": f"{t.r('primary'):.4f}", "r_stress": f"{t.r('stress'):.4f}",
            "hold_hours": f"{t.hold_hours:.2f}", "risk_2atr": f"{t.risk:.2f}"}


def write_ledger(rows):
    old = []
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            old = list(csv.DictReader(f))
    for k, o in enumerate(old):
        if k >= len(rows) or rows[k] != o:
            raise LedgerChangedError(f"recorded leg {k + 1} ({o['entry_utc']}) changed; investigate before continuing")
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows[len(old):]


def main():
    check_frozen()
    path = rebuild_bars()
    a, trades, pending, last_bar, bench = legs(path)
    new = write_ledger([row(t) for t in trades])
    rs = [t.r("primary") for t in trades]
    L = ["# Pivot Reversal BUY paper test: status", "", f"Updated {fmt(time.time())} UTC. Data to {fmt(last_bar)} UTC. "
         f"Counting since {fmt(C.START_UTC)} UTC. Rules: `PROTOCOL.md` (frozen).", "", "## Latest signal", ""]
    if pending:
        L.append(f"**At the last available candle, a BUY stop was pending at {pending[0]:.2f}** (bid), for the hour after "
                 f"{fmt(last_bar)} UTC. The Exness archive lags by about a day, so this is a paper record, not a live alert.")
    else:
        L.append("No BUY order is pending.")
    L += ["", "## Record", ""]
    if rs:
        sd = statistics.pstdev(rs) if len(rs) > 1 else float("nan")
        L += [f"- Closed BUY legs: **{len(rs)}** (decision at {C.FINAL_AT}; futility check at {C.FUTILITY_AT})",
              f"- Win rate: {100 * sum(r > 0 for r in rs) / len(rs):.1f}%",
              f"- Expectancy: {statistics.mean(rs):+.3f}R (stress cost {statistics.mean(t.r('stress') for t in trades):+.3f}R)",
              f"- Total: {sum(rs):+.2f}R; t = {statistics.mean(rs) / (sd / math.sqrt(len(rs))) if len(rs) > 1 and sd > 0 else 0:+.2f}"]
        if bench:
            z = (statistics.mean(rs) - bench[0]) / bench[1] if bench[1] > 0 else 0
            L.append(f"- Random entries with the same holding times: {bench[0]:+.3f}R; z = {z:+.2f}, p = {0.5 * math.erfc(z / math.sqrt(2)):.3f}")
        reached = [c for c in C.CHECKPOINTS if len(rs) >= c]
        if reached:
            L.append(f"- Checkpoints reached: {', '.join(map(str, reached))}")
        if len(rs) >= C.FUTILITY_AT and statistics.mean(rs[:C.FUTILITY_AT]) <= 0:
            L.append("- **Futility rule triggered: the test has failed.**")
        if len(rs) >= C.FINAL_AT:
            first = trades[:C.FINAL_AT]
            m = statistics.mean(t.r("primary") for t in first)
            ms = statistics.mean(t.r("stress") for t in first)
            b = __import__("fast_bench").held(a, first, C.START_UTC, first[-1].exit_time + 1, runs=1000)
            z = (m - b[0]) / b[1] if b[1] > 0 else 0
            p = 0.5 * math.erfc(z / math.sqrt(2))
            ok = m > 0 and ms > 0 and p <= 0.05
            L.append(f"- **Final decision at {C.FINAL_AT} legs: {'PASS' if ok else 'FAIL'}** (E {m:+.3f}R, stress {ms:+.3f}R, p {p:.3f})")
    else:
        L.append("No BUY leg has closed yet.")
    L += ["", "Paper test only. A pass would justify a small, separately reviewed live trial, not full live trading."]
    open(STATUS, "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    for r in new:
        print(f"NEW LEG: entry {r['entry_utc']} at {r['entry']}, exit {r['exit_utc']}, {float(r['r_primary']):+.2f}R")
    json.dump({"last_bar_utc": fmt(last_bar), "legs": len(rs), "pending_buy_stop": pending[0] if pending else None},
              open(os.path.join(ROOT, "ledger", "state.json"), "w"), indent=1)
    shutil.rmtree(os.path.join(CACHE, "parts"), ignore_errors=True) if os.environ.get("PAPER_CLEAN") else None


if __name__ == "__main__":
    main()
