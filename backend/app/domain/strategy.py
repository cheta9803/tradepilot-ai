from abc import ABC, abstractmethod

from app.domain.candle import Candle
from app.domain.signal import TradeSignal


class Strategy(ABC):

    @abstractmethod
    def analyze(
        self,
        candles: list[Candle],
    ) -> TradeSignal:
        pass