"""STR-045 post-hoc diagnostic: is the longer-hold flow effect just price momentum? Same rule, same windows/holds,
but the signal is the z-score of the past N-day price return (N = 1, 5, 20) instead of the N-day ETF flow, on the
same flow-calendar days. Also: correlation between flow z and momentum z, and the flow rule restricted to days where
flow and momentum DISAGREE in sign. usage: python3 -I momentum_control.py <scratch dir>"""
import json, os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_str045 as R5  # noqa: E402


def rule(z, ret, h):
    tr = []; nxt = None
    for d, zv in z.items():
        if nxt is not None and d < nxt: continue
        if abs(zv) >= 1: side = 1 if zv > 0 else -1; tr.append(side * ret[d] - 2 * R5.COST); nxt = d + pd.Timedelta(days=h)
    return np.array(tr)


def main():
    S = sys.argv[1]; out = []
    for asset, f, sym in (("BTC", "bitcoin-etf-flows.html", "BTCUSDT"), ("ETH", "ethereum-etf-flows.html", "ETHUSDT")):
        fl = R5.flows(os.path.join(S, f)); px = R5.opens(sym)
        for win in (1, 5, 20):
            s = fl.rolling(win).sum(); zf = ((s - s.rolling(60).mean().shift(1)) / s.rolling(60).std().shift(1))
            # price momentum known at the same moment as the flow signal (open of D+2): return over the previous `win` flow days ending at D+1 close ~ open D+2
            p_now = px.reindex(fl.index + pd.Timedelta(days=2)).values; p_then = px.reindex(fl.index.to_series().shift(win - 1).fillna(fl.index[0]).values + pd.Timedelta(days=1)).values
            m = pd.Series(np.log(p_now / p_then), index=fl.index); zm = (m - m.rolling(60).mean().shift(1)) / m.rolling(60).std().shift(1)
            both = pd.DataFrame(dict(zf=zf, zm=zm)).dropna(); rho = float(both.corr().iloc[0, 1])
            for h in (10, 20, 40, 60):
                ent = both.index + pd.Timedelta(days=2); ex = ent + pd.Timedelta(days=h); ok = ent.isin(px.index) & ex.isin(px.index); b = both[ok]
                ret = pd.Series(px.reindex(ex[ok]).values / px.reindex(ent[ok]).values - 1, index=b.index)
                f_ = rule(b.zf, ret, h); m_ = rule(b.zm, ret, h); dis = b[np.sign(b.zf) != np.sign(b.zm)]; d_ = rule(dis.zf, ret, h)
                out.append(dict(asset=asset, window=win, hold=h, corr_flow_momentum=round(rho, 2), flow_rule_mean_pct=round(float(f_.mean() * 100), 2) if len(f_) else None, flow_n=len(f_),
                                momentum_rule_mean_pct=round(float(m_.mean() * 100), 2) if len(m_) else None, momentum_n=len(m_),
                                flow_when_disagree_mean_pct=round(float(d_.mean() * 100), 2) if len(d_) else None, disagree_n=len(d_)))
                print(out[-1], flush=True)
    json.dump(dict(label="post-hoc diagnostic", cells=out), open(os.path.join(HERE, "momentum_control.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
