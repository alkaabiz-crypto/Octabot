"""Module-wide constants: indicator periods, thresholds and data settings.

Every threshold here is a textbook / conventional value. Nothing was optimised on BTC data.
"""
SYMBOL = "BTCUSDT"
ENTRY_TF = "1h"
TREND_TF = "4h"
STEP_SECONDS = {"1h": 3600, "4h": 14400}

# Indicator periods (as requested)
DONCHIAN_PERIOD = 20
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
ADX_PERIOD = 14

# Minimum closed candles needed before any indicator value is trusted.
# EMA200 needs 200 bars to be defined at all; we require extra bars so the
# seeded EMA has converged (the seed is an SMA, and its influence decays as (1-2/201)^n).
MIN_BARS_1H = EMA_SLOW + 100
MIN_BARS_4H = EMA_SLOW + 50

# Conventional thresholds
RSI_OVERBOUGHT = 70.0
RSI_OVERSOLD = 30.0
RSI_EXTREME_HIGH = 80.0   # a BUY is downgraded to WAIT above this
RSI_EXTREME_LOW = 20.0    # a SELL is downgraded to WAIT below this
RSI_MIDLINE = 50.0
ADX_TRENDING = 25.0
ADX_WEAK = 20.0

# Decision rules
MIN_CONFIRMING_1H_INDICATORS = 3   # of EMA, RSI, MACD, ADX (Donchian is the trigger itself)
HIGH_CONFIDENCE_MIN_AGREEMENT = 9  # of 10 indicator readings aligned with the direction
MEDIUM_CONFIDENCE_MIN_AGREEMENT = 7

# Data
BINANCE_KLINES_URL = "https://data-api.binance.vision/api/v3/klines"
CA_BUNDLE_PATH = "/root/.ccr/ca-bundle.crt"
DEFAULT_HISTORY_DAYS = 400
MAX_STALE_SECONDS = 2 * 3600       # last closed 1H candle must be at most this old
GAP_CHECK_BARS = 60                # a gap inside the last N bars marks data as UNUSABLE

# Files (relative to the module directory)
STATE_DIR = "state"
ALERTS_DIR = "alerts"
LAST_NOTIFIED_FILE = "last_notified.json"
ALERTS_CSV = "alerts.csv"

# Notification environment variables (all optional)
ENV_WEBHOOK_URL = "SIGNAL_ASSISTANT_WEBHOOK_URL"
ENV_TELEGRAM_TOKEN = "SIGNAL_ASSISTANT_TELEGRAM_BOT_TOKEN"
ENV_TELEGRAM_CHAT_ID = "SIGNAL_ASSISTANT_TELEGRAM_CHAT_ID"
