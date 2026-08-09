from app.candles.models import Candle
from app.history.loader import HistoryLoader
from app.history.redis_cache import HistoryCache
from app.indicators.cache import IndicatorCache
from app.indicators.calculators.atr import ATRCalculator
from app.indicators.calculators.ema import EMACalculator
from app.indicators.calculators.macd import MACDCalculator
from app.indicators.calculators.rsi import RSICalculator
from app.indicators.calculators.sma import SMACalculator
from app.indicators.calculators.supertrend import (
    SupertrendCalculator,
)
from app.indicators.calculators.vwap import VWAPCalculator
from app.indicators.repository import IndicatorRepository
from app.instruments.cache import InstrumentCache
from app.patterns.engine import PatternEngine
from app.timeframes.builder import TimeframeBuilder
from app.timeframes.config import TIMEFRAMES


class IndicatorEngine:

    EMA_FAST_PERIOD = 20
    EMA_SLOW_PERIOD = 50
    SMA_PERIOD = 20
    RSI_PERIOD = 14
    ATR_PERIOD = 14

    SUPER_TREND_PERIOD = 10
    SUPER_TREND_MULTIPLIER = 3.0

    @classmethod
    def _required_candles(cls) -> int:

        return max(
            cls.EMA_SLOW_PERIOD,
            cls.SMA_PERIOD,
            cls.RSI_PERIOD,
            cls.ATR_PERIOD,
            35,
        )

    @classmethod
    def _ensure_history(
        cls,
        *,
        symbol: str,
        timeframe: str,
    ) -> list[Candle]:

        instrument = InstrumentCache.get_by_symbol(
            exchange="NSE",
            symbol=symbol,
        )

        if instrument is None:

            raise ValueError(
                f"Instrument '{symbol}' not found."
            )

        repository = IndicatorRepository()

        try:

            candles = repository.get_candles(
                symbol=symbol,
                timeframe=timeframe,
            )

        except ValueError:

            candles = []

        required = cls._required_candles()

        #
        # Existing cache is sufficient.
        #
        if len(candles) >= required:

            return candles

        #
        # We are missing enough history for the requested
        # timeframe. Load the latest completed trading day's
        # 1m history directly into HistoryCache.
        #
        HistoryLoader.load(
            exchange=instrument.exchange,
            token=instrument.token,
            refresh=True,
        )

        candles_1m = HistoryCache.get(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe="1m",
        )

        if timeframe == "1m":

            return candles_1m

        interval = TIMEFRAMES.get(
            timeframe,
        )

        if interval is None:

            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        if not candles_1m:

            return []

        #
        # Build completed timeframe candles from 1m candles.
        #
        candles_tf: list[Candle] = []

        for i in range(
            0,
            len(candles_1m),
            interval,
        ):

            bucket = candles_1m[
                i:i + interval
            ]

            if len(bucket) != interval:

                continue

            candles_tf.append(
                TimeframeBuilder.create_from_candles(
                    bucket,
                    timeframe,
                )
            )

        if candles_tf:

            HistoryCache.save(
                exchange=instrument.exchange,
                token=instrument.token,
                timeframe=timeframe,
                candles=candles_tf,
            )

        return candles_tf

    @classmethod
    def calculate(
        cls,
        *,
        symbol: str,
        timeframe: str,
    ) -> dict | None:

        symbol = symbol.upper()

        candles = cls._ensure_history(
            symbol=symbol,
            timeframe=timeframe,
        )

        required = cls._required_candles()

        if len(candles) < required:

            print(
                f"Skipping indicators for "
                f"{symbol} {timeframe}. "
                f"Need {required} candles, "
                f"have {len(candles)}."
            )

            return None

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

        try:

            vwap = VWAPCalculator.calculate(
                candles,
            )

        except Exception as exc:

            print(
                f"VWAP failed "
                f"{symbol} "
                f"{timeframe}: "
                f"{exc}"
            )

            vwap = None

        macd = MACDCalculator.calculate(
            candles,
        )

        supertrend = (
            SupertrendCalculator.calculate(
                candles,
                period=cls.SUPER_TREND_PERIOD,
                multiplier=cls.SUPER_TREND_MULTIPLIER,
            )
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
            **supertrend,
        }

        IndicatorCache.save(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
            values=values,
        )

        PatternEngine.calculate(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        from app.strategy.engine import StrategyEngine

        StrategyEngine.calculate(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        #
        # Import here to avoid circular imports.
        #
        from app.ai.engine import AIEngine

        AIEngine.calculate(
            exchange=instrument.exchange,
            token=instrument.token,
            timeframe=timeframe,
        )

        #
        # The test endpoint and callers need the calculated
        # values. Previously this method implicitly returned None.
        #
        return values