"""Missed-run watchdog (task 3 of the 2026-11-14 list). Read-only. Checks, from the committed records alone, that every daily
scheduled run happened and succeeded within the last 26 hours. Exit code 1 and a MISSED/FAILED line per problem.
usage: python3 -I research/ops/watchdog.py
"""
import csv, os, re, sys, time, calendar

R = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAX_AGE_H = 26; now = time.time(); problems, ok = [], []
utc = lambda s: calendar.timegm(time.strptime(s, "%Y-%m-%d %H:%M"))


def age_h(t): return (now - t) / 3600


# 1. daily paper-test run: last row of research/ops/run_log.csv
rows = list(csv.DictReader(open(os.path.join(R, "ops", "run_log.csv"))))
sched = [r for r in rows if r.get("invocation") == "scheduled"]
if not sched: problems.append("MISSED daily paper run: no scheduled run recorded")
else:
    last = sched[-1]; t = utc(last["run_utc"][:16])
    if age_h(t) > MAX_AGE_H: problems.append(f"MISSED daily paper run: last scheduled run {last['run_utc']} ({age_h(t):.0f} h ago)")
    elif last["result"] != "SUCCESS": problems.append(f"FAILED daily paper run {last['run_utc']}: {last.get('failures', '')}")
    else: ok.append(f"daily paper run OK ({last['run_utc']})")

# 2-3. forward reports: timestamp in the first line "(... YYYY-MM-DD HH:MM UTC)"
for name, path in (("Coinbase-premium forward (STR-008)", "new_discovery/forward_h4/REPORT.md"), ("STR-023 forward", "new_discovery/forward_str023/REPORT.md")):
    p = os.path.join(R, path)
    if not os.path.exists(p): problems.append(f"MISSED {name}: no report"); continue
    m = re.search(r"\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC\)", open(p).readline())
    if not m: problems.append(f"FAILED {name}: report has no timestamp"); continue
    t = utc(m.group(1))
    if age_h(t) > MAX_AGE_H: problems.append(f"MISSED {name}: last report {m.group(1)} ({age_h(t):.0f} h ago)")
    else: ok.append(f"{name} OK ({m.group(1)})")
    alert = os.path.join(os.path.dirname(p), "RUN_ALERT.md")
    if os.path.exists(alert): problems.append(f"FAILED {name}: {open(alert).read().strip()}")

print("\n".join(ok + problems) if (ok or problems) else "nothing to check")
print("WATCHDOG:", "ALL OK" if not problems else f"{len(problems)} PROBLEM(S)")
sys.exit(1 if problems else 0)
