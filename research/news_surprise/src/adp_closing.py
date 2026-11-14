"""ADP closing amendment, items 1 and 2: methodology split (2016-01..2021-12 vs 2022-01..2026-06) and an exact
reconciliation of every sample count used in addendum 5 and its robustness audit. Read-only with respect to earlier
results. usage: same environment as adp_robustness.py"""
import datetime
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adp_preposition as AP  # noqa: E402
import adp_robustness as AR  # noqa: E402

S = AP.S
D0, D1 = datetime.date(2016, 1, 1), datetime.date(2026, 6, 30)


def main():
    out = {}
    # ---------------------------------------------------------------- source records and cross-source comparisons
    adp, adp_q = AR.merged("ADP Nonfarm Employment Change")
    nfp, nfp_q = AR.merged("Nonfarm Payrolls")
    une, une_q = AR.merged("Unemployment Rate")
    out["sources"] = {
        "ADP records per source": adp_q["sizes"], "ADP records total": sum(adp_q["sizes"].values()),
        "ADP pairwise cross-source comparisons (same reference month in two sources)": adp_q["pairwise_agree"] + len(adp_q["pairwise_disagree"]),
        "ADP comparisons agreeing": adp_q["pairwise_agree"], "ADP comparisons conflicting": adp_q["pairwise_disagree"],
        "ADP unique reference months after merging": len(adp),
        "NFP records per source": nfp_q["sizes"], "NFP records total": sum(nfp_q["sizes"].values()),
        "NFP pairwise cross-source comparisons": nfp_q["pairwise_agree"] + len(nfp_q["pairwise_disagree"]),
        "NFP comparisons agreeing": nfp_q["pairwise_agree"], "NFP comparisons conflicting": nfp_q["pairwise_disagree"],
        "NFP unique reference months after merging": len(nfp),
        "Unemployment unique reference months": len(une)}
    # ---------------------------------------------------------------- addendum 5 (original) sample, step by step
    o_adp, o_nfp = AP.adp_series(), AP.nfp_surprises()
    in_win = {d: s for d, s in o_nfp.items() if D0 <= d <= D1}
    nz = {d: s for d, s in in_win.items() if s != 0}
    with_adp = {d: max(x for x in o_adp if 0 <= (d - x).days <= 7) for d in nz if any(0 <= (d - x).days <= 7 for x in o_adp)}
    orig = {d: a for d, a in with_adp.items() if o_adp[a] != 0}
    out["addendum5_sample"] = {
        "source": "adp_preposition.py: ADP from Kaggle US + Hugging Face (by release date); NFP surprise from data/consensus_investing*.csv (by release date)",
        "NFP releases with a surprise value, all dates": len(o_nfp),
        "of which dated 2016-01-01..2026-06-30": len(in_win),
        "excluded: surprise exactly zero": sorted(d.isoformat() for d, s in in_win.items() if s == 0),
        "excluded: no ADP release 0-7 days before": sorted(d.isoformat() for d in nz if d not in with_adp),
        "excluded: ADP surprise exactly zero": sorted(d.isoformat() for d, a in with_adp.items() if o_adp[a] == 0),
        "N used (test 1 and the trade test pairs)": len(orig)}
    # ---------------------------------------------------------------- audit sample (reference-month pairing)
    ref = {}
    for rm, (d, a, f) in nfp.items():
        if D0 <= d <= D1 and rm in adp:
            ref[d] = rm
    no_adp_month = sorted(d.isoformat() for rm, (d, a, f) in nfp.items() if D0 <= d <= D1 and rm not in adp)
    rows = []
    for d, rm in sorted(ref.items()):
        _, na, nf = nfp[rm]
        u = une.get(rm)
        du = (u[1] - u[2]) if u else 0.0
        rows.append({"date": d, "ref": f"{rm[0]}-{rm[1]:02d}", "adp": adp[rm][1] - adp[rm][2], "nfp": (na - nf) - 100 * du,
                     "unemployment_missing": u is None})
    used = [r for r in rows if r["adp"] != 0 and r["nfp"] != 0]
    extra = sorted(r["date"].isoformat() for r in used if r["date"] not in orig)
    missing = sorted(d.isoformat() for d in orig if d not in {r["date"] for r in used})
    out["audit_sample"] = {
        "NFP reference months 2016-01..2026-06 (release dates)": sum(1 for rm, (d, a, f) in nfp.items() if D0 <= d <= D1),
        "excluded: no ADP figure for the same reference month": no_adp_month,
        "pairs by reference month": len(rows),
        "excluded: ADP surprise zero": sorted(r["date"].isoformat() for r in rows if r["adp"] == 0),
        "excluded: NFP surprise zero": sorted(r["date"].isoformat() for r in rows if r["adp"] != 0 and r["nfp"] == 0),
        "N used (audit test 1)": len(used),
        "in audit but not in addendum 5": extra,
        "in addendum 5 but not in audit": missing,
        "unemployment figure missing (term set to 0)": sorted(r["date"].isoformat() for r in rows if r["unemployment_missing"])}
    # why the extras differ: look them up in the addendum-5 loaders
    why = {}
    for ds in extra:
        d = datetime.date.fromisoformat(ds)
        reasons = []
        if d not in o_nfp:
            reasons.append("NFP surprise absent from data/consensus_investing*.csv (present only in the Kaggle global copy)")
        elif o_nfp[d] == 0:
            reasons.append("NFP surprise zero under addendum-5 data")
        if not any(0 <= (d - x).days <= 7 for x in o_adp):
            reasons.append("no ADP within 0-7 days in the addendum-5 ADP sources")
        why[ds] = reasons or ["other"]
    out["audit_sample"]["reasons for the extra matches"] = why
    # ---------------------------------------------------------------- methodology split
    split = {}
    for name, a0, a1 in (("2016-01..2021-12", D0, datetime.date(2021, 12, 31)), ("2022-01..2026-06", datetime.date(2022, 1, 1), D1)):
        for samp_name, samp in (("audit sample (reference-month pairing)", [(r["adp"], r["nfp"]) for r in used if a0 <= r["date"] <= a1]),
                                ("addendum-5 sample (date-window pairing)", [(o_adp[orig[d]], nz[d]) for d in orig if a0 <= d <= a1])):
            n = len(samp)
            h = int(sum(np.sign(a) == np.sign(b) for a, b in samp))
            lo, hi = AR.wilson(h, n)
            split[f"{name} | {samp_name}"] = {"N": n, "same_sign": h, "hit_rate_pct": 100 * h / n, "ci95_pct": [100 * lo, 100 * hi],
                                              "p_one_sided_greater_than_50pct": AR.binom_p(h, n),
                                              "p_two_sided": min(1.0, 2 * min(AR.binom_p(h, n), AR.binom_p(n - h, n)))}
    out["methodology_split"] = split
    out["generated_utc"] = S.fmt(time.time())
    json.dump(out, open(os.path.join(AP.R.ROOT, "reports", "adp_closing.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "sources"}, indent=1, default=str))
    print(json.dumps(out["sources"], indent=1, default=str)[:2500])


if __name__ == "__main__":
    main()
