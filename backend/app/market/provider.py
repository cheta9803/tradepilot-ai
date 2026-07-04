from abc import ABC
from abc import abstractmethod

from app.market.models import Candle


class MarketProvider(ABC):

    @abstractmethod
    def get_history(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[Candle]:
        pass