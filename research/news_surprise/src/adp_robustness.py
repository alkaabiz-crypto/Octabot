"""Robustness audit of PROTOCOL.md addendum 5 (ADP -> NFP pre-positioning). Does not modify the addendum-5 results.
usage: SURPRISE=consensus LONG_DATA=.. MULTI_BARS=.. TICK_WORK=.. KAGGLE_US=<csv> KAGGLE_GLOBAL=<csv> HF_CAL=<csv>
       python src/adp_robustness.py"""
import csv
import datetime
import json
import math
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import adp_preposition as AP  # noqa: E402
import replicate_2016 as RP  # noqa: E402

R, TK = RP.R, RP.TK
NM, G, S = R.NM, R.G, R.S
MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
RNG = np.random.default_rng(20261112)


# ------------------------------------------------------------------------------------------------- data
def ref_month(release, name):
    m = re.search(r"\((\w{3})\)", name)
    if not m or m.group(1) not in MON:
        return None
    mo = MON[m.group(1)]
    y = release.year - (1 if mo > release.month else 0)
    return (y, mo)


def load_investing_csv(path, pattern):
    out = {}
    for r in csv.DictReader(open(path, encoding="utf-8", errors="replace")):
        if r["zone"] != "united states":
            continue
        ev = re.sub(r"\s+", " ", r["event"]).strip()
        if not ev.startswith(pattern + " ("):
            continue
        d = datetime.datetime.strptime(r["date"], "%d/%m/%Y").date()
        a, f = R._num(r["actual"]), R._num(r["forecast"])
        rm = ref_month(d, ev)
        if a is not None and f is not None and rm:
            out[rm] = (d, a, f)
    return out


def load_hf(pattern):
    out, cur = {}, None
    for line in open(os.environ["HF_CAL"]):
        p = line.rstrip("\n").split(";")
        if re.match(r"^[A-Z][a-z]+day, ", p[0]):
            cur = datetime.datetime.strptime(p[0], "%A, %B %d, %Y").date()
        elif len(p) == 6 and cur and p[1] == "US" and p[2].startswith(pattern + " ("):
            a, f = R._num(p[3]), R._num(p[4])
            rm = ref_month(cur, p[2])
            if a is not None and f is not None and rm:
                out[rm] = (cur, a, f)
    return out


def merged(pattern):
    srcs = {"kaggle_us": load_investing_csv(os.environ["KAGGLE_US"], pattern),
            "kaggle_global": load_investing_csv(os.environ["KAGGLE_GLOBAL"], pattern), "hf": load_hf(pattern)}
    agree, disagree = 0, []
    names = list(srcs)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            for k in set(srcs[names[i]]) & set(srcs[names[j]]):
                x, y = srcs[names[i]][k], srcs[names[j]][k]
                if x[0] == y[0] and abs(x[1] - y[1]) < 1e-9 and abs(x[2] - y[2]) < 1e-9:
                    agree += 1
                else:
                    disagree.append([names[i], names[j], f"{k[0]}-{k[1]:02d}", str(x), str(y)])
    out = {}
    for nm in ("kaggle_us", "hf", "kaggle_global"):
        for k, v in srcs[nm].items():
            out.setdefault(k, v)
    return out, {"pairwise_agree": agree, "pairwise_disagree": disagree, "sizes": {k: len(v) for k, v in srcs.items()}}


# ------------------------------------------------------------------------------------------------- statistics
def wilson(h, n, z=1.96):
    p = h / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - w, c + w


def binom_p(h, n):
    return sum(math.comb(n, k) for k in range(h, n + 1)) / 2 ** n


def min_detectable_rate(n, alpha=0.05, power=0.8):
    crit = next(k for k in range(n + 1) if binom_p(k, n) <= alpha)
    for p1 in np.arange(0.5, 1.0, 0.005):
        pw = sum(math.comb(n, k) * p1 ** k * (1 - p1) ** (n - k) for k in range(crit, n + 1))
        if pw >= power:
            return float(p1)
    return None


def spearman(x, y, perms=5000):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    rho = float(np.corrcoef(rx, ry)[0, 1])
    null = np.array([np.corrcoef(rx, RNG.permutation(ry))[0, 1] for _ in range(perms)])
    return rho, float((np.sum(null >= rho) + 1) / (perms + 1))


