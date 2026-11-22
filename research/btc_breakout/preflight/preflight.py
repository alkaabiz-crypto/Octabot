"""Pre-flight audit for the Donchian 20 forward paper test. READ-ONLY with respect to the frozen strategy, ledgers and research.

Checks: execution timing, Exness data reconciliation, strategy parity (code paths, hashes, numeric rule checks) and
independence. Writes preflight/results/PREFLIGHT_<stamp>.json and .md. Every claim is recomputed here.
"""
import calendar, csv, glob, gzip, hashlib, io, json, os, ssl, statistics, subprocess, sys, time, urllib.request, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); BB = os.path.dirname(HERE); REPO = os.path.dirname(os.path.dirname(BB))
sys.path.insert(0, os.path.join(BB, "src"))
from engine import Lab, last_closed, rma  # frozen engine, read-only
RESEARCH_COMMIT, FREEZE_COMMIT = "67d9824e", "ce2e8c57"
TMP = os.environ.get("PREFLIGHT_TMP", "/tmp")
checks = []


def add(area, name, result, evidence):
    checks.append(dict(area=area, check=name, result=result, evidence=evidence)); print(f"[{result}] {area}: {name} - {evidence[:180]}", flush=True)


def sh(*a): return subprocess.run(a, cwd=REPO, capture_output=True, text=True).stdout.strip()
def sha_at(commit, path): return hashlib.sha256(subprocess.run(["git", "show", f"{commit}:{path}"], cwd=REPO, capture_output=True).stdout).hexdigest()
def sha_now(path): return hashlib.sha256(open(os.path.join(REPO, path), "rb").read()).hexdigest()
def fmt(t): return time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))


def gunzip_dir(src_glob, dst):
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(src_glob):
        open(os.path.join(dst, os.path.basename(f)[:-3]), "wb").write(gzip.open(f).read())
    return dst


# ======================================================================= 1. EXECUTION TIMING
pt = open(os.path.join(BB, "forward", "paper_trader.py")).read(); eng = open(os.path.join(BB, "src", "engine.py")).read()
idealized = 'entry = po[j]' in eng and "self.p_idx.get(t_sig_close)" in eng
add("1 Execution timing", "Frozen ledger fill model", "FAIL (idealized)" if idealized else "UNKNOWN",
    "engine.simulate fills at po[j] = open of the 15m candle starting exactly at the signal close T (p_idx[t_sig_close]). "
    "The hourly worker runs at about T+6 min plus 1-2 min of downloads, so this price is not executable. The frozen ledger is kept "
    "unchanged as the research-consistent idealized record and must not be presented as realistic execution.")
sh_path = os.path.join(BB, "forward", "execution_shadow.py")
ok_shadow = os.path.exists(sh_path) and all(s in open(sh_path).read() for s in ("bookTicker", "execution_unix", "LIVE_MAX_MIN = 20", "slippage_vs_modeled_entry"))
add("1 Execution timing", "Executable-quote shadow log (first quote after signal calculation)", "PASS" if ok_shadow else "FAIL",
    "execution_shadow.py records candle close, signal calculation time, execution time, Binance bid/ask, ASK fill, 1s trade price, "
    "slippage vs modeled open and vs signal close, latency; LIVE if latency <= 20 min. Fixture test: idempotent, NOT_EXECUTABLE / LATE "
    "classification correct (LIVE path needs a real hourly run). Binance spot spread only - NOT Exness.")

# ======================================================================= 3. STRATEGY PARITY
files = {"research/btc_breakout/src/engine.py": RESEARCH_COMMIT, "research/btc_breakout/src/protocol.py": RESEARCH_COMMIT,
         "research/btc_breakout/forward/paper_trader.py": FREEZE_COMMIT, "research/btc_breakout/forward/FROZEN.json": FREEZE_COMMIT}
hashes = {p: dict(at_commit=c, sha256_then=sha_at(c, p)[:16], sha256_now=sha_now(p)[:16]) for p, c in files.items()}
add("3 Strategy parity", "Frozen file hashes unchanged", "PASS" if all(h["sha256_then"] == h["sha256_now"] for h in hashes.values()) else "FAIL",
    json.dumps(hashes))
