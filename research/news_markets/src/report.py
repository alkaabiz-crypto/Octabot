"""Apply PROTOCOL.md's decision rule to reports/raw/*.json; write reports/RESULTS.md and reports/summary.json."""
import glob
import importlib.util
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_spec = importlib.util.spec_from_file_location("lr", os.path.join(os.path.dirname(ROOT), "long_history", "src", "report.py"))
_lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_lr)
NAMES = {"FOLLOW15": "follow first 15 min", "FADE15": "fade first 15 min", "FOLLOW30": "follow first 30 min",
         "BREAKOUT": "break of release candle", "PRE24": "buy 24 h before"}


def p_of(z):
    return 0.5 * math.erfc(z / math.sqrt(2))


def passes_fit(f):
    return f.get("events", 0) >= 15 and f.get("z", 0) >= 1.645 and f.get("expectancy_stress_r", -1) > 0


def cell(x):
    if "z" not in x:
        return f"{x.get('events', 0)} events"
    return f"{x['events']}, win {x['win_rate_pct']:.0f}%, {x['expectancy_r']:+.3f}R, z {x['z']:+.2f}"


def main():
    data = {os.path.basename(f)[:-5]: json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, "reports", "raw", "*.json")))}
    rows = [(m, k, r) for m, d in data.items() for k, r in d["results"].items()]
    passed = [(m, k, r) for m, k, r in rows if passes_fit(r["fit"]) and "z" in r["test"]]
    rej = _lr.benjamini_hochberg([p_of(r["test"]["z"]) for _, _, r in passed]) if passed else set()
    confirmed = [passed[i] for i in sorted(rej) if passed[i][2]["test"].get("expectancy_stress_r", -1) > 0]
    n_test = sum("z" in r["test"] for _, _, r in rows)
    raw05 = sum(p_of(r["test"]["z"]) <= 0.05 for _, _, r in rows if "z" in r["test"])
    L = ["# Results: trading scheduled news across markets", "",
         f"{len(data)} markets, {len(rows)} market × event × strategy combinations. Strategies are judged against the "
         "same rule on normal days at the same clock time. Cells: events, win rate, expectancy, z.", "",
         "## Headline", "",
         f"- Passed in the fit period: **{len(passed)}** (about {0.05 * len(rows):.0f} expected by luck).",
         f"- Confirmed in 2025-01 to now after the multiple-testing correction: **{len(confirmed)}**.",
         f"- Raw p ≤ 0.05 in the test period, before correction: {raw05} of {n_test} (about {0.05 * n_test:.0f} expected by luck).", ""]
    if confirmed:
        L += ["Confirmed:", ""] + [f"- {m} {k.split('|')[0]} {NAMES[k.split('|')[1]]}: test {cell(r['test'])}" for m, k, r in confirmed] + [""]
    L += ["## Combinations that passed the fit period", "", "| Market | Event | Strategy | Fit | Test | Test p |", "|---|---|---|---|---|---|"]
    for m, k, r in sorted(passed, key=lambda x: -x[2]["fit"]["z"]):
        e, s = k.split("|")
        L.append(f"| {m} | {e} | {NAMES[s]} | {cell(r['fit'])} | {cell(r['test'])} | {p_of(r['test']['z']):.3f} |")
    L += ["", "## How much more each market moves after news (4 hours after the release, in ATR)", "",
          "| Market | FOMC | CPI | NFP | EIA |", "|---|---|---|---|---|"]
    for m, d in data.items():
        cells = []
        for kind in ("FOMC", "CPI", "NFP", "EIA"):
            mv = d["moves"].get(kind)
            if not mv or not mv.get("event_median_4h_move_atr") or not mv.get("control_median_4h_move_atr"):
                cells.append("-")
            else:
                cells.append(f"{mv['event_median_4h_move_atr']:.1f} vs {mv['control_median_4h_move_atr']:.1f} "
                             f"(×{mv['event_median_4h_move_atr'] / mv['control_median_4h_move_atr']:.1f})")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L += ["", "## Every combination", "", "| Market | Event | Strategy | Fit | Test |", "|---|---|---|---|---|"]
    for m, k, r in rows:
        e, s = k.split("|")
        L.append(f"| {m} | {e} | {NAMES[s]} | {cell(r['fit'])} | {cell(r['test'])} |")
    meta = {m: d["meta"] for m, d in data.items()}
    open(os.path.join(ROOT, "reports", "RESULTS.md"), "w").write("\n".join(L) + "\n")
    json.dump({"passed_fit": [[m, k] for m, k, _ in passed], "confirmed": [[m, k] for m, k, _ in confirmed], "meta": meta},
              open(os.path.join(ROOT, "reports", "summary.json"), "w"), indent=1)
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
