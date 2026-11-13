"""Batch 3 runner (PREREGISTRATION.md): search on 2025 for every combination, shortlist top 30 per part, confirm once on 2026.
Usage: DATA_EXNESS=<dir of <mkt>_1m.npz> DATA_BINANCE=<dir> python3 -I run.py [--sanity]
Raw data stays in scratch; only derived statistics are written to results/.
"""
import itertools, json, os, sys, time, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import engine as E, signals as SG  # noqa: E402

MARKETS = {"XAUUSDm": "DATA_EXNESS", "USOILm": "DATA_EXNESS", "US500m": "DATA_EXNESS", "USTECm": "DATA_EXNESS", "DE30m": "DATA_EXNESS",
           "BTCUSDT": "DATA_BINANCE", "ETHUSDT": "DATA_BINANCE"}
TFS = {15: 60, 60: 240, 240: 1440}        # timeframe -> higher timeframe (minutes)
TOP, CAP, ALPHA, DRAWS = 30, 3, 0.05, 1000


def stats(r):
    r = r[~np.isnan(r)]; n = len(r)
    if n < 2: return dict(n=n)
    m, sd = r.mean(), r.std(ddof=1); gp, gl = r[r > 0].sum(), -r[r < 0].sum()
    return dict(n=n, mean_bp=round(float(m * 1e4), 2), t=round(float(m / (sd / np.sqrt(n))), 2) if sd > 0 else 0.0,
                pf=round(float(gp / gl), 3) if gl > 0 else None, win=round(float((r > 0).mean()), 3))


def eval_mask(L, S, R, disc):
    """Overlapping-trade screen statistics on the discovery period."""
    rl, rs = R[1][0], R[-1][0]; a = rl[L & disc]; b = rs[S & disc]; r = np.concatenate([a, b]); return stats(r)


def one_position(L, S, R, period, mult, cost):
    """Confirmation trades: one position at a time, signals in `period` only, net at `mult` x cost."""
    idx = np.flatnonzero((L | S) & period); out = []; sides = []; free = -1
    for i in idx:
        if i <= free: continue
        sd = 1 if L[i] else -1; r, xi = R[sd]
        if np.isnan(r[i]) or xi[i] < 0: continue
        out.append(r[i] - (mult - 1) * cost); sides.append(sd); free = xi[i]
    return np.array(out), np.array(sides)


def build(market, tf):
    d, cost_bp = E.load_1m(os.path.join(os.environ[MARKETS[market]], f"{market}_1m.npz"), market)
    df = E.bars(d, tf); hdf = E.bars(d, TFS[tf]); I = SG.compute(df, tf, market, hdf)
    T, F = SG.triggers(I), SG.filters(I); S = SG.strategies(I, T, F); Th = SG.theories(I, tf, market)
    R = E.outcomes(df, cost_bp); ent_min = np.r_[df.t.values[1:], df.t.values[-1] + tf]          # entry bar start (next bar)
    return dict(I=I, T=T, F=F, S=S, Th=Th, R=R, cost=cost_bp / 1e4, disc=ent_min < E.H2026, hold=ent_min >= E.H2026, n=len(df))


def combos(part, X):
    T, F = X["T"], X["F"]; fl = list(F)
    if part == "A":
        for tn, (L, S) in T.items():
            yield (tn, ()), tn, L, S
            for f in fl: yield (tn, (f,)), tn, L & F[f][0], S & F[f][1]
            for f, g in itertools.combinations(fl, 2): yield (tn, (f, g)), tn, L & F[f][0] & F[g][0], S & F[f][1] & F[g][1]
    elif part == "B":
        for sn, (L, S) in X["S"].items(): yield (sn, ()), sn, L, S
    else:
        wl, ws = X["T"]["Wick_rejection"]
        for tn, (L, S) in X["Th"].items():
            yield (tn, ()), tn, L, S
            yield (tn, ("+wick",)), tn, L & wl, S & ws
            for f in fl:
                yield (tn, (f,)), tn, L & F[f][0], S & F[f][1]
                yield (tn, ("+wick", f)), tn, L & wl & F[f][0], S & ws & F[f][1]
            for f, g in itertools.combinations(fl, 2): yield (tn, (f, g)), tn, L & F[f][0] & F[g][0], S & F[f][1] & F[g][1]


def sanity():
    """Engine checks: random signals lose about the cost; a look-ahead 'cheat' wins; outcome hand-check."""
    X = build("XAUUSDm", 60); R = X["R"]["X1"]; rng = np.random.default_rng(1); n = X["n"]
    L = rng.random(n) < 0.05; S = (rng.random(n) < 0.05) & ~L
    c = X["I"]["c"]; fut = np.r_[c[13:], np.full(13, np.nan)] - np.r_[c[1:], np.nan]; cheatL, cheatS = fut > 0, fut < 0
    print("random   :", eval_mask(L, S, R, X["disc"]), "cost bp", round(X["cost"] * 1e4, 2))
    print("cheat    :", eval_mask(cheatL, cheatS, X["R"]["X3"], X["disc"]))
    i = 5000; o, h, l, cl, A = X["I"]["o"], X["I"]["h"], X["I"]["l"], X["I"]["c"], E.atr(E.bars(E.load_1m(os.path.join(os.environ["DATA_EXNESS"], "XAUUSDm_1m.npz"), "XAUUSDm")[0], 60)).values
    ent = o[i + 1]; stop, tp = ent - 1.5 * A[i], ent + 3 * A[i]; px = None
    for j in range(i + 1, i + 25):
        if j > i + 1 and o[j] <= stop: px = o[j]; break
        if l[j] <= stop: px = stop; break
        if h[j] >= tp + ent * X["cost"]: px = tp; break
    px = px if px is not None else cl[i + 24]; hand = px / ent - 1 - X["cost"]
    print("hand-check long bar 5000:", round(hand * 1e4, 3), "engine:", round(R[1][0][i] * 1e4, 3), "exit idx", R[1][1][i], "j", j)


