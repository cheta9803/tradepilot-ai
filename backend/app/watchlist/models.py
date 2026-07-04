from datetime import datetime
from datetime import UTC

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base import Base


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    symbol: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    exchange: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
    )

    user = relationship(
        "User",
        back_populates="watchlists",
    )