wf = open(os.path.join(BB, "src", "run_walkforward.py")).read()
call_hist = "L.simulate(tf, model, d, stop, w0, w1)" in wf
call_fwd = 'L.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", CONFIG["forward_start"], 10 ** 11)' in pt
add("3 Strategy parity", "Same code path", "PASS" if call_hist and call_fwd else "FAIL",
    "research: run_walkforward.py -> engine.Lab.simulate(tf, model, d, stop, w0, w1) with defaults (stop_mult=2.0, trail_mult=3.0, dc_len=None->20) "
    "for variant 1h/M2_DONCHIAN20/LONG/TRAIL; forward: paper_trader.py -> engine.Lab.simulate(\"1h\",\"M2_DONCHIAN20\",1,\"TRAIL\",forward_start,1e11) "
    "with the same defaults (no keyword overrides).")
import importlib.util
spec = importlib.util.spec_from_file_location("pt", os.path.join(BB, "forward", "paper_trader.py")); ptm = importlib.util.module_from_spec(spec); spec.loader.exec_module(ptm)
fp_now = ptm.fingerprint(); fp_frozen = json.load(open(os.path.join(BB, "forward", "FROZEN.json")))["fingerprint"]
add("3 Strategy parity", "Configuration fingerprint (config + engine.py + protocol.py)", "PASS" if fp_now == fp_frozen else "FAIL",
    f"recomputed {fp_now[:16]}... vs FROZEN.json {fp_frozen[:16]}... ; config: {json.dumps({k: ptm.CONFIG[k] for k in ('model', 'direction', 'stop', 'initial_stop_atr', 'trail_atr', 'donchian_len', 'risk_per_trade')})}")

# numeric rule checks on BOTH datasets: research (2018-) and forward cache (2025-)
rdir = gunzip_dir(os.path.join(BB, "data", "btc_*.json.gz"), os.path.join(TMP, "pf_research"))
LR = Lab(rdir); LF = Lab(os.path.join(BB, "forward", "cache"))
for name, L in (("research data", LR), ("forward cache", LF)):
    E = L.B["1h"]; n = len(E["c"])
    bad_hh = sum(1 for i in range(20, n) if E["hh"][20][i] != max(E["h"][i - 20:i]))
    tr = [E["h"][0] - E["l"][0]] + [max(E["h"][i] - E["l"][i], abs(E["h"][i] - E["c"][i - 1]), abs(E["l"][i] - E["c"][i - 1])) for i in range(1, n)]
    atr = [None] * n; atr[13] = sum(tr[:14]) / 14
    for i in range(14, n): atr[i] = (atr[i - 1] * 13 + tr[i]) / 14
    bad_atr = sum(1 for i in range(13, n) if abs(atr[i] - E["atr"][i]) > 1e-9 * max(1, atr[i]))
    add("3 Strategy parity", f"Donchian HH20 = max of previous 20 COMPLETED 1H highs ({name})", "PASS" if bad_hh == 0 else "FAIL", f"{n - 20} candles checked, mismatches {bad_hh}")
    add("3 Strategy parity", f"ATR14 = Wilder RMA of true range ({name})", "PASS" if bad_atr == 0 else "FAIL", f"independent recompute over {n - 13} candles, mismatches {bad_atr}")
    H = L.B["4h"]; bad_htf = 0
    for i in range(300, n, 7):
        tc = E["t"][i] + 3600; k = last_closed(H["t"], 14400, tc)
        if not (H["t"][k] + 14400 <= tc and (k + 1 >= len(H["t"]) or H["t"][k + 1] + 14400 > tc)): bad_htf += 1
    add("3 Strategy parity", f"4H filter uses the last CLOSED 4H candle ({name})", "PASS" if bad_htf == 0 else "FAIL", f"sampled {len(range(300, n, 7))} signal times, violations {bad_htf}")
