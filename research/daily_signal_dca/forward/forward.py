"""Forward PAPER test of the TREND_ENS daily signal bot (spot, 1x). No orders, no accounts, fake money only.

Rule (fixed, from ../PREREGISTRATION.md and ../from_2025/run.py):
  after each daily close (00:00 UTC), target coin share = share of the AVAILABLE SMA20/50/100/200 (daily closes, data
  from 2025-01-01 only) that the close is above. The difference is traded at the next daily candle's open, fee 0.1%.
Accounts per coin (BTCUSDT, ETHUSDT):
  LUMP: starts with 2,722.94 USD (10,000 AED) cash.
  DCA:  10 USD is added before every daily decision; the same target share applies to the whole pot.
First decision: the close of 2026-11-10 (executed at the 2026-11-11 open). Nothing earlier is traded.
Exactly-once: state.json holds the last processed close date; ledger.csv is append-only.

Usage: python3 -I forward.py
"""
import csv, json, os, sys, time, urllib.request
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import study as S  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SYMS = ["BTCUSDT", "ETHUSDT"]; FEE = 0.001; LUMP0 = 2722.94; DCA_DAY = 10.0
DATA_START = "2025-01-01"; FIRST_CLOSE = "2026-11-10"
STATE, LEDGER, REPORT = (os.path.join(HERE, f) for f in ("state.json", "ledger.csv", "REPORT.md"))
FIELDS = ["close_date", "exec_utc", "symbol", "account", "signal_share", "above_sma20", "above_sma50", "above_sma100", "above_sma200",
          "exec_price_open", "contribution_usd", "trade_usd", "fee_usd", "coin_after", "usd_after", "value_after", "processed_utc"]


def daily(sym):
    t0 = int(pd.Timestamp(DATA_START, tz="UTC").value // 10**6); rows = []
    while True:
        r = json.loads(urllib.request.urlopen(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval=1d&startTime={t0}&limit=1000",
                                              timeout=30, context=S.CTX).read())
        if not r: break
        rows += [[x[0], float(x[1]), float(x[4]), x[6]] for x in r]
        if len(r) < 1000: break
        t0 = r[-1][0] + 1
    d = pd.DataFrame(rows, columns=["t", "o", "c", "close_t"]); d["date"] = pd.to_datetime(d.t, unit="ms", utc=True)
    assert d.t.min() >= int(pd.Timestamp(DATA_START, tz="UTC").value // 10**6), "pre-2025 data must not be used"
    gaps = int((d.date.diff().dt.days.dropna() != 1).sum())
    if gaps: raise SystemExit(f"STOPPED: {sym} daily candle gap detected ({gaps})")
    return d


def main():
    now_ms = int(time.time() * 1000)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {s: dict(last_close=None, LUMP=dict(usd=LUMP0, coin=0.0),
                                                                             DCA=dict(usd=0.0, coin=0.0, contributed=0.0)) for s in SYMS}
    new_rows = []
    for sym in SYMS:
        d = daily(sym); c = d.c
        closed = d[d.close_t < now_ms].reset_index(drop=True)                     # fully closed daily candles
        cc = closed.c; smas = {n: cc.rolling(n).mean() for n in (20, 50, 100, 200)}
        st = state[sym]
        for i in range(len(closed)):
            day = str(closed.date[i].date())
            if day < FIRST_CLOSE or (st["last_close"] and day <= st["last_close"]): continue
            nxt = d[d.t == closed.t[i] + 86_400_000]
            if nxt.empty: break                                                    # next candle not started yet
            px = float(nxt.o.iloc[0])
            votes = {n: (bool(cc[i] > smas[n][i]) if not np.isnan(smas[n][i]) else None) for n in smas}
            avail = [v for v in votes.values() if v is not None]; share = sum(avail) / len(avail)
            for acc in ("LUMP", "DCA"):
                a = st[acc]; contrib = 0.0
                if acc == "DCA": a["usd"] += DCA_DAY; a["contributed"] += DCA_DAY; contrib = DCA_DAY
                V = a["usd"] + a["coin"] * px; delta = share * V - a["coin"] * px; fee = abs(delta) * FEE
                a["coin"] += delta / px; a["usd"] -= delta + fee
                new_rows.append(dict(close_date=day, exec_utc=str(nxt.date.iloc[0]), symbol=sym, account=acc, signal_share=share,
                                     above_sma20=votes[20], above_sma50=votes[50], above_sma100=votes[100], above_sma200=votes[200],
                                     exec_price_open=px, contribution_usd=contrib, trade_usd=round(delta, 2), fee_usd=round(fee, 4),
                                     coin_after=round(a["coin"], 8), usd_after=round(a["usd"], 2), value_after=round(a["usd"] + a["coin"] * px, 2),
                                     processed_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime())))
            st["last_close"] = day
        st["latest_price"] = float(d.c.iloc[-1]); st["latest_price_utc"] = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    if new_rows:
        exists = os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if not exists: w.writeheader()
            w.writerows(new_rows)
    json.dump(state, open(STATE, "w"), indent=1)
    # report
    led = pd.read_csv(LEDGER) if os.path.exists(LEDGER) else pd.DataFrame(columns=FIELDS)
    lines = [f"# TREND_ENS daily bot - forward PAPER test (Binance prices, fake money) - {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC", "",
             "Rule: hold the coin share = share of SMA20/50/100/200 the daily close is above (data from 2025-01-01 only); trade the difference "
             "at the next daily open, 0.1% fee. Spot, no leverage. First decision: close of 2026-11-10.", "",
             "| Coin | Account | Days | Current share | Value now (USD) | Put in (USD) | Result | Buy & hold same money |", "|---|---|---|---|---|---|---|---|"]
    for sym in SYMS:
        st = state[sym]; px = st["latest_price"]; L = led[led.symbol == sym]
        for acc in ("LUMP", "DCA"):
            a = st[acc]; La = L[L.account == acc]; V = a["usd"] + a["coin"] * px
            put = LUMP0 if acc == "LUMP" else a.get("contributed", 0.0)
            if La.empty:
                lines.append(f"| {sym} | {acc} | 0 | - | {V:,.2f} | {put:,.2f} | waiting for first close ({FIRST_CLOSE}) | - |"); continue
            if acc == "LUMP": bh = LUMP0 * (1 - FEE) / La.exec_price_open.iloc[0] * px
            else: bh = float((DCA_DAY * (1 - FEE) / La.exec_price_open).sum() * px)
            lines.append(f"| {sym} | {acc} | {len(La)} | {La.signal_share.iloc[-1]:.0%} | {V:,.2f} | {put:,.2f} | {V / put - 1:+.2%} | {bh / put - 1:+.2%} |")
    lines += ["", f"Ledger rows: {len(led)}. No conclusion is drawn from a short forward sample."]
    open(REPORT, "w").write("\n".join(lines) + "\n")
    print(f"trend paper: {len(new_rows)} new ledger row(s)"); print("\n".join(lines[4:4 + 2 * len(SYMS) + 2]))


if __name__ == "__main__":
    main()
