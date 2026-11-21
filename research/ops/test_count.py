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
rows.append(("this branch", "STR-027 (4 markets) and TradingView batch 003 (260 IC + 50 combination TEST tests)", 4 + js("new_discovery/tv_batch_003/results.json", "n_ic_test_tests") + js("new_discovery/tv_batch_003/results.json", "n_combo_tests")))
rows.append(("this branch", "TradingView batch 004: Part A IC TEST tests + Part B 7,872 market x horizon cells searched (82 TEST picks)", js("new_discovery/tv_batch_004/results_A.json", "n_ic_test_tests") + js("new_discovery/tv_batch_004/results_B.json", "n_cells")))
rows.append(("this branch", "TradingView batch 005 (24 rules x 5 markets TEST tests)", js("new_discovery/tv_batch_005/results.json", "n_tests")))
rows.append(("this branch", "STR-032 GainzAlgo-style (2 variants x 5 markets)", js("new_discovery/str_032/results.json", "n_tests")))
rows.append(("this branch", "STR-033 QuantLab NY-open candle (3 variants)", 3))
rows.append(("this branch", "Academic batch 005 (STR-034..038, strategy x market)", js("new_discovery/acad_batch_005/results.json", "n_tests")))
rows.append(("this branch", "Pairs batch 006 (STR-039a-h, STR-040)", js("new_discovery/pairs_batch_006/results.json", "n_tests")))
rows.append(("this branch", "STR-041 ICT sweep/CHoCH/dominance/OTE (3 variants x 5 markets)", js("new_discovery/str_041/results.json", "n_tests")))
rows.append(("this branch", "STR-042 market making (6 settings), SIG-005 CryptoMeter (3 exits + 28-cell grid)", 6 + 3 + 28))
rows.append(("this branch", "STR-043 value-area reel (2 scenarios x 5 markets)", js("new_discovery/str_043/results.json", "n_tests")))
rows.append(("this branch", "STR-044 liquidity-sweep entry (2 variants x 5 markets)", js("new_discovery/str_044/results.json", "n_tests")))
rows.append(("this branch", "STR-045 ETF flows (2 assets x 2 holds x IC+rule)", 8))
rows.append(("this branch", "STR-045 post-hoc longer holds (24) + momentum control (24)", 48))
rows.append(("this branch", "STR-047 carry (2 assets x 2 rules) + STR-048 yields-gold (2)", 6))
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
