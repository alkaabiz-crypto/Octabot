"""STR-045 post-hoc (user question 2026-11-20: "what if more than 5 days"): holds of 10/20/40/60 days, with the
signal from 1-day, 5-day and 20-day summed flows (z vs the previous 60 days of that sum). Same 2-day reporting delay,
same 0.05%/side cost. Non-overlapping trades; IC on non-overlapping samples; random-day benchmark; BH over all cells.
Labelled post-hoc. usage: python3 -I longer_holds.py <scratch dir>"""
import json, math, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_str045 as R5  # noqa: E402


def main():
    S = sys.argv[1]; rng = np.random.default_rng(30451); cells = []
    for asset, f, sym in (("BTC", "bitcoin-etf-flows.html", "BTCUSDT"), ("ETH", "ethereum-etf-flows.html", "ETHUSDT")):
        fl = R5.flows(os.path.join(S, f)); px = R5.opens(sym)
        for win in (1, 5, 20):
            s = fl.rolling(win).sum(); z = ((s - s.rolling(60).mean().shift(1)) / s.rolling(60).std().shift(1)).dropna()
            for h in (10, 20, 40, 60):
                ent = z.index + pd.Timedelta(days=2); ex = ent + pd.Timedelta(days=h); ok = ent.isin(px.index) & ex.isin(px.index)
                zz = z[ok]; ret = pd.Series(px.reindex(ex[ok]).values / px.reindex(ent[ok]).values - 1, index=zz.index)
                tr = []; nxt = None
                for d, zv in zz.items():
                    if nxt is not None and d < nxt: continue
                    if abs(zv) >= 1: side = 1 if zv > 0 else -1; tr.append((d, side, side * ret[d])); nxt = d + pd.Timedelta(days=h)
                g = np.array([x[2] for x in tr]) - 2 * R5.COST; a = zz.iloc[::h]; b = ret.iloc[::h]
                ic = float(np.corrcoef(a.rank(), b.rank())[0, 1]) if len(a) > 3 else float("nan")
                sims = np.array([(rng.choice([-1, 1], len(tr)) * rng.choice(ret.values, len(tr))).mean() - 2 * R5.COST for _ in range(1000)]) if len(tr) else np.array([0])
                half = [x for x in tr if str(x[0].date()) < R5.SPLIT], [x for x in tr if str(x[0].date()) >= R5.SPLIT]
                cells.append(dict(asset=asset, flow_window_days=win, hold_days=h, trades=len(tr), mean_net_pct=round(float(g.mean() * 100), 2) if len(g) else None,
                                  win_pct=round(float((g > 0).mean() * 100), 1) if len(g) else None, ic_nonoverlap=round(ic, 3), ic_n=len(a),
                                  val_mean_pct=round(float(np.mean([x[2] for x in half[0]]) * 100 - 0.1), 2) if half[0] else None, val_n=len(half[0]),
                                  test_mean_pct=round(float(np.mean([x[2] for x in half[1]]) * 100 - 0.1), 2) if half[1] else None, test_n=len(half[1]),
                                  random_mean_pct=round(float(sims.mean() * 100), 2), p=float((sims >= g.mean()).mean()) if len(g) else 1.0))
                print(cells[-1], flush=True)
    ps = [c["p"] for c in cells]; o = np.argsort(ps); sig = set()
    for r, i in enumerate(o):
        if ps[i] <= 0.05 * (r + 1) / len(ps): sig = set(o[:r + 1])
    for i, c in enumerate(cells): c["bh_significant"] = i in sig
    json.dump(dict(label="post-hoc", cells=cells), open(os.path.join(HERE, "longer_holds.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
