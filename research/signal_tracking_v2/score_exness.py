"""Score every logged SignalPro signal on Exness 1-minute prices (the user's broker feed). One step per batch.

- Downloads the Exness public tick zips (ticks.ex2archive.com) for each needed instrument and month into a scratch dir
  (EXNESS_TMP, default a temp dir); zips are deleted after use, their SHA-256 recorded.
- Builds 1-minute mid bars with the same function as the frozen orb_study/build_bars.py bars() (copied below verbatim).
- Scores with the frozen SignalPro tracker's own score() (tracker_frozen.py = frozen tracker.py, SHA-256 checked).
- Writes exness_outcomes.csv (all signals, recomputed) and EXNESS_REPORT.md. Signals are never edited.
usage: python3 -I score_exness.py
"""
import calendar, csv, hashlib, os, ssl, sys, tempfile, time, urllib.request
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
TRACKER_SHA = "75a7aed5dc4ca57bd5777d4e8febf0dc74a2ae4f1570468c0f9995bb53ef4781"
assert hashlib.sha256(open(os.path.join(HERE, "tracker_frozen.py"), "rb").read()).hexdigest() == TRACKER_SHA, "tracker_frozen.py changed"
import tracker_frozen as TR  # noqa: E402
SYM = {"XAUUSD": "XAUUSDm", "XAUUSD247": "XAUUSDm", "USOIL": "USOILm", "XAGUSD": "XAGUSDm", "BTCUSD": "BTCUSDm"}
CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt") if os.path.exists("/root/.ccr/ca-bundle.crt") else ssl.create_default_context()
TMP = os.environ.get("EXNESS_TMP") or tempfile.mkdtemp()


def bars(t, b, a):   # verbatim logic of the frozen orb_study/build_bars.py bars() (without its 2025 start assertion)
    o = np.argsort(t, kind="stable"); t, b, a = t[o], b[o], a[o]
    mid = (b + a) / 2; sp = a - b; k = t // 60_000
    st = np.flatnonzero(np.r_[True, k[1:] != k[:-1]]); en = np.r_[st[1:], len(t)]
    med = np.array([np.median(sp[s:e]) for s, e in zip(st, en)])
    return dict(m=k[st], o=mid[st], h=np.maximum.reduceat(mid, st), l=np.minimum.reduceat(mid, st), c=mid[en - 1], sp=med)


def month_bars(sym, y, m, log):
    zp = os.path.join(TMP, f"{sym}_{y}_{m:02d}.zip")
    with urllib.request.urlopen(f"https://ticks.ex2archive.com/ticks/{sym}/{y}/{m:02d}/Exness_{sym}_{y}_{m:02d}.zip", timeout=300, context=CTX) as r, open(zp, "wb") as f:
        while (ch := r.read(1 << 20)): f.write(ch)
    sha = hashlib.sha256(open(zp, "rb").read()).hexdigest()
    df = pd.read_csv(zp, compression="zip", usecols=[1, 2, 3, 4], header=0, names=["sym", "ts", "bid", "ask"]); os.remove(zp)
    t = pd.to_datetime(df.ts, format="%Y-%m-%d %H:%M:%S.%fZ", utc=True).dt.as_unit("ms").astype("int64").to_numpy()
    log.append(f"{sym} {y}-{m:02d}: {len(df)} ticks to {df.ts.iloc[-1]}, zip SHA-256 {sha}")
    return bars(t, df.bid.to_numpy(float), df.ask.to_numpy(float))


def main():
    sig = list(csv.DictReader(open(os.path.join(HERE, "signals.csv")))); need = {}
    for s in sig:
        sym = SYM.get(s["instrument"])
        if not sym: continue
        t0 = TR.utc(s["posted_window_start_utc"]); t1 = min(time.time(), t0 + 8 * 86400)
        for t in (t0, t1):
            g = time.gmtime(t); need.setdefault(sym, set()).add((g.tm_year, g.tm_mon))
    log, series = [], {}
    for sym, months in need.items():
        parts = [month_bars(sym, y, m, log) for y, m in sorted(months)]
        mm = np.concatenate([p["m"] for p in parts]); order = np.argsort(mm, kind="stable")
        cols = {k: np.concatenate([p[k] for p in parts])[order] for k in ("m", "o", "h", "l", "c")}
        series[sym] = [(int(a) * 60, float(b), float(c), float(d), float(e)) for a, b, c, d, e in zip(cols["m"], cols["o"], cols["h"], cols["l"], cols["c"])]
    rows = []
    for s in sig:
        sym = SYM.get(s["instrument"])
        if not sym: rows.append(dict(signal_id=s["signal_id"], status="NO_EXNESS_MAPPING")); continue
        for bound, name in (("posted_window_start_utc", "early"), ("posted_window_end_utc", "late")):
            if s["entry"] == s["stop_loss"]: rows.append(dict(signal_id=s["signal_id"], capture=s["capture_type"].split(" ")[0], method=f"-@{name}", status="ORIGINAL_STOP_UNKNOWN")); continue
            for r in TR.score((series[sym], series[sym]), s, name, TR.utc(s[bound])):
                r["capture"] = s["capture_type"].split(" ")[0]; rows.append(r)
    keys = ["signal_id", "capture", "method", "status", "tp_hits", "exit_utc", "R_tp3_full", "R_thirds", "R_thirds_BE", "status_BE", "gap", "entry", "stop", "tps"]
    with open(os.path.join(HERE, "exness_outcomes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    def mean_r(cap):
        x = [float(r["R_thirds_BE"]) for r in rows if r.get("capture") == cap and str(r.get("method", "")).startswith("B_absolute@late") and r.get("R_thirds_BE") not in ("", None)]
        return (len(x), round(sum(x) / len(x), 3) if x else None)
    lines = [f"# SignalPro signals scored on Exness prices ({time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC)", "",
             "Frozen tracker rules (SHA-256 `75a7aed5…`) on Exness 1-minute mid bars. B = the app's levels; the late window end is the main reading. Paper evaluation only.", "",
             f"- PROSPECTIVE signals resolved (B@late, R with the app's breakeven management): n {mean_r('PROSPECTIVE')[0]}, mean {mean_r('PROSPECTIVE')[1]}R. **Verdict needs ≥ 50.**",
             f"- RETROSPECTIVE signals resolved (selection-biased, reported separately): n {mean_r('RETROSPECTIVE')[0]}, mean {mean_r('RETROSPECTIVE')[1]}R", "",
             "Per signal and method: `exness_outcomes.csv`.", "", "Data:"] + [f"- {x}" for x in log]
    open(os.path.join(HERE, "EXNESS_REPORT.md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    main()
