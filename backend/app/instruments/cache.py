from app.db.session import SessionLocal
from app.instruments.models import Instrument


class InstrumentCache:

    _token_map: dict[str, Instrument] = {}

    @classmethod
    def load(cls):

        db = SessionLocal()

        try:
            instruments = db.query(Instrument).all()

            cls._token_map = {
                instrument.token: instrument
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