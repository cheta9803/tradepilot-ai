from sqlalchemy.orm import Session

from app.live.instance import live_manager
from app.instruments.cache import InstrumentCache
from app.users.models import User
from app.watchlist.models import Watchlist
from app.watchlist.repository import WatchlistRepository
from app.watchlist.schemas import WatchlistCreate
from app.watchlist.live_service import WatchlistLiveService
from app.watchlist.live_schemas import WatchlistLiveResponse

class WatchlistService:

    @staticmethod
    def create(
        db: Session,
        current_user: User,
        payload: WatchlistCreate,
    ) -> Watchlist:

        existing = WatchlistRepository.get_by_symbol(
            db=db,
            user_id=current_user.id,
            symbol=payload.symbol,
        )

        if existing:
            raise ValueError(
                "Symbol already exists in watchlist."
            )

        watchlist = Watchlist(
            user_id=current_user.id,
            symbol=payload.symbol.upper(),
            exchange=payload.exchange.upper(),
        )

        watchlist = WatchlistRepository.create(
            db=db,
            watchlist=watchlist,
        )

        instrument = InstrumentCache.get_by_symbol(
            exchange=watchlist.exchange,
            symbol=watchlist.symbol,
        )

        if instrument:
            live_manager.subscribe(
                exchange=instrument.exchange,
                token=instrument.token,
            )

        return watchlist

    @staticmethod
    def list(
        db: Session,
        current_user: User,
    ) -> list[Watchlist]:

        return WatchlistRepository.get_by_user(
            db=db,
            user_id=current_user.id,
        )

    @staticmethod
    def list_live(
        db: Session,
        current_user: User,
    ) -> list[WatchlistLiveResponse]:

        watchlist = WatchlistRepository.get_by_user(
            db=db,
            user_id=current_user.id,
        )

        result = []

        for item in watchlist:

            live = WatchlistLiveService.get_live_data(
                item,
            )

            result.append(
                WatchlistLiveResponse(**live)
            )

        return result

    @staticmethod
    def delete(
        db: Session,
        current_user: User,
        watchlist_id: int,
    ) -> None:

        watchlist = WatchlistRepository.get_by_id(
            db=db,
            watchlist_id=watchlist_id,
        )

        if watchlist is None:
            raise ValueError(
                "Watchlist item not found."
            )

        if watchlist.user_id != current_user.id:
            raise ValueError(
                "Not authorized."
            )

        instrument = InstrumentCache.get_by_symbol(
            exchange=watchlist.exchange,
            symbol=watchlist.symbol,
        )

        total = WatchlistRepository.count_by_symbol(
            db=db,
            exchange=watchlist.exchange,
            symbol=watchlist.symbol,
        )

        WatchlistRepository.delete(
            db=db,
            watchlist=watchlist,
        )

        if (
            instrument is not None
            and total == 1
        ):
            live_manager.unsubscribe(
                exchange=instrument.exchange,
                token=instrument.token,
            )