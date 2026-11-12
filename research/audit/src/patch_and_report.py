"""Audit fix 1+3 applied to the long-history and multi-market studies, with their ORIGINAL report scripts.
Copies both studies to a scratch tree, patches every raw result:
  - held-leg variants: z, p_z and random_mean_r from the calibrated sequential benchmark (reports/rescore/);
  - every variant: expectancy at primary and stress cost re-based from the fixed 0.02% / 0.05% slippage to
    spread-linked slippage (0.5x / 1.5x the market's median 2025-26 spread, from reports/costs.json). This is a
    per-market average adjustment in R; z is unaffected because the benchmark pays the same costs.
then runs the unchanged report.py of each study on the patched copy.
usage: python src/patch_and_report.py <scratch dir>"""
import glob
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.dirname(HERE)
RESEARCH = os.path.dirname(AUD)


def main():
    out = sys.argv[1]
    if os.path.exists(out):
        shutil.rmtree(out)
    for s in ("long_history", "multi_market"):
        shutil.copytree(os.path.join(RESEARCH, s), os.path.join(out, s), ignore=shutil.ignore_patterns("__pycache__"))
    costs = json.load(open(os.path.join(AUD, "reports", "costs.json")))
    resc = {}
    for f in glob.glob(os.path.join(AUD, "reports", "rescore", "*.json")):
        d = json.load(open(f))
        resc[(d["meta"]["study"], d["meta"]["market"])] = d["results"]
    stats = {"held_replaced": 0, "cost_adjusted": 0}

    def fix(r, mkt, new):
        c = costs.get(mkt)
        if c and "expectancy_r" in r and c["median_spread_R"] == c["median_spread_R"]:
            r["expectancy_r"] += c["slip_primary_R"] - 0.5 * c["median_spread_R"]
            if "expectancy_stress_r" in r:
                r["expectancy_stress_r"] += c["slip_stress_R"] - 1.5 * c["median_spread_R"]
            stats["cost_adjusted"] += 1
        if new and "z" in new and "z" in r:
            r["z"], r["p_z"], r["random_mean_r"] = new["z"], new["p_z"], new["random_mean_r"]
            r["benchmark"] = "sequential held (audit)"
            stats["held_replaced"] += 1

    for p in glob.glob(os.path.join(out, "long_history", "reports", "raw_*.json")):
        d = json.load(open(p))
        mkt = d["meta"]["market"]
        rs = resc.get(("long", mkt), {})
        for k, r in d["results"].items():
            fix(r, mkt, rs.get(k, {}).get("all"))
        json.dump(d, open(p, "w"))
    for p in glob.glob(os.path.join(out, "multi_market", "reports", "raw", "*.json")):
        d = json.load(open(p))
        mkt = os.path.basename(p)[:-5]
        rs = resc.get(("multi", mkt), {})
        for k, r in d["results"].items():
            for w in ("discovery", "confirmation"):
                fix(r[w], mkt, rs.get(k, {}).get(w))
        json.dump(d, open(p, "w"))
    print(stats)
    for s in ("long_history", "multi_market"):
        subprocess.run([sys.executable, os.path.join(out, s, "src", "report.py")], check=True, capture_output=True)
        os.makedirs(os.path.join(AUD, "reports", f"corrected_{s}"), exist_ok=True)
        for f in ("RESULTS.md", "summary.json", "results.json"):
            src = os.path.join(out, s, "reports", f)
            if os.path.exists(src) and f != "results.json":
                shutil.copy(src, os.path.join(AUD, "reports", f"corrected_{s}", f))
    print(open(os.path.join(AUD, "reports", "corrected_long_history", "RESULTS.md")).read()[:3500])
    print(open(os.path.join(AUD, "reports", "corrected_multi_market", "RESULTS.md")).read()[:2500])


if __name__ == "__main__":
    main()
