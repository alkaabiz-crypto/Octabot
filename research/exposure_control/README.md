# Exposure-matched random-timing control: results

The rules were fixed in `PREREGISTRATION.md` (commit `cd7fe265`) before running. Each rule's daily position series was shifted to **1,000 random dates**. That keeps exactly the same time invested and holding pattern, so the only thing that changes is *when* it is invested.

## Verdict: all three primary tests FAIL the strict 95% bar, but narrowly

| Rule (forward test it backs) | Rule return | Random median | Random 95th pct | Rule percentile | Time invested | Buy & hold | Verdict |
|---|---|---|---|---|---|---|---|
| **TREND_ENS BTC** (trend bot) | **+4.9%** | −17.0% | +16.5% | **89.6** | 45% | −21.0% | FAIL |
| **TREND_ENS ETH** (trend bot) | **+40.9%** | −22.2% | +45.9% | **94.1** | 43% | −36.8% | FAIL |
| **Gold MOM50 + ATR, 2× spread** (gold MOM50) | **+49.0%** | +15.2% | +51.0% | **93.6** | 61% | +32.0% | FAIL |
| *Information only:* SMA50 BTC | +28.6% | −19.4% | +31.3% | 94.3 | 47% | | — |
| *Information only:* SMA50 ETH | +151.2% | −32.2% | +128.8% | 95.7 | 45% | | (would pass) |
| *Information only:* TREND_ENS_VOL BTC / ETH | +6.0% / +32.5% | | | 89.7 / 90.2 | | | — |

For comparison, **gold Asia sat at the 57th percentile** (`../session_study`), which is plain chance.

## What this means

- **The trend and momentum rules beat about 90–94% of random timings** with the same exposure. That is much better than chance, but **not proven** at the pre-registered 95% bar.
  - With only about 22 months of data and 17 gold trades, this test has low power. A real but modest edge would often land at exactly this level.
- **They are "promising, not proven".** The forward paper tests are the right next step, and they keep running unchanged. No real money should go on them yet.
- **SMA50 ETH passing is not a signal to switch.** It was information only, chosen with hindsight, and it had a −51% drop in the 2022–26 test.
- **The ranking of ideas changes:**
  - Gold MOM50 and the trend bot stay as the leading candidates.
  - **Gold Asia drops to the bottom.** Its timing showed no edge.

## Erratum found during this check

`../daily_signal_dca/from_2025/run.py` built the TREND_ENS votes as an object-dtype series.
- **Effect:** `numpy.nan_to_num` does not convert NaN in object arrays, so the warm-up NaNs carried through. The return of the first entry day was dropped, because a NaN cost made that day NaN and `cumprod` skipped it.
- **Size:** BTC TREND_ENS full-period return is **+4.9%, not +1.2%**. ETH is unchanged at +40.9%.
- **What this study does:** it fills NaN with 0 before every run.
- **The forward bot** (`forward/forward.py`) calculates its votes differently and is **not** affected.

Files: `study.py`, `results/results.json`.
