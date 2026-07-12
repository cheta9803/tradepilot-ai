from sqlalchemy.orm import Session

from app.candles.repository import CandleRepository
from app.candles.redis_cache import CandleCache


class CandleHistoryLoader:

    LIMIT = 200

    @staticmethod
    def load(
        db: Session,
    ) -> None:

        candles = CandleRepository.load_recent(
            db=db,
            limit=CandleHistoryLoader.LIMIT,
        )

        for candle in candles:
            CandleCache.save(candle)