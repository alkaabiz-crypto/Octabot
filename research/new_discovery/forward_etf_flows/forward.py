"""STR-046 ETF-flow forward PAPER test (FORWARD_RULES.md). Daily: read flows, record first-seen 5-day-flow z per day in
signals.csv (append-only), open/close paper trades at Binance daily opens, append closed trades to ledger.csv, write REPORT.md.
usage: python3 -I forward.py"""
import csv, json, math, os, re, ssl, sys, time, urllib.request
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
START = "2026-11-20"; HOLD = 20; COST, STRESS = 0.0005, 0.0020
ASSETS = (("BTC", "bitcoin-etf-flows", "BTCUSDT"), ("ETH", "ethereum-etf-flows", "ETHUSDT"))
SIG, LED, REP = (os.path.join(HERE, f) for f in ("signals.csv", "ledger.csv", "REPORT.md"))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for k in range(4):
        try: return urllib.request.urlopen(req, timeout=60, context=CTX).read()
        except Exception:
            if k == 3: raise
            time.sleep(2 ** (k + 1))


def flows(page):
    t = get(f"https://cryptoetf.today/en/{page}").decode("utf-8", "ignore").replace('\\"', '"'); rows = {}
    for m in re.finditer(r'\{"date":"(\d{4}-\d{2}-\d{2})","flow":(-?[\d.eE+-]+)', t): rows[m.group(1)] = float(m.group(2))
    if len(rows) < 200: print("STOPPED: flow page returned too little data", len(rows)); sys.exit(1)
    return pd.Series(rows).sort_index()


def opens(sym, since):
    t0 = int(pd.Timestamp(since).timestamp() * 1000); r = json.loads(get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1d&startTime={t0}&limit=1000"))
    return {pd.Timestamp(x[0], unit="ms").strftime("%Y-%m-%d"): float(x[1]) for x in r}


def main():
    now = pd.Timestamp.now("UTC").strftime("%Y-%m-%d %H:%M")
    sig = list(csv.DictReader(open(SIG))) if os.path.exists(SIG) else []; seen = {(r["asset"], r["day"]) for r in sig}
    led = list(csv.DictReader(open(LED))) if os.path.exists(LED) else []; new_sig, lines = [], []
    for asset, page, sym in ASSETS:
        fl = flows(page); f5 = fl.rolling(5).sum(); z = (f5 - f5.rolling(60).mean().shift(1)) / f5.rolling(60).std().shift(1)
        for d, zv in z.items():
            if d >= START and not np.isnan(zv) and (asset, d) not in seen:
                new_sig.append(dict(asset=asset, day=d, z=round(float(zv), 4), flow=fl[d], first_seen_utc=now)); seen.add((asset, d))
    if new_sig:
        first = not os.path.exists(SIG)
        with open(SIG, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["asset", "day", "z", "flow", "first_seen_utc"]); first and w.writeheader(); w.writerows(new_sig)
    sig = list(csv.DictReader(open(SIG))) if os.path.exists(SIG) else []
    closed_keys = {(r["asset"], r["entry_day"]) for r in led}; new_closed = []; open_pos = {}
    for asset, page, sym in ASSETS:
        px = opens(sym, "2026-11-01"); busy_until = None
        for r in sorted([s for s in sig if s["asset"] == asset], key=lambda s: s["day"]):
            zv = float(r["z"]); ent = (pd.Timestamp(r["day"]) + pd.Timedelta(days=2)).strftime("%Y-%m-%d")
            if abs(zv) < 1 or (busy_until and ent < busy_until): continue
            ex = (pd.Timestamp(ent) + pd.Timedelta(days=HOLD)).strftime("%Y-%m-%d"); side = 1 if zv > 0 else -1; busy_until = ex
            if ent not in px: open_pos[asset] = dict(signal_day=r["day"], side=side, entry_due=ent); continue
            if ex not in px: open_pos[asset] = dict(signal_day=r["day"], side=side, entry_day=ent, entry=px[ent], exit_due=ex); continue
            if (asset, ent) not in closed_keys:
                g = side * (px[ex] / px[ent] - 1)
                new_closed.append(dict(asset=asset, signal_day=r["day"], z=zv, side=side, entry_day=ent, entry=px[ent], exit_day=ex, exit=px[ex],
                                       net_pct=round((g - 2 * COST) * 100, 3), stress_pct=round((g - 2 * STRESS) * 100, 3), processed_utc=now))
    if new_closed:
        first = not os.path.exists(LED)
        with open(LED, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(new_closed[0])); first and w.writeheader(); w.writerows(new_closed)
    led = list(csv.DictReader(open(LED))) if os.path.exists(LED) else []; x = np.array([float(r["net_pct"]) for r in led])
    stat = f"{len(x)} closed trades (first look at 40; futility check at 20)" + (f" | mean net {x.mean():+.2f}% per trade" + (f", t {x.mean() / (x.std(ddof=1) / math.sqrt(len(x))):+.2f}" if len(x) > 2 else "") if len(x) else "")
    rep = [f"# ETF-flow forward PAPER test, STR-046 ({now} UTC)", "", "Rules: `FORWARD_RULES.md` (frozen 2026-11-20). Paper only.", "", f"- {stat}",
           f"- New signals recorded this run: {len(new_sig)}; new closed trades: {len(new_closed)}"] + [f"- Open/pending {a}: {json.dumps(p)}" for a, p in open_pos.items()]
    last = {a: max([s for s in sig if s["asset"] == a], key=lambda s: s["day"], default=None) for a, *_ in ASSETS}
    rep += [f"- Latest {a} signal day {s['day']}: z {float(s['z']):+.2f}" for a, s in last.items() if s]
    open(REP, "w").write("\n".join(rep) + "\n"); print("\n".join(rep))


if __name__ == "__main__":
    main()
