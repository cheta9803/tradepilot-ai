from app.indicators.calculators.atr import ATRCalculator
from app.indicators.calculators.ema import EMACalculator
from app.indicators.calculators.macd import MACDCalculator
from app.indicators.calculators.rsi import RSICalculator
from app.indicators.calculators.sma import SMACalculator
from app.indicators.calculators.vwap import VWAPCalculator
from app.indicators.repository import IndicatorRepository


class IndicatorService:

    def __init__(self):

        self.repository = IndicatorRepository()

    def _get_candles(
        self,
        *,
        symbol: str,
        timeframe: str,
    ):

        return self.repository.get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

    def calculate_ema(
        self,
        symbol: str,
        timeframe: str,
        period: int,
    ):

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
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

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
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

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
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

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

        value = VWAPCalculator.calculate(
            candles,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "vwap": value,
        }

    def calculate_atr(
        self,
        symbol: str,
        timeframe: str,
        period: int,
    ):

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

        value = ATRCalculator.calculate(
            candles,
            period,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "period": period,
            "atr": value,
        }

    def calculate_macd(
        self,
        symbol: str,
        timeframe: str,
    ):

        candles = self._get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

        result = MACDCalculator.calculate(
            candles,
        )

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            **result,
        }