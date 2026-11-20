# Capture script fix note (2026-11-14)

**Found in a dry run before the first live capture (NFP 2026-12-04).** The hash-locked `capture.py` could never read a BLS response.

1. **The main bug.** It runs curl with `text=True`, which converts every `\r\n` to `\n`. It then splits the headers from the body on `"\r\n\r\n"`, which can therefore never match. The body is always empty, the JSON parse always fails, and every capture would have ended as `timeout`.
2. **An environment quirk.** Behind this container's HTTPS proxy, `curl -D -` also prints the proxy's "200 Connection Established" header block first.

**Evidence.** Dry run on 2026-11-14:
- the original's `bls()` returned no JSON;
- `capture_fixed.py` returned `REQUEST_SUCCEEDED`, with the latest NFP (2026-M10, 159,293), unemployment (4.1%) and core CPI index (339.9).

**What was done.**
- `capture.py` is **unchanged**. Its hash, which `daily_run.py` checks through `FORWARD_TEST_PLAN.md`, stays valid.
- `capture_fixed.py` is a copy with **only** these changes (see `diff capture.py capture_fixed.py`):
  - `--suppress-connect-headers` added to the curl call;
  - the header/body split made line-ending safe;
  - a one-line docstring note.
- Polling, timing, series, forecast and scoring logic are identical.
- The scheduled NFP (2026-12-04) and CPI (2026-12-10) capture tasks run `capture_fixed.py`.

This is a disclosed amendment to how the forward test's captures are made. It is not a change to its rules or decision criteria.
