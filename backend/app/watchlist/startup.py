from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.history.load_queue import HistoryLoadQueue
from app.instruments.cache import InstrumentCache
from app.watchlist.models import Watchlist
from app.scanner.universe import Nifty50Universe


class WatchlistStartup:

    INDEX_SYMBOLS = [
        ("NSE", "NIFTY"),
        ("NSE", "BANKNIFTY"),
        ("NSE", "FINNIFTY"),
    ]

    @staticmethod
    def subscribe_all() -> None:

        from app.live.instance import live_manager

        db: Session = SessionLocal()

        try:

            subscribed: set[tuple[str, str]] = set()
            instruments: list[tuple[str, str]] = []

            def collect(
                exchange: str,
                symbol: str,
            ):

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

                instruments.append(
                    (
                        instrument.exchange,
                        instrument.token,
                    )
                )

            #
            # Market indices
            #
            for exchange, symbol in WatchlistStartup.INDEX_SYMBOLS:
                collect(exchange, symbol)

            #
            # Watchlist
            #
            for item in db.query(Watchlist).all():
                collect(
                    item.exchange,
                    item.symbol,
                )

            #
            # Nifty 50 universe
            #
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

            #
            # Load history sequentially
            #
            HistoryLoadQueue.load(
                instruments,
            )

            #
            # Subscribe after history load
            #
            for exchange, token in instruments:

                live_manager.subscribe(
                    exchange=exchange,
                    token=token,
                )

                instrument = InstrumentCache.get_by_token(
                    token,
                )

                print(
                    f"Auto subscribed: "
                    f"{instrument.symbol} "
                    f"({token})"
                )

        finally:
            db.close()