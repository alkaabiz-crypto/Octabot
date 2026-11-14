# Indicator information test, batch IND-002: results

Pre-registered in `PREREG.md` (commit `fa88378e`). Script `run_ind2.py` (a module-name clash was fixed before results); output `results.json`.

**270 TEST tests; 0 significant after Benjamini–Hochberg. Every indicator: NONE.**

| ID | Indicator | Verdict | Note |
|---|---|---|---|
| IND-019 | HMM regime probability (daily) | NONE | Positive in every period only for oil at 5 days, not significant |
| IND-022 | Aroon oscillator | NONE | contrarian at 1–4 h on BTC and EUR/USD |
| IND-023 | Vortex | NONE | contrarian at short horizons in 4 markets |
| IND-024 | TRIX | NONE | contrarian at short horizons |
| IND-025 | KAMA slope | NONE | |
| IND-026 | Williams Alligator | NONE | |
| IND-027 | Hull MA slope | NONE | |
| IND-028 | Keltner position | NONE | |
| IND-029 | Heikin-Ashi colour run | NONE | |
| IND-030 | Awesome Oscillator | NONE | |
| IND-031 | Ultimate Oscillator | NONE | |
| IND-032 | Rate of change (12) | NONE | |
| IND-033 | Fisher transform | NONE | |
| IND-034 | Elder ray | NONE | |

**Reading.** As in batch 001, no indicator carries reliable directional information at 1 h to 5 d in its usual (trend-following) reading. Many lean slightly contrarian at 1–4 hours: the weak short-horizon reversal already shown in THE-017 not to survive a matched test, and far below costs.
