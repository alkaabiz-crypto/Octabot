"""Forward PAPER test: gold MOM50 + ATR exits on Hyperliquid xyz:GOLD daily candles. Rules: FORWARD_RULES.md (frozen).

Usage: python3 -I forward.py      (run hourly; processes each newly closed weekday candle exactly once)
"""
import csv, json, os, ssl, time, urllib.request
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIRST_CLOSE = "2026-11-11"; START_EQ = 2722.94; COST = 0.20; DATA_START_MS = 1735689600000  # 2025-01-01
STATE, LEDGER, REPORT, CANDLES = (os.path.join(HERE, f) for f in ("state.json", "ledger.csv", "REPORT.md", "candles_xyz_GOLD_1d.csv"))
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
FIELDS = ["close_date", "action", "reason", "close", "sma20", "sma20_5d_ago", "close_50d_ago", "atr14", "entry_close", "peak_close", "days_held",
          "fill_date", "fill_price_open", "cost_usd", "oz_after", "cash_after", "equity_after", "processed_utc"]


def stop(msg):
    print("STOPPED:", msg); raise SystemExit(1)


def fetch():
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": "xyz:GOLD", "interval": "1d", "startTime": DATA_START_MS, "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}),
                                          timeout=30, context=CTX).read())
    now = time.time() * 1000
    d = pd.DataFrame([dict(t=x["t"], o=float(x["o"]), h=float(x["h"]), l=float(x["l"]), c=float(x["c"]), closed=x["T"] < now) for x in r])
    d["date"] = pd.to_datetime(d.t, unit="ms", utc=True); d = d[d.date.dt.weekday < 5].reset_index(drop=True)
    assert d.t.min() >= DATA_START_MS
    return d


def check_revisions(d):
    if os.path.exists(CANDLES):
        old = pd.read_csv(CANDLES)
        m = old.merge(d[d.closed], on="t", suffixes=("_old", ""))
        bad = m[(m.o_old != m.o) | (m.h_old != m.h) | (m.l_old != m.l) | (m.c_old != m.c)]
        if len(bad): stop(f"revised past candle(s): {bad.t.tolist()[:5]}")
    d[d.closed][["t", "o", "h", "l", "c"]].to_csv(CANDLES, index=False)
    gaps = d.date.diff().dt.days.dropna()
    if ((gaps != 1) & (gaps != 3)).any(): stop("weekday candle gap detected")


def main():
    d = fetch(); check_revisions(d)
    st = json.load(open(STATE)) if os.path.exists(STATE) else dict(last_close=None, pos=False, entry=None, peak=None, held=0, oz=0.0, cash=START_EQ, trades=0)
    cl = d[d.closed].reset_index(drop=True); c = cl.c
    tr = pd.concat([cl.h - cl.l, (cl.h - c.shift()).abs(), (cl.l - c.shift()).abs()], axis=1).max(axis=1); atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
    sma20 = c.rolling(20).mean(); rows = []
    for i in range(len(cl)):
        day = str(cl.date[i].date())
        if day < FIRST_CLOSE or (st["last_close"] and day <= st["last_close"]): continue
        nxt = d[d.t > cl.t[i]]
        if nxt.empty: break                                                        # next weekday candle not open yet
        fill_px, fill_day = float(nxt.o.iloc[0]), str(nxt.date.iloc[0].date())
        action, reason = "HOLD" if st["pos"] else "FLAT", ""
        if st["pos"]:
            st["held"] += 1; st["peak"] = max(st["peak"], c[i])
            if c[i] < st["entry"] - 2 * atr[i]: reason = "stop -2xATR"
            elif c[i] < st["peak"] - 1.5 * atr[i]: reason = "trailing -1.5xATR"
            elif st["held"] >= 30: reason = "30-day limit"
            if reason:
                action = "SELL"; st["cash"] = st["oz"] * (fill_px - COST); st["oz"] = 0.0; st["pos"] = False; st["trades"] += 1
        elif i >= 50 and c[i] > c[i - 50] and sma20[i] > sma20[i - 5]:
            action, reason = "BUY", "close > close 50d ago and SMA20 rising"
            st["oz"] = st["cash"] / (fill_px + COST); st["cash"] = 0.0; st["pos"] = True; st["entry"] = st["peak"] = float(c[i]); st["held"] = 0
        eq = st["cash"] + st["oz"] * fill_px
        rows.append(dict(close_date=day, action=action, reason=reason, close=c[i], sma20=round(sma20[i], 3), sma20_5d_ago=round(sma20[i - 5], 3),
                         close_50d_ago=c[i - 50] if i >= 50 else None, atr14=round(atr[i], 3), entry_close=st["entry"] if st["pos"] or action == "SELL" else None,
                         peak_close=st["peak"] if st["pos"] else None, days_held=st["held"] if st["pos"] else 0, fill_date=fill_day, fill_price_open=fill_px,
                         cost_usd=round(COST * (st["oz"] if action == "BUY" else (st["cash"] / (fill_px - COST) if action == "SELL" else 0)), 4),
                         oz_after=round(st["oz"], 6), cash_after=round(st["cash"], 2), equity_after=round(eq, 2), processed_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime())))
        st["last_close"] = day
    if rows:
        new = not os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new: w.writeheader()
            w.writerows(rows)
    json.dump(st, open(STATE, "w"), indent=1)
    last = float(d.c.iloc[-1]); eq = st["cash"] + st["oz"] * last
    led = pd.read_csv(LEDGER) if os.path.exists(LEDGER) else pd.DataFrame(columns=FIELDS)
    bh = (START_EQ / (led.fill_price_open.iloc[0] + COST) * last / START_EQ - 1) if len(led) else 0.0
    lines = [f"# Gold MOM50 + ATR exits - forward PAPER test ({time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC)", "",
             "Hyperliquid xyz:GOLD daily (weekdays), fake money 2,722.94 USD, long/flat, no leverage, 0.20 USD/oz per side, swap not deducted. Not Exness prices.", "",
             f"- Days processed: {len(led)} (first decision: close of {FIRST_CLOSE}) | completed trades: {st['trades']} / 20 for evaluation",
             f"- Position: {'LONG ' + format(st['oz'], '.4f') + ' oz since entry close ' + str(st['entry']) + ', held ' + str(st['held']) + ' days, peak ' + str(st['peak']) if st['pos'] else 'FLAT'}",
             f"- Equity now: {eq:,.2f} USD ({eq / START_EQ - 1:+.2%}) | buy and hold from first fill: {bh:+.2%}",
             "- No conclusion before 20 completed trades or 2027-11-11."]
    open(REPORT, "w").write("\n".join(lines) + "\n")
    print(f"gold mom50 paper: {len(rows)} new row(s)"); print("\n".join(lines[4:7]))


if __name__ == "__main__":
    main()
