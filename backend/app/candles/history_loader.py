from sqlalchemy.orm import Session

from app.history.redis_cache import HistoryCache
from app.candles.repository import CandleRepository


class CandleHistoryLoader:

    LIMIT = 3000

    @staticmethod
    def load(
        db: Session,
    ) -> None:

        candles = CandleRepository.load_recent(
            db=db,
            limit=CandleHistoryLoader.LIMIT,
        )

        grouped: dict[
            tuple[str, str, str],
            list,
        ] = {}

        for candle in candles:

            key = (
                candle.exchange,
                candle.token,
                candle.timeframe,
            )

            grouped.setdefault(
                key,
                [],
            ).append(candle)

        for (
            exchange,
            token,
            timeframe,
        ), candle_list in grouped.items():

            candle_list.sort(
                key=lambda candle: candle.timestamp,
            )

            HistoryCache.save(
                exchange=exchange,
                token=token,
                timeframe=timeframe,
                candles=candle_list,
            )

            print(
                f"Loaded {len(candle_list)} "
                f"historical candles "
                f"for {exchange}:{token}:{timeframe}"
            )