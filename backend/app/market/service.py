from app.angel.provider import AngelMarketProvider


class MarketService:

    def __init__(self):
        self.provider = AngelMarketProvider()

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