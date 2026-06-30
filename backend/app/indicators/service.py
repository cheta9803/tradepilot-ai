from app.indicators.calculators.ema import EMACalculator
from app.indicators.calculators.sma import SMACalculator
from app.indicators.calculators.rsi import RSICalculator
from app.indicators.calculators.vwap import VWAPCalculator

from app.market.service import MarketService


class IndicatorService:

    def __init__(self):
        self.market_service = MarketService()

    def calculate_ema(
        self,
        symbol: str,
        timeframe: str,
        period: int,
    ):

        candles = self.market_service.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=max(period * 3, period + 1),
        )

        value = EMACalculator.calculate(
            candles,
            period,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "ema": value,
        }

    def calculate_sma(
        self,
        symbol: str,
        timeframe: str,
        period: int,
    ):

        candles = self.market_service.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=max(period * 3, period + 1),
        )

        value = SMACalculator.calculate(
            candles,
            period,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "sma": value,
        }

    def calculate_rsi(
        self,
        symbol: str,
        timeframe: str,
        period: int,
    ):
        candles = self.market_service.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=period + 20,
        )

        value = RSICalculator.calculate(
            candles,
            period,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "rsi": value,
        }
    
    def calculate_vwap(
        self,
        symbol: str,
        timeframe: str,
    ):
        candles = self.market_service.get_history(
            symbol=symbol,
            timeframe=timeframe,
            limit=100,
        )

        value = VWAPCalculator.calculate(candles)

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "vwap": value,
        }