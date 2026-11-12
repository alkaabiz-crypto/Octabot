"""PROTOCOL.md: does the CPI / NFP surprise (vs. its own trend, first-published data) tell each market's direction?
usage: LONG_DATA=<dir> MULTI_BARS=<dir> python src/run.py"""
import importlib.util
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
_spec = importlib.util.spec_from_file_location("nm", os.path.join(RESEARCH, "news_markets", "src", "run.py"))
NM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(NM)
G, S = NM.G, NM.S
_spec2 = importlib.util.spec_from_file_location("lr", os.path.join(RESEARCH, "long_history", "src", "report.py"))
LR = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(LR)
TEXTBOOK = {"XAUUSDm": -1, "XAGUSDm": -1, "EURUSDm": -1, "GBPUSDm": -1, "US500m": -1, "USTECm": -1, "US30m": -1,
            "DE30m": -1, "BTCUSDm": -1, "ETHUSDm": -1, "USDJPYm": 1, "USDCADm": 1, "USOILm": 0, "UKOILm": 0}
PERMS = 2000


def load(series):
    return json.load(open(os.path.join(ROOT, "data", f"vintage_{series}.json")))


MODE = os.environ.get("SURPRISE", "trend")          # "trend" (own-trend proxy) or "consensus" (actual - forecast)
SUFFIX = "" if MODE == "trend" else "_consensus"


def _num(x):
    x = x.strip().replace(",", "")
    mult = 1.0
    if x.endswith("%"):
        x = x[:-1]
    elif x.endswith("K"):
        x = x[:-1]
    elif x.endswith("M"):
        x, mult = x[:-1], 1000.0
    return float(x) * mult if x not in ("", "-") else None


def scores_consensus():
    import csv as _csv
    rows = list(_csv.DictReader(l for l in open(os.path.join(ROOT, "data", "consensus_investing.csv")) if not l.startswith("#")))
    by = {}
    for r in rows:
        a, f = _num(r["actual"]), _num(r["forecast"])
        if a is None or f is None:
            continue
        kind = "CPI" if r["event"].startswith("Core CPI") else "NFP" if r["event"].startswith("Nonfarm") else "UNRATE"
        by.setdefault(r["date"], {})[kind] = a - f
    out = {}
    for d, v in by.items():
        t = G.ny_to_utc(G.datetime.date.fromisoformat(d), "08:30")
        if "CPI" in v and v["CPI"] != 0:
            out[("CPI", t)] = v["CPI"]
        if "NFP" in v:
            sc = v["NFP"] - 100 * v.get("UNRATE", 0.0)
            if sc != 0:
                out[("NFP", t)] = sc
    return out


def scores():
    if MODE == "consensus":
        return scores_consensus()
    return scores_trend()


def scores_trend():
    """{('CPI'|'NFP', utc release time): surprise score}"""
    out = {}
    for d, obs in load("CPILFESL").items():
        v = [x[1] for x in obs]
        if len(v) < 8:
            continue
        mom = [v[i] / v[i - 1] - 1 for i in range(1, len(v))]
        out[("CPI", G.ny_to_utc(G.datetime.date.fromisoformat(d), "08:30"))] = 100 * (mom[-1] - float(np.mean(mom[-7:-1])))
    pay, un = load("PAYEMS"), load("UNRATE")
    for d, obs in pay.items():
        v = [x[1] for x in obs]
        u = [x[1] for x in un.get(d, [])]
        if len(v) < 5 or len(u) < 2:
            continue
        ch = [v[i] - v[i - 1] for i in range(1, len(v))]
        out[("NFP", G.ny_to_utc(G.datetime.date.fromisoformat(d), "08:30"))] = ch[-1] - float(np.mean(ch[-4:-1])) - 100 * (u[-1] - u[-2])
    return out


def legs(m, t):
    a = m.atr_before(t)
    j, j1 = m.idx.get(t), m.idx.get(t + 900)
    if a is None or j is None or j1 is None:
        return None
    out = {}
    for cost in ("primary", "stress"):
        out[cost] = (m.walk(1, j1, t + NM.HOLD, a, cost), m.walk(-1, j1, t + NM.HOLD, a, cost))
    if None in out["primary"] or None in out["stress"]:
        return None
    out["first15"] = float(np.sign(m.q["bc"][j] - m.q["bo"][j]))
    return out


