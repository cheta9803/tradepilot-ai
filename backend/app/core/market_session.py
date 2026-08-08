from datetime import datetime, time
from zoneinfo import ZoneInfo


class MarketSession:

    IST = ZoneInfo("Asia/Kolkata")

    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)

    MAX_LIVE_DATA_AGE_SECONDS = 120

    @classmethod
    def now(cls) -> datetime:

        return datetime.now(
            cls.IST,
        )

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
    def status(cls) -> str:

        if cls.is_open():
            return "OPEN"

        return "CLOSED"

    @classmethod
    def can_enter_trade(cls) -> bool:

        return cls.is_open()

    @classmethod
    def should_square_off(cls) -> bool:

        if not cls.is_weekday():
            return False

        return (
            cls.now().time()
            >= cls.MARKET_CLOSE
        )

    @classmethod
    def normalize_timestamp(
        cls,
        timestamp: datetime,
    ) -> datetime:

        if timestamp.tzinfo is None:

            return timestamp.replace(
                tzinfo=cls.IST,
            )

        return timestamp.astimezone(
            cls.IST,
        )

    @classmethod
    def data_age_seconds(
        cls,
        timestamp: datetime,
    ) -> float:

        timestamp = cls.normalize_timestamp(
            timestamp,
        )

        return max(
            0.0,
            (
                cls.now()
                - timestamp
            ).total_seconds(),
        )

    @classmethod
    def is_data_live(
        cls,
        timestamp: datetime,
    ) -> bool:

        if not cls.is_open():
            return False

        age = cls.data_age_seconds(
            timestamp,
        )

        return (
            age
            <= cls.MAX_LIVE_DATA_AGE_SECONDS
        )

    @classmethod
    def data_status(
        cls,
        timestamp: datetime,
    ) -> str:

        if cls.is_data_live(
            timestamp,
        ):

            return "LIVE"

        return "STALE"