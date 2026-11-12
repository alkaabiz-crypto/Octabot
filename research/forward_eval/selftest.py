"""Self-test of evaluate.py on SYNTHETIC prices and ledgers only (written to a temporary folder; nothing real is read or written).
Checks: a look-ahead "skilled" ledger PASSes; a random ledger does not; tests below target stay blind; only LIVE Donchian trades count;
the cost formulas reproduce the ledgers' own numbers; Batch 2 H3 dating, blindness and Holm logic; results are deterministic.
Usage: python3 -I selftest.py <empty scratch dir>
"""
import csv, gzip, json, os, subprocess, sys, time
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
D = sys.argv[1]; P = os.path.join(D, "prices"); R = os.path.join(D, "research"); os.makedirs(P, exist_ok=True)
M = 60_000; fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))
T0, T1 = 1794182400000, 1798761600000                   # 2026-11-09 00:00 -> 2027-01-01 00:00 (synthetic)
rng = np.random.default_rng(7); t = np.arange(T0, T1, M)
PX = {}
for sym, p0, vol in (("BTCUSDT", 100000, 4e-4), ("ETHUSDT", 3500, 6e-4), ("xyz_GOLD", 4000, 2e-4), ("xyz_CL", 60, 4e-4)):
    o = p0 * np.exp(np.cumsum(rng.normal(0, vol, len(t)))); PX[sym] = o
    with gzip.open(os.path.join(P, f"{sym}_1m.csv.gz"), "wt") as f:
        f.write("t_ms,o\n" + "\n".join(f"{a},{b:.6f}" for a, b in zip(t, o)) + "\n")
