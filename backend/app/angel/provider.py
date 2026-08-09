from datetime import datetime, timedelta

from app.angel.client import AngelClient
from app.angel.exceptions import AngelAPIException
from app.instruments.cache import InstrumentCache
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

    def get_history(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:

        symbol = symbol.upper()

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:
            raise AngelAPIException(
                f"Instrument not found: {symbol}"
            )

        interval = self.INTERVAL_MAP.get(
            timeframe,
        )

        if interval is None:
            raise AngelAPIException(
                f"Unsupported timeframe: {timeframe}"
            )

        smart_api = AngelClient.login()

        to_date = datetime.now()

        from_date = (
            to_date -
            timedelta(days=5)
        )

        response = smart_api.getCandleData(
            {
                "exchange": instrument.exchange,
                "symboltoken": instrument.token,
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

            raise AngelAPIException(
                response.get(
                    "message",
                    "Unable to fetch historical data.",
                )
            )

        rows = response.get(
            "data",
            [],
        )

        candles: list[Candle] = []

        for row in rows[-limit:]:

            candles.append(
                Candle(
                    symbol=instrument.symbol,
                    timeframe=timeframe,
                    timestamp=datetime.fromisoformat(
                        row[0],
                    ),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                )
            )

        return candles

    def get_ltp(
        self,
        exchange: str,
        symbol: str,
        token: str,
    ) -> dict:

        from app.angel.service import AngelService

        return AngelService.get_ltp(
            exchange=exchange,
            symbol=symbol,
            token=token,
        )