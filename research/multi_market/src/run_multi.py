"""Discovery (2023-07 to 2024-12) and confirmation (2025-01 to now) results for every variant on every market whose
data exists (PROTOCOL.md). usage: MULTI_DATA=dir LONG_DATA=dir python run_multi.py [workers]
Writes reports/raw/<market>.json; skips markets already done. src/report.py applies the fit-and-confirm rules."""
import json
import multiprocessing
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "long_history", "src"))
import run_long as L  # noqa: E402  (sets up every research path)
import builtin_strategies as B  # noqa: E402
import builtin_indicators as I  # noqa: E402
import run_everything as R  # noqa: E402
import study as S  # noqa: E402

CLASSES = {
    "forex": ["EURUSDm", "GBPUSDm", "USDJPYm", "AUDUSDm", "USDCADm", "USDCHFm", "NZDUSDm", "EURJPYm", "GBPJPYm", "EURGBPm"],
    "indices": ["US500m", "USTECm", "US30m", "DE30m", "UK100m", "JP225m", "FR40m", "AUS200m", "HK50m", "STOXX50m"],
    "crypto": ["BTCUSDm", "ETHUSDm", "XRPUSDm", "LTCUSDm", "SOLUSDm", "BCHUSDm", "ADAUSDm", "BNBUSDm"],
    "commodities": ["USOILm", "UKOILm", "XNGUSDm", "XAUUSDm", "XAGUSDm"],
}
MARKET_CLASS = {m: c for c, ms in CLASSES.items() for m in ms}
FROM_LONG = {"USOILm", "XAUUSDm", "BTCUSDm"}
WINDOWS = {"discovery": ((2023, 7), (2025, 1)), "confirmation": ((2025, 1), None)}
RAW = os.path.join(ROOT, "reports", "raw")


def path_of(mkt):
    d = os.environ["LONG_DATA"] if mkt in FROM_LONG else os.environ["MULTI_DATA"]
    return os.path.join(d, f"{mkt}_15m.csv.gz")


def run(mkt):
    t0 = time.time()
    a = B.BuiltinAsset(path_of(mkt), crypto=MARKET_CLASS[mkt] == "crypto")
    end = a.e.t[-1] + 3600
    wins = {k: (S.ts(*v0, 1), S.ts(*v1, 1) if v1 else end) for k, (v0, v1) in WINDOWS.items()}
    sig_ind, flt = I.signals(a.e), R.filters(a)
    strat, out = {}, {}
    for (part, name, d, ex) in L.variants(a, sig_ind):
        for fname in (None,) + R.FILTERS:
            ok = flt[fname][0 if d > 0 else 1] if fname else None
            key = f"{part}|{name}{'+' + fname if fname else ''}|{'BUY' if d > 0 else 'SELL'}|{ex}"
            res = {}
            for wname, (w0, w1) in wins.items():
                if part in ("A", "C"):
                    if name not in strat:
                        strat[name] = a.simulate_strategy(name)
                    trades = [t for t in strat[name] if t.direction == d and w0 <= t.entry_time < w1 and (ok is None or ok[t.signal_index])]
                    kind = "held"
                else:
                    buy, sell = (sig_ind if part == "B" else a.sig)[name]
                    mine, other = (buy, sell) if d > 0 else (sell, buy)
                    if ok is not None:
                        mine = [m and f for m, f in zip(mine, ok)]
                    if ex == "FLIP":
                        trades, kind = R.flip_legs(a, mine, other, d, w0, w1), "held"
                    elif ex == "NATIVE":
                        trades, kind = a.run_signals(mine, d, "NATIVE", w0, w1), "held"
                    else:
                        trades, kind = a.run_signals(mine, d, ex, w0, w1), "standard"
                res[wname] = L.summarise(a, trades, kind, d, ex, w0, w1, (w0 + w1) // 2)
            out[key] = res
    meta = {"market": mkt, "class": MARKET_CLASS[mkt], "first_bar": S.fmt(a.e.t[0]), "last_bar": S.fmt(a.e.t[-1]),
            "bars_1h": len(a.e.t), "seconds": round(time.time() - t0)}
    tmp = os.path.join(RAW, f"{mkt}.json.tmp")
    json.dump({"meta": meta, "results": out}, open(tmp, "w"))
    os.replace(tmp, os.path.join(RAW, f"{mkt}.json"))
    return mkt, meta["seconds"]


def main():
    os.makedirs(RAW, exist_ok=True)
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    todo = [m for m in MARKET_CLASS if os.path.exists(path_of(m)) and not os.path.exists(os.path.join(RAW, f"{m}.json"))]
    if not todo:
        return
    with multiprocessing.Pool(workers) as pool:
        for m, sec in pool.imap_unordered(run, todo):
            print("finished", m, sec, "s", flush=True)


if __name__ == "__main__":
    main()
