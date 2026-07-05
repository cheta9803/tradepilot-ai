from sqlalchemy.orm import Session

from app.instruments.models import Instrument


class InstrumentRepository:

    @staticmethod
    def get_by_symbol(
        db: Session,
        exchange: str,
        symbol: str,
    ) -> Instrument | None:

        return (
            db.query(Instrument)
            .filter(
                Instrument.exchange == exchange,
                Instrument.symbol == symbol,
            )
            .first()
        )

    @staticmethod
    def get_by_token(
        db: Session,
        token: str,
    ) -> Instrument | None:

        return (
            db.query(Instrument)
            .filter(
                Instrument.token == token,
            )
            .first()
        )

    @staticmethod
    def get_by_trading_symbol(
        db: Session,
        trading_symbol: str,
    ) -> Instrument | None:

        return (
            db.query(Instrument)
            .filter(
                Instrument.trading_symbol == trading_symbol,
            )
            .first()
        )

    @staticmethod
    def create(
        db: Session,
        instrument: Instrument,
    ) -> Instrument:

        db.add(instrument)
        db.commit()
        db.refresh(instrument)

        return instrument

    @staticmethod
    def bulk_create(
        db: Session,
        instruments: list[Instrument],
    ) -> None:

        db.bulk_save_objects(instruments)
        db.commit()

    @staticmethod
    def delete_all(
        db: Session,
    ) -> None:

        db.query(Instrument).delete()
        db.commit()

    @staticmethod
    def count(
        db: Session,
    ) -> int:

        return db.query(Instrument).count()

    @staticmethod
    def search(
        db: Session,
        query: str,
        limit: int = 20,
    ) -> list[Instrument]:

        search = f"%{query.upper()}%"

        return (
            db.query(Instrument)
            .filter(
                (Instrument.symbol.ilike(search))
                | (Instrument.trading_symbol.ilike(search))
                | (Instrument.token.ilike(search))
            )
            .order_by(
                Instrument.symbol.asc(),
            )
            .limit(limit)
            .all()
        )