def summarize(rr, sg, lo, sh):
    rr = np.array(rr)
    perm = np.array([np.where(RNG.permutation(sg) > 0, lo, sh).mean() for _ in range(2000)])
    s = np.sort(rr)
    k = int(len(s) * 0.1)
    trimmed = float(s[k:len(s) - k].mean()) if len(s) > 2 * k else float(s.mean())
    sd = float(rr.std(ddof=1)) if len(rr) > 1 else float("nan")
    return {"trades": len(rr), "mean_r": float(rr.mean()), "median_r": float(np.median(rr)), "trimmed10_mean_r": trimmed,
            "win_rate_pct": float((rr > 0).mean() * 100), "p_signflip": float((np.sum(perm >= rr.mean()) + 1) / 2001),
            "min_detectable_mean_r_80pct_power": (1.645 + 0.842) * sd / math.sqrt(len(rr))}


# ------------------------------------------------------------------------------------------------- trades
def tick_leg(win, t, e_off, x_off):
    tt, b, a = win
    mid = (b + a) / 2
    t_in = t + e_off
    pre = mid[(tt >= t_in - 2700) & (tt < t_in)]
    i, j = TK.first_at(tt, t_in), TK.first_at(tt, t + x_off)
    if len(pre) < 10 or i is None or j is None or pre.max() <= pre.min() or tt[i] - t_in > 60:
        return None
    Rr = 2 * (pre.max() - pre.min())
    return (b[j] - a[i]) / Rr, (b[i] - a[j]) / Rr


def bar_leg(m, t, e_off, x_off):
    q = m.q
    ji, jx = m.idx.get(t + e_off), m.idx.get(t + x_off)
    if ji is None or jx is None or ji < 3:
        return None
    hi, lo = max(q["bh"][ji - 3:ji]), min(q["bl"][ji - 3:ji])
    if hi <= lo or m.tq[ji - 3] < t + e_off - 3 * 900 - 3600:       # require the 3 candles to be the 45 minutes before
        return None
    Rr = 2 * (hi - lo)
    return (q["bo"][jx] - q["ao"][ji]) / Rr, (q["bo"][ji] - q["ao"][jx]) / Rr


