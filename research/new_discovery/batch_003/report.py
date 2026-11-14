"""Apply PREREG.md decisions to results/batch_003.json; write RESULTS.md and append REGISTRY.csv rows (batch 003)."""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "src"))
import common as C  # noqa: E402

INFO = {"H1-R1": ("Round-number rejection fade (Osler)", "15m", "Osler (2003, JF); Osler (2000, FRBNY EPR)", "1h hold"),
        "H1-R2": ("Round-number crossing follow (Osler)", "15m", "Osler (2003, JF)", "1h hold"),
        "H2": ("London metal fix short (gold PM 15:00, silver 12:00)", "15m", "Caminschi & Heaney (2014, JFM); Abrantes-Metz & Metz (2014)", "30 min"),
        "H3": ("BTC CME weekend gap fill (popular theory)", "15m", "practitioner folklore; no peer-reviewed support known", "to fill/stop/Friday"),
        "H4": ("Coinbase premium z >= 2 -> follow 24 h", "1h signal / 15m execution", "practitioner flow signal (Coinbase vs Binance)", "24 h")}
P = ("EARLY", "TRAIN", "VALIDATION", "TEST")


def main():
    R = json.load(open(os.path.join(HERE, "results", "batch_003.json"))); keys = list(R)
    tp = [R[k]["TEST"].get("p_vs_benchmark") if R[k]["TEST"].get("p_vs_benchmark") is not None else 1.0 for k in keys]; rej = C.bh(tp)
    md = ["# Batch 003 results", "", "Pre-registered in `PREREG.md` (commit `f0fb5698`, before any code). TEST is reused evaluation data; EARLY (2019/2020–2022) had never been evaluated by this programme.", "",
          f"**{len(keys)} TEST tests, Benjamini–Hochberg at 5%: {len(rej)} significant.**", "",
          "| Test | Market | EARLY | TRAIN | VALID | TEST mean bp (n) | TEST stress | TEST p | BH | Decision |", "|---|---|---|---|---|---|---|---|---|---|"]
    reg = []
    for i, k in enumerate(keys):
        h, m = k.split("|"); r = R[k]; te = r["TEST"]
        avail = [p for p in P if r[p].get("trades", 0) > 0]; means = {p: r[p].get("mean_bp") for p in avail}
        pos_all = all(means[p] is not None and means[p] > 0 for p in avail) and "TEST" in avail
        sp = pos_all and (te.get("mean_stress_bp") or -1) > 0 and tp[i] <= 0.05 and i in rej and te.get("trades", 0) >= 30
        dec = "SCREEN-PASS" if sp else ("WATCH" if pos_all else "REJECT")
        f = lambda p: "—" if p not in avail else f"{means[p]:+.2f}"
        md.append(f"| {h} | {m} | {f('EARLY')} | {f('TRAIN')} | {f('VALIDATION')} | {f('TEST')} ({te.get('trades', 0)}) | {te.get('mean_stress_bp', float('nan')):+.2f} | {tp[i]:.3f} | {'yes' if i in rej else 'no'} | **{dec}** |")
        name, tf, src, hold = INFO[h]
        reg.append({"experiment_id": f"B003-{h}-{m}", "batch": "003", "name": name, "market": m, "timeframe": tf, "hypothesis_ref": "batch_003/PREREG.md", "source": src,
                    "rules": "see batch_003/PREREG.md", "parameters": "one pre-set setting", "periods": "EARLY to 2022 / TRAIN 2023-01..2024-06 / VALID 2024-07..2025-06 / TEST 2025-07..latest (reused)",
                    "variants_tested": 1, "data": "Exness 15m bid/ask (ticks.ex2archive.com); H4 also Coinbase + Binance 1h; not archived in the public repo",
                    "costs": "bid/ask + 0.5x median spread (stress 1.5x + 0.02%/day)", "train_mean_bp": "" if means.get("TRAIN") is None else round(means["TRAIN"], 4),
                    "valid_mean_bp": "" if means.get("VALIDATION") is None else round(means["VALIDATION"], 4), "test_mean_bp": round(means.get("TEST") or float("nan"), 4),
                    "test_stress_bp": round(te.get("mean_stress_bp", float("nan")), 4), "test_trades": te.get("trades", 0), "test_p": round(tp[i], 4), "bh_significant": i in rej,
                    "robustness": "not run (only for SCREEN-PASS)", "decision": dec,
                    "reason": ("passed on reused TEST data; needs forward" if sp else ("positive in every period incl. EARLY but not significant after BH" if pos_all else "not positive in every period"))})
    open(os.path.join(HERE, "RESULTS.md"), "w").write("\n".join(md) + "\n")
    path = os.path.join(ROOT, "REGISTRY.csv"); old = [x for x in csv.DictReader(open(path)) if x["batch"] != "003"]
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, list(old[0])); w.writeheader(); w.writerows(old + reg)
    print("\n".join(md))


if __name__ == "__main__":
    main()
