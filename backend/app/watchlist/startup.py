from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.history.load_queue import HistoryLoadQueue
from app.history.rebuilder import HistoryRebuilder
from app.instruments.cache import InstrumentCache
from app.watchlist.models import Watchlist
from app.scanner.universe import Nifty50Universe


class WatchlistStartup:

    INDEX_SYMBOLS = [
        ("NSE", "NIFTY"),
        ("NSE", "BANKNIFTY"),
        ("NSE", "FINNIFTY"),
    ]

    _history_loaded = False
    _instruments: list[tuple[str, str]] = []

    @classmethod
    def get_required_instruments(cls) -> list[tuple[str, str]]:
        db: Session = SessionLocal()

        try:
            subscribed: set[tuple[str, str]] = set()
            instruments: list[tuple[str, str]] = []

            def collect(
                exchange: str,
                symbol: str,
            ) -> None:
                instrument = InstrumentCache.get_by_symbol(
                    exchange=exchange,
                    symbol=symbol,
                )

                if instrument is None:
                    return

                key = (
                    instrument.exchange,
                    instrument.token,
                )

                if key in subscribed:
                    return

                subscribed.add(key)
                instruments.append(key)

            for exchange, symbol in cls.INDEX_SYMBOLS:
                collect(exchange, symbol)

            for item in db.query(Watchlist).all():
                collect(
                    item.exchange,
                    item.symbol,
                )

            for instrument in InstrumentCache.get_all():
                if instrument.exchange != "NSE":
                    continue

                if not Nifty50Universe.contains(
                    instrument.symbol,
                ):
                    continue

                collect(
                    instrument.exchange,
                    instrument.symbol,
                )

            cls._instruments = instruments
            return list(instruments)

        finally:
            db.close()

    @classmethod
    def load_history(cls) -> list[tuple[str, str]]:
        if cls._history_loaded:
            return list(cls._instruments)

        instruments = cls.get_required_instruments()

        if not instruments:
            cls._history_loaded = True
            return []

        HistoryLoadQueue.load(instruments)

        # History is now loaded. Rebuild higher timeframes,
        # indicators and strategy using the newly loaded data.
        HistoryRebuilder.rebuild()

        cls._history_loaded = True

        return list(instruments)

    @classmethod
    def subscribe_all(
        cls,
        *,
        load_history: bool = True,
    ) -> None:
        from app.live.instance import live_manager

        instruments = (
            cls.load_history()
            if load_history
            else cls.get_required_instruments()
        )

        for exchange, token in instruments:
            live_manager.subscribe(
                exchange=exchange,
                token=token,
            )

            instrument = InstrumentCache.get_by_token(token)

            if instrument is not None:
                print(
                    f"Auto subscribed: "
                    f"{instrument.symbol} "
                    f"({token})"
                )