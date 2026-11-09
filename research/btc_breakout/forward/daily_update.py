"""Daily wrapper for the Donchian 20 forward paper test (BINANCE PROXY, paper only).

This script never edits frozen strategy files (paper_trader.py, ../src/engine.py, ../src/protocol.py, FROZEN.json).

Each run does the following, in order:
  1. Checks that the git branch is up to date with the remote and that the parameter lock still matches.
  2. Snapshots the previously committed forward candles.
  3. Runs paper_trader.py, which uses closed candles only, replays deterministically and guards the ledgers.
  4. Data checks. If any check fails, the run stops, nothing is committed, and RUN_ALERT.md is written:
     - every 1H, 15m and 4H candle from forward start to the latest closed candle is present (contiguous);
     - every candle passes an OHLC sanity check;
     - previously committed candles are unchanged (no revised history);
     - the processed-candle watermark never moves backwards.
  5. Appends to run_log.csv: the previous and new watermark and the number of new 1H candles processed.
     Each candle is counted exactly once.
  6. Computes performance (win rate, profit factor, max drawdown, average win/loss R:R, cumulative return)
     and appends to DAILY_LOG.md.
  7. Commits, pushes, and confirms that the remote branch HEAD equals the local commit.

Exit code: 0 = success, 1 = stopped by a data or integrity check, 2 = git commit or push problem.
"""
import csv, datetime, gzip, io, json, os, statistics, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
BRANCH = "claude/download-skill-27d08k"
FWD = "research/btc_breakout/forward"
STEP = {"1h": 3600, "15m": 900, "4h": 14400}
ATTRIBUTION = ("\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n"
               "Claude-Session: https://claude.ai/code/session_011cwjyiPqBQSQrrDe4cprnA")


def git(*a, check=True):
    r = subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(a)} failed: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def stop(code, msg):
    now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    open(os.path.join(HERE, "RUN_ALERT.md"), "w").write(f"# RUN ALERT {now} UTC\n\n{msg}\n\nNothing was committed for this run.\n")
    print(f"STOPPED ({'data/integrity' if code == 1 else 'git'}): {msg}")
    sys.exit(code)


def read_candles_gz(data):
    rows = list(csv.reader(io.StringIO(gzip.decompress(data).decode())))[1:]
    return {r[0]: r[1:] for r in rows}


def committed_candles(tf):
    try:
        blob = subprocess.run(["git", "show", f"HEAD:{FWD}/candles_{tf}_forward.csv.gz"], cwd=REPO, capture_output=True, check=True).stdout
        return read_candles_gz(blob)
    except subprocess.CalledProcessError:
        return {}


def parse(s):
    return int(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp())


