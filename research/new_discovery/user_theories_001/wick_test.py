"""Test B of PREREG.md: wick rejection ("John Wick's theory") = the frozen library's C2, called UNCHANGED on new timeframes.
Scored with the frozen engine.evaluate / engine.random_control and run.py's verdict rule and seed formula.
usage: LIB_DIR=<extract>/research/theory_library BARS_DIR=<exness 1m bars> python3 -I wick_test.py
"""
import json, math, os, sys, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.environ["LIB_DIR"])
import engine as E, theories as T, run as RUN  # noqa: E401,E402  (frozen, unchanged)

NEW = [(m, tf) for m in E.EXNESS for tf in ("15m", "4h", "1d")] + [(m, tf) for m in E.CRYPTO for tf in ("4h", "1d")]
REF = [(m, "1h") for m in E.EXNESS + E.CRYPTO]
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))


def nw_t(x, L=5):
    n = len(x); d = x - x.mean(); v = (d @ d) / n + 2 * sum((1 - j / (L + 1)) * (d[j:] @ d[:-j]) / n for j in range(1, L + 1)); return float(x.mean() / math.sqrt(v / n))


def one(mkt, tf):
    key = f"C2|{mkt}|{tf}"; c, bk = T.c2(mkt, tf); r1, _ = E.evaluate(c, bk, 1); r2, meta = E.evaluate(c, bk, 2)
    rng = np.random.default_rng(RUN.SEED + zlib.crc32(key.encode()) % 100000)
    rc = E.random_control(c, meta, 2, RUN.DRAWS, rng) if len(meta) else {"dev": None, "holdout": None}
    d, h = RUN.summ(r2["dev"]), RUN.summ(r2["holdout"]); p95 = {p: (round(float(v[1] * 1e4), 2) if v is not None else None) for p, v in rc.items()}
    ok = (d["mean_bp"] is not None and h["mean_bp"] is not None and d["mean_bp"] > 0 and h["mean_bp"] > 0 and h["trades"] >= 30
          and p95["dev"] is not None and p95["holdout"] is not None and d["mean_bp"] > p95["dev"] and h["mean_bp"] > p95["holdout"])
    st = {}
    for p in ("dev", "holdout"):
        x = r2[p]
        st[p] = dict(t=round(float(x.mean() / (x.std(ddof=1) / math.sqrt(len(x)))), 2), nw_t=round(nw_t(x), 2)) if len(x) > 10 else {}
    p_hold = 1 - Phi(st["holdout"]["t"]) if st["holdout"] else 1.0
    return key, dict(x1=dict(dev=RUN.summ(r1["dev"]), holdout=RUN.summ(r1["holdout"])), x2=dict(dev=d, holdout=h), random_x2_p95_bp=p95,
                     stats_x2=st, p_holdout_one_sided=round(p_hold, 4), verdict="PASS" if ok else "FAIL")


def bh(p, q=0.05):
    o = np.argsort(p); m = len(p); k = max([i + 1 for i in range(m) if p[o[i]] <= q * (i + 1) / m], default=0); return set(o[:k].tolist())


def main():
    out = {"new": {}, "reference_1h": {}}
    for mkt, tf in NEW:
        k, v = one(mkt, tf); out["new"][k] = v; print("NEW", k, v["x2"], v["verdict"], v["stats_x2"], flush=True)
    for mkt, tf in REF:
        k, v = one(mkt, tf); out["reference_1h"][k] = v; print("REF", k, v["x2"], v["verdict"], flush=True)
    keys = list(out["new"]); sig = bh([out["new"][k]["p_holdout_one_sided"] for k in keys])
    for i, k in enumerate(keys): out["new"][k]["bh_significant"] = i in sig
    out["n_new"] = len(keys); out["n_pass_new"] = sum(v["verdict"] == "PASS" for v in out["new"].values()); out["n_bh_new"] = len(sig)
    ref = json.load(open(os.path.join(os.environ["LIB_DIR"], "results", "results.json")))["results"]
    out["reference_reproduces_frozen"] = all(ref[k]["x2"] == v["x2"] and ref[k]["verdict"] == v["verdict"] for k, v in out["reference_1h"].items())
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True); json.dump(out, open(os.path.join(HERE, "results", "wick_test.json"), "w"), indent=1)
    print("new:", out["n_new"], "PASS:", out["n_pass_new"], "BH:", out["n_bh_new"], "| 1h reference reproduces frozen:", out["reference_reproduces_frozen"])


if __name__ == "__main__":
    main()
