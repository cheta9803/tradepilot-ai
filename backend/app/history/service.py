from datetime import datetime

from app.history.client import HistoryClient
from app.history.date_utils import HistoryDateUtils


class HistoryService:

    INTERVAL = "ONE_MINUTE"

    @classmethod
    def get_last_day(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> list[dict]:

        return cls.get_warmup(
            exchange=exchange,
            token=token,
        )

    @classmethod
    def get_warmup(
        cls,
        *,
        exchange: str,
        token: str,
    ) -> list[dict]:

        from_date, to_date = (
            HistoryDateUtils.get_warmup_range()
        )

        return HistoryClient.get_candles(
            exchange=exchange,
            symbol_token=token,
            interval=cls.INTERVAL,
            from_date=from_date,
            to_date=to_date,
        )

    @classmethod
    def get_since(
        cls,
        *,
        exchange: str,
        token: str,
        from_date: datetime,
    ) -> list[dict]:

        _, to_date = HistoryDateUtils.get_history_range()

        return HistoryClient.get_candles(
            exchange=exchange,
            symbol_token=token,
            interval=cls.INTERVAL,
            from_date=from_date,
            to_date=to_date,
        )
