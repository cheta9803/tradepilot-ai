"""add user role

Revision ID: 0888c1cf81af
Revises: 4620459814a7
Create Date: 2026-07-04 17:27:12.074694
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0888c1cf81af"
down_revision: Union[str, Sequence[str], None] = "4620459814a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_roles = sa.Enum(
    "ADMIN",
    "TRADER",
    "PREMIUM",
    name="user_roles",
)


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    user_roles.create(bind, checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_roles,
            nullable=False,
            server_default="TRADER",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "role")

    bind = op.get_bind()

    user_roles.drop(bind, checkfirst=True)