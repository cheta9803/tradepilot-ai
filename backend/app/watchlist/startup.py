from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.history.loader import HistoryLoader
from app.instruments.cache import InstrumentCache
from app.watchlist.models import Watchlist


class WatchlistStartup:

    @staticmethod
    def subscribe_all() -> None:

        from app.live.instance import live_manager

        db: Session = SessionLocal()

        try:
            watchlists = db.query(
                Watchlist,
            ).all()

            subscribed: set[tuple[str, str]] = set()

            for item in watchlists:

                instrument = InstrumentCache.get_by_symbol(
                    exchange=item.exchange,
                    symbol=item.symbol,
                )

                if instrument is None:
                    continue

                key = (
                    instrument.exchange,
                    instrument.token,
                )

                if key in subscribed:
                    continue

                try:

                    # Load latest historical candle first
                    HistoryLoader.load(
                        exchange=instrument.exchange,
                        token=instrument.token,
                    )

                    # Then subscribe to live data
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

        finally:
            db.close()