from sqlalchemy.orm import Session

from app.instruments.models import Instrument
from app.instruments.repository import InstrumentRepository


class InstrumentService:

    @staticmethod
    def get_by_symbol(
        db: Session,
        exchange: str,
        symbol: str,
    ) -> Instrument | None:

        return InstrumentRepository.get_by_symbol(
            db=db,
            exchange=exchange,
            symbol=symbol,
        )

    @staticmethod
    def get_by_token(
        db: Session,
        token: str,
    ) -> Instrument | None:

        return InstrumentRepository.get_by_token(
            db=db,
            token=token,
        )

    @staticmethod
    def get_by_trading_symbol(
        db: Session,
        trading_symbol: str,
    ) -> Instrument | None:

        return InstrumentRepository.get_by_trading_symbol(
            db=db,
            trading_symbol=trading_symbol,
        )

    @staticmethod
    def bulk_create(
        db: Session,
        instruments: list[Instrument],
    ) -> None:

        InstrumentRepository.bulk_create(
            db=db,
            instruments=instruments,
        )

    @staticmethod
    def delete_all(
        db: Session,
    ) -> None:

        InstrumentRepository.delete_all(db)

    @staticmethod
    def count(
        db: Session,
    ) -> int:

        return InstrumentRepository.count(db)

    @staticmethod
    def search(
        db: Session,
        query: str,
        limit: int = 20,
    ) -> list[Instrument]:

        return InstrumentRepository.search(
            db=db,
            query=query,
            limit=limit,
        )