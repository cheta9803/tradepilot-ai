from enum import Enum


class OrderType(str, Enum):

    MARKET = "MARKET"

    LIMIT = "LIMIT"

    SL = "SL"

    SLM = "SL-M"


class TransactionType(str, Enum):

    BUY = "BUY"

    SELL = "SELL"


class ProductType(str, Enum):

    INTRADAY = "INTRADAY"

    DELIVERY = "DELIVERY"


class OrderStatus(str, Enum):

    PENDING = "PENDING"

    OPEN = "OPEN"

    COMPLETE = "COMPLETE"

    CANCELLED = "CANCELLED"

    REJECTED = "REJECTED"

    FAILED = "FAILED"