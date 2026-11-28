"""Operational runner for the daily scheduled task (session B). It changes no strategy, parameter, frozen file or
past ledger row; it only runs the existing paper-test scripts and checks the whole pipeline. It records an explicit
SUCCESS or FAILED for the run in research/ops/run_log.csv and research/ops/LAST_RUN.md.

Checks, in order (a failed check marks the run FAILED; later steps still run where safe):
  1. hashes   - every SHA-256 in news_surprise/FREEZE_NOTE.md and news_surprise/FORWARD_TEST_PLAN.md, and each paper
                test's own FROZEN_SHA256. A mismatch stops all paper scripts (nothing is run or committed for them).
  2. execute  - each paper/briefing/evaluation script exits with code 0.
  3. fresh    - each paper test's last candle is recent enough (Exness archive lags about a day; gold/forex close
                at weekends): crypto <= 54 h old; gold <= 54 h, or <= 84 h when the run is on a Sunday or Monday (UTC).
  4. ledgers  - every trades CSV has the expected header, parses, has non-decreasing entry times, exit >= entry,
                numeric R values, no duplicate rows, and its row count equals the leg count in state.json.
  5. outputs  - STATUS.md (each test) and BRIEFING.md were regenerated today (UTC).
  6. git      - commit the ledgers and the run record, push, and verify the remote branch hash equals HEAD.
usage: python3 research/ops/daily_run.py [--scheduled] [--no-git]"""
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESEARCH = os.path.dirname(HERE)
REPO = os.path.dirname(RESEARCH)
BRANCH = "claude/dazzling-albattani-j6uys7"
LOG = os.path.join(HERE, "run_log.csv")
LAST = os.path.join(HERE, "LAST_RUN.md")
ATTR = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_011cwjyeVS9r4rqVErdhWS32"
PAPER = {  # test folder: (asset class for freshness, trades files and state.json leg keys)
    "pivot_reversal_paper": ("crypto", [("ledger/trades.csv", None)]),
    "eth_pivot_paper": ("crypto", [("ledger/trades.csv", None)]),
    "gold_kst_paper": ("gold", [("ledger/trades_CHOSEN_48H_TIME_STOP.csv", "CHOSEN_48H_TIME_STOP"), ("ledger/trades_ORIGINAL.csv", "ORIGINAL"),
                                ("ledger/trades_DOLLAR_FALLING.csv", "DOLLAR_FALLING"), ("ledger/trades_VOL_LOW.csv", "VOL_LOW")]),
    "gold_kst_risk_paper": ("gold", [("ledger/trades_STOP2ATR_CLOSE_BEFORE_NEWS.csv", "STOP2ATR_CLOSE_BEFORE_NEWS")]),
}
COMMIT_PATHS = ["research/pivot_reversal_paper/ledger", "research/eth_pivot_paper/ledger", "research/gold_kst_paper/ledger",
                "research/gold_kst_risk_paper/ledger", "research/news_surprise/data/consensus_log.csv",
                "research/news_surprise/data/live_ledger.csv", "research/news_surprise/data/forward_adp_contrarian.csv",
                "research/ops/run_log.csv", "research/ops/LAST_RUN.md"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sh(cmd, timeout=1800):
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)[-1500:]


