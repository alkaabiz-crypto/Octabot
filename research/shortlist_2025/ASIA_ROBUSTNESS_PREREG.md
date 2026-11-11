# Gold Asian-session robustness test: pre-registration

Committed **2026-11-11 06:10 UTC, before running.** Same data (Exness XAUUSDm ticks, 2025-01 to 2026-10), same execution model and same costs (real spread, 1× and 2×) as `screen.py` G_ASIA_long. Only the entry time changes. The aim is to check that the result is not an artefact of the price reopening after gold's daily break (20:58–22:02 server time, GMT+0).

| Variant | Entry | Exit |
|---|---|---|
| A (stricter) | first tick at or after **22:05 UTC**, Sunday–Thursday | first tick at or after 07:00 UTC next day |
| B (much later) | first tick at or after **23:00 UTC**, Sunday–Thursday | 07:00 UTC |

**Pass:** variant A has net > 0 at both 1× and 2× costs, with at least 100 trades. Variant B is reported for information only.

If A fails, the original G_ASIA_long result is treated as a break-reopening artefact and is **not** forward tested.
