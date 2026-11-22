"""Independent re-check of a random sample of D2 trades with a plain tick-by-tick loop (no shared simulation code)."""
import csv, math, os, sys, numpy as np, calendar, time
CACHE = os.environ["CACHE_DIR"]
M = ["2025_11","2025_12","2026_01","2026_02","2026_03","2026_04","2026_05","2026_06","2026_07","2026_08","2026_09","2026_10"]
d = [np.load(f"{CACHE}/{m}.npz") for m in M]
t = np.concatenate([x["t"] for x in d]); bid = np.concatenate([x["bid"] for x in d]); ask = np.concatenate([x["ask"] for x in d])
rows = list(csv.DictReader(open("results/D2_trades.csv")))
rng = np.random.default_rng(7); pick = rng.choice(len(rows), 30, replace=False)
bad = 0
for k in pick:
    r = rows[k]; C = calendar.timegm(time.strptime(r["candle_close"], "%Y-%m-%d %H:%M:%S")) * 1000
    i = int(np.searchsorted(t, C)); buy = r["side"] == "BUY"
    E = ask[i] if buy else bid[i]; s = 1 if buy else -1
    tps = [E + 5 * s, E + 10 * s, (math.ceil((E + 30) / 10) * 10) if buy else (math.floor((E - 30) / 10) * 10)]
    stop = E - 10 * s; hit = 0; pnl = 0.0; j = i + 1; end = t[i] + 7 * 86400000
    while j < len(t) and t[j] < end:
        px = bid[j] if buy else ask[j]
        if (px - stop) * s <= 0: pnl += (3 - hit) * (px - E) * s; break
        while hit < 3 and (px - tps[hit]) * s >= 0: pnl += abs(tps[hit] - E); hit += 1
        if hit: stop = E
        if hit == 3: break
        j += 1
    R = pnl / 30
    ok = abs(R - float(r["R_M1_net"])) < 1e-3
    bad += not ok
    print(r["candle_close"], r["side"], round(R, 4), r["R_M1_net"], "OK" if ok else "MISMATCH")
print("mismatches", bad, "of", len(pick))
