"""create trade history table

Revision ID: 9f1a2b3c4d5e
Revises: 4079d95c80fb
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f1a2b3c4d5e"

down_revision: Union[
    str,
    Sequence[str],
    None,
] = "4079d95c80fb"

branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "trade_history",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "exchange",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "token",
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            "symbol",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "timeframe",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "signal",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "entry_price",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "exit_price",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "pnl",
            sa.Float(),
            nullable=False,
        ),

        sa.Column(
            "reason",
            sa.String(length=50),
            nullable=True,
        ),

        sa.Column(
            "opened_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "closed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "order_id",
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            "execution_mode",
            sa.String(length=10),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_trade_history_id",
        "trade_history",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_trade_history_exchange",
        "trade_history",
        ["exchange"],
        unique=False,
    )

    op.create_index(
        "ix_trade_history_token",
        "trade_history",
        ["token"],
        unique=False,
    )

    op.create_index(
        "ix_trade_history_symbol",
        "trade_history",
        ["symbol"],
        unique=False,
    )

    op.create_index(
        "ix_trade_history_closed_at",
        "trade_history",
        ["closed_at"],
        unique=False,
    )

    op.create_index(
        "ix_trade_history_order_id",
        "trade_history",
        ["order_id"],
        unique=True,
    )


def downgrade() -> None:

    op.drop_index(
        "ix_trade_history_order_id",
        table_name="trade_history",
    )

    op.drop_index(
        "ix_trade_history_closed_at",
        table_name="trade_history",
    )

    op.drop_index(
        "ix_trade_history_symbol",
        table_name="trade_history",
    )

    op.drop_index(
        "ix_trade_history_token",
        table_name="trade_history",
    )

    op.drop_index(
        "ix_trade_history_exchange",
        table_name="trade_history",
    )

    op.drop_index(
        "ix_trade_history_id",
        table_name="trade_history",
    )

    op.drop_table("trade_history")
