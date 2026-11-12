"""Forward PAPER test of the theory-library survivors (GOLD_FVG, OIL_FIB). Rules frozen in FORWARD_RULES.md.
Hyperliquid public API, fake money, no orders.

Usage: python3 -I forward.py      (run hourly; processes each new closed 1m candle exactly once per test)
"""
import csv, json, os, ssl, time, urllib.request
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); M1, H1 = 60_000, 3_600_000
TESTS = {"GOLD_FVG": dict(coin="xyz:GOLD", spread=0.22, unit=1, unit_name="1 oz (0.01 lot)", kind="fvg"),
         "OIL_FIB": dict(coin="xyz:CL", spread=0.02, unit=10, unit_name="10 bbl (0.01 lot)", kind="fib")}
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
FIELDS = ["side", "signal_close_utc", "limit", "stop", "target", "fill_utc", "entry", "exit_utc", "exit", "reason", "gross_usd", "net_usd_1x", "net_usd_2x",
          "net_bp_2x", "processed_utc"]
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def stop(msg):
    print("STOPPED:", msg); raise SystemExit(1)


def candles(coin, iv, start_ms):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": coin, "interval": iv, "startTime": int(start_ms), "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}),
                                          timeout=30, context=CTX).read())
    now = time.time() * 1000
    return [(int(x["t"]), float(x["o"]), float(x["h"]), float(x["l"]), float(x["c"])) for x in r if x["T"] < now]


def signal(kind, hc):
    """hc: closed 1h candles (t,o,h,l,c), oldest first; the last one is candle i. Returns (side, lim, stop, tp) or None."""
    if kind == "fvg":
        if len(hc) < 3: return None
        h2, l2 = hc[-3][2], hc[-3][3]; hi, li = hc[-1][2], hc[-1][3]
        if li > h2: lim, st = h2, l2; return (1, lim, st, lim + 2 * (lim - st)) if lim > st else None
        if hi < l2: lim, st = l2, h2; return (-1, lim, st, lim - 2 * (st - lim)) if st > lim else None
        return None
    if len(hc) < 50: return None
    c = np.array([x[4] for x in hc]); s50 = c[-50:].mean(); w = hc[-20:]
    hh = np.array([x[2] for x in w]); ll = np.array([x[3] for x in w]); ih, il = int(np.argmax(hh)), int(np.argmin(ll)); H, L = hh[ih], ll[il]
    if H <= L: return None
    if c[-1] > s50 and ih > il: return (1, H - 0.618 * (H - L), L, H)
    if c[-1] < s50 and il > ih: return (-1, L + 0.618 * (H - L), H, L)
    return None


