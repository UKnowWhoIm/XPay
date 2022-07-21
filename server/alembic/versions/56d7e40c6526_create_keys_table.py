"""create_keys_table

Revision ID: 56d7e40c6526
Revises: ad8168d2f0e9
Create Date: 2022-07-14 09:25:48.308478

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.crypto_utils.enums import KeyStatus


# revision identifiers, used by Alembic.
revision = '56d7e40c6526'
down_revision = 'ad8168d2f0e9'
branch_labels = None
depends_on = None

key_status_enum = postgresql.ENUM(KeyStatus, name="key_status")

def upgrade() -> None:
    op.create_table(
        "keys",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.String, sa.ForeignKey("users.id")),
        sa.Column("public_key", sa.LargeBinary, nullable=False),
        sa.Column("private_key", sa.LargeBinary, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False,  server_default=sa.func.now()),
        sa.Column("status", key_status_enum, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("keys")
    key_status_enum.drop(op.get_bind())
