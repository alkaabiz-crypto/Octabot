"""STR-023 forward PAPER test (FORWARD_RULES.md). Replays the frozen rsi_vwap_study rules on closed Binance candles.
usage: python3 -I forward.py                 (live)
       STR023_DIR=<scratch> python3 -I forward.py --replay START_ISO END_ISO   (history check; never touches live files)
"""
import csv, hashlib, json, math, os, ssl, sys, tempfile, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.environ.get("STR023_DIR", HERE)
STUDY = os.path.join(os.path.dirname(os.path.dirname(HERE)), "rsi_vwap_study", "src"); sys.path.insert(0, STUDY)
import study as S  # noqa: E402  (frozen study code, unchanged)

START = S.ts(2026, 11, 14); COSTS = {"primary": 0.0005, "stress": 0.0010, "binance_taker": 0.0020}
MARKETS = ("BTCUSDT", "ETHUSDT")
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
FIELDS = ["market", "signal_close_utc", "exit_utc", "entry", "risk", "reason", "r_gross", "r_primary", "r_stress", "r_binance_taker", "regime"]


def stop(msg):
    print("STOPPED:", msg); open(os.path.join(DIR, "RUN_ALERT.md"), "w").write(f"STOPPED {S.fmt(time.time())} UTC: {msg}\n"); raise SystemExit(1)


def klines(sym, iv, t0, now):
    out, t = [], t0 * 1000
    while True:
        for k in range(5):
            try:
                r = json.loads(urllib.request.urlopen(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={iv}&startTime={t}&limit=1000", timeout=30, context=CTX).read()); break
            except Exception as e:
                if k == 4: stop(f"Binance API failure {sym} {iv}: {type(e).__name__}")
                time.sleep(2 ** k)
        out += [[x[0] // 1000, float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5])] for x in r if x[6] < now * 1000]
        if len(r) < 1000 or r[-1][6] >= now * 1000: return out
        t = r[-1][0] + 1


def trades_for(sym, now):
    tmp = tempfile.mkdtemp(); paths = {}
    for iv, back in (("15m", 3 * 86400), ("1h", 40 * 86400), ("1d", 400 * 86400)):
        rows = klines(sym, iv, START - back, now); p = os.path.join(tmp, f"{iv}.json"); json.dump(rows, open(p, "w")); paths[iv] = p
        gaps = [b[0] - a[0] for a, b in zip(rows, rows[1:]) if b[0] - a[0] > {"15m": 900, "1h": 3600, "1d": 86400}[iv] * 3]
        if gaps and iv != "1d": stop(f"{sym} {iv} data gap of {max(gaps) // 60} min")
    A = S.Asset(sym, paths["15m"], paths["1h"], paths["1d"])
    E = A.e; sig = A.signals("V1_VWAP_MOMENTUM", S.DIRECTIONS["BUY"]); tab = A.table(1, "TRAIL"); out = []; open_pos = None
    i = next((k for k, t in enumerate(E.t) if t + 3600 >= START), len(E.t))
    while i < len(E.t):
        if not sig[i]: i += 1; continue
        tr = tab[i]
        if tr is None:                                   # signal whose trade is still open (or entry candle not yet closed)
            if E.t[i] + 3600 < now - 900: open_pos = dict(signal_close=S.fmt(E.t[i] + 3600), entry=A.p.o[A.p_idx[E.t[i] + 3600]] if (E.t[i] + 3600) in A.p_idx else None)
            break
        out.append(tr); i = next((k for k in range(i + 1, len(E.t)) if E.t[k] + 3600 > tr.exit_time), len(E.t))
    return out, open_pos


def row(sym, tr):
    rr = {k: round(tr.r_gross - c * tr.entry / tr.risk, 4) for k, c in COSTS.items()}
    return dict(market=sym, signal_close_utc=S.fmt(tr.entry_time), exit_utc=S.fmt(tr.exit_time), entry=tr.entry, risk=round(tr.risk, 4), reason=tr.reason,
                r_gross=round(tr.r_gross, 4), r_primary=rr["primary"], r_stress=rr["stress"], r_binance_taker=rr["binance_taker"], regime=tr.regime)


def nw(x, L=5):
    n = len(x); m = sum(x) / n; d = [v - m for v in x]; g = lambda j: sum(d[i] * d[i - j] for i in range(j, n)) / n
    v = g(0) + 2 * sum((1 - j / (L + 1)) * g(j) for j in range(1, min(L, n - 1) + 1)); return m, math.sqrt(max(v, 1e-12) / n)


def run(now):
    lp = os.path.join(DIR, "ledger.csv"); old = list(csv.DictReader(open(lp))) if os.path.exists(lp) else []
    rows, opens = [], {}
    for sym in MARKETS:
        tr, op = trades_for(sym, now); rows += [row(sym, t) for t in tr]; opens[sym] = op
    key = lambda r: (r["market"], r["signal_close_utc"]); new = {key(r): r for r in rows}
    for r in old:                                         # previously recorded trades must reproduce exactly
        n = new.get(key(r))
        if n is None or any(str(n[f]) != str(r[f]) for f in ("exit_utc", "reason", "r_gross")): stop(f"DATA REVISION for {key(r)}")
    with open(lp, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(sorted(rows, key=lambda r: (r["signal_close_utc"], r["market"])))
    lines = [f"# STR-023 forward PAPER test: VWAP momentum BUY + trail ({S.fmt(now)} UTC)", "", "Rules: `FORWARD_RULES.md` (pre-registered). Binance prices, fake money. Forward period from 2026-11-14 00:00 UTC.", ""]
    for sym in MARKETS:
        x = [float(r["r_primary"]) for r in rows if r["market"] == sym]; n = len(x)
        s = (f"mean {sum(x) / n:+.3f}R at 0.05% | " + f"{sum(float(r['r_binance_taker']) for r in rows if r['market'] == sym) / n:+.3f}R at 0.20%") if n else "no closed trades"
        look = ""
        for L in (100, 300, 600, 1000):
            if n >= L:
                m, se = nw(x[:L]); look = (f" | look {L}: PASS" if m / se >= 2.5 and m >= 0.05 else (f" | look {L}: STOP (futility)" if m + 1.645 * se < 0.05 else f" | look {L}: continue"))
                if "PASS" in look or "STOP" in look: break
        lines.append(f"- **{sym}**: {n} closed trades (first look at 100) | {s}{look} | open: {opens[sym] or 'none'}")
    open(os.path.join(DIR, "REPORT.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--replay":
        assert DIR != HERE; START = S.ts(*map(int, sys.argv[2].split("-")))
        run(S.ts(*map(int, sys.argv[3].split("-"))))
    else:
        if time.time() < START: print("forward period not started yet"); raise SystemExit(0)
        run(time.time())
