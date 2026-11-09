"""STAGE 2 - the final test, run ONCE.  Usage: python src/run_final.py <sha256 of LOCKED_selection.json>

Refuses to run if the lock file does not match the hash, or if a final result already exists. Applies the locked
candidates (and the textbook candidates) to trades entered from final_start to DATA_END, then applies the
pre-registered pass rule using the walk-forward numbers from stage 1 and the final-test numbers from this run.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import protocol as P  # noqa: E402
import stats  # noqa: E402
import study  # noqa: E402


def cand_from_key(approach, key):
    for c in P.candidates(approach):
        if study.cand_key(c) == key:
            return c
    raise KeyError(key)


def passes(wf, fin):
    """Pre-registered rule. Returns (passed, list of failed criteria)."""
    R, failed = P.PASS, []

    def need(ok, text):
        if not ok:
            failed.append(text)
    need(wf.get("trades", 0) >= R["wf_min_trades"], f"walk-forward trades < {R['wf_min_trades']}")
    need((wf.get("expectancy_r") or -1) > 0, "walk-forward expectancy <= 0")
    need((wf.get("t_stat") or -9) >= R["wf_min_t"], f"walk-forward t < {R['wf_min_t']}")
    need((wf.get("profit_factor") or 0) >= R["wf_min_pf"], f"walk-forward profit factor < {R['wf_min_pf']}")
    need((wf.get("positive_fold_share") or 0) >= R["wf_min_pos_fold_share"], "positive in < 60% of folds")
    need((wf.get("expectancy_stress") or -1) > 0, "walk-forward expectancy <= 0 at stress cost")
    need(wf.get("p_random") is not None and wf["p_random"] <= R["wf_max_p_random"], "not better than random entry (p > 0.05)")
    need(fin.get("trades", 0) >= R["final_min_trades"], f"final-test trades < {R['final_min_trades']}")
    need((fin.get("expectancy_r") or -1) > 0, "final-test expectancy <= 0")
    need((fin.get("profit_factor") or 0) >= R["final_min_pf"], f"final-test profit factor < {R['final_min_pf']}")
    return (not failed), failed


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    final_path = os.path.join(study.REPORTS_DIR, "final.json")
    if os.path.exists(final_path):
        raise SystemExit("final.json already exists: the final test is evaluated once and is not re-run.")
    with open(os.path.join(study.REPORTS_DIR, "LOCKED_selection.json")) as f:
        blob = f.read()
    sha = hashlib.sha256(blob.encode()).hexdigest()
    if sha != sys.argv[1]:
        raise SystemExit(f"LOCK MISMATCH: file hash {sha} differs from the hash given. Refusing to run.")
    locks = json.loads(blob)
    with open(os.path.join(study.REPORTS_DIR, "walkforward.json")) as f:
        wf_all = json.load(f)
    out = {}
    for asset, cfg in P.ASSETS.items():
        ctx = study.Context(asset, end_before=P.DATA_END)
        f0, f1 = cfg["final_start"], P.DATA_END
        res = dict(meta=dict(final_test=[study.fmt(f0), study.fmt(f1)], last_bar=study.fmt(ctx.market.h1.t[-1]),
                             final_context=study.period_context(ctx, f0, f1), today_spread_pct=ctx.today_spread * 100),
                   strategies={})
        for approach in P.APPROACHES:
            for dname in P.DIRECTIONS:
                for exit_rule in P.EXITS:
                    key = study.strategy_key(approach, dname, exit_rule)
                    row = {}
                    for label, cand in (("selected", locks[asset][key]), ("textbook", P.textbook_candidate(approach))):
                        ck = study.cand_key(cand)
                        tr = study.between(ctx.trades(approach, dname, exit_rule, cand_from_key(approach, ck)), f0, f1)
                        m = study.evaluate(ctx, tr, dname, exit_rule, f0, f1, key + "|final_" + label)
                        m["candidate"] = ck
                        row[label] = m
                        study.write_trades(os.path.join(study.LOGS_DIR, "final", f"{asset}_{approach}_{dname}_{exit_rule}_{label}.csv"), ctx, tr)
                    res["strategies"][key] = row
                    print(f"{asset} {key}: selected {row['selected']['candidate']} n={row['selected']['trades']} "
                          f"E={row['selected'].get('expectancy_r')} | textbook n={row['textbook']['trades']} E={row['textbook'].get('expectancy_r')}", flush=True)
        out[asset] = res
    # Holm across the 24 selected strategies (and separately across the 24 textbook ones), per period
    for label, wf_label in (("selected", "walkforward_selected"), ("textbook", "walkforward_textbook")):
        fin_p = {(a, k): out[a]["strategies"][k][label].get("p_one_sided") for a in out for k in out[a]["strategies"]}
        wf_p = {(a, k): wf_all[a]["strategies"][k][wf_label].get("p_one_sided") for a in out for k in out[a]["strategies"]}
        fin_adj, wf_adj = stats.holm(fin_p), stats.holm(wf_p)
        for (a, k) in fin_p:
            row = out[a]["strategies"][k][label]
            row["p_holm_final"] = fin_adj[(a, k)]
            row["p_holm_walkforward"] = wf_adj[(a, k)]
            ok, failed = passes(wf_all[a]["strategies"][k][wf_label], row)
            row["reliable"] = ok
            row["failed_criteria"] = failed
    with open(final_path, "w") as f:
        json.dump(out, f, indent=1)
    print("final test written to", final_path)


if __name__ == "__main__":
    main()
