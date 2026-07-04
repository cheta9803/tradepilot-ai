from sqlalchemy.orm import Session

from app.users.models import User
from app.watchlist.models import Watchlist
from app.watchlist.repository import WatchlistRepository
from app.watchlist.schemas import WatchlistCreate


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
            raise ValueError("Symbol already exists in watchlist.")

        watchlist = Watchlist(
            user_id=current_user.id,
            symbol=payload.symbol.upper(),
            exchange=payload.exchange.upper(),
        )

        return WatchlistRepository.create(
            db=db,
            watchlist=watchlist,
        )

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
            raise ValueError("Watchlist item not found.")

        if watchlist.user_id != current_user.id:
            raise ValueError("Not authorized.")

        WatchlistRepository.delete(
            db=db,
            watchlist=watchlist,
        )