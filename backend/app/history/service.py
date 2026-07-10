from datetime import datetime, timedelta

from app.history.client import HistoryClient


class HistoryService:

    INTERVAL = "ONE_MINUTE"

    @classmethod
    def get_last_day(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> list[dict]:

        now = datetime.now()

        from_date = now - timedelta(days=1)

        return HistoryClient.get_candles(
            exchange=exchange,
            symbol_token=token,
            interval=cls.INTERVAL,
            from_date=from_date,
            to_date=now,
        )