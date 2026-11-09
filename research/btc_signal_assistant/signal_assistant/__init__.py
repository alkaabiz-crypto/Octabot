"""BTCUSDT indicator signal assistant (research / paper use only).

Separate from, and independent of, the Donchian 20 forward paper test under ``research/btc_breakout``.
"""
from signal_assistant.analysis import (
                                     Assessment,
                                     IndicatorReading,
                                     assess,
                                     assess_latest,
                                     compute_series,
)
from signal_assistant.data import (
                                     Candles,
                                     assess_quality,
                                     fetch_market,
                                     load_candles_file,
                                     save_candles_file,
)
from signal_assistant.enums import Bias, Confidence, DataQuality, Recommendation
from signal_assistant.errors import (
                                     CorruptCandleError,
                                     DataError,
                                     DataUnavailableError,
                                     IndicatorError,
                                     InsufficientDataError,
                                     NotificationError,
                                     SignalAssistantError,
)
from signal_assistant.notify import Notifier
from signal_assistant.report import render_alert, render_json, render_text

__all__ = [
                                     "Assessment",
                                     "Bias",
                                     "Candles",
                                     "Confidence",
                                     "CorruptCandleError",
                                     "DataError",
                                     "DataQuality",
                                     "DataUnavailableError",
                                     "IndicatorError",
                                     "IndicatorReading",
                                     "InsufficientDataError",
                                     "NotificationError",
                                     "Notifier",
                                     "Recommendation",
                                     "SignalAssistantError",
                                     "assess",
                                     "assess_latest",
                                     "assess_quality",
                                     "compute_series",
                                     "fetch_market",
                                     "load_candles_file",
                                     "render_alert",
                                     "render_json",
                                     "render_text",
                                     "save_candles_file",
]
