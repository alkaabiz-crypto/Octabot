"""Apply PROTOCOL.md's fit-and-confirm rules to reports/raw/*.json; write reports/RESULTS.md and reports/summary.json."""
import glob
import importlib.util
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("long_report", os.path.join(os.path.dirname(ROOT), "long_history", "src", "report.py"))
_lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lr)
benjamini_hochberg = _lr.benjamini_hochberg

CLASS_ORDER = ("forex", "indices", "crypto", "commodities")
SEEN_BEFORE = {"USOILm", "XAUUSDm", "BTCUSDm"}


def p_of(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def eligible_disc(r):
    d = r["discovery"]
    return d["trades"] >= 100 and d.get("expectancy_r", -1) > 0 and d.get("expectancy_stress_r", -1) > 0 and "z" in d


def describe(key):
    part, name, side, ex = key.split("|")
    exits = {"HW": "target ½ stop", "SYM": "±1R", "TRAIL": "trailing stop", "FLIP": "hold to opposite signal",
             "NATIVE": "4-bar hold", "OWN": "strategy's own exits"}
    nm = name.replace("+F_4H_EMA200", " + 4H EMA200 filter").replace("+F_DAILY_EMA200", " + daily EMA200 filter")
    nm = nm.replace("+F_ADX14_GT20", " + ADX>20 filter").replace("+F_SESSION_VWAP", " + session VWAP filter")
    return f"{nm} {side}, {exits[ex]}"


def main():
    data = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "reports", "raw", "*.json"))):
        d = json.load(open(p))
        data[d["meta"]["market"]] = d
    mclass = {m: d["meta"]["class"] for m, d in data.items()}
    # 1. per-market picks
    picks = []
    for m, d in data.items():
        cand = sorted(((k, r) for k, r in d["results"].items() if eligible_disc(r)), key=lambda kv: -kv[1]["discovery"]["z"])[:5]
        picks += [(m, k, r) for k, r in cand]
    pv = [r["confirmation"].get("p_z", 1.0) for _, _, r in picks]
    rej = benjamini_hochberg(pv)
    market_rows, confirmed_m = [], []
    for idx, (m, k, r) in enumerate(picks):
        c = r["confirmation"]
        ok = idx in rej and c["trades"] >= 50 and c.get("expectancy_r", -1) > 0 and c.get("expectancy_stress_r", -1) > 0
        market_rows.append((m, k, r, ok))
        if ok:
            confirmed_m.append((m, k))
    # 2. per-class picks (Stouffer)
    class_picks = []
    for cl in CLASS_ORDER:
        ms = [m for m in data if mclass[m] == cl]
        if not ms:
            continue
        keys = set.intersection(*(set(data[m]["results"]) for m in ms))
        scored = []
        for k in keys:
            zs = [data[m]["results"][k]["discovery"]["z"] for m in ms if data[m]["results"][k]["discovery"].get("z") is not None
                  and data[m]["results"][k]["discovery"]["trades"] >= 30]
            if len(zs) >= max(2, len(ms) // 2):
                scored.append((sum(zs) / math.sqrt(len(zs)), k))
        for zd, k in sorted(scored, reverse=True)[:5]:
            cz = [(m, data[m]["results"][k]["confirmation"]) for m in ms]
            cz = [(m, c) for m, c in cz if c.get("z") is not None and c["trades"] >= 30]
            zc = sum(c["z"] for _, c in cz) / math.sqrt(len(cz)) if cz else 0.0
            pos = sum(c["expectancy_r"] > 0 for _, c in cz)
            class_picks.append({"class": cl, "key": k, "z_discovery": zd, "z_confirmation": zc, "p": p_of(zc),
                                "markets_positive": pos, "markets": len(cz),
                                "mean_e_conf": statistics.mean(c["expectancy_r"] for _, c in cz) if cz else 0.0})
    rej_c = benjamini_hochberg([c["p"] for c in class_picks])
    for i, c in enumerate(class_picks):
        c["confirmed"] = i in rej_c and c["markets_positive"] > c["markets"] / 2
    # 3. whole-sample check (combined z of the two periods)
    allk = [(m, k, r) for m, d in data.items() for k, r in d["results"].items()
            if r["discovery"].get("z") is not None and r["confirmation"].get("z") is not None]
    zall = [(r["discovery"]["z"] + r["confirmation"]["z"]) / math.sqrt(2) for _, _, r in allk]
    rej_all = benjamini_hochberg([p_of(z) for z in zall])
    raw05 = sum(p_of(z) <= 0.05 for z in zall)
    # write
    L = ["# Results: which indicators fit which markets", "",
         f"{len(data)} markets, {sum(len(d['results']) for d in data.values())} market-variant pairs. "
         "Discovery 2023-07 to 2024-12; confirmation 2025-01 to the latest candle. Primary cost unless noted.", "",
         "## Headline", "",
         f"- Per-market picks confirmed: **{len(confirmed_m)} of {len(picks)}** "
         f"(raw p ≤ 0.05 in confirmation: {sum(p <= 0.05 for p in pv)}, about {0.05 * len(pv):.0f} expected by luck).",
         f"- Per-class picks confirmed: **{sum(c['confirmed'] for c in class_picks)} of {len(class_picks)}**.",
         f"- Whole-sample check: {len(rej_all)} of {len(allk)} pairs significant after BH "
         f"(raw p ≤ 0.05: {raw05}, about {0.05 * len(allk):.0f} expected by luck).", "",
         "## Per-class picks (fitted on discovery, tested on 2025 to now)", "",
         "| Class | Variant | Discovery z | Confirmation z | p | Markets positive in confirmation | Mean E in confirmation | Confirmed |",
         "|---|---|---|---|---|---|---|---|"]
    for c in class_picks:
        L.append(f"| {c['class']} | {describe(c['key'])} | {c['z_discovery']:+.2f} | {c['z_confirmation']:+.2f} | {c['p']:.3f} | "
                 f"{c['markets_positive']}/{c['markets']} | {c['mean_e_conf']:+.3f}R | {'**yes**' if c['confirmed'] else 'no'} |")
    L += ["", "## Per-market picks", "",
          "| Class | Market | Variant | Discovery: trades, win, E, z | Confirmation: trades, win, E, E stress, z, p | Confirmed |",
          "|---|---|---|---|---|---|"]
    for cl in CLASS_ORDER:
        for m, k, r, ok in market_rows:
            if mclass[m] != cl:
                continue
            d, c = r["discovery"], r["confirmation"]
            ctext = (f"{c['trades']}, {c.get('win_rate_pct', 0):.0f}%, {c.get('expectancy_r', 0):+.3f}R, "
                     f"{c.get('expectancy_stress_r', 0):+.3f}R, {c.get('z', 0):+.2f}, {c.get('p_z', 1):.3f}")
            flag = " (seen in earlier rounds)" if m in SEEN_BEFORE else ""
            L.append(f"| {cl} | {m}{flag} | {describe(k)} | {d['trades']}, {d['win_rate_pct']:.0f}%, {d['expectancy_r']:+.3f}R, "
                     f"{d['z']:+.2f} | {ctext} | {'**yes**' if ok else 'no'} |")
    L += ["", "## Markets", "", "| Market | Class | Data from | Data to |", "|---|---|---|---|"]
    for m, d in sorted(data.items(), key=lambda kv: (CLASS_ORDER.index(kv[1]["meta"]["class"]), kv[0])):
        L.append(f"| {m} | {d['meta']['class']} | {d['meta']['first_bar']} | {d['meta']['last_bar']} |")
    open(os.path.join(ROOT, "reports", "RESULTS.md"), "w").write("\n".join(L) + "\n")
    json.dump({"confirmed_market_picks": confirmed_m, "class_picks": class_picks,
               "whole_sample_significant": [(allk[i][0], allk[i][1]) for i in sorted(rej_all)]},
              open(os.path.join(ROOT, "reports", "summary.json"), "w"), indent=1)
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
