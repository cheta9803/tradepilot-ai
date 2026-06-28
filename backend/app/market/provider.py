from datetime import datetime, timedelta

from app.market.models import Candle


class MockMarketProvider:

    def get_history(
        self,
        symbol: str,
        timeframe: str = "5m",
        limit: int = 20,
    ) -> list[Candle]:

        now = datetime.now()

        candles: list[Candle] = []

        price = 2500.0

        interval = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
        }.get(timeframe, 5)

        for i in range(limit):

            candles.append(
                Candle(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=now - timedelta(minutes=(limit - i) * interval),
                    open=price,
                    high=price + 4,
                    low=price - 2,
                    close=price + 1,
                    volume=1000 + i * 25,
                )
            )

            price += 2

        return candles