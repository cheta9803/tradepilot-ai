from datetime import datetime
from datetime import timedelta


class HistoryDateUtils:

    @staticmethod
    def get_history_range() -> tuple[datetime, datetime]:

        now = datetime.now()

        weekday = now.weekday()

        # Monday
        if weekday == 0:

            trading_day = now - timedelta(days=3)

        # Saturday
        elif weekday == 5:

            trading_day = now - timedelta(days=1)

        # Sunday
        elif weekday == 6:

            trading_day = now - timedelta(days=2)

        # Tuesday-Friday
        else:

            trading_day = now

        from_date = trading_day.replace(
            hour=9,
            minute=15,
            second=0,
            microsecond=0,
        )

        to_date = trading_day.replace(
            hour=15,
            minute=30,
            second=0,
            microsecond=0,
        )

        return (
            from_date,
            to_date,
        )