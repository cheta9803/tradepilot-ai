"""create instruments table

Revision ID: 2fcf05d44dee
Revises: f7df4209125c
Create Date: 2026-07-05 12:39:45.582229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2fcf05d44dee"
down_revision: Union[str, Sequence[str], None] = "f7df4209125c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "instruments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exchange", sa.String(length=10), nullable=False),
        sa.Column("symbol", sa.String(length=50), nullable=False),
        sa.Column("trading_symbol", sa.String(length=100), nullable=False),
        sa.Column("token", sa.String(length=30), nullable=False),
        sa.Column("instrument_type", sa.String(length=30), nullable=False),
        sa.Column("lot_size", sa.Integer(), nullable=False),
        sa.Column("tick_size", sa.Float(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trading_symbol"),
    )

    op.create_index(
        op.f("ix_instruments_exchange"),
        "instruments",
        ["exchange"],
        unique=False,
    )

    op.create_index(
        op.f("ix_instruments_symbol"),
        "instruments",
        ["symbol"],
        unique=False,
    )

    op.create_index(
        op.f("ix_instruments_token"),
        "instruments",
        ["token"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_instruments_token"),
        table_name="instruments",
    )

    op.drop_index(
        op.f("ix_instruments_symbol"),
        table_name="instruments",
    )

    op.drop_index(
        op.f("ix_instruments_exchange"),
        table_name="instruments",
    )

    op.drop_table("instruments")