"""STR-042 (PREREG.md): two-sided market maker simulated on Binance USDT-M aggTrades, 1-second steps, trade-through fills.
usage: python3 -I run_mm.py <scratch_dir>   (downloads each day's zip to scratch, processes, deletes it)"""
import io, json, math, os, ssl, sys, time, urllib.request, zipfile
import numpy as np, pandas as pd
from numba import njit
HERE = os.path.dirname(os.path.abspath(__file__)); CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
HS = [0.0002, 0.0005, 0.0010]; L = 5; NOTIONAL = 1000.0; TAKER = 0.0005; FEES = {"maker_0.02%": 0.0002, "maker_0.015%": 0.00015, "maker_0%": 0.0}
SPLIT = "2025-07-01"; TOUCH = os.environ.get("MM_TOUCH") == "1"   # post-hoc optimistic bound: fill when a trade touches the quote


def days():
    out = []
    for m in pd.period_range("2024-12", "2026-11", freq="M"):
        for d in (1, 15):
            day = f"{m.year}-{m.month:02d}-{d:02d}"
            if day <= "2026-11-15": out.append(day)
    return out


def load_day(sym, day, scratch):
    url = f"https://data.binance.vision/data/futures/um/daily/aggTrades/{sym}/{sym}-aggTrades-{day}.zip"
    for k in range(4):
        try: raw = urllib.request.urlopen(url, timeout=120, context=CTX).read(); break
        except Exception:
            if k == 3: return None
            time.sleep(2 ** (k + 1))
    z = zipfile.ZipFile(io.BytesIO(raw)); f = z.open(z.namelist()[0]); head = f.read(64); f.close(); f = z.open(z.namelist()[0])
    hdr = 0 if head[:1].isalpha() else None
    d = pd.read_csv(f, header=hdr, usecols=[1, 5], names=None if hdr == 0 else ["agg_trade_id", "price", "quantity", "first_trade_id", "last_trade_id", "transact_time", "is_buyer_maker"])
    d.columns = ["price", "t"]; s = (d.t.values // 1000).astype(np.int64); p = d.price.values.astype(float)
    g = pd.DataFrame(dict(s=s, p=p)).groupby("s").p; sec = g.last().index.values
    return sec, g.min().values, g.max().values, g.last().values


@njit(cache=True)
def simulate(sec, lo, hi, last, h, L, q, touch=False):
    """returns gross pnl (USD, before fees), maker turnover (USD), fills, inventory at end, last price."""
    inv = 0; cash = 0.0; turnover = 0.0; fills = 0
    for k in range(1, len(sec)):
        if sec[k] - sec[k - 1] > 5: continue                  # do not quote across data gaps
        ref = last[k - 1]; shift = -(inv / L) * h * ref; bid = ref * (1 - h) + shift; ask = ref * (1 + h) + shift
        if inv < L and (lo[k] < bid or (touch and lo[k] <= bid)): inv += 1; cash -= q * bid; turnover += q * bid; fills += 1
        if inv > -L and (hi[k] > ask or (touch and hi[k] >= ask)): inv -= 1; cash += q * ask; turnover += q * ask; fills += 1
    return cash + inv * q * last[-1], turnover, fills, inv, last[-1]


def main():
    scratch = sys.argv[1]; os.makedirs(scratch, exist_ok=True); R = []
    for sym in ("BTCUSDT", "ETHUSDT"):
        for day in days():
            x = load_day(sym, day, scratch)
            if x is None: print(sym, day, "missing", flush=True); continue
            sec, lo, hi, last = x; q = NOTIONAL / last[0]
            for h in HS:
                gross, turn, fills, inv, lp = simulate(sec, lo, hi, last, h, L, q, TOUCH); close_cost = abs(inv) * q * lp * TAKER
                row = dict(sym=sym, day=day, h_bp=h * 1e4, fills=int(fills), turnover_usd=round(turn, 2), gross_bp=round(gross / NOTIONAL * 1e4, 3))
                for name, fee in FEES.items(): row[name + "_bp"] = round((gross - fee * turn - close_cost) / NOTIONAL * 1e4, 3)
                R.append(row)
            print(sym, day, [(r["h_bp"], r["fills"], r["maker_0.02%_bp"], r["maker_0%_bp"]) for r in R[-3:]], flush=True)
    df = pd.DataFrame(R); df.to_csv(os.path.join(HERE, "daily_results_touch.csv" if TOUCH else "daily_results.csv"), index=False); summ = {}
    for (sym, h), g in df.groupby(["sym", "h_bp"]):
        key = f"STR-042|{sym}|h={h:g}bp"; summ[key] = {}
        for per, sel in (("VALIDATION", g.day < SPLIT), ("TEST", g.day >= SPLIT)):
            gg = g[sel]; d = dict(days=len(gg), mean_fills=round(float(gg.fills.mean()), 0), mean_gross_bp=round(float(gg.gross_bp.mean()), 2))
            for name in FEES:
                v = gg[name + "_bp"].values; d[name] = dict(mean_bp_per_day=round(float(v.mean()), 2), t=round(float(v.mean() / (v.std(ddof=1) / math.sqrt(len(v)))), 2) if len(v) > 2 else None,
                                                         positive_days_pct=round(float((v > 0).mean() * 100), 1))
            summ[key][per] = d
    ps = []; keys = list(summ)
    for k in keys:
        t = summ[k]["TEST"]["maker_0.02%"]["t"] or 0; ps.append(0.5 * math.erfc(t / math.sqrt(2)))
    o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / len(ps): sig = set(o[:r + 1])
    for i, k in enumerate(keys):
        v, te = summ[k]["VALIDATION"]["maker_0.02%"], summ[k]["TEST"]["maker_0.02%"]
        summ[k]["decision"] = "SCREEN-PASS (simulation only)" if (v["mean_bp_per_day"] > 0 and te["mean_bp_per_day"] > 0 and (te["t"] or 0) >= 2 and i in sig) else ("WATCH" if v["mean_bp_per_day"] > 0 and te["mean_bp_per_day"] > 0 else "REJECTED")
    json.dump(summ, open(os.path.join(HERE, "results_touch.json" if TOUCH else "results.json"), "w"), indent=1)
    for k, v in summ.items(): print(k, v["decision"], json.dumps({p: {f: v[p][f]["mean_bp_per_day"] for f in FEES} | {"fills": v[p]["mean_fills"], "gross": v[p]["mean_gross_bp"]} for p in ("VALIDATION", "TEST")}))


if __name__ == "__main__":
    main()
