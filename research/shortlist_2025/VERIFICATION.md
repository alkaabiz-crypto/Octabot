# Verification log (05:11 UAE session, 2026-11-11)

| Check | Method | Result |
|---|---|---|
| Shortlist screen, gold MOM50 + ATR exits (1× costs) | Separate, simple re-implementation (`verify_independent.py`): pandas daily candles and return-based equity | +49.33% vs recorded +49.14%. The 0.19 pt gap comes from different cost accounting (returns vs units). **MATCH** within 1 pt |
| Shortlist screen, US oil intraday momentum (1× costs) | Separate tick lookups and New York time conversion | −14.79% vs −14.79%; 456 vs 456 trades. **EXACT MATCH** |
| Shortlist screen, BTC close above SMA50 (0.1% fee) | Separate loop on Binance daily candles | +28.55% vs +28.55%. **EXACT MATCH** |
| TREND_ENS forward bot, first decision (2026-11-10 close) | Fresh Binance download from 2025-01-01; SMA votes recomputed by hand | BTC: above SMA200 only, share 25%, fill 73,796.06 at the 2026-11-11 open, trade 680.74 USD, fee 0.6807. ETH: below all four averages, share 0%. **MATCH** with ledger |
| Donchian forward audit (`audit.py --label forward`, 01:20 UTC) | Independent replay | 0 trades vs 0, 0 signals vs 0. CRITICAL 0, DISCREPANCY 0. 1 FINDING: the 40-trade cap is not enforced in code; evaluation must use trades 1–40, and the frozen code is unchanged. 2 WARNINGs (hypothetical costs, intrabar assumption) |
| 2025-onward trend study reproduction (`from_2025/run.py`) | Full rerun | 0 of all lump/DCA/hour entries differ. **REPRODUCED** |

No bugs were found. Nothing was changed in any frozen paper test.
