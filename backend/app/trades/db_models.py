from datetime import datetime, UTC

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class TradeHistory(Base):
    __tablename__ = "trade_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    exchange: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    timeframe: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    signal: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    entry_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    exit_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    pnl: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    reason: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    closed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    order_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    execution_mode: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="PAPER",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
