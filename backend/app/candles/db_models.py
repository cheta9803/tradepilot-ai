from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
)

from app.db.base import Base


class CandleModel(Base):
    __tablename__ = "candles"

    id = Column(
        Integer,
        primary_key=True,
    )

    exchange = Column(
        String,
        nullable=False,
    )

    symbol = Column(
        String,
        nullable=False,
    )

    token = Column(
        String,
        nullable=False,
        index=True,
    )

    timeframe = Column(
        String,
        nullable=False,
    )

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    open = Column(
        Float,
        nullable=False,
    )

    high = Column(
        Float,
        nullable=False,
    )

    low = Column(
        Float,
        nullable=False,
    )

    close = Column(
        Float,
        nullable=False,
    )

    volume = Column(
        Integer,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "exchange",
            "token",
            "timeframe",
            "timestamp",
            name="uq_candle",
        ),
    )