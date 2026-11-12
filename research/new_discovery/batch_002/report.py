"""Apply PREREG.md / PROTOCOL.md decisions to results/batch_002.json; write RESULTS.md, append REGISTRY.csv rows (batch 002)."""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))
import common as C  # noqa: E402

INFO = {
    "E005": ("Volatility-managed long exposure (EWMA 0.94, cap 2)", "1d", "Moreira & Muir (2017); Harvey et al. (2018); Cederburg et al. (2020)", "sharpe_diff"),
    "E006": ("HAR-RV vs EWMA next-day variance forecast (component)", "1d", "Corsi (2009); Andersen et al. (2003)", "loss_reduction"),
    "E007": ("Two-state Gaussian HMM regime filter (long if P(bull)>0.5)", "1d", "Hamilton (1989); Nystrup et al. (2017)", "sharpe_diff"),
    "E008": ("Crypto lead-lag: trade the laggard after a 2-sigma 15m move of the leader", "15m", "Sifat et al. (2019); Brandvold et al. (2015)", "mean_bp"),
    "E009": ("Pre-holiday effect, close to close", "1d", "Ariel (1990); Kim & Park (1994)", "mean_bp"),
}


def val(x, k):
    v = x.get(k)
    return v if isinstance(v, (int, float)) and not (isinstance(v, float) and math.isnan(v)) else None


def main():
    D = json.load(open(os.path.join(HERE, "results", "batch_002.json")))
    rows = []
    for e in ("E005", "E006", "E007", "E008", "E009"):
        for m, r in D[e].items():
            rows.append((e, m, r))

    def test_p(e, r):
        te = r.get("TEST", {})
        if e in ("E005", "E007") and (val(te, "sharpe_diff") is None or (te.get("mean_exposure") or 0) == 0):
            return 1.0                                            # no exposure: not testable
        return te.get("p_vs_benchmark", 1.0) if val(te, "p_vs_benchmark") is not None else 1.0
    tp = [test_p(e, r) for e, _, r in rows]
    rej = C.bh(tp)
    md = ["# Batch 002 results", "",
          "Pre-registered in `PREREG.md`, with amendment 1 disclosed there. TEST is **reused evaluation data**, so a pass is only a SCREEN-PASS, which still needs a forward period.",
          "", f"**{len(rows)} TEST-period tests, Benjamini–Hochberg at 5%: {len(rej)} significant** "
          f"({', '.join(rows[i][0] + ' ' + rows[i][1] for i in sorted(rej)) or 'none'}).", "",
          "Effect metric: E005/E007 Sharpe difference against the constant-exposure benchmark; E006 QLIKE loss reduction (positive means HAR is better); E008/E009 mean net bp per trade.", "",
          "| Exp | Market | TRAIN effect | VALID effect | TEST effect | TEST p | BH | Extra (TEST) | Decision |", "|---|---|---|---|---|---|---|---|---|"]
    reg = []
    for i, (e, m, r) in enumerate(rows):
        key = INFO[e][3]
        eff = [val(r.get(p, {}), key) for p in ("TRAIN", "VALIDATION", "TEST")]
        te = r.get("TEST", {})
        untestable = e in ("E005", "E007") and any(val(r.get(p, {}), key) is None for p in ("TRAIN", "VALIDATION", "TEST"))
        pos_all = all(x is not None and x > 0 for x in eff)
        stress_ok = (val(te, "mean_stress_bp") or 0) > 0 if e in ("E008", "E009") else ((val(te, "sharpe_strategy_stress") or -1) > (val(te, "sharpe_benchmark") or 0) if e in ("E005", "E007") else True)
        n_ok = (te.get("trades", 0) >= 30) if e in ("E008", "E009") else True
        sp = pos_all and stress_ok and tp[i] <= 0.05 and i in rej and n_ok
        dec = "SCREEN-PASS" if sp else ("WATCH" if pos_all else "REJECT")
        why = ("passed every rule on reused TEST data; needs forward data" if sp else
               ("positive in all periods but not significant after correction" + ("" if n_ok else "; too few TEST trades") if pos_all else
                ("no exposure in some period (HMM needs 250 days, or stayed flat)" if untestable else "not positive in every period")))
        extra = ""
        if e in ("E005", "E007"):
            extra = f"Sharpe {val(te, 'sharpe_strategy') or float('nan'):.2f} vs {val(te, 'sharpe_benchmark') or float('nan'):.2f}, exposure {te.get('mean_exposure', 0):.2f}, max DD {te.get('max_drawdown_pct', float('nan')):.1f}%"
        elif e == "E006":
            extra = f"QLIKE EWMA {te.get('qlike_ewma', float('nan')):.3f} vs HAR {te.get('qlike_har', float('nan')):.3f}, DM {te.get('dm_stat', float('nan')):+.2f}"
        else:
            extra = f"n {te.get('trades', 0)}, stress {val(te, 'mean_stress_bp') or float('nan'):+.1f} bp" + (f", ordinary-day mean {te.get('ordinary_day_mean_bp'):+.1f} bp" if "ordinary_day_mean_bp" in te else "")
        fmt = lambda x: "n/a" if x is None else f"{x:+.3f}"  # noqa: E731
        md.append(f"| {e} | {m} | {fmt(eff[0])} | {fmt(eff[1])} | {fmt(eff[2])} | {tp[i]:.3f} | {'yes' if i in rej else 'no'} | {extra} | **{dec}** |")
        name, tf, ref, _ = INFO[e]
        reg.append({"experiment_id": f"{e}-{m}", "batch": "002", "name": name, "market": m, "timeframe": tf, "hypothesis_ref": "batch_002/PREREG.md",
                    "source": ref, "rules": "see batch_002/PREREG.md", "parameters": "one pre-set setting (PREREG.md)",
                    "periods": "TRAIN 2023-01..2024-06 / VALID 2024-07..2025-06 / TEST 2025-07..latest (reused evaluation data)", "variants_tested": 1,
                    "data": "Exness 15m bid/ask (ticks.ex2archive.com), not archived", "costs": "bid/ask + 0.5x median spread (stress 1.5x + 0.02%/day)",
                    "train_mean_bp": "" if eff[0] is None else round(eff[0], 4), "valid_mean_bp": "" if eff[1] is None else round(eff[1], 4),
                    "test_mean_bp": "" if eff[2] is None else round(eff[2], 4), "test_stress_bp": round(val(te, "mean_stress_bp") or val(te, "sharpe_strategy_stress") or float("nan"), 4),
                    "test_trades": te.get("trades", te.get("days", 0)), "test_p": round(tp[i], 4), "bh_significant": i in rej,
                    "robustness": "not run (only for SCREEN-PASS)", "decision": dec, "reason": why})
    open(os.path.join(HERE, "RESULTS.md"), "w").write("\n".join(md) + "\n")
    path = os.path.join(ROOT, "REGISTRY.csv")
    old = [x for x in csv.DictReader(open(path)) if x["batch"] != "002"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, list(old[0]))
        w.writeheader()
        w.writerows(old + reg)
    print("\n".join(md))


if __name__ == "__main__":
    main()
