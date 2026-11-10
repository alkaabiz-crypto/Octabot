"""SignalPro free-signal tracker. Paper evaluation only: no orders, and the app is not connected.

Pre-registered scoring (2026-11-10, before any outcome was known; methods A and B unchanged since):

Price reference: Hyperliquid 1-minute candles. XAUUSD -> xyz:GOLD, USOIL -> xyz:CL (WTI). These feeds differ from the
app's own feed.

  A (relative): E = open of the feed's 1m candle containing the posting time. Stop and targets keep the app's
    DISTANCES from its entry.
  B (absolute): the app's own price levels. SELL triggers on a 1m high >= entry, BUY on a low <= entry, at or after
    the posting time. Untriggered for 7 days -> NOT_TRIGGERED.

Resolution: 1m candles in order. If the stop and a target fall in the same candle, the STOP counts first. Open after
7 days -> EXPIRED (closed at the last close).

R (risk = |SL - entry|):
  R_tp3_full : whole position to TP3, stop unchanged.
  R_thirds   : 1/3 of the position at each TP, stop unchanged.
  R_thirds_BE: like R_thirds, but the stop moves to entry after TP1. This is the app's displayed management
               ("SL moved to entry (B.E.)"); added 2026-11-10 as an extra, labelled variant.
All results are gross: no spread or commission.

Changes 2026-11-10 (batch 2):
  - The posting time is a WINDOW, because the app shows "Nh ago" rounded down. Each signal is scored at both window
    ends (early, late). Outcomes that differ between the two are flagged TIME_SENSITIVE.
  - USOIL is supported.
  - A signal with stop == entry is INVALID_ZERO_RISK (not scoreable in R).
  - capture_type: PROSPECTIVE signals (captured before any target or stop) are reported separately from
    RETROSPECTIVE ones (outcome already visible), to avoid selection bias.

Every logged signal is scored. Logged signals are never edited. Candles are persisted to candles/<coin>_1m.csv.
"""
import csv, json, os, ssl, time, urllib.request, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
COIN = {"XAUUSD": "xyz:GOLD", "USOIL": "xyz:CL"}
MAX_DAYS = 7
ctx = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
fmt = lambda t: time.strftime("%Y-%m-%d %H:%M", time.gmtime(t))
utc = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M"))


def fetch(coin, t0, t1):
    out = []
    while t0 < t1:
        body = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1m", "startTime": t0 * 1000, "endTime": t1 * 1000}}).encode()
        req = urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"})
        rows = json.loads(urllib.request.urlopen(req, timeout=30, context=ctx).read()) or []
        if not rows: break
        out += rows; nxt = rows[-1]["t"] // 1000 + 60
        if nxt <= t0 or len(rows) < 4000: break
        t0 = nxt
    now = time.time()
    return [(r["t"] // 1000, float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"])) for r in out if r["T"] / 1000 < now]


def candles(coin, t0):
    os.makedirs(os.path.join(HERE, "candles"), exist_ok=True)
    path = os.path.join(HERE, "candles", coin.replace(":", "_") + "_1m.csv")
    have = {}
    if os.path.exists(path):
        for r in csv.DictReader(open(path)): have[int(r["t"])] = (int(r["t"]), float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]))
    start = min([t0] + ([max(have)] if have else []))
    for c in fetch(coin, start, int(time.time())):
        if c[0] in have and have[c[0]] != c:
            raise SystemExit(f"DATA REVISION: {coin} candle {fmt(c[0])} changed {have[c[0]]} -> {c}")
        have[c[0]] = c
    rows = [have[k] for k in sorted(have)]
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "o", "h", "l", "c"]); w.writerows(rows)
    return rows


def resolve(cs, side, e, sl, tps, t_start, be=False):
    sgn = 1 if side == "BUY" else -1; hits = []; risk = abs(sl - e); stop = sl
    for t, o, h, l, c in cs:
        if t < t_start: continue
        adverse, favor = (l, h) if sgn > 0 else (h, l)
        if (adverse - stop) * sgn <= 0:
            return dict(status="STOP" if not hits else ("BE_STOP" if be else "STOP"), exit_time=fmt(t), tp_hits=hits, risk=risk, stop_px=stop)
        for k, tp in enumerate(tps):
            if k == len(hits) and (favor - tp) * sgn >= 0: hits.append(fmt(t))
        if be and hits: stop = e
        if len(hits) == len(tps):
            return dict(status="TP3", exit_time=fmt(t), tp_hits=hits, risk=risk)
        if t >= t_start + MAX_DAYS * 86400:
            return dict(status="EXPIRED", exit_time=fmt(t), tp_hits=hits, risk=risk, last=c)
    return dict(status="OPEN", exit_time="", tp_hits=hits, risk=risk)


def r_full(res, side, e, tps):
    sgn = 1 if side == "BUY" else -1; risk = res["risk"]
    if res["status"] == "OPEN": return ""
    if res["status"] == "TP3": return round(abs(tps[-1] - e) / risk, 3)
    if res["status"] == "EXPIRED": return round((res["last"] - e) * sgn / risk, 3)
    return -1.0


def r_thirds(res, side, e, tps):
    sgn = 1 if side == "BUY" else -1; risk = res["risk"]; n = len(res["tp_hits"])
    if res["status"] == "OPEN": return ""
    gains = sum(abs(tp - e) / risk for tp in tps[:n]) / 3
    if res["status"] == "TP3": return round(gains, 3)
    if res["status"] == "EXPIRED": rest = (res["last"] - e) * sgn / risk
    else: rest = (res["stop_px"] - e) * sgn / risk
    return round(gains + (3 - n) / 3 * rest, 3)


