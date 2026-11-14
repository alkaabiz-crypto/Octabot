"""G7 monthly honesty check: count every statistical test / configuration evaluated so far, across both branches, and write
research/ops/TEST_COUNT.md. Dynamic counts are read from result files in this branch; the other session's and earlier studies'
counts are documented constants (from their own result files, read 2026-11-13/14). Read-only except TEST_COUNT.md.
usage: python3 -I research/ops/test_count.py
"""
import json, os, re, time
from statistics import NormalDist

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ND = os.path.join(R, "new_discovery")


def js(p, *keys, default=0):
    try:
        d = json.load(open(os.path.join(R, p)))
        for k in keys: d = d[k]
        return d
    except Exception: return default


rows = []
reg = [l for l in open(os.path.join(ND, "REGISTRY.md")) if l.startswith("| ") and not l.startswith("| ID") and not l.startswith("|---")]
rows.append(("this branch", "discovery batches 001–004, user theories, H4 checks (REGISTRY.md rows)", len(reg)))
rows.append(("this branch", "IND batches 001–002 (TEST tests)", js("new_discovery/ind_batch_001/results.json", "n_test_tests") + js("new_discovery/ind_batch_002/results.json", "n_test_tests")))
rows.append(("this branch", "theory event studies THE-005, THE-017, event batch 001 (TEST tests)", 12 + 8 + 30))
rows.append(("this branch", "STR-023 replication, STR-025, STR-026, H4 ETH/A/B/C checks", 5 + 1 + 1 + 4))
rows.append(("this branch", "earlier studies: news_markets 225, news_surprise 56, indicator scans (multi_market ~2,950 variants × 33 markets fitted picks 108; long_history ~2,640 per market × 3), TradingView/community/requested scans", 225 + 56 + 108 + 3 * 2640 + 400))
rows.append(("other branch", "theory library screen 535 + earlier runs 2 × 416 + V2 54 + V1 3", 535 + 832 + 54 + 3))
rows.append(("other branch", "ORB 96, zone 60, oil_dca_bot 502, signal clone 10, shortlist / session / Batch 2 (~30)", 96 + 60 + 502 + 10 + 30))
total = sum(n for _, _, n in rows); z_bonf = NormalDist().inv_cdf(1 - 0.05 / (2 * total))
lines = [f"# Test count (G7 honesty check), {time.strftime('%Y-%m-%d %H:%M', time.gmtime())} UTC", "",
         "Every evaluated configuration counts. Several are rough counts, documented in the script, and the total is a lower-bound order of magnitude.", "",
         "| Branch | What | Tests / configurations |", "|---|---|---|"] + [f"| {b} | {w} | {n:,} |" for b, w, n in rows] + [
         f"| **Total** | | **{total:,}** |", "",
         f"- **Bonferroni threshold** for the whole family (two-sided 5%): |z| ≥ **{z_bonf:.2f}**.",
         "- **No result in the programme reaches it.** The strongest single results are the H4 2017–19 period (p < 0.001; 1,000 random draws, so the resolution floor is 0.001) and the HAR volatility forecast (a volatility, not direction, result).",
         "- **How to read this:** with this many tests, about 5% of truly useless ideas pass any single 5% test. That is why every result must survive a **forward test on new data** before it counts.", ""]
open(os.path.join(R, "ops", "TEST_COUNT.md"), "w").write("\n".join(lines)); print("\n".join(lines))
