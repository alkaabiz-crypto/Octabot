"""STAGE 1 - walk-forward on the development zone only, then lock the final-test parameter choices.

The loader is given ``end_before = final_start``, so no candle of the final test period is ever in memory.
Writes reports/walkforward.json, logs/walkforward/*.csv and reports/LOCKED_selection.json (+ its SHA-256).
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protocol as P  # noqa: E402
import study  # noqa: E402


def run_asset(asset):
    cfg = P.ASSETS[asset]
    ctx = study.Context(asset, end_before=cfg["final_start"])
    folds = P.folds(asset)
    wf0, wf1 = folds[0][1], folds[-1][2]
    out = dict(meta=dict(first_bar=study.fmt(ctx.market.h1.t[0]), last_bar_loaded=study.fmt(ctx.market.h1.t[-1]),
                         bars_loaded=len(ctx.market.h1), development_start=study.fmt(cfg["dev_start"]),
                         walkforward=[study.fmt(wf0), study.fmt(wf1)], folds=[f[0] for f in folds],
                         today_spread_pct=ctx.today_spread * 100, walkforward_context=study.period_context(ctx, wf0, wf1)),
               strategies={})
    lock = {}
    for approach in P.APPROACHES:
        for dname in P.DIRECTIONS:
            for exit_rule in P.EXITS:
                key = study.strategy_key(approach, dname, exit_rule)
                stitched, chosen_per_trade, fold_rows = [], [], []
                for name, f0, f1 in folds:
                    cand, _ = study.select_candidate(ctx, approach, dname, exit_rule, f0)
                    tr = study.between(ctx.trades(approach, dname, exit_rule, cand), f0, f1)
                    rs = [ctx.r(t) for t in tr]
                    fold_rows.append(dict(fold=name, candidate=study.cand_key(cand), trades=len(tr),
                                          expectancy_r=(sum(rs) / len(rs)) if rs else None, total_r=sum(rs)))
                    stitched += tr
                    chosen_per_trade += [study.cand_key(cand)] * len(tr)
                sel = study.evaluate(ctx, stitched, dname, exit_rule, wf0, wf1, key + "|wf_selected")
                traded = [f for f in fold_rows if f["trades"]]
                sel["folds"] = fold_rows
                sel["positive_fold_share"] = (sum(f["expectancy_r"] > 0 for f in traded) / len(traded)) if traded else None
                tb_cand = P.textbook_candidate(approach)
                tb_trades = study.between(ctx.trades(approach, dname, exit_rule, tb_cand), wf0, wf1)
                tb = study.evaluate(ctx, tb_trades, dname, exit_rule, wf0, wf1, key + "|wf_textbook")
                tb_folds = []
                for name, f0, f1 in folds:
                    rs = [ctx.r(t) for t in study.between(tb_trades, f0, f1)]
                    tb_folds.append(dict(fold=name, trades=len(rs), expectancy_r=(sum(rs) / len(rs)) if rs else None))
                traded = [f for f in tb_folds if f["trades"]]
                tb["folds"] = tb_folds
                tb["positive_fold_share"] = (sum(f["expectancy_r"] > 0 for f in traded) / len(traded)) if traded else None
                final_cand, table = study.select_candidate(ctx, approach, dname, exit_rule, cfg["final_start"])
                lock[key] = final_cand
                out["strategies"][key] = dict(walkforward_selected=sel, walkforward_textbook=tb,
                                              final_candidate=study.cand_key(final_cand), development_candidates=table)
                base = os.path.join(study.LOGS_DIR, "walkforward", f"{asset}_{approach}_{dname}_{exit_rule}")
                study.write_trades(base + "_selected.csv", ctx, stitched, chosen_per_trade)
                study.write_trades(base + "_textbook.csv", ctx, tb_trades)
                print(f"{asset} {key}: selected n={sel['trades']} E={sel.get('expectancy_r')} | textbook n={tb['trades']} "
                      f"E={tb.get('expectancy_r')} | final candidate {study.cand_key(final_cand)}", flush=True)
    return out, lock


def main():
    os.makedirs(study.REPORTS_DIR, exist_ok=True)
    lock_path = os.path.join(study.REPORTS_DIR, "LOCKED_selection.json")
    if os.path.exists(os.path.join(study.REPORTS_DIR, "final.json")):
        raise SystemExit("final.json exists: the final test has been run. Stage 1 must not be re-run after it.")
    results, locks = {}, {}
    for asset in P.ASSETS:
        results[asset], locks[asset] = run_asset(asset)
    with open(os.path.join(study.REPORTS_DIR, "walkforward.json"), "w") as f:
        json.dump(results, f, indent=1)
    blob = json.dumps(locks, sort_keys=True, indent=1)
    with open(lock_path, "w") as f:
        f.write(blob)
    sha = hashlib.sha256(blob.encode()).hexdigest()
    with open(os.path.join(study.REPORTS_DIR, "LOCKED_selection.sha256"), "w") as f:
        f.write(sha + "\n")
    print("LOCKED selection SHA-256:", sha)


if __name__ == "__main__":
    main()
