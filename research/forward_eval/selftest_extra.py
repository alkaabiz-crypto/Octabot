"""Extra checks on SYNTHETIC data (run after selftest.py, same scratch dir): false-positive rate of the random-timing rule on 300 no-skill
ledgers (expected about 0.7%), and the Batch 2 H3 path once due (dating, benchmarks, Holm). Usage: python3 -I selftest_extra.py <selftest dir>
"""
import sys, os, csv, time, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); S = sys.argv[1]; sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "batch2"))
os.environ["EVAL_PRICE_DIR"] = os.path.join(S, "prices"); import evaluate as EV, common as C
import gzip
o = np.array([float(r["o"]) for r in csv.DictReader(gzip.open(os.path.join(S, "prices/ETHUSDT_1m.csv.gz"), "rt"))]); T0 = 1794182400000; M = 60000
rng = np.random.default_rng(1); passes = fails = inc = 0; N = 300
cfg = EV.TESTS["ETH_FIB"]
for k in range(N):
    s = 1794550000000; trs = []
    for _ in range(100):
        s += int(rng.integers(5, 60)) * M; h = int(rng.integers(30, 600)) * M; a, b = o[(s - T0) // M], o[(s + h - T0) // M]; sd = int(rng.choice([1, -1]))
        trs.append(dict(side=sd, entry_ms=s, exit_ms=s + h, p_in=a, p_out=b, obs=cfg["metric"](sd, a, b, None))); s += h
    t = np.arange(T0, T0 + len(o) * M, M); end = trs[-1]["exit_ms"]; sel = (t >= 1794550000000) & (t <= end + M)
    st = EV.stats([x["obs"] for x in trs]); d = EV.random_timing(trs, cfg["metric"], t[sel], o[sel], 1794550000000, end, k); p = EV.pval(st["mean"], d)
    if st["mean"] > 0 and p <= EV.BAR: passes += 1
    elif st["mean"] <= 0 or p > 0.5: fails += 1
    else: inc += 1
print(f"null ledgers: {N}; PASS {passes} ({passes/max(N,1):.1%}), FAIL {fails}, INCONCLUSIVE {inc}")
# Batch 2 H3 due-path with synthetic data (end = E + 7 months, n_req tiny via cfg override)
E = EV.E_MS; end = EV.add_months(E, 7); tt = np.arange(E, end + 2 * M, M); px = 1e5 * np.exp(np.cumsum(rng.normal(0, 4e-4, len(tt))))
m1 = pd.DataFrame(dict(t=tt, o=px, h=px, l=px, c=px, v=1.0, close_ms=tt + M, tbv=0.5))
th = np.arange(C.START_MS, end, 3_600_000); h1 = pd.DataFrame(dict(t=th, o=1.0, h=1.0, l=1.0, c=1.0, v=10.0, close_ms=th + 3_600_000, tbv=np.clip(5 + rng.standard_t(3, len(th)), 0.1, 9.9)))
EV.b2_data = lambda coin, e: (m1, h1)
rows = []; d0 = E
for i in range(40):
    d0 += int(rng.integers(5, 100)) * 3_600_000; a = d0 + M; b = a + 4 * 3_600_000; ia, ib = (a - E) // M, (b - E) // M
    rows.append(dict(test="H3_BTC", decision_utc=EV.fmt(d0), side=1, entry_utc=EV.fmt(a), entry=px[ia], exit_utc=EV.fmt(b), exit=px[ib])); d0 = b
os.makedirs(os.path.join(S, "b2/batch2"), exist_ok=True)
with open(os.path.join(S, "b2/batch2/ledger.csv"), "w", newline="") as f: w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
cfg2 = dict(EV.TESTS["H3_BTC"], n_req=30)
r, p1 = EV.judge_batch2("H3_BTC", cfg2, os.path.join(S, "b2"), end + 86_400_000); EV.holm2({"H3_BTC": r})
print("H3 due path:", r["status"], "eval date", r["evaluation_date"], "n", r["stats_primary"]["trades"], "mean", r["stats_primary"]["mean_bp"], "B1", r["B1_random_p"], "B2", r["B2_placebo_p"], "cov", r["m1_coverage"])
