# Category protocol: Signals (SIG)

**Definition.** Trade calls made by someone else, for example the SignalPro app: an entry, a stop and targets that we did not design and cannot inspect.

**Question.** Are the calls profitable, and are the provider's reported results accurate?

## Test: a prospective audit

1. **Capture.**
   - **PROSPECTIVE:** a screenshot taken when the signal is posted and nothing has been hit yet ("Trade Active, 0/3"). Only these count towards the verdict.
   - **RETROSPECTIVE:** the outcome was already visible. Logged and scored, but reported separately, because of selection bias.
2. **Logging.** The signal ID, the posting-time window (the app rounds "N h ago" down), all levels, and the screenshot's SHA-256. Logged signals are never edited.
3. **Scoring** with the frozen SignalPro tracker's rules: stop first within a candle; three managements (full position to TP3; thirds; thirds with the stop moved to breakeven).
   - **On the broker's own prices** (Exness 1-minute bars, available about a day later).
   - Hyperliquid prices are used only as a quick check, and are flagged when the feed gap exceeds the stop.
4. **Benchmark.** The same stops and targets entered at random times in the same session and direction.
5. **Claim accuracy.** Compare the app's displayed status (TP hit, stop hit) with what the broker's prices show. Count contradictions.

## Verdicts (needs ≥ 50 prospective signals per candidate)

| Verdict | Conditions |
|---|---|
| **PROFITABLE** | Mean R > 0 under the app's own management, above the random benchmark at p ≤ 0.05 |
| **UNPROFITABLE** | Otherwise |
| **NOT YET DECIDABLE** | Fewer than 50 prospective signals |

**Separate flag:** CLAIMS ACCURATE / INACCURATE.
