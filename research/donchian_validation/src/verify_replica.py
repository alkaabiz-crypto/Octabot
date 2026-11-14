"""Check that the replica reproduces the frozen engine exactly (windows of the original study + continuous run)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
import frozen
import replica


def compare(eng_trades, rep_trades):
    if len(eng_trades) != len(rep_trades):
        return f"count {len(eng_trades)} vs {len(rep_trades)}"
    for a, b in zip(eng_trades, rep_trades):
        if (a["entry_time"], a["exit_time"], a["exit"], a["regime"]) != (b.entry_time, b.exit_time, b.reason, b.regime):
            return f"trade at {a['entry_time']} differs"
        if abs(a["R_gross"] - round(b.r_gross, 6)) > 1e-6 or abs(a["entry"] - round(b.entry, 2)) > 1e-9 or abs(a["risk"] - round(b.risk, 4)) > 1e-9:
            return f"values at {a['entry_time']} differ"
    return None


def main():
    lab = frozen.lab()
    frozen.engine_module()
    sys.path.insert(0, os.path.join(config.FROZEN_DIR, "src"))
    import protocol as fp  # frozen protocol (read-only)
    m = replica.Market(lab)
    results = {}
    for name, w0, w1 in list(fp.WINDOWS) + [fp.HOLDOUT, ("CONTINUOUS_2020_ON", config.ts(2020, 1), 10 ** 11)]:
        e = lab.simulate("1h", "M2_DONCHIAN20", 1, "TRAIL", w0, w1)
        r = m.run(w0, w1)
        diff = compare(e, r)
        results[name] = {"trades": len(e), "identical": diff is None, "difference": diff}
        print(name, len(e), "identical" if diff is None else diff)
    ok = all(v["identical"] for v in results.values())
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"), exist_ok=True)
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports", "replica_check.json"), "w") as f:
        json.dump({"all_identical": ok, "windows": results, "frozen_commit": config.FROZEN_COMMIT}, f, indent=1)
    if not ok:
        raise SystemExit("REPLICA DOES NOT MATCH THE FROZEN ENGINE")
    print("replica identical to frozen engine on every window")


if __name__ == "__main__":
    main()
