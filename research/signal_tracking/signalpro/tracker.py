"""SignalPro free-signal tracker. Paper evaluation only: no orders, and the app is not connected.

Pre-registered scoring, written 2026-11-10 before any outcome was known:

Price reference: Hyperliquid xyz:GOLD 1-minute candles for XAUUSD (a spot-tracking perpetual). The app's price feed is
unknown and differs from this feed (SP-001: the app shows entry 4094 while the feed was about 4085). Two methods are scored:

  A (primary, relative):
      E = open of the feed's 1m candle containing the posted time.
      Stop and targets keep the app's DISTANCES from its entry. For a SELL: SL = E + (app SL - app entry),
      TPk = E - (app entry - app TPk). A BUY is mirrored.
  B (absolute):
      The app's own price levels on this feed.
      SELL triggers when a 1m high >= entry at or after posting; BUY triggers when a low <= entry.
      Untriggered for 7 days -> NOT_TRIGGERED.

Resolution: scan 1m candles in order. If the stop and a target are touched in the same candle, the STOP counts first
(conservative). A trade still open after 7 days is closed at the last close (EXPIRED).

Results in R (risk = |SL - entry|):
  R_tp3_full : the whole position targets TP3.
  R_thirds   : 1/3 of the position closes at each TP, with the stop unchanged.
Both are gross (no spread or commission). Verification against Exness XAUUSDm ticks follows when the monthly archive
is published.

Every signal in signals.csv is scored. No selection, no edits to logged signals. Candles used are persisted to
candles/<coin>_1m.csv (append-only) for reproducibility.
"""
import csv, json, os, ssl, time, urllib.request, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
COIN = {"XAUUSD": "xyz:GOLD"}
MAX_DAYS = 7
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
fmt = lambda t: time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))
utc = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M"))


def fetch(coin, t0, t1):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1m", "startTime": t0 * 1000, "endTime": t1 * 1000}}).encode()
    req = urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"})
    rows = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read())
    now = time.time()
    return [(r["t"] // 1000, float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"])) for r in rows if r["T"] / 1000 < now]  # closed only


def candles(coin, t0):
    os.makedirs(os.path.join(HERE, "candles"), exist_ok=True)
    path = os.path.join(HERE, "candles", coin.replace(":", "_") + "_1m.csv")
    have = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)): have[int(r["t"])] = (int(r["t"]), float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]))
    for c in fetch(coin, t0, int(time.time())):
        if c[0] in have and have[c[0]] != c:
            raise SystemExit(f"DATA REVISION: {coin} candle {fmt(c[0])} changed {have[c[0]]} -> {c}")
        have[c[0]] = c
    rows = [have[k] for k in sorted(have)]
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c"]); w.writerows(rows)
    return rows


def resolve(cs, side, e, sl, tps, t_start):
    sgn = 1 if side == "BUY" else -1; hits = []; risk = abs(sl - e)
    for t, o, h, l, c in cs:
        if t < t_start: continue
        adverse, favor = (l, h) if sgn > 0 else (h, l)
        if (adverse - sl) * sgn <= 0:
            return dict(status="STOP", exit_time=fmt(t), tp_hits=hits, risk=risk, end_t=t)
        for k, tp in enumerate(tps):
            if k == len(hits) and (favor - tp) * sgn >= 0: hits.append(fmt(t))
        if len(hits) == len(tps):
            return dict(status="TP3", exit_time=fmt(t), tp_hits=hits, risk=risk, end_t=t)
        if t >= t_start + MAX_DAYS * 86400:
            return dict(status="EXPIRED", exit_time=fmt(t), tp_hits=hits, risk=risk, end_t=t, last=c)
    last = cs[-1] if cs else None
    return dict(status="OPEN", exit_time="", tp_hits=hits, risk=risk, end_t=None, last=last[4] if last else None)


def r_values(res, side, e, tps):
    sgn = 1 if side == "BUY" else -1; risk = res["risk"]; n = len(res["tp_hits"])
    gains = [abs(tp - e) / risk for tp in tps]
    if res["status"] == "OPEN": return "", ""
    if res["status"] == "TP3": full = gains[-1]
    elif res["status"] == "STOP": full = -1.0
    else: full = (res["last"] - e) * sgn / risk
    rest = -1.0 if res["status"] == "STOP" else ((res["last"] - e) * sgn / risk if res["status"] == "EXPIRED" else 0)
    thirds = sum(gains[:n]) / 3 + (3 - n) / 3 * (rest if res["status"] != "TP3" else 0)
    return round(full, 3), round(thirds, 3)


