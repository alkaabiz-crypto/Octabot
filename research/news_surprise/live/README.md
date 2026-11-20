# Trading the news surprise: forward paper test

This tests the one news edge the studies found: the actual number versus the forecast predicts the direction of the first second or so after the US jobs report and CPI. The question here is whether a **free, realistic setup** can capture it. **No orders are ever placed.**

1. **`capture.py`** runs at each release, started by a scheduled task about 18 minutes before.
   - It polls the official BLS data API about once a second from 15 seconds before 08:30:00 New York time, and records the exact moment the new figure first appears.
   - It works out the surprise immediately against the forecast logged by the daily briefing, using the previous month's figure cached before the release, as a live bot would.
   - Output goes to `../data/live_captures.csv`.
2. **`evaluate.py`** runs daily, once Exness's tick archive has the day.
   - It scores a paper trade on gold, EUR/USD, GBP/USD and USD/JPY in the textbook direction.
   - Entry is at the first Exness quote 0.5 seconds after the number was seen; exit is 15 minutes after the release. It also records the theoretical 1-second entry for comparison.
   - Output goes to `../data/live_ledger.csv`, which is append-only.

The first captures are the jobs report on 2026-12-04 and CPI on 2026-12-10.

**API key.** Requests from this cloud machine without a key share an exhausted daily limit. A free personal BLS key (data.bls.gov/registrationEngine) gives 500 requests a day; set it as `BLS_API_KEY` in the environment's settings. BLS takes the key in the request body, so the secure credential form cannot add it.

**Caveats.**
- A cloud session is not a low-latency setup. The BLS API may also publish later than the BLS website and the professional newswires.
- The clock offset is estimated from the server's `Date` header, which is only accurate to about a second.

The measured "seconds until seen" is the real test. In the 2016–2026 data, entries from 5 seconds onward had no edge.
