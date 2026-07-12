from app.indicators.cache import IndicatorCache
from app.indicators.calculators.atr import ATRCalculator
from app.indicators.calculators.ema import EMACalculator
from app.indicators.calculators.macd import MACDCalculator
from app.indicators.calculators.rsi import RSICalculator
from app.indicators.calculators.sma import SMACalculator
from app.indicators.calculators.vwap import VWAPCalculator
from app.indicators.repository import IndicatorRepository
from app.instruments.cache import InstrumentCache


class IndicatorEngine:

    EMA_PERIOD = 20
    SMA_PERIOD = 20
    RSI_PERIOD = 14
    ATR_PERIOD = 14

    @classmethod
    def calculate(
        cls,
        *,
        symbol: str,
        timeframe: str,
    ) -> dict:

        from datetime import datetime

        print(
            f">>> Indicator calculation at {datetime.now()}"
        )

        repository = IndicatorRepository()

        candles = repository.get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

        ema = EMACalculator.calculate(
            candles,
            cls.EMA_PERIOD,
        )

        sma = SMACalculator.calculate(
            candles,
            cls.SMA_PERIOD,
        )

        rsi = RSICalculator.calculate(
            candles,
            cls.RSI_PERIOD,
        )

        atr = ATRCalculator.calculate(
            candles,
            cls.ATR_PERIOD,
        )

        vwap = VWAPCalculator.calculate(
            candles,
        )

        macd = MACDCalculator.calculate(
            candles,
        )

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        values = {
            "ema20": ema,
            "sma20": sma,
            "rsi14": rsi,
            "atr14": atr,
            "vwap": vwap,
            **macd,
        }

        IndicatorCache.save(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
            values=values,
        )

        return values