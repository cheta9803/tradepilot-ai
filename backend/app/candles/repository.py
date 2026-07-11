from sqlalchemy.orm import Session

from app.candles.db_models import CandleModel
from app.candles.models import Candle


class CandleRepository:

    @staticmethod
    def save(
        db: Session,
        candle: Candle,
    ) -> CandleModel:

        db_candle = (
            db.query(CandleModel)
            .filter(
                CandleModel.exchange == candle.exchange,
                CandleModel.token == candle.token,
                CandleModel.timeframe == candle.timeframe,
                CandleModel.timestamp == candle.timestamp,
            )
            .first()
        )

        if db_candle is None:

            db_candle = CandleModel(
                exchange=candle.exchange,
                symbol=candle.symbol,
                token=candle.token,
                timeframe=candle.timeframe,
                timestamp=candle.timestamp,
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,
            )

            db.add(db_candle)

        else:

            db_candle.high = candle.high
            db_candle.low = candle.low
            db_candle.close = candle.close
            db_candle.volume = candle.volume

        db.commit()
        db.refresh(db_candle)

        return db_candle

    @staticmethod
    def get_latest(
        *,
        db: Session,
        exchange: str,
        token: str,
        timeframe: str,
    ):

        return (
            db.query(CandleEntity)
            .filter(
                CandleEntity.exchange == exchange,
                CandleEntity.token == token,
                CandleEntity.timeframe == timeframe,
            )
            .order_by(
                CandleEntity.timestamp.desc()
            )
            .first()
        )