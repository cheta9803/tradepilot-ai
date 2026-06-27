from app.market.provider import MockMarketProvider


class MarketService:

    def __init__(self):
        self.provider = MockMarketProvider()

    def get_history(self, symbol: str):
        return self.provider.get_history(symbol)