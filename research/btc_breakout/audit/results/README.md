# Audit results index

Result files are never edited after they are written. This index says what each one is.

## A. Forward-test audits: actual forward paper-test results (BINANCE PROXY)

These files audit the real forward test in `research/btc_breakout/forward/`. Its window starts at 2026-11-09 07:00 UTC. Only files whose name contains `audit_forward_` or `AUDIT_forward_` belong here.

| File | Audited (UTC) | Last 1H close audited | Trades | Signals | CRITICAL / DISCREPANCY |
|---|---|---|---|---|---|
| `audit_forward_20261109T0733Z.json` | 2026-11-09 07:33 | 2026-11-09 07:00 | 0 | 0 | 0 / 0 |
| `AUDIT_forward_LATEST.md` | latest forward audit | | | | |

## B. Audit-tool validation on historical data: NOT forward-test results

**These files are not performance evidence and must never be quoted as forward results.**

They come from a dry-run copy of the paper trader, pointed at a past period (2026-09-01 to 2026-11-09). That period was already examined in earlier research. The copy was used only to show that the audit script reproduces real trades and catches tampering. The copy also contains one row that was tampered with on purpose (trade 1 `hold_hours`), so the reported DISCREPANCY is the expected result.

| File | Purpose | Outcome |
|---|---|---|
| `audit_DRYRUN_TEST_past_period_20261109T0731Z.json` | Audit-tool validation on a past-period dry run | 21/21 trades and 56/56 signals reproduced independently. 1 DISCREPANCY, which is the planted tamper. |
| `AUDIT_DRYRUN_TEST_past_period_LATEST.md` | Readable version of the line above | Same |

A second tamper test (a falsified exit price and a falsified signal status) was run on a throwaway copy. The audit flagged all of them. Its output files were deleted because they were only a test of the tool.