def main():
    # ---- 1. repository state
    git("fetch", "-q", "origin", BRANCH)
    if git("rev-parse", "--abbrev-ref", "HEAD") != BRANCH:
        git("checkout", BRANCH)
    git("pull", "-q", "--ff-only", "origin", BRANCH)
    if git("rev-parse", "HEAD") != git("rev-parse", f"origin/{BRANCH}"):
        stop(2, "local branch differs from remote after pull")
    frozen = json.load(open(os.path.join(HERE, "FROZEN.json")))
    fwd_start = frozen["config"]["forward_start"]
    prev = {tf: committed_candles(tf) for tf in STEP}
    log_path = os.path.join(HERE, "run_log.csv")
    log = list(csv.DictReader(open(log_path))) if os.path.exists(log_path) else []
    prev_wm = log[-1]["new_watermark_1h_close_utc"] if log else None

    # ---- 2-3. run the frozen paper trader
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "paper_trader.py")], cwd=REPO, capture_output=True, text=True)
    if r.returncode:
        stop(1, f"paper_trader.py failed: {(r.stdout + r.stderr).strip().splitlines()[-1]}")

    # ---- 4. data checks on the candles the trader actually used
    new = {tf: read_candles_gz(open(os.path.join(HERE, f"candles_{tf}_forward.csv.gz"), "rb").read()) for tf in STEP}
    for tf, rows in new.items():
        times = sorted(parse(t) for t in rows)
        fwd_times = [t for t in times if t >= fwd_start - 3 * 86400]
        gaps = [(a, b) for a, b in zip(fwd_times, fwd_times[1:]) if b - a != STEP[tf]]
        if gaps:
            a, b = gaps[0]
            stop(1, f"missing {tf} candles between {time.strftime('%Y-%m-%d %H:%M', time.gmtime(a))} and "
                    f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(b))} UTC ({len(gaps)} gap(s))")
        for t, v in rows.items():
            o, h, l, c, vol = map(float, v)
            if not (l <= min(o, c) and max(o, c) <= h and l > 0 and vol >= 0):
                stop(1, f"corrupted {tf} candle {t}: {v}")
        changed = [t for t, v in prev[tf].items() if t in rows and rows[t] != v]
        vanished = [t for t in prev[tf] if t not in rows]
        if changed or vanished:
            stop(1, f"previously recorded {tf} candles changed ({len(changed)}) or disappeared ({len(vanished)}), "
                    f"first: {(changed + vanished)[0]}")

    status = json.load(open(os.path.join(HERE, "status.json")))
    new_wm = status["last_closed_1h_candle_close_utc"]
    if prev_wm and parse(new_wm) < parse(prev_wm):
        stop(1, f"watermark moved backwards: {prev_wm} -> {new_wm}")
    first_close = fwd_start + 3600
    new_1h = 0 if parse(new_wm) < first_close else (
        (parse(new_wm) - max(parse(prev_wm), fwd_start)) // 3600 if prev_wm else (parse(new_wm) - fwd_start) // 3600)

    # ---- 5-6. run log + performance
    trades = list(csv.DictReader(open(os.path.join(HERE, "trades.csv")))) if os.path.exists(os.path.join(HERE, "trades.csv")) else []
    sigs = list(csv.DictReader(open(os.path.join(HERE, "signals.csv")))) if os.path.exists(os.path.join(HERE, "signals.csv")) else []
    R = [float(t["R_net_mid"]) for t in trades]
    wins, losses = [x for x in R if x > 0], [x for x in R if x <= 0]
    perf = dict(
        trades=len(R),
        win_rate_pct=round(len(wins) / len(R) * 100, 1) if R else None,
        profit_factor=round(sum(wins) / -sum(losses), 3) if losses and sum(losses) < 0 else None,
        avg_win_loss_rr=round(statistics.mean(wins) / -statistics.mean(losses), 2) if wins and losses and statistics.mean(losses) < 0 else None,
        expectancy_R=round(statistics.mean(R), 4) if R else None,
        cumulative_return_pct=status["return_pct_mid"],
        max_drawdown_pct=status["max_drawdown_pct_mid"],
        current_losing_streak=status["stats_net"]["mid"].get("current_losing_streak", 0))
    prev_trades = int(log[-1]["completed_trades"]) if log else 0
    prev_sigs = int(log[-1]["signals_total"]) if log else 0
    new_sig_rows = sigs[prev_sigs:] if len(sigs) >= prev_sigs else sigs
    now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
    row = dict(run_utc=now, previous_watermark_1h_close_utc=prev_wm or "", new_watermark_1h_close_utc=new_wm,
               new_1h_candles_processed=new_1h, completed_trades=len(trades), signals_total=len(sigs),
               open_position="yes" if status["open_position"] else "no", equity_usd_mid=status["equity_usd_mid"])
    write_header = not os.path.exists(log_path)
    with open(log_path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if write_header:
            w.writeheader()
        w.writerow(row)
    op = status["open_position"]
    closed_now = trades[prev_trades:]
    lines = [f"## {now} UTC - BINANCE PROXY (not Exness), paper only",
             f"- Candles: {new_1h} new 1H candle(s) processed ({prev_wm or 'start'} -> {new_wm}); data checks passed",
             f"- Progress: **{len(trades)} / 40 trades**" + (" (profitability is not assessed before 40 trades)" if len(trades) < 40 else ""),
             f"- New signals: {len(new_sig_rows)} (accepted {sum(s['status'] == 'ACCEPTED' for s in new_sig_rows)}, "
             f"rejected {sum(s['status'].startswith('REJECTED') for s in new_sig_rows)}, "
             f"pending {sum(s['status'].startswith('PENDING') for s in new_sig_rows)})",
             f"- Trades closed this run: " + (", ".join(f"#{t['trade_no']} {t['exit_reason']} {t['R_net_mid']}R" for t in closed_now) or "none"),
             f"- Open position: " + (f"LONG from {op['entry_price']} ({op['entry_utc']}), initial stop {op['initial_stop']}, "
                                    f"unrealized {op['unrealized_R_gross']}R gross" if op else "none"),
             f"- Performance (0.05% cost): win rate {perf['win_rate_pct']}%, PF {perf['profit_factor']}, avg win/loss {perf['avg_win_loss_rr']}, "
             f"expectancy {perf['expectancy_R']}R, cumulative return {perf['cumulative_return_pct']}%, max drawdown {perf['max_drawdown_pct']}%, "
             f"losing streak {perf['current_losing_streak']}", ""]
    with open(os.path.join(HERE, "DAILY_LOG.md"), "a") as f:
        if os.path.getsize(os.path.join(HERE, "DAILY_LOG.md")) == 0:
            f.write("# Daily log - Donchian 20 forward paper test (BINANCE PROXY, not Exness)\n\n")
        f.write("\n".join(lines) + "\n")
    alert = os.path.join(HERE, "RUN_ALERT.md")
    if os.path.exists(alert):
        os.remove(alert)  # the previous problem is cleared once a fully checked run succeeds

    # ---- 7. commit, push, verify
    git("add", "-A", FWD)
    git("commit", "-q", "-m", f"Forward paper test daily update {now[:10]}" + ATTRIBUTION)
    local = git("rev-parse", "HEAD")
    for attempt in range(5):
        p = subprocess.run(["git", "push", "-u", "origin", BRANCH], cwd=REPO, capture_output=True, text=True)
        if p.returncode == 0:
            break
        if "403" in p.stderr or "denied" in p.stderr.lower():
            stop(2, f"push rejected (authorization): {p.stderr.strip().splitlines()[-1]}")
        time.sleep(2 * 2 ** attempt)
    else:
        stop(2, f"push failed after retries: {p.stderr.strip().splitlines()[-1]}")
    git("fetch", "-q", "origin", BRANCH)
    remote = git("rev-parse", f"origin/{BRANCH}")
    if remote != local:
        stop(2, f"remote HEAD {remote[:8]} != local commit {local[:8]} after push")
    print("\n".join(lines[:-1]) + f"\n- Commit {local[:8]} pushed and verified on origin/{BRANCH}")


if __name__ == "__main__":
    main()