px = lambda sym, ms: PX[sym][int((ms - T0) // M)]


def w(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f: x = csv.DictWriter(f, fieldnames=list(rows[0])); x.writeheader(); x.writerows(rows)


def pick(sym, n, start, skilled, hold_min=(30, 600)):
    """n non-overlapping trades; skilled = side chosen with look-ahead (always the winning side)."""
    out, s = [], start
    for _ in range(n):
        s += int(rng.integers(5, 60)) * M; h = int(rng.integers(*hold_min)) * M; a, b = px(sym, s), px(sym, s + h)
        side = (1 if b > a else -1) if skilled else int(rng.choice([1, -1])); out.append((side, s, s + h, a, b)); s += h
    return out


# Donchian (long only): 45 trades, look-ahead picked; 3 are LATE (must be ignored)
start = 1794207600000; tr, ex = [], []; s = start; k = 0
while len(tr) < 45:
    s += int(rng.integers(5, 60)) * M; h = int(rng.integers(60, 600)) * M; a, b = px("BTCUSDT", s), px("BTCUSDT", s + h)
    if b <= a * 1.002: s += h; continue
    k += 1; sig = fmt(s - 3600_000); risk = a * 0.01
    tr.append(dict(trade_no=k, signal_close_utc=sig, exit_utc=fmt(s + h), exit_price=round(b, 2), R_net_mid=round((b - a) / risk - 0.0005 * a / risk, 4)))
    ex.append(dict(signal_close_utc=sig, execution_unix=s // 1000, execution_price_ask=round(a, 2), rule_risk_per_btc=round(risk, 2), status="LATE" if k in (3, 10, 20) else "LIVE"))
    s += h
w(os.path.join(R, "btc_breakout/forward/trades.csv"), tr); w(os.path.join(R, "btc_breakout/forward/execution_log.csv"), ex)

# Oil Stochastic: 100 random trades (no edge)
w(os.path.join(R, "oil_stoch_forward/ledger.csv"), [dict(side="BUY" if sd > 0 else "SELL", entry_utc=fmt(a), entry_mid=round(pa, 4), exit_utc=fmt(b), exit_mid=round(pb, 4),
  pnl_usd=round((sd * (pb - pa) - 0.02) * 10, 2)) for sd, a, b, pa, pb in pick("xyz_CL", 100, 1794320000000, False)])
# ETH_FIB: 100 skilled trades; GOLD_FVG: 50 trades (not due); OIL_FIB: none
eth = pick("ETHUSDT", 100, 1794550000000, True)
w(os.path.join(R, "library_forward/ledger_ETH_FIB.csv"), [dict(side="BUY" if sd > 0 else "SELL", fill_utc=fmt(a), entry=round(pa, 4), exit_utc=fmt(b), exit=round(pb, 4),
  net_bp_2x=round((sd * (pb - pa) - 2 * 0.0005 * (pa + pb)) / pa * 1e4, 2)) for sd, a, b, pa, pb in eth])
w(os.path.join(R, "library_forward/ledger_GOLD_FVG.csv"), [dict(side="BUY", fill_utc=fmt(a), entry=round(pa, 4), exit_utc=fmt(b), exit=round(pb, 4),
  net_bp_2x=round(((pb - pa) - 0.44) / pa * 1e4, 2)) for sd, a, b, pa, pb in pick("xyz_GOLD", 50, 1794550000000, False)])
w(os.path.join(R, "batch2/ledger.csv"), [dict(test="H3_BTC", decision_utc=fmt(1794620000000), side=1, entry_utc=fmt(1794620060000), entry=1.0, exit_utc=fmt(1794634460000), exit=1.0)])

NOW = T1 - 86_400_000
env = dict(os.environ, EVAL_PRICE_DIR=P)
outs = []
for run in (1, 2):
    o = os.path.join(D, f"out{run}"); subprocess.run([sys.executable, "-I", os.path.join(HERE, "evaluate.py"), "--root", R, "--now", str(NOW), "--out", o], env=env, check=True)
    outs.append(json.load(open(os.path.join(o, "results", "evaluation.json"))))
res = outs[0]["confirmatory"]; fails = []
chk = lambda cond, msg: fails.append(msg) if not cond else None
chk(json.dumps(outs[0]) == json.dumps(outs[1]), "results not deterministic")
chk(res["DONCHIAN_BTC"]["closed_valid"] == 42, f"Donchian LIVE filter: {res['DONCHIAN_BTC']['closed_valid']} valid (expected 42)")
chk(res["DONCHIAN_BTC"]["status"] == "PASS_PENDING_AUDIT", f"skilled Donchian should pass: {res['DONCHIAN_BTC']['status']}")
chk(res["DONCHIAN_BTC"]["stages"][0]["trades"] == 40, "Donchian must be judged on the first 40 valid trades")
chk(res["ETH_FIB"]["status"] == "PASS_PENDING_AUDIT", f"skilled ETH_FIB should pass: {res['ETH_FIB']['status']}")
chk(res["OIL_STOCH"]["status"] in ("FAIL", "INCONCLUSIVE_EXTENDED"), f"random oil ledger must not pass: {res['OIL_STOCH']['status']}")
for k in ("GOLD_FVG", "OIL_FIB", "H3_BTC", "H3_ETH"):
    chk(res[k]["status"] == "NOT_DUE" and not any(x in res[k] for x in ("stages", "stats_primary")), f"{k} must be NOT_DUE and blind")
chk(res["H3_BTC"]["evaluation_date"] == "2029-11-14 00:00", f"H3 cap date {res['H3_BTC']['evaluation_date']}")
# cost formulas reproduce the ledger's own figures
import evaluate as EV
for r in csv.DictReader(open(os.path.join(R, "library_forward/ledger_ETH_FIB.csv"))):
    v = EV.TESTS["ETH_FIB"]["metric"](EV.sgn(r["side"]), float(r["entry"]), float(r["exit"]), None)
    chk(abs(v - float(r["net_bp_2x"])) < 0.02, f"ETH cost formula mismatch {v} vs {r['net_bp_2x']}"); break
r = next(csv.DictReader(open(os.path.join(R, "oil_stoch_forward/ledger.csv"))))
v = EV.TESTS["OIL_STOCH"]["metric"](EV.sgn(r["side"]), float(r["entry_mid"]), float(r["exit_mid"]), None); o = EV.TESTS["OIL_STOCH"]["observed"](r)
chk(abs(v - o) < 0.05, f"oil formula mismatch {v} vs {o}")
# Holm logic for the two H3 tests (synthetic numbers)
mk = lambda p, m, n=600, nreq=479: dict(B1_random_p=p, B2_placebo_p=0.01, stats_primary=dict(mean_bp=m, trades=n), stats_stress=dict(mean_bp=m - 1), n_req=nreq)
cases = [({"H3_BTC": mk(0.02, 5), "H3_ETH": mk(0.04, 5, 700, 697)}, ("PASS_PENDING_AUDIT", "PASS_PENDING_AUDIT")),
         ({"H3_BTC": mk(0.03, 5), "H3_ETH": mk(0.04, 5, 700, 697)}, ("INCONCLUSIVE", "INCONCLUSIVE")),
         ({"H3_BTC": mk(0.02, 5, 400), "H3_ETH": mk(0.6, 5, 700, 697)}, ("INCONCLUSIVE", "FAIL")),
         ({"H3_BTC": mk(0.02, 5)}, ("PASS_PENDING_AUDIT",))]
for c, exp in cases:
    EV.holm2(c); got = tuple(c[k]["status"] for k in sorted(c))
    chk(got == exp, f"Holm case {exp}: got {got}")
print(json.dumps({k: (v["status"], v.get("stages", [{}])[0].get("random_timing", {}).get("p")) for k, v in res.items()}))
print("SELFTEST", "PASSED" if not fails else "FAILED:\n- " + "\n- ".join(fails))
sys.exit(1 if fails else 0)
