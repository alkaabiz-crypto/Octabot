"""Forward PAPER test: gold long 22:05 -> 07:00 UTC, Sunday-Thursday entries. Rules frozen in FORWARD_RULES.md.
Hyperliquid xyz:GOLD 1m prices. Fake money, no orders.

Usage: python3 -I forward.py   (run hourly; processes each new closed 1m candle exactly once)
"""
import csv, datetime as dt, json, os, ssl, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
COIN = "xyz:GOLD"; START_EQ = 2722.94; COST = 0.20; M1 = 60_000
FIRST_ENTRY_MS = int(dt.datetime(2026, 11, 12, 22, 5, tzinfo=dt.timezone.utc).timestamp() * 1000)
ENTRY_DAYS = {6, 0, 1, 2, 3}  # Sunday..Thursday (Python weekday: Monday=0)
MAX_GAP = 90 * M1
STATE, LEDGER, REPORT = (os.path.join(HERE, f) for f in ("state.json", "ledger.csv", "REPORT.md"))
CA = "/root/.ccr/ca-bundle.crt"; CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
FIELDS = ["entry_utc", "entry_open", "exit_utc", "exit_open", "gross_usd_per_oz", "net_usd_per_oz_1x", "net_usd_per_oz_2x", "net_bp_2x",
          "oz_1x", "equity_1x_after", "equity_2x_after", "processed_utc"]
fmt = lambda ms: time.strftime("%Y-%m-%d %H:%M", time.gmtime(ms / 1000))


def stop(msg):
    print("STOPPED:", msg); raise SystemExit(1)


def next_entry(after_ms):
    d = dt.datetime.fromtimestamp(after_ms / 1000, dt.timezone.utc).replace(hour=22, minute=5, second=0, microsecond=0)
    while d.timestamp() * 1000 < after_ms or d.weekday() not in ENTRY_DAYS:
        d += dt.timedelta(days=1)
    return int(d.timestamp() * 1000)


def exit_for(entry_target_ms):
    d = dt.datetime.fromtimestamp(entry_target_ms / 1000, dt.timezone.utc).replace(hour=7, minute=0) + dt.timedelta(days=1)
    return int(d.timestamp() * 1000)


