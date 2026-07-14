from app.db.session import SessionLocal
from app.instruments.models import Instrument


class InstrumentCache:

    _token_map: dict[str, Instrument] = {}
    _symbol_map: dict[tuple[str, str], Instrument] = {}

    @classmethod
    def load(cls):

        db = SessionLocal()

        try:
            instruments = db.query(Instrument).all()

            cls._token_map = {
                instrument.token: instrument
                for instrument in instruments
            }

            cls._symbol_map = {
                (
                    instrument.exchange,
                    instrument.symbol,
                ): instrument
                for instrument in instruments
            }

            print(
                f"Loaded {len(cls._token_map)} instruments into memory."
            )

        finally:
            db.close()

    @classmethod
    def get_by_token(
        cls,
        token: str,
    ) -> Instrument | None:

        return cls._token_map.get(token)

    @classmethod
    def get_by_symbol(
        cls,
        exchange: str,
        symbol: str,
    ) -> Instrument | None:

        return cls._symbol_map.get(
            (
                exchange.upper(),
                symbol.upper(),
            )
        )

    @classmethod
    def get_all(cls) -> list[Instrument]:

        return list(cls._token_map.values())