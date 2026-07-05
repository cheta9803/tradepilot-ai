import requests
from sqlalchemy.orm import Session

from app.instruments.models import Instrument
from app.instruments.service import InstrumentService


class InstrumentLoader:

    MASTER_URL = (
        "https://margincalculator.angelbroking.com/"
        "OpenAPI_File/files/OpenAPIScripMaster.json"
    )

    @classmethod
    def sync(cls, db: Session) -> int:

        response = requests.get(
            cls.MASTER_URL,
            timeout=60,
            headers={
                "User-Agent": "TradePilot-AI/1.0",
            },
        )

        response.raise_for_status()

        records = response.json()

        InstrumentService.delete_all(db)

        instruments: list[Instrument] = []

        for item in records:

            exchange = item.get("exch_seg")

            if exchange not in (
                "NSE",
                "BSE",
            ):
                continue

            symbol = item.get("name")

            trading_symbol = item.get("symbol")

            token = item.get("token")

            if (
                not symbol
                or not trading_symbol
                or not token
            ):
                continue

            instruments.append(
                Instrument(
                    exchange=exchange,
                    symbol=symbol.upper(),
                    trading_symbol=trading_symbol.upper(),
                    token=str(token),
                    instrument_type=item.get(
                        "instrumenttype",
                        "",
                    ),
                    lot_size=int(
                        item.get(
                            "lotsize",
                            1,
                        )
                    ),
                    tick_size=float(
                        item.get(
                            "tick_size",
                            0.05,
                        )
                    ),
                )
            )

        InstrumentService.bulk_create(
            db=db,
            instruments=instruments,
        )

        return len(instruments)