def main():
    if "--sanity" in sys.argv: sanity(); return
    t0 = time.time(); res = {"A": [], "B": [], "C": []}; cache = {}; n_eval = 0
    for market in MARKETS:
        for tf in TFS:
            X = build(market, tf); cache[(market, tf)] = None
            for part in "ABC":
                if part == "C" and tf == 240: pass
                for key, trig, L, S in combos(part, X):
                    for ex in E.EXITS:
                        s = eval_mask(L, S, X["R"][ex], X["disc"]); n_eval += 1
                        if s.get("n", 0) >= 30 and s["mean_bp"] > 0 and (s["pf"] or 0) > 1.0:
                            res[part].append(dict(part=part, market=market, tf=tf, exit=ex, entry=key[0], extra=list(key[1]), trig=trig, **s))
            print(f"{market} {tf}m done, evaluations so far {n_eval}, kept A/B/C {len(res['A'])}/{len(res['B'])}/{len(res['C'])}, {time.time() - t0:.0f}s", flush=True)
            del X
    short = {}
    for part in "ABC":
        cnt = {}; sel = []
        for r in sorted(res[part], key=lambda z: -z["t"]):
            k = (r["market"], r["trig"])
            if cnt.get(k, 0) >= CAP: continue
            cnt[k] = cnt.get(k, 0) + 1; sel.append(r)
            if len(sel) == TOP: break
        short[part] = sel
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    json.dump(dict(evaluations=n_eval, kept={p: len(v) for p, v in res.items()}, shortlist=short), open(os.path.join(HERE, "results", "search_2025.json"), "w"), indent=1)
    # ---- confirmation on 2026, each shortlisted item once
    conf = []
    for part in "ABC":
        for r in short[part]:
            X = build(r["market"], r["tf"]); src = {"A": None, "B": X["S"], "C": X["Th"]}[part]
            if part == "A": L, S = X["T"][r["entry"]]
            else: L, S = src[r["entry"]]
            for f in r["extra"]:
                if f == "+wick": L, S = L & X["T"]["Wick_rejection"][0], S & X["T"]["Wick_rejection"][1]
                else: L, S = L & X["F"][f][0], S & X["F"][f][1]
            R = X["R"][r["exit"]]; r2, sides = one_position(L, S, R, X["hold"], 2, X["cost"]); r1, _ = one_position(L, S, R, X["hold"], 1, X["cost"])
            elig = np.flatnonzero(X["hold"] & ~np.isnan(R[1][0]) & ~np.isnan(R[-1][0])); rng = np.random.default_rng(20261113 + zlib.crc32(json.dumps([r["part"], r["market"], r["tf"], r["exit"], r["entry"], r["extra"]]).encode()))
            if len(r2) >= 2:
                draws = np.empty(DRAWS)
                for k in range(DRAWS):
                    ii = rng.choice(elig, len(r2)); draws[k] = np.mean(np.where(sides > 0, R[1][0][ii], R[-1][0][ii]) - X["cost"])
                p = float((1 + (draws >= r2.mean()).sum()) / (DRAWS + 1))
            else: p = 1.0
            conf.append(dict(**{k: r[k] for k in ("part", "market", "tf", "exit", "entry", "extra")}, search_2025=dict(n=r["n"], mean_bp=r["mean_bp"], t=r["t"], pf=r["pf"]),
                             confirm_2026=dict(trades=int(len(r2)), mean_bp_2x=round(float(r2.mean() * 1e4), 2) if len(r2) else None, mean_bp_1x=round(float(r1.mean() * 1e4), 2) if len(r1) else None,
                                               win=round(float((r2 > 0).mean()), 3) if len(r2) else None, sum_pct_2x=round(float(r2.sum() * 100), 2) if len(r2) else None, p_random=round(p, 4))))
            del X
    order = sorted(range(len(conf)), key=lambda i: conf[i]["confirm_2026"]["p_random"]); m = len(conf); alive = True
    for rank, i in enumerate(order):
        c = conf[i]["confirm_2026"]; thr = ALPHA / (m - rank); holm = alive and c["p_random"] <= thr; alive = holm
        c["holm_threshold"] = round(thr, 5); c["PASS"] = bool(holm and c["trades"] >= 20 and (c["mean_bp_2x"] or -1) > 0)
    json.dump(dict(evaluations=n_eval, confirmation=conf, passed=[c for c in conf if c["confirm_2026"]["PASS"]]), open(os.path.join(HERE, "results", "confirm_2026.json"), "w"), indent=1)
    print("PASSED:", sum(c["confirm_2026"]["PASS"] for c in conf), "of", m, f"{time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
