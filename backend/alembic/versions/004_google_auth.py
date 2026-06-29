"""add google_id and auth_provider to users

Revision ID: 004
Revises: 003
Create Date: 2026-06-29 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_id", sa.String(255), nullable=True, unique=True))
    op.add_column("users", sa.Column("auth_provider", sa.String(32), nullable=False, server_default="email"))


def downgrade() -> None:
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "google_id")
