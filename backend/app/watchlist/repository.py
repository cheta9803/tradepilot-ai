from sqlalchemy.orm import Session

from app.watchlist.models import Watchlist


class WatchlistRepository:

    @staticmethod
    def create(
        db: Session,
        watchlist: Watchlist,
    ) -> Watchlist:
        db.add(watchlist)
        db.commit()
        db.refresh(watchlist)
        return watchlist

    @staticmethod
    def get_by_user(
        db: Session,
        user_id: int,
    ) -> list[Watchlist]:
        return (
            db.query(Watchlist)
            .filter(Watchlist.user_id == user_id)
            .all()
        )

    @staticmethod
    def get_by_symbol(
        db: Session,
        user_id: int,
        symbol: str,
    ) -> Watchlist | None:
        return (
            db.query(Watchlist)
            .filter(
                Watchlist.user_id == user_id,
                Watchlist.symbol == symbol,
            )
            .first()
        )

    @staticmethod
    def get_by_id(
        db: Session,
        watchlist_id: int,
    ) -> Watchlist | None:
        return (
            db.query(Watchlist)
            .filter(Watchlist.id == watchlist_id)
            .first()
        )

    @staticmethod
    def delete(
        db: Session,
        watchlist: Watchlist,
    ) -> None:
        db.delete(watchlist)
        db.commit()