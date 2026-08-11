from threading import Lock

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.history.load_queue import HistoryLoadQueue
from app.history.rebuilder import HistoryRebuilder
from app.instruments.cache import InstrumentCache
from app.scanner.universe import Nifty50Universe
from app.watchlist.models import Watchlist


class WatchlistStartup:

    INDEX_SYMBOLS = [
        ("NSE", "NIFTY"),
        ("NSE", "BANKNIFTY"),
        ("NSE", "FINNIFTY"),
    ]

    _history_loaded = False
    _history_loading = False

    _history_lock = Lock()

    _instruments: list[tuple[str, str]] = []

    @classmethod
    def get_required_instruments(
        cls,
    ) -> list[tuple[str, str]]:

        db: Session = SessionLocal()

        try:

            subscribed: set[
                tuple[str, str]
            ] = set()

            instruments: list[
                tuple[str, str]
            ] = []

            def collect(
                exchange: str,
                symbol: str,
            ) -> None:

                instrument = (
                    InstrumentCache.get_by_symbol(
                        exchange=exchange,
                        symbol=symbol,
                    )
                )

                if instrument is None:

                    return

                key = (
                    instrument.exchange,
                    instrument.token,
                )

                if key in subscribed:

                    return

                subscribed.add(
                    key,
                )

                instruments.append(
                    key,
                )

            # -------------------------------------------------
            # Market indices
            # -------------------------------------------------

            for exchange, symbol in (
                cls.INDEX_SYMBOLS
            ):

                collect(
                    exchange,
                    symbol,
                )

            # -------------------------------------------------
            # User watchlist
            # -------------------------------------------------

            for item in db.query(
                Watchlist
            ).all():

                collect(
                    item.exchange,
                    item.symbol,
                )

            # -------------------------------------------------
            # Nifty 50 universe
            # -------------------------------------------------

            for instrument in (
                InstrumentCache.get_all()
            ):

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

            return list(
                instruments,
            )

        finally:

            db.close()

    @classmethod
    def load_history(
        cls,
    ) -> list[tuple[str, str]]:

        # ---------------------------------------------------------
        # Prevent duplicate historical loads.
        #
        # This is especially important when the Angel WebSocket
        # reconnects or startup is triggered more than once.
        # ---------------------------------------------------------

        with cls._history_lock:

            if cls._history_loaded:

                return list(
                    cls._instruments,
                )

            if cls._history_loading:

                logger_message = (
                    "Historical warm-up is already running."
                )

                print(
                    logger_message,
                )

                return list(
                    cls._instruments,
                )

            cls._history_loading = True

        try:

            instruments = (
                cls.get_required_instruments()
            )

            if not instruments:

                with cls._history_lock:

                    cls._history_loaded = True

                return []

            # -----------------------------------------------------
            # Load 1m historical candles.
            #
            # This method is called from LiveManager's background
            # history thread, never from the Angel WebSocket
            # on_open callback.
            # -----------------------------------------------------

            HistoryLoadQueue.load(
                instruments,
            )

            # -----------------------------------------------------
            # Rebuild only the required instruments.
            #
            # Do not rebuild every NSE instrument.
            # -----------------------------------------------------

            HistoryRebuilder.rebuild(
                instruments=instruments,
            )

            with cls._history_lock:

                cls._history_loaded = True

            return list(
                instruments,
            )

        finally:

            with cls._history_lock:

                cls._history_loading = False

    @classmethod
    def subscribe_all(
        cls,
        *,
        load_history: bool = False,
    ) -> None:

        from app.live.instance import live_manager

        # ---------------------------------------------------------
        # During live WebSocket on_open:
        #
        # load_history MUST be False.
        #
        # History loading happens separately in the background.
        # ---------------------------------------------------------

        if load_history:

            instruments = cls.load_history()

        else:

            instruments = (
                cls.get_required_instruments()
            )

        if not instruments:

            print(
                "No instruments available for subscription.",
            )

            return

        print(
            f"Subscribing {len(instruments)} instruments.",
        )

        for exchange, token in instruments:

            live_manager.subscribe(
                exchange=exchange,
                token=token,
            )

            instrument = (
                InstrumentCache.get_by_token(
                    token,
                )
            )

            if instrument is not None:

                print(
                    f"Auto subscribed: "
                    f"{instrument.symbol} "
                    f"({token})"
                )