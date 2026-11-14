"""Fixed settings of the independent validation. Written before any validation result was computed (2026-11-10).

Nothing here changes the frozen strategy. The frozen engine, its data and its locked parameters are READ from a
checkout of branch claude/download-skill-27d08k pinned at FROZEN_COMMIT. Set FROZEN_BTC_BREAKOUT to the
research/btc_breakout directory of that checkout (data/*.json must be gunzipped, see README).
"""
import calendar
import os

FROZEN_COMMIT = "f1798b71"
FREEZE_COMMIT = "ce2e8c57"   # strategy files unchanged since this commit (checked by frozen.py)
FROZEN_DIR = os.environ.get("FROZEN_BTC_BREAKOUT", "")
EXNESS_BARS_DIR = os.environ.get("EXNESS_BARS_15M", os.path.join(os.path.dirname(FROZEN_DIR), "exness_validation", "data", "bars15m"))

# SHA-256 of the frozen files (verified on 2026-11-10 against the freeze commit)
EXPECTED_SHA256 = {
    "src/engine.py": "1cd380279e496230aa9cf1c61608d1442f4017b4273280fd677bdb7c2c0bc8a9",
    "src/protocol.py": "ed709512c42e09cb07cc3e1e9a6e94946c06f831f86c05e4bd065da85eaead5d",
    "forward/paper_trader.py": "19d084c4d4295a6f7e3b9afd9240b77a77627ca3a0c489034591610703ab2f72",
}


def ts(y, m, d=1, h=0):
    return calendar.timegm((y, m, d, h, 0, 0))


# The locked candidate (from FROZEN.json): Donchian 20 breakout, 1H entries, 4H close > EMA200, long, ATR trail
MODEL, ENTRY_TF, DIRECTION, STOP = "M2_DONCHIAN20", "1h", 1, "TRAIL"
STOP_ATR, TRAIL_ATR = 2.0, 3.0

# Periods (same split as the original study; no new parameter is chosen anywhere)
DEV = ("development 2020-01..2025-06", ts(2020, 1), ts(2025, 7))
HOLDOUT = ("holdout 2025-07..2026-11-08", ts(2025, 7), ts(2026, 11, 9))
ALL = ("2020-01..2026-11-08", ts(2020, 1), ts(2026, 11, 9))
PERIODS = (DEV, HOLDOUT, ALL)

# Cost scenarios in fraction of price per ROUND TRIP (same as the frozen study) plus measured Exness spread
COSTS = {"zero": 0.0, "low": 0.0002, "mid": 0.0005, "high": 0.0010}
PRIMARY_COST = "mid"

# Execution-delay scenarios: entry this many 15m bars after the first available bar
DELAYS_15M = (0, 1, 2, 4)
# Stop slippage scenarios (fraction of price added against the trade when a stop is hit without a gap)
STOP_SLIPPAGE = (0.0, 0.0005, 0.001)

# Random-entry benchmark
RANDOM_RUNS = 2000
SEED = 20261110
BOOTSTRAP_RUNS = 5000
BLOCK_MONTHS = 3            # mean block length (months) for the stationary bootstrap

# Swap: Exness rollover is at 21:00 UTC (northern summer time) or 22:00 UTC (winter); triple on Friday night
ROLLOVER_HOUR_SUMMER, ROLLOVER_HOUR_WINTER = 21, 22
TRIPLE_SWAP_WEEKDAY = 4     # Friday
