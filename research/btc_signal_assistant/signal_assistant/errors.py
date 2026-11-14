"""Typed errors for the signal assistant."""


class SignalAssistantError(Exception):
    """Base class for all signal assistant errors."""


class DataError(SignalAssistantError):
    """Market data could not be obtained or is unusable."""


class DataUnavailableError(DataError):
    """The data source could not be reached."""


class InsufficientDataError(DataError):
    """Not enough closed candles to compute the indicators."""


class CorruptCandleError(DataError):
    """A candle failed the OHLC sanity check."""


class IndicatorError(SignalAssistantError):
    """An indicator was asked for an impossible configuration."""


class NotificationError(SignalAssistantError):
    """A notification channel failed."""
