"""Enumerations for the BTCUSDT indicator signal assistant."""
import enum


class Bias(enum.Enum):
    """Directional reading of a single indicator."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class Recommendation(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"
    AVOID = "AVOID"


class Confidence(enum.Enum):
    """Rule-agreement level. This is NOT a probability of a profitable outcome."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class Timeframe(enum.Enum):
    H1 = "1h"
    H4 = "4h"


class DataQuality(enum.Enum):
    OK = "OK"
    DEGRADED = "DEGRADED"
    UNUSABLE = "UNUSABLE"
