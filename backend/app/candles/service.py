from datetime import datetime

from app.candles.builder import CandleBuilder
from app.candles.models import Candle
from app.candles.redis_cache import CandleCache
from app.candles.repository import CandleRepository
from app.db.session import SessionLocal
from app.history.redis_cache import HistoryCache

from app.indicators.engine import IndicatorEngine

class CandleService:

    TIMEFRAME = "1m"

    @staticmethod
    def process_tick(
        *,
        exchange: str,
        symbol: str,
        token: str,
        price: float,
        volume: int,
        timestamp: datetime,
    ) -> None:

        minute = timestamp.replace(
            second=0,
            microsecond=0,
        )

        candle = CandleService._get_current_candle(
            exchange=exchange,
            token=token,
        )

        if candle is None:

            CandleService._create_new_candle(
                exchange=exchange,
                symbol=symbol,
                token=token,
                minute=minute,
                price=price,
                volume=volume,
            )

            return

        if CandleService._is_new_minute(
            candle=candle,
            minute=minute,
        ):

            HistoryCache.append(candle)

            IndicatorEngine.calculate(
                symbol=symbol,
                timeframe=CandleService.TIMEFRAME,
            )

            CandleService._create_new_candle(
                exchange=exchange,
                symbol=symbol,
                token=token,
                minute=minute,
                price=price,
                volume=volume,
            )

            return

        CandleService._update_existing_candle(
            candle=candle,
            price=price,
            volume=volume,
        )

    @staticmethod
    def _is_new_minute(
        *,
        candle: Candle,
        minute: datetime,
    ) -> bool:

        return candle.timestamp != minute

    @staticmethod
    def _get_current_candle(
        *,
        exchange: str,
        token: str,
    ) -> Candle | None:

        candle = CandleCache.get(
            exchange=exchange,
            token=token,
            timeframe=CandleService.TIMEFRAME,
        )

        if candle is not None:
            return candle

        db = SessionLocal()

        try:

            entity = CandleRepository.get_latest(
                db=db,
                exchange=exchange,
                token=token,
                timeframe=CandleService.TIMEFRAME,
            )

        finally:
            db.close()

        if entity is None:
            return None

        candle = Candle(
            exchange=entity.exchange,
            symbol=entity.symbol,
            token=entity.token,
            timeframe=entity.timeframe,
            timestamp=entity.timestamp,
            open=entity.open,
            high=entity.high,
            low=entity.low,
            close=entity.close,
            volume=entity.volume,
        )

        CandleCache.save(candle)

        return candle

    @staticmethod
    def _create_new_candle(
        *,
        exchange: str,
        symbol: str,
        token: str,
        minute: datetime,
        price: float,
        volume: int,
    ) -> None:

        candle = CandleBuilder.create(
            exchange=exchange,
            symbol=symbol,
            token=token,
            timeframe=CandleService.TIMEFRAME,
            timestamp=minute,
            price=price,
            volume=volume,
        )

        CandleService._persist(candle)

    @staticmethod
    def _update_existing_candle(
        *,
        candle: Candle,
        price: float,
        volume: int,
    ) -> None:

        if (
            candle.close == price
            and candle.volume == volume
        ):
            return

        candle = CandleBuilder.update(
            candle,
            price=price,
            volume=volume,
        )

        CandleService._persist(candle)

    @staticmethod
    def _persist(
        candle: Candle,
    ) -> None:

        CandleCache.save(candle)

        db = SessionLocal()

        try:

            CandleRepository.save(
                db=db,
                candle=candle,
            )

        finally:

            db.close()