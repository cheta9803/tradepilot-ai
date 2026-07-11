from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    exchange: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    trading_symbol: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    token: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    instrument_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    lot_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    tick_size: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.05,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )