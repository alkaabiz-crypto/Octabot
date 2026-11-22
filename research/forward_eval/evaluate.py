"""Forward evaluator: implements research/FORWARD_EVALUATION.md (4-test confirmatory family, revision of 2026-11-12) and, for
Batch 2 H3, research/batch2/PREREGISTRATION.md as amended by AMENDMENT_1.md and AMENDMENT_2.md. Written and frozen before any
forward trade existed (re-frozen 2026-11-12, still with zero forward trades, after research/library_checks/README.md).

BLIND: a test that is not yet due shows only its progress count, never running statistics or p-values.
Reads the unchanged ledgers; never writes to them. Output: results/evaluation.json and EVALUATION.md (in this folder or --out).

Usage: python3 -I evaluate.py [--root <research dir>] [--now <unix ms>] [--out <dir>]   (--root/--now/--out exist for selftest.py)
Prices for the random-timing benchmark: Binance spot 1m (re-fetched, not stored), Hyperliquid 1m from prices/ (archive_prices.py).
"""
import argparse, calendar, csv, gzip, json, os, sys, time, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ALPHA, FAMILY, DRAWS, SEED_BASE = 0.05, 4, 1000, 20261113
BAR = ALPHA / FAMILY                                   # Bonferroni across the confirmatory family (FORWARD_EVALUATION.md)
M = 60_000
ms_of = lambda s: calendar.timegm(time.strptime(s.strip()[:16], "%Y-%m-%d %H:%M")) * 1000
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))
read = lambda p: list(csv.DictReader(open(p))) if os.path.exists(p) else []
sgn = lambda s: 1 if str(s).upper() in ("BUY", "LONG", "1") else -1

# metric(side, p_in, p_out, trade) -> per-trade result in the test's unit, used identically for real and random trades
bp = lambda cost: (lambda sd, a, b, tr: sd * (b / a - 1) * 1e4 - cost(a, b))
TESTS = {
    "DONCHIAN_BTC": dict(kind="donchian", feed=("binance", "BTCUSDT"), target=40, start="2026-11-09 07:00", unit="R (executable ask fill, 0.05% cost)"),
    "OIL_STOCH":    dict(kind="ledger", path="oil_stoch_forward/ledger.csv", t_in="entry_utc", p_in="entry_mid", p_out="exit_mid",
                         feed=("hyperliquid", "xyz:CL"), target=100, start="2026-11-11 08:26", unit="net bp (0.02 USD/bbl spread)",
                         metric=bp(lambda a, b: 0.02 / a * 1e4), observed=lambda r: float(r["pnl_usd"]) / (10 * float(r["entry_mid"])) * 1e4),
}
# Demoted to MONITORING on 2026-11-12 (research/library_checks/README.md: their historical edge was an order-handling look-ahead).
# Kept here only so the cost formulas stay documented and self-tested; they are never judged.
LIBRARY_MONITORING = {
    "GOLD_FVG":     dict(kind="ledger", path="library_forward/ledger_GOLD_FVG.csv", t_in="fill_utc", p_in="entry", p_out="exit",
                         feed=("hyperliquid", "xyz:GOLD"), target=100, start="2026-11-12 16:44", unit="net bp at 2x cost",
                         metric=bp(lambda a, b: 2 * 0.22 / a * 1e4), observed=lambda r: float(r["net_bp_2x"])),
    "OIL_FIB":      dict(kind="ledger", path="library_forward/ledger_OIL_FIB.csv", t_in="fill_utc", p_in="entry", p_out="exit",
                         feed=("hyperliquid", "xyz:CL"), target=100, start="2026-11-12 16:44", unit="net bp at 2x cost",
                         metric=bp(lambda a, b: 2 * 0.02 / a * 1e4), observed=lambda r: float(r["net_bp_2x"])),
    "ETH_FIB":      dict(kind="ledger", path="library_forward/ledger_ETH_FIB.csv", t_in="fill_utc", p_in="entry", p_out="exit",
                         feed=("binance", "ETHUSDT"), target=100, start="2026-11-12 17:25", unit="net bp at 2x cost",
                         metric=bp(lambda a, b: 2 * 0.0005 * (a + b) / a * 1e4), observed=lambda r: float(r["net_bp_2x"])),
}
TESTS.update({
    "H3_BTC": dict(kind="batch2", coin="BTC", n_req=479), "H3_ETH": dict(kind="batch2", coin="ETH", n_req=697),
})
MONITORING = ["GOLD_FVG", "OIL_FIB", "ETH_FIB", "TREND_ENS_BTC", "TREND_ENS_ETH", "GOLD_MOM50", "H1_BTC", "H1_ETH", "H2_BTC", "H2_ETH", "H4_BTC", "H4_ETH"]
E_MS = 1794614400000                                   # Batch 2 forward start 2026-11-14 00:00 UTC
add_months = lambda ms, k: calendar.timegm((lambda t: (t.tm_year + (t.tm_mon - 1 + k) // 12, (t.tm_mon - 1 + k) % 12 + 1, t.tm_mday, 0, 0, 0))(time.gmtime(ms / 1000))) * 1000


# ------------------------------------------------------------------ prices
def prices(feed, start_ms, end_ms):
    """Sorted arrays (t_ms, open) of 1m candles covering [start_ms, end_ms]."""
    src, sym = feed; local = os.environ.get("EVAL_PRICE_DIR")
    if local:                                          # selftest: synthetic prices
        rows = list(csv.DictReader(gzip.open(os.path.join(local, f"{sym.replace(':', '_')}_1m.csv.gz"), "rt")))
    elif src == "hyperliquid":
        d = os.path.join(HERE, "prices"); rows = []
        for f in sorted(os.listdir(d)):
            if f.startswith(sym.replace(":", "_") + "_1m_"): rows += list(csv.DictReader(gzip.open(os.path.join(d, f), "rt")))
    else:
        sys.path.insert(0, os.path.join(HERE, "..", "batch2")); import common as C
        k = C.binance_klines(sym, "1m", start_ms, end_ms + M); rows = [dict(t_ms=t, o=o) for t, o in zip(k.t.values, k.o.values)]
    t = np.array([int(r["t_ms"]) for r in rows], dtype=np.int64); o = np.array([float(r["o"]) for r in rows]); ix = np.argsort(t)
    t, o = t[ix], o[ix]; keep = (t >= start_ms) & (t <= end_ms + M); return t[keep], o[keep]


def coverage(t, start_ms, end_ms):
    t = np.asarray(t); return round(float(((t >= start_ms) & (t <= end_ms)).sum()) / max(1, (end_ms - start_ms) // M + 1), 4)


# ------------------------------------------------------------------ trades
def donchian_trades(root):
    base = os.path.join(root, "btc_breakout", "forward"); live = {r["signal_close_utc"]: r for r in read(os.path.join(base, "execution_log.csv")) if r.get("status") == "LIVE"}
    out = []
    for r in read(os.path.join(base, "trades.csv")):
        x = live.get(r["signal_close_utc"])
        if not x: continue                             # EVALUATION_RULES.md: only trades with a LIVE execution record are valid
        a, b, risk = float(x["execution_price_ask"]), float(r["exit_price"]), float(x["rule_risk_per_btc"])
        out.append(dict(side=1, entry_ms=int(float(x["execution_unix"])) * 1000, exit_ms=ms_of(r["exit_utc"]), p_in=a, p_out=b, risk=risk,
                        obs=(b - a) / risk - 0.0005 * a / risk, obs_high=(b - a) / risk - 0.0010 * a / risk, obs_ideal=float(r["R_net_mid"])))
    return out


def donchian_metric(sd, a, b, tr): return (b - a) / tr["risk"] - 0.0005 * a / tr["risk"]


def ledger_trades(root, cfg):
    return [dict(side=sgn(r["side"]), entry_ms=ms_of(r[cfg["t_in"]]), exit_ms=ms_of(r["exit_utc"]), p_in=float(r[cfg["p_in"]]), p_out=float(r[cfg["p_out"]]),
                 obs=cfg["observed"](r)) for r in read(os.path.join(root, cfg["path"]))]


# ------------------------------------------------------------------ statistics
def stats(x):
    x = np.asarray(x, float); n = len(x); se = x.std(ddof=1) / np.sqrt(n) if n > 1 else np.nan
    gp, gl = x[x > 0].sum(), -x[x < 0].sum()
    return dict(n=n, mean=round(float(x.mean()), 4), median=round(float(np.median(x)), 4), sd=round(float(x.std(ddof=1)), 4) if n > 1 else None,
                ci95=[round(float(x.mean() - 1.96 * se), 4), round(float(x.mean() + 1.96 * se), 4)] if n > 1 else None,
                win_rate=round(float((x > 0).mean()), 3), profit_factor=round(float(gp / gl), 3) if gl > 0 else None, total=round(float(x.sum()), 4))


def random_timing(trs, metric, t, o, start_ms, end_ms, seed):
    """Same sides, holding times and cost model; each trade's start drawn uniformly among 1m candles in [start, end - hold]."""
    rng = np.random.default_rng(seed); means = np.full(DRAWS, np.nan)
    for k in range(DRAWS):
        vals = []
        for tr in trs:
            hold = tr["exit_ms"] - tr["entry_ms"]; hi = end_ms - hold
            if hi <= start_ms: continue
            s = int(rng.integers(start_ms // M, hi // M + 1)) * M; i = int(np.searchsorted(t, s)); j = int(np.searchsorted(t, s + hold))
            if j >= len(t) or i >= len(t): continue
            vals.append(metric(tr["side"], o[i], o[j], tr))
        if vals: means[k] = np.mean(vals)
    return means


def pval(obs, draws):
    d = draws[~np.isnan(draws)]; return round(float((1 + (d >= obs).sum()) / (1 + len(d))), 4) if len(d) else None


# ------------------------------------------------------------------ verdicts
def judge_simple(tid, cfg, root, now):
    trs = donchian_trades(root) if cfg["kind"] == "donchian" else ledger_trades(root, cfg)
    trs = [x for x in trs if x["exit_ms"] <= now]; n_all, target = len(trs), cfg["target"]
    stage = 2 if n_all >= 2 * target else 1 if n_all >= target else 0
    out = dict(test=tid, family="confirmatory", unit=cfg["unit"], target=target, closed_valid=n_all)
    if stage == 0: out.update(status="NOT_DUE", note=f"{n_all}/{target} (blind until due)"); return out, None
    results = []
    for st in range(1, stage + 1):
        ev = trs[: st * target]; start_ms = ms_of(cfg["start"]); end_ms = max(x["exit_ms"] for x in ev)
        t, o = prices(cfg["feed"], start_ms, end_ms); metric = donchian_metric if cfg["kind"] == "donchian" else cfg["metric"]
        obs = np.array([x["obs"] for x in ev]); s = stats(obs)
        draws = random_timing(ev, metric, t, o, start_ms, end_ms, SEED_BASE + zlib.crc32(tid.encode()) + st); p = pval(s["mean"], draws)
        ok_mean = s["mean"] > 0 and (cfg["kind"] != "donchian" or float(np.mean([x["obs_high"] for x in ev])) > 0)
        v = ("PASS_PENDING_AUDIT" if ok_mean and p is not None and p <= BAR else
             "FAIL" if (not s["mean"] > 0) or (p is not None and p > 0.5) else "INCONCLUSIVE" if st == 1 else "NOT_CONFIRMED")
        r = dict(stage=st, trades=len(ev), window=[fmt(start_ms), fmt(end_ms)], stats=s, random_timing=dict(p=p, bar=round(BAR, 5),
                 median=round(float(np.nanmedian(draws)), 4), p95=round(float(np.nanpercentile(draws, 95)), 4)), price_coverage=coverage(t, start_ms, end_ms), verdict=v)
        if cfg["kind"] == "donchian":
            r["mean_R_at_0.10pct"] = round(float(np.mean([x["obs_high"] for x in ev])), 4); r["mean_R_idealized_fill"] = round(float(np.mean([x["obs_ideal"] for x in ev])), 4)
        if r["price_coverage"] < 0.99: r["warning"] = "price coverage below 99%: benchmark less reliable"
        results.append(r)
        if v != "INCONCLUSIVE": break
    last = results[-1]
    out.update(status=last["verdict"] if not (last["verdict"] == "INCONCLUSIVE" and stage == 1) else "INCONCLUSIVE_EXTENDED",
               note=(f"extended to {2 * target} trades; {n_all}/{2 * target}" if last["verdict"] == "INCONCLUSIVE" else ""), stages=results)
    return out, None


def b2_data(coin, end_ms):                             # overridden by selftest.py
    sys.path.insert(0, os.path.join(HERE, "..", "batch2")); import common as C
    return C.binance_klines(f"{coin}USDT", "1m", E_MS, end_ms), C.binance_klines(f"{coin}USDT", "1h", C.START_MS, end_ms)


def judge_batch2(tid, cfg, root, now):
    sys.path.insert(0, os.path.join(HERE, "..", "batch2")); import common as C
    rows = [r for r in read(os.path.join(root, "batch2", "ledger.csv")) if r["test"] == tid]
    trs = sorted([dict(decision_ms=ms_of(r["decision_utc"]), side=int(r["side"]), entry_ms=ms_of(r["entry_utc"]), entry=float(r["entry"]),
                       exit_ms=ms_of(r["exit_utc"]), exit=float(r["exit"])) for r in rows], key=lambda z: z["exit_ms"])
    six, cap = add_months(E_MS, 6), add_months(E_MS, 36)
    d_nreq = trs[cfg["n_req"] - 1]["exit_ms"] if len(trs) >= cfg["n_req"] else None
    eval_ms = min(max(d_nreq or cap, six), cap)
    out = dict(test=tid, family="confirmatory (Batch 2; B1 p <= 0.05/4, AMENDMENT_2.md)", unit="net bp (pre-registered primary/stress costs)",
               n_req=cfg["n_req"], evaluation_date=fmt(eval_ms), closed=len([x for x in trs if x["exit_ms"] <= now]))
    if now < eval_ms: out.update(status="NOT_DUE", note=f"{out['closed']}/{cfg['n_req']} trades; evaluation date {fmt(eval_ms)} at the latest (blind until due)"); return out, None
    ev = [x for x in trs if x["exit_ms"] <= eval_ms]; coin = cfg["coin"]
    if not ev: out.update(status="INCONCLUSIVE", note="no closed trades by the evaluation date"); return out, None
    m1, h1 = b2_data(coin, eval_ms); s1, s2 = C.summarize(ev, coin, "primary"), C.summarize(ev, coin, "stress")
    obs = s1["mean_bp"] / 1e4; seed = C.test_seed(tid)
    b1 = C.bench_random(ev, "H3", coin, m1, E_MS, eval_ms, seed); b2 = C.bench_placebo(C.h3_signals(h1), "H3", coin, m1, E_MS, eval_ms, seed)
    p1 = C.pval(obs, b1) if b1 is not None else None; p2 = C.pval(obs, b2) if b2 is not None else None   # None: no draws possible -> cannot pass
    out.update(stats_primary=s1, stats_stress=s2, B1_random_p=p1, B2_placebo_p=p2, m1_coverage=coverage(m1.t.values, E_MS, eval_ms))
    return out, p1


def judge_h3(results):
    """Batch 2 H3 verdicts (AMENDMENT_2.md): B1 p <= 0.05/4 (Bonferroni across the 4 confirmatory tests), B2 p <= 0.05."""
    for k, r in results.items():
        if not (k.startswith("H3_") and r.get("B1_random_p") is not None): continue
        thr = BAR; holm_ok = r["B1_random_p"] <= thr
        s1, s2 = r["stats_primary"], r["stats_stress"]; n = s1["trades"]
        if s1["mean_bp"] <= 0 or r["B1_random_p"] > 0.5: v = "FAIL"
        elif s1["mean_bp"] > 0 and s2["mean_bp"] > 0 and holm_ok and (r["B2_placebo_p"] if r["B2_placebo_p"] is not None else 1.0) <= 0.05 and n >= 30 and n >= r["n_req"]: v = "PASS_PENDING_AUDIT"
        else: v = "INCONCLUSIVE"
        r.update(holm_threshold=round(thr, 4), status=v)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=os.path.abspath(os.path.join(HERE, ".."))); ap.add_argument("--now", type=int)
    ap.add_argument("--out", default=HERE); a = ap.parse_args(); now = a.now or int(time.time() * 1000)
    res = {}
    for tid, cfg in TESTS.items(): res[tid] = (judge_batch2 if cfg["kind"] == "batch2" else judge_simple)(tid, cfg, a.root, now)[0]
    judge_h3(res)
    doc = dict(generated_utc=fmt(now), rules="research/FORWARD_EVALUATION.md; research/batch2/PREREGISTRATION.md + AMENDMENT_1.md",
               bar=dict(family=FAMILY, one_sided_p=round(BAR, 5)), confirmatory=res, monitoring_only=MONITORING)
    os.makedirs(os.path.join(a.out, "results"), exist_ok=True); json.dump(doc, open(os.path.join(a.out, "results", "evaluation.json"), "w"), indent=1)
    L = [f"# Forward evaluation ({fmt(now)} UTC)", "", f"Confirmatory family of {FAMILY}; a test passes only with random-timing p <= {BAR:.4f}, a positive mean at its stated cost "
         "and a clean independent audit (FORWARD_EVALUATION.md). **Blind:** tests not yet due show progress only. A PASS means more paper testing at real Exness prices, never live money by itself.", "",
         "| Test | Status | Progress / note |", "|---|---|---|"]
    for tid, r in res.items():
        L.append(f"| {tid} | **{r['status']}** | {r.get('note') or ''} |")
    L += ["", "Monitoring only (can never pass): " + ", ".join(MONITORING) + "."]
    for tid, r in res.items():
        if r["status"] != "NOT_DUE": L += ["", f"## {tid}", "```json", json.dumps(r, indent=1), "```"]
    open(os.path.join(a.out, "EVALUATION.md"), "w").write("\n".join(L) + "\n"); print("\n".join(L[4:4 + len(res) + 2]))


if __name__ == "__main__":
    main()
