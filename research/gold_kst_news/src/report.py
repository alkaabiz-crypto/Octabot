"""Apply PROTOCOL.md's choice rule to reports/grid.json (+ news_direction.json if present); write reports/RESULTS.md."""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REP = os.path.join(ROOT, "reports")
NEWS = {"NONE": "no news rule", "BLOCK": "no entry 2 h before to 1 h after news",
        "BLOCK_FLAT": "no entry 2 h before to 1 h after news, close 30 min before news",
        "BLOCK_24H": "no entry in the 24 h before news"}


def describe(k):
    p = dict(x.split("=") for x in k.split("|"))
    parts = []
    parts.append("no hard stop" if p["stop"] == "0" else f"stop {p['stop']}×ATR")
    parts.append("no trailing stop" if p["trail"] == "0" else f"trailing {p['trail']}×ATR")
    if p["be"] == "1":
        parts.append("breakeven after +2×ATR")
    if p["time"] != "0":
        parts.append(f"time stop {p['time']} h")
    if p["lose"] != "0":
        parts.append(f"exit if losing after {p['lose']} h")
    parts.append(NEWS[p["news"]])
    return ", ".join(parts)


def eligible(r):
    f = r["fit"]
    return f["trades"] >= 150 and f.get("expectancy_stress_r", -1) > 0 and "z" in f


def chosen(res):
    el = {k: r for k, r in res.items() if eligible(r)}
    return max(el, key=lambda k: el[k]["fit"]["z"]) if el else None


def row(name, k, r):
    f, t = r["fit"], r["test"]
    return (f"| {name} | {describe(k)} | {f['trades']}, {f['win_rate_pct']:.0f}%, {f['expectancy_r']:+.3f}R, "
            f"{f['total_r']:+.0f}R, DD {f['max_drawdown_r']:.0f}R, z {f['z']:+.2f} | {t['trades']}, {t['win_rate_pct']:.0f}%, "
            f"{t['expectancy_r']:+.3f}R (stress {t['expectancy_stress_r']:+.3f}), {t['total_r']:+.0f}R, DD {t['max_drawdown_r']:.0f}R, "
            f"z {t['z']:+.2f} |")


def main():
    res = json.load(open(os.path.join(REP, "grid.json")))["results"]
    base_k = "stop=0|trail=0|be=0|time=0|lose=0|news=NONE"
    ck = chosen(res)
    el = [k for k in res if eligible(res[k])]
    prof = max(el, key=lambda k: res[k]["fit"]["total_r"]) if el else None
    lines = ["# Results: gold KST + session VWAP exits and news rules", "",
             f"{len(res)} combinations. Fit 2020-07 to 2024-12, test 2025-01 to the latest candle. "
             "Legs: count, win rate, expectancy, total, worst drawdown, z against random entries with the same exits.", "",
             "| | Rules | Fit | Test |", "|---|---|---|---|", row("Original rule", base_k, res[base_k])]
    if ck:
        lines.append(row("**Chosen (highest fit z)**", ck, res[ck]))
    if prof and prof != ck:
        lines.append(row("Most profitable in fit", prof, res[prof]))
    verdict = None
    if ck:
        t, bt = res[ck]["test"], res[base_k]["test"]
        ok = t.get("expectancy_stress_r", -1) > 0 and t.get("z", 0) >= 1.645 and t["max_drawdown_r"] < bt["max_drawdown_r"]
        verdict = ok
        lines += ["", f"Verdict on the pre-registered rule: **{'improvement confirmed' if ok else 'not confirmed'}** "
                  f"(needs test expectancy > 0 at stress cost, z ≥ 1.645, and a smaller worst drawdown than the original rule's {bt['max_drawdown_r']:.1f}R)."]
    # top 20 fit by z: how do they do in test?
    top = sorted(el, key=lambda k: -res[k]["fit"]["z"])[:20]
    if top:
        tz = [res[k]["test"].get("z", 0) for k in top]
        te = [res[k]["test"].get("expectancy_r", 0) for k in top]
        lines += ["", f"The 20 best fit combinations, in the test period: median z {statistics.median(tz):+.2f}, "
                  f"median expectancy {statistics.median(te):+.3f}R, {sum(e > 0 for e in te)} of 20 profitable."]
    # marginal effect of each option (average over all other options)
    lines += ["", "## What each option does on average", "",
              "Each value's average over every combination of the other options. z is against random entries with the same rules.", "",
              "| Option | Value | Fit z | Fit expectancy | Test z | Test expectancy | Test worst drawdown |", "|---|---|---|---|---|---|---|"]
    for opt in ("stop", "trail", "be", "time", "lose", "news"):
        vals = sorted({dict(x.split("=") for x in k.split("|"))[opt] for k in res})
        for v in vals:
            ks = [k for k in res if dict(x.split("=") for x in k.split("|"))[opt] == v and "z" in res[k]["fit"] and "z" in res[k]["test"]]
            if not ks:
                continue
            m = lambda p, f: statistics.mean(res[k][p][f] for k in ks)  # noqa: E731
            vv = NEWS.get(v, v) if opt == "news" else v
            lines.append(f"| {opt} | {vv} | {m('fit', 'z'):+.2f} | {m('fit', 'expectancy_r'):+.3f}R | {m('test', 'z'):+.2f} | "
                         f"{m('test', 'expectancy_r'):+.3f}R | {m('test', 'max_drawdown_r'):.1f}R |")
    nd = os.path.join(REP, "news_direction.json")
    if os.path.exists(nd):
        nr = json.load(open(nd))["results"]
        lines += ["", "## Does the first 15 minutes after news tell the direction?", "",
                  "Enter in (follow) or against (fade) the first 15-minute move after the release, exit 4 h after the release, "
                  "2×ATR stop. Compared with the same clock time on normal days.", "",
                  "| Event | Mode | Fit: events, win, E, z | Test: events, win, E, z | Gold's 4 h move after the event vs normal days |",
                  "|---|---|---|---|---|"]
        for k, r in nr.items():
            ev, mode = k.split("|")
            f, t = r["fit"], r["test"]
            if "z" not in f or "z" not in t:
                continue
            mv = f"{t['median_4h_move_atr']:.1f}× ATR vs {t['control_median_4h_move_atr']:.1f}× ATR" if t.get("median_4h_move_atr") else ""
            lines.append(f"| {ev} | {mode} | {f['events']}, {f['win_rate_pct']:.0f}%, {f['expectancy_r']:+.3f}R, {f['z']:+.2f} | "
                         f"{t['events']}, {t['win_rate_pct']:.0f}%, {t['expectancy_r']:+.3f}R, {t['z']:+.2f} | {mv} |")
    open(os.path.join(REP, "RESULTS.md"), "w").write("\n".join(lines) + "\n")
    json.dump({"chosen": ck, "verdict": verdict, "most_profitable_fit": prof}, open(os.path.join(REP, "summary.json"), "w"), indent=1)
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
