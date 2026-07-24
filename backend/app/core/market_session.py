from datetime import datetime, time
from zoneinfo import ZoneInfo


class MarketSession:

    IST = ZoneInfo("Asia/Kolkata")

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)

    @classmethod
    def now(cls) -> datetime:

        return datetime.now(cls.IST)

    @classmethod
    def is_weekday(cls) -> bool:

        return cls.now().weekday() < 5

    @classmethod
    def is_open(cls) -> bool:

        if not cls.is_weekday():
            return False

        current = cls.now().time()

        return (
            cls.MARKET_OPEN
            <= current
            <= cls.MARKET_CLOSE
        )

    @classmethod
    def can_enter_trade(cls) -> bool:

        return cls.is_open()

    @classmethod
    def should_square_off(cls) -> bool:

        if not cls.is_weekday():
            return False

        return cls.now().time() >= cls.MARKET_CLOSE