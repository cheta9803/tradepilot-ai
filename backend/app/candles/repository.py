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
            db.query(CandleModel)
            .filter(
                CandleModel.exchange == exchange,
                CandleModel.token == token,
                CandleModel.timeframe == timeframe,
            )
            .order_by(
                CandleModel.timestamp.desc()
            )
            .first()
        )

    @staticmethod
    def load_recent(
        *,
        db: Session,
        limit: int,
    ) -> list[Candle]:

        rows = (
            db.query(CandleModel)
            .order_by(
                CandleModel.timestamp.desc()
            )
            .limit(limit)
            .all()
        )

        candles = []

        for row in reversed(rows):

            candles.append(
                Candle(
                    exchange=row.exchange,
                    symbol=row.symbol,
                    token=row.token,
                    timeframe=row.timeframe,
                    timestamp=row.timestamp,
                    open=row.open,
                    high=row.high,
                    low=row.low,
                    close=row.close,
                    volume=row.volume,
                )
            )

        return candles

    @staticmethod
    def load_recent_grouped(
        *,
        db: Session,
        limit: int,
    ) -> dict[tuple[str, str, str], list[Candle]]:
        """
        Load up to `limit` most recent candles for every
        exchange/token/timeframe combination.

        The previous implementation used one global LIMIT,
        which caused the available candles to be divided
        across all instruments.
        """

        keys = (
            db.query(
                CandleModel.exchange,
                CandleModel.token,
                CandleModel.timeframe,
            )
            .distinct()
            .all()
        )

        grouped: dict[
            tuple[str, str, str],
            list[Candle],
        ] = {}

        for exchange, token, timeframe in keys:

            rows = (
                db.query(CandleModel)
                .filter(
                    CandleModel.exchange == exchange,
                    CandleModel.token == token,
                    CandleModel.timeframe == timeframe,
                )
                .order_by(
                    CandleModel.timestamp.desc()
                )
                .limit(limit)
                .all()
            )

            if not rows:
                continue

            candles = [
                Candle(
                    exchange=row.exchange,
                    symbol=row.symbol,
                    token=row.token,
                    timeframe=row.timeframe,
                    timestamp=row.timestamp,
                    open=row.open,
                    high=row.high,
                    low=row.low,
                    close=row.close,
                    volume=row.volume,
                )
                for row in reversed(rows)
            ]

            grouped[
                (
                    exchange,
                    token,
                    timeframe,
                )
            ] = candles

        return grouped

    @staticmethod
    def save_many(
        db: Session,
        candles: list[Candle],
    ) -> None:

        if not candles:
            return

        grouped: dict[
            tuple[str, str, str],
            list[Candle],
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

            timestamps = [
                candle.timestamp
                for candle in candle_list
            ]

            existing_rows = (
                db.query(CandleModel)
                .filter(
                    CandleModel.exchange == exchange,
                    CandleModel.token == token,
                    CandleModel.timeframe == timeframe,
                    CandleModel.timestamp.in_(
                        timestamps
                    ),
                )
                .all()
            )

            existing_by_timestamp = {
                row.timestamp: row
                for row in existing_rows
            }

            for candle in candle_list:

                existing = existing_by_timestamp.get(
                    candle.timestamp
                )

                if existing is None:

                    db.add(
                        CandleModel(
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
                    )

                else:

                    existing.symbol = candle.symbol
                    existing.open = candle.open
                    existing.high = candle.high
                    existing.low = candle.low
                    existing.close = candle.close
                    existing.volume = candle.volume

        db.commit()