"""Forward PAPER test: oil Stochastic 4H entry, no extra orders, TP 100 pips + 4-pip trailing, SL 100 pips.
Rules frozen in FORWARD_RULES.md. Hyperliquid xyz:CL prices. Fake money, no orders.

Usage: python3 -I forward.py   (run hourly; processes each new closed 1m candle exactly once)
"""
import csv, json, os, ssl, time, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
COIN = "xyz:CL"; BBL = 10; STOP = 1.00; TP = 1.00; TRAIL = 0.04; HALF_SPREAD = 0.01
STATE, LEDGER, REPORT = (os.path.join(HERE, f) for f in ("state.json", "ledger.csv", "REPORT.md"))
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
FIELDS = ["side", "signal_4h_close_utc", "k", "d", "entry_utc", "entry_mid", "exit_utc", "exit_mid", "reason", "pnl_usd", "processed_utc"]
H1, M1 = 3_600_000, 60_000
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def candles(iv, start_ms):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": COIN, "interval": iv, "startTime": int(start_ms), "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}), timeout=30, context=CTX).read())
    now = time.time() * 1000
    return pd.DataFrame([dict(t=x["t"], T=x["T"], o=float(x["o"]), h=float(x["h"]), l=float(x["l"]), c=float(x["c"])) for x in r if x["T"] < now])


def stoch_signals(c4):
    k = (100 * (c4.c - c4.l.rolling(14).min()) / (c4.h.rolling(14).max() - c4.l.rolling(14).min())).rolling(3).mean(); d = k.rolling(3).mean()
    sig = np.where((k < 20) & (k > d), 1, np.where((k > 80) & (k < d), -1, 0))
    return pd.DataFrame(dict(close_ms=c4.t + 4 * H1, sig=sig, k=k, d=d))


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else None
    if st is None:
        st = dict(cursor=int(time.time() * 1000) // M1 * M1, pos=None, trades=0, pnl=0.0, started=fmt(time.time() * 1000))
    c4 = candles("4h", 1735689600000); sg = stoch_signals(c4)
    m1 = candles("1m", st["cursor"] - 5 * M1); m1 = m1[m1.t > st["cursor"]].reset_index(drop=True)
    rows = []
    for i in range(len(m1)):
        t, o, h, l = int(m1.t[i]), m1.o[i], m1.h[i], m1.l[i]
        if i and t - int(m1.t[i - 1]) > 90 * M1 and st["pos"] and pd.Timestamp(t, unit="ms").weekday() < 5:
            print("STOPPED: 1m feed gap > 90 min on a weekday with an open trade"); raise SystemExit(1)
        if st["pos"] is None and t % H1 == 0:
            s = sg[sg.close_ms <= t]
            if len(s) and s.sig.iloc[-1] != 0:
                st["pos"] = dict(side=int(s.sig.iloc[-1]), entry=o, entry_t=t, active=False, best=None,
                                 sig_close=fmt(int(s.close_ms.iloc[-1])), k=round(float(s.k.iloc[-1]), 2), d=round(float(s.d.iloc[-1]), 2))
        p = st["pos"]
        if p:
            sd = p["side"]; stop = p["entry"] - sd * STOP; adv, fav = (l, h) if sd > 0 else (h, l); ex = None
            if not p["active"]:
                if (o - stop) * sd <= 0 and t != p["entry_t"]: ex = (o, "stop (gap)")
                elif (adv - stop) * sd <= 0: ex = (stop, "stop -100 pips")
                elif (fav - (p["entry"] + sd * TP)) * sd >= 0: p["active"], p["best"] = True, fav
            else:
                lvl = p["best"] - sd * TRAIL
                if (o - lvl) * sd <= 0: ex = (o, "trailing TP (gap)")
                elif (adv - lvl) * sd <= 0: ex = (lvl, "trailing TP")
                else: p["best"] = max(p["best"], fav) if sd > 0 else min(p["best"], fav)
            if ex:
                pnl = (sd * (ex[0] - p["entry"]) - 2 * HALF_SPREAD) * BBL
                rows.append(dict(side="BUY" if sd > 0 else "SELL", signal_4h_close_utc=p["sig_close"], k=p["k"], d=p["d"], entry_utc=fmt(p["entry_t"]),
                                 entry_mid=p["entry"], exit_utc=fmt(t), exit_mid=round(ex[0], 4), reason=ex[1], pnl_usd=round(pnl, 2),
                                 processed_utc=fmt(time.time() * 1000)))
                st["trades"] += 1; st["pnl"] = round(st["pnl"] + pnl, 2); st["pos"] = None
        st["cursor"] = t
    if rows:
        new = not os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new: w.writeheader()
            w.writerows(rows)
    json.dump(st, open(STATE, "w"), indent=1)
    last = float(m1.c.iloc[-1]) if len(m1) else None; p = st["pos"]
    openp = (p["side"] * (last - p["entry"]) * BBL) if (p and last) else 0.0
    lines = [f"# Oil Stochastic 4H bot - forward PAPER test ({fmt(time.time() * 1000)} UTC)", "",
             "Hyperliquid xyz:CL (not Exness). 0.01 lot = 10 bbl, no extra orders, TP 100 pips + 4 trailing, SL 100 pips, 0.02 spread per round trip, swap 0. Fake money.", "",
             f"- Started {st['started']} UTC | closed trades: {st['trades']} / 100 for evaluation | realised P&L: {st['pnl']:+.2f} USD",
             f"- Open position: {('BUY' if p['side'] > 0 else 'SELL') + ' at ' + str(p['entry']) + ' since ' + fmt(p['entry_t']) + (' (trailing active)' if p['active'] else '') + f', floating {openp:+.2f} USD' if p else 'none'}",
             "- No conclusion before 100 closed trades."]
    open(REPORT, "w").write("\n".join(lines) + "\n")
    print(f"oil stoch paper: {len(rows)} trade(s) closed this run"); print("\n".join(lines[4:6]))


if __name__ == "__main__":
    main()
