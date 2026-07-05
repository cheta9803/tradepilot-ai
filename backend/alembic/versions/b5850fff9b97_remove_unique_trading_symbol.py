"""remove unique trading_symbol

Revision ID: b5850fff9b97
Revises: d39a677a1020
Create Date: 2026-07-05

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b5850fff9b97"
down_revision: Union[str, Sequence[str], None] = "d39a677a1020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "instruments_trading_symbol_key",
        "instruments",
        type_="unique",
    )

    op.create_index(
        "ix_instruments_trading_symbol",
        "instruments",
        ["trading_symbol"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_instruments_trading_symbol",
        table_name="instruments",
    )

    op.create_unique_constraint(
        "instruments_trading_symbol_key",
        "instruments",
        ["trading_symbol"],
    )