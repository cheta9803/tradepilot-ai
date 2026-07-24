class TradePilotException(Exception):
    """Base exception for TradePilot AI."""


class RetryLimitExceededException(TradePilotException):
    """Raised when all retry attempts have been exhausted."""


class BrokerUnavailableException(TradePilotException):
    """Raised when the broker service is temporarily unavailable."""


class BrokerTimeoutException(TradePilotException):
    """Raised when a broker request times out."""


class AuthenticationException(TradePilotException):
    """Raised when broker authentication fails."""


class OrderRejectedException(TradePilotException):
    """Raised when the broker rejects an order."""