def main():
    adp, adp_q = merged("ADP Nonfarm Employment Change")
    nfp, nfp_q = merged("Nonfarm Payrolls")
    une, _ = merged("Unemployment Rate")
    out = {"data": {"adp_sources": adp_q, "nfp_sources": nfp_q}}
    # pairing: reference month vs the original 0-7 day window
    orig_adp, orig_nfp = AP.adp_series(), AP.nfp_surprises()
    orig_pairs = {}
    for d, s in orig_nfp.items():
        if datetime.date(2016, 1, 1) <= d <= datetime.date(2026, 6, 30) and s != 0:
            prior = [x for x in orig_adp if 0 <= (d - x).days <= 7]
            if prior and orig_adp[max(prior)] != 0:
                orig_pairs[d] = max(prior)
    ref_pairs, mism = {}, []
    for rm, (d, a, f) in nfp.items():
        if not (datetime.date(2016, 1, 1) <= d <= datetime.date(2026, 6, 30)) or rm not in adp:
            continue
        ad = adp[rm][0]
        ref_pairs[d] = (rm, ad)
        if d in orig_pairs and orig_pairs[d] != ad:
            mism.append([d.isoformat(), orig_pairs[d].isoformat(), ad.isoformat()])
        if (d - ad).days < 0:
            mism.append([d.isoformat(), "ADP released after NFP", ad.isoformat()])
    out["data"]["pairing"] = {"original_window_pairs": len(orig_pairs), "reference_month_pairs": len(ref_pairs),
                              "window_vs_reference_mismatches": mism}
    # surprise scores (reference-month pairing)
    rows = []
    for d, (rm, ad) in sorted(ref_pairs.items()):
        _, na, nf = nfp[rm]
        u = une.get(rm)
        du = (u[1] - u[2]) if u else 0.0
        sa = adp[rm][1] - adp[rm][2]
        rows.append({"date": d, "adp": sa, "nfp_full": (na - nf) - 100 * du, "nfp_pay": na - nf})
    t1 = {}

    def hit_block(name, sel, key):
        z = [(r["adp"], r[key]) for r in sel if r["adp"] != 0 and r[key] != 0]
        if len(z) < 10:
            return
        h = sum(np.sign(a) == np.sign(b) for a, b in z)
        n = len(z)
        lo, hi = wilson(h, n)
        t1[name] = {"releases": n, "same_sign": int(h), "pct": 100 * h / n, "p_one_sided": binom_p(int(h), n),
                    "ci95_pct": [100 * lo, 100 * hi], "min_detectable_hit_rate_pct_80pct_power": 100 * min_detectable_rate(n)}
        rho, p = spearman(np.array([a for a, _ in z]), np.array([b for _, b in z]))
        t1[name]["spearman_rho"], t1[name]["spearman_p_one_sided"] = rho, p

    absadp = np.array([abs(r["adp"]) for r in rows])
    med, ter = float(np.median(absadp)), float(np.quantile(absadp, 2 / 3))
    hit_block("all, NFP payrolls + unemployment", rows, "nfp_full")
    hit_block("all, NFP payrolls only", rows, "nfp_pay")
    hit_block("|ADP surprise| above median", [r for r in rows if abs(r["adp"]) > med], "nfp_full")
    hit_block("|ADP surprise| top third", [r for r in rows if abs(r["adp"]) > ter], "nfp_full")
    hit_block("2016-2019", [r for r in rows if r["date"].year <= 2019], "nfp_full")
    hit_block("2020-2026", [r for r in rows if r["date"].year >= 2020], "nfp_full")
    hit_block("2016-2026 excluding 2020", [r for r in rows if r["date"].year != 2020], "nfp_full")
    out["test1"] = t1
    out["thresholds"] = {"adp_abs_median_k": med, "adp_abs_top_third_k": ter}
    for k, v in t1.items():
        print(f"T1 {k:36} {v['same_sign']}/{v['releases']} = {v['pct']:.0f}% (95% CI {v['ci95_pct'][0]:.0f}-{v['ci95_pct'][1]:.0f}%), "
              f"p {v['p_one_sided']:.3f}, rho {v['spearman_rho']:+.2f} (p {v['spearman_p_one_sided']:.3f}), "
              f"detectable at 80% power: >= {v['min_detectable_hit_rate_pct_80pct_power']:.0f}%")
    # trade grid
    t2 = {}
    n_variants = 0
    for mkt, hot in TK.MARKETS.items():
        early = [r for r in rows if r["date"].year <= 2019 and r["adp"] != 0]
        ts = {G.ny_to_utc(r["date"], "08:30"): r for r in early}
        win = RP.windows(mkt, sorted(ts), os.environ["TICK_WORK"])
        base = os.environ["LONG_DATA"] if mkt in NM.FROM_LONG else os.environ["MULTI_BARS"]
        m = NM.Mkt(os.path.join(base, f"{mkt}_15m.csv.gz"))
        late = [r for r in rows if r["date"].year >= 2020 and r["adp"] != 0]
        grids = [("ticks 2016-19", e, x) for e in (-900, -300, -60) for x in (300, 900)] + \
                [("candles 2020-26", e, x) for e in (-3600, -1800, -900) for x in (900, 3600)]
        for src, e, x in grids:
            legs = []
            for r in (early if src.startswith("ticks") else late):
                t = G.ny_to_utc(r["date"], "08:30")
                lg = tick_leg(win[t], t, e, x) if src.startswith("ticks") and t in win else (bar_leg(m, t, e, x) if not src.startswith("ticks") else None)
                if lg:
                    legs.append((r, np.sign(r["adp"]) * hot, lg[0], lg[1]))
            if len(legs) < 10:
                continue
            for var, flt, flip in (("all", lambda r: True, 1), ("excluding 2020", lambda r: r["date"].year != 2020, 1),
                                   ("large ADP surprises", lambda r: abs(r["adp"]) > med, 1), ("reversed direction", lambda r: True, -1)):
                L = [lg for lg in legs if flt(lg[0])]
                if len(L) < 10:
                    continue
                sg = np.array([lg[1] * flip for lg in L])
                lo_, sh_ = np.array([lg[2] for lg in L]), np.array([lg[3] for lg in L])
                rr = np.where(sg > 0, lo_, sh_)
                key = f"{mkt}|{src}|entry T{e // 60:+d}m|exit T{x // 60:+d}m|{var}"
                t2[key] = summarize(rr, sg, lo_, sh_)
                n_variants += 1
    out["test2"] = t2
    ps = [v["p_signflip"] for v in t2.values()]
    keys = list(t2)
    rej = R.LR.benjamini_hochberg(ps)
    out["test2_summary"] = {"variants": n_variants, "raw_p_le_0.05": int(sum(p <= 0.05 for p in ps)),
                            "expected_by_luck": 0.05 * n_variants, "bh_significant": [keys[i] for i in sorted(rej)],
                            "positive_mean": int(sum(v["mean_r"] > 0 for v in t2.values()))}
    print(json.dumps(out["test2_summary"], indent=1))
    best = sorted(t2.items(), key=lambda kv: kv[1]["p_signflip"])[:8]
    for k, v in best:
        print(f"{k:75} n={v['trades']:3} mean {v['mean_r']:+.3f} median {v['median_r']:+.3f} trim {v['trimmed10_mean_r']:+.3f} p {v['p_signflip']:.3f} MDE {v['min_detectable_mean_r_80pct_power']:.2f}")
    out["generated_utc"] = S.fmt(time.time())
    json.dump(out, open(os.path.join(R.ROOT, "reports", "adp_robustness.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
