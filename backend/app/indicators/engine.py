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

    EMA_FAST_PERIOD = 20
    EMA_SLOW_PERIOD = 50
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

        repository = IndicatorRepository()

        candles = repository.get_candles(
            symbol=symbol,
            timeframe=timeframe,
        )

        ema20 = EMACalculator.calculate(
            candles,
            cls.EMA_FAST_PERIOD,
        )

        ema50 = EMACalculator.calculate(
            candles,
            cls.EMA_SLOW_PERIOD,
        )

        sma20 = SMACalculator.calculate(
            candles,
            cls.SMA_PERIOD,
        )

        rsi14 = RSICalculator.calculate(
            candles,
            cls.RSI_PERIOD,
        )

        atr14 = ATRCalculator.calculate(
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

        if instrument is None:
            raise ValueError(
                f"Instrument not found: {symbol}"
            )

        values = {
            "ema20": ema20,
            "ema50": ema50,
            "sma20": sma20,
            "rsi14": rsi14,
            "atr14": atr14,
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