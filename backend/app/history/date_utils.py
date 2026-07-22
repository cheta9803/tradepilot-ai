from datetime import datetime
from datetime import timedelta


class HistoryDateUtils:

    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 15

    MARKET_CLOSE_HOUR = 15
    MARKET_CLOSE_MINUTE = 30

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

        # Before market opens today.
        # Use the previous trading day's full session.
        if trading_day.date() != now.date():

            return (
                market_open,
                market_close,
            )

        # Before 09:15 today.
        if now < market_open:

            previous = cls._previous_trading_day(now)

            return (
                previous.replace(
                    hour=cls.MARKET_OPEN_HOUR,
                    minute=cls.MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0,
                ),
                previous.replace(
                    hour=cls.MARKET_CLOSE_HOUR,
                    minute=cls.MARKET_CLOSE_MINUTE,
                    second=0,
                    microsecond=0,
                ),
            )

        # During market hours.
        if now <= market_close:

            return (
                market_open,
                now.replace(
                    second=0,
                    microsecond=0,
                ),
            )

        # After market close.
        return (
            market_open,
            market_close,
        )

    @classmethod
    def _get_trading_day(
        cls,
        now: datetime,
    ) -> datetime:

        weekday = now.weekday()

        # Saturday
        if weekday == 5:
            return now - timedelta(days=1)

        # Sunday
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