def run(name, cfg):
    sp, unit = cfg["spread"], cfg["unit"]; path = lambda f: os.path.join(HERE, f"{f}_{name}.{'json' if f == 'state' else 'csv'}")
    st = json.load(open(path("state"))) if os.path.exists(path("state")) else dict(
        cursor=int(time.time() * 1000) // M1 * M1, pending=[], pos=None, next_check=0, trades=0, net1=0.0, net2=0.0, bp2=0.0, wins2=0, started=fmt(time.time() * 1000))
    m1 = candles(cfg["coin"], "1m", st["cursor"] - 5 * M1)
    active = bool(st["pending"] or st["pos"])
    if not m1 or m1[0][0] > st["cursor"]:
        if active: stop(f"{name}: 1m feed does not reach back to the cursor {fmt(st['cursor'])}")
    m1 = [x for x in m1 if x[0] > st["cursor"]]
    h1 = candles(cfg["coin"], "1h", time.time() * 1000 - 40 * 86_400_000)
    rows = []; prev = st["cursor"]
    for t, o, h, l, cl in m1:
        if (st["pending"] or st["pos"]) and t - prev > 90 * M1 and time.gmtime(t / 1000).tm_wday < 5:
            stop(f"{name}: 1m feed gap {fmt(prev)} -> {fmt(t)} with an open order/position")
        if t % H1 == 0 and st["pos"] is None and t >= st["next_check"]:
            hc = [x for x in h1 if x[0] + H1 <= t]
            sg = signal(cfg["kind"], hc) if hc and hc[-1][0] + H1 == t else None
            if sg: st["pending"].append(dict(side=int(sg[0]), lim=float(sg[1]), stop=float(sg[2]), tp=float(sg[3]), made=t, expires=t + 10 * H1))
        p = st["pos"]
        if p is None and st["pending"]:
            st["pending"] = [q for q in st["pending"] if t < q["expires"]]
            for q in st["pending"]:                                   # oldest first
                if (q["side"] > 0 and l <= q["lim"] - sp) or (q["side"] < 0 and h >= q["lim"] + sp):
                    e = min(o, q["lim"]) if q["side"] > 0 else max(o, q["lim"])
                    st["pos"] = p = dict(side=q["side"], entry=float(e), stop=q["stop"], tp=q["tp"], lim=q["lim"], made=q["made"], fill=t, deadline=t // H1 * H1 + 21 * H1)
                    st["pending"] = []; break
        if p:
            sd, ex = p["side"], None
            if t > p["fill"] and ((sd > 0 and o <= p["stop"]) or (sd < 0 and o >= p["stop"])): ex = (o, "stop (gap)")
            elif (sd > 0 and l <= p["stop"]) or (sd < 0 and h >= p["stop"]): ex = (p["stop"], "stop")
            elif t > p["fill"] and ((sd > 0 and h >= p["tp"] + sp) or (sd < 0 and l <= p["tp"] - sp)): ex = (p["tp"], "target")
            elif t + M1 >= p["deadline"]: ex = (cl, "time (20 candles)")
            if ex:
                g = sd * (ex[0] - p["entry"]); n1, n2 = (g - sp) * unit, (g - 2 * sp) * unit; bp2 = (g - 2 * sp) / p["entry"] * 1e4
                rows.append(dict(side="BUY" if sd > 0 else "SELL", signal_close_utc=fmt(p["made"]), limit=round(p["lim"], 4), stop=round(p["stop"], 4), target=round(p["tp"], 4),
                                 fill_utc=fmt(p["fill"]), entry=round(p["entry"], 4), exit_utc=fmt(t), exit=round(ex[0], 4), reason=ex[1], gross_usd=round(g * unit, 2),
                                 net_usd_1x=round(n1, 2), net_usd_2x=round(n2, 2), net_bp_2x=round(bp2, 2), processed_utc=fmt(time.time() * 1000)))
                st["trades"] += 1; st["net1"] = round(float(st["net1"] + n1), 2); st["net2"] = round(float(st["net2"] + n2), 2); st["bp2"] = round(float(st["bp2"] + bp2), 3); st["wins2"] += int(n2 > 0)
                st["pos"] = None; st["next_check"] = t // H1 * H1 + 2 * H1
        st["cursor"] = prev = t
    if rows:
        new = not os.path.exists(path("ledger"))
        with open(path("ledger"), "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new: w.writeheader()
            w.writerows(rows)
    json.dump(st, open(path("state"), "w"), indent=1)
    last = m1[-1][4] if m1 else None; p = st["pos"]; n = st["trades"]
    flo = f", floating {p['side'] * (last - p['entry']) * unit:+.2f} USD" if (p and last) else ""
    return rows, [f"## {name} ({cfg['coin']}, {cfg['unit_name']})",
                  f"- Started {st['started']} UTC | closed trades {n} / 100 for evaluation | net {st['net1']:+.2f} USD at 1x, {st['net2']:+.2f} USD at 2x cost | "
                  f"win rate {(st['wins2'] / n * 100 if n else 0):.0f}% | average {(st['bp2'] / n if n else 0):+.2f} bp per trade at 2x",
                  f"- Open position: {(('BUY' if p['side'] > 0 else 'SELL') + ' at ' + str(round(p['entry'], 3)) + ' since ' + fmt(p['fill']) + ', stop ' + str(round(p['stop'], 3)) + ', target ' + str(round(p['tp'], 3)) + flo) if p else 'none'}"
                  f" | pending limit orders: {len(st['pending'])}", ""]


def main():
    lines = [f"# Theory-library survivors - forward PAPER test ({fmt(time.time() * 1000)} UTC)", "",
             "Hyperliquid prices (not Exness), fake money, rules frozen in FORWARD_RULES.md. No conclusion before 100 closed trades per test.", ""]
    for name, cfg in TESTS.items():
        rows, ln = run(name, cfg); lines += ln
        for r in rows: print(name, "closed:", r)
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    main()