def test(rows, direction, big_thr, rng):
    """rows: [(score, legs)]. Returns stats for the strategy 'trade direction * sign(score)'."""
    sel = [(s, L) for s, L in rows if big_thr is None or abs(s) > big_thr]
    if len(sel) < 5:
        return {"trades": len(sel)}
    sg = np.array([np.sign(s) * direction for s, _ in sel])
    lo = np.array([L["primary"][0] for _, L in sel])
    sh = np.array([L["primary"][1] for _, L in sel])
    los = np.array([L["stress"][0] for _, L in sel])
    shs = np.array([L["stress"][1] for _, L in sel])
    r = np.where(sg > 0, lo, sh)
    rs = np.where(sg > 0, los, shs)
    perm = np.array([np.where(rng.permutation(sg) > 0, lo, sh).mean() for _ in range(PERMS)])
    p = float((np.sum(perm >= r.mean()) + 1) / (PERMS + 1))
    f15 = np.array([L["first15"] for _, L in sel])
    return {"trades": len(r), "win_rate_pct": float((r > 0).mean() * 100), "expectancy_r": float(r.mean()),
            "expectancy_stress_r": float(rs.mean()), "total_r": float(r.sum()), "perm_mean_r": float(perm.mean()), "p": p,
            "first15_agrees_pct": float(np.mean(f15 == sg) * 100)}


def main():
    sc = scores()
    rng = np.random.default_rng(20261112)
    res = {}
    for mkt in NM.MARKETS:
        base = os.environ["LONG_DATA"] if mkt in NM.FROM_LONG else os.environ["MULTI_BARS"]
        m = NM.Mkt(os.path.join(base, f"{mkt}_15m.csv.gz"))
        fit0 = max(S.ts(2020, 7) if mkt in NM.FROM_LONG else S.ts(2023, 7), int(m.tq[0]) + 30 * 86400)
        end = int(m.tq[-1])
        for kind in ("CPI", "NFP"):
            ev = sorted((t, s) for (k, t), s in sc.items() if k == kind)
            fit = [(s, L) for t, s in ev if fit0 <= t < NM.TEST0 for L in [legs(m, t)] if L]
            tst = [(s, L) for t, s in ev if NM.TEST0 <= t <= end for L in [legs(m, t)] if L]
            if len(fit) < 10:
                continue
            hot = [L["primary"][0] for s, L in fit if s > 0]
            cool = [L["primary"][0] for s, L in fit if s < 0]
            direction = 1 if np.mean(hot) - np.mean(cool) > 0 else -1
            thr = float(np.median([abs(s) for s, _ in fit]))
            for var, th in (("ALL", None), ("BIG", thr)):
                res[f"{mkt}|{kind}|{var}"] = {"direction_when_hot": direction, "textbook": TEXTBOOK[mkt],
                                              "fit": test(fit, direction, th, rng), "test": test(tst, direction, th, rng)}
                r = res[f"{mkt}|{kind}|{var}"]
                print(mkt, kind, var, "hot->", "UP" if direction > 0 else "DOWN",
                      {p: (r[p]["trades"], round(r[p].get("expectancy_r", 0), 3), round(r[p].get("p", 1), 3), round(r[p].get("first15_agrees_pct", 0)))
                       for p in ("fit", "test")}, flush=True)
    passed = [k for k, r in res.items() if r["fit"].get("trades", 0) >= 15 and r["fit"].get("p", 1) <= 0.05
              and r["fit"].get("expectancy_stress_r", -1) > 0 and "p" in r["test"]]
    rej = LR.benjamini_hochberg([res[k]["test"]["p"] for k in passed]) if passed else set()
    confirmed = [passed[i] for i in sorted(rej) if res[passed[i]]["test"]["expectancy_stress_r"] > 0]
    json.dump({"meta": {"generated_utc": S.fmt(time.time()), "perms": PERMS}, "passed_fit": passed, "confirmed": confirmed,
               "results": res}, open(os.path.join(ROOT, "reports", f"results{SUFFIX}.json"), "w"), indent=1)
    print("passed fit:", passed, "\nconfirmed:", confirmed)


if __name__ == "__main__":
    main()
