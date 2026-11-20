# Batch 2 implementation notes (code fixes; the pre-registered rules are unchanged)

These fixes make the code match `PREREGISTRATION.md`. None changes a hypothesis, threshold, holding time, cost or decision rule. All were made **before E** (2026-11-14 00:00 UTC), so no forward data had been processed when they were made.

| Date (UTC) | Fix | Effect |
|---|---|---|
| 2026-11-12 19:3x | `E_MS` constant was 2026-11-19; corrected to **2026-11-14 00:00**, the first 00:00 at least 24 h after T0, as the pre-registration defines | Only the forward start; the development run does not use E |
| 2026-11-12 19:5x | `deribit_quarterlies`: Deribit's `get_instruments(expired=true)` lists only contracts expired in the last day, so every archived 2025–2026 quarterly was missing from H2's basis history. Archived quarterlies are now looked up by name (last Friday of Mar/Jun/Sep/Dec) through `get_instrument`. | H2 (BTC, ETH) development results are recomputed. The first run only had the 4 live contracts (7 BTC trades), so it is superseded. |
