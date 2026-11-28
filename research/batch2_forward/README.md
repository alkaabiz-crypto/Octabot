# Batch 2 forward paper test (run from this branch)

**Authorised by the user on 2026-11-16** ("Run the other session batch 2 i give u authorisation").

- **What this is:** a byte copy of `research/batch2/` from branch `claude/download-skill-27d08k` at commit a5c15a3c. That branch is not modified. `SOURCE_SHA256SUMS` lists the copied files' SHA-256 hashes, so any later change to the code is detectable.
- **Rules:** `PREREGISTRATION.md` with `AMENDMENT_1.md` / `AMENDMENT_2.md`, unchanged. The forward period is from 2026-11-14 00:00 UTC (E).
- **How it runs:** `forward.py` rebuilds every signal from fresh public data (Binance, Hyperliquid funding, Deribit futures and DVOL) on each run. It appends newly closed trades to `ledger.csv` and stops on any revision of a recorded trade.
  - The file says "run hourly". Because it rebuilds from E every time, a daily run records exactly the same trades, only later.
  - It is run daily by a scheduled task. Paper only, no orders.
- **Decisions:** none before each test's pre-registered evaluation date. That is the later of reaching its power target n_req and 6 months after E, capped at 24 months.
