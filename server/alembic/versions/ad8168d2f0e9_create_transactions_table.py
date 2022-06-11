"""create_transactions_table

Revision ID: ad8168d2f0e9
Revises: f42d0dfcd4a5
Create Date: 2022-06-11 19:14:50.686491

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.payments.enums import RequestStates, TransactionTypes
from app.utils import uuid_to_string


# revision identifiers, used by Alembic.
revision = 'ad8168d2f0e9'
down_revision = 'f42d0dfcd4a5'
branch_labels = None
depends_on = None

transaction_types_enum = postgresql.ENUM(TransactionTypes, name="transaction_types")
request_states_enum = postgresql.ENUM(RequestStates, name="request_states")

def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.String, primary_key=True, default=uuid_to_string),
        sa.Column("type", transaction_types_enum, nullable=False),
        sa.Column("sender_id", sa.String, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("receiver_id", sa.String, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.now()),
        sa.Column("request_state", request_states_enum, nullable=True)
    )


def downgrade() -> None:
    op.drop_table("transactions")
    transaction_types_enum.drop(op.get_bind())
    request_states_enum.drop(op.get_bind())
