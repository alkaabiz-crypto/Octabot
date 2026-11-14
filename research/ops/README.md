# Operations: daily scheduled run

`daily_run.py` is the only thing the daily scheduled task runs. It executes the existing paper-test, briefing and news-evaluation scripts unchanged, then checks the whole pipeline:
- hashes;
- script exit codes;
- data freshness;
- ledger consistency;
- regenerated outputs;
- git commit, push and remote-hash verification.

It records an explicit **SUCCESS** or **FAILED** for every run in `run_log.csv` (one row per run) and `LAST_RUN.md`.

Rows marked `manual` are not scheduled runs. They do not count as a successful scheduled execution, and neither does a by-hand hash check.

It changes no strategy, parameter, frozen file or past ledger row.
