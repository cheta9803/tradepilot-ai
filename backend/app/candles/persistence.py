from sqlalchemy.orm import Session

from app.candles.models import Candle
from app.candles.repository import CandleRepository
from app.db.session import SessionLocal


class CandlePersistence:

    @staticmethod
    def save(
        candle: Candle,
    ) -> None:

        db: Session = SessionLocal()

        try:
            CandleRepository.save(
                db=db,
                candle=candle,
            )
        finally:
            db.close()