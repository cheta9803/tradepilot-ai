from datetime import datetime, timedelta

from app.market.models import Candle


class MockMarketProvider:

    def get_history(self, symbol: str) -> list[Candle]:

        now = datetime.now()

        candles = []

        price = 2500.0

        for i in range(20):

            candles.append(
                Candle(
                    symbol=symbol,
                    timestamp=now - timedelta(minutes=20 - i),
                    open=price,
                    high=price + 4,
                    low=price - 2,
                    close=price + 1,
                    volume=1000 + i * 25,
                )
            )

            price += 2

        return candles