def check_hashes():
    probs, n = [], 0
    t = open(os.path.join(RESEARCH, "news_surprise", "FREEZE_NOTE.md")).read()
    for p, h in re.findall(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", t):
        n += 1
        fp = os.path.join(RESEARCH, p)
        if not os.path.exists(fp) or sha(fp) != h:
            probs.append(f"FREEZE_NOTE: {p}")
    plan = open(os.path.join(RESEARCH, "news_surprise", "FORWARD_TEST_PLAN.md")).read()
    plan_hashes = set(re.findall(r"`([0-9a-f]{64})`", plan))
    locked = ["news_surprise/live/capture.py", "news_surprise/live/evaluate.py", "news_surprise/live/adp_contrarian_forward.py",
              "gold_kst_paper/src/briefing.py", "audit/src/seq_held.py"] + [f"{d}/src/{f}" for d in PAPER for f in ("config.py", "paper.py")]
    for p in locked:
        n += 1
        if sha(os.path.join(RESEARCH, p)) not in plan_hashes:
            probs.append(f"FORWARD_TEST_PLAN: {p}")
    for d in PAPER:
        spec = importlib.util.spec_from_file_location(f"cfg_{d}", os.path.join(RESEARCH, d, "src", "config.py"))
        c = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(c)
        for p, h in c.FROZEN_SHA256.items():
            n += 1
            if sha(os.path.join(RESEARCH, p)) != h:
                probs.append(f"{d} FROZEN_SHA256: {p}")
    return n, probs


def check_ledgers(d, files, state):
    probs = []
    for rel, key in files:
        path = os.path.join(RESEARCH, d, rel)
        if not os.path.exists(path):
            probs.append(f"{d}/{rel} missing")
            continue
        rows = list(csv.DictReader(open(path)))
        hdr = open(path).readline().strip().split(",")
        if "entry_utc" not in hdr or "exit_utc" not in hdr:
            probs.append(f"{d}/{rel} unexpected header")
        seen = set()
        last = ""
        for r in rows:
            k = tuple(r.values())
            if k in seen:
                probs.append(f"{d}/{rel} duplicate row {r.get('entry_utc')}")
            seen.add(k)
            if r["entry_utc"] < last:
                probs.append(f"{d}/{rel} entry times out of order at {r['entry_utc']}")
            last = r["entry_utc"]
            if r["exit_utc"] < r["entry_utc"]:
                probs.append(f"{d}/{rel} exit before entry at {r['entry_utc']}")
            try:
                float(r["r_primary"]), float(r["r_stress"])
            except (KeyError, ValueError):
                probs.append(f"{d}/{rel} non-numeric R at {r.get('entry_utc')}")
        legs = state.get("legs") if key is None else (state.get(key) or {}).get("legs")
        if legs is not None and legs != len(rows):
            probs.append(f"{d}/{rel}: {len(rows)} rows but state.json says {legs} legs")
    return probs


def main():
    scheduled = "--scheduled" in sys.argv
    no_git = "--no-git" in sys.argv
    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.strftime("%Y-%m-%d")
    rec = {"run_utc": now.strftime("%Y-%m-%d %H:%M:%S"), "invocation": "scheduled" if scheduled else "manual"}
    fails = []
    # 1. hashes
    n, probs = check_hashes()
    rec["hashes"] = f"{n} checked, {len(probs)} problems" + (": " + "; ".join(probs) if probs else "")
    hash_ok = not probs
    if not hash_ok:
        fails.append("hashes")
    # 2. execute
    ex = []
    if hash_ok:
        for d in PAPER:
            code, out = sh([sys.executable, f"research/{d}/src/paper.py"])
            ex.append(f"{d}={code}")
            if code != 0:
                fails.append(f"execute {d}: {out.strip().splitlines()[-1] if out.strip() else code}")
    code, out = sh([sys.executable, "research/gold_kst_paper/src/briefing.py"], 300)
    ex.append(f"briefing={code}")
    if code != 0:
        fails.append("execute briefing")
    if hash_ok:
        os.makedirs("/tmp/ticks", exist_ok=True)
        env_cmd = ["env", "TICK_WORK=/tmp/ticks", sys.executable, "research/news_surprise/live/evaluate.py"]
        code, out = sh(env_cmd)
        ex.append(f"news_evaluate={code}")
        if code != 0:
            fails.append("execute news evaluate.py")
        code, out = sh([sys.executable, "research/news_surprise/live/adp_contrarian_forward.py"])
        ex.append(f"adp_contrarian={code}")
        if code != 0:
            fails.append("execute adp_contrarian_forward.py")
    rec["execute"] = " ".join(ex) if ex else "skipped (hash problems)"
    # 3-5. freshness, ledgers, outputs
    fr, lg, outp = [], [], []
    wd = now.weekday()                          # Monday 0 ... Sunday 6
    for d, (cls, files) in PAPER.items():
        st_p = os.path.join(RESEARCH, d, "ledger", "state.json")
        state = json.load(open(st_p)) if os.path.exists(st_p) else {}
        lb = state.get("last_bar_utc")
        if lb:
            age = (now - datetime.datetime.strptime(lb, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc)).total_seconds() / 3600
            lim = 54 if cls == "crypto" or wd not in (6, 0) else 84
            fr.append(f"{d} {age:.0f}h/{lim}h")
            if age > lim:
                fails.append(f"stale data {d} ({lb}, {age:.0f} h old)")
        else:
            fails.append(f"no last_bar_utc for {d}")
        p = check_ledgers(d, files, state)
        lg += p
        status = os.path.join(RESEARCH, d, "ledger", "STATUS.md")
        if not os.path.exists(status) or f"Updated {today}" not in open(status).read():
            outp.append(f"{d}/ledger/STATUS.md not regenerated today")
    br = os.path.join(RESEARCH, "gold_kst_paper", "ledger", "BRIEFING.md")
    if not os.path.exists(br) or f"Generated {today}" not in open(br).read():
        outp.append("BRIEFING.md not regenerated today")
    rec["freshness"] = ", ".join(fr)
    rec["ledgers"] = "consistent" if not lg else "; ".join(lg)
    rec["outputs"] = "regenerated" if not outp else "; ".join(outp)
    fails += lg + outp

    def write(git_note):
        rec["git"] = git_note
        rec["result"] = "SUCCESS" if not fails else "FAILED"
        rec["failures"] = " | ".join(fails)
        new = not os.path.exists(LOG)
        fields = ["run_utc", "invocation", "result", "hashes", "execute", "freshness", "ledgers", "outputs", "git", "failures"]
        rows = list(csv.DictReader(open(LOG))) if not new else []
        if rows and rows[-1]["run_utc"] == rec["run_utc"]:
            rows[-1] = {k: rec.get(k, "") for k in fields}       # update this run's own row (two-phase commit)
        else:
            rows.append({k: rec.get(k, "") for k in fields})
        with open(LOG, "w", newline="") as f:
            w = csv.DictWriter(f, fields)
            w.writeheader()
            w.writerows(rows)
        L = [f"# Last daily run: **{rec['result']}**", "", f"- Run (UTC): {rec['run_utc']} ({rec['invocation']})"] + \
            [f"- {k}: {rec.get(k, '')}" for k in ("hashes", "execute", "freshness", "ledgers", "outputs", "git", "failures")]
        open(LAST, "w").write("\n".join(L) + "\n")

    if no_git:
        write("skipped (--no-git)")
        print(open(LAST).read())
        return 0 if not fails else 1
    # 6. git, two phases: commit ledgers + record, push, verify; then record the verified hash
    write("pending")
    paths = [p for p in COMMIT_PATHS if os.path.exists(os.path.join(REPO, p))]
    sh(["git", "add", "-f"] + paths)
    code, out = sh(["git", "commit", "-q", "-m", f"Paper tests and briefing: daily update {today} ({rec['result']} before push){ATTR}"])
    pushed, remote = False, ""
    for wait in (0, 2, 4, 8, 16):
        time.sleep(wait)
        c, o = sh(["git", "push", "-q", "-u", "origin", BRANCH], 300)
        if c == 0:
            pushed = True
            break
    head = sh(["git", "rev-parse", "HEAD"])[1].strip()
    if pushed:
        remote = sh(["git", "ls-remote", "origin", BRANCH])[1].split()[0] if sh(["git", "ls-remote", "origin", BRANCH])[0] == 0 else ""
    if not pushed or remote != head:
        fails.append("git push not verified")
        write(f"push failed or remote {remote[:8]} != HEAD {head[:8]}")
        print(open(LAST).read())
        return 1
    write(f"pushed and verified, data commit {head[:8]}")
    sh(["git", "add", "-f", "research/ops/run_log.csv", "research/ops/LAST_RUN.md"])
    sh(["git", "commit", "-q", "-m", f"Daily run record {today}: {rec['result']}{ATTR}"])
    ok2 = sh(["git", "push", "-q", "-u", "origin", BRANCH], 300)[0] == 0
    head2 = sh(["git", "rev-parse", "HEAD"])[1].strip()
    remote2 = sh(["git", "ls-remote", "origin", BRANCH])[1].split()[0] if ok2 else ""
    print(open(LAST).read())
    print("record commit", head2[:8], "remote", remote2[:8], "verified" if remote2 == head2 else "NOT VERIFIED")
    return 0 if (not fails and remote2 == head2) else 1


if __name__ == "__main__":
    sys.exit(main())