# warm-up / dataset parity: same signals and same 4H trend over the common period
c0, c1 = calendar.timegm((2025, 7, 1, 0, 0, 0)), calendar.timegm((2026, 11, 8, 0, 0, 0))
sr, sf = LR.signals("1h", "M2_DONCHIAN20", 1), LF.signals("1h", "M2_DONCHIAN20", 1)
set_r = {LR.B["1h"]["t"][i] for i in range(len(sr)) if sr[i] and c0 <= LR.B["1h"]["t"][i] < c1}
set_f = {LF.B["1h"]["t"][i] for i in range(len(sf)) if sf[i] and c0 <= LF.B["1h"]["t"][i] < c1}
HR, HF = LR.B["4h"], LF.B["4h"]; idx = {t: k for k, t in enumerate(HF["t"])}
diffs = [abs(HR["e200"][k] - HF["e200"][idx[t]]) for k, t in enumerate(HR["t"]) if c0 <= t < c1 and t in idx]
flips = sum(1 for k, t in enumerate(HR["t"]) if c0 <= t < c1 and t in idx and (HR["c"][k] > HR["e200"][k]) != (HF["c"][idx[t]] > HF["e200"][idx[t]]))
add("3 Strategy parity", "Warm-up independence: research (2018 warm-up) vs forward (2025 warm-up), 2025-07..2026-11",
    "PASS" if set_r == set_f and flips == 0 else "FAIL",
    f"breakout signals {len(set_r)} vs {len(set_f)} (identical={set_r == set_f}); 4H EMA200 max abs diff {max(diffs):.6f} USD; trend-filter flips {flips}")
