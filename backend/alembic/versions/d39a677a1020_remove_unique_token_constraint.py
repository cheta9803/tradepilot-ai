"""remove unique token constraint

Revision ID: d39a677a1020
Revises: 2fcf05d44dee
Create Date: 2026-07-05 12:59:53.787189
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d39a677a1020"
down_revision: Union[str, Sequence[str], None] = "2fcf05d44dee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_index(
        "ix_instruments_token",
        table_name="instruments",
    )

    op.create_index(
        "ix_instruments_token",
        "instruments",
        ["token"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        "ix_instruments_token",
        table_name="instruments",
    )

    op.create_index(
        "ix_instruments_token",
        "instruments",
        ["token"],
        unique=True,
    )