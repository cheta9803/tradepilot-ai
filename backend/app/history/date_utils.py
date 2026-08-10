from datetime import datetime
from datetime import timedelta


class HistoryDateUtils:

    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 15

    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30

    WARMUP_TRADING_DAYS = 10

    @classmethod
    def get_history_range(
        cls,
    ) -> tuple[datetime, datetime]:

        now = datetime.now()
        trading_day = cls._get_trading_day(now)

        market_open = trading_day.replace(
            hour=cls.MARKET_OPEN_HOUR,
            minute=cls.MARKET_OPEN_MINUTE,
            second=0,
            microsecond=0,
        )

        market_close = trading_day.replace(
            hour=cls.MARKET_CLOSE_HOUR,
            minute=cls.MARKET_CLOSE_MINUTE,
            second=0,
            microsecond=0,
        )

        if trading_day.date() != now.date():
            return market_open, market_close

        if now < market_open:
            previous = cls._previous_trading_day(now)
            return cls._session_range(previous)

        if now <= market_close:
            return (
                market_open,
                now.replace(second=0, microsecond=0),
            )

        return market_open, market_close

    @classmethod
    def get_warmup_range(
        cls,
        trading_days: int | None = None,
    ) -> tuple[datetime, datetime]:
        """Return a multi-session range suitable for indicator warm-up."""

        days = trading_days or cls.WARMUP_TRADING_DAYS
        if days < 1:
            raise ValueError("trading_days must be >= 1")

        _, end = cls.get_history_range()
        current_day = cls._get_trading_day(datetime.now())

        start_day = current_day
        remaining = days - 1

        while remaining > 0:
            start_day -= timedelta(days=1)
            if start_day.weekday() < 5:
                remaining -= 1

        start, _ = cls._session_range(start_day)
        return start, end

    @classmethod
    def _session_range(
        cls,
        trading_day: datetime,
    ) -> tuple[datetime, datetime]:

        return (
            trading_day.replace(
                hour=cls.MARKET_OPEN_HOUR,
                minute=cls.MARKET_OPEN_MINUTE,
                second=0,
                microsecond=0,
            ),
            trading_day.replace(
                hour=cls.MARKET_CLOSE_HOUR,
                minute=cls.MARKET_CLOSE_MINUTE,
                second=0,
                microsecond=0,
            ),
        )

    @classmethod
    def _get_trading_day(
        cls,
        now: datetime,
    ) -> datetime:

        weekday = now.weekday()

        if weekday == 5:
            return now - timedelta(days=1)

        if weekday == 6:
            return now - timedelta(days=2)

        return now

    @classmethod
    def _previous_trading_day(
        cls,
        current: datetime,
    ) -> datetime:

        previous = current - timedelta(days=1)

        while previous.weekday() >= 5:
            previous -= timedelta(days=1)

        return previous