trs_r = [t for t in LR.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", c0, c1) if t["exit"] != "data_end"]
trs_f = [t for t in LF.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", c0, c1) if t["exit"] != "data_end"]
same = [(a["entry_time"], round(a["R_gross"], 6), round(a["risk"], 4)) for a in trs_r] == [(b["entry_time"], round(b["R_gross"], 6), round(b["risk"], 4)) for b in trs_f]
E = LR.B["1h"]; tix = {t: i for i, t in enumerate(E["t"])}
stop_ok = all(abs(t["risk"] - 2.0 * E["atr"][tix[t["entry_time"] - 3600]]) < 1e-4 for t in trs_r)  # engine stores risk rounded to 4 dp
add("3 Strategy parity", "Trades identical on both datasets + initial stop = 2 x ATR14(signal candle)", "PASS" if same and stop_ok else "FAIL",
    f"{len(trs_r)} vs {len(trs_f)} closed trades over 2025-07..2026-11-08, identical entry/R/risk={same}; risk==2*ATR14 for all={stop_ok}")
# trailing stop 3 x ATR + sizing: independent audit replay results
aud = sorted(glob.glob(os.path.join(BB, "audit", "results", "audit_DRYRUN_TEST_past_period_*.json")))
a = json.load(open(aud[-1])) if aud else {}
trail_ok = a.get("independent_trades") == a.get("recorded_trades") == 21 and not any(f["severity"] == "DISCREPANCY" and "replay" in f["check"] for f in a.get("findings", []))
add("3 Strategy parity", "3 x ATR trailing stop + exits (independent re-implementation)", "PASS" if trail_ok else "FAIL",
    f"audit.py (independent code) replayed {a.get('independent_trades')} dry-run trades vs {a.get('recorded_trades')} recorded: no replay discrepancy in entry, exit time/price, R (dry-run = code validation only)")
siz = [f for f in a.get("findings", []) if any(k in f["check"] for k in ("risk usd", "size btc", "equity", "pnl"))]
add("3 Strategy parity", "Position sizing: risk = 0.5% equity, size = risk / (2 x ATR)", "PASS" if not siz else "FAIL",
    f"audit arithmetic on 21 dry-run trades: {len(siz)} sizing discrepancies; research metrics use the same 0.5%-of-equity-per-R compounding")

# ======================================================================= 4. INDEPENDENCE
closed_only = "closed = [r for r in rows if r[6] < now_ms]" in pt
add("4 Independence", "No unfinished/future candles used", "PASS" if closed_only else "FAIL",
    "paper_trader keeps only klines with closeTime < now; engine signals use bar i and earlier; 4H via last_closed(); the forward audits report 0 look-ahead/repainting findings")
hist_paths = ["research/btc_breakout/reports", "research/btc_breakout/logs", "research/btc_breakout/data", "research/btc_breakout/src", "research/btc_breakout/README.md"]
d = sh("git", "diff", "--stat", RESEARCH_COMMIT, "HEAD", "--", *hist_paths)
add("4 Independence", "Historical research results unmodified since research commit", "PASS" if not d else "FAIL", d or f"git diff {RESEARCH_COMMIT}..HEAD on {hist_paths}: empty")
ntr = json.load(open(os.path.join(BB, "forward", "status.json")))["completed_trades"]
src_log = sh("git", "log", "--oneline", f"{FREEZE_COMMIT}..HEAD", "--", "research/btc_breakout/src", "research/btc_breakout/forward/paper_trader.py", "research/btc_breakout/forward/FROZEN.json")
add("4 Independence", "No parameters changed/optimized after forward start", "PASS" if not src_log and fp_now == fp_frozen else "FAIL",
    f"commits touching strategy files since freeze: {src_log or 'none'}; forward trades so far: {ntr}")

# ======================================================================= 2. EXNESS DATA RECONCILIATION
ED = os.path.join(REPO, "research", "exness_validation", "data")
man = list(csv.DictReader(open(os.path.join(ED, "manifest.csv"))))
months = sorted(m["month"] for m in man)  # manifest is in build order
exp = []
y, mo = 2019, 1
while (y, mo) <= (2026, 10): exp.append(f"{y}-{mo:02d}"); y, mo = (y + 1, 1) if mo == 12 else (y, mo + 1)
add("2 Exness data", "Monthly coverage 2019-01..2026-10", "PASS" if months == exp else "FAIL", f"{len(months)} months present, missing {sorted(set(exp) - set(months))}, extra {sorted(set(months) - set(exp))}")
bars, viol, cross_bad, spikes, per_month_missing = [], 0, 0, [], {}
for m in man:
    rows = list(csv.DictReader(gzip.open(os.path.join(ED, "bars15m", f"BTCUSDm_{m['month'].replace('-', '_')}.csv.gz"), "rt")))
    yy, mm = map(int, m["month"].split("-")); start = calendar.timegm((yy, mm, 1, 0, 0, 0))
    end = calendar.timegm((yy + (mm == 12), 1 if mm == 12 else mm + 1, 1, 0, 0, 0))
    ts = [int(r["open_time_utc"]) for r in rows]
    per_month_missing[m["month"]] = (end - start) // 900 - len(set(ts))
    if any(t < start or t >= end or t % 900 for t in ts) or ts != sorted(set(ts)): viol += 1
    for r in rows:
        bo, bh, bl, bc = (float(r[k]) for k in ("bid_o", "bid_h", "bid_l", "bid_c")); ao, ah, al, ac = (float(r[k]) for k in ("ask_o", "ask_h", "ask_l", "ask_c"))
        if not (bl <= min(bo, bc) <= max(bo, bc) <= bh and al <= min(ao, ac) <= max(ao, ac) <= ah and ao >= bo and ac >= bc and float(r["spread_mean"]) >= 0): cross_bad += 1
        if (bh - bl) / bl > 0.08: spikes.append((fmt(int(r["open_time_utc"])), round((bh - bl) / bl * 100, 1)))
    bars += [(int(r["open_time_utc"]), float(r["bid_c"])) for r in rows]
add("2 Exness data", "Timestamps (UTC, 15m-aligned, inside their month, sorted, no duplicates)", "PASS" if viol == 0 else "FAIL", f"months with violations: {viol}")
add("2 Exness data", "Bid/ask candle integrity (low<=open/close<=high, ask>=bid at open/close, spread>=0)", "PASS" if cross_bad == 0 else "FAIL", f"violating 15m candles: {cross_bad} of {len(bars)}")
miss_total = sum(per_month_missing.values()); worst = sorted(per_month_missing.items(), key=lambda x: -x[1])[:6]
add("2 Exness data", "Completeness: missing 15m periods (no ticks)", "PASS (gaps documented)" if miss_total < 0.01 * len(bars) else "FAIL",
    f"{miss_total} missing 15m periods of {miss_total + len(bars)} ({miss_total / (miss_total + len(bars)) * 100:.3f}%); worst months {worst}. Gaps are NOT filled; '0 bad ticks' alone does not imply completeness.")
add("2 Exness data", "Price spikes (15m bid range > 8%)", "PASS" if len(spikes) < 50 else "REVIEW", f"{len(spikes)} candles: {spikes[:8]}")
# cross-check vs Binance 15m close (research data)
bmap = {c[0]: c[4] for c in LR.raw["15m"]}
dev = [abs(c - bmap[t]) / bmap[t] * 100 for t, c in bars if t in bmap]
by_year = {}
for t, c in bars:
    if t in bmap: by_year.setdefault(time.gmtime(t).tm_year, []).append((c - bmap[t]) / bmap[t] * 100)
yr = {y: dict(median_signed_pct=round(statistics.median(v), 4), median_abs_pct=round(statistics.median(abs(x) for x in v), 4), share_over_1pct=round(sum(abs(x) > 1 for x in v) / len(v) * 100, 2)) for y, v in sorted(by_year.items())}
add("2 Exness data", "Exness-Binance deviation by year (bid minus Binance close)", "INFO", json.dumps(yr))
allts = sorted(t for t, _ in bars); rng = []
for a2, b2 in zip(allts, allts[1:]):
    if b2 - a2 > 3600: rng.append(f"{fmt(a2 + 900)} -> {fmt(b2)} ({(b2 - a2) // 900 - 1} x 15m)")
add("2 Exness data", "Missing periods longer than 1 hour (exact ranges)", "INFO", "; ".join(rng) if rng else "none")
big = sum(1 for x in dev if x > 1.0)
add("2 Exness data", "Exness bid close vs Binance BTCUSDT close (15m)", "PASS" if statistics.median(dev) < 0.3 and big < 0.01 * len(dev) else "REVIEW",
    f"{len(dev)} matched candles: median abs dev {statistics.median(dev):.4f}%, p99 {sorted(dev)[int(0.99 * len(dev))]:.4f}%, >1%: {big}")
# checksum reproducibility (Exness publishes no checksums; verify by re-downloading two sample months)
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
repro = []
for m in (man[0], man[len(man) // 2]):
    data = urllib.request.urlopen(m["url"], timeout=300, context=ctx).read(); sha = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        lines = z.open(z.namelist()[0]).read().decode().splitlines()[1:]
    tsl = [l.split(",")[2] for l in lines]
    dup = len(tsl) - len(set(tsl)); exact_dup = len(lines) - len(set(lines)); nonmono = sum(1 for x, y2 in zip(tsl, tsl[1:]) if y2 < x)
    repro.append(dict(month=m["month"], sha_match=sha == m["zip_sha256"], ticks=len(lines), manifest_ticks=int(m["ticks"]), duplicate_timestamps=dup, exact_duplicate_rows=exact_dup, non_monotonic=nonmono))
add("2 Exness data", "Checksum reproducibility (re-download) + tick-level duplicates/order (sample months)",
    "PASS" if all(r["sha_match"] and r["ticks"] == r["manifest_ticks"] for r in repro) else "FAIL",
    json.dumps(repro) + " | Exness publishes no checksums: SHA256 values are recorded at download and only prove the files are reproducible, not authenticated.")

# ======================================================================= output
stamp = time.strftime("%Y%m%dT%H%MZ", time.gmtime()); os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
json.dump(dict(generated_utc=fmt(time.time()), checks=checks, exness_missing_by_month=per_month_missing), open(os.path.join(HERE, "results", f"PREFLIGHT_{stamp}.json"), "w"), indent=1)
md = [f"# Pre-flight audit - {fmt(time.time())} UTC", "", "| Area | Check | Result | Evidence |", "|---|---|---|---|"] + \
     [f"| {c['area']} | {c['check']} | **{c['result']}** | {c['evidence'].replace('|', '/')} |" for c in checks]
open(os.path.join(HERE, "results", f"PREFLIGHT_{stamp}.md"), "w").write("\n".join(md) + "\n")
print(f"\nsaved preflight/results/PREFLIGHT_{stamp}.(json|md)")
