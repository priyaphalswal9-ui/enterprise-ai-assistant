"""add name to users

Revision ID: 6375b9673d13
Revises: 6055c0868e78
Create Date: 2026-09-21 00:45:20.218061

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6375b9673d13"
down_revision: Union[str, Sequence[str], None] = "6055c0868e78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add the new column temporarily as nullable
    op.add_column(
        "users",
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=True,
        ),
    )

    # Give existing users a temporary name
    op.execute(
        "UPDATE users SET name = 'User' WHERE name IS NULL"
    )

    # Make the column required for all future users
    op.alter_column(
        "users",
        "name",
        existing_type=sa.String(length=100),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "name")