"""Forward PAPER observation of batch 003 H4 (Coinbase premium). Rules: FORWARD_RULES.md. Fake money, no orders.
usage: python3 -I forward.py                       (live: processes every closed hour since the cursor)
       python3 -I forward.py --replay START END    (history check into a scratch folder given by H4_DIR; never touches the live files)
"""
import csv, json, math, os, ssl, sys, time, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); DIR = os.environ.get("H4_DIR", HERE)
START = pd.Timestamp("2026-11-13 13:00", tz="UTC"); H = 3600; FEE = 0.0010; WIN = 720
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
LEDGER = ["signal_close_utc", "z", "prem", "side", "entry_utc", "entry", "exit_utc", "exit", "gross_bp", "net_bp_1x", "net_bp_2x", "processed_utc"]


def stop(msg):
    print("STOPPED:", msg); open(os.path.join(DIR, "RUN_ALERT.md"), "w").write(f"STOPPED {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC: {msg}\n"); raise SystemExit(1)


def get(url):
    for k in range(5):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-client"}), timeout=30, context=CTX).read())
        except Exception as e:
            if k == 4: stop(f"API failure {url.split('?')[0]}: {type(e).__name__}")
            time.sleep(2 ** k)


def hourly(t0, t1):
    """Closed hourly closes (Coinbase BTC-USD, Binance BTCUSDT) for hour starts in [t0, t1) (unix seconds)."""
    cb, t = {}, t0
    while t < t1:
        e = min(t + 300 * H, t1)
        for x in get(f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600&start={pd.Timestamp(t, unit='s').isoformat()}Z&end={pd.Timestamp(e, unit='s').isoformat()}Z"):
            if t0 <= x[0] < t1: cb[int(x[0])] = float(x[4])
        t = e; time.sleep(0.15)
    bn, t = {}, t0 * 1000
    while t < t1 * 1000:
        r = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&startTime={t}&limit=1000")
        if not r: break
        for x in r:
            if x[0] < t1 * 1000: bn[int(x[0]) // 1000] = float(x[4])
        t = r[-1][0] + 1
        if len(r) < 1000: break
    ts = sorted(set(cb) & set(bn)); x = pd.DataFrame(dict(t=ts, cb=[cb[s] for s in ts], bn=[bn[s] for s in ts]))
    x["prem"] = np.log(x.cb / x.bn); x["z"] = (x.prem - x.prem.rolling(WIN).mean().shift(1)) / x.prem.rolling(WIN).std().shift(1); x["close"] = x.t + H
    return x


def minute_open(ts, now):
    """Open of the first closed Binance 1m candle starting at or after ts (unix seconds); None if not yet available."""
    r = get(f"https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m&startTime={int(ts) * 1000}&limit=1")
    if not r or r[0][6] >= now * 1000: return None
    if r[0][0] - ts * 1000 > 10 * 60 * 1000: stop(f"1m gap after {pd.Timestamp(ts, unit='s')}")
    return int(r[0][0]) // 1000, float(r[0][1])


def fmt(s): return pd.Timestamp(s, unit="s").strftime("%Y-%m-%d %H:%M")


def run(now, start):
    sp, lp, gp = (os.path.join(DIR, f) for f in ("state.json", "ledger.csv", "signals.csv"))
    st = json.load(open(sp)) if os.path.exists(sp) else dict(cursor=int(start.timestamp()) - H, pos=None, free=0, trades=0, sum_net1=0.0)
    last_closed = (int(now) // H) * H                                  # the last hour whose close is <= now
    x = hourly(st["cursor"] - (WIN + 48) * H, last_closed)
    if len(x) and (np.diff(x.t.values) > H).any() and (x.t.values[-1] - x.t.values[0]) > 0:
        gaps = x.t.values[1:][np.diff(x.t.values) > H]
        if any(g > st["cursor"] - 24 * H for g in gaps): stop(f"hourly data gap near {fmt(int(gaps[-1]))}")
    if os.path.exists(gp):                                             # data-revision check on recorded signals
        rec = {int(r["close"]): float(r["prem"]) for r in csv.DictReader(open(gp))}; pm = dict(zip(x.close.values, x.prem.values))
        bad = [c for c, p in rec.items() if c in pm and abs(pm[c] - p) > 1e-9]
        if bad: stop(f"DATA REVISION at {[fmt(c) for c in bad[:3]]}")
    new_sig, rows = [], []
    def close_pos():
        p = st["pos"]; mo = minute_open(p["exit_due"], now)
        if mo is None: return False
        g = p["side"] * (mo[1] - p["entry"]) / p["entry"]
        rows.append(dict(signal_close_utc=fmt(p["signal_close"]), z=round(p["z"], 3), prem=p["prem"], side="LONG" if p["side"] > 0 else "SHORT", entry_utc=fmt(p["entry_t"]),
                         entry=p["entry"], exit_utc=fmt(mo[0]), exit=mo[1], gross_bp=round(g * 1e4, 2), net_bp_1x=round((g - 2 * FEE) * 1e4, 2), net_bp_2x=round((g - 4 * FEE) * 1e4, 2),
                         processed_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime())))
        st["trades"] += 1; st["sum_net1"] = round(st["sum_net1"] + (g - 2 * FEE) * 1e4, 3); st["free"] = mo[0]; st["pos"] = None; return True
    for r in x[(x.close > st["cursor"]) & (x.close <= last_closed)].itertuples():
        c = int(r.close)
        if st["pos"] and st["pos"]["exit_due"] <= c and not close_pos(): break
        if st["pos"] is None and c >= st["free"] and not math.isnan(r.z) and abs(r.z) >= 2:
            mo = minute_open(c, now)
            if mo is None: break                                       # entry minute not closed yet: retry next run
            side = 1 if r.z > 0 else -1; new_sig.append(dict(close=c, prem=repr(float(r.prem)), z=round(float(r.z), 4), side=side))
            st["pos"] = dict(side=side, signal_close=c, z=float(r.z), prem=float(r.prem), entry_t=mo[0], entry=mo[1], exit_due=mo[0] + 24 * H)
        st["cursor"] = c
    if st["pos"] and st["pos"]["exit_due"] <= now - 60: close_pos()
    for path, fields, data in ((lp, LEDGER, rows), (gp, ["close", "prem", "z", "side"], new_sig)):
        if data:
            new = not os.path.exists(path)
            with open(path, "a", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                if new: w.writeheader()
                w.writerows(data)
    json.dump(st, open(sp, "w"), indent=1)
    p = st["pos"]; n = st["trades"]
    rep = [f"# Coinbase premium forward PAPER observation ({time.strftime('%Y-%m-%d %H:%M', time.gmtime(now))} UTC)", "",
           f"Rules: `FORWARD_RULES.md` (pre-registered). Forward period from {fmt(int(start.timestamp()))} UTC. Binance prices, fake money.", "",
           f"- Hours processed to: {fmt(st['cursor'])} UTC | closed trades: {n} (first evaluation look at 100)",
           f"- Mean net per trade at the primary cost (0.10% per side): {(st['sum_net1'] / n if n else 0):+.2f} bp",
           "- Open position: " + (f"{'LONG' if p['side'] > 0 else 'SHORT'} from {fmt(p['entry_t'])} at {p['entry']}, z {p['z']:+.2f}, exit due {fmt(p['exit_due'])}" if p else "none"),
           f"- Latest z: {x.z.dropna().iloc[-1]:+.2f} at the close of {fmt(int(x.close.iloc[-1]))}" if len(x.z.dropna()) else "- Latest z: n/a", ""]
    open(os.path.join(DIR, "REPORT.md"), "w").write("\n".join(rep)); print("\n".join(rep))
    for r in rows: print("closed:", r)
    return rows


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--replay":
        assert DIR != HERE, "replays must use a scratch H4_DIR"
        s, e = pd.Timestamp(sys.argv[2], tz="UTC"), pd.Timestamp(sys.argv[3], tz="UTC"); t = s
        while t < e:                                                    # simulate daily runs
            t = min(t + pd.Timedelta(days=1), e); run(t.timestamp(), s)
    else:
        if time.time() < START.timestamp(): print("forward period not started yet"); raise SystemExit(0)
        run(time.time(), START)
