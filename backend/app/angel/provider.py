from datetime import datetime

from app.angel.client import AngelClient
from app.angel.exceptions import AngelAPIException
from app.market.models import Candle
from app.market.provider import MarketProvider


class AngelMarketProvider(MarketProvider):

    INTERVAL_MAP = {
        "1m": "ONE_MINUTE",
        "5m": "FIVE_MINUTE",
        "15m": "FIFTEEN_MINUTE",
        "30m": "THIRTY_MINUTE",
        "1h": "ONE_HOUR",
        "1d": "ONE_DAY",
    }

    TOKEN_MAP = {
        "RELIANCE": "2885",
        "TCS": "11536",
        "INFY": "1594",
    }

    def get_history(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:

        smart_api = AngelClient.login()

        interval = self.INTERVAL_MAP.get(
            timeframe,
            "FIVE_MINUTE",
        )

        token = self.TOKEN_MAP.get(symbol)

        if token is None:
            raise AngelAPIException(
                f"Unsupported symbol {symbol}"
            )

        from datetime import timedelta

        to_date = datetime.now()

        from_date = to_date - timedelta(days=5)

        response = smart_api.getCandleData(
            {
                "exchange": "NSE",
                "symboltoken": token,
                "interval": interval,
                "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                "todate": to_date.strftime("%Y-%m-%d %H:%M"),
            }
        )

        if not response["status"]:
            raise AngelAPIException(response["message"])

        candles = []

        for row in response["data"][-limit:]:

            candles.append(
                Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=datetime.fromisoformat(row[0]),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                )
            )

        return candles