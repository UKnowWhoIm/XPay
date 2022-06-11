"""create_users_table

Revision ID: f42d0dfcd4a5
Revises: 
Create Date: 2022-06-11 15:58:40.369417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f42d0dfcd4a5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("phone_number", sa.String, unique=True, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("password", sa.String, nullable=False)
    )


def downgrade() -> None:
    op.drop_table("users")

