# Forward evaluation

This folder holds the code that will judge every forward paper test. It was written and frozen on 2026-11-12, before any forward trade existed, so the pass/fail rules cannot be adjusted after seeing results.

## Files

- **`evaluate.py`** reads the forward ledgers unchanged and applies `../FORWARD_EVALUATION.md`, plus Batch 2's pre-registration and Amendment 1. It writes `EVALUATION.md` and `results/evaluation.json`.
- **`archive_prices.py`** keeps an append-only, hourly archive of Hyperliquid 1-minute candles for xyz:GOLD and xyz:CL. Hyperliquid serves only the most recent ≈ 3.5 days, but the random-timing benchmark needs the whole forward period.
  - If the feed later reports a different value for an archived candle, that is logged in `prices/revisions.csv` and the archived candle is kept.
  - Missing stretches are logged in `prices/gaps.csv`.
  - Binance prices are re-fetched at evaluation time and never stored, because of their licence.
- **`selftest.py` / `selftest_extra.py`** run checks on synthetic data only (see `../FORWARD_EVALUATION.md`).
- **`EVAL_MANIFEST.sha256` / `verify_eval_freeze.py`** hold the SHA-256 fingerprints of the frozen evaluation files and check them every hour.

## Why it is blind

A test that is not yet due shows only its progress count. Watching running p-values and stopping when one looks good would inflate false passes, so the evaluator never prints them.
