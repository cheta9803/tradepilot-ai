from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.history.loader import HistoryLoader
from app.instruments.cache import InstrumentCache
from app.watchlist.models import Watchlist


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

            def subscribe_instrument(exchange: str, symbol: str):

                instrument = InstrumentCache.get_by_symbol(
                    exchange=exchange,
                    symbol=symbol,
                )

                if instrument is None:
                    print(
                        f"Instrument not found: {exchange} {symbol}"
                    )
                    return

                key = (
                    instrument.exchange,
                    instrument.token,
                )

                if key in subscribed:
                    return

                try:

                    HistoryLoader.load(
                        exchange=instrument.exchange,
                        token=instrument.token,
                    )

                    live_manager.subscribe(
                        exchange=instrument.exchange,
                        token=instrument.token,
                    )

                    subscribed.add(key)

                    print(
                        f"Auto subscribed: "
                        f"{instrument.symbol} "
                        f"({instrument.token})"
                    )

                except Exception as exc:
                    print(
                        f"Failed to initialize "
                        f"{instrument.symbol}: {exc}"
                    )

            #
            # Subscribe market indices
            #
            for exchange, symbol in WatchlistStartup.INDEX_SYMBOLS:
                subscribe_instrument(
                    exchange=exchange,
                    symbol=symbol,
                )

            #
            # Subscribe watchlist instruments
            #
            watchlists = db.query(
                Watchlist,
            ).all()

            for item in watchlists:
                subscribe_instrument(
                    exchange=item.exchange,
                    symbol=item.symbol,
                )

        finally:
            db.close()