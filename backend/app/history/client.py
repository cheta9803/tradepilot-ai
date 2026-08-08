from datetime import datetime

from app.angel.client import AngelClient
from app.core.logger import logger


class HistoryClient:

    @staticmethod
    def get_candles(
        *,
        exchange: str,
        symbol_token: str,
        interval: str,
        from_date: datetime,
        to_date: datetime,
    ) -> list[dict]:

        try:
            client = AngelClient.login()

            response = client.getCandleData(
                {
                    "exchange": exchange,
                    "symboltoken": symbol_token,
                    "interval": interval,
                    "fromdate": from_date.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                    "todate": to_date.strftime(
                        "%Y-%m-%d %H:%M"
                    ),
                }
            )
        except Exception as exc:
            logger.debug(
                "Historical candle fetch failed for %s/%s: %s",
                exchange,
                symbol_token,
                exc,
            )
            return []

        if not response or not response.get("status"):
            logger.debug(
                "Historical candle fetch returned no data for %s/%s: %s",
                exchange,
                symbol_token,
                (response or {}).get(
                    "message",
                    "No data",
                ),
            )
            return []

        logger.debug(
            "History API returned %d candles for %s/%s",
            len(response["data"] or []),
            exchange,
            symbol_token,
        )

        return response["data"] or []