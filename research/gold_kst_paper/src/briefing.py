"""Daily gold news briefing: high-impact events in the next 48 h (weekly calendar feed), gold's measured move size
after each event type (research/gold_kst_news/reports/news_direction.json) and the paper-test state.
usage: python src/briefing.py   ->  ledger/BRIEFING.md"""
import csv
import datetime
import json
import os
import subprocess
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RESEARCH = os.path.dirname(ROOT)
FEED = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
NY = zoneinfo.ZoneInfo("America/New_York")
HORIZON_H = 48


def kind_of(title):
    t = title.upper()
    if "CPI" in t:
        return "CPI"
    if "NON-FARM" in t or "NONFARM" in t:
        return "NFP"
    if "FOMC" in t or "FEDERAL FUNDS RATE" in t:
        return "FOMC"
    return None


CONSENSUS = os.path.join(RESEARCH, "news_surprise", "data", "consensus_log.csv")
FIELDS = ["event_utc", "country", "title", "forecast", "previous", "first_seen_utc", "last_seen_utc"]


def log_consensus(cal, now):
    """Append-only log of forecasts for high-impact USD events (a real consensus history for later tests).
    A forecast that changes between runs is kept as a new row."""
    rows = list(csv.DictReader(open(CONSENSUS))) if os.path.exists(CONSENSUS) else []
    last = {(r["event_utc"], r["title"]): r for r in rows}
    for e in cal:
        if e.get("country") != "USD" or e.get("impact") != "High":
            continue
        t = datetime.datetime.fromisoformat(e["date"]).astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
        key = (t, e["title"])
        r = last.get(key)
        if r and r["forecast"] == (e.get("forecast") or "") and r["previous"] == (e.get("previous") or ""):
            r["last_seen_utc"] = f"{now:%Y-%m-%d %H:%M}"
            continue
        new = {"event_utc": t, "country": "USD", "title": e["title"], "forecast": e.get("forecast") or "",
               "previous": e.get("previous") or "", "first_seen_utc": f"{now:%Y-%m-%d %H:%M}", "last_seen_utc": f"{now:%Y-%m-%d %H:%M}"}
        rows.append(new)
        last[key] = new
    os.makedirs(os.path.dirname(CONSENSUS), exist_ok=True)
    with open(CONSENSUS, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    cal = json.loads(subprocess.run(["curl", "-sSf", "-m", "30", FEED], check=True, capture_output=True, text=True).stdout)
    nd_path = os.path.join(RESEARCH, "gold_kst_news", "reports", "news_direction.json")
    moves = {}
    if os.path.exists(nd_path):
        nd = json.load(open(nd_path))["results"]
        for k in ("FOMC", "CPI", "NFP"):
            t = nd.get(f"{k}|follow", {}).get("test", {})
            if t.get("median_4h_move_atr"):
                moves[k] = (t["median_4h_move_atr"], t["control_median_4h_move_atr"])
    upcoming = []
    for e in cal:
        if e.get("impact") != "High":
            continue
        t = datetime.datetime.fromisoformat(e["date"]).astimezone(datetime.timezone.utc)
        if now - datetime.timedelta(hours=1) <= t <= now + datetime.timedelta(hours=HORIZON_H):
            upcoming.append((t, e))
    upcoming.sort(key=lambda x: x[0])
    log_consensus(cal, now)
    state_p = os.path.join(ROOT, "ledger", "state.json")
    state = json.load(open(state_p)) if os.path.exists(state_p) else {}
    L = ["# Gold daily briefing", "", f"Generated {now:%Y-%m-%d %H:%M} UTC. Events: weekly economic calendar (high impact only).", "",
         f"## High-impact events in the next {HORIZON_H} hours", ""]
    if upcoming:
        L += ["| UTC | New York | Currency | Event | Forecast | Previous | Gold's usual 4 h move after it |", "|---|---|---|---|---|---|---|"]
        for t, e in upcoming:
            k = kind_of(e["title"]) if e.get("country") == "USD" else None
            mv = f"{moves[k][0]:.1f}× ATR (normal day {moves[k][1]:.1f}×)" if k in moves else ("not measured" if e.get("country") == "USD" else "")
            L.append(f"| {t:%a %d %H:%M} | {t.astimezone(NY):%H:%M} | {e.get('country', '')} | {e['title']} | "
                     f"{e.get('forecast') or '-'} | {e.get('previous') or '-'} | {mv} |")
    else:
        L.append("None.")
    usd_soon = [t for t, e in upcoming if e.get("country") == "USD" and t - now <= datetime.timedelta(hours=2)]
    L += ["", "## What this means", "",
          "- **Direction:** the tests found no reliable way to tell from the news itself whether gold will rise or fall "
          "(first-15-minute follow/fade after FOMC, CPI and NFP: not confirmed on 2025-26). This briefing therefore does not "
          "forecast direction.",
          "- **Size:** after US high-impact news gold usually moves much more than normal, so stops get hit more often and spreads widen.",
          f"- **Right now:** {'a USD high-impact event is within 2 hours: the news-block rule would skip new entries.' if usd_soon else 'no USD high-impact event in the next 2 hours.'}",
          "", "## Paper test (KST + session VWAP BUY)", ""]
    if state:
        L.append(f"- Data to {state.get('last_bar_utc')} UTC; KST {'above' if state.get('kst_above_signal') else 'below'} its signal line.")
        for k, v in state.items():
            if isinstance(v, dict):
                L.append(f"- {k}: {v['legs']} closed legs; {'open BUY leg since ' + v['open_leg_since'] + ' UTC' if v.get('open_leg_since') else 'no open leg'}.")
    L += ["", "Research record, not financial advice."]
    open(os.path.join(ROOT, "ledger", "BRIEFING.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