def main():
    sig = list(csv.DictReader(open(os.path.join(HERE, "signals.csv"))))
    out = []
    for s in sig:
        coin = COIN.get(s["instrument"])
        if not coin:
            out.append(dict(signal_id=s["signal_id"], method="-", status="UNSUPPORTED_INSTRUMENT")); continue
        t0 = utc(s["posted_utc_estimated"]); cs = candles(coin, t0 - 600)
        side = s["side"]; sgn = 1 if side == "BUY" else -1
        ae, asl, atp = float(s["entry"]), float(s["stop_loss"]), [float(s[k]) for k in ("tp1", "tp2", "tp3")]
        first = next((c for c in cs if c[0] <= t0 < c[0] + 60), None) or next((c for c in cs if c[0] >= t0), None)
        # method A
        E = first[1]; slA = E + (asl - ae); tpA = [E + (tp - ae) for tp in atp]
        rA = resolve(cs, side, E, slA, tpA, first[0]); fA, tA = r_values(rA, side, E, tpA)
        out.append(dict(signal_id=s["signal_id"], method="A_relative", instrument=s["instrument"], side=side, feed=coin, entry=round(E, 2), stop=round(slA, 2),
                        tps=" / ".join(f"{x:.2f}" for x in tpA), triggered_utc=fmt(first[0]), status=rA["status"], tp_hits=" | ".join(rA["tp_hits"]),
                        exit_utc=rA["exit_time"], R_tp3_full=fA, R_thirds=tA))
        # method B
        trig = next((c for c in cs if c[0] >= first[0] and ((c[2] >= ae) if sgn < 0 else (c[3] <= ae))), None)
        if trig is None:
            st = "NOT_TRIGGERED" if time.time() - t0 > MAX_DAYS * 86400 else "WAITING_FOR_TRIGGER"
            out.append(dict(signal_id=s["signal_id"], method="B_absolute", instrument=s["instrument"], side=side, feed=coin, entry=ae, stop=asl,
                            tps=" / ".join(f"{x:.2f}" for x in atp), triggered_utc="", status=st, tp_hits="", exit_utc="", R_tp3_full="", R_thirds=""))
        else:
            rB = resolve(cs, side, ae, asl, atp, trig[0]); fB, tB = r_values(rB, side, ae, atp)
            out.append(dict(signal_id=s["signal_id"], method="B_absolute", instrument=s["instrument"], side=side, feed=coin, entry=ae, stop=asl,
                            tps=" / ".join(f"{x:.2f}" for x in atp), triggered_utc=fmt(trig[0]), status=rB["status"], tp_hits=" | ".join(rB["tp_hits"]),
                            exit_utc=rB["exit_time"], R_tp3_full=fB, R_thirds=tB))
    keys = ["signal_id", "method", "instrument", "side", "feed", "entry", "stop", "tps", "triggered_utc", "status", "tp_hits", "exit_utc", "R_tp3_full", "R_thirds"]
    with open(os.path.join(HERE, "outcomes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    done = [o for o in out if o.get("method") == "A_relative" and o.get("R_tp3_full") not in ("", None)]
    lines = [f"# SignalPro free-signal tracking - updated {fmt(time.time())} UTC", "",
             "Paper evaluation only. Feed: Hyperliquid xyz:GOLD 1m (NOT the app's feed and NOT Exness). R values are gross (no costs).", "",
             f"- Signals logged: {len(sig)} | resolved (method A): {len(done)} | open: {sum(1 for o in out if o.get('status') == 'OPEN')}",
             "- No conclusion about the app is possible from a handful of signals.", "",
             "| Signal | Method | Side | Entry | Stop | TP1 / TP2 / TP3 | Status | TP hits | Exit | R (full to TP3) | R (thirds) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {o['signal_id']} | {o.get('method')} | {o.get('side', '')} | {o.get('entry', '')} | {o.get('stop', '')} | {o.get('tps', '')} | {o['status']} | "
              f"{o.get('tp_hits', '')} | {o.get('exit_utc', '')} | {o.get('R_tp3_full', '')} | {o.get('R_thirds', '')} |" for o in out]
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