def candles(start_ms):
    body = json.dumps({"type": "candleSnapshot", "req": {"coin": COIN, "interval": "1m", "startTime": int(start_ms), "endTime": int(time.time() * 1000)}}).encode()
    r = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.hyperliquid.xyz/info", data=body, headers={"Content-Type": "application/json"}),
                                          timeout=30, context=CTX).read())
    now = time.time() * 1000
    return [(int(x["t"]), float(x["o"]), float(x["c"])) for x in r if x["T"] < now]


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else dict(
        cursor=int(time.time() * 1000) // M1 * M1, next_entry=next_entry(FIRST_ENTRY_MS), pos=None, trades=0, wins_2x=0,
        eq1=START_EQ, eq2=START_EQ, oz_cum_1x=0.0, oz_cum_2x=0.0, bp_sum_2x=0.0, first_entry_px=None, started=fmt(time.time() * 1000))
    cs = candles(st["cursor"] - 5 * M1)
    if not cs or cs[0][0] > st["cursor"]:
        stop(f"feed does not reach back to the last processed candle {fmt(st['cursor'])} (first returned: {fmt(cs[0][0]) if cs else 'none'})")
    cs = [c for c in cs if c[0] > st["cursor"]]
    rows = []; prev = st["cursor"]
    for t, o, c in cs:
        p = st["pos"]
        if t - prev > MAX_GAP and p:
            stop(f"1m feed gap {fmt(prev)} -> {fmt(t)} while a position is open")
        if p and t >= p["exit_target"]:
            g = o - p["entry"]; n1, n2 = g - COST, g - 2 * COST
            oz1, oz2 = st["eq1"] / p["entry"], st["eq2"] / p["entry"]
            st["eq1"] = round(st["eq1"] + oz1 * n1, 4); st["eq2"] = round(st["eq2"] + oz2 * n2, 4)
            bp2 = n2 / p["entry"] * 1e4
            st["trades"] += 1; st["wins_2x"] += n2 > 0; st["oz_cum_1x"] = round(st["oz_cum_1x"] + n1, 4); st["oz_cum_2x"] = round(st["oz_cum_2x"] + n2, 4)
            st["bp_sum_2x"] = round(st["bp_sum_2x"] + bp2, 4)
            rows.append(dict(entry_utc=fmt(p["entry_t"]), entry_open=p["entry"], exit_utc=fmt(t), exit_open=o, gross_usd_per_oz=round(g, 3),
                             net_usd_per_oz_1x=round(n1, 3), net_usd_per_oz_2x=round(n2, 3), net_bp_2x=round(bp2, 3), oz_1x=round(oz1, 6),
                             equity_1x_after=round(st["eq1"], 2), equity_2x_after=round(st["eq2"], 2), processed_utc=fmt(time.time() * 1000)))
            st["pos"] = None; p = None
        if p is None and t >= st["next_entry"]:
            if t - st["next_entry"] > MAX_GAP:
                stop(f"no 1m candle within 90 min of the {fmt(st['next_entry'])} entry time (first: {fmt(t)})")
            st["pos"] = dict(entry=o, entry_t=t, exit_target=exit_for(st["next_entry"]))
            if st["first_entry_px"] is None: st["first_entry_px"] = o
            st["next_entry"] = next_entry(st["pos"]["exit_target"])
        st["cursor"] = prev = t
    if rows:
        new = not os.path.exists(LEDGER)
        with open(LEDGER, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new: w.writeheader()
            w.writerows(rows)
    json.dump(st, open(STATE, "w"), indent=1)
    last = cs[-1][2] if cs else None; p = st["pos"]; n = st["trades"]
    flo = f", floating {(last - p['entry']):+.2f} USD per oz" if (p and last) else ""
    bh = f"{(last / st['first_entry_px'] - 1) * 100:+.2f}%" if (last and st["first_entry_px"]) else "n/a (no entry yet)"
    lines = [f"# Gold Asian-session long - forward PAPER test ({fmt(time.time() * 1000)} UTC)", "",
             "Hyperliquid xyz:GOLD 1m (not Exness). Long 22:05 -> 07:00 UTC, entries Sunday-Thursday, whole paper account, no leverage. "
             "Cost 0.20 USD/oz per round trip (2x = 0.40). Fake money.", "",
             f"- Started {st['started']} UTC | first entry {fmt(FIRST_ENTRY_MS)} UTC | closed trades: {n} / 100 for evaluation",
             f"- Account: {st['eq1']:,.2f} USD at 1x cost ({(st['eq1'] / START_EQ - 1) * 100:+.2f}%), {st['eq2']:,.2f} USD at 2x cost ({(st['eq2'] / START_EQ - 1) * 100:+.2f}%)",
             f"- Fixed 1 oz (0.01 lot): {st['oz_cum_1x']:+.2f} USD at 1x, {st['oz_cum_2x']:+.2f} USD at 2x | win rate at 2x: "
             f"{(st['wins_2x'] / n * 100 if n else 0):.0f}% | average per trade at 2x: {(st['bp_sum_2x'] / n if n else 0):+.2f} bp",
             f"- Open position: {'BUY at ' + str(p['entry']) + ' since ' + fmt(p['entry_t']) + ', exit at ' + fmt(p['exit_target']) + flo if p else 'none'} | next entry: {fmt(st['next_entry'])} UTC",
             f"- Gold buy-and-hold from the first entry: {bh}",
             "- No conclusion before 100 closed trades."]
    open(REPORT, "w").write("\n".join(lines) + "\n")
    print(f"gold asia paper: {len(rows)} trade(s) closed this run"); print("\n".join(lines[4:9]))


if __name__ == "__main__":
    main()
