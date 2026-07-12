from datetime import datetime

from app.angel.client import AngelClient


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

        if not response.get("status"):
            raise ValueError(
                response.get(
                    "message",
                    "Unable to fetch historical candles.",
                )
            )

        print(f"History API returned {len(response['data'] or [])} candles")

        return response["data"] or []