def score(cs, s, bound_name, t_post):
    side = s["side"]; sgn = 1 if side == "BUY" else -1
    ae, asl, atp = float(s["entry"]), float(s["stop_loss"]), [float(s[k]) for k in ("tp1", "tp2", "tp3")]
    first = next((c for c in cs if c[0] <= t_post < c[0] + 60), None) or next((c for c in cs if c[0] >= t_post), None)
    rows = []
    if first is None:
        return [dict(signal_id=s["signal_id"], method=f"A_relative@{bound_name}", status="NO_DATA"), dict(signal_id=s["signal_id"], method=f"B_absolute@{bound_name}", status="NO_DATA")]
    E = first[1]; slA = E + (asl - ae); tpA = [E + (tp - ae) for tp in atp]
    for meth, e, sl, tps, t_start, trig in (("A_relative", E, slA, tpA, first[0], fmt(first[0])), ("B_absolute", ae, asl, atp, None, None)):
        if meth == "B_absolute":
            tc = next((c for c in cs if c[0] >= first[0] and ((c[2] >= ae) if sgn < 0 else (c[3] <= ae))), None)
            if tc is None:
                st = "NOT_TRIGGERED" if time.time() - t_post > MAX_DAYS * 86400 else "WAITING_FOR_TRIGGER"
                rows.append(dict(signal_id=s["signal_id"], method=f"{meth}@{bound_name}", entry=e, stop=sl, tps=" / ".join(f"{x:.3f}" for x in tps), status=st))
                continue
            t_start, trig = tc[0], fmt(tc[0])
        r0 = resolve(cs, side, e, sl, tps, t_start); r1 = resolve(cs, side, e, sl, tps, t_start, be=True)
        rows.append(dict(signal_id=s["signal_id"], method=f"{meth}@{bound_name}", entry=round(e, 3), stop=round(sl, 3), tps=" / ".join(f"{x:.3f}" for x in tps),
                         triggered_utc=trig, status=r0["status"], tp_hits=", ".join(r0["tp_hits"]), exit_utc=r0["exit_time"],
                         R_tp3_full=r_full(r0, side, e, tps), R_thirds=r_thirds(r0, side, e, tps),
                         status_BE=r1["status"], R_thirds_BE=r_thirds(r1, side, e, tps)))
    return rows


def main():
    sig = list(csv.DictReader(open(os.path.join(HERE, "signals.csv"))))
    out, cache = [], {}
    for s in sig:
        base = dict(signal_id=s["signal_id"], capture=s.get("capture_type", "").split(" ")[0], instrument=s["instrument"], side=s["side"])
        if float(s["stop_loss"]) == float(s["entry"]):
            out.append(dict(base, method="-", status="INVALID_ZERO_RISK")); continue
        coin = COIN.get(s["instrument"])
        if not coin:
            out.append(dict(base, method="-", status="UNSUPPORTED_INSTRUMENT")); continue
        w0, w1 = utc(s["posted_window_start_utc"]), utc(s["posted_window_end_utc"])
        if coin not in cache: cache[coin] = candles(coin, min(utc(x["posted_window_start_utc"]) for x in sig if COIN.get(x["instrument"]) == coin) - 600)
        rows = score(cache[coin], s, "early", w0) + score(cache[coin], s, "late", w1)
        for r in rows:
            r.update(base, feed=coin)
        for m in ("A_relative", "B_absolute"):
            a = next(r for r in rows if r["method"] == f"{m}@early"); b = next(r for r in rows if r["method"] == f"{m}@late")
            flag = "TIME_SENSITIVE" if (a["status"], a.get("R_thirds")) != (b["status"], b.get("R_thirds")) else ""
            a["timing"] = b["timing"] = flag
        out += rows
    keys = ["signal_id", "capture", "instrument", "side", "feed", "method", "entry", "stop", "tps", "triggered_utc", "status", "tp_hits", "exit_utc",
            "R_tp3_full", "R_thirds", "status_BE", "R_thirds_BE", "timing"]
    with open(os.path.join(HERE, "outcomes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    lines = [f"# SignalPro free-signal tracking - updated {fmt(time.time())} UTC", "",
             "Paper evaluation only. Feeds: Hyperliquid xyz:GOLD / xyz:CL 1m (NOT the app's feed, NOT Exness). R values are gross (no costs).",
             "PROSPECTIVE = captured before any outcome; RETROSPECTIVE = outcome already visible when captured (selection-bias risk, reported separately).", "",
             f"- Signals logged: {len(sig)} (prospective {sum(1 for x in sig if x.get('capture_type', '').startswith('PROSPECTIVE'))}, "
             f"retrospective {sum(1 for x in sig if x.get('capture_type', '').startswith('RETROSPECTIVE'))})",
             "- No conclusion about the app is possible from a handful of signals.", "",
             "| Signal | Capture | Instr | Side | Method@window | Entry | Stop | TP1 / TP2 / TP3 | Status | TP hits | Exit | R full | R thirds | Status (BE) | R thirds (BE) | Timing |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {o['signal_id']} | {o.get('capture', '')} | {o.get('instrument', '')} | {o.get('side', '')} | {o.get('method', '')} | {o.get('entry', '')} | {o.get('stop', '')} | "
              f"{o.get('tps', '')} | {o['status']} | {o.get('tp_hits', '')} | {o.get('exit_utc', '')} | {o.get('R_tp3_full', '')} | {o.get('R_thirds', '')} | "
              f"{o.get('status_BE', '')} | {o.get('R_thirds_BE', '')} | {o.get('timing', '')} |" for o in out]
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
