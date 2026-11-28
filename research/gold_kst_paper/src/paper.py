"""Gold KST + session VWAP BUY forward paper test on Exness XAUUSDm. Run any time:  python src/paper.py
1. checks the engine files are byte-identical to the frozen versions;
2. rebuilds 15-minute bid/ask candles from the Exness tick archive (current and previous month re-downloaded);
3. replays the rules and appends every leg entered since START_UTC to ledger/trades_<track>.csv (append-only);
4. writes ledger/STATUS.md (open leg, latest KST state, record, checkpoints) and ledger/state.json."""
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

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
sys.path.insert(0, HERE)
import config as C  # noqa: E402

CACHE = os.path.join(ROOT, "cache")
LEDGER_DIR = os.path.join(ROOT, "ledger")
FIELDS = ["entry_utc", "exit_utc", "entry", "r_gross", "r_primary", "r_stress", "hold_hours", "risk_2atr"]


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
    return time.strftime("%Y-%m-%d %H:%M", time.gmtime(int(t)))


def rebuild_bars():
    work = os.path.join(CACHE, "parts")
    os.makedirs(work, exist_ok=True)
    now = time.gmtime()
    prev = (now.tm_year, now.tm_mon - 1) if now.tm_mon > 1 else (now.tm_year - 1, 12)
    for y, m in ((now.tm_year, now.tm_mon), prev):
        p = os.path.join(work, f"{C.SYMBOL}_{y}_{m:02d}.csv")
        if os.path.exists(p):
            os.remove(p)
    out = os.path.join(CACHE, f"{C.SYMBOL}_15m.csv.gz")
    subprocess.run([sys.executable, os.path.join(RESEARCH, "oil_rsi_vwap", "src", "build_bars.py"), C.SYMBOL,
                    C.WARMUP_FIRST_MONTH, f"{now.tm_year}-{now.tm_mon:02d}", out, work, "2"], check=True, capture_output=True)
    for name in ("DFII10", "DTWEXBGS"):          # macro series for the shadow filters (published with a lag)
        subprocess.run(["curl", "-sSf", "-m", "60", "-o", os.path.join(CACHE, f"fred_{name}.csv"),
                        f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={name}"], check=True)
    os.environ["FRED_DIR"] = CACHE
    return out


def load(path):
    sys.path.insert(0, os.path.join(RESEARCH, "gold_kst_news", "src"))
    import engine as G
    g = G.Gold(path)
    ev = G.all_events()
    return G, g, G.Runner(g, ev["FOMC"] + ev["CPI"] + ev["NFP"])


def rows_of(G, R, L):
    rp, rs = R.r(L, "primary"), R.r(L, "stress")
    out = []
    for k in range(len(rp)):
        out.append({"entry_utc": fmt(L["entry_t"][k]), "exit_utc": fmt(L["exit_t"][k]), "entry": f"{L['entry'][k]:.3f}",
                    "r_gross": f"{L['r_gross'][k]:.4f}", "r_primary": f"{rp[k]:.4f}", "r_stress": f"{rs[k]:.4f}",
                    "hold_hours": f"{(L['exit_t'][k] - L['entry_t'][k]) / 3600:.2f}", "risk_2atr": f"{L['risk'][k]:.3f}"})
    return out


def write_ledger(track, rows):
    path = os.path.join(LEDGER_DIR, f"trades_{track}.csv")
    old = list(csv.DictReader(open(path))) if os.path.exists(path) else []
    for k, o in enumerate(old):
        if k >= len(rows) or rows[k] != o:
            raise LedgerChangedError(f"{track}: recorded leg {k + 1} ({o['entry_utc']}) changed; investigate before continuing")
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows[len(old):]


def open_leg(g, L, start, sig=None):
    """A BUY signal taken after the last closed leg whose exit has not happened yet (entry time) or None."""
    busy = max([start] + [int(x) for x in L["exit_t"]])
    sig = g.buy if sig is None else sig
    cand = [int(g.th[i]) + 3600 for i in range(len(g.th)) if sig[i] and int(g.th[i]) + 3600 >= busy]
    return cand[0] if cand else None


def stats(rs):
    if not len(rs):
        return "no closed legs yet"
    sd = statistics.pstdev(rs) if len(rs) > 1 else 0
    t = statistics.mean(rs) / (sd / math.sqrt(len(rs))) if sd > 0 else 0
    return (f"{len(rs)} legs, win {100 * sum(r > 0 for r in rs) / len(rs):.0f}%, expectancy {statistics.mean(rs):+.3f}R, "
            f"total {sum(rs):+.2f}R, t {t:+.2f}")


def main():
    check_frozen()
    path = rebuild_bars()
    G, g, R = load(path)
    last = int(g.th[-1]) + 3600
    lines = ["# Gold KST + session VWAP BUY paper test: status", "",
             f"Updated {fmt(time.time())} UTC. Data to {fmt(last)} UTC (the Exness archive lags about a day). "
             f"Counting since {fmt(C.START_UTC)} UTC. Rules: `research/gold_kst_news/PROTOCOL.md` and `src/config.py` (frozen).", ""]
    kst_up = None
    state = {"last_bar_utc": fmt(last)}
    flt = None
    for track, p, fname in [(C.PRIMARY[0], C.PRIMARY[1], None)] + list(C.SHADOWS):
        sig = None
        if fname:
            if flt is None:
                sys.path.insert(0, os.path.join(RESEARCH, "gold_kst_news", "src"))
                import ideas
                flt = ideas.filters(g)
            sig = np.array([b and o for b, o in zip(g.buy, flt[fname])])
        L = R.legs(p, C.START_UTC, last + 1, sig=sig)
        new = write_ledger(track, rows_of(G, R, L))
        rs = list(R.r(L, "primary"))
        ol = open_leg(g, L, C.START_UTC, None if sig is None else list(sig))
        lines += [f"## {track}{' (primary)' if track == C.PRIMARY[0] else ' (shadow, comparison only)'}", "",
                  f"- Record: {stats(rs)}"]
        if ol:
            lines.append(f"- **Open BUY leg since {fmt(ol)} UTC**")
        else:
            lines.append("- No open leg.")
        if track == C.PRIMARY[0]:
            reached = [c for c in C.CHECKPOINTS if len(rs) >= c]
            if reached:
                lines.append(f"- Checkpoints reached: {', '.join(map(str, reached))}")
            if len(rs) >= C.FUTILITY_AT and statistics.mean(rs[:C.FUTILITY_AT]) <= 0:
                lines.append("- **Futility rule triggered: the test has failed.**")
            if len(rs) >= C.FINAL_AT:
                sub = {k: v[:C.FINAL_AT] for k, v in L.items()}
                mu, sd = R.bench(p, sub, C.START_UTC, int(sub["exit_t"][-1]) + 1, runs=1000)
                m, ms = float(np.mean(R.r(sub, "primary"))), float(np.mean(R.r(sub, "stress")))
                z = (m - mu) / sd if sd > 0 else 0
                pz = 0.5 * math.erfc(z / math.sqrt(2))
                lines.append(f"- **Final decision at {C.FINAL_AT} legs: {'PASS' if m > 0 and ms > 0 and pz <= 0.05 else 'FAIL'}** "
                             f"(E {m:+.3f}R, stress {ms:+.3f}R, p {pz:.3f})")
        lines.append("")
        for r in new:
            print(f"NEW LEG [{track}]: entry {r['entry_utc']} at {r['entry']}, exit {r['exit_utc']}, {float(r['r_primary']):+.2f}R")
        state[track] = {"legs": len(rs), "open_leg_since": fmt(ol) if ol else None}
    up, dn = g.kst_up, g.kst_dn
    last_up = max([i for i in range(len(up)) if up[i]], default=None)
    last_dn = max([i for i in range(len(dn)) if dn[i]], default=None)
    kst_up = last_up is not None and (last_dn is None or last_up > last_dn)
    lines += ["## Signal state at the last candle", "",
              f"- KST is {'above' if kst_up else 'below'} its signal line (last bullish cross {fmt(g.th[last_up] + 3600) if last_up is not None else '-'}, "
              f"last bearish cross {fmt(g.th[last_dn] + 3600) if last_dn is not None else '-'} UTC).",
              f"- Last close {g.e.c[-1]:.2f} (bid); session VWAP {g.vwap[-1]:.2f}; ATR14 {g.atr[-1]:.2f}.", "",
              "Paper test only. Not a live trading signal."]
    state["kst_above_signal"] = kst_up
    open(os.path.join(LEDGER_DIR, "STATUS.md"), "w").write("\n".join(lines) + "\n")
    json.dump(state, open(os.path.join(LEDGER_DIR, "state.json"), "w"), indent=1)
    print("\n".join(lines))
    if os.environ.get("PAPER_CLEAN"):
        shutil.rmtree(os.path.join(CACHE, "parts"), ignore_errors=True)


if __name__ == "__main__":
    main()
