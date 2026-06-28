from app.market.provider import MockMarketProvider


class MarketService:

    def __init__(self):
        self.provider = MockMarketProvider()

    def get_history(
        self,
        symbol: str,
        timeframe: str = "5m",
        limit: int = 20,
    ):
        return self.provider.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )